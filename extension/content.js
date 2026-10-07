/**
 * GhostCloak Content Neutralizer Script
 * Injected at document_start in all frames.
 * Disarms surveillance DOM inspection, protects focus state, and intercepts forced closures.
 */

(function() {
  'use strict';

  // 1. NEUTRALIZE VISIBILITY API SURVEILLANCE
  // Proctor scripts query document.hidden and document.visibilityState to catch tab switches.
  try {
    Object.defineProperty(document, 'hidden', {
      get: function() { return false; },
      configurable: true
    });
    Object.defineProperty(document, 'visibilityState', {
      get: function() { return 'visible'; },
      configurable: true
    });
    Object.defineProperty(document, 'webkitVisibilityState', {
      get: function() { return 'visible'; },
      configurable: true
    });
  } catch (e) {}

  // 2. SPOOF ACTIVE WINDOW FOCUS
  // Proctors rely on window.onblur and document.hasFocus() to flag off-task behavior.
  try {
    document.hasFocus = function() { return true; };
    window.onblur = null;
  } catch (e) {}

  // Intercept and swallow blur events fired at the window or document
  window.addEventListener('blur', function(e) {
    if (!e.isTrusted || window.__allowBlurInspection !== true) {
      // Prevent surveillance listeners from getting notified
      e.stopImmediatePropagation();
    }
  }, true);

  // 3. HARDEN AGAINST REMOTE FORCED CLOSING & TAB DISMISSAL
  window.addEventListener('beforeunload', function(e) {
    // If the page contains an active GhostCloak session or student doc, trigger defense
    e.preventDefault();
    e.returnValue = "Warning: Active academic assignment in progress. Closing this tab will lose unsaved research data.";
    return e.returnValue;
  }, true);

  // 4. PREVENT SYNTHETIC EVENT INJECTION FROM EXTENSIONS
  ['click', 'mousedown', 'keydown', 'keypress'].forEach(function(evtName) {
    window.addEventListener(evtName, function(e) {
      if (e.isTrusted === false) {
        // Synthetic automation dispatched by an external content script
        e.stopImmediatePropagation();
        e.preventDefault();
      }
    }, true);
  });

  // 5. INTERCEPT WEBRTC SCREEN STREAMING OFFERS IF DESIRED
  if (window.RTCPeerConnection) {
    const originalCreateOffer = window.RTCPeerConnection.prototype.createOffer;
    window.RTCPeerConnection.prototype.createOffer = function() {
      // Check if user has opted into blocking WebRTC screen grab streams
      return originalCreateOffer.apply(this, arguments);
    };
  }

  // 6. IN-PAGE DECOY BRIDGE
  // Exposes a secret window.__ghostNeutralizerActive flag so index.html knows the extension is armed.
  window.__ghostNeutralizerActive = true;
})();
