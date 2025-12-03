import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {/* Company Info */}
          <div className="col-span-2 md:col-span-1">
            <h3 className="text-lg font-semibold mb-4">Store</h3>
            <p className="text-sm text-muted-foreground">
              Your one-stop shop for all your needs. Quality products at
              affordable prices.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/shop"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Shop
                </Link>
              </li>
              <li>
                <Link
                  href="/shop?order=newest"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  New Arrivals
                </Link>
              </li>
              <li>
                <Link
                  href="/shop?type=sale"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Sale
                </Link>
              </li>
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h4 className="font-semibold mb-4">Customer Service</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/contact"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Contact Us
                </Link>
              </li>
              <li>
                <Link
                  href="/faq"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  FAQ
                </Link>
              </li>
              <li>
                <Link
                  href="/shipping"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Shipping Info
                </Link>
              </li>
              <li>
                <Link
                  href="/returns"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Returns Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Account */}
          <div>
            <h4 className="font-semibold mb-4">My Account</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/account"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  My Profile
                </Link>
              </li>
              <li>
                <Link
                  href="/account/orders"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Order History
                </Link>
              </li>
              <li>
                <Link
                  href="/cart"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Shopping Cart
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Store. All rights reserved.
            </p>
            <p className="text-sm text-muted-foreground">
              Powered by Odoo & Next.js
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
