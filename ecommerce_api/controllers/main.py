# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import functools
import logging
import time
import re
import hashlib
from collections import defaultdict
from werkzeug.exceptions import Unauthorized, BadRequest

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITING
# ============================================================================

# In-memory rate limit storage (in production, use Redis)
_rate_limit_storage = defaultdict(list)
_rate_limit_lock_storage = {}

def get_client_ip():
    """Get client IP address from request headers."""
    # Check for forwarded IP (behind proxy)
    forwarded = request.httprequest.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.httprequest.remote_addr or 'unknown'


def rate_limit(max_requests=10, window_seconds=60, key_func=None):
    """
    Rate limiting decorator.

    Args:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds
        key_func: Optional function to generate rate limit key (default: IP-based)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = f"{func.__name__}:{get_client_ip()}"

            current_time = time.time()
            window_start = current_time - window_seconds

            # Check if locked out
            if key in _rate_limit_lock_storage:
                lock_until = _rate_limit_lock_storage[key]
                if current_time < lock_until:
                    remaining = int(lock_until - current_time)
                    return api_response(
                        success=False,
                        error='Rate limit exceeded',
                        message=f'Too many requests. Try again in {remaining} seconds.',
                        status=429
                    )
                else:
                    del _rate_limit_lock_storage[key]

            # Clean old entries
            _rate_limit_storage[key] = [
                t for t in _rate_limit_storage[key] if t > window_start
            ]

            # Check rate limit
            if len(_rate_limit_storage[key]) >= max_requests:
                # Lock out for extended period on repeated violations
                _rate_limit_lock_storage[key] = current_time + (window_seconds * 2)
                return api_response(
                    success=False,
                    error='Rate limit exceeded',
                    message=f'Too many requests. Please wait before trying again.',
                    status=429
                )

            # Record this request
            _rate_limit_storage[key].append(current_time)

            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# SECURITY HEADERS
# ============================================================================

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Cache-Control': 'no-store, no-cache, must-revalidate, private',
    'Pragma': 'no-cache',
}


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password):
    """
    Validate password meets security requirements.
    Returns (is_valid, error_message)
    """
    if not password:
        return False, 'Password is required'

    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'

    if len(password) > 128:
        return False, 'Password is too long'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'

    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'

    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty123', 'admin123', 'letmein']
    if password.lower() in weak_passwords:
        return False, 'Password is too common. Please choose a stronger password.'

    return True, None


def validate_quantity(quantity, max_quantity=9999):
    """
    Validate quantity is within acceptable bounds.
    Returns (is_valid, sanitized_value, error_message)
    """
    try:
        qty = float(quantity)
        if qty <= 0:
            return False, None, 'Quantity must be greater than 0'
        if qty > max_quantity:
            return False, None, f'Quantity cannot exceed {max_quantity}'
        # Round to 2 decimal places
        return True, round(qty, 2), None
    except (TypeError, ValueError):
        return False, None, 'Invalid quantity value'


def sanitize_string(value, max_length=255, allow_html=False):
    """Sanitize string input."""
    if not value:
        return ''

    value = str(value)[:max_length]

    if not allow_html:
        # Remove potential script tags
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'<[^>]+>', '', value)

    return value.strip()


# ============================================================================
# CORS HANDLER
# ============================================================================

def cors_handler(func):
    """
    Decorator to handle CORS headers for API endpoints.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get allowed origins from config
        try:
            config = request.env['ecommerce.api.config'].sudo().get_config()
            allowed_origins = config.get_allowed_origins_list()
        except Exception:
            # Fail closed - only allow localhost in case of error
            allowed_origins = ['http://localhost:3000']

        origin = request.httprequest.headers.get('Origin', '')

        # SECURITY FIX: Never fall back to wildcard
        # Only allow explicitly configured origins
        if origin in allowed_origins:
            allow_origin = origin
        elif not origin and allowed_origins:
            # No origin header (same-origin request) - allow first configured
            allow_origin = allowed_origins[0]
        else:
            # Reject unknown origins for credentialed requests
            # Log the attempt for security monitoring
            _logger.warning(f'CORS: Rejected request from unknown origin: {origin}')
            allow_origin = 'null'  # Explicitly reject

        # Handle preflight OPTIONS request
        if request.httprequest.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': allow_origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, X-CSRF-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '86400',
                **SECURITY_HEADERS,
            }
            return Response(status=200, headers=headers)

        # Execute the actual function
        result = func(*args, **kwargs)

        # Add CORS and security headers to response
        if isinstance(result, Response):
            result.headers['Access-Control-Allow-Origin'] = allow_origin
            result.headers['Access-Control-Allow-Credentials'] = 'true'
            # Add security headers
            for header, value in SECURITY_HEADERS.items():
                result.headers[header] = value

        return result

    return wrapper


# ============================================================================
# API RESPONSE HELPER
# ============================================================================

def api_response(success=True, data=None, message=None, error=None, status=200):
    """
    Create a standardized API response.

    Args:
        success: Boolean indicating if the request was successful
        data: The response data (dict, list, or any JSON-serializable value)
        message: A human-readable message
        error: Error details if success is False
        status: HTTP status code

    Returns:
        Response object with JSON content and CORS headers
    """
    response_data = {
        'success': success,
        'data': data,
        'message': message,
    }

    if error:
        # SECURITY FIX: Don't expose detailed error messages in production
        # Only include generic error type, not stack traces
        if isinstance(error, str) and len(error) > 100:
            response_data['error'] = 'An error occurred'
        else:
            response_data['error'] = error

    # Get allowed origins from config
    try:
        config = request.env['ecommerce.api.config'].sudo().get_config()
        allowed_origins = config.get_allowed_origins_list()
    except Exception:
        allowed_origins = ['http://localhost:3000']

    origin = request.httprequest.headers.get('Origin', '')

    # SECURITY FIX: Never fall back to wildcard
    if origin in allowed_origins:
        allow_origin = origin
    elif not origin and allowed_origins:
        allow_origin = allowed_origins[0]
    else:
        allow_origin = 'null'

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': allow_origin,
        'Access-Control-Allow-Credentials': 'true',
        **SECURITY_HEADERS,
    }

    return Response(
        json.dumps(response_data),
        status=status,
        headers=headers
    )


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================

def require_auth(func):
    """
    Decorator to require authentication for API endpoints.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.session.uid:
            return api_response(
                success=False,
                error='Authentication required',
                message='Please login to access this resource',
                status=401
            )
        return func(*args, **kwargs)
    return wrapper


# ============================================================================
# CART OWNERSHIP VERIFICATION
# ============================================================================

def verify_cart_ownership(order, partner_id=None):
    """
    Verify that the cart/order belongs to the current user.

    Args:
        order: The sale.order record
        partner_id: Optional partner ID to check against

    Returns:
        (is_valid, error_response or None)
    """
    if not order or not order.exists():
        return False, api_response(
            success=False,
            error='Cart not found',
            message='No active cart found',
            status=404
        )

    # For authenticated users, verify partner ownership
    if request.session.uid:
        user = request.env['res.users'].sudo().browse(request.session.uid)
        current_partner_id = user.partner_id.id if user.partner_id else None

        if current_partner_id and order.partner_id.id != current_partner_id:
            # Check if this is a public partner cart being claimed
            public_partner = request.env.ref('base.public_partner', raise_if_not_found=False)
            if not public_partner or order.partner_id.id != public_partner.id:
                _logger.warning(
                    f'Cart ownership violation: User {request.session.uid} attempted to access '
                    f'cart {order.id} belonging to partner {order.partner_id.id}'
                )
                return False, api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this cart',
                    status=403
                )

    return True, None


# ============================================================================
# MAIN CONTROLLER
# ============================================================================

class EcommerceApiMain(http.Controller):
    """
    Main controller for E-commerce API.
    Provides health check and API info endpoints.
    """

    @http.route(
        '/api/v1',
        type='http',
        auth='none',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def api_info(self, **kwargs):
        """
        API information and health check endpoint.
        """
        return api_response(
            success=True,
            data={
                'name': 'E-commerce REST API',
                'version': '1.0.0',
                'odoo_version': '18.0',
                'endpoints': {
                    'auth': {
                        'login': 'POST /api/v1/auth/login',
                        'register': 'POST /api/v1/auth/register',
                        'logout': 'POST /api/v1/auth/logout',
                        'session': 'GET /api/v1/auth/session',
                        'reset_password': 'POST /api/v1/auth/reset-password',
                    },
                    'products': {
                        'list': 'GET /api/v1/products',
                        'detail': 'GET /api/v1/products/<id>',
                        'categories': 'GET /api/v1/categories',
                    },
                    'cart': {
                        'get': 'GET /api/v1/cart',
                        'add': 'POST /api/v1/cart/add',
                        'update': 'POST /api/v1/cart/update',
                        'remove': 'DELETE /api/v1/cart/remove/<line_id>',
                        'clear': 'DELETE /api/v1/cart/clear',
                    },
                    'orders': {
                        'list': 'GET /api/v1/orders',
                        'detail': 'GET /api/v1/orders/<id>',
                        'create': 'POST /api/v1/orders/create',
                    },
                    'user': {
                        'profile': 'GET /api/v1/user/profile',
                        'update_profile': 'POST /api/v1/user/profile',
                        'addresses': 'GET /api/v1/user/addresses',
                        'add_address': 'POST /api/v1/user/addresses',
                    },
                    'countries': 'GET /api/v1/countries',
                }
            },
            message='E-commerce API is running'
        )

    @http.route(
        '/api/v1/countries',
        type='http',
        auth='none',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_countries(self, **kwargs):
        """
        Get list of all countries with their states.
        """
        countries = request.env['res.country'].sudo().search([])

        countries_data = []
        for country in countries:
            country_data = {
                'id': country.id,
                'name': country.name,
                'code': country.code,
                'phone_code': country.phone_code,
                'states': [{
                    'id': state.id,
                    'name': state.name,
                    'code': state.code,
                } for state in country.state_ids]
            }
            countries_data.append(country_data)

        return api_response(
            success=True,
            data=countries_data,
            message=f'Found {len(countries_data)} countries'
        )
