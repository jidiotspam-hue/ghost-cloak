/**
 * Cloudflare Worker: Serverless Encrypted Egress Relay & Stream Proxy
 * Part of GhostCloak Suite
 * 
 * Purpose:
 * Bypasses school perimeter hardware firewalls (Fortinet, Palo Alto, Cisco Umbrella)
 * by proxying YouTube stream extraction, DNS resolution, and web content
 * through Cloudflare's edge network (*.workers.dev / custom domains).
 * 
 * Free tier: 100,000 requests/day on Cloudflare Workers.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
          "Access-Control-Allow-Headers": "*",
          "Access-Control-Max-Age": "86400"
        }
      });
    }

    // Health check endpoint
    if (url.pathname === "/health" || url.pathname === "/api/health") {
      return new Response(JSON.stringify({
        status: "ok",
        service: "GhostCloak Cloudflare Worker Relay",
        edge_region: request.cf?.colo || "global",
        timestamp: new Date().toISOString()
      }), {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }

    // Encrypted DNS-over-HTTPS (DoH) forwarder
    if (url.pathname === "/api/dns" || url.pathname === "/dns-query") {
      const name = url.searchParams.get("name") || "google.com";
      const type = url.searchParams.get("type") || "A";
      const dohUrl = `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(name)}&type=${encodeURIComponent(type)}`;
      
      const dohResp = await fetch(dohUrl, {
        headers: { "Accept": "application/dns-json" }
      });
      const data = await dohResp.text();
      return new Response(data, {
        headers: {
          "Content-Type": "application/dns-json",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }

    // Direct Forward Proxy Relay /fetch?url=...
    if (url.pathname === "/fetch" || url.pathname === "/api/proxy") {
      const targetUrl = url.searchParams.get("url");
      if (!targetUrl) {
        return new Response(JSON.stringify({ error: "Missing 'url' query parameter" }), {
          status: 400,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });
      }

      try {
        const decodedTarget = decodeURIComponent(targetUrl);
        const upstreamResp = await fetch(decodedTarget, {
          method: request.method,
          headers: {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://docs.google.com/document/u/0/",
            "Origin": "https://docs.google.com"
          }
        });

        const newHeaders = new Headers(upstreamResp.headers);
        newHeaders.set("Access-Control-Allow-Origin", "*");
        newHeaders.delete("x-frame-options");
        newHeaders.delete("content-security-policy");

        return new Response(upstreamResp.body, {
          status: upstreamResp.status,
          headers: newHeaders
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: "Upstream fetch failed", detail: err.message }), {
          status: 502,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });
      }
    }

    // Default dashboard response
    return new Response(JSON.stringify({
      message: "GhostCloak Cloudflare Worker Relay is Active",
      usage: {
        proxy: "/fetch?url=https://example.com",
        dns: "/api/dns?name=example.com",
        health: "/health"
      }
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
};
