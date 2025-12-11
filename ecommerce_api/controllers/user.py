# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, _
from odoo.http import request

from .main import api_response, cors_handler, require_auth

_logger = logging.getLogger(__name__)


class EcommerceApiUser(http.Controller):
    """
    User profile controller for E-commerce API.
    Handles user profile and address management.
    """

    @http.route(
        '/api/v1/user/profile',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_profile(self, **kwargs):
        """
        Get current user profile.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to view your profile',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            
            if not user.exists():
                return api_response(
                    success=False,
                    error='User not found',
                    message='User not found',
                    status=404
                )
            
            partner = user.partner_id
            
            profile_data = {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email or user.login,
                },
                'partner': partner._get_api_data(include_addresses=True) if partner else None,
            }
            
            return api_response(
                success=True,
                data=profile_data,
                message='Profile retrieved'
            )
            
        except Exception as e:
            print('Error getting profile: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get profile',
                status=500
            )

    @http.route(
        '/api/v1/user/profile',
        type='http',
        auth='public',
        methods=['POST', 'PUT', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def update_profile(self, **kwargs):
        """
        Update user profile.
        
        Expected JSON body:
        {
            "name": "John Doe",
            "email": "john@example.com",  // Will update login
            "phone": "+1234567890",
            "mobile": "+1234567890",
            "street": "123 Main St",
            "street2": "Apt 4",
            "city": "New York",
            "zip": "10001",
            "country_id": 233,
            "state_id": 39,
            "whatsapp_number": "+1234567890",
            "whatsapp_opt_in": true
        }
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to update your profile',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            if not partner:
                return api_response(
                    success=False,
                    error='Partner not found',
                    message='User has no associated partner',
                    status=400
                )
            
            data = json.loads(request.httprequest.data or '{}')
            
            # Allowed partner fields
            allowed_fields = [
                'name', 'phone', 'mobile', 'street', 'street2',
                'city', 'zip', 'country_id', 'state_id',
                'whatsapp_number', 'whatsapp_opt_in'
            ]
            
            partner_vals = {}
            for field in allowed_fields:
                if field in data:
                    value = data[field]
                    # Convert IDs to integers
                    if field in ['country_id', 'state_id'] and value:
                        value = int(value)
                    partner_vals[field] = value
            
            if partner_vals:
                partner.write(partner_vals)
            
            # Update email (and login) if provided
            if 'email' in data and data['email'] != user.login:
                new_email = data['email']
                
                # Check if email is already used
                existing = request.env['res.users'].sudo().search([
                    ('login', '=', new_email),
                    ('id', '!=', user.id)
                ], limit=1)
                
                if existing:
                    return api_response(
                        success=False,
                        error='Email in use',
                        message='This email is already registered to another account',
                        status=400
                    )
                
                user.write({
                    'login': new_email,
                    'email': new_email,
                })
                partner.write({'email': new_email})
            
            return api_response(
                success=True,
                data=partner._get_api_data(include_addresses=True),
                message='Profile updated successfully'
            )
            
        except Exception as e:
            print('Error updating profile: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to update profile',
                status=500
            )

    @http.route(
        '/api/v1/user/addresses',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_addresses(self, **kwargs):
        """
        Get all user addresses.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to view your addresses',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            if not partner:
                return api_response(
                    success=False,
                    error='Partner not found',
                    message='User has no associated partner',
                    status=400
                )
            
            # Get all addresses
            addresses = partner.child_ids.filtered(
                lambda p: p.type in ('delivery', 'invoice', 'contact')
            )
            
            addresses_data = [{
                'id': addr.id,
                'type': addr.type,
                'name': addr.name,
                'street': addr.street or '',
                'street2': addr.street2 or '',
                'city': addr.city or '',
                'zip': addr.zip or '',
                'country': {
                    'id': addr.country_id.id,
                    'name': addr.country_id.name,
                    'code': addr.country_id.code,
                } if addr.country_id else None,
                'state': {
                    'id': addr.state_id.id,
                    'name': addr.state_id.name,
                    'code': addr.state_id.code,
                } if addr.state_id else None,
                'phone': addr.phone or '',
                'email': addr.email or '',
            } for addr in addresses]
            
            # Include main address
            main_address = {
                'id': partner.id,
                'type': 'main',
                'name': partner.name,
                'street': partner.street or '',
                'street2': partner.street2 or '',
                'city': partner.city or '',
                'zip': partner.zip or '',
                'country': {
                    'id': partner.country_id.id,
                    'name': partner.country_id.name,
                    'code': partner.country_id.code,
                } if partner.country_id else None,
                'state': {
                    'id': partner.state_id.id,
                    'name': partner.state_id.name,
                    'code': partner.state_id.code,
                } if partner.state_id else None,
                'phone': partner.phone or '',
                'email': partner.email or '',
            }
            
            return api_response(
                success=True,
                data={
                    'main': main_address,
                    'addresses': addresses_data,
                },
                message=f'Found {len(addresses_data)} addresses'
            )
            
        except Exception as e:
            print('Error getting addresses: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get addresses',
                status=500
            )

    @http.route(
        '/api/v1/user/addresses',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def add_address(self, **kwargs):
        """
        Add a new address.
        
        Expected JSON body:
        {
            "type": "delivery",  // delivery, invoice, contact
            "name": "John Doe",
            "street": "123 Main St",
            "street2": "Apt 4",
            "city": "New York",
            "zip": "10001",
            "country_id": 233,
            "state_id": 39,
            "phone": "+1234567890"
        }
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to add an address',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            if not partner:
                return api_response(
                    success=False,
                    error='Partner not found',
                    message='User has no associated partner',
                    status=400
                )
            
            data = json.loads(request.httprequest.data or '{}')
            
            # Validate required fields
            required_fields = ['name', 'street', 'city', 'country_id']
            for field in required_fields:
                if not data.get(field):
                    return api_response(
                        success=False,
                        error='Missing field',
                        message=f'{field} is required',
                        status=400
                    )
            
            # Create address
            address_type = data.get('type', 'delivery')
            if address_type not in ('delivery', 'invoice', 'contact'):
                address_type = 'delivery'
            
            address_vals = {
                'parent_id': partner.id,
                'type': address_type,
                'name': data['name'],
                'street': data.get('street', ''),
                'street2': data.get('street2', ''),
                'city': data.get('city', ''),
                'zip': data.get('zip', ''),
                'country_id': int(data['country_id']),
                'phone': data.get('phone', ''),
                'email': data.get('email', partner.email),
            }
            
            if data.get('state_id'):
                address_vals['state_id'] = int(data['state_id'])
            
            new_address = request.env['res.partner'].sudo().create(address_vals)
            
            return api_response(
                success=True,
                data={
                    'id': new_address.id,
                    'type': new_address.type,
                    'name': new_address.name,
                    'street': new_address.street or '',
                    'street2': new_address.street2 or '',
                    'city': new_address.city or '',
                    'zip': new_address.zip or '',
                    'country': {
                        'id': new_address.country_id.id,
                        'name': new_address.country_id.name,
                    } if new_address.country_id else None,
                    'state': {
                        'id': new_address.state_id.id,
                        'name': new_address.state_id.name,
                    } if new_address.state_id else None,
                    'phone': new_address.phone or '',
                },
                message='Address added successfully'
            )
            
        except Exception as e:
            print('Error adding address: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to add address',
                status=500
            )

    @http.route(
        '/api/v1/user/addresses/<int:address_id>',
        type='http',
        auth='public',
        methods=['PUT', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def update_address(self, address_id, **kwargs):
        """
        Update an existing address.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to update an address',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            # Find address
            address = request.env['res.partner'].sudo().browse(address_id)
            
            if not address.exists():
                return api_response(
                    success=False,
                    error='Address not found',
                    message=f'Address with ID {address_id} not found',
                    status=404
                )
            
            # Check ownership
            if address.parent_id.id != partner.id and address.id != partner.id:
                return api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this address',
                    status=403
                )
            
            data = json.loads(request.httprequest.data or '{}')
            
            # Allowed fields
            allowed_fields = [
                'name', 'street', 'street2', 'city', 'zip',
                'country_id', 'state_id', 'phone'
            ]
            
            address_vals = {}
            for field in allowed_fields:
                if field in data:
                    value = data[field]
                    if field in ['country_id', 'state_id'] and value:
                        value = int(value)
                    address_vals[field] = value
            
            if address_vals:
                address.write(address_vals)
            
            return api_response(
                success=True,
                data={
                    'id': address.id,
                    'name': address.name,
                    'street': address.street or '',
                    'city': address.city or '',
                },
                message='Address updated successfully'
            )
            
        except Exception as e:
            print('Error updating address: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to update address',
                status=500
            )

    @http.route(
        '/api/v1/user/addresses/<int:address_id>',
        type='http',
        auth='public',
        methods=['DELETE', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def delete_address(self, address_id, **kwargs):
        """
        Delete an address.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to delete an address',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            # Find address
            address = request.env['res.partner'].sudo().browse(address_id)
            
            if not address.exists():
                return api_response(
                    success=False,
                    error='Address not found',
                    message=f'Address with ID {address_id} not found',
                    status=404
                )
            
            # Check ownership - must be a child of partner
            if address.parent_id.id != partner.id:
                return api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this address',
                    status=403
                )
            
            # Cannot delete main address
            if address.id == partner.id:
                return api_response(
                    success=False,
                    error='Cannot delete',
                    message='Cannot delete main address',
                    status=400
                )
            
            address.unlink()
            
            return api_response(
                success=True,
                data=None,
                message='Address deleted successfully'
            )
            
        except Exception as e:
            print('Error deleting address: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to delete address',
                status=500
            )

    @http.route(
        '/api/v1/user/change-password',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def change_password(self, **kwargs):
        """
        Change user password.
        
        Expected JSON body:
        {
            "current_password": "oldpass123",
            "new_password": "newpass123"
        }
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to change your password',
                    status=401
                )
            
            data = json.loads(request.httprequest.data or '{}')
            
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return api_response(
                    success=False,
                    error='Missing fields',
                    message='Current password and new password are required',
                    status=400
                )
            
            if len(new_password) < 8:
                return api_response(
                    success=False,
                    error='Weak password',
                    message='New password must be at least 8 characters',
                    status=400
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            
            # Verify current password
            try:
                request.env['res.users']._check_credentials({
                    'login': user.login,
                    'password': current_password,
                    'type': 'password'
                }, {'interactive': False})
            except Exception:
                return api_response(
                    success=False,
                    error='Invalid password',
                    message='Current password is incorrect',
                    status=400
                )
            
            # Change password
            user.write({'password': new_password})
            
            return api_response(
                success=True,
                data=None,
                message='Password changed successfully'
            )
            
        except Exception as e:
            print('Error changing password: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to change password',
                status=500
            )
