import { Suspense } from "react";
import { OdooApiClient } from "@/lib/api";
import { ProductCard, ProductCardSkeleton } from "@/components/product/product-card";
import { ProductFilters } from "./product-filters";
import { ProductSort } from "./product-sort";
import { Pagination } from "./pagination";

interface ShopPageProps {
  searchParams: Promise<{
    page?: string;
    category?: string;
    search?: string;
    order?: string;
    min_price?: string;
    max_price?: string;
    in_stock?: string;
  }>;
}

async function getProducts(searchParams: Awaited<ShopPageProps["searchParams"]>) {
  const api = new OdooApiClient();
  
  try {
    const response = await api.getProducts({
      page: searchParams.page ? parseInt(searchParams.page) : 1,
      limit: 12,
      category: searchParams.category ? parseInt(searchParams.category) : undefined,
      search: searchParams.search,
      order: searchParams.order as "name_asc" | "name_desc" | "price_asc" | "price_desc" | "newest",
      min_price: searchParams.min_price ? parseFloat(searchParams.min_price) : undefined,
      max_price: searchParams.max_price ? parseFloat(searchParams.max_price) : undefined,
      in_stock: searchParams.in_stock === "true" ? true : undefined,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch products:", error);
    return { products: [], pagination: { page: 1, limit: 12, total: 0, total_pages: 0, has_next: false, has_prev: false } };
  }
}

async function getCategories() {
  const api = new OdooApiClient();
  try {
    const response = await api.getCategories();
    return response.data || [];
  } catch (error) {
    console.error("Failed to fetch categories:", error);
    return [];
  }
}

export default async function ShopPage({ searchParams }: ShopPageProps) {
  const params = await searchParams;
  const [productsData, categories] = await Promise.all([
    getProducts(params),
    getCategories(),
  ]);

  const products = productsData?.products || [];
  const pagination = productsData?.pagination;

  return (
    <div className="container py-8">
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Shop</h1>
          <p className="text-muted-foreground mt-2">
            Browse our collection of products
          </p>
        </div>

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Filters */}
          <aside className="w-full lg:w-64 shrink-0">
            <Suspense fallback={<div className="h-96 bg-muted animate-pulse rounded-lg" />}>
              <ProductFilters 
                categories={categories} 
                currentCategory={params.category}
                minPrice={params.min_price}
                maxPrice={params.max_price}
                inStock={params.in_stock === "true"}
              />
            </Suspense>
          </aside>

          {/* Product Grid */}
          <div className="flex-1">
            {/* Sort and Results */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <p className="text-sm text-muted-foreground">
                {pagination?.total || 0} products found
              </p>
              <ProductSort currentOrder={params.order} />
            </div>

            {/* Products */}
            <Suspense
              fallback={
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <ProductCardSkeleton key={i} />
                  ))}
                </div>
              }
            >
              {products.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No products found.</p>
                </div>
              )}
            </Suspense>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="mt-8">
                <Pagination
                  currentPage={pagination.page}
                  totalPages={pagination.total_pages}
                  hasNext={pagination.has_next}
                  hasPrev={pagination.has_prev}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
