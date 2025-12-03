"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ShoppingCart,
  User,
  Search,
  Menu,
  X,
  LogOut,
  Package,
  Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuthStore, useCartStore, useUIStore } from "@/lib/store";
import { useRouter } from "next/navigation";

export function Header() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const { isAuthenticated, user, logout } = useAuthStore();
  const cartCount = useCartStore((state) => state.cartCount);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/shop?search=${encodeURIComponent(searchQuery)}`);
      setIsSearchOpen(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold">Store</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link
            href="/shop"
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Shop
          </Link>
          <Link
            href="/shop?order=newest"
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            New Arrivals
          </Link>
          <Link
            href="/shop?type=sale"
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Sale
          </Link>
        </nav>

        {/* Search Bar - Desktop */}
        <form
          onSubmit={handleSearch}
          className="hidden md:flex flex-1 max-w-sm mx-6"
        >
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search products..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          {/* Mobile Search */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsSearchOpen(true)}
          >
            <Search className="h-5 w-5" />
          </Button>

          {/* Cart */}
          <Link href="/cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="h-5 w-5" />
              {cartCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
                >
                  {cartCount > 99 ? "99+" : cartCount}
                </Badge>
              )}
            </Button>
          </Link>

          {/* User Menu */}
          {isAuthenticated ? (
            <div className="hidden md:flex items-center space-x-2">
              <Link href="/account">
                <Button variant="ghost" size="sm">
                  <User className="h-4 w-4 mr-2" />
                  {user?.name || "Account"}
                </Button>
              </Link>
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="hidden md:flex items-center space-x-2">
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button size="sm">Register</Button>
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t bg-background">
          <nav className="container py-4 space-y-4">
            <Link
              href="/shop"
              className="block text-sm font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Shop
            </Link>
            <Link
              href="/shop?order=newest"
              className="block text-sm font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              New Arrivals
            </Link>
            <Link
              href="/shop?type=sale"
              className="block text-sm font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Sale
            </Link>

            <div className="pt-4 border-t">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/account"
                    className="flex items-center space-x-2 py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <User className="h-4 w-4" />
                    <span>My Account</span>
                  </Link>
                  <Link
                    href="/account/orders"
                    className="flex items-center space-x-2 py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Package className="h-4 w-4" />
                    <span>My Orders</span>
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="flex items-center space-x-2 py-2 text-destructive"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </>
              ) : (
                <div className="space-y-2">
                  <Link href="/auth/login" className="block">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Sign In
                    </Button>
                  </Link>
                  <Link href="/auth/register" className="block">
                    <Button
                      className="w-full"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Register
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </nav>
        </div>
      )}

      {/* Mobile Search Dialog */}
      <Dialog open={isSearchOpen} onOpenChange={setIsSearchOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Search Products</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search products..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
              />
            </div>
            <Button type="submit" className="w-full mt-4">
              Search
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </header>
  );
}
