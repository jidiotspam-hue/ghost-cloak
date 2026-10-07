# All-in-One Stealth Suite: Proxy, YouTube Unblocker & Screen Cloak

A unified unblocking and surveillance defense system supporting both **native macOS hardware display cloaking** and **100% standalone execution on school Chromebooks**.

---

## 🌐 Live Web App (Chromebook & Any Device)

- **Live GitHub Pages URL**: 👉 **[https://jidiotspam-hue.github.io/ghost-cloak/](https://jidiotspam-hue.github.io/ghost-cloak/)**
- **GitHub Repository**: [`https://github.com/jidiotspam-hue/ghost-cloak`](https://github.com/jidiotspam-hue/ghost-cloak)

---

## Deliverable Paths

- **Primary Storage**: [`/Users/alexisgrimmace/Documents/AI_Outputs/web_proxy_server/`](file:///Users/alexisgrimmace/Documents/AI_Outputs/web_proxy_server/)
- **Workspace Mirror**: [`/Users/alexisgrimmace/Documents/gemislop/`](file:///Users/alexisgrimmace/Documents/gemislop/)

---

## 💻 Chromebook Specific Features

School Chromebooks typically have strict administration policies: no Linux container (Crostini disabled), no terminal access, no third-party extensions, and aggressive surveillance extensions (GoGuardian, Securly, Lightspeed, LanSchool).

GhostCloak addresses all of these limitations purely in client-side web technologies:

1. **Zero Admin Rights / Zero Installation**:
   - Runs directly in Google Chrome on any Chromebook.
   - Requires zero extensions, zero flags, and zero developer mode.

2. **Active Surveillance Radar, Sensitivity Tuning & Debouncing**:
   - **Real-Time Inspection Alert**: Continuously monitors tab focus state (`window.onblur`), visibility changes (`document.hidden`), compositor/frame micro-stutter spikes (caused by WebRTC screen recording or rapid desktop thumbnail generation), and untrusted automation clicks (`e.isTrusted === false`).
   - **Multi-Level Radar Sensitivity Mode**:
     - ⚖️ **Balanced (Default)**: Optimized for typical classroom use with standard debouncing and 260ms jitter threshold.
     - ⚡ **High Sensitivity**: Instant alerts with reduced debouncing (600ms) and tight 200ms frame threshold for strict proctor environments.
     - 🛡️ **Relaxed / Low False Alarms**: Features dynamic user-gesture suppression (suppresses accidental focus flaps when clicking UI dropdowns or inputs) and 380ms frame jitter threshold.
   - **Surveillance Debouncing Engine**: Automatically suppresses duplicate hook flaps for the exact same event within a configurable window, preventing alert flutter.
   - **Visual Pulse & Floating Alert**: Features a live telemetry banner (`🟢 Surveillance Radar: Screen Private` → `🚨 ACTIVE SURVEILLANCE ALERT: MONITORING DETECTED!`) with exact trigger timestamps.
   - **Acoustic Warning Chime**: Synthesizes a discrete high-frequency double-tone (`880Hz → 660Hz`) via Web Audio API right into the user's earbuds to alert them immediately if the screen is inspected while looking away.
   - **Auto-Engage Decoy on Alert**: Instantly flips to the Google Docs essay the millisecond an inspection hook is flagged.
   - **Emergency Blackout Mode**: Press `Alt + K` or click **"⬛ Emergency Blackout"** to immediately display a pure black asleep screen.
   - **Real-Time Surveillance Telemetry Audit Log**: Tracks, logs, and displays every remote blur, visibility loss, or compositor jitter event with exact time of detection and defense action taken.

3. **Dynamic Self-Masking Engine (Automated Multi-Course Camouflage)**:
   - Continuously rotates the tab's visible identity across genuine academic coursework on a 45-second timer:
     - 🧬 *AP Biology: Mitochondrial ATP Synthesis*
     - 🎓 *Canvas LMS: Assignment Modules*
     - 📐 *AP Calculus BC: Problem Set 4*
     - ⚡ *Khan Academy: Cellular Energy Unit*
     - 📘 *Quizlet: Cellular Respiration Study Set*
   - Dynamically swaps `<title>`, authentic favicon icons, and address bar query strings (`history.replaceState`) to ensure browser history, tab lists, and over-the-shoulder teacher glances always see active academic work.

4. **Stealth Arcade & Logic Study Breaks (Offline Pure JS)**:
   - Embedded offline logic games designed for discreet study breaks during long sessions:
     - 🔢 **2048: Powers of 2 Math Logic**: Full 4x4 tile merging math game with persistent best score tracking. Playable with Arrow keys or `WASD`.
     - 🐍 **Cellular Respiration Snake**: Interactive cell biology themed snake game where the organelle matrix consumes mitochondrial ATP nutrients (`38bdf8`) on an HTML5 canvas.
   - **Dual-Surface Execution**: Playable both in the main workspace and inside a dedicated **Computational Thinking / Bioenergetics Logic Lab** decoy template screen.

5. **Multi-Theme Workspace Styling Engine**:
   - Switch seamlessly between 6 distinct visual workspace themes via the header selector:
     - 🌙 **Midnight Dark** (Default)
     - ⚡ **Neon Cyan** (High-contrast blue/cyan cyberpunk palette)
     - 🌲 **Emerald Focus** (Muted deep green eye-comfort theme)
     - 📜 **Warm Academic** (Classic sepia-toned parchment paper aesthetic)
     - 🌆 **Synthwave Sunset** (Vibrant 80s neon purple & pink retro aesthetic)
     - ⬛ **Pure OLED Stealth** (True `#000000` absolute black for zero backlight bleed)
   - Preferences automatically persist to local storage.

6. **Pomodoro Focus Study Timer**:
   - Integrated study cycle clock (25-minute Deep Focus + 5-minute Rest interval).
   - Embedded both in the top header and inside the Google Docs decoy toolbar (`⏱️ 25:00`).
   - Plays a gentle acoustic alert blip when switching between focus and rest periods.

7. **In-Decoy Draggable "Ghost PiP" Floating Player**:
   - Floating video player that operates **directly inside the Google Docs decoy screen**.
   - **Draggable & Resizable**: Drag from the header bar across the document on Chromebook touchscreen or mouse.
   - **Stealth Opacity Slider**: Adjust transparency from 20% to 100% so text on the document shows through.
   - **Quick Toggle**: Dedicated toolbar button or hotkey `Ctrl + Shift + P`.

8. **Study Focus Sound Studio (Web Audio Procedural Synthesis)**:
   - 100% offline procedural ambient audio generator built with the Web Audio API — zero network downloads or external audio files.
   - **🌧️ Gentle Rain**: Filtered white noise stream simulating raindrops.
   - **🌊 Ocean Tides**: Low-pass filtered noise modulated by a 0.12Hz Low-Frequency Oscillator (LFO) creating rhythmic rolling surf waves.
   - **🧠 40Hz Gamma Focus (Binaural Beats)**: Left ear (200Hz) and right ear (240Hz) tone synthesis generating a 40Hz gamma entrainment frequency for deep study concentration.
   - **☕ Cafe Study Ambience**: Warm integrated brown noise passed through dynamic bandpass filters with slow dual-LFO drift simulating coffeehouse room tone.
   - **Panic Mute Protection**: Instantly suspends Web Audio context when panic mode triggers so ambient sounds go completely silent during decoy inspection, resuming seamlessly when restored.
   - **Master & Track Volume**: Individual slider controls plus an animated real-time oscilloscope wave canvas.

9. **In-App Study Notes & Citation Scratchpad**:
   - Built-in scratchpad for jotting lecture notes, timestamps, and bibliography citations.
   - Auto-saves to `localStorage`.
   - **💾 Export .MD**: One-click download as structured Markdown.
   - **📄 Export .TXT**: One-click download as plain text.
   - **📋 Copy Citation**: Automatically formats notes into academic BibTeX citations.
   - **📄 Send to Google Doc**: Appends notes directly into the active Google Docs decoy essay.

10. **Multi-Template School Decoys & Full Interactivity**:
    - 📄 **Google Docs with Multi-Subject Switcher**: Switch between 4 complete academic documents on the fly:
      - 🧬 *AP Biology: Cellular Respiration & ATP Synthesis*
      - 🏛️ *AP US History: Progressive Era & Labor Reform*
      - 📖 *English Literature: Thematic Duality in Hamlet*
      - ⚗️ *Chemistry: Equilibrium & Le Chatelier's Principle*
      Includes rich toolbar (bold, italic, align), word & character counter, and secret uncloak click on `"☁️ Saved to Drive"`.
    - 🎓 **Interactive Canvas LMS**: Tabbed interface featuring Dashboard, Courses, Grades (with GPA calculator), Calendar (homework timeline), and interactive To-Do checkboxes.
    - 🏫 **Interactive Google Classroom**: Stream, Classwork, and People views with clickable "Turn In" buttons and submission confirmations.
    - 📐 **Dynamic Desmos Graphing Calculator**: Mathematical function plotter with equation toggles, expression input (`+ Add Expression`), Zoom In/Out, reset controls, and real-time trigonometric/polynomial curve rendering.
    - 📖 **Authentic Wikipedia Decoy**: Encyclopedic layout complete with article search, infobox, table of contents, and scholarly references.

11. **Academic Media Player Controls**:
    - **Playback Speed Selector**: Choose `0.75x`, `1.0x`, `1.25x`, `1.5x`, or `2.0x`.
    - **Mini PiP Popout**: Spawn a clean 480×270 floating popout window.
    - **Theater Mode**: One-click distraction-free cinema player.

12. **Client-Side Web Gateway & Sandbox Hub**:
    - Embedded inline iframe browser sandbox with popout and close controls.
    - Quick pre-configured shortcuts for Hacker News, Wikipedia, Lichess, and IP Info.
    - Full `about:blank` history-cloaked popout mode.

13. **Security, Sensors & Cloaking**:
    - **Configurable Panic Key**: Choose between `ESC / ~` (Default), `Ctrl + B`, or `Ctrl + Q`.
    - **Hardened Anti-Force Close Guard (`beforeunload` + User Gesture Arming)**: Intercepts accidental tab closure and extension remote tab-close signals with an authentic academic confirmation modal (`"Warning: Active academic assignment in progress. Closing this tab will lose unsaved research data."`).
    - **Session Resurrection Engine**: Continuously snapshots active video ID, playback position, scratchpad notes, and active decoy to local storage every 3 seconds. If a tab is forcibly closed, a one-click **"⚡ Session Restored"** banner appears upon next load to immediately resume playback.
    - **Address Bar Cloaking (HTML5 History API)**: Dynamically disguises the visible URL in the Chrome address bar using `history.replaceState` (e.g. `?doc=ap_biology_mitochondrial_atp_synthesis&id=1BxiMVs...`). Extension tab queries and teacher glances see an authentic assignment document link.
    - **Surveillance Sensors**: Auto-cloak on tab blur, cursor exit, and window visibility change.
    - **Secret Uncloak Click**: Clicking `"☁️ Saved to Drive"`, the Canvas `"C"` logo, or the Wikipedia `"📖"` icon quietly unlocks the hub without touching the keyboard.

14. **`about:blank` Cloaking**:
    - Spawns the entire unblocker inside an `about:blank` window.
    - GoGuardian, Securly, Lightspeed, and ChromeOS URL filters **cannot block `about:blank`** because there is no domain name.
    - Leaves **zero history** in `chrome://history`.

15. **Lightspeed Systems Stealth Optimizations**:
    - **Title Scanner Immunity**: Default tab title is `Document - Google Docs` with real Google Docs favicon. Zero filter trigger keywords ("unblocker", "stealth", "proxy") in DOM or metadata.
    - **Outgoing Request Camouflage (Proxy & Backend)**: Local proxy and API requests are cloaked with academic Referer headers (`https://docs.google.com/document/u/0/...`) and Origin (`https://docs.google.com`), disguising outbound traffic from network packet inspectors and district logs.
    - **NoCookie Domain Whitelisting**: Defaults to `https://www.youtube-nocookie.com/embed/`, the exact domain whitelisted by Lightspeed for Canvas and Google Classroom embeds.
    - **Classroom Live Thumbnail Grabber Camouflage**: Integrates a synchronized video lecture citation (`Figure 3.1: Video Lecture &bull; Bioenergetics Reference`) directly inside the Google Docs essay. When teacher grid thumbnails capture student screens, the video appears as authentic coursework.
    - **Discreet Offline File (`Biology_Lab_Notes.html`)**: Downloads as `Biology_Lab_Notes.html` so Chromebook `Downloads` folder inspections see an ordinary biology lab file. Runs directly from `file:///`.

16. **Multi-Tier Rotating School Wi-Fi Mirrors & Backend Synergy**:
    - Multi-tier search fallback pipeline:
      1. Local backend API search (`127.0.0.1:8080/api/search`) via Python `yt-dlp` engine.
      2. Public Piped private mirror.
      3. Invidious secondary mirror.
      4. Yewtube tertiary mirror.
    - **Direct MP4 Stream Extraction (`/api/stream?v=...`)**:
      - Extracts direct CDN video stream URLs via `yt-dlp`.
      - Playable directly in native HTML5 `<video controls autoplay>` player, bypassing iframe sandbox restrictions.
    - **Real-Time Telemetry & Stats API (`/api/stats`)**:
      - Returns uptime, total requests handled, active connections, and recent activity logs.
    - Complete CORS preflight (`OPTIONS`) support across all backend endpoints.

---

## 🛡️ Full Threat Model: Every Way Lightspeed Sees Your Screen & The Patches

| # | Lightspeed Surveillance Vector | How Lightspeed Works | GhostCloak Patch & Neutralization |
| :--- | :--- | :--- | :--- |
| **1** | **Live Thumbnail Grid** (`chrome.tabs.captureVisibleTab`) | Extension captures 10-second periodic screenshots of the active browser viewport for teacher dashboard tiles. | **Dedicated Ghost Tab Boot (`#ghost` / `ghost.html`)**: Boots directly into Google Docs Decoy on frame 1. The thumbnail always captures authentic AP Biology coursework, real toolbars, word counts, and academic citations. |
| **2** | **Open Tabs Inspection** (`chrome.tabs.query`) | Teacher clicks a student's card to list all open tabs (titles, URLs, favicons). Flagged domains or "YouTube" titles trigger automatic off-task alerts. | **Single-Tab Architecture + Tab Masking**: Entire suite runs within a single tab. `<title>` is dynamically cloaked to `Document - Google Docs` with authentic Google Docs favicon. Zero secondary tabs exist for the extension to list. |
| **3** | **Browsing History & URL Logs** (`chrome.webNavigation`) | Logs visited domains and search query URLs to district servers. | **`about:blank` Execution**: Launches into an `about:blank` window. Lightspeed cannot block or log `about:blank` because it has no domain and writes zero history to `chrome://history`. |
| **4** | **Full-Screen Live Stream** (`chrome.desktopCapture` / WebRTC) | Teacher clicks to watch 30fps real-time screen stream when suspicious. | **Ghost Peek (`Shift + ~` / `👁️ Ghost Peek`)**: Lets the student view their media underneath at adjustable opacity while the solid Google Doc remains dominant. The millisecond the window blurs or proctor acts, it snaps to 100% solid opacity instantly. |
| **5** | **Audio Leakage** | Teacher walks down the hallway or aisle and hears music or video audio. | **Panic Mute Protection**: `togglePanicMode()` suspends `AudioContext` at the driver level and mutes video iframes in 0ms. Zero sound escapes even with headphones removed. |
| **6** | **Remote Tab Close / Screen Lock** | Teacher pushes a lock screen or forcibly closes the student's tab. | **`beforeunload` Protection & Auto-Decoy**: Intercepts unprompted close events. Remote focus shifts immediately trigger the audible chime and auto-engage the decoy overlay. |
| **7** | **Desktop Sharing (macOS)** | Zoom, Microsoft Teams, Google Meet screen sharing. | **Hardware Window Cloaking (`ScreenCloak.swift`)**: Uses macOS WindowServer `NSWindow.sharingType = .none` to physically remove the window from the display compositor. |
| **8** | **Chromebook Real-Time Frame Capture** (`chrome.desktopCapture` on ChromeOS) | Live 30fps screen stream viewing where native Swift/Cocoa WindowServer APIs cannot run. | **Audio-Only Stealth Diagram Mode**: Completely decouples audio playback from screen rendering. Reduces video viewport to zero pixels and replaces screen with high-fidelity AP Biology Chemiosmosis Diagram (`Figure 4.3`). Observer sees 100% academic biology content. |
| **9** | **Network Perimeter Deep Packet Inspection & DNS Sinkholing** | District firewalls (Palo Alto, Fortinet) block YouTube IP ranges and poison local DNS. Localhost proxy egress is dropped. | **Serverless Cloudflare Relay (`worker.js`) & Encrypted DoH**: Intercepts and tunnels egress through Cloudflare edge network (`cloudflare-dns.com` + `worker.js`), stripping origin headers and bypassing local gateway DNS/IP filters. |

---

## 🔬 Architectural Defense Analysis & Mitigation Guide

### 1. Chromebook Live Remote Screen Viewing
* **Limitation Addressed**: `ScreenCloak.swift` relies on macOS Cocoa APIs (`NSWindow.sharingType = .none`). ChromeOS does not permit unprivileged web pages to exclude windows from OS compositing.
* **Mitigation**: **Zero-Video Audio Stealth Mode (`toggleAudioOnlyMode`)**. On Chromebooks, media playback is rendered as an audio stream while replacing the entire visible canvas with an authentic, interactive academic diagram (`Figure 4.3: Chemiosmosis & ATP Synthase`). Live screen viewing captures legitimate coursework with zero media artifacts.

### 2. Perimeter Firewall & Deep Packet Inspection (DPI)
* **Limitation Addressed**: Running a local proxy on `127.0.0.1:8080` does not change egress network routing. School routers filter YouTube IPs and block unencrypted DNS lookups.
* **Mitigation**:
  1. **Serverless Cloudflare Worker Relay (`worker.js`)**: Deployable to Cloudflare's free edge network (`*.workers.dev`), serving as an encrypted off-network relay that handles upstream media requests and strips headers.
  2. **Encrypted DNS-over-HTTPS (DoH)**: Built-in fallback resolving upstream hosts via `https://cloudflare-dns.com/dns-query` directly in `server.py`.
  3. **Upstream Proxy Chaining**: `python3 server.py --upstream-proxy http://user:pass@remote-proxy:port` routes all egress traffic through external tunnels.

### 3. Managed Chromebook Policy Locks
* **Limitation Addressed**: District administrative settings block developer mode, downloading shell scripts, and third-party Chrome extensions.
* **Mitigation**: GhostCloak operates purely in standards-compliant HTML5/Web Audio/Canvas running client-side on GitHub Pages or from an offline `Biology_Lab_Notes.html` file. Requires zero downloads, extensions, or administrative permissions.

---

## 👻 macOS Hardware Graphics Screen Cloak (`ScreenCloak`)

For macOS users, a native Swift utility utilizing `NSWindow.sharingType = .none` removes the real browser window from digital framebuffers (Zoom, Teams, Discord, Screen Sharing, Screen Recorders) while projecting the Decoy layer beneath it.

- Launch: `./launch_screen_cloak.sh`
- Verify: `python3 test_cloak.py`

---

## Quick Start (Local macOS Proxy Server)

```bash
# Start local proxy server with optional upstream proxy
python3 server.py 8080 --upstream-proxy http://remote-proxy:8080

# Or start with shell script
./start_proxy.sh

# Open local dashboard
open http://127.0.0.1:8080/

# Stop local proxy server
./stop_proxy.sh
```
