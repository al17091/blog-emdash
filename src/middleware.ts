import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();
  const url = new URL(context.request.url);

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

