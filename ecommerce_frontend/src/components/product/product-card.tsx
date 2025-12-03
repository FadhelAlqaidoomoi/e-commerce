"use client";

import Image from "next/image";
import Link from "next/link";
import { ShoppingCart } from "lucide-react";

import { Product } from "@/lib/types";
import { formatCurrency, getImageUrl, getDiscountPercentage } from "@/lib/utils";
import { useCartStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const { addItem, isLoading } = useCartStore();

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    await addItem(product.id, 1);
  };

  const imageUrl = getImageUrl(product.image);
  const discountPercentage = getDiscountPercentage(product.price, product.compare_price);
  const categoryName = product.categories?.[0]?.name;

  return (
    <Link href={`/shop/${product.id}`}>
      <Card className="group h-full overflow-hidden transition-all hover:shadow-lg">
        <div className="relative aspect-square overflow-hidden">
          <Image
            src={imageUrl}
            alt={product.name}
            fill
            className="object-cover transition-transform group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
          {!product.in_stock && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50">
              <Badge variant="destructive" className="text-sm">
                Out of Stock
              </Badge>
            </div>
          )}
          {discountPercentage > 0 && (
            <Badge
              variant="secondary"
              className="absolute top-2 left-2 bg-red-500 text-white"
            >
              -{discountPercentage}%
            </Badge>
          )}
        </div>
        <CardContent className="p-4">
          <h3 className="font-semibold line-clamp-2 group-hover:text-primary transition-colors">
            {product.name}
          </h3>
          {categoryName && (
            <p className="text-xs text-muted-foreground mt-1">
              {categoryName}
            </p>
          )}
          <div className="mt-2 flex items-center gap-2">
            <span className="font-bold text-lg">
              {formatCurrency(product.price, product.currency)}
            </span>
            {product.compare_price && product.compare_price > product.price && (
              <span className="text-sm text-muted-foreground line-through">
                {formatCurrency(product.compare_price, product.currency)}
              </span>
            )}
          </div>
        </CardContent>
        <CardFooter className="p-4 pt-0">
          <Button
            className="w-full"
            onClick={handleAddToCart}
            disabled={!product.in_stock || isLoading}
          >
            <ShoppingCart className="mr-2 h-4 w-4" />
            Add to Cart
          </Button>
        </CardFooter>
      </Card>
    </Link>
  );
}

export function ProductCardSkeleton() {
  return (
    <Card className="h-full overflow-hidden">
      <div className="aspect-square bg-muted animate-pulse" />
      <CardContent className="p-4 space-y-3">
        <div className="h-4 bg-muted rounded animate-pulse" />
        <div className="h-3 bg-muted rounded w-1/2 animate-pulse" />
        <div className="h-5 bg-muted rounded w-1/3 animate-pulse" />
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <div className="h-10 bg-muted rounded w-full animate-pulse" />
      </CardFooter>
    </Card>
  );
}
