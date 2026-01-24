"use client";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useAuthStore, useCartStore } from "@/lib/store";
import {
    ChevronDown,
    Heart,
    LogOut,
    Package,
    Search,
    ShoppingCart,
    Sparkles
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

export function Header() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Use individual selectors to prevent re-renders when unrelated auth state changes
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const cartCount = useCartStore((s) => s.cartCount);

  // Optimized scroll handler with requestAnimationFrame to reduce layout thrashing
  const rafId = useRef<number>(0);
  useEffect(() => {
    const handleScroll = () => {
      if (rafId.current) return; // Skip if a frame is already scheduled
      rafId.current = requestAnimationFrame(() => {
        setIsScrolled(window.scrollY > 20);
        rafId.current = 0;
      });
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (rafId.current) cancelAnimationFrame(rafId.current);
    };
  }, []);

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/shop?search=${encodeURIComponent(searchQuery)}`);
      setIsSearchOpen(false);
      setSearchQuery("");
    }
  }, [searchQuery, router]);

  const handleLogout = useCallback(async () => {
    await logout();
    router.push("/");
  }, [logout, router]);

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-500 ${
        isScrolled
          ? "bg-background/80 backdrop-blur-xl shadow-lg shadow-black/5 border-b border-border/50"
          : "bg-transparent"
      }`}
    >
      {/* Top Banner */}
      <div className="hidden md:block gradient-bg text-white text-center py-2 text-sm">
        <div className="container flex items-center justify-center gap-2">
          <Sparkles className="w-4 h-4" />
          <span>Free shipping on orders over $50 • Use code WELCOME20 for 20% off</span>
          <Sparkles className="w-4 h-4" />
        </div>
      </div>

      <div className="container flex h-20 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <div className="absolute -inset-1 rounded-xl gradient-bg opacity-0 group-hover:opacity-30 blur transition-opacity duration-300" />
          </div>
          <span className="text-2xl font-bold gradient-text hidden sm:block">Store</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex items-center space-x-1">
          <Link
            href="/shop"
            className="relative px-4 py-2 text-sm font-medium transition-colors hover:text-primary animated-underline"
          >
            Shop
          </Link>
          <Link
            href="/shop?order=newest"
            className="relative px-4 py-2 text-sm font-medium transition-colors hover:text-primary animated-underline"
          >
            New Arrivals
          </Link>
          <Link
            href="/shop?type=sale"
            className="relative px-4 py-2 text-sm font-medium transition-colors hover:text-primary animated-underline flex items-center gap-1"
          >
            Sale
            <span className="px-1.5 py-0.5 text-xs font-bold bg-red-500 text-white rounded-full">Hot</span>
          </Link>
        </nav>

        {/* Search Bar - Desktop */}
        <form
          onSubmit={handleSearch}
          className="hidden md:flex flex-1 max-w-md mx-6"
        >
          <div
            className={`relative w-full transition-all duration-300 ${
              isSearchFocused ? "scale-105" : ""
            }`}
          >
            <div
              className={`absolute inset-0 rounded-full gradient-bg opacity-0 blur transition-opacity duration-300 ${
                isSearchFocused ? "opacity-20" : ""
              }`}
            />
            <Search
              className={`absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 transition-colors duration-300 ${
                isSearchFocused ? "text-primary" : "text-muted-foreground"
              }`}
            />
            <Input
              type="search"
              placeholder="Search for products..."
              className="pl-11 pr-4 h-12 rounded-full border-2 border-transparent bg-secondary/50 focus:border-primary/50 focus:bg-background transition-all duration-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setIsSearchFocused(false)}
            />
          </div>
        </form>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {/* Mobile Search */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden rounded-full hover:bg-primary/10 hover:text-primary"
            onClick={() => setIsSearchOpen(true)}
          >
            <Search className="h-5 w-5" />
          </Button>

          {/* Wishlist */}
          <Button
            variant="ghost"
            size="icon"
            className="hidden sm:flex rounded-full hover:bg-primary/10 hover:text-primary relative"
          >
            <Heart className="h-5 w-5" />
          </Button>

          {/* Cart */}
          <Link href="/cart">
            <Button
              variant="ghost"
              size="icon"
              className="relative rounded-full hover:bg-primary/10 hover:text-primary group"
            >
              <ShoppingCart className="h-5 w-5 group-hover:scale-110 transition-transform" />
              {cartCount > 0 && (
                <span className="absolute -right-1 -top-1 h-5 w-5 rounded-full gradient-bg text-white text-xs flex items-center justify-center font-bold animate-scale-in">
                  {cartCount > 99 ? "99+" : cartCount}
                </span>
              )}
            </Button>
          </Link>

          {/* User Menu */}
          {isAuthenticated ? (
            <div className="hidden md:flex items-center space-x-2">
              <Link href="/account">
                <Button
                  variant="ghost"
                  className="rounded-full hover:bg-primary/10 hover:text-primary gap-2"
                >
                  <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center text-white text-sm font-bold">
                    {user?.name?.charAt(0) || "U"}
                  </div>
                  <span className="hidden lg:block">{user?.name || "Account"}</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="rounded-full hover:bg-destructive/10 hover:text-destructive"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="hidden md:flex items-center space-x-2">
              <Link href="/auth/login">
                <Button variant="ghost" className="rounded-full hover:bg-primary/10 hover:text-primary">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button className="rounded-full gradient-bg hover:opacity-90 btn-shine">
                  Get Started
                </Button>
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden rounded-full hover:bg-primary/10"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            <div className="relative w-5 h-5">
              <span
                className={`absolute left-0 w-5 h-0.5 bg-current transition-all duration-300 ${
                  isMobileMenuOpen ? "top-2 rotate-45" : "top-1"
                }`}
              />
              <span
                className={`absolute left-0 top-2 w-5 h-0.5 bg-current transition-all duration-300 ${
                  isMobileMenuOpen ? "opacity-0" : "opacity-100"
                }`}
              />
              <span
                className={`absolute left-0 w-5 h-0.5 bg-current transition-all duration-300 ${
                  isMobileMenuOpen ? "top-2 -rotate-45" : "top-3"
                }`}
              />
            </div>
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={`lg:hidden overflow-hidden transition-all duration-500 ease-out ${
          isMobileMenuOpen ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="container py-6 space-y-6 border-t bg-background/95 backdrop-blur-xl">
          <nav className="space-y-2">
            <Link
              href="/shop"
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <ShoppingCart className="h-5 w-5 text-primary" />
              </div>
              <span className="font-medium">Shop All</span>
            </Link>
            <Link
              href="/shop?order=newest"
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-cyan-500" />
              </div>
              <span className="font-medium">New Arrivals</span>
            </Link>
            <Link
              href="/shop?type=sale"
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <Heart className="h-5 w-5 text-red-500" />
              </div>
              <span className="font-medium">Sale</span>
              <span className="ml-auto px-2 py-0.5 text-xs font-bold bg-red-500 text-white rounded-full">
                Up to 50% off
              </span>
            </Link>
          </nav>

          <div className="h-px bg-border" />

          {isAuthenticated ? (
            <div className="space-y-2">
              <Link
                href="/account"
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <div className="w-10 h-10 rounded-lg gradient-bg flex items-center justify-center text-white font-bold">
                  {user?.name?.charAt(0) || "U"}
                </div>
                <div>
                  <p className="font-medium">{user?.name || "My Account"}</p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
              </Link>
              <Link
                href="/account/orders"
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Package className="h-5 w-5 text-primary" />
                </div>
                <span className="font-medium">My Orders</span>
              </Link>
              <button
                onClick={() => {
                  handleLogout();
                  setIsMobileMenuOpen(false);
                }}
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-destructive/10 transition-colors w-full text-destructive"
              >
                <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center">
                  <LogOut className="h-5 w-5" />
                </div>
                <span className="font-medium">Sign Out</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <Link href="/auth/login" onClick={() => setIsMobileMenuOpen(false)}>
                <Button variant="outline" className="w-full rounded-xl h-12">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/register" onClick={() => setIsMobileMenuOpen(false)}>
                <Button className="w-full rounded-xl h-12 gradient-bg">
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Search Dialog */}
      <Dialog open={isSearchOpen} onOpenChange={setIsSearchOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Search className="w-5 h-5 text-primary" />
              Search Products
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <Input
                type="search"
                placeholder="What are you looking for?"
                className="pl-4 pr-12 h-14 text-lg rounded-xl"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
              />
              <Button
                type="submit"
                size="icon"
                className="absolute right-2 top-2 h-10 w-10 rounded-lg gradient-bg"
              >
                <Search className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-muted-foreground">Popular:</span>
              {["Electronics", "Fashion", "Home", "Sports"].map((term) => (
                <button
                  key={term}
                  type="button"
                  onClick={() => {
                    setSearchQuery(term);
                    router.push(`/shop?search=${term}`);
                    setIsSearchOpen(false);
                  }}
                  className="px-3 py-1 text-sm rounded-full bg-secondary hover:bg-primary/10 hover:text-primary transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </header>
  );
}
