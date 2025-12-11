import type {
    Address,
    AddressInput,
    ApiResponse,
    Cart,
    CartCount,
    Category,
    Country,
    CreateOrderInput,
    LoginCredentials,
    Order,
    OrdersResponse,
    Partner,
    Product,
    ProductsResponse,
    RegisterData,
    SearchSuggestion,
    SessionInfo,
} from './types';

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.NEXT_PUBLIC_ODOO_DB || 'odoo18';

class OdooApiClient {
    private baseUrl: string;
    private db: string;

    constructor(baseUrl: string = ODOO_URL, db: string = ODOO_DB) {
        this.baseUrl = baseUrl;
        this.db = db;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultHeaders: HeadersInit = {
            'Content-Type': 'application/json',
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...defaultHeaders,
                    ...options.headers,
                },
                credentials: 'include', // Important for session cookies
            });

            const data = await response.json();
            return data as ApiResponse<T>;
        } catch (error) {
            console.error('API Error:', error);
            return {
                success: false,
                data: null as T,
                message: 'Network error',
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }

    // ==================== Authentication ====================

    async login(credentials: LoginCredentials): Promise<ApiResponse<SessionInfo>> {
        return this.request<SessionInfo>('/api/v1/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                login: credentials.email,
                password: credentials.password,
                db: credentials.db || this.db,
            }),
        });
    }

    async register(data: RegisterData): Promise<ApiResponse<SessionInfo>> {
        return this.request<SessionInfo>('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async logout(): Promise<ApiResponse<null>> {
        return this.request<null>('/api/v1/auth/logout', {
            method: 'POST',
        });
    }

    async getSession(): Promise<ApiResponse<SessionInfo>> {
        return this.request<SessionInfo>('/api/v1/auth/session');
    }

    async resetPassword(email: string): Promise<ApiResponse<null>> {
        return this.request<null>('/api/v1/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    }

    // ==================== Products ====================

    async getProducts(params?: {
        page?: number;
        limit?: number;
        category?: number;
        search?: string;
        order?: 'name_asc' | 'name_desc' | 'price_asc' | 'price_desc' | 'newest';
        min_price?: number;
        max_price?: number;
        in_stock?: boolean;
    }): Promise<ApiResponse<ProductsResponse>> {
        const searchParams = new URLSearchParams();

        if (params?.page) searchParams.set('page', params.page.toString());
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        if (params?.category) searchParams.set('category', params.category.toString());
        if (params?.search) searchParams.set('search', params.search);
        if (params?.order) searchParams.set('order', params.order);
        if (params?.min_price) searchParams.set('min_price', params.min_price.toString());
        if (params?.max_price) searchParams.set('max_price', params.max_price.toString());
        if (params?.in_stock !== undefined) searchParams.set('in_stock', params.in_stock.toString());

        const query = searchParams.toString();
        return this.request<ProductsResponse>(`/api/v1/products${query ? `?${query}` : ''}`);
    }

    async getProduct(id: number, includeVariants: boolean = true): Promise<ApiResponse<Product>> {
        const params = includeVariants ? '?include_variants=true' : '';
        return this.request<Product>(`/api/v1/products/${id}${params}`);
    }

    async getFeaturedProducts(
        type: 'newest' | 'sale' | 'popular' = 'newest',
        limit: number = 8
    ): Promise<ApiResponse<Product[]>> {
        return this.request<Product[]>(`/api/v1/products/featured?type=${type}&limit=${limit}`);
    }

    async searchSuggestions(query: string, limit: number = 10): Promise<ApiResponse<SearchSuggestion[]>> {
        return this.request<SearchSuggestion[]>(
            `/api/v1/products/search-suggestions?q=${encodeURIComponent(query)}&limit=${limit}`
        );
    }

    // ==================== Categories ====================

    async getCategories(params?: {
        parent_id?: number;
        include_children?: boolean;
        include_count?: boolean;
    }): Promise<ApiResponse<Category[]>> {
        const searchParams = new URLSearchParams();

        if (params?.parent_id) searchParams.set('parent_id', params.parent_id.toString());
        if (params?.include_children !== undefined)
            searchParams.set('include_children', params.include_children.toString());
        if (params?.include_count !== undefined)
            searchParams.set('include_count', params.include_count.toString());

        const query = searchParams.toString();
        return this.request<Category[]>(`/api/v1/categories${query ? `?${query}` : ''}`);
    }

    // ==================== Cart ====================

    async getCart(): Promise<ApiResponse<Cart>> {
        return this.request<Cart>('/api/v1/cart');
    }

    async addToCart(
        productId: number,
        quantity: number = 1,
        variantId?: number
    ): Promise<ApiResponse<Cart>> {
        return this.request<Cart>('/api/v1/cart/add', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                variant_id: variantId,
                quantity,
            }),
        });
    }

    async updateCartLine(lineId: number, quantity: number): Promise<ApiResponse<Cart>> {
        return this.request<Cart>('/api/v1/cart/update', {
            method: 'POST',
            body: JSON.stringify({
                line_id: lineId,
                quantity,
            }),
        });
    }

    async removeFromCart(lineId: number): Promise<ApiResponse<Cart>> {
        return this.request<Cart>(`/api/v1/cart/remove/${lineId}`, {
            method: 'DELETE',
        });
    }

    async clearCart(): Promise<ApiResponse<Cart>> {
        return this.request<Cart>('/api/v1/cart/clear', {
            method: 'DELETE',
        });
    }

    async getCartCount(): Promise<ApiResponse<CartCount>> {
        return this.request<CartCount>('/api/v1/cart/count');
    }

    // ==================== Orders ====================

    async getOrders(params?: {
        page?: number;
        limit?: number;
        state?: 'draft' | 'sent' | 'sale' | 'done' | 'cancel' | 'pending';
    }): Promise<ApiResponse<OrdersResponse>> {
        const searchParams = new URLSearchParams();

        if (params?.page) searchParams.set('page', params.page.toString());
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        if (params?.state) searchParams.set('state', params.state);

        const query = searchParams.toString();
        return this.request<OrdersResponse>(`/api/v1/orders${query ? `?${query}` : ''}`);
    }

    async getOrder(orderId: number): Promise<ApiResponse<Order>> {
        return this.request<Order>(`/api/v1/orders/${orderId}`);
    }

    async createOrder(data: CreateOrderInput): Promise<ApiResponse<Order>> {
        return this.request<Order>('/api/v1/orders/create', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async cancelOrder(orderId: number): Promise<ApiResponse<Order>> {
        return this.request<Order>(`/api/v1/orders/${orderId}/cancel`, {
            method: 'POST',
        });
    }

    async reorder(orderId: number): Promise<ApiResponse<{ cart_id: number }>> {
        return this.request<{ cart_id: number }>(`/api/v1/orders/${orderId}/reorder`, {
            method: 'POST',
        });
    }

    async restoreOrder(orderId: number): Promise<ApiResponse<Order>> {
        return this.request<Order>(`/api/v1/orders/${orderId}/restore`, {
            method: 'POST',
        });
    }

    // ==================== User Profile ====================

    async getProfile(): Promise<ApiResponse<{ user: { id: number; name: string; login: string; email: string }; partner: Partner }>> {
        return this.request('/api/v1/user/profile');
    }

    async updateProfile(data: Partial<Partner>): Promise<ApiResponse<Partner>> {
        return this.request<Partner>('/api/v1/user/profile', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getAddresses(): Promise<ApiResponse<{ main: Address; addresses: Address[] }>> {
        return this.request('/api/v1/user/addresses');
    }

    async addAddress(address: AddressInput): Promise<ApiResponse<Address>> {
        return this.request<Address>('/api/v1/user/addresses', {
            method: 'POST',
            body: JSON.stringify(address),
        });
    }

    async updateAddress(addressId: number, address: Partial<AddressInput>): Promise<ApiResponse<Address>> {
        return this.request<Address>(`/api/v1/user/addresses/${addressId}`, {
            method: 'PUT',
            body: JSON.stringify(address),
        });
    }

    async deleteAddress(addressId: number): Promise<ApiResponse<null>> {
        return this.request<null>(`/api/v1/user/addresses/${addressId}`, {
            method: 'DELETE',
        });
    }

    async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse<null>> {
        return this.request<null>('/api/v1/user/change-password', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });
    }

    // ==================== Countries ====================

    async getCountries(): Promise<ApiResponse<Country[]>> {
        return this.request<Country[]>('/api/v1/countries');
    }

    // ==================== Utilities ====================

    getImageUrl(path: string | null): string {
        if (!path) return '/placeholder-product.png';
        if (path.startsWith('http')) return path;
        return `${this.baseUrl}${path}`;
    }

    formatPrice(amount: number, currency?: { symbol: string; position: string }): string {
        const formatted = amount.toFixed(2);
        if (!currency) return `$${formatted}`;

        if (currency.position === 'before') {
            return `${currency.symbol}${formatted}`;
        }
        return `${formatted}${currency.symbol}`;
    }
}

// Export a singleton instance
export const odooApi = new OdooApiClient();

// Export the class for custom instances
export { OdooApiClient };
