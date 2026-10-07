#!/usr/bin/env python3
"""
Test suite for the All-in-One Proxy Server.
Verifies:
1. Server is responding on port 8080.
2. Web Dashboard UI loads with Stealth features.
3. API status endpoint works.
4. Web Gateway browsing works.
5. Standard Forward HTTP & HTTPS CONNECT proxy works.
6. Undetectable Stealth URL Obfuscation & Address Bar Cloaking works.
"""

import urllib.request
import urllib.parse
import json
import sys

PROXY_ADDR = "http://127.0.0.1:8080"
# direct_opener bypasses any environment or system proxy settings when testing local endpoints
direct_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def test_dashboard():
    print("[1/6] Testing Web Dashboard UI...")
    req = urllib.request.Request(f"{PROXY_ADDR}/")
    with direct_opener.open(req, timeout=5) as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "Proxy" in content
        assert "Stealth" in content
        print("  ✓ Dashboard returned 200 OK with Stealth controls")

def test_api():
    print("[2/6] Testing API Status Endpoint...")
    req = urllib.request.Request(f"{PROXY_ADDR}/api/status")
    with direct_opener.open(req, timeout=5) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "requests_handled" in data
        assert "uptime_seconds" in data
        print(f"  ✓ API status OK (uptime: {data['uptime_seconds']}s, requests: {data['requests_handled']})")

def test_web_gateway():
    print("[3/6] Testing Standard Web Gateway (/browse?url=https://example.com)...")
    target = urllib.parse.quote("https://example.com")
    req = urllib.request.Request(f"{PROXY_ADDR}/browse?url={target}")
    with direct_opener.open(req, timeout=10) as resp:
        assert resp.status == 200
        html = resp.read().decode("utf-8")
        assert "Example Domain" in html
        print("  ✓ Web Gateway proxied example.com successfully")

def test_forward_http_proxy():
    print("[4/6] Testing Forward HTTP Proxy...")
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY_ADDR})
    opener = urllib.request.build_opener(proxy_handler)
    with opener.open('http://example.com', timeout=10) as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "Example Domain" in content
        print("  ✓ Forward HTTP proxy routed request successfully")

def test_forward_https_proxy():
    print("[5/6] Testing Forward HTTPS CONNECT Tunneling...")
    proxy_handler = urllib.request.ProxyHandler({'https': PROXY_ADDR})
    opener = urllib.request.build_opener(proxy_handler)
    with opener.open('https://example.com', timeout=10) as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "Example Domain" in content
        print("  ✓ Forward HTTPS CONNECT tunnel successfully established and verified")

def test_stealth_mode():
    print("[6/6] Testing Undetectable Stealth URL & Address Bar Cloaking...")
    # 1. Test URL obfuscation endpoint
    req_enc = urllib.request.Request(f"{PROXY_ADDR}/api/encode?url=https://example.com")
    with direct_opener.open(req_enc, timeout=5) as resp:
        assert resp.status == 200
        enc_data = json.loads(resp.read().decode("utf-8"))
        stealth_path = enc_data["stealth_url"]
        assert "example.com" not in stealth_path
        print(f"  ✓ Target URL successfully obfuscated to: {stealth_path}")

    # 2. Fetch via stealth path
    req_stealth = urllib.request.Request(f"{PROXY_ADDR}{stealth_path}")
    with direct_opener.open(req_stealth, timeout=10) as resp:
        assert resp.status == 200
        html = resp.read().decode("utf-8")
        assert "Example Domain" in html
        assert "UNDETECTABLE STEALTH ENGINE" in html
        assert "replaceState(null, '', '/app/session')" in html
        print("  ✓ Stealth proxy fetched successfully with address-bar cloaking script verified")

if __name__ == "__main__":
    try:
        test_dashboard()
        test_api()
        test_web_gateway()
        test_forward_http_proxy()
        test_forward_https_proxy()
        test_stealth_mode()
        print("\n========================================================")
        print(" ALL 6 TESTS (INCLUDING STEALTH URL) PASSED! ")
        print("========================================================")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
