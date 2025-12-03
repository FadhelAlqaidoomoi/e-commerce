# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, _, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from .main import api_response, cors_handler, require_auth

_logger = logging.getLogger(__name__)


class EcommerceApiAuth(http.Controller):
    """
    Authentication controller for E-commerce API.
    Handles login, registration, logout, and session management.
    """

    @http.route(
        '/api/v1/auth/login',
        type='http',
        auth='none',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def login(self, **kwargs):
        """
        Authenticate user and create session.
        
        Expected JSON body:
        {
            "db": "database_name",  // Optional if single DB
            "login": "user@example.com",
            "password": "password123"
        }
        """
        try:
            # Parse JSON body
            data = json.loads(request.httprequest.data or '{}')
            
            login = data.get('login') or data.get('email')
            password = data.get('password')
            db = data.get('db') or request.db
            
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
                'is_public': user._is_public(),
            }
            
            response = api_response(
                success=True,
                data=session_info,
                message='Login successful'
            )
            
            # Set session cookie
            response.set_cookie(
                'session_id',
                request.session.sid,
                httponly=True,
                samesite='None',
                secure=True,
                max_age=60 * 60 * 24 * 7  # 7 days
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
            _logger.exception('Login error: %s', str(e))
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
            "whatsapp_opt_in": true  // Optional
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
            
            if not name or not email or not password:
                return api_response(
                    success=False,
                    error='Missing required fields',
                    message='Name, email, and password are required',
                    status=400
                )
            
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
            
            # Create the user using signup
            values = {
                'login': email,
                'name': name,
                'password': password,
            }
            
            # Use Odoo's signup mechanism
            db, login, password = request.env['res.users'].sudo().signup(values)
            
            # Get the created user
            user = request.env['res.users'].sudo().search([
                ('login', '=', login)
            ], limit=1)
            
            if user and user.partner_id:
                # Update partner with additional info
                partner_vals = {
                    'ecommerce_registered': True,
                }
                if phone:
                    partner_vals['phone'] = phone
                if whatsapp_number:
                    partner_vals['whatsapp_number'] = whatsapp_number
                    partner_vals['whatsapp_opt_in'] = whatsapp_opt_in
                
                user.partner_id.sudo().write(partner_vals)
            
            # Auto-login the user
            credential = {'login': login, 'password': data.get('password'), 'type': 'password'}
            auth_info = request.session.authenticate(db, credential)
            
            if auth_info.get('uid'):
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
                    samesite='None',
                    secure=True,
                    max_age=60 * 60 * 24 * 7
                )
                
                return response
            
            return api_response(
                success=True,
                data={'user_id': user.id},
                message='Registration successful. Please login.'
            )
            
        except SignupError as e:
            _logger.warning('Signup error: %s', str(e))
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
            _logger.exception('Registration error: %s', str(e))
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
            _logger.exception('Logout error: %s', str(e))
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
                    'is_public': True,
                },
                message='Public session'
            )
            
        except Exception as e:
            _logger.exception('Session check error: %s', str(e))
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
                    _logger.warning('Password reset failed for %s: %s', email, str(e))
            
            # Always return success to prevent email enumeration
            return api_response(
                success=True,
                data=None,
                message='If an account exists with this email, password reset instructions have been sent.'
            )
            
        except Exception as e:
            _logger.exception('Password reset error: %s', str(e))
            return api_response(
                success=True,  # Still return success to prevent enumeration
                data=None,
                message='If an account exists with this email, password reset instructions have been sent.'
            )
