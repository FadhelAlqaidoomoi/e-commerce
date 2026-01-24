"use client";

import { useEffect } from "react";
import { useAuthStore, useCartStore } from "@/lib/store";

export function Providers({ children }: { children: React.ReactNode }) {
  const checkSession = useAuthStore((s) => s.checkSession);
  const fetchCart = useCartStore((s) => s.fetchCart);

  useEffect(() => {
    // Fetch session and cart in parallel for faster initial load
    Promise.all([checkSession(), fetchCart()]);
  }, [checkSession, fetchCart]);

  return <>{children}</>;
}
