import { Button } from "@/components/ui/button";
import { Home, ShoppingBag, Sparkles } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="relative min-h-[calc(100vh-16rem)] overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-blob" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-blob" style={{ animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-blob" style={{ animationDelay: "4s" }} />
      </div>

      <div className="container relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-16rem)] py-16 text-center">
        {/* 404 Visual */}
        <div className="relative mb-8">
          <span className="text-[12rem] md:text-[16rem] font-black gradient-text leading-none opacity-20">
            404
          </span>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full gradient-bg flex items-center justify-center animate-bounce-subtle">
              <Sparkles className="w-16 h-16 text-white" />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4 max-w-lg animate-fade-in-up">
          <h1 className="text-3xl md:text-4xl font-bold">
            Oops! Page <span className="gradient-text">Not Found</span>
          </h1>
          <p className="text-lg text-muted-foreground">
            Looks like you&apos;ve ventured into uncharted territory. The page you&apos;re
            looking for doesn&apos;t exist or has been moved.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mt-10 animate-fade-in-up stagger-2">
          <Link href="/">
            <Button size="lg" className="rounded-full gradient-bg gap-2 btn-shine">
              <Home className="w-5 h-5" />
              Back to Home
            </Button>
          </Link>
          <Link href="/shop">
            <Button size="lg" variant="outline" className="rounded-full gap-2">
              <ShoppingBag className="w-5 h-5" />
              Browse Products
            </Button>
          </Link>
        </div>

        {/* Quick Links */}
        <div className="mt-16 p-8 rounded-3xl glass-card animate-fade-in-up stagger-3">
          <h3 className="font-semibold mb-4">Popular Destinations</h3>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              { href: "/shop?order=newest", label: "New Arrivals" },
              { href: "/shop?type=sale", label: "Sale Items" },
              { href: "/shop", label: "All Products" },
              { href: "/account", label: "My Account" },
            ].map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-4 py-2 rounded-full bg-secondary/50 hover:bg-primary/10 hover:text-primary transition-colors text-sm"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
