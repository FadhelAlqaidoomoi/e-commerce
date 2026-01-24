import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { odooApi } from './api';
import type { Cart, Partner, User } from './types';

// ==================== Cart Token Utilities ====================

const CART_TOKEN_KEY = 'ecommerce_cart_token';
const CART_TOKEN_EXPIRY_DAYS = 30;

function setCartTokenStorage(token: string): void {
    if (typeof window === 'undefined') return;

    // Set in localStorage (primary)
    localStorage.setItem(CART_TOKEN_KEY, token);

    // Set in cookie (backup, for server-side access)
    const expires = new Date(Date.now() + CART_TOKEN_EXPIRY_DAYS * 24 * 60 * 60 * 1000);
    document.cookie = `${CART_TOKEN_KEY}=${token}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
}

function getCartTokenFromStorage(): string | null {
    if (typeof window === 'undefined') return null;

    // Try localStorage first
    const localToken = localStorage.getItem(CART_TOKEN_KEY);
    if (localToken) return localToken;

    // Fall back to cookie
    const match = document.cookie.match(new RegExp(`${CART_TOKEN_KEY}=([^;]+)`));
    return match?.[1] ?? null;
}

function clearCartToken(): void {
    if (typeof window === 'undefined') return;

    localStorage.removeItem(CART_TOKEN_KEY);
    document.cookie = `${CART_TOKEN_KEY}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

// Export for use in components if needed
export { getCartTokenFromStorage, clearCartToken };

interface AuthState {
    isAuthenticated: boolean;
    isLoading: boolean;
    user: User | null;
    partner: Partner | null;
    sessionId: string | null;

    // Actions
    login: (data: { email: string; password: string }) => Promise<{ success: boolean; error?: string }>;
    register: (data: { name: string; email: string; password: string; phone?: string }) => Promise<{ success: boolean; error?: string }>;
    logout: () => Promise<void>;
    checkSession: () => Promise<void>;
    updatePartner: (partner: Partner) => void;
}

interface CartState {
    cart: Cart | null;
    cartCount: number;
    isLoading: boolean;
    cartToken: string | null;

    // Actions
    fetchCart: () => Promise<void>;
    addToCart: (productId: number, quantity?: number, variantId?: number) => Promise<{ success: boolean; error?: string }>;
    updateQuantity: (lineId: number, quantity: number) => Promise<{ success: boolean; error?: string }>;
    removeItem: (lineId: number) => Promise<{ success: boolean; error?: string }>;
    clearCart: () => Promise<void>;
    refreshCartCount: () => Promise<void>;

    // Cart Token Actions
    initializeCart: () => Promise<void>;
    restoreCartFromToken: () => Promise<boolean>;
    getCartToken: () => Promise<string | null>;
    onAuthSuccess: () => void;
}

interface UIState {
    isMobileMenuOpen: boolean;
    isCartOpen: boolean;
    isSearchOpen: boolean;

    // Actions
    setMobileMenuOpen: (open: boolean) => void;
    setCartOpen: (open: boolean) => void;
    setSearchOpen: (open: boolean) => void;
}

// Auth Store
export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            isAuthenticated: false,
            isLoading: false,
            user: null,
            partner: null,
            sessionId: null,

            login: async ({ email, password }) => {
                set({ isLoading: true });

                // Get cart token to potentially merge guest cart
                const cartToken = getCartTokenFromStorage();

                const response = await odooApi.login({
                    email,
                    password,
                    ...(cartToken ? { cart_token: cartToken, cart_merge_strategy: 'merge' } : {}),
                });

                if (response.success && response.data) {
                    set({
                        isAuthenticated: !response.data.is_public,
                        user: response.data.user || null,
                        partner: response.data.partner || null,
                        sessionId: response.data.session_id,
                        isLoading: false,
                    });

                    // Clear guest cart token after login (cart was merged/transferred)
                    if (response.data.cart_merged) {
                        clearCartToken();
                    }

                    // Notify cart store to refresh
                    useCartStore.getState().onAuthSuccess();

                    return { success: true };
                }

                set({ isLoading: false });
                return { success: false, error: response.error || response.message };
            },

            register: async ({ name, email, password, phone }) => {
                set({ isLoading: true });

                // Get cart token to transfer guest cart
                const cartToken = getCartTokenFromStorage();

                const response = await odooApi.register({
                    name,
                    email,
                    password,
                    ...(phone ? { phone } : {}),
                    ...(cartToken ? { cart_token: cartToken } : {}),
                });

                if (response.success && response.data) {
                    set({
                        isAuthenticated: !response.data.is_public,
                        user: response.data.user || null,
                        partner: response.data.partner || null,
                        sessionId: response.data.session_id,
                        isLoading: false,
                    });

                    // Clear guest cart token after registration
                    clearCartToken();

                    // Notify cart store to refresh
                    useCartStore.getState().onAuthSuccess();

                    return { success: true };
                }

                set({ isLoading: false });
                return { success: false, error: response.error || response.message };
            },

            logout: async () => {
                await odooApi.logout();
                set({
                    isAuthenticated: false,
                    user: null,
                    partner: null,
                    sessionId: null,
                });
            },

            checkSession: async () => {
                set({ isLoading: true });
                const response = await odooApi.getSession();

                if (response.success && response.data) {
                    set({
                        isAuthenticated: response.data.authenticated && !response.data.is_public,
                        user: response.data.user || null,
                        partner: response.data.partner || null,
                        sessionId: response.data.session_id,
                        isLoading: false,
                    });
                } else {
                    set({
                        isAuthenticated: false,
                        user: null,
                        partner: null,
                        sessionId: null,
                        isLoading: false,
                    });
                }
            },

            updatePartner: (partner) => {
                set({ partner });
            },
        }),
        {
            name: 'auth-storage',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                isAuthenticated: state.isAuthenticated,
                user: state.user,
                partner: state.partner,
                sessionId: state.sessionId,
            }),
        }
    )
);

// Cart Store
export const useCartStore = create<CartState>((set, get) => ({
    cart: null,
    cartCount: 0,
    isLoading: false,
    cartToken: null,

    initializeCart: async () => {
        const storedToken = getCartTokenFromStorage();

        if (storedToken) {
            // Try to restore cart from token first
            const restored = await get().restoreCartFromToken();
            if (restored) return;
        }

        // Fall back to fetching current session cart
        await get().fetchCart();

        // Get a token for the cart if we have items
        const currentCart = get().cart;
        if (currentCart && currentCart.item_count > 0 && !get().cartToken) {
            await get().getCartToken();
        }
    },

    restoreCartFromToken: async () => {
        const token = getCartTokenFromStorage();
        if (!token) return false;

        set({ isLoading: true });

        const response = await odooApi.restoreCartByToken(token);

        if (response.success && response.data) {
            set({
                cart: response.data,
                cartCount: response.data.item_count,
                cartToken: response.data.token || token,
                isLoading: false,
            });
            return true;
        }

        // Token invalid or expired, clear it
        clearCartToken();
        set({ isLoading: false, cartToken: null });
        return false;
    },

    getCartToken: async () => {
        const response = await odooApi.getCartToken();

        if (response.success && response.data?.token) {
            const token = response.data.token;
            setCartTokenStorage(token);
            set({ cartToken: token });
            return token;
        }

        return null;
    },

    onAuthSuccess: () => {
        // Clear token state (it was used during auth)
        set({ cartToken: null });
        // Refresh cart
        get().fetchCart();
    },

    fetchCart: async () => {
        set({ isLoading: true });
        const response = await odooApi.getCart();

        if (response.success && response.data) {
            set({
                cart: response.data,
                cartCount: response.data.item_count,
                isLoading: false,
            });
        } else {
            set({ isLoading: false });
        }
    },

    addToCart: async (productId, quantity = 1, variantId) => {
        set({ isLoading: true });
        const response = await odooApi.addToCart(productId, quantity, variantId);

        if (response.success && response.data) {
            set({
                cart: response.data,
                cartCount: response.data.item_count,
                isLoading: false,
            });

            // Ensure we have a token for cart persistence
            if (!get().cartToken) {
                get().getCartToken();
            }

            return { success: true };
        }

        set({ isLoading: false });
        return { success: false, error: response.error || response.message };
    },

    updateQuantity: async (lineId, quantity) => {
        const response = await odooApi.updateCartLine(lineId, quantity);

        if (response.success && response.data) {
            set({
                cart: response.data,
                cartCount: response.data.item_count,
            });
            return { success: true };
        }

        return { success: false, error: response.error || response.message };
    },

    removeItem: async (lineId) => {
        const response = await odooApi.removeFromCart(lineId);

        if (response.success && response.data) {
            set({
                cart: response.data,
                cartCount: response.data.item_count,
            });
            return { success: true };
        }

        return { success: false, error: response.error || response.message };
    },

    clearCart: async () => {
        const response = await odooApi.clearCart();

        if (response.success) {
            set({
                cart: response.data,
                cartCount: 0,
            });
        }
    },

    refreshCartCount: async () => {
        const response = await odooApi.getCartCount();

        if (response.success && response.data) {
            set({ cartCount: response.data.count });
        }
    },
}));

// UI Store
export const useUIStore = create<UIState>((set) => ({
    isMobileMenuOpen: false,
    isCartOpen: false,
    isSearchOpen: false,

    setMobileMenuOpen: (open) => set({ isMobileMenuOpen: open }),
    setCartOpen: (open) => set({ isCartOpen: open }),
    setSearchOpen: (open) => set({ isSearchOpen: open }),
}));
