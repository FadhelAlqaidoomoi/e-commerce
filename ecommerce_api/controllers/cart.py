# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import uuid
import logging

from odoo import http, fields, _
from odoo.http import request

from .main import api_response, cors_handler, require_auth, verify_cart_ownership, validate_quantity

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

            # SECURITY: Verify cart ownership
            is_valid, error_response = verify_cart_ownership(order)
            if not is_valid:
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
            print('Error getting cart: %s', str(e))
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

            if not product_id and not variant_id:
                return api_response(
                    success=False,
                    error='Missing product',
                    message='Product ID or variant ID is required',
                    status=400
                )

            # SECURITY: Validate quantity with bounds checking
            is_valid, quantity, error_msg = validate_quantity(data.get('quantity', 1))
            if not is_valid:
                return api_response(
                    success=False,
                    error='Invalid quantity',
                    message=error_msg,
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
            print('Error adding to cart: %s', str(e))
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

            # SECURITY: Verify cart ownership
            is_valid, error_response = verify_cart_ownership(order)
            if not is_valid:
                return error_response

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
            print('Error updating cart: %s', str(e))
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

            # SECURITY: Verify cart ownership
            is_valid, error_response = verify_cart_ownership(order)
            if not is_valid:
                return error_response

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
            print('Error removing from cart: %s', str(e))
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
                # SECURITY: Verify cart ownership before clearing
                is_valid, error_response = verify_cart_ownership(order)
                if is_valid:
                    # Remove all lines
                    order.order_line.unlink()

            cart_data = self._format_cart(order if order.exists() else None)
            
            return api_response(
                success=True,
                data=cart_data,
                message='Cart cleared'
            )
            
        except Exception as e:
            print('Error clearing cart: %s', str(e))
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

            # SECURITY: Verify cart ownership
            is_valid, error_response = verify_cart_ownership(order)
            if not is_valid:
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
            print('Error getting cart count: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get cart count',
                status=500
            )

    # ==================== Cart Token Endpoints ====================

    @http.route(
        '/api/v1/cart/token',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_cart_token(self, **kwargs):
        """
        Get or create a cart token for the current cart.
        Returns existing valid token if cart already has one.

        Response:
        {
            "token": "uuid-string",
            "expires_at": "ISO datetime",
            "cart_id": 123
        }
        """
        try:
            order = self._get_or_create_cart()

            CartToken = request.env['ecommerce.cart.token'].sudo()

            # Look for existing valid token
            token_record = CartToken.get_valid_token_for_order(order.id)

            if not token_record:
                # Generate new token
                token_record = CartToken.generate_token(order.id)
            else:
                # Refresh expiry on access
                token_record.refresh_expiry()

            # Store cart in session
            request.session['sale_order_id'] = order.id

            return api_response(
                success=True,
                data={
                    'token': token_record.token,
                    'expires_at': token_record.expires_at.isoformat(),
                    'cart_id': order.id,
                },
                message='Cart token retrieved'
            )

        except Exception as e:
            print('Error getting cart token: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get cart token',
                status=500
            )

    @http.route(
        '/api/v1/cart/restore',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def restore_cart_by_token(self, **kwargs):
        """
        Restore a cart using a token.

        Expected JSON body:
        {
            "token": "uuid-string"
        }

        This endpoint:
        1. Validates the token
        2. Checks if cart still exists and is draft
        3. Sets the cart in the current session
        4. For authenticated users: transfers cart to their partner
        5. Returns cart data
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            token_str = data.get('token')

            if not token_str:
                return api_response(
                    success=False,
                    error='Missing token',
                    message='Cart token is required',
                    status=400
                )

            # Validate UUID format
            try:
                uuid.UUID(token_str)
            except ValueError:
                return api_response(
                    success=False,
                    error='Invalid token format',
                    message='Invalid cart token format',
                    status=400
                )

            CartToken = request.env['ecommerce.cart.token'].sudo()
            token_record = CartToken.find_by_token(token_str)

            if not token_record:
                return api_response(
                    success=False,
                    error='TOKEN_NOT_FOUND',
                    message='Cart token not found or expired',
                    status=404
                )

            is_valid, error_code, error_msg = token_record.validate_token()
            if not is_valid:
                return api_response(
                    success=False,
                    error=error_code,
                    message=error_msg,
                    status=400
                )

            order = token_record.sale_order_id

            # Handle authenticated user trying to restore guest cart
            if request.session.uid:
                user = request.env['res.users'].sudo().browse(request.session.uid)
                # Transfer cart to authenticated user
                order.write({'partner_id': user.partner_id.id})
                token_record.claim_token(user.partner_id)
                response_token = None
            else:
                token_record.refresh_expiry()
                response_token = token_record.token

            # Set cart in session
            request.session['sale_order_id'] = order.id

            cart_data = self._format_cart(order)
            cart_data['token'] = response_token

            return api_response(
                success=True,
                data=cart_data,
                message='Cart restored successfully'
            )

        except Exception as e:
            print('Error restoring cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to restore cart',
                status=500
            )

    @http.route(
        '/api/v1/cart/merge',
        type='http',
        auth='public',
        methods=['POST', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    @require_auth
    def merge_guest_cart(self, **kwargs):
        """
        Merge a guest cart into the authenticated user's cart.

        Expected JSON body:
        {
            "token": "uuid-string",
            "strategy": "merge" | "replace" | "keep_current"
        }

        Strategies:
        - merge: Add guest cart items to current cart (default)
        - replace: Replace current cart with guest cart
        - keep_current: Keep current cart, discard guest cart
        """
        try:
            data = json.loads(request.httprequest.data or '{}')
            token_str = data.get('token')
            strategy = data.get('strategy', 'merge')

            if not token_str:
                return api_response(
                    success=False,
                    error='Missing token',
                    message='Cart token is required',
                    status=400
                )

            if strategy not in ['merge', 'replace', 'keep_current']:
                return api_response(
                    success=False,
                    error='Invalid strategy',
                    message='Strategy must be: merge, replace, or keep_current',
                    status=400
                )

            # Validate token
            CartToken = request.env['ecommerce.cart.token'].sudo()
            token_record = CartToken.find_by_token(token_str)

            if not token_record:
                return api_response(
                    success=False,
                    error='TOKEN_NOT_FOUND',
                    message='Guest cart not found',
                    status=404
                )

            is_valid, error_code, error_msg = token_record.validate_token()
            if not is_valid:
                return api_response(
                    success=False,
                    error=error_code,
                    message=error_msg,
                    status=400
                )

            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id
            guest_cart = token_record.sale_order_id

            # Get user's current cart (if any)
            user_cart_id = request.session.get('sale_order_id')
            user_cart = None
            if user_cart_id:
                user_cart = request.env['sale.order'].sudo().browse(user_cart_id)
                if not user_cart.exists() or user_cart.state != 'draft':
                    user_cart = None
                elif user_cart.id == guest_cart.id:
                    # Same cart, nothing to merge
                    user_cart = None

            if strategy == 'keep_current':
                # Just discard guest cart
                token_record.claim_token(partner)
                result_cart = user_cart if user_cart else self._get_or_create_cart()

            elif strategy == 'replace':
                # Transfer guest cart to user, discard user's current cart
                if user_cart and user_cart.id != guest_cart.id:
                    user_cart.order_line.unlink()  # Clear current cart
                guest_cart.write({'partner_id': partner.id})
                token_record.claim_token(partner)
                result_cart = guest_cart

            else:  # merge
                if not user_cart:
                    # No current cart, just transfer
                    guest_cart.write({'partner_id': partner.id})
                    result_cart = guest_cart
                else:
                    # Merge items from guest cart to user cart
                    for line in guest_cart.order_line:
                        existing = user_cart.order_line.filtered(
                            lambda l: l.product_id.id == line.product_id.id
                        )
                        if existing:
                            existing[0].product_uom_qty += line.product_uom_qty
                        else:
                            line.copy({'order_id': user_cart.id})
                    result_cart = user_cart

                token_record.claim_token(partner)

            request.session['sale_order_id'] = result_cart.id

            return api_response(
                success=True,
                data=self._format_cart(result_cart),
                message=f'Cart merged using {strategy} strategy'
            )

        except Exception as e:
            print('Error merging cart: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to merge cart',
                status=500
            )
