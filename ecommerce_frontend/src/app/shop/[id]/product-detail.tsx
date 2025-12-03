"use client";

import { ChevronLeft, Minus, Plus, ShoppingCart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useCartStore } from "@/lib/store";
import { Product, ProductVariant } from "@/lib/types";
import { formatCurrency, getDiscountPercentage, getImageUrl } from "@/lib/utils";

interface ProductDetailProps {
  product: Product;
}

export function ProductDetail({ product }: ProductDetailProps) {
  const [quantity, setQuantity] = useState(1);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(
    product.variants?.[0] || null
  );
  const [mainImage, setMainImage] = useState(getImageUrl(product.image_large || product.image));

  const { addItem, isLoading } = useCartStore();

  const currentPrice = selectedVariant
    ? product.price + selectedVariant.price_extra
    : product.price;

  const discountPercentage = getDiscountPercentage(currentPrice, product.compare_price);

  const handleQuantityChange = (delta: number) => {
    const newQuantity = quantity + delta;
    if (newQuantity >= 1) {
      setQuantity(newQuantity);
    }
  };

  const handleAddToCart = async () => {
    const productId = selectedVariant?.id || product.id;
    await addItem(productId, quantity);
  };

  const handleVariantChange = (variant: ProductVariant) => {
    setSelectedVariant(variant);
    if (variant.image) {
      setMainImage(getImageUrl(variant.image));
    }
  };

  const allImages = [
    getImageUrl(product.image_large || product.image),
    ...(product.additional_images?.map((img) => getImageUrl(img.url)) || []),
  ].filter(Boolean) as string[];

  const inStock = selectedVariant ? selectedVariant.in_stock : product.in_stock;

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-6">
        <Link
          href="/shop"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back to Shop
        </Link>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="relative aspect-square overflow-hidden rounded-lg bg-muted">
            <Image
              src={mainImage || getImageUrl(null)}
              alt={product.name}
              fill
              className="object-cover"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
            {discountPercentage > 0 && (
              <Badge className="absolute top-4 left-4 bg-red-500 text-white">
                -{discountPercentage}%
              </Badge>
            )}
            {!inStock && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                <Badge variant="destructive" className="text-lg">
                  Out of Stock
                </Badge>
              </div>
            )}
          </div>

          {/* Thumbnails */}
          {allImages.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {allImages.map((img, index) => (
                <button
                  key={index}
                  onClick={() => setMainImage(img)}
                  className={`relative w-20 h-20 rounded-md overflow-hidden shrink-0 border-2 transition-colors ${
                    mainImage === img
                      ? "border-primary"
                      : "border-transparent hover:border-muted-foreground/50"
                  }`}
                >
                  <Image
                    src={img}
                    alt={`${product.name} ${index + 1}`}
                    fill
                    className="object-cover"
                    sizes="80px"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          {/* Categories */}
          {product.categories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {product.categories.map((cat) => (
                <Link key={cat.id} href={`/shop?category=${cat.id}`}>
                  <Badge variant="outline">{cat.name}</Badge>
                </Link>
              ))}
            </div>
          )}

          {/* Title */}
          <h1 className="text-3xl font-bold tracking-tight">{product.name}</h1>

          {/* Price */}
          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold">
              {formatCurrency(currentPrice, product.currency)}
            </span>
            {product.compare_price && product.compare_price > currentPrice && (
              <span className="text-xl text-muted-foreground line-through">
                {formatCurrency(product.compare_price, product.currency)}
              </span>
            )}
          </div>

          {/* Short Description */}
          {product.description_short && (
            <p className="text-muted-foreground">{product.description_short}</p>
          )}

          <Separator />

          {/* Variants */}
          {product.has_variants && product.attributes && product.attributes.length > 0 && (
            <div className="space-y-4">
              {product.attributes.map((attribute) => (
                <div key={attribute.id}>
                  <h3 className="text-sm font-medium mb-2">{attribute.name}</h3>
                  <div className="flex flex-wrap gap-2">
                    {attribute.values.map((value) => {
                      const matchingVariant = product.variants?.find((v) =>
                        v.attribute_values.some(
                          (av) =>
                            av.attribute_id === attribute.id &&
                            av.value_id === value.id
                        )
                      );

                      const isSelected = selectedVariant?.attribute_values.some(
                        (av) =>
                          av.attribute_id === attribute.id &&
                          av.value_id === value.id
                      );

                      return (
                        <button
                          key={value.id}
                          onClick={() =>
                            matchingVariant && handleVariantChange(matchingVariant)
                          }
                          disabled={!matchingVariant}
                          className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                            isSelected
                              ? "bg-primary text-primary-foreground border-primary"
                              : matchingVariant
                              ? "hover:border-primary"
                              : "opacity-50 cursor-not-allowed"
                          }`}
                          style={
                            value.html_color
                              ? { backgroundColor: value.html_color }
                              : undefined
                          }
                        >
                          {!value.html_color && value.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quantity */}
          <div>
            <h3 className="text-sm font-medium mb-2">Quantity</h3>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => handleQuantityChange(-1)}
                disabled={quantity <= 1}
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="w-12 text-center font-medium">{quantity}</span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => handleQuantityChange(1)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Add to Cart */}
          <Button
            size="lg"
            className="w-full"
            onClick={handleAddToCart}
            disabled={!inStock || isLoading}
          >
            <ShoppingCart className="mr-2 h-5 w-5" />
            {isLoading ? "Adding..." : "Add to Cart"}
          </Button>

          {/* SKU/Barcode */}
          {(product.sku || product.barcode) && (
            <div className="text-sm text-muted-foreground space-y-1">
              {product.sku && <p>SKU: {product.sku}</p>}
              {product.barcode && <p>Barcode: {product.barcode}</p>}
            </div>
          )}
        </div>
      </div>

      {/* Full Description */}
      {(product.description || product.description_ecommerce) && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-4">Description</h2>
          <div
            className="prose prose-gray max-w-none"
            dangerouslySetInnerHTML={{
              __html: product.description_ecommerce || product.description || "",
            }}
          />
        </div>
      )}

      {/* Related Products */}
      {(product.alternative_products?.length || product.accessory_products?.length) && (
        <div className="mt-12 space-y-8">
          {product.alternative_products && product.alternative_products.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Similar Products</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {product.alternative_products.slice(0, 4).map((p) => (
                  <Link
                    key={p.id}
                    href={`/shop/${p.id}`}
                    className="group"
                  >
                    <div className="relative aspect-square rounded-lg overflow-hidden bg-muted mb-2">
                      <Image
                        src={getImageUrl(p.image)}
                        alt={p.name}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform"
                        sizes="(max-width: 768px) 50vw, 25vw"
                      />
                    </div>
                    <p className="font-medium text-sm line-clamp-2 group-hover:text-primary transition-colors">
                      {p.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {formatCurrency(p.price, p.currency)}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {product.accessory_products && product.accessory_products.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Accessories</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {product.accessory_products.slice(0, 4).map((p) => (
                  <Link
                    key={p.id}
                    href={`/shop/${p.id}`}
                    className="group"
                  >
                    <div className="relative aspect-square rounded-lg overflow-hidden bg-muted mb-2">
                      <Image
                        src={getImageUrl(p.image)}
                        alt={p.name}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform"
                        sizes="(max-width: 768px) 50vw, 25vw"
                      />
                    </div>
                    <p className="font-medium text-sm line-clamp-2 group-hover:text-primary transition-colors">
                      {p.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {formatCurrency(p.price, p.currency)}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
