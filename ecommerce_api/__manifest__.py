# -*- coding: utf-8 -*-
{
    'name': 'E-commerce REST API',
    'version': '18.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'REST API for headless e-commerce with Next.js frontend',
    'description': """
E-commerce REST API for Headless Commerce
==========================================

This module provides CORS-enabled REST-like API endpoints for building
headless e-commerce applications with frameworks like Next.js, React, Vue, etc.

Features:
---------
* CORS-enabled endpoints for cross-origin requests
* User authentication (login, register, logout)
* Product catalog with categories and filters
* Shopping cart management
* Order placement without payment gateway
* Customer portal (order history, profile)
* Prepared for future WhatsApp integration

API Endpoints:
--------------
Authentication:
* POST /api/v1/auth/login
* POST /api/v1/auth/register
* POST /api/v1/auth/logout
* GET /api/v1/auth/session
* POST /api/v1/auth/reset-password

Products:
* GET /api/v1/products
* GET /api/v1/products/<id>
* GET /api/v1/categories

Cart:
* GET /api/v1/cart
* POST /api/v1/cart/add
* POST /api/v1/cart/update
* DELETE /api/v1/cart/remove
* DELETE /api/v1/cart/clear
* GET /api/v1/cart/token
* POST /api/v1/cart/restore
* POST /api/v1/cart/merge

Orders:
* GET /api/v1/orders
* GET /api/v1/orders/<id>
* POST /api/v1/orders/create

User:
* GET /api/v1/user/profile
* POST /api/v1/user/profile
* GET /api/v1/user/addresses
* POST /api/v1/user/addresses
    """,
    'author': 'Fadhel Addons',
    'website': 'https://github.com/fadhel-addons',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website_sale',
        'auth_signup',
        'portal',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/api_config_data.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
