import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { Currency } from "./types"

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'
const USE_IMAGE_PROXY = process.env.NEXT_PUBLIC_USE_IMAGE_PROXY === 'true'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format amount with currency from Odoo
 * Handles Currency object with symbol, position, and code
 */
export function formatCurrency(amount: number, currency?: Currency | string | null): string {
  // Handle null/undefined
  if (!currency) {
    return amount.toFixed(2)
  }
  
  // Handle string currency code (e.g., "USD", "BHD")
  if (typeof currency === "string") {
    try {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency,
      }).format(amount)
    } catch {
      // If currency code is invalid, just format as number
      return `${currency} ${amount.toFixed(2)}`
    }
  }
  
  // Handle Currency object from Odoo
  const { symbol, position, code } = currency
  
  // Try to use Intl.NumberFormat with the currency code
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: code,
    }).format(amount)
  } catch {
    // If currency code not supported by Intl, format manually
    const formattedAmount = amount.toFixed(2)
    if (position === "before") {
      return `${symbol}${formattedAmount}`
    } else {
      return `${formattedAmount} ${symbol}`
    }
  }
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

/**
 * Format a date string to a readable format
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(d)
}

/**
 * Format a date string to include time
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d)
}

/**
 * Get CSS class for order status badge
 */
export function getOrderStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-blue-100 text-blue-800',
    sale: 'bg-green-100 text-green-800',
    done: 'bg-green-100 text-green-800',
    cancel: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}
