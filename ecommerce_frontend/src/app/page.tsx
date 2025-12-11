import {
    ArrowRight,
    Gift,
    HeadphonesIcon,
    Shield,
    Sparkles,
    Star,
    TrendingUp,
    Truck,
    Zap,
} from "lucide-react";
import Link from "next/link";

import { ProductCard } from "@/components/product/product-card";
import { OdooApiClient } from "@/lib/api";
import { getImageUrl } from "@/lib/utils";

async function getFeaturedProducts() {
  const api = new OdooApiClient();
  try {
    const response = await api.getProducts({ limit: 8 });
    return response.data?.products || [];
  } catch (error) {
    console.error("Failed to fetch featured products:", error);
    return [];
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

export default async function HomePage() {
  const [products, categories] = await Promise.all([
    getFeaturedProducts(),
    getCategories(),
  ]);

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 hero-mesh" />
        <div className="absolute inset-0 dot-grid opacity-50" />
        
        {/* Floating Shapes */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/30 rounded-full blur-3xl animate-blob" />
        <div className="absolute top-40 right-10 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-blob" style={{ animationDelay: "2s" }} />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl animate-blob" style={{ animationDelay: "4s" }} />

        <div className="container relative z-10 py-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card animate-fade-in-down">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">New Collection 2025</span>
              </div>

              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight animate-fade-in-up">
                Discover
                <span className="block gradient-text">Extraordinary</span>
                Products
              </h1>

              <p className="text-xl text-muted-foreground max-w-lg animate-fade-in-up stagger-2">
                Curated collections that blend quality, style, and innovation.
                Shop the future of e-commerce today.
              </p>

              <div className="flex flex-wrap gap-4 animate-fade-in-up stagger-3">
                <Link
                  href="/shop"
                  className="group inline-flex items-center gap-2 px-8 py-4 rounded-full gradient-bg text-white font-semibold btn-shine hover:shadow-2xl hover:shadow-primary/25 transition-all duration-300"
                >
                  Shop Now
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/shop?order=newest"
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-full glass-card font-semibold hover:bg-white/80 dark:hover:bg-white/10 transition-all duration-300"
                >
                  New Arrivals
                  <Zap className="w-5 h-5 text-primary" />
                </Link>
              </div>

              {/* Stats */}
              <div className="flex gap-8 pt-8 animate-fade-in-up stagger-4">
                <div>
                  <p className="text-3xl font-bold gradient-text">10K+</p>
                  <p className="text-sm text-muted-foreground">Happy Customers</p>
                </div>
                <div className="w-px bg-border" />
                <div>
                  <p className="text-3xl font-bold gradient-text">500+</p>
                  <p className="text-sm text-muted-foreground">Products</p>
                </div>
                <div className="w-px bg-border" />
                <div>
                  <p className="text-3xl font-bold gradient-text">4.9</p>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    Rating
                  </p>
                </div>
              </div>
            </div>

            {/* Right Content - Featured Visual */}
            <div className="relative hidden lg:block">
              <div className="relative w-full aspect-square">
                {/* Glowing Ring */}
                <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-spin-slow" />
                <div className="absolute inset-4 rounded-full border-2 border-pink-500/20 animate-spin-slow" style={{ animationDirection: "reverse" }} />
                
                {/* Center Circle */}
                <div className="absolute inset-8 rounded-full gradient-bg-subtle flex items-center justify-center">
                  <div className="w-3/4 h-3/4 rounded-full bg-gradient-to-br from-white to-transparent dark:from-white/10 flex items-center justify-center shadow-2xl">
                    <div className="text-center space-y-2 p-8">
                      <Gift className="w-16 h-16 mx-auto text-primary animate-bounce-subtle" />
                      <p className="text-2xl font-bold">Special Offer</p>
                      <p className="text-4xl font-black gradient-text">30% OFF</p>
                      <p className="text-sm text-muted-foreground">First Purchase</p>
                    </div>
                  </div>
                </div>

                {/* Floating Product Cards */}
                <div className="absolute top-0 left-0 glass-card p-4 animate-float">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <p className="font-semibold">Trending</p>
                      <p className="text-xs text-muted-foreground">+250 items</p>
                    </div>
                  </div>
                </div>

                <div className="absolute bottom-10 right-0 glass-card p-4 float-delayed">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-pink-500/10 flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-pink-500" />
                    </div>
                    <div>
                      <p className="font-semibold">Premium</p>
                      <p className="text-xs text-muted-foreground">Quality first</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 rounded-full border-2 border-muted-foreground/30 flex justify-center pt-2">
            <div className="w-1 h-2 rounded-full bg-muted-foreground/50" />
          </div>
        </div>
      </section>

      {/* Categories Section */}
      {categories.length > 0 && (
        <section className="py-24 relative overflow-hidden">
          <div className="absolute inset-0 mesh-gradient opacity-50" />
          <div className="container relative z-10">
            <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-4 mb-12">
              <div className="space-y-2">
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium gradient-bg text-white">
                  CATEGORIES
                </span>
                <h2 className="text-4xl md:text-5xl font-bold">
                  Shop by <span className="gradient-text">Category</span>
                </h2>
                <p className="text-muted-foreground max-w-md">
                  Explore our curated collections and find exactly what you&apos;re looking for
                </p>
              </div>
              <Link
                href="/shop"
                className="group inline-flex items-center gap-2 text-sm font-medium text-primary hover:gap-3 transition-all"
              >
                View All Categories
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {categories.slice(0, 8).map((category, index) => (
                <Link
                  key={category.id}
                  href={`/shop?category=${category.id}`}
                  className={`group relative aspect-[4/5] overflow-hidden rounded-3xl card-glow animate-fade-in-up stagger-${index + 1}`}
                >
                  {/* Background */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-pink-500/5" />
                  
                  {category.image && (
                    <img
                      src={getImageUrl(category.image)}
                      alt={category.name}
                      className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />
                  )}
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                  
                  {/* Content */}
                  <div className="absolute inset-0 flex flex-col justify-end p-6">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:translate-y-0 translate-y-2 transition-transform duration-300">
                      {category.name}
                    </h3>
                    <div className="flex items-center gap-2 text-white/80 opacity-0 group-hover:opacity-100 -translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                      <span className="text-sm">Explore</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Hover Border */}
                  <div className="absolute inset-0 rounded-3xl border-2 border-transparent group-hover:border-white/20 transition-colors duration-300" />
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Featured Products Section */}
      <section className="py-24 relative">
        <div className="container">
          <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-4 mb-12">
            <div className="space-y-2">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                <Sparkles className="w-3 h-3" />
                FEATURED
              </span>
              <h2 className="text-4xl md:text-5xl font-bold">
                Trending <span className="gradient-text">Products</span>
              </h2>
              <p className="text-muted-foreground max-w-md">
                Discover our most popular items loved by thousands of customers
              </p>
            </div>
            <Link
              href="/shop"
              className="group inline-flex items-center gap-2 px-6 py-3 rounded-full border border-primary/20 hover:border-primary hover:bg-primary/5 transition-all duration-300"
            >
              <span className="font-medium">View All Products</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {products.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {products.map((product, index) => (
                <div
                  key={product.id}
                  className={`animate-fade-in-up stagger-${(index % 8) + 1}`}
                >
                  <ProductCard product={product} />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20 glass-card rounded-3xl">
              <Sparkles className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-xl font-medium">No products available</p>
              <p className="text-muted-foreground">Check back soon for new arrivals!</p>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 gradient-bg opacity-5" />
        <div className="container relative z-10">
          <div className="text-center mb-16 space-y-4">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium gradient-bg text-white">
              WHY CHOOSE US
            </span>
            <h2 className="text-4xl md:text-5xl font-bold">
              The <span className="gradient-text">Best</span> Shopping Experience
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We&apos;re committed to providing you with the best online shopping experience possible
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group relative p-8 rounded-3xl glass-card hover-lift">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl group-hover:bg-primary/20 transition-colors" />
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Truck className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">Lightning Fast Delivery</h3>
                <p className="text-muted-foreground">
                  Get your orders delivered within 24-48 hours. Free shipping on orders over $50.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="group relative p-8 rounded-3xl glass-card hover-lift">
              <div className="absolute top-0 right-0 w-32 h-32 bg-pink-500/10 rounded-full blur-3xl group-hover:bg-pink-500/20 transition-colors" />
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">Secure Shopping</h3>
                <p className="text-muted-foreground">
                  Your data is protected with bank-level encryption. Shop with complete confidence.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="group relative p-8 rounded-3xl glass-card hover-lift">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl group-hover:bg-cyan-500/20 transition-colors" />
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <HeadphonesIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">24/7 Support</h3>
                <p className="text-muted-foreground">
                  Our dedicated support team is always here to help you with any questions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 dot-grid opacity-20" />
        
        {/* Floating Shapes */}
        <div className="absolute -top-20 -left-20 w-72 h-72 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -right-20 w-96 h-96 bg-white/10 rounded-full blur-3xl" />

        <div className="container relative z-10">
          <div className="max-w-3xl mx-auto text-center text-white space-y-6">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 text-sm font-medium backdrop-blur-sm">
              <Sparkles className="w-4 h-4" />
              JOIN OUR COMMUNITY
            </span>
            <h2 className="text-4xl md:text-5xl font-bold">
              Get 20% Off Your First Order
            </h2>
            <p className="text-lg text-white/80">
              Subscribe to our newsletter and stay updated with the latest products,
              exclusive deals, and insider tips.
            </p>
            <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 rounded-full bg-white/20 backdrop-blur-sm border border-white/20 text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-white/40"
              />
              <button
                type="submit"
                className="px-8 py-4 rounded-full bg-white text-primary font-semibold hover:bg-white/90 transition-colors btn-shine"
              >
                Subscribe
              </button>
            </form>
            <p className="text-sm text-white/60">
              No spam, unsubscribe at any time.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
