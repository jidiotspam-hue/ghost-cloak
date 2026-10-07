"""
AWS Lambda Serverless Free-Tier Reverse Proxy & Egress Cloak
Part of GhostCloak Suite

Deployment instructions:
1. Create an AWS Lambda function (Python 3.12 or 3.11).
2. Paste this code into lambda_function.py.
3. Under Function Configuration -> Function URL:
   - Auth type: NONE
   - Configure CORS:
     - Allow Origin: *
     - Allow Methods: GET, POST, HEAD, OPTIONS
     - Allow Headers: *
4. Save and deploy.
Free Tier: 1,000,000 invocations and 3.2 million seconds of compute time free every month forever.
Zero bills.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

def lambda_handler(event, context):
    http_method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    raw_path = event.get("rawPath", "/")
    query_params = event.get("queryStringParameters", {}) or {}

    # Handle CORS preflight
    if http_method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400"
            },
            "body": ""
        }

    # Health check endpoint
    if raw_path in ["/health", "/api/health"]:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "ok",
                "service": "GhostCloak AWS Lambda Serverless Egress Relay",
                "cost_tier": "AWS Lambda Forever-Free Tier (1M invocations/mo)",
                "region": context.invoked_function_arn.split(":")[3] if hasattr(context, "invoked_function_arn") else "aws-free"
            })
        }

    # Encrypted DNS-over-HTTPS (DoH) forwarder
    if raw_path in ["/api/dns", "/dns-query"]:
        name = query_params.get("name", "google.com")
        dns_type = query_params.get("type", "A")
        doh_url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(name)}&type={urllib.parse.quote(dns_type)}"
        
        req = urllib.request.Request(
            doh_url,
            headers={
                "Accept": "application/dns-json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read().decode("utf-8")
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/dns-json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": data
                }
        except Exception as e:
            return {
                "statusCode": 502,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "DoH lookup failed", "detail": str(e)})
            }

    # Forward Proxy Relay: /fetch?url=...
    if raw_path in ["/fetch", "/api/proxy"]:
        target_url = query_params.get("url")
        if not target_url:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Missing 'url' query parameter"})
            }

        try:
            target_url = urllib.parse.unquote(target_url)
            req = urllib.request.Request(
                target_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://docs.google.com/document/u/0/",
                    "Origin": "https://docs.google.com"
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "text/plain")
                # Strip framing blockers and security headers
                return {
                    "statusCode": resp.status,
                    "headers": {
                        "Content-Type": content_type,
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "*"
                    },
                    "body": content.decode("utf-8", errors="replace")
                }
        except Exception as e:
            return {
                "statusCode": 502,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Upstream proxy request failed", "detail": str(e)})
            }

    # Default dashboard
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "GhostCloak AWS Lambda Relay is Active",
            "tier": "AWS Free Tier (Zero Cost)",
            "endpoints": {
                "proxy": "/fetch?url=https://example.com",
                "dns": "/api/dns?name=example.com",
                "health": "/health"
            }
        }, indent=2)
    }
