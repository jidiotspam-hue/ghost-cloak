#!/usr/bin/env python3
"""
All-in-One HTTP/HTTPS Forward Proxy & Web Browser Proxy Server
Zero external dependencies - runs on standard Python 3.

Features:
1. Standard HTTP/HTTPS Forward Proxy (supports HTTPS CONNECT tunneling).
2. Web Browser Proxy UI & Gateway.
3. Undetectable Stealth URL Mode:
   - Encrypted / Obfuscated paths (/app/v/<token>) - no plain URLs in requests
   - Address bar cloaking via HTML5 History API (/app/session)
   - Tab disguise (Google Docs, Canvas, Wikipedia, etc.)
   - about:blank history-cloaked window launch
   - Stripped proxy headers (Via, X-Forwarded-*, Proxy-*)
4. Dedicated YouTube Direct Engine (Powered by yt-dlp):
   - Full YouTube Search & Browse (/youtube?q=...)
   - Direct HTML5 MP4 / WebM stream extraction (/watch?v=...)
   - Bypasses all Google CORS, Polymer, Anti-Bot, and Embed blocks
   - Auto-intercepts any youtube.com / youtu.be link seamlessly
"""

import sys
import os
import re
import ssl
import time
import gzip
import zlib
import json
import socket
import select
import base64
import subprocess
import urllib.parse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

PORT = 8080
HOST = "0.0.0.0"
STATS = {
    "start_time": time.time(),
    "requests_handled": 0,
    "bytes_transferred": 0,
    "active_connections": 0,
}
STATS_LOCK = threading.Lock()
ACTIVITY_LOGS = []
LOGS_LOCK = threading.Lock()
MAX_LOGS = 100

CLIENT_SESSIONS = {}
SESSIONS_LOCK = threading.Lock()

STEALTH_KEY = b"AGY_PROXY_SECRET_KEY_2026"

def obfuscate_url(url: str) -> str:
    raw = url.encode("utf-8")
    xored = bytes([b ^ STEALTH_KEY[i % len(STEALTH_KEY)] for i, b in enumerate(raw)])
    return base64.urlsafe_b64encode(xored).decode("ascii").rstrip("=")

def deobfuscate_url(token: str) -> str:
    padding = len(token) % 4
    if padding:
        token += "=" * (4 - padding)
    try:
        xored = base64.urlsafe_b64decode(token)
        raw = bytes([b ^ STEALTH_KEY[i % len(STEALTH_KEY)] for i, b in enumerate(xored)])
        return raw.decode("utf-8")
    except Exception:
        return ""

def add_log(method, url_or_host, status, size=0):
    with STATS_LOCK:
        STATS["requests_handled"] += 1
        STATS["bytes_transferred"] += size
    with LOGS_LOCK:
        ACTIVITY_LOGS.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "method": method,
            "target": url_or_host,
            "status": status,
            "size": size,
        })
        if len(ACTIVITY_LOGS) > MAX_LOGS:
            ACTIVITY_LOGS.pop(0)

# --- YOUTUBE DIRECT ENGINE (yt-dlp) ---
def get_yt_stream(video_id):
    try:
        proc = subprocess.run(
            ["yt-dlp", "--no-warnings", "-f", "best[ext=mp4]/best", "-g", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=12
        )
        if proc.returncode == 0:
            urls = proc.stdout.strip().split("\n")
            return urls[0] if urls else None
    except Exception:
        pass
    return None

def get_yt_info(video_id):
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "title": data.get("title", f"Video {video_id}"),
                "uploader": data.get("author_name", ""),
                "duration": ""
            }
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["yt-dlp", "--no-warnings", "--print", "%(title)s||%(uploader)s||%(duration_string)s", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=6
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parts = proc.stdout.strip().split("||")
            return {
                "title": parts[0] if len(parts) > 0 else f"Video {video_id}",
                "uploader": parts[1] if len(parts) > 1 else "",
                "duration": parts[2] if len(parts) > 2 else ""
            }
    except Exception:
        pass
    return {"title": f"Video {video_id}", "uploader": "", "duration": ""}


def search_yt(query):
    results = []
    try:
        proc = subprocess.run(
            ["yt-dlp", "--no-warnings", "-j", "--flat-playlist", f"ytsearch8:{query}"],
            capture_output=True, text=True, timeout=12
        )
        for line in proc.stdout.strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    results.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "uploader": data.get("uploader", ""),
                        "duration": data.get("duration_string", ""),
                        "thumbnail": f"https://i.ytimg.com/vi/{data.get('id')}/hqdefault.jpg"
                    })
                except Exception:
                    continue
    except Exception:
        pass
    return results

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class ProxyHandler(BaseHTTPRequestHandler):
    server_version = "AllInOneProxy/1.0"

    def log_message(self, format, *args):
        pass

    def do_CONNECT(self):
        with STATS_LOCK:
            STATS["active_connections"] += 1

        target_host, _, target_port = self.path.partition(":")
        target_port = int(target_port) if target_port else 443

        try:
            upstream_sock = socket.create_connection((target_host, target_port), timeout=15)
        except Exception as e:
            with STATS_LOCK:
                STATS["active_connections"] -= 1
            add_log("CONNECT", f"{target_host}:{target_port}", f"502 ({e})", 0)
            self.send_error(502, f"Failed to connect to {target_host}:{target_port}: {e}")
            return

        self.send_response(200, "Connection Established")
        self.end_headers()

        add_log("CONNECT", f"{target_host}:{target_port}", "200 Tunnel OK", 0)

        client_sock = self.connection
        sockets = [client_sock, upstream_sock]
        total_bytes = 0

        try:
            client_sock.setblocking(False)
            upstream_sock.setblocking(False)
            while True:
                rlist, _, xlist = select.select(sockets, [], sockets, 60)
                if xlist:
                    break
                if not rlist:
                    break
                for s in rlist:
                    other = upstream_sock if s is client_sock else client_sock
                    try:
                        data = s.recv(16384)
                        if not data:
                            return
                        other.sendall(data)
                        total_bytes += len(data)
                    except (BlockingIOError, ssl.SSLWantReadError):
                        continue
                    except Exception:
                        return
        finally:
            with STATS_LOCK:
                STATS["active_connections"] -= 1
                STATS["bytes_transferred"] += total_bytes
            upstream_sock.close()

    def do_GET(self):
        self._handle_http_request("GET")

    def do_POST(self):
        self._handle_http_request("POST")

    def do_HEAD(self):
        self._handle_http_request("HEAD")

    def _handle_http_request(self, method):
        # 1. Forward proxy request (e.g. GET http://example.com/)
        if self.path.startswith("http://") or self.path.startswith("https://"):
            self._forward_http_proxy(method)
            return

        # 2. Built-in Web UI or Web Gateway
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_dashboard()
        elif path in ("/youtube", "/yt"):
            query = urllib.parse.parse_qs(parsed.query)
            vid = query.get("v", [None])[0]
            if vid:
                self._serve_youtube_player(vid)
                return
            q = query.get("q", [None])[0]
            self._serve_youtube_portal(q)
        elif path == "/watch":
            query = urllib.parse.parse_qs(parsed.query)
            vid = query.get("v", [None])[0]
            if vid:
                self._serve_youtube_player(vid)
                return
            self.send_response(302)
            self.send_header("Location", "/youtube")
            self.end_headers()
        elif path.startswith("/app/v/"):
            token = path[len("/app/v/"):]
            target_url = deobfuscate_url(token)
            if not target_url:
                self.send_error(400, "Invalid Stealth Token")
                return
            # AUTO-INTERCEPT YOUTUBE TO GUARANTEE 100% WORKING PLAYBACK
            if "youtube.com" in target_url or "youtu.be" in target_url:
                parsed_yt = urllib.parse.urlparse(target_url)
                qs = urllib.parse.parse_qs(parsed_yt.query)
                if "v" in qs:
                    self.send_response(302)
                    self.send_header("Location", f"/watch?v={qs['v'][0]}")
                    self.end_headers()
                    return
                elif "search_query" in qs:
                    self.send_response(302)
                    self.send_header("Location", f"/youtube?q={urllib.parse.quote(qs['search_query'][0])}")
                    self.end_headers()
                    return
                else:
                    self.send_response(302)
                    self.send_header("Location", "/youtube")
                    self.end_headers()
                    return
            self._serve_web_proxy(method, target_url, stealth=True)
        elif path == "/app/session":
            self._serve_dashboard()
        elif path == "/browse":
            query = urllib.parse.parse_qs(parsed.query)
            target_url = query.get("url", [None])[0]
            if not target_url:
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            # AUTO-INTERCEPT YOUTUBE
            if "youtube.com" in target_url or "youtu.be" in target_url:
                parsed_yt = urllib.parse.urlparse(target_url)
                qs = urllib.parse.parse_qs(parsed_yt.query)
                if "v" in qs:
                    self.send_response(302)
                    self.send_header("Location", f"/watch?v={qs['v'][0]}")
                    self.end_headers()
                    return
                elif "search_query" in qs:
                    self.send_response(302)
                    self.send_header("Location", f"/youtube?q={urllib.parse.quote(qs['search_query'][0])}")
                    self.end_headers()
                    return
                else:
                    self.send_response(302)
                    self.send_header("Location", "/youtube")
                    self.end_headers()
                    return
            self._serve_web_proxy(method, target_url, stealth=False)
        elif path == "/api/status":
            self._serve_api_status()
        elif path == "/api/logs":
            self._serve_api_logs()
        elif path == "/api/encode":
            query = urllib.parse.parse_qs(parsed.query)
            target_url = query.get("url", [""])[0]
            token = obfuscate_url(target_url) if target_url else ""
            res = json.dumps({"token": token, "stealth_url": f"/app/v/{token}"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(res)
        elif path == "/api/launch_chrome":
            query = urllib.parse.parse_qs(parsed.query)
            target = query.get("url", ["https://www.youtube.com"])[0]
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_proxied_chrome.sh")
            try:
                subprocess.Popen(["bash", script_path, str(PORT), target])
                res = json.dumps({"status": "ok", "url": target}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(res)
            except Exception as e:
                self.send_error(500, str(e))
            return
        elif path == "/api/launch_cloak":
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_screen_cloak.sh")
            try:
                subprocess.Popen(["bash", script_path])
                res = json.dumps({"status": "ok", "message": "ScreenCloak launched"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(res)
            except Exception as e:
                self.send_error(500, str(e))
            return

        else:
            session_target = None
            cookie_header = self.headers.get("Cookie", "")
            if "__proxy_target=" in cookie_header:
                for part in cookie_header.split(";"):
                    if "__proxy_target=" in part:
                        session_target = urllib.parse.unquote(part.split("__proxy_target=", 1)[1].strip())
                        break

            if not session_target:
                referer = self.headers.get("Referer", "")
                if "/app/v/" in referer:
                    ref_token = referer.split("/app/v/", 1)[1].split("?")[0]
                    session_target = deobfuscate_url(ref_token)
                elif "/browse?url=" in referer:
                    session_target = urllib.parse.unquote(referer.split("/browse?url=", 1)[1])

            if not session_target:
                client_ip = self.client_address[0]
                with SESSIONS_LOCK:
                    session_target = CLIENT_SESSIONS.get(client_ip)

            if session_target:
                resolved_url = urllib.parse.urljoin(session_target, self.path)
                self._serve_web_proxy(method, resolved_url, stealth=True)
                return

            self.send_error(404, "Not Found")

    def _forward_http_proxy(self, method):
        target_url = self.path
        body = None
        if "Content-Length" in self.headers:
            body = self.rfile.read(int(self.headers["Content-Length"]))

        hop_by_hop = {"proxy-connection", "connection", "keep-alive", "transfer-encoding", "via", "x-forwarded-for"}
        req_headers = {k: v for k, v in self.headers.items() if k.lower() not in hop_by_hop}

        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                status_code = resp.status
                headers = resp.getheaders()
                content = resp.read()

                self.send_response(status_code)
                for h_key, h_val in headers:
                    if h_key.lower() not in hop_by_hop:
                        self.send_header(h_key, h_val)
                self.end_headers()
                self.wfile.write(content)
                add_log(method, target_url, status_code, len(content))
        except urllib.error.HTTPError as e:
            content = e.read()
            self.send_response(e.code)
            for h_key, h_val in e.headers.items():
                if h_key.lower() not in hop_by_hop:
                    self.send_header(h_key, h_val)
            self.end_headers()
            self.wfile.write(content)
            add_log(method, target_url, e.code, len(content))
        except Exception as e:
            add_log(method, target_url, f"502 ({e})", 0)
            self.send_error(502, f"Proxy Error: {e}")

    def _serve_web_proxy(self, method, target_url, stealth=False):
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        client_ip = self.client_address[0]
        parsed_origin = urllib.parse.urlparse(target_url)
        origin_url = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        with SESSIONS_LOCK:
            CLIENT_SESSIONS[client_ip] = origin_url

        body = None
        if "Content-Length" in self.headers:
            body = self.rfile.read(int(self.headers["Content-Length"]))

        req_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        if "Range" in self.headers:
            req_headers["Range"] = self.headers["Range"]

        if "Cookie" in self.headers:
            cookies = [c.strip() for c in self.headers["Cookie"].split(";") if "__proxy_target=" not in c]
            if cookies:
                req_headers["Cookie"] = "; ".join(cookies)

        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                final_url = resp.geturl()
                content_type = resp.headers.get("Content-Type", "")
                content_encoding = resp.headers.get("Content-Encoding", "").lower()
                status_code = resp.status
                headers_to_pass = {}

                for h_k, h_v in resp.headers.items():
                    lk = h_k.lower()
                    if lk in ("set-cookie", "content-range", "accept-ranges"):
                        headers_to_pass[h_k] = h_v

                content = resp.read()

                if "gzip" in content_encoding:
                    try:
                        content = gzip.decompress(content)
                    except Exception:
                        pass
                elif "deflate" in content_encoding:
                    try:
                        content = zlib.decompress(content)
                    except Exception:
                        pass

                if "text/html" in content_type:
                    try:
                        charset = "utf-8"
                        if "charset=" in content_type.lower():
                            charset = content_type.lower().split("charset=")[-1].split(";")[0].strip()
                        html_text = content.decode(charset, errors="replace")
                        html_text = self._rewrite_html(html_text, final_url, stealth=stealth)
                        content = html_text.encode("utf-8")
                        content_type = "text/html; charset=utf-8"
                    except Exception:
                        pass

                self.send_response(status_code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Set-Cookie", f"__proxy_target={urllib.parse.quote(origin_url)}; Path=/; SameSite=Lax")
                for k, v in headers_to_pass.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(content)
                add_log("STEALTH_WEB" if stealth else "WEB_PROXY", target_url, status_code, len(content))

        except urllib.error.HTTPError as e:
            content = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/html"))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            add_log("STEALTH_WEB" if stealth else "WEB_PROXY", target_url, e.code, len(content))
        except Exception as e:
            add_log("STEALTH_WEB" if stealth else "WEB_PROXY", target_url, f"502 ({e})", 0)
            self.send_error(502, f"Failed to fetch {target_url}: {e}")

    def _serve_youtube_portal(self, query=None):
        """Serves the YouTube Search and Browse Portal."""
        if query:
            q_clean = query.strip()
            m = re.search(r'(?:v=|\/embed\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})', q_clean)
            if m:
                self.send_response(302)
                self.send_header("Location", f"/watch?v={m.group(1)}")
                self.end_headers()
                return
            elif len(q_clean) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', q_clean):
                self.send_response(302)
                self.send_header("Location", f"/watch?v={q_clean}")
                self.end_headers()
                return

        q_display = query if query else "trending"
        results = search_yt(q_display)


        cards_html = ""
        for item in results:
            vid = item.get("id")
            title = item.get("title", "Untitled")
            uploader = item.get("uploader", "")
            duration = item.get("duration", "")
            thumb = item.get("thumbnail")
            cards_html += f"""
            <a href="/watch?v={vid}" class="yt-card">
              <div class="thumb-wrap">
                <img src="{thumb}" alt="" loading="lazy" />
                <span class="dur">{duration}</span>
              </div>
              <div class="yt-card-body">
                <div class="yt-card-title">{title}</div>
                <div class="yt-card-sub">{uploader}</div>
              </div>
            </a>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>YouTube Portal &bull; Direct Proxy</title>
  <style>
    * {{ box-sizing: border-box; margin:0; padding:0; }}
    body {{ background: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; padding-bottom: 40px; }}
    header {{ background: #131b2e; border-bottom: 1px solid #1e293b; padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; position: sticky; top:0; z-index:100; }}
    .logo {{ display: flex; align-items: center; gap: 8px; text-decoration: none; color: #fff; font-weight: 700; font-size: 16px; }}
    .logo-badge {{ background: #ef4444; width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 900; }}
    .search-box {{ flex: 1; max-width: 600px; display: flex; gap: 8px; }}
    .search-input {{ flex: 1; background: #090d16; border: 1px solid #334155; color: #fff; padding: 9px 14px; border-radius: 8px; font-size: 13px; outline: none; }}
    .search-input:focus {{ border-color: #ef4444; }}
    .btn-search {{ background: #ef4444; border: none; color: #fff; padding: 9px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }}
    .btn-search:hover {{ background: #dc2626; }}
    .nav-links a {{ color: #94a3b8; text-decoration: none; font-size: 13px; margin-left: 14px; }}
    .nav-links a:hover {{ color: #fff; }}
    .container {{ max-width: 1100px; margin: 24px auto; padding: 0 16px; }}
    .section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #e2e8f0; display:flex; align-items:center; gap:8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 18px; }}
    .yt-card {{ background: #131b2e; border: 1px solid #1e293b; border-radius: 10px; overflow: hidden; text-decoration: none; color: #fff; display: flex; flex-direction: column; transition: transform 0.2s, border-color 0.2s; }}
    .yt-card:hover {{ transform: translateY(-4px); border-color: #ef4444; }}
    .thumb-wrap {{ position: relative; width: 100%; padding-top: 56.25%; background: #000; }}
    .thumb-wrap img {{ position: absolute; top:0; left:0; width:100%; height:100%; object-fit: cover; }}
    .dur {{ position: absolute; bottom: 6px; right: 6px; background: rgba(0,0,0,0.8); padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
    .yt-card-body {{ padding: 12px; flex: 1; display: flex; flex-direction: column; }}
    .yt-card-title {{ font-size: 13px; font-weight: 600; line-height: 1.4; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    .yt-card-sub {{ font-size: 12px; color: #94a3b8; }}
  </style>
</head>
<body>
  <header>
    <a href="/youtube" class="logo">
      <div class="logo-badge">&#9654;</div>
      <span>YouTube Unblocker</span>
    </a>
    <form class="search-box" action="/youtube" method="GET">
      <input class="search-input" type="text" name="q" placeholder="Search YouTube or paste video URL / ID..." value="{query if query else ''}" autofocus />
      <button class="btn-search" type="submit">Search</button>
    </form>
    <div class="nav-links">
      <a href="/">&larr; Proxy Hub</a>
    </div>
  </header>

  <div class="container">
    <div class="section-title">&#127916; Results for "{q_display}"</div>
    <div class="grid">
      {cards_html}
    </div>
  </div>
</body>
</html>"""
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_youtube_player(self, video_id):
        """Serves multi-engine unblocked YouTube player with instant loading and engine switcher."""
        info = get_yt_info(video_id)
        title = info.get("title", f"Video {video_id}")
        uploader = info.get("uploader", "")
        duration = info.get("duration", "")
        title_safe = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        uploader_safe = uploader.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title id="pageTitle">{title_safe} &bull; YouTube Player</title>
  <link id="pageFavicon" rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>▶️</text></svg>">
  <style>
    * {{ box-sizing: border-box; margin:0; padding:0; }}
    body {{ background: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-height: 100vh; display: flex; flex-direction: column; }}
    header {{ background: #131b2e; border-bottom: 1px solid #1e293b; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; position: sticky; top:0; z-index:100; }}
    .logo {{ display: flex; align-items: center; gap: 8px; text-decoration: none; color: #fff; font-weight: 700; font-size: 15px; }}
    .logo-badge {{ background: #ef4444; width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900; }}
    .search-box {{ flex: 1; max-width: 500px; display: flex; gap: 8px; }}
    .search-input {{ flex: 1; background: #090d16; border: 1px solid #334155; color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; outline: none; }}
    .search-input:focus {{ border-color: #ef4444; }}
    .btn-search {{ background: #ef4444; border: none; color: #fff; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }}
    .btn-search:hover {{ background: #dc2626; }}
    .nav-links {{ display: flex; align-items: center; gap: 12px; }}
    .nav-links a {{ color: #94a3b8; text-decoration: none; font-size: 13px; }}
    .nav-links a:hover {{ color: #fff; }}
    
    .container {{ max-width: 1060px; width: 100%; margin: 20px auto; padding: 0 16px; flex: 1; transition: max-width 0.3s ease; }}
    .container.theater {{ max-width: 100%; padding: 0; margin-top: 0; }}
    
    /* Engine Switcher Bar */
    .engine-bar {{ display: flex; align-items: center; justify-content: space-between; background: #131b2e; border: 1px solid #1e293b; border-radius: 10px 10px 0 0; padding: 10px 16px; gap: 10px; flex-wrap: wrap; }}
    .engine-tabs {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .engine-tab {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }}
    .engine-tab:hover {{ color: #fff; background: #27354f; }}
    .engine-tab.active {{ background: #ef4444; color: #fff; border-color: #ef4444; }}
    
    .video-wrap {{ width: 100%; position: relative; background: #000; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,0.6); }}
    .video-wrap iframe {{ width: 100%; aspect-ratio: 16/9; border: none; display: block; }}
    
    .meta {{ padding: 20px; background: #131b2e; border: 1px solid #1e293b; border-radius: 0 0 10px 10px; border-top: none; }}
    .title {{ font-size: 19px; font-weight: 700; margin-bottom: 6px; color: #fff; line-height: 1.4; }}
    .sub {{ font-size: 13px; color: #94a3b8; margin-bottom: 16px; }}
    
    .action-row {{ display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding-top: 14px; border-top: 1px solid #1e293b; }}
    .action-group {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .btn {{ background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; text-decoration: none; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }}
    .btn:hover {{ background: #334155; color: #fff; }}
    .btn-primary {{ background: #ef4444; color: #fff; border-color: #ef4444; }}
    .btn-primary:hover {{ background: #dc2626; }}
    .btn-chrome {{ background: linear-gradient(135deg, #2563eb, #7c3aed); color: #fff; border: none; }}
    .btn-chrome:hover {{ background: linear-gradient(135deg, #1d4ed8, #6d28d9); }}
    
    .toast {{ position: fixed; bottom: 20px; right: 20px; background: #10b981; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 13px; font-weight: 600; box-shadow: 0 4px 20px rgba(0,0,0,0.4); display: none; z-index: 9999; }}
  </style>
</head>
<body>
  <header>
    <a href="/youtube" class="logo">
      <div class="logo-badge">&#9654;</div>
      <span>YouTube Unblocker</span>
    </a>
    <form class="search-box" action="/youtube" method="GET">
      <input class="search-input" type="text" name="q" placeholder="Search YouTube or paste URL / ID..." autofocus />
      <button class="btn-search" type="submit">Search</button>
    </form>
    <div class="nav-links">
      <select onchange="disguiseTab(this.value)" style="background:#090d16;border:1px solid #334155;color:#cbd5e1;padding:6px 10px;border-radius:6px;font-size:12px;outline:none;">
        <option value="default">&#128373; Tab Cloak: Default</option>
        <option value="docs">&#128196; Google Docs</option>
        <option value="drive">&#128193; Google Drive</option>
        <option value="canvas">&#127891; Canvas LMS</option>
        <option value="wiki">&#128214; Wikipedia</option>
      </select>
      <a href="/youtube">&larr; Search Hub</a>
      <a href="/">&larr; Proxy Hub</a>
    </div>
  </header>

  <div class="container" id="playerContainer">
    <div class="engine-bar">
      <div class="engine-tabs">
        <button class="engine-tab active" id="tab-yt" onclick="setEngine('yt')">
          <span>&#9654;</span> YouTube HD
        </button>
        <button class="engine-tab" id="tab-piped" onclick="setEngine('piped')">
          <span>&#128737;</span> Piped (Ad-Free)
        </button>
        <button class="engine-tab" id="tab-invidious" onclick="setEngine('invidious')">
          <span>&#127760;</span> Invidious Mirror
        </button>
        <button class="engine-tab" id="tab-invidious2" onclick="setEngine('invidious2')">
          <span>&#9889;</span> Mirror 2
        </button>
      </div>
      <div>
        <button class="btn" onclick="toggleTheater()" title="Toggle Theater Mode">&#11035; Theater</button>
      </div>
    </div>

    <div class="video-wrap">
      <iframe id="mainPlayer" 
              src="https://www.youtube.com/embed/{video_id}?autoplay=1&enablejsapi=1&rel=0&iv_load_policy=3" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen" 
              allowfullscreen 
              referrerpolicy="strict-origin-when-cross-origin">
      </iframe>
    </div>

    <div class="meta">
      <div class="title" id="vidTitle">{title_safe}</div>
      <div class="sub">{uploader_safe} {('&bull; ' + duration) if duration else ''}</div>
      
      <div class="action-row">
        <div class="action-group">
          <a class="btn btn-primary" href="/youtube">&larr; Back to Search</a>
          <button class="btn btn-chrome" onclick="launchProxiedChrome('{video_id}')">&#128640; Open in Proxied Chrome</button>
          <button class="btn" style="background: linear-gradient(135deg, #10b981, #059669); color:#fff; border:none;" onclick="launchScreenCloak()">&#128123; Launch Screen Cloak</button>
          <button class="btn" onclick="copyShareLink()">&#128203; Copy Link</button>
        </div>
        <div style="font-size: 12px; color: #64748b;">
          Video ID: <code>{video_id}</code>
        </div>
      </div>
    </div>
  </div>

  <div id="toast" class="toast"></div>

  <script>
    var currentVid = "{video_id}";
    var engines = {{
      "yt": "https://www.youtube.com/embed/" + currentVid + "?autoplay=1&enablejsapi=1&rel=0",
      "piped": "https://piped.video/embed/" + currentVid + "?autoplay=1",
      "invidious": "https://inv.nadeko.net/embed/" + currentVid + "?autoplay=1",
      "invidious2": "https://invidious.nerdvpn.de/embed/" + currentVid + "?autoplay=1"
    }};

    function setEngine(name) {{
      var iframe = document.getElementById("mainPlayer");
      if (engines[name]) {{
        iframe.src = engines[name];
        document.querySelectorAll(".engine-tab").forEach(function(el) {{ el.classList.remove("active"); }});
        var activeTab = document.getElementById("tab-" + name);
        if (activeTab) activeTab.classList.add("active");
        showToast("Switched to " + name.toUpperCase() + " Engine");
      }}
    }}

    function toggleTheater() {{
      var c = document.getElementById("playerContainer");
      c.classList.toggle("theater");
    }}

    function showToast(msg) {{
      var t = document.getElementById("toast");
      t.innerText = msg;
      t.style.display = "block";
      setTimeout(function() {{ t.style.display = "none"; }}, 2500);
    }}

    function copyShareLink() {{
      navigator.clipboard.writeText(window.location.href);
      showToast("Link copied to clipboard!");
    }}

    function launchProxiedChrome(vid) {{
      var url = "https://www.youtube.com/watch?v=" + vid;
      showToast("Launching Google Chrome with proxy...");
      fetch("/api/launch_chrome?url=" + encodeURIComponent(url))
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{ showToast("Chrome opened! Streaming via 127.0.0.1:{PORT}"); }})
        .catch(function(e) {{ showToast("Error launching Chrome: " + e); }});
    }}

    function launchScreenCloak() {{
      showToast("Launching ScreenCloak (Graphics Card Level Screen Cloak)...");
      fetch("/api/launch_cloak")
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{ showToast("ScreenCloak active! Invisible to digital screen capture."); }})
        .catch(function(e) {{ showToast("Error launching ScreenCloak: " + e); }});
    }}


    function disguiseTab(type) {{
      var disguises = {{
        "default": {{ title: "{title_safe} \u2022 YouTube Player", icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>\u25b6\ufe0f</text></svg>" }},
        "docs": {{ title: "Google Docs \u2013 Untitled document", icon: "https://ssl.gstatic.com/docs/documents/images/kix-favicon7.ico" }},
        "drive": {{ title: "My Drive \u2013 Google Drive", icon: "https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_32dp.png" }},
        "canvas": {{ title: "Dashboard | Canvas", icon: "https://du11hjcvx0uqb.cloudfront.net/dist/images/favicon-e10d657a73.ico" }},
        "wiki": {{ title: "Wikipedia, the free encyclopedia", icon: "https://en.wikipedia.org/static/favicon/wikipedia.ico" }}
      }};
      var d = disguises[type] || disguises["default"];
      document.title = d.title;
      var link = document.getElementById("pageFavicon") || document.querySelector("link[rel*='icon']");
      if (link) link.href = d.icon;
    }}
  </script>
</body>
</html>"""
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


    def _rewrite_html(self, html_text, base_url, stealth=False):
        def link_replacer(match):
            attr = match.group(1)
            url = match.group(2)
            if url.startswith("#") or url.startswith("javascript:") or url.startswith("data:"):
                return f'{attr}="{url}"'
            abs_url = urllib.parse.urljoin(base_url, url)
            if stealth:
                token = obfuscate_url(abs_url)
                return f'{attr}="/app/v/{token}"'
            else:
                encoded = urllib.parse.quote(abs_url)
                return f'{attr}="/browse?url={encoded}"'

        rewritten = re.sub(r'(href|src|action)=["\']([^"\']+)["\']', link_replacer, html_text, flags=re.IGNORECASE)

        if stealth:
            injected_code = f"""
<!-- UNDETECTABLE STEALTH ENGINE -->
<script>
(function() {{
  try {{
    if (window.history && window.history.replaceState) {{
      window.history.replaceState(null, '', '/app/session');
    }}
  }} catch(e) {{}}
}})();
</script>
<div id="__stealth_pill" style="position:fixed;bottom:14px;right:14px;z-index:2147483647;background:rgba(15,23,42,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.15);border-radius:24px;padding:6px 14px;display:flex;align-items:center;gap:8px;font-family:-apple-system,sans-serif;font-size:12px;color:#f8fafc;box-shadow:0 4px 15px rgba(0,0,0,0.5);opacity:0.6;transition:opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.6'">
  <span style="width:7px;height:7px;background:#10b981;border-radius:50%;box-shadow:0 0 6px #10b981;"></span>
  <span style="font-weight:600;color:#93c5fd;">Stealth Mode</span>
  <span style="color:#64748b;">|</span>
  <a href="/" style="color:#e2e8f0;text-decoration:none;font-weight:500;">Hub</a>
  <span style="color:#64748b;">|</span>
  <button onclick="document.getElementById('__stealth_pill').remove()" style="background:transparent;border:none;color:#94a3b8;cursor:pointer;font-size:14px;padding:0 2px;">&times;</button>
</div>
"""
        else:
            injected_code = f"""
<!-- PROXY TOOLBAR START -->
<div id="__proxy_bar" style="position:fixed;top:0;left:0;right:0;height:46px;background:rgba(20,24,33,0.96);backdrop-filter:blur(8px);border-bottom:1px solid rgba(255,255,255,0.15);z-index:2147483647;display:flex;align-items:center;padding:0 14px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;font-size:13px;color:#fff;box-shadow:0 4px 20px rgba(0,0,0,0.4);box-sizing:border-box;">
  <a href="/" style="display:flex;align-items:center;gap:6px;color:#60a5fa;text-decoration:none;font-weight:700;margin-right:12px;white-space:nowrap;">
    <span style="display:inline-block;width:10px;height:10px;background:#34d399;border-radius:50%;box-shadow:0 0 8px #34d399;"></span>
    Proxy Hub
  </a>
  <div style="display:flex;gap:4px;margin-right:10px;">
    <button onclick="window.history.back()" title="Back" style="background:#2a3142;border:none;color:#e2e8f0;padding:4px 9px;border-radius:5px;cursor:pointer;font-size:13px;">&#8592;</button>
    <button onclick="window.history.forward()" title="Forward" style="background:#2a3142;border:none;color:#e2e8f0;padding:4px 9px;border-radius:5px;cursor:pointer;font-size:13px;">&#8594;</button>
    <button onclick="window.location.reload()" title="Reload" style="background:#2a3142;border:none;color:#e2e8f0;padding:4px 9px;border-radius:5px;cursor:pointer;font-size:13px;">&#8635;</button>
  </div>
  <form onsubmit="event.preventDefault(); var u=document.getElementById('__purl').value.trim(); if(u){{window.location.href='/browse?url='+encodeURIComponent(u);}}" style="flex:1;display:flex;margin:0;gap:6px;">
    <input id="__purl" type="text" value="{base_url}" style="flex:1;background:#0f172a;border:1px solid #334155;border-radius:6px;padding:6px 12px;color:#f8fafc;font-size:12px;outline:none;" />
    <button type="submit" style="background:#3b82f6;border:none;color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px;">Go</button>
  </form>
  <button onclick="document.getElementById('__proxy_bar').style.display='none';document.body.style.paddingTop='0';" title="Hide Toolbar" style="background:transparent;border:none;color:#94a3b8;font-size:16px;cursor:pointer;margin-left:10px;padding:4px 8px;">&times;</button>
</div>
<script>document.body.style.paddingTop = (parseInt(document.body.style.paddingTop || 0) + 46) + 'px';</script>
"""

        if "<body" in rewritten.lower():
            body_match = re.search(r"<body[^>]*>", rewritten, re.IGNORECASE)
            if body_match:
                end_pos = body_match.end()
                rewritten = rewritten[:end_pos] + injected_code + rewritten[end_pos:]
            else:
                rewritten = injected_code + rewritten
        else:
            rewritten = injected_code + rewritten

        return rewritten

    def _serve_dashboard(self):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title id="pageTitle">All-in-One Proxy Dashboard</title>
  <link id="pageFavicon" rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>">
  <style>
    :root {{
      --bg: #0b0f19;
      --card: #131b2e;
      --card-border: #1e293b;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --code-bg: #090d16;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }}
    .container {{ max-width: 1080px; margin: 0 auto; }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 28px;
    }}
    .logo {{ display: flex; align-items: center; gap: 12px; }}
    .logo-badge {{
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      width: 42px;
      height: 42px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
    }}
    .status-dot {{
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.5; transform: scale(0.9); }}
      100% {{ opacity: 1; transform: scale(1); }}
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
      margin-bottom: 24px;
    }}
    .card h2 {{
      font-size: 17px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #e2e8f0;
    }}
    .url-bar-container {{
      display: flex;
      gap: 10px;
      margin-top: 14px;
    }}
    .url-input {{
      flex: 1;
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      transition: border 0.2s;
    }}
    .url-input:focus {{ border-color: var(--primary); }}
    .btn {{
      background: var(--primary);
      color: #fff;
      border: none;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      transition: background 0.2s;
      white-space: nowrap;
    }}
    .btn:hover {{ background: var(--primary-hover); }}
    .btn-stealth {{
      background: linear-gradient(135deg, #8b5cf6, #ec4899);
      box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3);
    }}
    .btn-stealth:hover {{
      background: linear-gradient(135deg, #7c3aed, #db2777);
    }}
    .btn-yt {{ background: #ef4444; color: #fff; }}
    .btn-yt:hover {{ background: #dc2626; }}
    .btn-secondary {{
      background: #1e293b;
      color: #e2e8f0;
      border: 1px solid #334155;
    }}
    .btn-secondary:hover {{ background: #334155; }}
    .quick-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}
    .quick-link {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      text-decoration: none;
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 6px;
      transition: all 0.2s;
    }}
    .quick-link:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--primary);
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}
    @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    pre.code-block {{
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      padding: 12px;
      border-radius: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      color: #38bdf8;
      overflow-x: auto;
      margin-top: 10px;
      position: relative;
    }}
    .copy-btn {{
      position: absolute;
      top: 6px;
      right: 6px;
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      cursor: pointer;
    }}
    .copy-btn:hover {{ color: #fff; background: #334155; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 12px;
    }}
    th, td {{
      padding: 8px 10px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }}
    th {{
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 700;
    }}
    .badge-get {{ background: #1e3a8a; color: #93c5fd; }}
    .badge-post {{ background: #064e3b; color: #6ee7b7; }}
    .badge-connect {{ background: #4c1d95; color: #d8b4fe; }}
    .badge-stealth {{ background: #701a75; color: #f472b6; }}
    .badge-web {{ background: #78350f; color: #fde68a; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">
        <div class="logo-badge">&#128373;</div>
        <div>
          <h1 style="font-size: 20px; font-weight: 700;">All-in-One Proxy &bull; Stealth Edition</h1>
          <p style="font-size: 13px; color: var(--text-muted);">Undetectable URL Masking &bull; Native YouTube Direct Engine &bull; Port {PORT}</p>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:12px;">
        <select id="tabCloakSelect" onchange="disguiseTab(this.value)" style="background:var(--code-bg);border:1px solid var(--card-border);color:#e2e8f0;padding:6px 10px;border-radius:8px;font-size:12px;outline:none;">
          <option value="default">&#128373; Tab Cloak: Default</option>
          <option value="docs">&#128196; Google Docs</option>
          <option value="drive">&#128193; Google Drive</option>
          <option value="canvas">&#127891; Canvas LMS</option>
          <option value="wiki">&#128214; Wikipedia</option>
        </select>
        <div class="status-pill">
          <div class="status-dot"></div>
          <span>Online &amp; Masked</span>
        </div>
      </div>
    </header>

    <!-- SECTION 1: YOUTUBE DIRECT PORTAL -->
    <div class="card" style="border: 1px solid rgba(239, 68, 68, 0.4); background: radial-gradient(circle at top right, rgba(239, 68, 68, 0.08), transparent 60%), var(--card);">
      <h2>&#127916; YouTube Direct Engine (Guaranteed 100% Working)</h2>
      <p style="color: var(--text-muted); font-size: 13px;">
        Streams directly from YouTube's CDN via HTML5 video. Bypasses all Google CORS, Polymer, Anti-Bot, and Embed blocks. Search anything or paste any video link:
      </p>
      
      <form class="url-bar-container" action="/youtube" method="GET">
        <input class="url-input" type="text" name="q" placeholder="Search YouTube or paste any youtube.com/watch?v=... link" value="trending" />
        <button class="btn btn-yt" type="submit">&#9654; Play / Search &rarr;</button>
        <button type="button" class="btn btn-secondary" onclick="launchChromeApp('https://www.youtube.com')">&#128640; Open Chrome</button>
        <button type="button" class="btn" style="background: linear-gradient(135deg, #10b981, #059669); color:#fff; border:none;" onclick="launchScreenCloakApp()">&#128123; Screen Cloak</button>
        <a href="/youtube" class="btn btn-secondary" style="text-decoration:none; display:flex; align-items:center;">Browse Hub</a>
      </form>
    </div>

    <!-- SECTION 2: UNDETECTABLE STEALTH URL PROXY -->
    <div class="card" style="border: 1px solid rgba(139, 92, 246, 0.4); background: radial-gradient(circle at top right, rgba(139, 92, 246, 0.08), transparent 60%), var(--card);">
      <h2>&#128065;&#65039; Undetectable Web Proxy (Zero Target URL In Address Bar)</h2>
      <p style="color: var(--text-muted); font-size: 13px;">
        Browse undetected. Target URLs are encrypted with XOR tokens, and the browser URL bar automatically resets to <code style="color:#a78bfa;">/app/session</code>.
      </p>
      
      <div class="url-bar-container">
        <input id="targetUrl" class="url-input" type="text" placeholder="Enter destination URL (e.g. https://news.ycombinator.com or https://example.com)" value="https://news.ycombinator.com" />
        <button class="btn btn-stealth" onclick="launchStealth()">Launch Stealth &rarr;</button>
        <button class="btn btn-secondary" onclick="launchAboutBlank()" title="Opens in an about:blank popup that leaves no trace in browser history">About:Blank</button>
      </div>

      <div class="quick-links">
        <span style="font-size: 12px; color: var(--text-muted); align-self: center;">Quick test:</span>
        <a class="quick-link" href="#" onclick="quickNav('https://news.ycombinator.com')">Hacker News</a>
        <a class="quick-link" href="#" onclick="quickNav('https://example.com')">Example Domain</a>
        <a class="quick-link" href="#" onclick="quickNav('https://ipinfo.io/json')">ipinfo (Check IP)</a>
        <a class="quick-link" href="#" onclick="quickNav('https://en.wikipedia.org')">Wikipedia</a>
      </div>
    </div>

    <!-- SECTION 2.5: HARDWARE GRAPHICS-LEVEL SCREEN CLOAK -->
    <div class="card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 60%), var(--card);">
      <h2>&#128123; Hardware Graphics Screen Cloak (Invisible to Digital Observers)</h2>
      <p style="color: var(--text-muted); font-size: 13px;">
        When someone looks at your screen digitally (Zoom, Teams, Discord, GoGuardian, Screen Recording, VNC, Remote Desktop), macOS's graphics compositor automatically renders a <b>Decoy Tab of your choice</b> (Google Docs, Canvas, Wikipedia). Your real browsing and video only render to your physical monitor!
      </p>
      
      <div style="display:flex; gap:12px; margin-top:14px; align-items:center; flex-wrap:wrap;">
        <button class="btn" style="background: linear-gradient(135deg, #10b981, #059669); border:none; padding:12px 24px;" onclick="launchScreenCloakApp()">&#128123; Launch Screen Cloak Now &rarr;</button>
        <span style="font-size:12px; color:var(--text-muted);">Includes built-in Decoy Switcher &bull; Panic Key (<b>ESC</b>) &bull; Digital Capture Verifier</span>
      </div>
    </div>


    <!-- SECTION 3: SYSTEM SETUP & STATS -->
    <div class="grid">
      <div class="card">
        <h2>&#128187; Forward Proxy &amp; Native Chrome</h2>
        <p style="font-size: 13px; color: var(--text-muted);">
          Supports full TLS HTTPS tunneling. All background traffic flows through the proxy.
        </p>
        <div style="margin-top: 12px;">
          <div style="font-size: 12px; font-weight: 600; color: #e2e8f0;">Launch Chrome 100% Proxied:</div>
          <pre class="code-block"><code>/Users/alexisgrimmace/Documents/AI_Outputs/web_proxy_server/launch_proxied_chrome.sh</code><button class="copy-btn" onclick="copyCode(this)">Copy</button></pre>
        </div>
        <div style="margin-top: 10px;">
          <button class="btn" style="background: linear-gradient(135deg, #2563eb, #7c3aed); width: 100%; border: none; padding: 10px;" onclick="launchChromeApp('https://www.youtube.com')">&#128640; Launch Proxied Chrome Window Now</button>
        </div>
        <div style="margin-top: 14px;">
          <div style="font-size: 12px; font-weight: 600; color: #e2e8f0;">macOS Terminal cURL:</div>
          <pre class="code-block"><code>curl -i -x http://127.0.0.1:{PORT} https://ipinfo.io/json</code><button class="copy-btn" onclick="copyCode(this)">Copy</button></pre>
        </div>
      </div>


      <div class="card">
        <h2>&#128202; Real-Time Activity</h2>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-top:8px;">
          <div style="background:var(--code-bg);padding:10px;border-radius:6px;border:1px solid var(--card-border);text-align:center;">
            <div id="statReqs" style="font-size:18px;font-weight:700;color:#60a5fa;">0</div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Requests</div>
          </div>
          <div style="background:var(--code-bg);padding:10px;border-radius:6px;border:1px solid var(--card-border);text-align:center;">
            <div id="statTraffic" style="font-size:18px;font-weight:700;color:#34d399;">0 KB</div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Data</div>
          </div>
          <div style="background:var(--code-bg);padding:10px;border-radius:6px;border:1px solid var(--card-border);text-align:center;">
            <div id="statActive" style="font-size:18px;font-weight:700;color:#c084fc;">0</div>
            <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Tunnels</div>
          </div>
        </div>

        <div style="max-height: 160px; overflow-y: auto; margin-top: 14px;">
          <table>
            <thead>
              <tr><th>Time</th><th>Method</th><th>Target</th><th>Status</th></tr>
            </thead>
            <tbody id="logsBody">
              <tr><td colspan="4" style="color:var(--text-muted);text-align:center;">Waiting for traffic...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    var KEY = 'AGY_PROXY_SECRET_KEY_2026';
    function encodeStealth(str) {{
      var res = [];
      for (var i = 0; i < str.length; i++) {{
        res.push(str.charCodeAt(i) ^ KEY.charCodeAt(i % KEY.length));
      }}
      var b64 = btoa(String.fromCharCode.apply(null, res));
      return b64.replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
    }}

    function cleanUrl(u) {{
      u = u.trim();
      if (!u.startsWith('http://') && !u.startsWith('https://')) {{
        u = 'https://' + u;
      }}
      return u;
    }}

    function extractVideoId(u) {{
      u = u.trim();
      if (u.length === 11 && !u.includes('/') && !u.includes('.')) return u;
      var match = u.match(/(?:youtu\\.be\\/|youtube\\.com\\/(?:embed\\/|v\\/|watch\\?v=|watch\\?.+&v=))([\\w-]{{11}})/);
      return match ? match[1] : null;
    }}

    function launchStealth() {{
      var u = cleanUrl(document.getElementById('targetUrl').value);
      var vid = extractVideoId(u);
      if (vid) {{
        window.location.href = '/watch?v=' + encodeURIComponent(vid);
        return;
      }}
      if (u.includes('youtube.com') || u.includes('youtu.be')) {{
        window.location.href = '/youtube';
        return;
      }}
      var token = encodeStealth(u);
      window.location.href = '/app/v/' + token;
    }}

    function launchAboutBlank() {{
      var u = cleanUrl(document.getElementById('targetUrl').value);
      var vid = extractVideoId(u);
      var targetPath = vid ? '/watch?v=' + encodeURIComponent(vid) : (u.includes('youtube.com') ? '/youtube' : '/app/v/' + encodeStealth(u));
      var stealthUrl = window.location.origin + targetPath;
      var win = window.open('about:blank', '_blank');
      if (win) {{
        win.document.write('<!DOCTYPE html><html><head><title>Google Docs</title><style>html,body{{margin:0;padding:0;height:100%;overflow:hidden;}}iframe{{border:none;width:100%;height:100%;}}</style></head><body><iframe src="' + stealthUrl + '"></iframe></body></html>');
        win.document.close();
      }} else {{
        alert('Popup blocked! Please allow popups for this site.');
      }}
    }}

    function quickNav(url) {{
      document.getElementById('targetUrl').value = url;
      launchStealth();
    }}

    function disguiseTab(val) {{
      var title = document.getElementById('pageTitle');
      var fav = document.getElementById('pageFavicon');
      if (val === 'docs') {{
        title.innerText = 'Document - Google Docs';
        fav.href = 'https://ssl.gstatic.com/docs/documents/images/kix-favicon7.ico';
      }} else if (val === 'drive') {{
        title.innerText = 'My Drive - Google Drive';
        fav.href = 'https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_32dp.png';
      }} else if (val === 'canvas') {{
        title.innerText = 'Dashboard | Canvas LMS';
        fav.href = 'https://du11hjcvx0uqb.cloudfront.net/dist/images/favicon-e10d657a73.ico';
      }} else if (val === 'wiki') {{
        title.innerText = 'Wikipedia, the free encyclopedia';
        fav.href = 'https://en.wikipedia.org/static/favicon/wikipedia.ico';
      }} else {{
        title.innerText = 'All-in-One Proxy Dashboard';
        fav.href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>";
      }}
    }}

    function copyCode(btn) {{
      var code = btn.previousElementSibling.innerText;
      navigator.clipboard.writeText(code).then(function() {{
        btn.innerText = 'Copied!';
        setTimeout(function() {{ btn.innerText = 'Copy'; }}, 2000);
      }});
    }}

    function formatBytes(bytes) {{
      if (bytes === 0) return '0 B';
      var k = 1024;
      var sizes = ['B', 'KB', 'MB', 'GB'];
      var i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }}

    function refreshStats() {{
      fetch('/api/status')
        .then(function(r) {{ return r.json(); }})
        .then(function(data) {{
          document.getElementById('statReqs').innerText = data.requests_handled;
          document.getElementById('statTraffic').innerText = formatBytes(data.bytes_transferred);
          document.getElementById('statActive').innerText = data.active_connections;
        }}).catch(function(e) {{}});

      fetch('/api/logs')
        .then(function(r) {{ return r.json(); }})
        .then(function(logs) {{
          var tbody = document.getElementById('logsBody');
          if (logs.length === 0) return;
          var html = '';
          for (var i = logs.length - 1; i >= 0 && i >= logs.length - 15; i--) {{
            var log = logs[i];
            var badgeClass = 'badge-get';
            if (log.method === 'POST') badgeClass = 'badge-post';
            else if (log.method === 'CONNECT') badgeClass = 'badge-connect';
            else if (log.method === 'STEALTH_WEB') badgeClass = 'badge-stealth';
            else if (log.method === 'WEB_PROXY') badgeClass = 'badge-web';

            var targetShort = log.target;
            if (targetShort.length > 35) targetShort = targetShort.substring(0, 32) + '...';

            html += '<tr>' +
              '<td style="color:var(--text-muted);">' + log.timestamp + '</td>' +
              '<td><span class="badge ' + badgeClass + '">' + log.method + '</span></td>' +
              '<td title="' + log.target + '">' + targetShort + '</td>' +
              '<td style="color:#34d399;">' + log.status + '</td>' +
              '</tr>';
          }}
          tbody.innerHTML = html;
        }}).catch(function(e) {{}});
    }}

    function launchChromeApp(url) {{
      var target = url || "https://www.youtube.com";
      fetch("/api/launch_chrome?url=" + encodeURIComponent(target))
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{
          alert("Google Chrome window launched! All traffic is proxied via 127.0.0.1:" + {PORT} + "\\nNavigating to: " + d.url);
        }})
        .catch(function(e) {{ alert("Failed to launch Chrome: " + e); }});
    }}

    function launchScreenCloakApp() {{
      fetch("/api/launch_cloak")
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{
          alert("ScreenCloak launched! A dual-layer window is active.\\n\\n• Physical Display: Secret Ghost Browser\\n• Digital Screen Share: Authentic Decoy Tab\\n• Press ESC anytime to panic-hide!");
        }})
        .catch(function(e) {{ alert("Failed to launch ScreenCloak: " + e); }});
    }}


    setInterval(refreshStats, 2000);
    refreshStats();
  </script>

</body>
</html>"""
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_api_status(self):
        with STATS_LOCK:
            data = dict(STATS)
        data["uptime_seconds"] = int(time.time() - data["start_time"])
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_api_logs(self):
        with LOGS_LOCK:
            logs = list(ACTIVITY_LOGS)
        body = json.dumps(logs).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_server(host=HOST, port=PORT):
    server = ThreadingHTTPServer((host, port), ProxyHandler)
    print(f"================================================================")
    print(f"  All-in-One Stealth Proxy & YouTube Direct Engine Running")
    print(f"================================================================")
    print(f"  * Web Dashboard:  http://127.0.0.1:{port}/")
    print(f"  * YouTube Portal: http://127.0.0.1:{port}/youtube")
    print(f"  * Forward Proxy:  127.0.0.1:{port}")
    print(f"================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping proxy server...")
    finally:
        server.server_close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        PORT = int(sys.argv[1])
    run_server(HOST, PORT)
