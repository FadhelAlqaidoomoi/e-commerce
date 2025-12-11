import { ProductCard, ProductCardSkeleton } from "@/components/product/product-card";
import { OdooApiClient } from "@/lib/api";
import { LayoutGrid, SlidersHorizontal, Sparkles } from "lucide-react";
import { Suspense } from "react";
import { Pagination } from "./pagination";
import { ProductFilters } from "./product-filters";
import { ProductSort } from "./product-sort";

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
    <div className="min-h-screen">
      {/* Hero Banner */}
      <section className="relative py-16 overflow-hidden">
        <div className="absolute inset-0 gradient-bg opacity-5" />
        <div className="absolute inset-0 dot-grid opacity-30" />
        <div className="container relative z-10">
          <div className="max-w-2xl space-y-4">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium gradient-bg text-white">
              <Sparkles className="w-3 h-3" />
              {params.search ? `Results for "${params.search}"` : "EXPLORE"}
            </span>
            <h1 className="text-4xl md:text-5xl font-bold">
              {params.search ? (
                <>Search Results</>
              ) : (
                <>
                  Discover Our <span className="gradient-text">Collection</span>
                </>
              )}
            </h1>
            <p className="text-lg text-muted-foreground">
              {params.search
                ? `Found ${pagination?.total || 0} products matching your search`
                : "Browse through our curated selection of premium products"}
            </p>
          </div>
        </div>
      </section>

      <div className="container pb-16">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Filters */}
          <aside className="w-full lg:w-72 shrink-0">
            <div className="sticky top-28">
              <div className="glass-card p-6 space-y-6">
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="w-5 h-5 text-primary" />
                  <h2 className="font-bold text-lg">Filters</h2>
                </div>
                <Suspense fallback={<div className="h-96 skeleton rounded-xl" />}>
                  <ProductFilters 
                    categories={categories} 
                    currentCategory={params.category}
                    minPrice={params.min_price}
                    maxPrice={params.max_price}
                    inStock={params.in_stock === "true"}
                  />
                </Suspense>
              </div>
            </div>
          </aside>

          {/* Product Grid */}
          <div className="flex-1">
            {/* Sort and Results Bar */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 p-4 rounded-2xl bg-secondary/30">
              <div className="flex items-center gap-3">
                <LayoutGrid className="w-5 h-5 text-primary" />
                <p className="text-sm">
                  Showing <span className="font-bold text-primary">{products.length}</span> of{" "}
                  <span className="font-bold">{pagination?.total || 0}</span> products
                </p>
              </div>
              <ProductSort currentOrder={params.order} />
            </div>

            {/* Products */}
            <Suspense
              fallback={
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <ProductCardSkeleton key={i} />
                  ))}
                </div>
              }
            >
              {products.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                  {products.map((product, index) => (
                    <div
                      key={product.id}
                      className={`animate-fade-in-up stagger-${(index % 6) + 1}`}
                    >
                      <ProductCard product={product} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 glass-card rounded-3xl">
                  <div className="w-20 h-20 mx-auto rounded-full gradient-bg-subtle flex items-center justify-center mb-6">
                    <Sparkles className="w-10 h-10 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">No products found</h3>
                  <p className="text-muted-foreground max-w-md mx-auto">
                    We couldn&apos;t find any products matching your criteria. Try adjusting your
                    filters or search terms.
                  </p>
                </div>
              )}
            </Suspense>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="mt-12 flex justify-center">
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
