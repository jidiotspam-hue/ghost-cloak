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

2. **Surveillance Defense Sensors (Auto-Cloak)**:
   - **Auto-Cloak on Tab Blur**: When a teacher inspects the Chromebook or when you click another window, the tab automatically flips to an authentic Decoy.
   - **Auto-Cloak on Cursor Leave**: Automatically cloaks if your mouse exits the window.
   - **Auto-Cloak on Visibility Change**: Instantly hides when minimized or split-screened.

3. **Multi-Template School Decoys**:
   - 📄 **Google Docs**: Active essay on Cellular Respiration with editable text, live word counter, real Google Docs layout, toolbar, and formatting buttons.
   - 🎓 **Canvas LMS**: Full dashboard with course cards (AP Biology, Calculus BC, US History) and interactive To-Do assignment checkboxes.
   - 🏫 **Google Classroom**: Authentic Stream and Classwork cards with "Turned In" status.
   - 📐 **Desmos Graphing Calculator**: Interactive mathematical function plotter with coordinate axes, sine waves, and parabola curves.


4. **`about:blank` Cloaking**:
   - Spawns the entire unblocker inside an `about:blank` window.
   - GoGuardian, Securly, Lightspeed, and ChromeOS URL filters **cannot block `about:blank`** because there is no domain name.
   - Leaves **zero history** in `chrome://history`.

5. **Lightspeed Systems Stealth Optimizations**:
   - **Title Scanner Immunity**: Default tab title is `Document - Google Docs` with real Google Docs favicon. Zero filter trigger keywords ("unblocker", "stealth", "proxy") in DOM or metadata.
   - **NoCookie Domain Whitelisting**: Defaults to `https://www.youtube-nocookie.com/embed/`, the exact domain whitelisted by Lightspeed for Canvas and Google Classroom embeds.
   - **Classroom Live Thumbnail Grabber Camouflage**: Integrates a synchronized video lecture citation (`Figure 3.1: Video Lecture &bull; Bioenergetics Reference`) directly inside the Google Docs essay. When teacher grid thumbnails capture student screens, the video appears as authentic coursework.
   - **Discreet Offline File (`Biology_Lab_Notes.html`)**: Downloads as `Biology_Lab_Notes.html` so Chromebook `Downloads` folder inspections see an ordinary biology lab file. Runs directly from `file:///`.

6. **Rotating School Wi-Fi Mirrors**:
   - Built-in multi-mirror fallback (NoCookie, YouTube HD, Piped, Invidious Mirrors 1, 2, 3) ensuring uninterrupted streaming even if the school network filters common domains.

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
