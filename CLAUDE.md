# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a headless e-commerce application with a Next.js frontend and Odoo 18 backend API module. The frontend communicates with Odoo via custom REST API endpoints for authentication, product catalog, cart management, and orders.

## Architecture

- **Frontend**: Next.js 16 with App Router (`ecommerce_frontend/`)
- **Backend**: Odoo 18 module providing REST API (`ecommerce_api/`)
- **State Management**: Zustand for client-side state
- **Styling**: Tailwind CSS with shadcn/ui components
- **API Communication**: Custom Odoo API client in `src/lib/api.ts`

## Common Commands

### Frontend (ecommerce_frontend/)
```bash
cd ecommerce_frontend
npm run dev          # Development server
npm run build        # Production build
npm start            # Production server
npm run lint         # ESLint
```

### Backend (ecommerce_api/)
This is an Odoo module. Development requires an Odoo 18 installation:
- Install the module in Odoo via Apps menu
- Module depends on: `base`, `website_sale`, `auth_signup`, `portal`, `sale`, `product`
- CORS configuration required for frontend access

## Key Files and Directories

### Frontend Structure
- `src/app/` - Next.js App Router pages and layouts
- `src/components/` - React components (layout, product, ui)
- `src/lib/api.ts` - Odoo API client with authentication and CRUD methods
- `src/lib/store.ts` - Zustand state management stores
- `src/lib/types.ts` - TypeScript type definitions
- `.env.local` - Environment variables (copy from `.env.example`)

### Backend Structure
- `controllers/` - API endpoint implementations (auth, products, cart, orders, user)
- `models/` - Odoo model extensions and API configuration
- `security/` - Access control definitions
- `__manifest__.py` - Module configuration with API endpoint documentation

## API Endpoints

The backend provides RESTful endpoints under `/api/v1/`:

**Authentication:**
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/session`

**Products:**
- `GET /api/v1/products`
- `GET /api/v1/products/<id>`
- `GET /api/v1/categories`

**Cart:**
- `GET /api/v1/cart`
- `POST /api/v1/cart/add`
- `POST /api/v1/cart/update`
- `DELETE /api/v1/cart/remove`

**Orders:**
- `GET /api/v1/orders`
- `GET /api/v1/orders/<id>`
- `POST /api/v1/orders/create`

## Environment Setup

1. Set up Odoo 18 instance with `ecommerce_api` module
2. Configure environment variables in `ecommerce_frontend/.env.local`:
   ```
   NEXT_PUBLIC_ODOO_URL=http://localhost:8069
   NEXT_PUBLIC_ODOO_DB=your_database_name
   ```
3. Ensure CORS is configured in Odoo for frontend domain

## Development Workflow

When making changes:
1. Frontend changes: Work in `ecommerce_frontend/src/`
2. Backend changes: Modify Odoo module in `ecommerce_api/`
3. After backend changes: Upgrade module in Odoo Apps menu
4. Always run `npm run lint` before committing frontend changes