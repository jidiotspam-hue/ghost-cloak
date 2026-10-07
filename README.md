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

2. **Active Surveillance Radar & Real-Time Monitoring Alert**:
   - **Real-Time Inspection Alert**: Continuously monitors tab focus state (`window.onblur`), visibility changes (`document.hidden`), compositor/frame micro-stutter spikes (caused by WebRTC screen recording or rapid desktop thumbnail generation), and untrusted automation clicks.
   - **Visual Pulse & Floating Alert**: Features a live telemetry banner (`🟢 Surveillance Radar: Screen Private` → `🚨 ACTIVE SURVEILLANCE ALERT: MONITORING DETECTED!`) with exact trigger timestamps.
   - **Acoustic Warning Chime**: Synthesizes a discrete high-frequency double-tone (`880Hz → 660Hz`) via Web Audio API right into the user's earbuds to alert them immediately if the screen is inspected while looking away.
   - **Auto-Engage Decoy on Alert**: Instantly flips to the Google Docs essay the millisecond an inspection hook is flagged.
   - **Emergency Blackout Mode**: Press `Alt + K` or click **"⬛ Emergency Blackout"** to immediately display a pure black asleep screen.
   - **Real-Time Surveillance Telemetry Audit Log**: Tracks, logs, and displays every remote blur, visibility loss, or compositor jitter event with exact time of detection and defense action taken.

3. **Multi-Theme Workspace Styling Engine**:
   - Switch seamlessly between 6 distinct visual workspace themes via the header selector:
     - 🌙 **Midnight Dark** (Default)
     - ⚡ **Neon Cyan** (High-contrast blue/cyan cyberpunk palette)
     - 🌲 **Emerald Focus** (Muted deep green eye-comfort theme)
     - 📜 **Warm Academic** (Classic sepia-toned parchment paper aesthetic)
     - 🌆 **Synthwave Sunset** (Vibrant 80s neon purple & pink retro aesthetic)
     - ⬛ **Pure OLED Stealth** (True `#000000` absolute black for zero backlight bleed)
   - Preferences automatically persist to local storage.

4. **Pomodoro Focus Study Timer**:
   - Integrated study cycle clock (25-minute Deep Focus + 5-minute Rest interval).
   - Embedded both in the top header and inside the Google Docs decoy toolbar (`⏱️ 25:00`).
   - Plays a gentle acoustic alert blip when switching between focus and rest periods.

5. **In-Decoy Draggable "Ghost PiP" Floating Player**:
   - Floating video player that operates **directly inside the Google Docs decoy screen**.
   - **Draggable & Resizable**: Drag from the header bar across the document on Chromebook touchscreen or mouse.
   - **Stealth Opacity Slider**: Adjust transparency from 20% to 100% so text on the document shows through.
   - **Quick Toggle**: Dedicated toolbar button or hotkey `Ctrl + Shift + P`.

6. **Study Focus Sound Studio (Web Audio Procedural Synthesis)**:
   - 100% offline procedural ambient audio generator built with the Web Audio API — zero network downloads or external audio files.
   - **🌧️ Gentle Rain**: Filtered white noise stream simulating raindrops.
   - **🌊 Ocean Tides**: Low-pass filtered noise modulated by a 0.12Hz Low-Frequency Oscillator (LFO) creating rhythmic rolling surf waves.
   - **🧠 40Hz Gamma Focus (Binaural Beats)**: Left ear (200Hz) and right ear (240Hz) tone synthesis generating a 40Hz gamma entrainment frequency for deep study concentration.
   - **☕ Cafe Study Ambience**: Warm integrated brown noise passed through dynamic bandpass filters with slow dual-LFO drift simulating coffeehouse room tone.
   - **Panic Mute Protection**: Instantly suspends Web Audio context when panic mode triggers so ambient sounds go completely silent during decoy inspection, resuming seamlessly when restored.
   - **Master & Track Volume**: Individual slider controls plus an animated real-time oscilloscope wave canvas.

7. **In-App Study Notes & Citation Scratchpad**:
   - Built-in scratchpad for jotting lecture notes, timestamps, and bibliography citations.
   - Auto-saves to `localStorage`.
   - **💾 Export .MD**: One-click download as structured Markdown.
   - **📄 Export .TXT**: One-click download as plain text.
   - **📋 Copy Citation**: Automatically formats notes into academic BibTeX citations.
   - **📄 Send to Google Doc**: Appends notes directly into the active Google Docs decoy essay.

8. **Multi-Template School Decoys & Full Interactivity**:
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

9. **Academic Media Player Controls**:
   - **Playback Speed Selector**: Choose `0.75x`, `1.0x`, `1.25x`, `1.5x`, or `2.0x`.
   - **Mini PiP Popout**: Spawn a clean 480×270 floating popout window.
   - **Theater Mode**: One-click distraction-free cinema player.

10. **Client-Side Web Gateway & Sandbox Hub**:
    - Embedded inline iframe browser sandbox with popout and close controls.
    - Quick pre-configured shortcuts for Hacker News, Wikipedia, Lichess, and IP Info.
    - Full `about:blank` history-cloaked popout mode.

11. **Security, Sensors & Cloaking**:
    - **Configurable Panic Key**: Choose between `ESC / ~` (Default), `Ctrl + B`, or `Ctrl + Q`.
    - **Force-Close Prevention (`onbeforeunload`)**: Optional prompt before leaving to block monitoring tools or accidental tab closure.
    - **Surveillance Sensors**: Auto-cloak on tab blur, cursor exit, and window visibility change.
    - **Secret Uncloak Click**: Clicking `"☁️ Saved to Drive"`, the Canvas `"C"` logo, or the Wikipedia `"📖"` icon quietly unlocks the hub without touching the keyboard.

12. **`about:blank` Cloaking**:
    - Spawns the entire unblocker inside an `about:blank` window.
    - GoGuardian, Securly, Lightspeed, and ChromeOS URL filters **cannot block `about:blank`** because there is no domain name.
    - Leaves **zero history** in `chrome://history`.

13. **Lightspeed Systems Stealth Optimizations**:
    - **Title Scanner Immunity**: Default tab title is `Document - Google Docs` with real Google Docs favicon. Zero filter trigger keywords ("unblocker", "stealth", "proxy") in DOM or metadata.
    - **NoCookie Domain Whitelisting**: Defaults to `https://www.youtube-nocookie.com/embed/`, the exact domain whitelisted by Lightspeed for Canvas and Google Classroom embeds.
    - **Classroom Live Thumbnail Grabber Camouflage**: Integrates a synchronized video lecture citation (`Figure 3.1: Video Lecture &bull; Bioenergetics Reference`) directly inside the Google Docs essay. When teacher grid thumbnails capture student screens, the video appears as authentic coursework.
    - **Discreet Offline File (`Biology_Lab_Notes.html`)**: Downloads as `Biology_Lab_Notes.html` so Chromebook `Downloads` folder inspections see an ordinary biology lab file. Runs directly from `file:///`.

14. **Multi-Tier Rotating School Wi-Fi Mirrors & Backend Synergy**:
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

## 👻 macOS Hardware Graphics Screen Cloak (`ScreenCloak`)

For macOS users, a native Swift utility utilizing `NSWindow.sharingType = .none` removes the real browser window from digital framebuffers (Zoom, Teams, Discord, Screen Sharing, Screen Recorders) while projecting the Decoy layer beneath it.

- Launch: `./launch_screen_cloak.sh`
- Verify: `python3 test_cloak.py`

---

## Quick Start (Local macOS Proxy Server)

```bash
# Start local proxy server
./start_proxy.sh

# Open local dashboard
open http://127.0.0.1:8080/

# Stop local proxy server
./stop_proxy.sh
```
