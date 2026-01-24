# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, fields, _, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from .main import (
    api_response, cors_handler, require_auth, rate_limit,
    validate_email, validate_password_strength, sanitize_string
)

_logger = logging.getLogger(__name__)

# Maximum order value for automatic linking (orders above this need manual verification)
MAX_AUTO_LINK_ORDER_VALUE = 10000


class EcommerceApiAuth(http.Controller):
    """
    Authentication controller for E-commerce API.
    Handles login, registration, logout, and session management.
    """

    def _get_user_type(self, user):
        """
        Determine the user type based on Odoo groups.

        Returns:
            str: 'internal', 'portal', or 'public'
        """
        if user._is_internal():
            return 'internal'
        elif user._is_portal():
            return 'portal'
        else:
            return 'public'

    def _link_guest_orders(self, partner, email):
        """
        Link past guest orders to newly registered user.

        Matches orders by:
        1. guest_checkout_email field
        2. Partner email matching (for partners not linked to users)

        Args:
            partner: res.partner record of the new user
            email: User's email address

        Returns:
            int: Number of orders linked
        """
        SaleOrder = request.env['sale.order'].sudo()
        Partner = request.env['res.partner'].sudo()

        linked_count = 0

        # Strategy 1: Find orders by guest_checkout_email
        email_matched = SaleOrder.search([
            ('guest_checkout_email', '=ilike', email),
            ('state', 'in', ['sale', 'done']),  # Only completed orders
            ('partner_id.user_ids', '=', False),  # Partner not linked to user
        ])

        # Strategy 2: Find orders from unlinked partners with same email
        guest_partners = Partner.search([
            ('email', '=ilike', email),
            ('user_ids', '=', False),  # Not linked to any user
            ('id', '!=', partner.id),  # Not the current partner
            ('parent_id', '=', False),  # Main partners only
            ('ecommerce_registered', '=', False),  # Not API-registered (guest)
        ])

        partner_matched = SaleOrder.browse()
        if guest_partners:
            partner_matched = SaleOrder.search([
                ('partner_id', 'in', guest_partners.ids),
                ('state', 'in', ['sale', 'done']),
            ])

        # Combine and deduplicate
        orders_to_link = email_matched | partner_matched

        for order in orders_to_link:
            # Safety: Skip high-value orders (require manual verification)
            if order.amount_total > MAX_AUTO_LINK_ORDER_VALUE:
                _logger.warning(
                    'Skipping high-value order %s for auto-linking. Value: %s',
                    order.name, order.amount_total
                )
                continue

            # Store original partner for audit
            original_partner = order.partner_id

            # Update order to new partner
            order.write({
                'partner_id': partner.id,
                # Preserve original guest email for audit
                'guest_checkout_email': order.guest_checkout_email or original_partner.email,
            })

            # Log the linking
            order.message_post(
                body=f'Order linked from guest ({original_partner.email}) to '
                     f'registered user ({partner.email})',
                message_type='notification',
            )

            linked_count += 1
            _logger.info(
                'Linked order %s from guest %s to user %s',
                order.name, original_partner.email, partner.email
            )

        # Mark partner as having linked orders
        if linked_count > 0:
            partner.write({
                'guest_orders_linked': True,
                'guest_orders_linked_date': fields.Datetime.now(),
            })

        return linked_count

    def _transfer_guest_cart(self, partner, token_str):
        """
        Transfer guest cart to newly registered/logged in user.

        Args:
            partner: res.partner record of the user
            token_str: Cart token string

        Returns:
            bool: True if cart was transferred
        """
        if not token_str:
            return False

        CartToken = request.env['ecommerce.cart.token'].sudo()
        token_record = CartToken.find_by_token(token_str)

        if not token_record:
            return False

        is_valid, error_code, error_msg = token_record.validate_token()
        if not is_valid:
            _logger.debug('Cart token invalid for transfer: %s', error_msg)
            return False

        # Transfer cart to user's partner
        token_record.sale_order_id.write({
            'partner_id': partner.id
        })
        token_record.claim_token(partner)
        request.session['sale_order_id'] = token_record.sale_order_id.id

        _logger.info(
            'Transferred cart %s to partner %s via token',
            token_record.sale_order_id.name, partner.name
        )
        return True

    def _handle_cart_on_auth(self, partner, cart_token, merge_strategy='merge'):
        """
        Handle guest cart when user logs in or registers.

        Args:
            partner: User's partner record
            cart_token: Optional cart token string
            merge_strategy: 'merge', 'replace', or 'keep_current'

        Returns:
            dict: Cart handling result with keys: merged, strategy, cart_id
        """
        if not cart_token:
            return {'merged': False, 'reason': 'No token provided'}

        CartToken = request.env['ecommerce.cart.token'].sudo()
        token_record = CartToken.find_by_token(cart_token)

        if not token_record:
            return {'merged': False, 'reason': 'Token not found'}

        is_valid, error_code, error_msg = token_record.validate_token()
        if not is_valid:
            return {'merged': False, 'reason': error_msg}

        guest_cart = token_record.sale_order_id

        # Check for existing user cart
        user_cart_id = request.session.get('sale_order_id')
        user_cart = None
        if user_cart_id:
            user_cart = request.env['sale.order'].sudo().browse(user_cart_id)
            if not user_cart.exists() or user_cart.state != 'draft':
                user_cart = None
            elif user_cart.partner_id.id != partner.id:
                user_cart = None  # Cart belongs to different user
            elif user_cart.id == guest_cart.id:
                # Same cart, just transfer ownership
                guest_cart.write({'partner_id': partner.id})
                token_record.claim_token(partner)
                return {
                    'merged': True,
                    'strategy': 'transfer',
                    'cart_id': guest_cart.id
                }

        if merge_strategy == 'keep_current' and user_cart:
            token_record.claim_token(partner)
            return {
                'merged': True,
                'strategy': 'keep_current',
                'cart_id': user_cart.id
            }

        elif merge_strategy == 'replace' or not user_cart:
            # Transfer guest cart to user
            guest_cart.write({'partner_id': partner.id})
            token_record.claim_token(partner)
            request.session['sale_order_id'] = guest_cart.id
            return {
                'merged': True,
                'strategy': 'replace' if user_cart else 'transfer',
                'cart_id': guest_cart.id
            }

        else:  # merge
            # Merge guest cart items into user cart
            for line in guest_cart.order_line:
                existing = user_cart.order_line.filtered(
                    lambda l: l.product_id.id == line.product_id.id
                )
                if existing:
                    existing[0].product_uom_qty += line.product_uom_qty
                else:
                    line.copy({'order_id': user_cart.id})

            token_record.claim_token(partner)
            return {
                'merged': True,
                'strategy': 'merge',
                'cart_id': user_cart.id
            }

    @http.route(
        '/api/v1/auth/login',
        type='http',
        auth='none',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    @rate_limit(max_requests=5, window_seconds=60)  # 5 attempts per minute
    def login(self, **kwargs):
        """
        Authenticate user and create session.

        Expected JSON body:
        {
            "db": "database_name",  // Optional if single DB
            "login": "user@example.com",
            "password": "password123",
            "cart_token": "uuid-string",  // Optional: transfer/merge guest cart
            "cart_merge_strategy": "merge"  // Optional: merge, replace, keep_current
        }
        """
        try:
            # Parse JSON body
            data = json.loads(request.httprequest.data or '{}')

            login = data.get('login') or data.get('email')
            password = data.get('password')
            db = data.get('db') or request.db
            cart_token = data.get('cart_token')
            merge_strategy = data.get('cart_merge_strategy', 'merge')

            if not login or not password:
                return api_response(
                    success=False,
                    error='Missing credentials',
                    message='Email and password are required',
                    status=400
                )

            if not db:
                return api_response(
                    success=False,
                    error='Database not specified',
                    message='Database name is required',
                    status=400
                )

            # Authenticate user
            credential = {'login': login, 'password': password, 'type': 'password'}
            auth_info = request.session.authenticate(db, credential)

            if not auth_info.get('uid'):
                return api_response(
                    success=False,
                    error='Invalid credentials',
                    message='Invalid email or password',
                    status=401
                )

            # Get user info
            user = request.env['res.users'].sudo().browse(auth_info['uid'])
            partner = user.partner_id

            # Determine user type based on Odoo groups
            user_type = self._get_user_type(user)

            # Handle guest cart token if provided
            cart_result = None
            if cart_token:
                cart_result = self._handle_cart_on_auth(partner, cart_token, merge_strategy)

            # Get session info
            session_info = {
                'session_id': request.session.sid,
                'uid': auth_info['uid'],
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email or user.login,
                },
                'partner': partner._get_api_data() if partner else None,
                'user_type': user_type,
                'is_internal': user._is_internal(),
                'is_portal': user._is_portal(),
                'is_public': user._is_public(),
            }

            # Add cart merge info to response
            if cart_result:
                session_info['cart_merged'] = cart_result.get('merged', False)
                session_info['cart_merge_strategy'] = cart_result.get('strategy')

            response = api_response(
                success=True,
                data=session_info,
                message='Login successful'
            )

            # Set session cookie with secure settings
            response.set_cookie(
                'session_id',
                request.session.sid,
                httponly=True,
                samesite='Lax',  # Changed from 'None' - more secure default
                secure=True,
                max_age=60 * 60 * 24  # 24 hours instead of 7 days
            )

            return response

        except AccessDenied:
            return api_response(
                success=False,
                error='Access denied',
                message='Invalid email or password',
                status=401
            )
        except Exception as e:
            print('Login error: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Login failed',
                status=500
            )

    @http.route(
        '/api/v1/auth/register',
        type='http',
        auth='none',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    @rate_limit(max_requests=3, window_seconds=60)  # 3 registrations per minute
    def register(self, **kwargs):
        """
        Register a new customer account.

        Expected JSON body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "+1234567890",  // Optional
            "whatsapp_number": "+1234567890",  // Optional
            "whatsapp_opt_in": true,  // Optional
            "cart_token": "uuid-string"  // Optional: transfer guest cart
        }
        """
        try:
            # Check if registration is enabled
            config = request.env['ecommerce.api.config'].sudo().get_config()
            if not config.registration_enabled:
                return api_response(
                    success=False,
                    error='Registration disabled',
                    message='Public registration is currently disabled',
                    status=403
                )

            # Check if signup is enabled in Odoo
            if request.env['res.users'].sudo()._get_signup_invitation_scope() != 'b2c':
                return api_response(
                    success=False,
                    error='Registration disabled',
                    message='Public registration is not allowed. Please contact administrator.',
                    status=403
                )

            # Parse JSON body
            data = json.loads(request.httprequest.data or '{}')

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            phone = data.get('phone')
            whatsapp_number = data.get('whatsapp_number')
            whatsapp_opt_in = data.get('whatsapp_opt_in', False)
            cart_token = data.get('cart_token')

            if not name or not email or not password:
                return api_response(
                    success=False,
                    error='Missing required fields',
                    message='Name, email, and password are required',
                    status=400
                )

            # Validate email format
            if not validate_email(email):
                return api_response(
                    success=False,
                    error='Invalid email',
                    message='Please provide a valid email address',
                    status=400
                )

            # Validate password strength
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                return api_response(
                    success=False,
                    error='Weak password',
                    message=error_msg,
                    status=400
                )

            # Sanitize name input
            name = sanitize_string(name, max_length=100)

            # Check if user already exists
            existing_user = request.env['res.users'].sudo().search([
                ('login', '=', email)
            ], limit=1)

            if existing_user:
                return api_response(
                    success=False,
                    error='User exists',
                    message='A user with this email already exists',
                    status=409
                )

            # Create partner first with ecommerce-specific fields
            partner_vals = {
                'name': name,
                'email': email,
                'ecommerce_registered': True,
            }
            if phone:
                partner_vals['phone'] = phone
            if whatsapp_number:
                partner_vals['whatsapp_number'] = whatsapp_number
                partner_vals['whatsapp_opt_in'] = whatsapp_opt_in

            partner = request.env['res.partner'].sudo().create(partner_vals)

            # Get the main company (required for user creation)
            main_company = request.env['res.company'].sudo().search([], limit=1, order='id')
            if not main_company:
                return api_response(
                    success=False,
                    error='Configuration error',
                    message='No company configured in the system',
                    status=500
                )

            # Get the portal group
            portal_group = request.env.ref('base.group_portal')

            # Create portal user directly with all required fields
            # Use with_user(SUPERUSER_ID) to ensure proper environment context
            # This is needed because auth='none' has no user, which causes issues
            # with mail module's message_post during user creation
            user = request.env['res.users'].with_user(SUPERUSER_ID).with_context(
                no_reset_password=True,
                mail_create_nosubscribe=True,  # Don't subscribe to mail
                mail_create_nolog=True,  # Don't log creation in chatter
            ).create({
                'login': email,
                'name': name,
                'password': password,
                'partner_id': partner.id,
                'company_id': main_company.id,
                'company_ids': [(6, 0, [main_company.id])],
                'groups_id': [(6, 0, [portal_group.id])],
            })

            if not user:
                return api_response(
                    success=False,
                    error='User creation failed',
                    message='Failed to create user account',
                    status=500
                )

            # Link past guest orders by email
            linked_orders_count = self._link_guest_orders(partner, email)

            # Transfer guest cart if token provided
            cart_transferred = False
            if cart_token:
                cart_transferred = self._transfer_guest_cart(partner, cart_token)

            # Auto-login the user
            db = request.db
            credential = {'login': email, 'password': password, 'type': 'password'}
            auth_info = request.session.authenticate(db, credential)

            if auth_info.get('uid'):
                user_type = self._get_user_type(user)

                session_info = {
                    'session_id': request.session.sid,
                    'uid': auth_info['uid'],
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'login': user.login,
                        'email': user.email or user.login,
                    },
                    'partner': user.partner_id._get_api_data() if user.partner_id else None,
                    'user_type': user_type,
                    'is_portal': user._is_portal(),
                    'linked_orders_count': linked_orders_count,
                    'cart_transferred': cart_transferred,
                }

                response = api_response(
                    success=True,
                    data=session_info,
                    message='Registration successful'
                )

                response.set_cookie(
                    'session_id',
                    request.session.sid,
                    httponly=True,
                    samesite='Lax',
                    secure=True,
                    max_age=60 * 60 * 24  # 24 hours
                )

                return response

            return api_response(
                success=True,
                data={
                    'user_id': user.id,
                    'linked_orders_count': linked_orders_count,
                },
                message='Registration successful. Please login.'
            )

        except SignupError as e:
            print('Signup error: %s', str(e))
            return api_response(
                success=False,
                error='Signup failed',
                message=str(e),
                status=400
            )
        except UserError as e:
            return api_response(
                success=False,
                error='Registration failed',
                message=e.args[0],
                status=400
            )
        except Exception as e:
            print('Registration error: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Registration failed',
                status=500
            )

    @http.route(
        '/api/v1/auth/logout',
        type='http',
        auth='none',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def logout(self, **kwargs):
        """
        Logout current user and destroy session.
        """
        try:
            request.session.logout(keep_db=True)
            
            response = api_response(
                success=True,
                data=None,
                message='Logged out successfully'
            )
            
            # Clear session cookie
            response.delete_cookie('session_id')
            
            return response
            
        except Exception as e:
            print('Logout error: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Logout failed',
                status=500
            )

    @http.route(
        '/api/v1/auth/session',
        type='http',
        auth='none',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_session(self, **kwargs):
        """
        Get current session information.
        Returns user data if authenticated, otherwise returns public session.
        """
        try:
            if request.session.uid:
                user = request.env['res.users'].sudo().browse(request.session.uid)
                
                if user.exists():
                    user_type = self._get_user_type(user)
                    
                    session_info = {
                        'authenticated': True,
                        'session_id': request.session.sid,
                        'uid': user.id,
                        'user': {
                            'id': user.id,
                            'name': user.name,
                            'login': user.login,
                            'email': user.email or user.login,
                        },
                        'partner': user.partner_id._get_api_data(include_addresses=True) if user.partner_id else None,
                        'user_type': user_type,
                        'is_internal': user._is_internal(),
                        'is_portal': user._is_portal(),
                        'is_public': user._is_public(),
                    }
                    
                    return api_response(
                        success=True,
                        data=session_info,
                        message='Session active'
                    )
            
            # Return public session info
            return api_response(
                success=True,
                data={
                    'authenticated': False,
                    'session_id': request.session.sid,
                    'user_type': 'public',
                    'is_public': True,
                },
                message='Public session'
            )
            
        except Exception as e:
            print('Session check error: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get session info',
                status=500
            )

    @http.route(
        '/api/v1/auth/reset-password',
        type='http',
        auth='none',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    @rate_limit(max_requests=3, window_seconds=300)  # 3 attempts per 5 minutes
    def reset_password(self, **kwargs):
        """
        Request password reset email.
        
        Expected JSON body:
        {
            "email": "user@example.com"
        }
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            email = data.get('email')
            
            if not email:
                return api_response(
                    success=False,
                    error='Missing email',
                    message='Email address is required',
                    status=400
                )
            
            # Find user by email
            user = request.env['res.users'].sudo().search([
                '|',
                ('login', '=', email),
                ('email', '=', email)
            ], limit=1)
            
            if user:
                try:
                    user.reset_password(email)
                except Exception as e:
                    print('Password reset failed for %s: %s', email, str(e))
            
            # Always return success to prevent email enumeration
            return api_response(
                success=True,
                data=None,
                message='If an account exists with this email, password reset instructions have been sent.'
            )
            
        except Exception as e:
            print('Password reset error: %s', str(e))
            return api_response(
                success=True,  # Still return success to prevent enumeration
                data=None,
                message='If an account exists with this email, password reset instructions have been sent.'
            )
