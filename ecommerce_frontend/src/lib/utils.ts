import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'

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

export function getImageUrl(path: string | null | undefined): string {
  if (!path) return getPlaceholderImage(300, 300)
  if (path.startsWith('http')) return path
  return `${ODOO_URL}${path}`
}
