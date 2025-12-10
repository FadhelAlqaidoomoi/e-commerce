# E-commerce REST API Documentation

**Version:** 1.0.0  
**Base URL:** `/api/v1`  
**Module:** `ecommerce_api`

## Overview

This is a CORS-enabled REST API for headless e-commerce applications. It supports Next.js, React, Vue, and other frontend frameworks.

### Response Format

All endpoints return a standardized JSON response:

```json
{
    "success": true,
    "data": { ... },
    "message": "Human-readable message",
    "error": "Error details (only on failure)"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

---

## Authentication

### User Types

The API supports multiple Odoo user types:

| Type | Description | Group |
|------|-------------|-------|
| `internal` | Employees/Admin users | `base.group_user` |
| `portal` | Registered customers | `base.group_portal` |
| `public` | Anonymous visitors | `base.group_public` |

### Session-Based Authentication

Authentication is handled via session cookies. After login, include credentials in requests:

```javascript
fetch('/api/v1/auth/session', {
    credentials: 'include'  // Required for cookies
})
```

---

## Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/login`

Authenticate user and create session. Supports both internal and portal users.

**Request Body:**
```json
{
    "login": "user@example.com",
    "password": "password123",
    "db": "database_name"  // Optional if single DB
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "abc123...",
        "uid": 42,
        "user": {
            "id": 42,
            "name": "John Doe",
            "login": "john@example.com",
            "email": "john@example.com"
        },
        "partner": { ... },
        "user_type": "portal",
        "is_internal": false,
        "is_portal": true,
        "is_public": false
    },
    "message": "Login successful"
}
```

---

#### POST `/api/v1/auth/register`

Register a new portal customer account using Odoo's template user pattern.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "phone": "+1234567890",          // Optional
    "whatsapp_number": "+1234567890", // Optional
    "whatsapp_opt_in": true           // Optional
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "abc123...",
        "uid": 43,
        "user": {
            "id": 43,
            "name": "John Doe",
            "login": "john@example.com",
            "email": "john@example.com"
        },
        "partner": { ... },
        "user_type": "portal",
        "is_portal": true
    },
    "message": "Registration successful"
}
```

**Requirements:**
- `auth_signup.invitation_scope` must be set to `b2c`
- `registration_enabled` must be `true` in API config
- Password minimum 8 characters

---

#### POST `/api/v1/auth/logout`

Logout current user and destroy session.

**Response:**
```json
{
    "success": true,
    "data": null,
    "message": "Logged out successfully"
}
```

---

#### GET `/api/v1/auth/session`

Get current session information.

**Response (Authenticated):**
```json
{
    "success": true,
    "data": {
        "authenticated": true,
        "session_id": "abc123...",
        "uid": 42,
        "user": { ... },
        "partner": { ... },
        "user_type": "portal",
        "is_internal": false,
        "is_portal": true,
        "is_public": false
    },
    "message": "Session active"
}
```

**Response (Public):**
```json
{
    "success": true,
    "data": {
        "authenticated": false,
        "session_id": "xyz789...",
        "user_type": "public",
        "is_public": true
    },
    "message": "Public session"
}
```

---

#### POST `/api/v1/auth/reset-password`

Request password reset email.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "data": null,
    "message": "If an account exists with this email, password reset instructions have been sent."
}
```

---

### Product Endpoints

#### GET `/api/v1/products`

List products with filtering and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 20) |
| `category_id` | int | Filter by category |
| `search` | string | Search in name/description |
| `min_price` | float | Minimum price filter |
| `max_price` | float | Maximum price filter |
| `sort` | string | Sort field (name, price, create_date) |
| `order` | string | Sort order (asc, desc) |

**Response:**
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "id": 1,
                "name": "Product Name",
                "description": "...",
                "price": 99.99,
                "image_url": "/web/image/product.template/1/image_1920",
                "category": { "id": 1, "name": "Category" },
                "variants": [ ... ]
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

---

#### GET `/api/v1/products/<int:product_id>`

Get single product details.

---

#### GET `/api/v1/products/variants/<int:variant_id>`

Get specific product variant.

---

#### GET `/api/v1/products/categories` or `/api/v1/categories`

List all product categories.

---

#### GET `/api/v1/products/featured`

Get featured/highlighted products.

---

#### GET `/api/v1/products/search/autocomplete`

Autocomplete search for products.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `limit` | int | Max results (default: 10) |

---

### Cart Endpoints

#### GET `/api/v1/cart`

Get current shopping cart.

**Response:**
```json
{
    "success": true,
    "data": {
        "order_id": 123,
        "lines": [
            {
                "id": 1,
                "product": { ... },
                "quantity": 2,
                "price_unit": 49.99,
                "price_subtotal": 99.98
            }
        ],
        "subtotal": 99.98,
        "tax": 10.00,
        "total": 109.98,
        "item_count": 2
    }
}
```

---

#### POST `/api/v1/cart/add`

Add product to cart.

**Request Body:**
```json
{
    "product_id": 123,        // Product template ID
    "variant_id": 456,        // Optional: variant ID
    "quantity": 1             // Optional (default: 1)
}
```

---

#### POST `/api/v1/cart/update`

Update cart line quantity.

**Request Body:**
```json
{
    "line_id": 1,
    "quantity": 3
}
```

---

#### DELETE `/api/v1/cart/remove/<int:line_id>`

Remove line from cart.

---

#### DELETE `/api/v1/cart/clear`

Clear all cart items.

---

#### GET `/api/v1/cart/count`

Get cart item count.

---

### Order Endpoints

#### GET `/api/v1/orders`

Get order history (requires authentication).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number |
| `limit` | int | Items per page |
| `state` | string | Filter by state |

---

#### GET `/api/v1/orders/<int:order_id>`

Get order details (requires authentication).

---

#### POST `/api/v1/orders/create`

Create order from cart.

**Request Body:**
```json
{
    "shipping_address": {
        "name": "John Doe",
        "street": "123 Main St",
        "street2": "Apt 4",
        "city": "New York",
        "zip": "10001",
        "country_id": 233,
        "state_id": 39,
        "phone": "+1234567890",
        "email": "john@example.com"
    },
    "billing_address": { ... },   // Optional
    "use_same_address": true,      // Use shipping as billing
    "note": "Special instructions"
}
```

---

#### POST `/api/v1/orders/<int:order_id>/cancel`

Cancel an order (requires authentication).

---

#### POST `/api/v1/orders/<int:order_id>/reorder`

Add items from previous order to cart.

---

### User Profile Endpoints

#### GET `/api/v1/user/profile`

Get user profile (requires authentication).

---

#### POST `/api/v1/user/profile`

Update user profile (requires authentication).

**Request Body:**
```json
{
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com"
}
```

---

#### GET `/api/v1/user/addresses`

Get all user addresses (requires authentication).

---

#### POST `/api/v1/user/addresses`

Add new address (requires authentication).

**Request Body:**
```json
{
    "name": "Home",
    "street": "123 Main St",
    "street2": "Apt 4",
    "city": "New York",
    "zip": "10001",
    "country_id": 233,
    "state_id": 39,
    "phone": "+1234567890",
    "type": "delivery"
}
```

---

#### PUT `/api/v1/user/addresses/<int:address_id>`

Update address (requires authentication).

---

#### DELETE `/api/v1/user/addresses/<int:address_id>`

Delete address (requires authentication).

---

#### POST `/api/v1/user/change-password`

Change user password (requires authentication).

**Request Body:**
```json
{
    "old_password": "currentPassword123",
    "new_password": "newPassword456"
}
```

---

### Utility Endpoints

#### GET `/api/v1`

API health check and info.

**Response:**
```json
{
    "success": true,
    "data": {
        "name": "E-commerce REST API",
        "version": "1.0.0",
        "endpoints": [ ... ]
    }
}
```

---

#### GET `/api/v1/countries`

List all countries with states.

---

## Configuration

### API Config Model (`ecommerce.api.config`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `allowed_origins` | Text | `localhost:3000` | CORS allowed origins |
| `products_per_page` | Integer | 20 | Default pagination size |
| `guest_checkout_enabled` | Boolean | true | Allow guest checkout |
| `registration_enabled` | Boolean | true | Allow public registration |
| `whatsapp_enabled` | Boolean | false | Enable WhatsApp integration |

### Odoo Settings Required

1. **Enable Public Signup:**
   - Settings → General Settings → Customer Account → "Free sign up"
   - Or set `auth_signup.invitation_scope` = `b2c`

2. **Portal Template User:**
   - Ensure `base.template_portal_user_id` is configured (automatic)

---

## Error Handling

### Common Errors

```json
{
    "success": false,
    "error": "Authentication required",
    "message": "Please login to access this resource"
}
```

| Error | Status | Description |
|-------|--------|-------------|
| `Missing credentials` | 400 | Email/password not provided |
| `Invalid credentials` | 401 | Wrong email or password |
| `Authentication required` | 401 | Session expired or not logged in |
| `Registration disabled` | 403 | Public signup not allowed |
| `User exists` | 409 | Email already registered |
| `Password too short` | 400 | Password < 8 characters |

---

## CORS Configuration

The API supports CORS for cross-origin requests. Configure allowed origins in the API config.

**Default allowed origins:**
- `http://localhost:3000`
- `http://127.0.0.1:3000`

**Headers included:**
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With`

---

## Frontend Integration Example

```javascript
// API client example
const API_BASE = 'https://your-odoo.com/api/v1';

// Login
async function login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login: email, password })
    });
    return response.json();
}

// Register
async function register(name, email, password) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
    });
    return response.json();
}

// Get session
async function getSession() {
    const response = await fetch(`${API_BASE}/auth/session`, {
        credentials: 'include'
    });
    return response.json();
}

// Get products
async function getProducts(page = 1, categoryId = null) {
    const params = new URLSearchParams({ page });
    if (categoryId) params.append('category_id', categoryId);
    
    const response = await fetch(`${API_BASE}/products?${params}`, {
        credentials: 'include'
    });
    return response.json();
}

// Add to cart
async function addToCart(productId, quantity = 1) {
    const response = await fetch(`${API_BASE}/cart/add`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity })
    });
    return response.json();
}
```

---

## User Type Permissions

The API uses Odoo's permission system. Different user types have different capabilities:

### Portal Users (`user_type: "portal"`)
- View products
- Manage their own cart
- Place and view their own orders
- Manage their own addresses and profile

### Internal Users (`user_type: "internal"`)
- All portal capabilities
- Additional admin capabilities based on Odoo groups

### Public Users (`user_type: "public"`)
- View products
- Use cart (guest checkout if enabled)
- Cannot view order history or manage profile
