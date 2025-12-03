# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import functools
import logging
from werkzeug.exceptions import Unauthorized, BadRequest

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def cors_handler(func):
    """
    Decorator to handle CORS headers for API endpoints.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get allowed origins from config
        config = request.env['ecommerce.api.config'].sudo().get_config()
        allowed_origins = config.get_allowed_origins_list()
        
        origin = request.httprequest.headers.get('Origin', '')
        
        # Determine which origin to allow
        if '*' in allowed_origins:
            allow_origin = '*'
        elif origin in allowed_origins:
            allow_origin = origin
        else:
            allow_origin = allowed_origins[0] if allowed_origins else '*'
        
        # Handle preflight OPTIONS request
        if request.httprequest.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': allow_origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '86400',
            }
            return Response(status=200, headers=headers)
        
        # Execute the actual function
        result = func(*args, **kwargs)
        
        # Add CORS headers to response
        if isinstance(result, Response):
            result.headers['Access-Control-Allow-Origin'] = allow_origin
            result.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return result
    
    return wrapper


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
        response_data['error'] = error
    
    # Get allowed origins from config
    try:
        config = request.env['ecommerce.api.config'].sudo().get_config()
        allowed_origins = config.get_allowed_origins_list()
    except Exception:
        allowed_origins = ['*']
    
    origin = request.httprequest.headers.get('Origin', '')
    
    if '*' in allowed_origins:
        allow_origin = '*'
    elif origin in allowed_origins:
        allow_origin = origin
    else:
        allow_origin = allowed_origins[0] if allowed_origins else '*'
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': allow_origin,
        'Access-Control-Allow-Credentials': 'true',
    }
    
    return Response(
        json.dumps(response_data),
        status=status,
        headers=headers
    )


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
