import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'
const USE_IMAGE_PROXY = process.env.NEXT_PUBLIC_USE_IMAGE_PROXY === 'true'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency?: string | object): string {
  const currencyCode = typeof currency === "string" ? currency : "USD"
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currencyCode,
  }).format(amount)
}

export function getPlaceholderImage(width: number, height: number): string {
  return `https://placehold.co/${width}x${height}/png`
}

export function getDiscountPercentage(price: number, comparePrice?: number | null): number {
  if (!comparePrice || comparePrice <= price) {
    return 0
  }
  return Math.round(((comparePrice - price) / comparePrice) * 100)
}

/**
 * Get image URL - uses proxy in development to enable Next.js image optimization
 * In production, use your actual domain or CDN
 */
export function getImageUrl(path: string | null | undefined): string {
  if (!path) return getPlaceholderImage(300, 300)
  
  // Already a full URL
  if (path.startsWith('http')) {
    // If it's a localhost URL and we want to proxy it
    if (USE_IMAGE_PROXY && (path.includes('localhost') || path.includes('127.0.0.1'))) {
      // Extract the path portion and use proxy
      const url = new URL(path)
      return `/api/image${url.pathname}`
    }
    return path
  }
  
  // Relative path - use proxy for optimization
  if (USE_IMAGE_PROXY) {
    return `/api/image${path}`
  }
  
  return `${ODOO_URL}${path}`
}

/**
 * Check if image is from localhost (needs unoptimized or proxy)
 */
export function isLocalImage(url: string | null | undefined): boolean {
  if (!url) return false
  // If using proxy, localhost images are served from our domain
  if (USE_IMAGE_PROXY && url.startsWith('/api/image')) return false
  return url.includes('localhost') || url.includes('127.0.0.1')
}
