# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError

from .main import api_response, cors_handler, require_auth

_logger = logging.getLogger(__name__)


class EcommerceApiOrders(http.Controller):
    """
    Orders controller for E-commerce API.
    Handles order creation and order history.
    """

    def _format_order_line(self, line):
        """Format order line data for API response."""
        product = line.product_id
        template = product.product_tmpl_id
        
        return {
            'id': line.id,
            'product_id': template.id,
            'variant_id': product.id,
            'name': line.name,
            'product_name': template.name,
            'sku': product.default_code or '',
            'image': f'/web/image/product.product/{product.id}/image_256',
            'quantity': line.product_uom_qty,
            'price_unit': line.price_unit,
            'price_subtotal': line.price_subtotal,
            'price_tax': line.price_tax,
            'price_total': line.price_total,
            'discount': line.discount,
        }

    def _format_order(self, order, include_lines=True):
        """Format order data for API response."""
        data = {
            'id': order.id,
            'name': order.name,
            'state': order.state,
            'state_label': dict(order._fields['state'].selection).get(order.state, order.state),
            'date_order': order.date_order.isoformat() if order.date_order else None,
            'commitment_date': order.commitment_date.isoformat() if order.commitment_date else None,
            'create_date': order.create_date.isoformat() if order.create_date else None,
            'subtotal': order.amount_untaxed,
            'tax_total': order.amount_tax,
            'total': order.amount_total,
            'currency': {
                'symbol': order.currency_id.symbol,
                'position': order.currency_id.position,
                'code': order.currency_id.name,
            } if order.currency_id else None,
            'partner': {
                'id': order.partner_id.id,
                'name': order.partner_id.name,
                'email': order.partner_id.email,
                'phone': order.partner_id.phone,
            } if order.partner_id else None,
            'invoice_address': {
                'id': order.partner_invoice_id.id,
                'name': order.partner_invoice_id.name,
                'street': order.partner_invoice_id.street,
                'street2': order.partner_invoice_id.street2,
                'city': order.partner_invoice_id.city,
                'zip': order.partner_invoice_id.zip,
                'country': order.partner_invoice_id.country_id.name if order.partner_invoice_id.country_id else None,
                'state': order.partner_invoice_id.state_id.name if order.partner_invoice_id.state_id else None,
                'phone': order.partner_invoice_id.phone,
            } if order.partner_invoice_id else None,
            'shipping_address': {
                'id': order.partner_shipping_id.id,
                'name': order.partner_shipping_id.name,
                'street': order.partner_shipping_id.street,
                'street2': order.partner_shipping_id.street2,
                'city': order.partner_shipping_id.city,
                'zip': order.partner_shipping_id.zip,
                'country': order.partner_shipping_id.country_id.name if order.partner_shipping_id.country_id else None,
                'state': order.partner_shipping_id.state_id.name if order.partner_shipping_id.state_id else None,
                'phone': order.partner_shipping_id.phone,
            } if order.partner_shipping_id else None,
            'note': order.note or '',
            'client_order_ref': order.client_order_ref or '',
        }
        
        if include_lines:
            data['lines'] = [
                self._format_order_line(line)
                for line in order.order_line
                if not line.is_delivery and line.product_id
            ]
            data['line_count'] = len(data['lines'])
        
        return data

    @http.route(
        '/api/v1/orders',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_orders(self, **kwargs):
        """
        Get order history for the current user.
        Requires authentication.
        
        Query parameters:
        - page: Page number (default: 1)
        - limit: Orders per page (default: 10)
        - state: Filter by state (draft, sent, sale, cancel)
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to view your orders',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            if not partner:
                return api_response(
                    success=False,
                    error='No partner found',
                    message='User has no associated partner',
                    status=400
                )
            
            # Parse parameters
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 10)), 50)
            state = kwargs.get('state')
            offset = (page - 1) * limit
            
            # Build domain
            domain = [
                ('partner_id', '=', partner.id),
                ('state', '!=', 'draft'),  # Don't show draft/cart orders
            ]
            
            if state and state in ['sent', 'sale', 'cancel']:
                domain.append(('state', '=', state))
            
            SaleOrder = request.env['sale.order'].sudo()
            
            # Get total count
            total_count = SaleOrder.search_count(domain)
            
            # Get orders
            orders = SaleOrder.search(
                domain,
                order='date_order desc, id desc',
                limit=limit,
                offset=offset
            )
            
            orders_data = [
                self._format_order(order, include_lines=False)
                for order in orders
            ]
            
            total_pages = (total_count + limit - 1) // limit
            
            return api_response(
                success=True,
                data={
                    'orders': orders_data,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total_count,
                        'total_pages': total_pages,
                        'has_next': page < total_pages,
                        'has_prev': page > 1,
                    }
                },
                message=f'Found {total_count} orders'
            )
            
        except Exception as e:
            _logger.exception('Error getting orders: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get orders',
                status=500
            )

    @http.route(
        '/api/v1/orders/<int:order_id>',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_order(self, order_id, **kwargs):
        """
        Get detailed order information.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to view order details',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            order = request.env['sale.order'].sudo().browse(order_id)
            
            if not order.exists():
                return api_response(
                    success=False,
                    error='Order not found',
                    message=f'Order with ID {order_id} not found',
                    status=404
                )
            
            # Check ownership
            if order.partner_id.id != partner.id:
                return api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this order',
                    status=403
                )
            
            order_data = self._format_order(order, include_lines=True)
            
            return api_response(
                success=True,
                data=order_data,
                message='Order details retrieved'
            )
            
        except Exception as e:
            _logger.exception('Error getting order: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get order',
                status=500
            )

    @http.route(
        '/api/v1/orders/create',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def create_order(self, **kwargs):
        """
        Create an order from the current cart.
        
        Expected JSON body:
        {
            "shipping_address": {
                "name": "John Doe",
                "street": "123 Main St",
                "street2": "Apt 4",  // Optional
                "city": "New York",
                "zip": "10001",
                "country_id": 233,
                "state_id": 39,      // Optional
                "phone": "+1234567890",
                "email": "john@example.com"  // Required for guests
            },
            "billing_address": {  // Optional, same as shipping if not provided
                ...
            },
            "note": "Special instructions",  // Optional
            "use_same_address": true  // Optional, default true
        }
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            
            order_id = request.session.get('sale_order_id')
            if not order_id:
                return api_response(
                    success=False,
                    error='Cart is empty',
                    message='No items in cart to checkout',
                    status=400
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists() or order.state != 'draft':
                return api_response(
                    success=False,
                    error='Cart not found',
                    message='No active cart found',
                    status=404
                )
            
            if not order.order_line:
                return api_response(
                    success=False,
                    error='Cart is empty',
                    message='No items in cart to checkout',
                    status=400
                )
            
            shipping_address = data.get('shipping_address', {})
            billing_address = data.get('billing_address', {})
            use_same_address = data.get('use_same_address', True)
            note = data.get('note', '')
            
            # Validate shipping address
            required_fields = ['name', 'street', 'city', 'country_id']
            for field in required_fields:
                if not shipping_address.get(field):
                    return api_response(
                        success=False,
                        error='Missing address field',
                        message=f'{field} is required in shipping address',
                        status=400
                    )
            
            Partner = request.env['res.partner'].sudo()
            
            # Handle authenticated vs guest checkout
            if request.session.uid:
                user = request.env['res.users'].sudo().browse(request.session.uid)
                main_partner = user.partner_id
                
                # Create or find shipping address
                shipping_partner = self._create_or_update_address(
                    main_partner, shipping_address, 'delivery'
                )
                
                # Handle billing address
                if use_same_address or not billing_address:
                    billing_partner = shipping_partner
                else:
                    billing_partner = self._create_or_update_address(
                        main_partner, billing_address, 'invoice'
                    )
                
                # Update order partner
                order.write({
                    'partner_id': main_partner.id,
                    'partner_shipping_id': shipping_partner.id,
                    'partner_invoice_id': billing_partner.id,
                    'note': note,
                })
            else:
                # Guest checkout
                config = request.env['ecommerce.api.config'].sudo().get_config()
                if not config.guest_checkout_enabled:
                    return api_response(
                        success=False,
                        error='Login required',
                        message='Please login to complete checkout',
                        status=401
                    )
                
                email = shipping_address.get('email')
                if not email:
                    return api_response(
                        success=False,
                        error='Email required',
                        message='Email is required for guest checkout',
                        status=400
                    )
                
                # Create guest partner
                guest_partner = Partner.create({
                    'name': shipping_address['name'],
                    'email': email,
                    'phone': shipping_address.get('phone', ''),
                    'street': shipping_address.get('street', ''),
                    'street2': shipping_address.get('street2', ''),
                    'city': shipping_address.get('city', ''),
                    'zip': shipping_address.get('zip', ''),
                    'country_id': int(shipping_address['country_id']),
                    'state_id': int(shipping_address['state_id']) if shipping_address.get('state_id') else False,
                    'ecommerce_registered': False,
                })
                
                order.write({
                    'partner_id': guest_partner.id,
                    'partner_shipping_id': guest_partner.id,
                    'partner_invoice_id': guest_partner.id,
                    'note': note,
                })
            
            # Confirm the order
            try:
                order.action_confirm()
            except (ValidationError, UserError) as e:
                return api_response(
                    success=False,
                    error='Order confirmation failed',
                    message=str(e),
                    status=400
                )
            
            # Clear cart from session
            request.session['sale_order_id'] = None
            
            order_data = self._format_order(order, include_lines=True)
            
            return api_response(
                success=True,
                data=order_data,
                message=f'Order {order.name} confirmed successfully'
            )
            
        except Exception as e:
            _logger.exception('Error creating order: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to create order',
                status=500
            )

    def _create_or_update_address(self, parent_partner, address_data, address_type):
        """Create or find an address for the partner."""
        Partner = request.env['res.partner'].sudo()
        
        # Try to find existing address with same details
        domain = [
            ('parent_id', '=', parent_partner.id),
            ('type', '=', address_type),
            ('name', '=', address_data.get('name')),
            ('street', '=', address_data.get('street', '')),
            ('city', '=', address_data.get('city', '')),
            ('zip', '=', address_data.get('zip', '')),
            ('country_id', '=', int(address_data['country_id'])),
        ]
        
        existing = Partner.search(domain, limit=1)
        if existing:
            return existing
        
        # Create new address
        return Partner.create({
            'parent_id': parent_partner.id,
            'type': address_type,
            'name': address_data['name'],
            'street': address_data.get('street', ''),
            'street2': address_data.get('street2', ''),
            'city': address_data.get('city', ''),
            'zip': address_data.get('zip', ''),
            'country_id': int(address_data['country_id']),
            'state_id': int(address_data['state_id']) if address_data.get('state_id') else False,
            'phone': address_data.get('phone', ''),
            'email': address_data.get('email', parent_partner.email),
        })

    @http.route(
        '/api/v1/orders/<int:order_id>/cancel',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def cancel_order(self, order_id, **kwargs):
        """
        Cancel an order (only if not yet processed).
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to cancel orders',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            order = request.env['sale.order'].sudo().browse(order_id)
            
            if not order.exists():
                return api_response(
                    success=False,
                    error='Order not found',
                    message=f'Order with ID {order_id} not found',
                    status=404
                )
            
            # Check ownership
            if order.partner_id.id != partner.id:
                return api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this order',
                    status=403
                )
            
            # Check if order can be cancelled
            if order.state not in ['draft', 'sent', 'sale']:
                return api_response(
                    success=False,
                    error='Cannot cancel',
                    message='This order cannot be cancelled',
                    status=400
                )
            
            # Check if already shipped/invoiced
            if hasattr(order, 'delivery_count') and order.delivery_count > 0:
                return api_response(
                    success=False,
                    error='Cannot cancel',
                    message='Order has already been shipped',
                    status=400
                )
            
            try:
                order.action_cancel()
            except (ValidationError, UserError) as e:
                return api_response(
                    success=False,
                    error='Cancellation failed',
                    message=str(e),
                    status=400
                )
            
            return api_response(
                success=True,
                data=self._format_order(order, include_lines=False),
                message=f'Order {order.name} has been cancelled'
            )
            
        except Exception as e:
            _logger.exception('Error cancelling order: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to cancel order',
                status=500
            )

    @http.route(
        '/api/v1/orders/<int:order_id>/reorder',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def reorder(self, order_id, **kwargs):
        """
        Add all items from a previous order to the cart.
        """
        try:
            if not request.session.uid:
                return api_response(
                    success=False,
                    error='Authentication required',
                    message='Please login to reorder',
                    status=401
                )
            
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            
            order = request.env['sale.order'].sudo().browse(order_id)
            
            if not order.exists():
                return api_response(
                    success=False,
                    error='Order not found',
                    message=f'Order with ID {order_id} not found',
                    status=404
                )
            
            # Check ownership
            if order.partner_id.id != partner.id:
                return api_response(
                    success=False,
                    error='Access denied',
                    message='You do not have access to this order',
                    status=403
                )
            
            # Get or create cart
            cart = self._get_or_create_cart()
            
            # Add items to cart
            for line in order.order_line:
                if line.is_delivery or not line.product_id:
                    continue
                
                # Check if product is still available
                if not line.product_id.active or not line.product_id.sale_ok:
                    continue
                
                if hasattr(cart, '_cart_update'):
                    cart._cart_update(
                        product_id=line.product_id.id,
                        add_qty=line.product_uom_qty,
                    )
                else:
                    cart.write({
                        'order_line': [(0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'name': line.product_id.display_name,
                        })]
                    })
            
            request.session['sale_order_id'] = cart.id
            
            return api_response(
                success=True,
                data={'cart_id': cart.id},
                message='Items added to cart'
            )
            
        except Exception as e:
            _logger.exception('Error reordering: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to reorder',
                status=500
            )

    def _get_or_create_cart(self):
        """Get the current cart or create a new one."""
        SaleOrder = request.env['sale.order'].sudo()
        order_id = request.session.get('sale_order_id')
        
        if order_id:
            order = SaleOrder.browse(order_id)
            if order.exists() and order.state == 'draft':
                return order
        
        # Create new cart
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
        else:
            partner = request.env.ref('base.public_partner')
        
        order = SaleOrder.create({
            'partner_id': partner.id,
            'state': 'draft',
        })
        request.session['sale_order_id'] = order.id
        
        return order
