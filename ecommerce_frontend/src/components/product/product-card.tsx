"use client";

import { Eye, Heart, ShoppingCart, Sparkles, Star } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { memo, useState, useCallback } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCartStore } from "@/lib/store";
import { Product } from "@/lib/types";
import { formatCurrency, getDiscountPercentage, getImageUrl } from "@/lib/utils";

interface ProductCardProps {
  product: Product;
}

export const ProductCard = memo(function ProductCard({ product }: ProductCardProps) {
  // Use individual selectors to prevent re-renders when other cart state changes
  const addToCart = useCartStore((s) => s.addToCart);
  const isLoading = useCartStore((s) => s.isLoading);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleAddToCart = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    await addToCart(product.id, 1);
  }, [addToCart, product.id]);

  const handleWishlist = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsWishlisted((prev) => !prev);
  }, []);

  const imageUrl = getImageUrl(product.image);
  const discountPercentage = getDiscountPercentage(product.price, product.compare_price);
  const categoryName = product.categories?.[0]?.name;
  const isLocalImage = imageUrl.includes("localhost") || imageUrl.includes("127.0.0.1");

  return (
    <Link href={`/shop/${product.id}`}>
      <div
        className="group relative h-full rounded-2xl bg-card overflow-hidden card-glow transition-all duration-500"
      >
        {/* Image Container */}
        <div className="relative aspect-square overflow-hidden bg-gradient-to-br from-secondary/50 to-muted">
          {/* Loading Skeleton */}
          {!imageLoaded && (
            <div className="absolute inset-0 skeleton" />
          )}
          
          <Image
            src={imageUrl}
            alt={product.name}
            fill
            unoptimized={isLocalImage}
            className={`object-contain p-4 transition-all duration-700 scale-100 group-hover:scale-110 ${imageLoaded ? "opacity-100" : "opacity-0"}`}
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            onLoad={() => setImageLoaded(true)}
          />

          {/* Overlay on hover - using CSS group-hover */}
          <div
            className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent transition-opacity duration-300 opacity-0 group-hover:opacity-100"
          />

          {/* Badges */}
          <div className="absolute top-3 left-3 flex flex-col gap-2">
            {discountPercentage > 0 && (
              <Badge className="bg-red-500 hover:bg-red-600 text-white font-bold px-2 py-1 animate-scale-in">
                -{discountPercentage}%
              </Badge>
            )}
            {product.is_new && (
              <Badge className="gradient-bg text-white font-medium px-2 py-1 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                New
              </Badge>
            )}
          </div>

          {/* Out of Stock Overlay */}
          {!product.in_stock && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
              <Badge variant="destructive" className="text-sm px-4 py-2">
                Out of Stock
              </Badge>
            </div>
          )}

          {/* Quick Actions - using CSS group-hover */}
          <div
            className="absolute top-3 right-3 flex flex-col gap-2 transition-all duration-300 opacity-0 translate-x-4 group-hover:opacity-100 group-hover:translate-x-0"
          >
            <Button
              variant="secondary"
              size="icon"
              className={`h-9 w-9 rounded-full shadow-lg backdrop-blur-sm transition-all duration-300 ${
                isWishlisted
                  ? "bg-red-500 text-white hover:bg-red-600"
                  : "bg-white/90 hover:bg-white hover:text-red-500"
              }`}
              onClick={handleWishlist}
            >
              <Heart className={`h-4 w-4 ${isWishlisted ? "fill-current" : ""}`} />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="h-9 w-9 rounded-full bg-white/90 shadow-lg backdrop-blur-sm hover:bg-white hover:text-primary"
            >
              <Eye className="h-4 w-4" />
            </Button>
          </div>

          {/* Add to Cart Button - Slides up on hover using CSS group-hover */}
          <div
            className="absolute bottom-0 left-0 right-0 p-4 transition-all duration-300 translate-y-full opacity-0 group-hover:translate-y-0 group-hover:opacity-100"
          >
            <Button
              className="w-full h-11 rounded-xl gradient-bg text-white font-semibold btn-shine hover:opacity-90 transition-opacity"
              onClick={handleAddToCart}
              disabled={!product.in_stock || isLoading}
            >
              <ShoppingCart className="mr-2 h-4 w-4" />
              Add to Cart
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Category */}
          {categoryName && (
            <p className="text-xs font-medium text-primary/80 uppercase tracking-wider">
              {categoryName}
            </p>
          )}

          {/* Title */}
          <h3 className="font-semibold text-base line-clamp-2 min-h-[2.5rem] group-hover:text-primary transition-colors duration-300">
            {product.name}
          </h3>

          {/* Rating */}
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-3.5 h-3.5 ${
                  i < 4 ? "fill-yellow-400 text-yellow-400" : "fill-muted text-muted"
                }`}
              />
            ))}
            <span className="text-xs text-muted-foreground ml-1">(128)</span>
          </div>

          {/* Price */}
          <div className="flex items-center gap-2 pt-1">
            <span className="text-xl font-bold gradient-text">
              {formatCurrency(product.price, product.currency)}
            </span>
            {product.compare_price && product.compare_price > product.price && (
              <span className="text-sm text-muted-foreground line-through">
                {formatCurrency(product.compare_price, product.currency)}
              </span>
            )}
          </div>
        </div>

        {/* Bottom Border Gradient on Hover - using CSS group-hover */}
        <div
          className="absolute bottom-0 left-0 right-0 h-1 gradient-bg transition-all duration-300 opacity-0 group-hover:opacity-100"
        />
      </div>
    </Link>
  );
});

export function ProductCardSkeleton() {
  return (
    <div className="h-full rounded-2xl bg-card overflow-hidden">
      <div className="aspect-square skeleton" />
      <div className="p-4 space-y-3">
        <div className="h-3 w-16 rounded skeleton" />
        <div className="h-5 w-full rounded skeleton" />
        <div className="h-5 w-2/3 rounded skeleton" />
        <div className="flex gap-1 pt-1">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="w-3.5 h-3.5 rounded skeleton" />
          ))}
        </div>
        <div className="h-6 w-24 rounded skeleton pt-1" />
      </div>
    </div>
  );
}
