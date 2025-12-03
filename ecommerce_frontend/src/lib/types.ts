// Types for Odoo E-commerce API

// API Response wrapper
export interface ApiResponse<T = unknown> {
    success: boolean;
    data: T;
    message: string;
    error?: string;
}

// Authentication types
export interface User {
    id: number;
    name: string;
    login: string;
    email: string;
}

export interface Partner {
    id: number;
    name: string;
    email: string;
    phone: string;
    mobile: string;
    street: string;
    street2: string;
    city: string;
    zip: string;
    country: Country | null;
    state: State | null;
    whatsapp_number: string;
    whatsapp_opt_in: boolean;
    addresses?: Address[];
}

export interface SessionInfo {
    authenticated: boolean;
    session_id: string;
    uid?: number;
    user?: User;
    partner?: Partner;
    is_public: boolean;
}

export interface LoginCredentials {
    email: string;
    password: string;
    db?: string;
}

export interface RegisterData {
    name: string;
    email: string;
    password: string;
    phone?: string;
    whatsapp_number?: string;
    whatsapp_opt_in?: boolean;
}

// Product types
export interface Currency {
    symbol: string;
    position: 'before' | 'after';
    code: string;
}

export interface ProductCategory {
    id: number;
    name: string;
    slug: string;
}

export interface ProductRibbon {
    id: number;
    html: string;
    bg_color: string;
    text_color: string;
}

export interface ProductAttribute {
    id: number;
    name: string;
    display_type: string;
    values: ProductAttributeValue[];
}

export interface ProductAttributeValue {
    id: number;
    name: string;
    html_color?: string;
    is_custom: boolean;
}

export interface ProductVariant {
    id: number;
    name: string;
    sku: string;
    price: number;
    price_extra: number;
    image: string | null;
    in_stock: boolean;
    qty_available?: number;
    attribute_values: {
        attribute_id: number;
        attribute_name: string;
        value_id: number;
        value_name: string;
    }[];
}

export interface Product {
    id: number;
    name: string;
    slug: string;
    description_short: string;
    description?: string;
    description_ecommerce?: string;
    price: number;
    compare_price: number | null;
    currency: Currency;
    image: string | null;
    image_large?: string | null;
    additional_images?: { id: number; url: string; name: string }[];
    is_published: boolean;
    in_stock: boolean;
    qty_available?: number;
    categories: ProductCategory[];
    has_variants: boolean;
    variant_count: number;
    variant_id?: number;
    sku?: string;
    barcode?: string;
    attributes?: ProductAttribute[];
    variants?: ProductVariant[];
    ribbon?: ProductRibbon;
    alternative_products?: Product[];
    accessory_products?: Product[];
}

export interface Category {
    id: number;
    name: string;
    slug: string;
    image: string | null;
    parent_id: number | null;
    product_count?: number;
    children?: Category[];
}

export interface ProductsResponse {
    products: Product[];
    pagination: Pagination;
}

export interface Pagination {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
}

// Cart types
export interface CartLineAttribute {
    attribute: string;
    value: string;
}

export interface CartLine {
    id: number;
    product_id: number;
    variant_id: number;
    name: string;
    product_name: string;
    variant_name: string | null;
    sku: string;
    image: string;
    quantity: number;
    price_unit: number;
    price_subtotal: number;
    price_tax: number;
    price_total: number;
    discount: number;
    uom: { id: number; name: string } | null;
    attributes: CartLineAttribute[];
}

export interface Cart {
    id: number | null;
    name?: string;
    lines: CartLine[];
    line_count: number;
    item_count: number;
    subtotal: number;
    tax_total: number;
    total: number;
    currency: Currency | null;
    partner_id: number | null;
}

export interface CartCount {
    count: number;
    total: number;
    currency: string;
}

// Order types
export interface OrderAddress {
    id: number;
    name: string;
    street: string | null;
    street2: string | null;
    city: string | null;
    zip: string | null;
    country: string | null;
    state: string | null;
    phone: string | null;
}

export interface OrderLine {
    id: number;
    product_id: number;
    variant_id: number;
    name: string;
    product_name: string;
    sku: string;
    image: string;
    quantity: number;
    price_unit: number;
    price_subtotal: number;
    price_tax: number;
    price_total: number;
    discount: number;
}

export interface Order {
    id: number;
    name: string;
    state: 'draft' | 'sent' | 'sale' | 'cancel';
    state_label: string;
    date_order: string | null;
    commitment_date: string | null;
    create_date: string | null;
    subtotal: number;
    tax_total: number;
    total: number;
    currency: Currency | null;
    partner: {
        id: number;
        name: string;
        email: string;
        phone: string;
    } | null;
    invoice_address: OrderAddress | null;
    shipping_address: OrderAddress | null;
    note: string;
    client_order_ref: string;
    lines?: OrderLine[];
    line_count?: number;
}

export interface OrdersResponse {
    orders: Order[];
    pagination: Pagination;
}

// Address types
export interface Country {
    id: number;
    name: string;
    code: string;
    phone_code?: string;
    states?: State[];
}

export interface State {
    id: number;
    name: string;
    code: string;
}

export interface Address {
    id: number;
    type: 'main' | 'delivery' | 'invoice' | 'contact';
    name: string;
    street: string;
    street2: string;
    city: string;
    zip: string;
    country: Country | null;
    state: State | null;
    phone: string;
    email?: string;
}

export interface AddressInput {
    type?: 'delivery' | 'invoice' | 'contact';
    name: string;
    street: string;
    street2?: string;
    city: string;
    zip?: string;
    country_id: number;
    state_id?: number;
    phone?: string;
    email?: string;
}

export interface CheckoutAddress extends AddressInput {
    email: string;
}

export interface CreateOrderInput {
    shipping_address: CheckoutAddress;
    billing_address?: CheckoutAddress;
    use_same_address?: boolean;
    note?: string;
}

// Search suggestion
export interface SearchSuggestion {
    id: number;
    name: string;
    price: number;
    image: string;
}
