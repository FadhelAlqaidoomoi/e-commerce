"use client";

import { useEffect } from "react";
import { useAuthStore, useCartStore } from "@/lib/store";

export function Providers({ children }: { children: React.ReactNode }) {
  const checkSession = useAuthStore((state) => state.checkSession);
  const fetchCart = useCartStore((state) => state.fetchCart);

  useEffect(() => {
    // Check session on mount
    checkSession();
    // Fetch cart on mount
    fetchCart();
  }, [checkSession, fetchCart]);

  return <>{children}</>;
}
