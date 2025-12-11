"use client";

import { ArrowRight, Minus, Plus, Shield, ShoppingBag, Sparkles, Trash2, Truck } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useCartStore } from "@/lib/store";
import { formatCurrency, getImageUrl, isLocalImage } from "@/lib/utils";

export default function CartPage() {
  const { cart, isLoading, fetchCart, updateQuantity, removeItem } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (isLoading && !cart) {
    return (
      <div className="min-h-screen">
        <div className="container py-12">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
              <ShoppingBag className="w-5 h-5 text-white" />
            </div>
            <Skeleton className="h-8 w-48" />
          </div>
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="p-6 rounded-2xl bg-card border">
                  <div className="flex gap-4">
                    <Skeleton className="w-28 h-28 rounded-xl" />
                    <div className="flex-1 space-y-3">
                      <Skeleton className="h-5 w-3/4" />
                      <Skeleton className="h-4 w-1/4" />
                      <Skeleton className="h-10 w-32" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div>
              <div className="p-6 rounded-2xl bg-card border space-y-4">
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-12 w-full rounded-xl" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!cart || cart.lines.length === 0) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-blob" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-blob" style={{ animationDelay: "2s" }} />
        </div>

        <div className="container relative z-10 py-16">
          <div className="max-w-lg mx-auto text-center">
            <div className="w-32 h-32 mx-auto rounded-full gradient-bg-subtle flex items-center justify-center mb-8">
              <ShoppingBag className="w-16 h-16 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-4">Your Cart is Empty</h1>
            <p className="text-muted-foreground mb-8">
              Looks like you haven&apos;t added anything to your cart yet.
              Start exploring our amazing products!
            </p>
            <Link href="/shop">
              <Button size="lg" className="rounded-full gradient-bg gap-2 btn-shine">
                Start Shopping
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <section className="relative py-12 overflow-hidden">
        <div className="absolute inset-0 gradient-bg opacity-5" />
        <div className="container relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center">
              <ShoppingBag className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Shopping Cart</h1>
              <p className="text-muted-foreground">{cart.lines.length} items in your cart</p>
            </div>
          </div>
        </div>
      </section>

      <div className="container pb-16">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.lines.map((line, index) => (
              <div
                key={line.id}
                className={`p-6 rounded-2xl bg-card border hover:shadow-lg transition-all duration-300 animate-fade-in-up stagger-${index + 1}`}
              >
                <div className="flex gap-6">
                  {/* Product Image */}
                  <Link href={`/shop/${line.product_id}`} className="shrink-0 group">
                    <div className="relative w-28 h-28 rounded-xl overflow-hidden bg-secondary">
                      <Image
                        src={getImageUrl(line.image)}
                        alt={line.product_name}
                        fill
                        unoptimized={isLocalImage(getImageUrl(line.image))}
                        className="object-cover group-hover:scale-110 transition-transform duration-500"
                        sizes="112px"
                      />
                    </div>
                  </Link>

                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <Link
                      href={`/shop/${line.product_id}`}
                      className="font-semibold text-lg hover:text-primary transition-colors line-clamp-2"
                    >
                      {line.product_name}
                    </Link>

                    {/* Attributes */}
                    {line.attributes && line.attributes.length > 0 && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {line.attributes.map((attr) => `${attr.attribute}: ${attr.value}`).join(", ")}
                      </p>
                    )}

                    <p className="font-bold text-lg gradient-text mt-2">
                      {formatCurrency(line.price_unit, cart.currency)}
                    </p>

                    {/* Quantity Controls */}
                    <div className="flex items-center gap-3 mt-4">
                      <div className="flex items-center rounded-xl border overflow-hidden">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-10 w-10 rounded-none hover:bg-primary/10"
                          onClick={() => updateQuantity(line.id, line.quantity - 1)}
                          disabled={line.quantity <= 1 || isLoading}
                        >
                          <Minus className="h-4 w-4" />
                        </Button>
                        <span className="w-12 text-center font-semibold">{line.quantity}</span>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-10 w-10 rounded-none hover:bg-primary/10"
                          onClick={() => updateQuantity(line.id, line.quantity + 1)}
                          disabled={isLoading}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Line Total & Remove */}
                  <div className="flex flex-col items-end justify-between">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-xl text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                      onClick={() => removeItem(line.id)}
                      disabled={isLoading}
                    >
                      <Trash2 className="h-5 w-5" />
                    </Button>
                    <p className="text-xl font-bold">
                      {formatCurrency(line.price_subtotal, cart.currency)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:sticky lg:top-28 lg:h-fit">
            <div className="rounded-2xl border bg-card overflow-hidden">
              <div className="p-6 gradient-bg text-white">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  Order Summary
                </h2>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span className="font-medium">{formatCurrency(cart.subtotal, cart.currency)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tax</span>
                  <span className="font-medium">{formatCurrency(cart.tax_total, cart.currency)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Shipping</span>
                  <span className="font-medium text-green-500">Free</span>
                </div>
                <Separator />
                <div className="flex justify-between text-xl font-bold">
                  <span>Total</span>
                  <span className="gradient-text">{formatCurrency(cart.total, cart.currency)}</span>
                </div>

                <div className="space-y-3 pt-4">
                  <Link href="/checkout" className="block">
                    <Button className="w-full h-12 rounded-xl gradient-bg text-base btn-shine" size="lg">
                      Checkout
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </Button>
                  </Link>
                  <Link href="/shop" className="block">
                    <Button variant="outline" className="w-full h-12 rounded-xl" size="lg">
                      Continue Shopping
                    </Button>
                  </Link>
                </div>

                {/* Trust Badges */}
                <div className="pt-6 space-y-3">
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Shield className="w-5 h-5 text-green-500" />
                    <span>Secure checkout with SSL encryption</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Truck className="w-5 h-5 text-primary" />
                    <span>Free shipping on orders over $50</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
