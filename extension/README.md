# Docs Workspace & Academic Sync Assistant (Chrome Extension)

A lightweight Manifest V3 Chrome Extension providing deep client-side privacy, surveillance telemetry neutralization, and forced-close prevention on managed ChromeOS and Chrome browsers.

---

## 🚀 How to Install on Chromebook or Chrome

1. Open Google Chrome and navigate to:
   ```
   chrome://extensions/
   ```
2. In the top-right corner, enable **Developer mode** toggle.
3. Click **"Load unpacked"**.
4. Select the `extension/` folder from this repository.
5. The extension will activate immediately disguised as **"Docs Workspace & Academic Sync Assistant"**.

---

## 🛡️ Active Countermeasures & Neutralization

1. **Visibility API Spoofing (`content.js`)**:
   - Overrides `document.hidden` to permanently return `false`.
   - Overrides `document.visibilityState` to permanently return `'visible'`.
   - Neutralizes teacher surveillance scripts that check if you switch away from an assignment or test.

2. **Window Focus Lock (`document.hasFocus()`)**:
   - Spoofs `document.hasFocus()` to return `true`.
   - Intercepts and blocks synthetic `window.blur` events from being reported to extension listeners.

3. **Anti-Force Close Guard (`beforeunload`)**:
   - Injects a top-priority `beforeunload` event handler that blocks unprompted remote tab closures.
   - Prevents proctor software from silently killing the tab.

4. **Declarative Network Telemetry Blocker (`rules.json`)**:
   - Blocks outbound network requests to known surveillance domains:
     - `lightspeedsystems.com/api/screen*`
     - `relay.school/telemetry*`
     - `goguardian.com/api/stream*`
     - `securly.com/stream*`
   - Dynamically injects academic headers (`Referer: https://docs.google.com/document/u/0/`) onto all cross-origin requests.

5. **Synthetic Automation Defense**:
   - Discards non-trusted input events (`e.isTrusted === false`) injected by third-party extension scripts.
