# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class EcommerceApiConfig(models.Model):
    """
    Configuration model for E-commerce API settings.
    """
    _name = 'ecommerce.api.config'
    _description = 'E-commerce API Configuration'

    name = fields.Char(string='Name', required=True, default='Default')
    active = fields.Boolean(string='Active', default=True)
    
    # CORS Settings
    allowed_origins = fields.Text(
        string='Allowed Origins',
        help='Comma-separated list of allowed origins for CORS. Use * for all origins.',
        default='http://localhost:3000,http://127.0.0.1:3000'
    )
    
    # API Settings
    products_per_page = fields.Integer(
        string='Products Per Page',
        default=20,
        help='Number of products to return per page in API responses.'
    )
    
    # Features
    guest_checkout_enabled = fields.Boolean(
        string='Guest Checkout',
        default=True,
        help='Allow customers to checkout without creating an account.'
    )
    
    registration_enabled = fields.Boolean(
        string='Public Registration',
        default=True,
        help='Allow public user registration through the API.'
    )
    
    # WhatsApp Integration (Future)
    whatsapp_enabled = fields.Boolean(
        string='WhatsApp Integration',
        default=False,
        help='Enable WhatsApp integration for order notifications.'
    )
    
    whatsapp_phone = fields.Char(
        string='WhatsApp Business Phone',
        help='WhatsApp Business phone number for notifications.'
    )

    @api.model
    def get_config(self):
        """Get the active API configuration."""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({'name': 'Default'})
        return config

    def get_allowed_origins_list(self):
        """Return list of allowed origins."""
        self.ensure_one()
        if not self.allowed_origins:
            return ['*']
        origins = [o.strip() for o in self.allowed_origins.split(',')]
        return origins if origins else ['*']


class ResPartner(models.Model):
    """
    Extend partner model for e-commerce API features.
    """
    _inherit = 'res.partner'

    ecommerce_registered = fields.Boolean(
        string='E-commerce Registered',
        default=False,
        help='Customer registered through e-commerce API.'
    )
    
    whatsapp_number = fields.Char(
        string='WhatsApp Number',
        help='Customer WhatsApp number for notifications.'
    )
    
    whatsapp_opt_in = fields.Boolean(
        string='WhatsApp Opt-in',
        default=False,
        help='Customer opted in for WhatsApp notifications.'
    )

    def _get_api_data(self, include_addresses=False):
        """Return partner data formatted for API response."""
        self.ensure_one()
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone or '',
            'mobile': self.mobile or '',
            'street': self.street or '',
            'street2': self.street2 or '',
            'city': self.city or '',
            'zip': self.zip or '',
            'country': {
                'id': self.country_id.id,
                'name': self.country_id.name,
                'code': self.country_id.code,
            } if self.country_id else None,
            'state': {
                'id': self.state_id.id,
                'name': self.state_id.name,
                'code': self.state_id.code,
            } if self.state_id else None,
            'whatsapp_number': self.whatsapp_number or '',
            'whatsapp_opt_in': self.whatsapp_opt_in,
        }
        
        if include_addresses:
            # Get all delivery and invoice addresses
            addresses = self.child_ids.filtered(
                lambda p: p.type in ('delivery', 'invoice')
            )
            data['addresses'] = [{
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
            } for addr in addresses]
        
        return data
