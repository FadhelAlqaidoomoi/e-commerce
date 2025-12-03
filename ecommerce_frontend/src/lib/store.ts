import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { odooApi } from './api';
import type { SessionInfo, Cart, CartCount, User, Partner } from './types';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  partner: Partner | null;
  sessionId: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
  updatePartner: (partner: Partner) => void;
}

interface CartState {
  cart: Cart | null;
  cartCount: number;
  isLoading: boolean;
  
  // Actions
  fetchCart: () => Promise<void>;
  addToCart: (productId: number, quantity?: number, variantId?: number) => Promise<{ success: boolean; error?: string }>;
  updateQuantity: (lineId: number, quantity: number) => Promise<{ success: boolean; error?: string }>;
  removeItem: (lineId: number) => Promise<{ success: boolean; error?: string }>;
  clearCart: () => Promise<void>;
  refreshCartCount: () => Promise<void>;
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
      isLoading: true,
      user: null,
      partner: null,
      sessionId: null,

      login: async (email, password) => {
        set({ isLoading: true });
        const response = await odooApi.login({ email, password });
        
        if (response.success && response.data) {
          set({
            isAuthenticated: !response.data.is_public,
            user: response.data.user || null,
            partner: response.data.partner || null,
            sessionId: response.data.session_id,
            isLoading: false,
          });
          return { success: true };
        }
        
        set({ isLoading: false });
        return { success: false, error: response.error || response.message };
      },

      register: async (name, email, password, phone) => {
        set({ isLoading: true });
        const response = await odooApi.register({ name, email, password, phone });
        
        if (response.success && response.data) {
          set({
            isAuthenticated: !response.data.is_public,
            user: response.data.user || null,
            partner: response.data.partner || null,
            sessionId: response.data.session_id,
            isLoading: false,
          });
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
