import {
    ArrowRight,
    Facebook,
    Heart,
    Instagram,
    Mail,
    MapPin,
    Phone,
    Twitter,
    Youtube,
} from "lucide-react";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background to-secondary/30" />
      <div className="absolute inset-0 dot-grid opacity-30" />

      <div className="relative">
        {/* Main Footer Content */}
        <div className="container py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
            {/* Brand Column */}
            <div className="lg:col-span-2 space-y-6">
              <Link href="/" className="inline-flex items-center space-x-2 group">
                <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-white font-bold text-2xl">S</span>
                </div>
                <span className="text-3xl font-bold gradient-text">Store</span>
              </Link>
              <p className="text-muted-foreground max-w-sm">
                Your premier destination for quality products. We bring you the finest
                selection curated with care and delivered with love.
              </p>
              
              {/* Social Links */}
              <div className="flex items-center gap-3">
                <a
                  href="#"
                  className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary hover:text-white transition-all duration-300 hover:scale-110"
                >
                  <Facebook className="w-5 h-5" />
                </a>
                <a
                  href="#"
                  className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary hover:text-white transition-all duration-300 hover:scale-110"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a
                  href="#"
                  className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-pink-500 hover:text-white transition-all duration-300 hover:scale-110"
                >
                  <Instagram className="w-5 h-5" />
                </a>
                <a
                  href="#"
                  className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-red-500 hover:text-white transition-all duration-300 hover:scale-110"
                >
                  <Youtube className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-4">
              <h4 className="font-bold text-lg">Quick Links</h4>
              <ul className="space-y-3">
                {[
                  { href: "/shop", label: "Shop All" },
                  { href: "/shop?order=newest", label: "New Arrivals" },
                  { href: "/shop?type=sale", label: "Sale" },
                  { href: "/shop?type=bestseller", label: "Best Sellers" },
                ].map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="group inline-flex items-center text-muted-foreground hover:text-primary transition-colors"
                    >
                      <ArrowRight className="w-4 h-4 mr-2 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Customer Service */}
            <div className="space-y-4">
              <h4 className="font-bold text-lg">Support</h4>
              <ul className="space-y-3">
                {[
                  { href: "/contact", label: "Contact Us" },
                  { href: "/faq", label: "FAQ" },
                  { href: "/shipping", label: "Shipping Info" },
                  { href: "/returns", label: "Returns & Refunds" },
                  { href: "/track-order", label: "Track Order" },
                ].map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="group inline-flex items-center text-muted-foreground hover:text-primary transition-colors"
                    >
                      <ArrowRight className="w-4 h-4 mr-2 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact Info */}
            <div className="space-y-4">
              <h4 className="font-bold text-lg">Contact</h4>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 text-muted-foreground">
                  <MapPin className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>123 Commerce Street, Business District, NY 10001</span>
                </li>
                <li className="flex items-center gap-3 text-muted-foreground">
                  <Phone className="w-5 h-5 text-primary shrink-0" />
                  <span>+1 (555) 123-4567</span>
                </li>
                <li className="flex items-center gap-3 text-muted-foreground">
                  <Mail className="w-5 h-5 text-primary shrink-0" />
                  <span>support@store.com</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border/50">
          <div className="container py-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                © {new Date().getFullYear()} Store. Made with
                <Heart className="w-4 h-4 text-red-500 fill-red-500 inline animate-bounce-subtle" />
                All rights reserved.
              </p>
              <div className="flex items-center gap-6">
                <Link
                  href="/privacy"
                  className="text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  Privacy Policy
                </Link>
                <Link
                  href="/terms"
                  className="text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  Terms of Service
                </Link>
                <span className="text-sm text-muted-foreground">
                  Powered by <span className="gradient-text font-semibold">Odoo & Next.js</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="border-t border-border/50">
          <div className="container py-4">
            <div className="flex flex-wrap items-center justify-center gap-4">
              {["Visa", "Mastercard", "PayPal", "Apple Pay", "Google Pay"].map(
                (method) => (
                  <div
                    key={method}
                    className="px-4 py-2 rounded-lg bg-secondary/50 text-xs font-medium text-muted-foreground"
                  >
                    {method}
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
