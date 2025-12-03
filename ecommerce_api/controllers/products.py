# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import json
import logging
import base64

from odoo import http, _
from odoo.http import request
from odoo.osv import expression

from .main import api_response, cors_handler

_logger = logging.getLogger(__name__)


class EcommerceApiProducts(http.Controller):
    """
    Products controller for E-commerce API.
    Handles product listing, search, and category management.
    """

    def _get_product_image_url(self, product, image_field='image_512'):
        """Generate URL for product image."""
        if product[image_field]:
            return f'/web/image/product.product/{product.id}/{image_field}'
        elif product.product_tmpl_id.image_512:
            return f'/web/image/product.template/{product.product_tmpl_id.id}/{image_field}'
        return None

    def _get_product_data(self, product, include_variants=False, include_details=False):
        """
        Format product data for API response.
        
        Args:
            product: product.product or product.template record
            include_variants: Include variant information
            include_details: Include detailed description and attributes
        """
        # Handle both product.product and product.template
        if product._name == 'product.product':
            template = product.product_tmpl_id
            variant = product
        else:
            template = product
            variant = template.product_variant_id if template.product_variant_count == 1 else None
        
        # Get website for pricing
        website = request.website if hasattr(request, 'website') else None
        pricelist = website.pricelist_id if website else None
        
        # Calculate price
        if variant and pricelist:
            price = pricelist._get_product_price(variant, 1.0)
        elif variant:
            price = variant.lst_price
        else:
            price = template.list_price
        
        # Base product data
        data = {
            'id': template.id,
            'name': template.name,
            'slug': template.website_slug if hasattr(template, 'website_slug') else str(template.id),
            'description_short': template.description_sale or '',
            'price': price,
            'compare_price': template.compare_list_price if template.compare_list_price > price else None,
            'currency': {
                'symbol': template.currency_id.symbol,
                'position': template.currency_id.position,
                'code': template.currency_id.name,
            },
            'image': self._get_product_image_url(variant or template.product_variant_id, 'image_512'),
            'image_large': self._get_product_image_url(variant or template.product_variant_id, 'image_1024'),
            'is_published': template.is_published if hasattr(template, 'is_published') else True,
            'in_stock': True,  # Will be updated if stock module is installed
            'categories': [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.name.lower().replace(' ', '-'),
            } for cat in template.public_categ_ids] if hasattr(template, 'public_categ_ids') else [],
            'has_variants': template.product_variant_count > 1,
            'variant_count': template.product_variant_count,
        }
        
        # Add variant info if single variant
        if variant:
            data['variant_id'] = variant.id
            data['sku'] = variant.default_code or ''
            data['barcode'] = variant.barcode or ''
        
        # Check stock if module is installed
        if hasattr(variant or template.product_variant_id, 'qty_available'):
            product_for_stock = variant or template.product_variant_id
            data['in_stock'] = product_for_stock.qty_available > 0
            data['qty_available'] = product_for_stock.qty_available
        
        # Include details if requested
        if include_details:
            data['description'] = template.website_description or template.description_sale or ''
            data['description_ecommerce'] = template.description_ecommerce if hasattr(template, 'description_ecommerce') else ''
            
            # Get additional images
            images = []
            if hasattr(template, 'product_template_image_ids'):
                for img in template.product_template_image_ids:
                    images.append({
                        'id': img.id,
                        'url': f'/web/image/product.image/{img.id}/image_1024',
                        'name': img.name,
                    })
            data['additional_images'] = images
            
            # Get attributes
            attributes = []
            for line in template.attribute_line_ids:
                attr = {
                    'id': line.attribute_id.id,
                    'name': line.attribute_id.name,
                    'display_type': line.attribute_id.display_type,
                    'values': [{
                        'id': val.id,
                        'name': val.name,
                        'html_color': val.html_color if hasattr(val, 'html_color') else None,
                        'is_custom': val.is_custom,
                    } for val in line.value_ids]
                }
                attributes.append(attr)
            data['attributes'] = attributes
            
            # Get ribbon if any
            if hasattr(template, 'website_ribbon_id') and template.website_ribbon_id:
                data['ribbon'] = {
                    'id': template.website_ribbon_id.id,
                    'html': template.website_ribbon_id.html,
                    'bg_color': template.website_ribbon_id.bg_color,
                    'text_color': template.website_ribbon_id.text_color,
                }
            
            # Get alternative products (upsell)
            if hasattr(template, 'alternative_product_ids'):
                data['alternative_products'] = [{
                    'id': p.id,
                    'name': p.name,
                    'price': p.list_price,
                    'image': f'/web/image/product.template/{p.id}/image_256',
                } for p in template.alternative_product_ids[:4]]
            
            # Get accessory products (cross-sell)
            if hasattr(template, 'accessory_product_ids'):
                data['accessory_products'] = [{
                    'id': p.id,
                    'name': p.name,
                    'price': p.lst_price,
                    'image': f'/web/image/product.product/{p.id}/image_256',
                } for p in template.accessory_product_ids[:4]]
        
        # Include variants if requested
        if include_variants and template.product_variant_count > 1:
            variants = []
            for var in template.product_variant_ids:
                var_data = {
                    'id': var.id,
                    'name': var.display_name,
                    'sku': var.default_code or '',
                    'price': var.lst_price,
                    'price_extra': var.price_extra,
                    'image': self._get_product_image_url(var, 'image_512'),
                    'in_stock': True,
                    'attribute_values': [{
                        'attribute_id': ptav.attribute_id.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value_id': ptav.product_attribute_value_id.id,
                        'value_name': ptav.product_attribute_value_id.name,
                    } for ptav in var.product_template_attribute_value_ids]
                }
                
                if hasattr(var, 'qty_available'):
                    var_data['in_stock'] = var.qty_available > 0
                    var_data['qty_available'] = var.qty_available
                
                variants.append(var_data)
            
            data['variants'] = variants
        
        return data

    @http.route(
        '/api/v1/products',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_products(self, **kwargs):
        """
        Get list of products with optional filtering and pagination.
        
        Query parameters:
        - page: Page number (default: 1)
        - limit: Products per page (default: 20)
        - category: Category ID to filter by
        - search: Search term for product name/description
        - order: Sort order (name_asc, name_desc, price_asc, price_desc, newest)
        - min_price: Minimum price filter
        - max_price: Maximum price filter
        - in_stock: Filter by stock availability (true/false)
        """
        try:
            # Get config
            config = request.env['ecommerce.api.config'].sudo().get_config()
            
            # Parse parameters
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', config.products_per_page)), 100)
            category_id = kwargs.get('category')
            search = kwargs.get('search', '').strip()
            order = kwargs.get('order', 'name_asc')
            min_price = kwargs.get('min_price')
            max_price = kwargs.get('max_price')
            in_stock = kwargs.get('in_stock')
            
            offset = (page - 1) * limit
            
            # Build domain
            domain = [
                ('sale_ok', '=', True),
                ('active', '=', True),
            ]
            
            # Add is_published filter if website_sale is installed
            ProductTemplate = request.env['product.template'].sudo()
            if 'is_published' in ProductTemplate._fields:
                domain.append(('is_published', '=', True))
            
            # Category filter
            if category_id:
                try:
                    cat_id = int(category_id)
                    domain.append(('public_categ_ids', 'child_of', cat_id))
                except (ValueError, TypeError):
                    pass
            
            # Search filter
            if search:
                search_domain = [
                    '|', '|',
                    ('name', 'ilike', search),
                    ('description_sale', 'ilike', search),
                    ('default_code', 'ilike', search),
                ]
                domain = expression.AND([domain, search_domain])
            
            # Price filters
            if min_price:
                try:
                    domain.append(('list_price', '>=', float(min_price)))
                except (ValueError, TypeError):
                    pass
            
            if max_price:
                try:
                    domain.append(('list_price', '<=', float(max_price)))
                except (ValueError, TypeError):
                    pass
            
            # Sort order
            order_mapping = {
                'name_asc': 'name asc',
                'name_desc': 'name desc',
                'price_asc': 'list_price asc',
                'price_desc': 'list_price desc',
                'newest': 'create_date desc',
            }
            sort_order = order_mapping.get(order, 'name asc')
            
            # Get total count
            total_count = ProductTemplate.search_count(domain)
            
            # Get products
            products = ProductTemplate.search(
                domain,
                order=sort_order,
                limit=limit,
                offset=offset
            )
            
            # Format product data
            products_data = [
                self._get_product_data(p, include_variants=False, include_details=False)
                for p in products
            ]
            
            # Filter by stock if requested
            if in_stock == 'true':
                products_data = [p for p in products_data if p.get('in_stock', True)]
            
            # Calculate pagination
            total_pages = (total_count + limit - 1) // limit
            
            return api_response(
                success=True,
                data={
                    'products': products_data,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total_count,
                        'total_pages': total_pages,
                        'has_next': page < total_pages,
                        'has_prev': page > 1,
                    }
                },
                message=f'Found {total_count} products'
            )
            
        except Exception as e:
            _logger.exception('Error getting products: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get products',
                status=500
            )

    @http.route(
        '/api/v1/products/<int:product_id>',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_product(self, product_id, **kwargs):
        """
        Get detailed product information.
        
        Path parameters:
        - product_id: Product template ID
        
        Query parameters:
        - include_variants: Include all variant details (default: true)
        """
        try:
            include_variants = kwargs.get('include_variants', 'true').lower() == 'true'
            
            product = request.env['product.template'].sudo().browse(product_id)
            
            if not product.exists():
                return api_response(
                    success=False,
                    error='Product not found',
                    message=f'Product with ID {product_id} not found',
                    status=404
                )
            
            # Check if published
            if hasattr(product, 'is_published') and not product.is_published:
                return api_response(
                    success=False,
                    error='Product not available',
                    message='This product is not available',
                    status=404
                )
            
            product_data = self._get_product_data(
                product,
                include_variants=include_variants,
                include_details=True
            )
            
            return api_response(
                success=True,
                data=product_data,
                message='Product details retrieved'
            )
            
        except Exception as e:
            _logger.exception('Error getting product: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get product',
                status=500
            )

    @http.route(
        '/api/v1/products/<int:product_id>/variants/<int:variant_id>',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_variant(self, product_id, variant_id, **kwargs):
        """
        Get specific variant information.
        """
        try:
            variant = request.env['product.product'].sudo().browse(variant_id)
            
            if not variant.exists() or variant.product_tmpl_id.id != product_id:
                return api_response(
                    success=False,
                    error='Variant not found',
                    message=f'Variant with ID {variant_id} not found',
                    status=404
                )
            
            variant_data = self._get_product_data(
                variant,
                include_variants=False,
                include_details=True
            )
            
            return api_response(
                success=True,
                data=variant_data,
                message='Variant details retrieved'
            )
            
        except Exception as e:
            _logger.exception('Error getting variant: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get variant',
                status=500
            )

    @http.route(
        '/api/v1/categories',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_categories(self, **kwargs):
        """
        Get list of product categories.
        
        Query parameters:
        - parent_id: Get children of specific category (default: root categories)
        - include_children: Include nested children (default: true)
        - include_count: Include product count (default: true)
        """
        try:
            parent_id = kwargs.get('parent_id')
            include_children = kwargs.get('include_children', 'true').lower() == 'true'
            include_count = kwargs.get('include_count', 'true').lower() == 'true'
            
            # Check if product.public.category exists (website_sale module)
            if 'product.public.category' not in request.env:
                # Fallback to product.category
                return self._get_internal_categories(**kwargs)
            
            Category = request.env['product.public.category'].sudo()
            
            # Build domain
            if parent_id:
                try:
                    domain = [('parent_id', '=', int(parent_id))]
                except (ValueError, TypeError):
                    domain = [('parent_id', '=', False)]
            else:
                domain = [('parent_id', '=', False)]
            
            categories = Category.search(domain, order='sequence, name')
            
            def format_category(cat, depth=0):
                cat_data = {
                    'id': cat.id,
                    'name': cat.name,
                    'slug': cat.name.lower().replace(' ', '-'),
                    'image': f'/web/image/product.public.category/{cat.id}/image_256' if cat.image_128 else None,
                    'parent_id': cat.parent_id.id if cat.parent_id else None,
                }
                
                if include_count:
                    # Count products in this category and children
                    cat_ids = Category.search([('id', 'child_of', cat.id)]).ids
                    product_count = request.env['product.template'].sudo().search_count([
                        ('public_categ_ids', 'in', cat_ids),
                        ('is_published', '=', True),
                        ('sale_ok', '=', True),
                    ])
                    cat_data['product_count'] = product_count
                
                if include_children and cat.child_id and depth < 3:  # Limit depth
                    cat_data['children'] = [
                        format_category(child, depth + 1) 
                        for child in cat.child_id.sorted('sequence')
                    ]
                
                return cat_data
            
            categories_data = [format_category(cat) for cat in categories]
            
            return api_response(
                success=True,
                data=categories_data,
                message=f'Found {len(categories_data)} categories'
            )
            
        except Exception as e:
            _logger.exception('Error getting categories: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get categories',
                status=500
            )

    def _get_internal_categories(self, **kwargs):
        """Fallback to internal product categories if website_sale not installed."""
        Category = request.env['product.category'].sudo()
        
        parent_id = kwargs.get('parent_id')
        
        if parent_id:
            try:
                domain = [('parent_id', '=', int(parent_id))]
            except (ValueError, TypeError):
                domain = [('parent_id', '=', False)]
        else:
            domain = [('parent_id', '=', False)]
        
        categories = Category.search(domain, order='name')
        
        categories_data = [{
            'id': cat.id,
            'name': cat.name,
            'slug': cat.name.lower().replace(' ', '-'),
            'parent_id': cat.parent_id.id if cat.parent_id else None,
        } for cat in categories]
        
        return api_response(
            success=True,
            data=categories_data,
            message=f'Found {len(categories_data)} categories'
        )

    @http.route(
        '/api/v1/products/featured',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def get_featured_products(self, **kwargs):
        """
        Get featured products (newest or with ribbons).
        
        Query parameters:
        - limit: Number of products (default: 8)
        - type: Type of featured (newest, sale, popular)
        """
        try:
            limit = min(int(kwargs.get('limit', 8)), 20)
            featured_type = kwargs.get('type', 'newest')
            
            ProductTemplate = request.env['product.template'].sudo()
            
            domain = [
                ('sale_ok', '=', True),
                ('active', '=', True),
            ]
            
            if 'is_published' in ProductTemplate._fields:
                domain.append(('is_published', '=', True))
            
            if featured_type == 'sale' and hasattr(ProductTemplate, 'website_ribbon_id'):
                # Products with sale ribbon
                domain.append(('website_ribbon_id', '!=', False))
                order = 'website_sequence asc'
            elif featured_type == 'popular':
                # Best sellers (by sales count if available)
                order = 'sales_count desc' if 'sales_count' in ProductTemplate._fields else 'create_date desc'
            else:
                # Newest products
                order = 'create_date desc'
            
            products = ProductTemplate.search(domain, order=order, limit=limit)
            
            products_data = [
                self._get_product_data(p, include_variants=False, include_details=False)
                for p in products
            ]
            
            return api_response(
                success=True,
                data=products_data,
                message=f'Found {len(products_data)} featured products'
            )
            
        except Exception as e:
            _logger.exception('Error getting featured products: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get featured products',
                status=500
            )

    @http.route(
        '/api/v1/products/search-suggestions',
        type='http',
        auth='public',
        methods=['GET', 'OPTIONS'],
        csrf=False
    )
    @cors_handler
    def search_suggestions(self, **kwargs):
        """
        Get search suggestions for autocomplete.
        
        Query parameters:
        - q: Search query (minimum 2 characters)
        - limit: Maximum suggestions (default: 10)
        """
        try:
            query = kwargs.get('q', '').strip()
            limit = min(int(kwargs.get('limit', 10)), 20)
            
            if len(query) < 2:
                return api_response(
                    success=True,
                    data=[],
                    message='Query too short'
                )
            
            ProductTemplate = request.env['product.template'].sudo()
            
            domain = [
                ('sale_ok', '=', True),
                ('active', '=', True),
                '|',
                ('name', 'ilike', query),
                ('default_code', 'ilike', query),
            ]
            
            if 'is_published' in ProductTemplate._fields:
                domain.insert(0, ('is_published', '=', True))
            
            products = ProductTemplate.search(domain, limit=limit)
            
            suggestions = [{
                'id': p.id,
                'name': p.name,
                'price': p.list_price,
                'image': f'/web/image/product.template/{p.id}/image_128',
            } for p in products]
            
            return api_response(
                success=True,
                data=suggestions,
                message=f'Found {len(suggestions)} suggestions'
            )
            
        except Exception as e:
            _logger.exception('Error getting search suggestions: %s', str(e))
            return api_response(
                success=False,
                error=str(e),
                message='Failed to get suggestions',
                status=500
            )
