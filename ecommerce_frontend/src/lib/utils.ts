import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function formatPrice(
    amount: number,
    currency?: { symbol: string; position: string } | null,
    locale: string = 'en-US'
): string {
    const formatted = new Intl.NumberFormat(locale, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(amount);

    if (!currency) return `$${formatted}`;

    if (currency.position === 'before') {
        return `${currency.symbol}${formatted}`;
    }
    return `${formatted} ${currency.symbol}`;
}

export function formatDate(
    date: string | Date,
    locale: string = 'en-US'
): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    }).format(d);
}

export function formatDateTime(
    date: string | Date,
    locale: string = 'en-US'
): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(d);
}

export function truncate(str: string, length: number): string {
    if (str.length <= length) return str;
    return str.slice(0, length) + '...';
}

export function slugify(str: string): string {
    return str
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

export function getOrderStatusColor(status: string): string {
    switch (status) {
        case 'draft':
            return 'bg-gray-100 text-gray-800';
        case 'sent':
            return 'bg-blue-100 text-blue-800';
        case 'sale':
            return 'bg-green-100 text-green-800';
        case 'cancel':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

export function debounce<T extends (...args: unknown[]) => unknown>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;

    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

export function formatCurrency(
    amount: number,
    currency?: { symbol: string; position: string; code?: string } | null,
    locale: string = 'en-US'
): string {
    return formatPrice(amount, currency, locale);
}

export function getPlaceholderImage(width: number, height: number): string {
    return `https://placehold.co/${width}x${height}/e2e8f0/64748b?text=No+Image`;
}

export function getDiscountPercentage(price: number, comparePrice: number | null): number {
    if (!comparePrice || comparePrice <= price) return 0;
    return Math.round(((comparePrice - price) / comparePrice) * 100);
}
