# E-commerce Frontend

A modern Next.js 16 e-commerce frontend connected to Odoo 18 backend.

## Features

- 🛍️ **Product Catalog**: Browse products with filtering, sorting, and pagination
- 🛒 **Shopping Cart**: Add/remove items, update quantities
- 👤 **User Authentication**: Register, login, logout
- 📦 **Order Management**: View order history and order details
- 📱 **Responsive Design**: Mobile-first approach with Tailwind CSS
- 🎨 **Modern UI**: Built with shadcn/ui components

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: Zustand
- **Backend**: Odoo 18 (via custom API module)

## Prerequisites

- Node.js 18+ 
- npm or pnpm
- Odoo 18 instance with the `ecommerce_api` module installed

## Getting Started

1. **Install dependencies**

```bash
npm install
```

2. **Configure environment variables**

Copy `.env.example` to `.env.local` and update the values:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_ODOO_URL=http://localhost:8069
NEXT_PUBLIC_ODOO_DB=your_database_name
```

3. **Run the development server**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page
│   ├── shop/              # Product catalog
│   │   ├── page.tsx       # Products listing
│   │   └── [id]/          # Product detail
│   ├── cart/              # Shopping cart
│   ├── checkout/          # Checkout flow
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   └── account/           # User account
│       └── orders/        # Order history
├── components/
│   ├── layout/            # Header, Footer
│   ├── product/           # Product-related components
│   └── ui/                # shadcn/ui components
└── lib/
    ├── api.ts             # Odoo API client
    ├── store.ts           # Zustand stores
    ├── types.ts           # TypeScript types
    └── utils.ts           # Utility functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Backend Setup

This frontend requires the `ecommerce_api` Odoo module. Make sure to:

1. Install the module in your Odoo 18 instance
2. Configure CORS settings to allow requests from your frontend URL
3. Enable the necessary Odoo modules: `website_sale`, `sale`, `auth_signup`

## API Endpoints

The frontend communicates with these Odoo API endpoints:

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/session` - Get session info
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product detail
- `GET /api/v1/categories` - List categories
- `GET /api/v1/cart` - Get cart
- `POST /api/v1/cart/add` - Add item to cart
- `PUT /api/v1/cart/update` - Update cart item
- `DELETE /api/v1/cart/remove` - Remove cart item
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{id}` - Get order detail
- `POST /api/v1/orders` - Create order

## Future Features

- [ ] WhatsApp integration for order notifications
- [ ] Payment gateway integration
- [ ] Wishlist functionality
- [ ] Product reviews and ratings
- [ ] Advanced search with Algolia
- [ ] Multi-language support

## License

MIT
