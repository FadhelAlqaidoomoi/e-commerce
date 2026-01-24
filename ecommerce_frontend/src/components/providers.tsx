"use client";

import { useEffect, useRef } from "react";
import { useAuthStore, useCartStore } from "@/lib/store";

export function Providers({ children }: { children: React.ReactNode }) {
  const checkSession = useAuthStore((s) => s.checkSession);
  const initializeCart = useCartStore((s) => s.initializeCart);
  const initialized = useRef(false);

  useEffect(() => {
    // Prevent double initialization in React Strict Mode
    if (initialized.current) return;
    initialized.current = true;

    // Initialize session and cart
    // Cart initialization handles token restoration automatically
    const init = async () => {
      await checkSession();
      await initializeCart();
    };

    init();
  }, [checkSession, initializeCart]);

  return <>{children}</>;
}
