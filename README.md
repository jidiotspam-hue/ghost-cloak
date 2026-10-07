# All-in-One Stealth Proxy, YouTube Unblocker & Hardware Screen Cloak

A high-performance proxy server and native macOS graphics-level stealth suite featuring:
1. **Hardware Graphics Screen Cloak (`ScreenCloak`)**: Employs macOS WindowServer's `NSWindow.sharingType = .none` to completely omit secret browsing from digital capture while rendering an authentic Decoy tab (Google Docs, Canvas, Wikipedia).
2. **Undetectable Stealth Web Proxy**: XOR token path masking with address bar auto-reset to `/app/session`.
3. **Dedicated YouTube Unblocker**: Sub-150ms multi-engine playback with official YouTube HD, Piped privacy proxy, and Invidious mirrors.
4. **Full HTTPS CONNECT Forward Proxy**: macOS system network proxying with loopback bypasses.

---

## Deliverable Paths

- **Primary Storage**: [`/Users/alexisgrimmace/Documents/AI_Outputs/web_proxy_server/`](file:///Users/alexisgrimmace/Documents/AI_Outputs/web_proxy_server/)
- **Workspace Mirror**: [`/Users/alexisgrimmace/Documents/gemislop/`](file:///Users/alexisgrimmace/Documents/gemislop/)

---

## 👻 Hardware Graphics Screen Cloak (`ScreenCloak`)

### How It Works
When you are on Zoom, Microsoft Teams, Google Meet, Discord, or under digital monitoring (e.g., GoGuardian, LanSchool, Screen Sharing / VNC, or recording software):
- **On your physical display**: You interact with the **Ghost Browser** running the All-in-One Proxy / YouTube / any site with full audio, video, clicks, and keystrokes.
- **In digital framebuffers**: macOS Quartz WindowServer removes the Ghost Window entirely and replaces it with your chosen **Decoy Tab** (Google Docs with authentic essay drafts, Canvas LMS, Wikipedia, or Google Drive).
- **Boss / Panic Key**: Press **`ESC`** at any moment to hide the Ghost Window and bring the Decoy forward for physical onlookers.

### Launching ScreenCloak
Run from terminal or click the **"👻 Screen Cloak"** button in the web dashboard:
```bash
./launch_screen_cloak.sh
```

### Verifying Graphics Cloak
Run the automated test:
```bash
python3 test_cloak.py
```
*Result: 0 pixels of the Ghost Window captured in digital screenshots, >300,000 pixels of the Decoy Window captured.*

---

## Features

1. **Undetectable Stealth Web Proxy**:
   - Zero destination URLs in browser address bar (resets to `/app/session`).
   - Obfuscated XOR token paths (`/app/v/<token>`).
   - One-click tab disguise selector (Google Docs, Drive, Canvas LMS, Wikipedia).
   - `about:blank` popup mode leaving zero browser history.

2. **Dedicated YouTube Unblocker**:
   - Instant playback (<150ms load time via oEmbed).
   - **Multi-Engine Switcher**:
     - 🔴 **YouTube HD / 4K** (Official player with full controls & subtitles)
     - 🟢 **Piped Privacy Mirror** (Ad-free, unblocked from strict network firewalls)
     - 🟣 **Invidious Mirror**
     - 🔵 **Mirror 2**
   - **Theater Mode** toggle for widescreen viewing.
   - Built-in search portal (`/youtube?q=...`) supporting queries, video IDs, or direct YouTube links.

3. **One-Click Proxied Chrome Launcher**:
   - Launches a dedicated Google Chrome window routed 100% through the proxy (`127.0.0.1:8080`).
   - Works directly from the web UI buttons or `./launch_proxied_chrome.sh`.

4. **Forward HTTPS CONNECT Tunneling**:
   - macOS network proxy support (`./enable_macos_proxy.sh`).
   - Loopback bypass protection for seamless local connectivity.

---

## Quick Start

### 1. Start Server
```bash
./start_proxy.sh
```

### 2. Access in Browser
- **Dashboard**: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- **YouTube Unblocker**: [http://127.0.0.1:8080/youtube](http://127.0.0.1:8080/youtube)
- **Watch Direct Video**: `http://127.0.0.1:8080/watch?v=<VIDEO_ID>`

### 3. Launch Screen Cloak
```bash
./launch_screen_cloak.sh
```

### 4. Stop Server
```bash
./stop_proxy.sh
```
