"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useCallback } from "react";

import { Category } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

interface ProductFiltersProps {
  categories: Category[];
  currentCategory?: string;
  minPrice?: string;
  maxPrice?: string;
  inStock?: boolean;
}

export function ProductFilters({
  categories,
  currentCategory,
  minPrice,
  maxPrice,
  inStock,
}: ProductFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const createQueryString = useCallback(
    (updates: Record<string, string | undefined>) => {
      const params = new URLSearchParams(searchParams.toString());
      
      Object.entries(updates).forEach(([key, value]) => {
        if (value === undefined || value === "") {
          params.delete(key);
        } else {
          params.set(key, value);
        }
      });
      
      // Reset to page 1 when filters change
      params.delete("page");
      
      return params.toString();
    },
    [searchParams]
  );

  const handleCategoryChange = (categoryId: string | undefined) => {
    const query = createQueryString({ category: categoryId });
    router.push(`${pathname}?${query}`);
  };

  const handlePriceChange = (min?: string, max?: string) => {
    const query = createQueryString({ min_price: min, max_price: max });
    router.push(`${pathname}?${query}`);
  };

  const handleInStockChange = (checked: boolean) => {
    const query = createQueryString({ in_stock: checked ? "true" : undefined });
    router.push(`${pathname}?${query}`);
  };

  const clearFilters = () => {
    router.push(pathname);
  };

  const hasActiveFilters = currentCategory || minPrice || maxPrice || inStock;

  return (
    <div className="space-y-6">
      {/* Clear Filters */}
      {hasActiveFilters && (
        <Button
          variant="outline"
          size="sm"
          onClick={clearFilters}
          className="w-full"
        >
          Clear All Filters
        </Button>
      )}

      {/* Categories */}
      <div>
        <h3 className="font-semibold mb-3">Categories</h3>
        <div className="space-y-2">
          <button
            onClick={() => handleCategoryChange(undefined)}
            className={`block w-full text-left px-2 py-1.5 text-sm rounded-md transition-colors ${
              !currentCategory
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            All Products
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategoryChange(category.id.toString())}
              className={`block w-full text-left px-2 py-1.5 text-sm rounded-md transition-colors ${
                currentCategory === category.id.toString()
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted"
              }`}
            >
              {category.name}
              {category.product_count !== undefined && (
                <span className="text-xs text-muted-foreground ml-1">
                  ({category.product_count})
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <Separator />

      {/* Price Range */}
      <div>
        <h3 className="font-semibold mb-3">Price Range</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            handlePriceChange(
              formData.get("min") as string,
              formData.get("max") as string
            );
          }}
          className="space-y-3"
        >
          <div className="flex gap-2 items-center">
            <div className="flex-1">
              <Label htmlFor="min-price" className="sr-only">
                Min Price
              </Label>
              <Input
                id="min-price"
                name="min"
                type="number"
                placeholder="Min"
                defaultValue={minPrice}
                min={0}
                step="0.01"
              />
            </div>
            <span className="text-muted-foreground">-</span>
            <div className="flex-1">
              <Label htmlFor="max-price" className="sr-only">
                Max Price
              </Label>
              <Input
                id="max-price"
                name="max"
                type="number"
                placeholder="Max"
                defaultValue={maxPrice}
                min={0}
                step="0.01"
              />
            </div>
          </div>
          <Button type="submit" variant="secondary" size="sm" className="w-full">
            Apply Price Filter
          </Button>
        </form>
      </div>

      <Separator />

      {/* Availability */}
      <div>
        <h3 className="font-semibold mb-3">Availability</h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={inStock}
            onChange={(e) => handleInStockChange(e.target.checked)}
            className="rounded border-gray-300 text-primary focus:ring-primary"
          />
          <span className="text-sm">In Stock Only</span>
        </label>
      </div>
    </div>
  );
}
