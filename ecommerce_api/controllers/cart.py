# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, _
from odoo.http import request

from .main import api_response, cors_handler, require_auth

_logger = logging.getLogger(__name__)


class EcommerceApiCart(http.Controller):
    """
    Shopping cart controller for E-commerce API.
    Handles cart operations: add, update, remove, clear.
    """

    def _get_or_create_cart(self):
        """
        Get the current cart or create a new one.
        Uses Odoo's built-in cart management.
        """
        # Use website's sale_get_order method if available
        if hasattr(request, 'website') and request.website:
            order = request.website.sale_get_order(force_create=True)
        else:
            # Fallback: get cart from session or create new
            SaleOrder = request.env['sale.order'].sudo()
            order_id = request.session.get('sale_order_id')
            
            if order_id:
                order = SaleOrder.browse(order_id)
                if not order.exists() or order.state != 'draft':
                    order = None
            else:
                order = None
            
            if not order:
                # Create new cart
                if request.session.uid:
                    user = request.env['res.users'].sudo().browse(request.session.uid)
                    partner = user.partner_id
                else:
                    # Guest cart - use public partner
                    partner = request.env.ref('base.public_partner')
                
                order = SaleOrder.create({
                    'partner_id': partner.id,
                    'state': 'draft',
                })
                request.session['sale_order_id'] = order.id
        
        return order

    def _format_cart_line(self, line):
        """Format cart line data for API response."""
        product = line.product_id
        template = product.product_tmpl_id
        
        return {
            'id': line.id,
            'product_id': template.id,
            'variant_id': product.id,
            'name': line.name or product.display_name,
            'product_name': template.name,
            'variant_name': product.display_name if template.product_variant_count > 1 else None,
            'sku': product.default_code or '',
            'image': f'/web/image/product.product/{product.id}/image_256',
            'quantity': line.product_uom_qty,
            'price_unit': line.price_unit,
            'price_subtotal': line.price_subtotal,
            'price_tax': line.price_tax,
            'price_total': line.price_total,
            'discount': line.discount,
            'uom': {
                'id': line.product_uom.id,
                'name': line.product_uom.name,
            } if line.product_uom else None,
            'attributes': [{
                'attribute': ptav.attribute_id.name,
                'value': ptav.product_attribute_value_id.name,
            } for ptav in product.product_template_attribute_value_ids],
        }

    def _format_cart(self, order):
        """Format cart data for API response."""
        if not order:
            return {
                'id': None,
                'lines': [],
                'line_count': 0,
                'item_count': 0,
                'subtotal': 0,
                'tax_total': 0,
                'total': 0,
                'currency': None,
            }
        
        lines = [
            self._format_cart_line(line) 
            for line in order.order_line 
            if not line.is_delivery and line.product_id
        ]
        
        return {
            'id': order.id,
            'name': order.name,
            'lines': lines,
            'line_count': len(lines),
            'item_count': sum(line['quantity'] for line in lines),
            'subtotal': order.amount_untaxed,
            'tax_total': order.amount_tax,
            'total': order.amount_total,
            'currency': {
                'symbol': order.currency_id.symbol,
                'position': order.currency_id.position,
                'code': order.currency_id.name,
            } if order.currency_id else None,
            'partner_id': order.partner_id.id if order.partner_id else None,
        }

    @http.route(
        '/api/v1/cart',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_cart(self, **kwargs):
        """
        Get the current shopping cart.
        """
        try:
            order_id = request.session.get('sale_order_id')
            
            if not order_id:
                return api_response(
                    success=True,
                    data=self._format_cart(None),
                    message='Cart is empty'
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            
            if not order.exists() or order.state != 'draft':
                request.session['sale_order_id'] = None
                return api_response(
                    success=True,
                    data=self._format_cart(None),
                    message='Cart is empty'
                )
            
            cart_data = self._format_cart(order)
            
            return api_response(
                success=True,
                data=cart_data,
                message=f'Cart has {cart_data["item_count"]} items'
            )
            
        except Exception as e:
            _logger.exception('Error getting cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/add',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def add_to_cart(self, **kwargs):
        """
        Add a product to cart.
        
        Expected JSON body:
        {
            "product_id": 123,  // Product template ID
            "variant_id": 456,  // Optional: Product variant ID
            "quantity": 1,      // Optional: Quantity to add (default: 1)
        }
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            
            product_id = data.get('product_id')
            variant_id = data.get('variant_id')
            quantity = float(data.get('quantity', 1))
            
            if not product_id and not variant_id:
                return api_response(
                    success=False,
                    error='Missing product',
                    message='Product ID or variant ID is required',
                    status=400
                )
            
            if quantity <= 0:
                return api_response(
                    success=False,
                    error='Invalid quantity',
                    message='Quantity must be greater than 0',
                    status=400
                )
            
            # Get the product
            if variant_id:
                product = request.env['product.product'].sudo().browse(int(variant_id))
                if not product.exists():
                    return api_response(
                        success=False,
                        error='Product not found',
                        message=f'Variant with ID {variant_id} not found',
                        status=404
                    )
            else:
                template = request.env['product.template'].sudo().browse(int(product_id))
                if not template.exists():
                    return api_response(
                        success=False,
                        error='Product not found',
                        message=f'Product with ID {product_id} not found',
                        status=404
                    )
                
                # Get the default variant
                if template.product_variant_count == 1:
                    product = template.product_variant_id
                else:
                    # Need to specify variant for products with multiple variants
                    return api_response(
                        success=False,
                        error='Variant required',
                        message='This product has multiple variants. Please specify variant_id.',
                        status=400
                    )
            
            # Get or create cart
            order = self._get_or_create_cart()
            
            # Use _cart_update if available (website_sale)
            if hasattr(order, '_cart_update'):
                result = order._cart_update(
                    product_id=product.id,
                    add_qty=quantity,
                )
            else:
                # Manual cart update
                existing_line = order.order_line.filtered(
                    lambda l: l.product_id.id == product.id
                )
                
                if existing_line:
                    existing_line[0].product_uom_qty += quantity
                else:
                    order.write({
                        'order_line': [(0, 0, {
                            'product_id': product.id,
                            'product_uom_qty': quantity,
                            'name': product.display_name,
                        })]
                    })
            
            # Store cart in session
            request.session['sale_order_id'] = order.id
            
            cart_data = self._format_cart(order)
            
            return api_response(
                success=True,
                data=cart_data,
                message=f'Added {quantity} x {product.name} to cart'
            )
            
        except Exception as e:
            _logger.exception('Error adding to cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to add to cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/update',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def update_cart(self, **kwargs):
        """
        Update cart line quantity.
        
        Expected JSON body:
        {
            "line_id": 123,     // Cart line ID
            "quantity": 2,      // New quantity
        }
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            
            line_id = data.get('line_id')
            quantity = float(data.get('quantity', 0))
            
            if not line_id:
                return api_response(
                    success=False,
                    error='Missing line_id',
                    message='Cart line ID is required',
                    status=400
                )
            
            order_id = request.session.get('sale_order_id')
            if not order_id:
                return api_response(
                    success=False,
                    error='Cart not found',
                    message='No active cart found',
                    status=404
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists() or order.state != 'draft':
                return api_response(
                    success=False,
                    error='Cart not found',
                    message='No active cart found',
                    status=404
                )
            
            # Find the line
            line = order.order_line.filtered(lambda l: l.id == int(line_id))
            if not line:
                return api_response(
                    success=False,
                    error='Line not found',
                    message=f'Cart line with ID {line_id} not found',
                    status=404
                )
            
            if quantity <= 0:
                # Remove the line
                line.unlink()
                message = 'Item removed from cart'
            else:
                # Update quantity
                if hasattr(order, '_cart_update'):
                    order._cart_update(
                        product_id=line.product_id.id,
                        line_id=line.id,
                        set_qty=quantity,
                    )
                else:
                    line.product_uom_qty = quantity
                message = 'Cart updated'
            
            cart_data = self._format_cart(order)
            
            return api_response(
                success=True,
                data=cart_data,
                message=message
            )
            
        except Exception as e:
            _logger.exception('Error updating cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to update cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/remove/<int:line_id>',
        type='http',
        auth='public',
        methods=['DELETE', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def remove_from_cart(self, line_id, **kwargs):
        """
        Remove a line from the cart.
        """
        try:
            order_id = request.session.get('sale_order_id')
            if not order_id:
                return api_response(
                    success=False,
                    error='Cart not found',
                    message='No active cart found',
                    status=404
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists() or order.state != 'draft':
                return api_response(
                    success=False,
                    error='Cart not found',
                    message='No active cart found',
                    status=404
                )
            
            # Find and remove the line
            line = order.order_line.filtered(lambda l: l.id == line_id)
            if not line:
                return api_response(
                    success=False,
                    error='Line not found',
                    message=f'Cart line with ID {line_id} not found',
                    status=404
                )
            
            product_name = line.product_id.name
            line.unlink()
            
            cart_data = self._format_cart(order)
            
            return api_response(
                success=True,
                data=cart_data,
                message=f'Removed {product_name} from cart'
            )
            
        except Exception as e:
            _logger.exception('Error removing from cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to remove from cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/clear',
        type='http',
        auth='public',
        methods=['DELETE', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def clear_cart(self, **kwargs):
        """
        Clear all items from the cart.
        """
        try:
            order_id = request.session.get('sale_order_id')
            if not order_id:
                return api_response(
                    success=True,
                    data=self._format_cart(None),
                    message='Cart is already empty'
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            if order.exists() and order.state == 'draft':
                # Remove all lines
                order.order_line.unlink()
            
            cart_data = self._format_cart(order if order.exists() else None)
            
            return api_response(
                success=True,
                data=cart_data,
                message='Cart cleared'
            )
            
        except Exception as e:
            _logger.exception('Error clearing cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to clear cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/count',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def cart_count(self, **kwargs):
        """
        Get cart item count (lightweight endpoint for UI).
        """
        try:
            order_id = request.session.get('sale_order_id')
            if not order_id:
                return api_response(
                    success=True,
                    data={'count': 0, 'total': 0},
                    message='Cart is empty'
                )
            
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists() or order.state != 'draft':
                return api_response(
                    success=True,
                    data={'count': 0, 'total': 0},
                    message='Cart is empty'
                )
            
            count = sum(line.product_uom_qty for line in order.order_line if not line.is_delivery)
            
            return api_response(
                success=True,
                data={
                    'count': int(count),
                    'total': order.amount_total,
                    'currency': order.currency_id.symbol,
                },
                message=f'Cart has {int(count)} items'
            )
            
        except Exception as e:
            _logger.exception('Error getting cart count: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get cart count',
                status=500
            )
