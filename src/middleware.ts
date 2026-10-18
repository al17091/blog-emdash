import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();
  const url = new URL(context.request.url);

  // Security headers for application responses
  if (!response.headers.has("X-Content-Type-Options")) {
    response.headers.set("X-Content-Type-Options", "nosniff");
  }
  if (!response.headers.has("Referrer-Policy")) {
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  }
  if (!response.headers.has("Cross-Origin-Opener-Policy")) {
    response.headers.set("Cross-Origin-Opener-Policy", "same-origin");
  }
  if (!response.headers.has("Cross-Origin-Resource-Policy")) {
    response.headers.set("Cross-Origin-Resource-Policy", "same-origin");
  }
  if (!response.headers.has("Permissions-Policy")) {
    response.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
  }
  if (!response.headers.has("X-Frame-Options")) {
    response.headers.set("X-Frame-Options", "SAMEORIGIN");
  }

  // Content Security Policy for public pages (exempting /_emdash admin and API)
  if (!url.pathname.startsWith("/_emdash")) {
    if (!response.headers.has("Content-Security-Policy")) {
      response.headers.set(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'self';"
      );
    }
  }

  // For admin and API routes, prevent CDN and browser caching
  if (
    url.pathname.startsWith("/_emdash/admin") ||
    url.pathname.startsWith("/_emdash/api") ||
    url.pathname.startsWith("/api")
  ) {
    response.headers.set("Cache-Control", "private, no-cache, no-store, must-revalidate");
    return response;
  }

  // For public pages, apply SWR caching policy if not explicitly overridden:
  // - max-age=0: Browser always revalidates with CDN
  // - s-maxage=60: CloudFront caches for up to 60 seconds
  // - stale-while-revalidate=300: Serves stale cache for 5 minutes during background updates
  if (!response.headers.has("Cache-Control")) {
    response.headers.set(
      "Cache-Control",
      "public, max-age=0, s-maxage=60, stale-while-revalidate=300"
    );
  }

  return response;
});

