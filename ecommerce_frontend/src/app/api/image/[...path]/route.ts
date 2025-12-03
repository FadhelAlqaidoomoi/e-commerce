import { NextRequest, NextResponse } from 'next/server';

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069';

// In-memory cache for image responses (for development)
const imageCache = new Map<string, { data: ArrayBuffer; contentType: string; timestamp: number }>();
const CACHE_DURATION = 60 * 60 * 1000; // 1 hour in milliseconds

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const imagePath = '/' + path.join('/');
  const cacheKey = imagePath;

  // Check cache first
  const cached = imageCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return new NextResponse(cached.data, {
      headers: {
        'Content-Type': cached.contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
        'X-Cache': 'HIT',
      },
    });
  }

  try {
    const imageUrl = `${ODOO_URL}${imagePath}`;
    
    const response = await fetch(imageUrl, {
      headers: {
        'Accept': 'image/*',
      },
      // Cache at fetch level too
      next: { revalidate: 3600 }, // Cache for 1 hour
    });

    if (!response.ok) {
      return new NextResponse('Image not found', { status: 404 });
    }

    const contentType = response.headers.get('content-type') || 'image/png';
    const arrayBuffer = await response.arrayBuffer();

    // Store in cache
    imageCache.set(cacheKey, {
      data: arrayBuffer,
      contentType,
      timestamp: Date.now(),
    });

    // Clean old cache entries periodically
    if (imageCache.size > 1000) {
      const now = Date.now();
      for (const [key, value] of imageCache.entries()) {
        if (now - value.timestamp > CACHE_DURATION) {
          imageCache.delete(key);
        }
      }
    }

    return new NextResponse(arrayBuffer, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
        'X-Cache': 'MISS',
      },
    });
  } catch (error) {
    console.error('Image proxy error:', error);
    return new NextResponse('Failed to fetch image', { status: 500 });
  }
}
