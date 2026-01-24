#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive E-commerce API Test Suite

This test suite covers all API endpoints and security features.
Run with: python3 test_api_comprehensive.py

Requirements:
- Odoo server running on localhost:8069
- Database: 18-ecommerce
"""

import json
import requests
import time
import sys
import random
import string
from datetime import datetime
from typing import Optional, Dict, Any, Tuple


BASE_URL = "http://localhost:8069"
API_BASE = f"{BASE_URL}/api/v1"
FRONTEND_ORIGIN = "http://localhost:3000"

TEST_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test User"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestSession:
    """Manages session state across tests."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Origin': FRONTEND_ORIGIN,
        })
        self.user_id = None
        self.partner_id = None
        self.cart_id = None
        self.order_id = None
        self.address_id = None
        self.product_id = None
        self.variant_id = None
        self.category_id = None

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.session.get(f"{API_BASE}{endpoint}", **kwargs)

    def post(self, endpoint: str, data: dict = None, **kwargs) -> requests.Response:
        return self.session.post(f"{API_BASE}{endpoint}", json=data, **kwargs)

    def put(self, endpoint: str, data: dict = None, **kwargs) -> requests.Response:
        return self.session.put(f"{API_BASE}{endpoint}", json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{API_BASE}{endpoint}", **kwargs)

    def options(self, endpoint: str, headers: dict = None, **kwargs) -> requests.Response:
        return self.session.options(f"{API_BASE}{endpoint}", headers=headers, **kwargs)


class TestResult:
    """Stores test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []

    def add_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        self.results.append(('PASS', test_name, message))
        print(f"  {Colors.GREEN}✓ PASS{Colors.END}: {test_name}")
        if message:
            print(f"           {Colors.CYAN}{message}{Colors.END}")

    def add_fail(self, test_name: str, message: str = ""):
        self.failed += 1
        self.results.append(('FAIL', test_name, message))
        print(f"  {Colors.RED}✗ FAIL{Colors.END}: {test_name}")
        if message:
            print(f"           {Colors.RED}{message}{Colors.END}")

    def add_skip(self, test_name: str, reason: str = ""):
        self.skipped += 1
        self.results.append(('SKIP', test_name, reason))
        print(f"  {Colors.YELLOW}○ SKIP{Colors.END}: {test_name}")
        if reason:
            print(f"           {Colors.YELLOW}{reason}{Colors.END}")

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
        print(f"{'='*60}")
        print(f"  Total:   {total}")
        print(f"  {Colors.GREEN}Passed:  {self.passed}{Colors.END}")
        print(f"  {Colors.RED}Failed:  {self.failed}{Colors.END}")
        print(f"  {Colors.YELLOW}Skipped: {self.skipped}{Colors.END}")
        print(f"{'='*60}")

        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}FAILED TESTS:{Colors.END}")
            for status, name, msg in self.results:
                if status == 'FAIL':
                    print(f"  - {name}: {msg}")

        return self.failed == 0


def run_test(test_func, session: TestSession, results: TestResult, test_name: str):
    """Run a single test with error handling."""
    try:
        test_func(session, results)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")



def test_api_health(session: TestSession, results: TestResult):
    """Test API health check endpoint."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}1. API HEALTH & INFO TESTS{Colors.END}")

    r = session.get("")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data.get('data', {}).get('name') == 'E-commerce REST API':
            results.add_pass("API Info endpoint returns correct data")
        else:
            results.add_fail("API Info endpoint", "Unexpected response format")
    else:
        results.add_fail("API Info endpoint", f"Status: {r.status_code}")

    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Cache-Control'
    ]
    missing = [h for h in required_headers if h not in r.headers]
    if not missing:
        results.add_pass("Security headers present", ", ".join(required_headers))
    else:
        results.add_fail("Security headers", f"Missing: {missing}")

    if r.headers.get('Access-Control-Allow-Origin') == FRONTEND_ORIGIN:
        results.add_pass("CORS allows configured origin")
    else:
        results.add_fail("CORS headers", f"Got: {r.headers.get('Access-Control-Allow-Origin')}")



def test_cors_security(session: TestSession, results: TestResult):
    """Test CORS security implementation."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}2. CORS SECURITY TESTS{Colors.END}")

    r = session.options("/cart", headers={
        'Origin': FRONTEND_ORIGIN,
        'Access-Control-Request-Method': 'POST'
    })
    if r.status_code == 200:
        if 'POST' in r.headers.get('Access-Control-Allow-Methods', ''):
            results.add_pass("OPTIONS preflight returns allowed methods")
        else:
            results.add_fail("OPTIONS preflight", "POST not in allowed methods")
    else:
        results.add_fail("OPTIONS preflight", f"Status: {r.status_code}")

    temp_session = requests.Session()
    r = temp_session.options(
        f"{API_BASE}/cart",
        headers={
            'Origin': 'https://malicious-site.com',
            'Access-Control-Request-Method': 'POST'
        }
    )
    origin_header = r.headers.get('Access-Control-Allow-Origin', '')
    if origin_header == 'null' or origin_header != 'https://malicious-site.com':
        results.add_pass("Unknown origin rejected", f"Got: {origin_header}")
    else:
        results.add_fail("Unknown origin not rejected", f"Allowed: {origin_header}")

    r = session.get("")
    if r.headers.get('Access-Control-Allow-Origin') != '*':
        results.add_pass("Wildcard origin not used")
    else:
        results.add_fail("Wildcard origin used", "Security risk!")

    if r.headers.get('Access-Control-Allow-Credentials') == 'true':
        results.add_pass("Credentials allowed for valid origin")
    else:
        results.add_fail("Credentials not allowed")



def test_authentication(session: TestSession, results: TestResult):
    """Test authentication endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}3. AUTHENTICATION TESTS{Colors.END}")

    r = session.get("/auth/session")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data.get('data', {}).get('authenticated') == False:
            results.add_pass("Session check (unauthenticated)")
        else:
            results.add_fail("Session check", "Expected unauthenticated")
    else:
        results.add_fail("Session check", f"Status: {r.status_code}")

    r = session.post("/auth/login", {})
    if r.status_code == 400:
        results.add_pass("Login rejects missing credentials")
    else:
        results.add_fail("Login missing credentials", f"Status: {r.status_code}")

    r = session.post("/auth/login", {
        "login": "nonexistent@example.com",
        "password": "WrongPass123!"
    })
    if r.status_code == 401:
        results.add_pass("Login rejects invalid credentials")
    else:
        results.add_fail("Login invalid credentials", f"Status: {r.status_code}")



def test_registration(session: TestSession, results: TestResult):
    """Test user registration with validation."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}4. REGISTRATION TESTS{Colors.END}")

    time.sleep(2)

    r = session.post("/auth/register", {"name": "Test"})
    if r.status_code == 400:
        results.add_pass("Register rejects missing fields")
    else:
        results.add_fail("Register missing fields", f"Status: {r.status_code}")

    r = session.post("/auth/register", {
        "name": "Test User",
        "email": "not-an-email",
        "password": "ValidPass123!"
    })
    data = r.json()
    if not data.get('success') and 'email' in data.get('message', '').lower():
        results.add_pass("Register rejects invalid email format")
    else:
        results.add_fail("Register invalid email", f"Message: {data.get('message')}")

    r = session.post("/auth/register", {
        "name": "Test User",
        "email": "valid@example.com",
        "password": "Short1"
    })
    data = r.json()
    if not data.get('success') and '8 character' in data.get('message', ''):
        results.add_pass("Register rejects short password")
    else:
        results.add_fail("Register short password", f"Message: {data.get('message')}")

    r = session.post("/auth/register", {
        "name": "Test User",
        "email": "valid@example.com",
        "password": "lowercase123"
    })
    data = r.json()
    if not data.get('success') and 'uppercase' in data.get('message', '').lower():
        results.add_pass("Register rejects password without uppercase")
    else:
        results.add_fail("Register no uppercase", f"Message: {data.get('message')}")

    r = session.post("/auth/register", {
        "name": "Test User",
        "email": "valid@example.com",
        "password": "NoNumberHere"
    })
    data = r.json()
    if not data.get('success') and 'number' in data.get('message', '').lower():
        results.add_pass("Register rejects password without number")
    else:
        results.add_fail("Register no number", f"Message: {data.get('message')}")



def test_rate_limiting(session: TestSession, results: TestResult):
    """Test rate limiting on sensitive endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}5. RATE LIMITING TESTS{Colors.END}")

    temp_session = requests.Session()
    temp_session.headers.update({
        'Content-Type': 'application/json',
        'Origin': FRONTEND_ORIGIN,
    })

    blocked = False
    for i in range(7):
        r = temp_session.post(f"{API_BASE}/auth/login", json={
            "login": f"ratelimit{i}@test.com",
            "password": "WrongPass123!"
        })
        if r.status_code == 429:
            blocked = True
            break

    if blocked:
        results.add_pass("Login rate limiting works", f"Blocked after {i+1} attempts")
    else:
        results.add_fail("Login rate limiting", "Not blocked after 7 attempts")

    if blocked:
        data = r.json()
        if 'Too many requests' in data.get('message', ''):
            results.add_pass("Rate limit returns proper message")
        else:
            results.add_fail("Rate limit message", f"Got: {data.get('message')}")
    else:
        results.add_skip("Rate limit message check", "Rate limiting not triggered")



def test_products(session: TestSession, results: TestResult):
    """Test product endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}6. PRODUCT TESTS{Colors.END}")

    r = session.get("/products")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and 'products' in data.get('data', {}):
            products = data['data']['products']
            results.add_pass("Get products list", f"Found {len(products)} products")

            if products:
                session.product_id = products[0]['id']
                if products[0].get('variants'):
                    session.variant_id = products[0]['variants'][0]['id']
        else:
            results.add_fail("Get products list", "Invalid response format")
    else:
        results.add_fail("Get products list", f"Status: {r.status_code}")

    r = session.get("/products?page=1&limit=5")
    if r.status_code == 200:
        data = r.json()
        pagination = data.get('data', {}).get('pagination', {})
        if pagination.get('page') == 1 and pagination.get('limit') == 5:
            results.add_pass("Product pagination works")
        else:
            results.add_fail("Product pagination", f"Got: {pagination}")
    else:
        results.add_fail("Product pagination", f"Status: {r.status_code}")

    if session.product_id:
        r = session.get(f"/products/{session.product_id}")
        if r.status_code == 200:
            data = r.json()
            if data.get('success') and data.get('data', {}).get('id') == session.product_id:
                results.add_pass("Get single product")
            else:
                results.add_fail("Get single product", "Product ID mismatch")
        else:
            results.add_fail("Get single product", f"Status: {r.status_code}")
    else:
        results.add_skip("Get single product", "No product ID available")

    r = session.get("/products/999999")
    if r.status_code == 404:
        results.add_pass("Non-existent product returns 404")
    else:
        results.add_fail("Non-existent product", f"Status: {r.status_code}")

    r = session.get("/categories")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            categories = data.get('data', [])
            results.add_pass("Get categories", f"Found {len(categories)} categories")
            if categories:
                session.category_id = categories[0]['id']
        else:
            results.add_fail("Get categories", "Request not successful")
    else:
        results.add_fail("Get categories", f"Status: {r.status_code}")

    if session.category_id:
        r = session.get(f"/products?category={session.category_id}")
        if r.status_code == 200:
            results.add_pass("Filter products by category")
        else:
            results.add_fail("Filter by category", f"Status: {r.status_code}")
    else:
        results.add_skip("Filter by category", "No category ID available")

    r = session.get("/products?search=test")
    if r.status_code == 200:
        results.add_pass("Search products")
    else:
        results.add_fail("Search products", f"Status: {r.status_code}")

    for order in ['name_asc', 'name_desc', 'price_asc', 'price_desc', 'newest']:
        r = session.get(f"/products?order={order}")
        if r.status_code == 200:
            results.add_pass(f"Sort products by {order}")
            break
        else:
            results.add_fail(f"Sort products by {order}", f"Status: {r.status_code}")
            break



def test_cart(session: TestSession, results: TestResult):
    """Test cart functionality."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}7. CART TESTS{Colors.END}")

    r = session.get("/cart")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            results.add_pass("Get cart (empty)")
        else:
            results.add_fail("Get cart", "Request not successful")
    else:
        results.add_fail("Get cart", f"Status: {r.status_code}")

    r = session.post("/cart/add", {})
    if r.status_code == 400:
        results.add_pass("Add to cart rejects missing product")
    else:
        results.add_fail("Add to cart missing product", f"Status: {r.status_code}")

    r = session.post("/cart/add", {
        "product_id": session.product_id or 1,
        "quantity": -5
    })
    data = r.json()
    if not data.get('success') and 'greater than 0' in data.get('message', ''):
        results.add_pass("Add to cart rejects negative quantity")
    else:
        results.add_fail("Add to cart negative quantity", f"Message: {data.get('message')}")

    r = session.post("/cart/add", {
        "product_id": session.product_id or 1,
        "quantity": 99999
    })
    data = r.json()
    if not data.get('success') and 'exceed' in data.get('message', '').lower():
        results.add_pass("Add to cart rejects excessive quantity")
    else:
        results.add_fail("Add to cart excessive quantity", f"Message: {data.get('message')}")

    if session.product_id:
        r = session.post("/cart/add", {
            "product_id": session.product_id,
            "quantity": 2
        })
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                cart_data = data.get('data', {})
                session.cart_id = cart_data.get('id')
                results.add_pass("Add product to cart", f"Cart ID: {session.cart_id}")
            else:
                results.add_fail("Add product to cart", data.get('message'))
        else:
            results.add_fail("Add product to cart", f"Status: {r.status_code}")
    else:
        results.add_skip("Add product to cart", "No product ID available")

    r = session.get("/cart")
    if r.status_code == 200:
        data = r.json()
        cart_data = data.get('data', {})
        if cart_data.get('lines') and len(cart_data['lines']) > 0:
            results.add_pass("Get cart with items", f"Items: {len(cart_data['lines'])}")
            line_id = cart_data['lines'][0]['id']
        else:
            results.add_fail("Get cart with items", "No items in cart")
            line_id = None
    else:
        results.add_fail("Get cart with items", f"Status: {r.status_code}")
        line_id = None

    if line_id:
        r = session.post("/cart/update", {
            "line_id": line_id,
            "quantity": 3
        })
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                results.add_pass("Update cart quantity")
            else:
                results.add_fail("Update cart quantity", data.get('message'))
        else:
            results.add_fail("Update cart quantity", f"Status: {r.status_code}")
    else:
        results.add_skip("Update cart quantity", "No line ID available")

    r = session.get("/cart/count")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and 'count' in data.get('data', {}):
            results.add_pass("Get cart count", f"Count: {data['data']['count']}")
        else:
            results.add_fail("Get cart count", "Invalid response")
    else:
        results.add_fail("Get cart count", f"Status: {r.status_code}")

    if line_id:
        r = session.delete(f"/cart/remove/{line_id}")
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                results.add_pass("Remove item from cart")
            else:
                results.add_fail("Remove item from cart", data.get('message'))
        else:
            results.add_fail("Remove item from cart", f"Status: {r.status_code}")
    else:
        results.add_skip("Remove item from cart", "No line ID available")

    if session.product_id:
        session.post("/cart/add", {"product_id": session.product_id, "quantity": 1})

    r = session.delete("/cart/clear")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            results.add_pass("Clear cart")
        else:
            results.add_fail("Clear cart", data.get('message'))
    else:
        results.add_fail("Clear cart", f"Status: {r.status_code}")



def test_user_auth_flow(session: TestSession, results: TestResult):
    """Test complete user authentication flow."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}8. USER AUTHENTICATION FLOW TESTS{Colors.END}")

    unique_email = f"test_{int(time.time())}_{random.randint(1000,9999)}@example.com"

    time.sleep(3)

    r = session.post("/auth/register", {
        "name": TEST_USER_NAME,
        "email": unique_email,
        "password": TEST_USER_PASSWORD,
        "phone": "+1234567890"
    })

    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            session.user_id = data.get('data', {}).get('uid')
            session.partner_id = data.get('data', {}).get('partner', {}).get('id')
            results.add_pass("Register new user", f"User ID: {session.user_id}")
        else:
            if 'rate' in data.get('message', '').lower() or 'too many' in data.get('message', '').lower():
                results.add_skip("Register new user", "Rate limited")
            else:
                results.add_fail("Register new user", data.get('message'))
    else:
        results.add_fail("Register new user", f"Status: {r.status_code}")

    if session.user_id:
        r = session.get("/auth/session")
        data = r.json()
        if data.get('data', {}).get('authenticated'):
            results.add_pass("Auto-login after registration")
        else:
            results.add_fail("Auto-login after registration", "Not authenticated")
    else:
        results.add_skip("Auto-login check", "Registration skipped")

    r = session.post("/auth/logout")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            results.add_pass("Logout")
        else:
            results.add_fail("Logout", data.get('message'))
    else:
        results.add_fail("Logout", f"Status: {r.status_code}")

    r = session.get("/auth/session")
    data = r.json()
    if not data.get('data', {}).get('authenticated'):
        results.add_pass("Session cleared after logout")
    else:
        results.add_fail("Session after logout", "Still authenticated")

    if session.user_id:
        time.sleep(2)
        r = session.post("/auth/login", {
            "login": unique_email,
            "password": TEST_USER_PASSWORD
        })
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                results.add_pass("Login with registered user")
            else:
                results.add_fail("Login registered user", data.get('message'))
        else:
            results.add_fail("Login registered user", f"Status: {r.status_code}")
    else:
        results.add_skip("Login registered user", "No user registered")



def test_user_profile(session: TestSession, results: TestResult):
    """Test user profile endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}9. USER PROFILE TESTS{Colors.END}")

    temp_session = TestSession()
    r = temp_session.get("/user/profile")
    if r.status_code == 401:
        results.add_pass("Get profile requires authentication")
    else:
        results.add_fail("Get profile unauthenticated", f"Status: {r.status_code}")

    r = session.get("/user/profile")
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data.get('data', {}).get('user'):
            results.add_pass("Get profile (authenticated)")
        else:
            results.add_fail("Get profile", "Invalid response")
    elif r.status_code == 401:
        results.add_skip("Get profile", "Not authenticated")
    else:
        results.add_fail("Get profile", f"Status: {r.status_code}")

    r = session.post("/user/profile", {
        "phone": "+9876543210",
        "city": "Test City"
    })
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            results.add_pass("Update profile")
        else:
            results.add_fail("Update profile", data.get('message'))
    elif r.status_code == 401:
        results.add_skip("Update profile", "Not authenticated")
    else:
        results.add_fail("Update profile", f"Status: {r.status_code}")



def test_addresses(session: TestSession, results: TestResult):
    """Test address management endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}10. ADDRESS TESTS{Colors.END}")

    temp_session = TestSession()
    r = temp_session.get("/user/addresses")
    if r.status_code == 401:
        results.add_pass("Get addresses requires authentication")
    else:
        results.add_fail("Get addresses unauthenticated", f"Status: {r.status_code}")

    r = session.get("/user/addresses")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            results.add_pass("Get addresses")
        else:
            results.add_fail("Get addresses", data.get('message'))
    elif r.status_code == 401:
        results.add_skip("Get addresses", "Not authenticated")
    else:
        results.add_fail("Get addresses", f"Status: {r.status_code}")

    r = session.post("/user/addresses", {"name": "Test"})
    if r.status_code == 400:
        results.add_pass("Add address rejects missing fields")
    elif r.status_code == 401:
        results.add_skip("Add address validation", "Not authenticated")
    else:
        results.add_fail("Add address missing fields", f"Status: {r.status_code}")

    r = session.post("/user/addresses", {
        "type": "delivery",
        "name": "Test Address",
        "street": "123 Test Street",
        "city": "Test City",
        "zip": "12345",
        "country_id": 233,
        "phone": "+1234567890"
    })
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            session.address_id = data.get('data', {}).get('id')
            results.add_pass("Add address", f"Address ID: {session.address_id}")
        else:
            results.add_fail("Add address", data.get('message'))
    elif r.status_code == 401:
        results.add_skip("Add address", "Not authenticated")
    else:
        results.add_fail("Add address", f"Status: {r.status_code}")

    if session.address_id:
        r = session.put(f"/user/addresses/{session.address_id}", {
            "city": "Updated City"
        })
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                results.add_pass("Update address")
            else:
                results.add_fail("Update address", data.get('message'))
        else:
            results.add_fail("Update address", f"Status: {r.status_code}")
    else:
        results.add_skip("Update address", "No address ID")

    if session.address_id:
        r = session.delete(f"/user/addresses/{session.address_id}")
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                results.add_pass("Delete address")
            else:
                results.add_fail("Delete address", data.get('message'))
        else:
            results.add_fail("Delete address", f"Status: {r.status_code}")
    else:
        results.add_skip("Delete address", "No address ID")



def test_orders(session: TestSession, results: TestResult):
    """Test order endpoints."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}11. ORDER TESTS{Colors.END}")

    temp_session = TestSession()
    r = temp_session.get("/orders")
    if r.status_code == 401:
        results.add_pass("Get orders requires authentication")
    else:
        results.add_fail("Get orders unauthenticated", f"Status: {r.status_code}")

    r = session.get("/orders")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            orders = data.get('data', {}).get('orders', [])
            results.add_pass("Get orders", f"Found {len(orders)} orders")

            if 'debug' not in data.get('data', {}):
                results.add_pass("Debug info not exposed in orders")
            else:
                results.add_fail("Debug info exposed", "Security issue!")
        else:
            results.add_fail("Get orders", data.get('message'))
    elif r.status_code == 401:
        results.add_skip("Get orders", "Not authenticated")
    else:
        results.add_fail("Get orders", f"Status: {r.status_code}")

    temp_session2 = TestSession()
    r = temp_session2.post("/orders/create", {
        "shipping_address": {
            "name": "Test",
            "street": "123 Test St",
            "city": "Test City",
            "country_id": 233
        }
    })
    if r.status_code in [400, 401, 404]:
        results.add_pass("Create order fails without cart/auth")
    else:
        results.add_fail("Create order without cart", f"Status: {r.status_code}")

    if session.product_id:
        session.post("/cart/add", {"product_id": session.product_id, "quantity": 1})

    r = session.post("/orders/create", {
        "shipping_address": {"name": "Test"}
    })
    if r.status_code == 400:
        results.add_pass("Create order rejects incomplete address")
    elif r.status_code == 401:
        results.add_skip("Create order validation", "Not authenticated")
    else:
        results.add_fail("Create order incomplete address", f"Status: {r.status_code}")



def test_password_change(session: TestSession, results: TestResult):
    """Test password change functionality."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}12. PASSWORD CHANGE TESTS{Colors.END}")

    temp_session = TestSession()
    r = temp_session.post("/user/change-password", {
        "current_password": "OldPass123!",
        "new_password": "NewPass123!"
    })
    if r.status_code == 401:
        results.add_pass("Change password requires authentication")
    else:
        results.add_fail("Change password unauthenticated", f"Status: {r.status_code}")

    r = session.post("/user/change-password", {})
    if r.status_code == 400:
        results.add_pass("Change password rejects missing fields")
    elif r.status_code == 401:
        results.add_skip("Change password validation", "Not authenticated")
    else:
        results.add_fail("Change password missing fields", f"Status: {r.status_code}")

    r = session.post("/user/change-password", {
        "current_password": TEST_USER_PASSWORD,
        "new_password": "weak"
    })
    data = r.json()
    if not data.get('success'):
        results.add_pass("Change password rejects weak password")
    elif r.status_code == 401:
        results.add_skip("Change password weak validation", "Not authenticated")
    else:
        results.add_fail("Change password weak", "Accepted weak password")



def test_countries(session: TestSession, results: TestResult):
    """Test countries endpoint."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}13. COUNTRIES ENDPOINT TEST{Colors.END}")

    r = session.get("/countries")
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            countries = data.get('data', [])
            results.add_pass("Get countries", f"Found {len(countries)} countries")

            if countries:
                sample = countries[0]
                if 'id' in sample and 'name' in sample:
                    results.add_pass("Country data structure correct")
                else:
                    results.add_fail("Country data structure", "Missing fields")
        else:
            results.add_fail("Get countries", data.get('message'))
    else:
        results.add_fail("Get countries", f"Status: {r.status_code}")



def test_input_sanitization(session: TestSession, results: TestResult):
    """Test input sanitization and XSS prevention."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}14. INPUT SANITIZATION TESTS{Colors.END}")

    r = session.get("/products?search=<script>alert('xss')</script>")
    if r.status_code == 200:
        if '<script>' not in r.text:
            results.add_pass("XSS in search query sanitized")
        else:
            results.add_fail("XSS in search", "Script tag in response")
    else:
        results.add_pass("XSS in search rejected", f"Status: {r.status_code}")

    r = session.get("/products?category=1;DROP TABLE products;--")
    if r.status_code in [200, 400]:
        results.add_pass("SQL injection in category handled safely")
    else:
        results.add_fail("SQL injection handling", f"Status: {r.status_code}")

    long_string = "A" * 10000
    r = session.get(f"/products?search={long_string[:1000]}")
    if r.status_code in [200, 400, 414]:
        results.add_pass("Long input handled safely")
    else:
        results.add_fail("Long input handling", f"Status: {r.status_code}")



def test_ownership_verification(session: TestSession, results: TestResult):
    """Test that users cannot access other users' resources."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}15. OWNERSHIP VERIFICATION TESTS{Colors.END}")

    r = session.get("/orders/999999")
    if r.status_code in [403, 404]:
        results.add_pass("Cannot access non-existent order")
    elif r.status_code == 401:
        results.add_skip("Order access check", "Not authenticated")
    else:
        results.add_fail("Non-existent order access", f"Status: {r.status_code}")

    r = session.put("/user/addresses/999999", {"city": "Test"})
    if r.status_code in [403, 404]:
        results.add_pass("Cannot update non-existent address")
    elif r.status_code == 401:
        results.add_skip("Address update check", "Not authenticated")
    else:
        results.add_fail("Non-existent address update", f"Status: {r.status_code}")

    r = session.delete("/user/addresses/999999")
    if r.status_code in [403, 404]:
        results.add_pass("Cannot delete non-existent address")
    elif r.status_code == 401:
        results.add_skip("Address delete check", "Not authenticated")
    else:
        results.add_fail("Non-existent address delete", f"Status: {r.status_code}")



def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}E-COMMERCE API COMPREHENSIVE TEST SUITE{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"API Base URL: {API_BASE}")
    print(f"Frontend Origin: {FRONTEND_ORIGIN}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        r = requests.get(f"{API_BASE}", timeout=5)
        if r.status_code != 200:
            print(f"\n{Colors.RED}ERROR: API not reachable. Status: {r.status_code}{Colors.END}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}ERROR: Cannot connect to API at {API_BASE}{Colors.END}")
        print("Make sure Odoo is running with the ecommerce_api module installed.")
        return False

    session = TestSession()
    results = TestResult()

    test_api_health(session, results)
    test_cors_security(session, results)
    test_authentication(session, results)
    test_registration(session, results)
    test_rate_limiting(session, results)
    test_products(session, results)
    test_cart(session, results)
    test_user_auth_flow(session, results)
    test_user_profile(session, results)
    test_addresses(session, results)
    test_orders(session, results)
    test_password_change(session, results)
    test_countries(session, results)
    test_input_sanitization(session, results)
    test_ownership_verification(session, results)

    success = results.summary()

    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
