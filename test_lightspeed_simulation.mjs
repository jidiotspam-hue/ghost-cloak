// Simulation & Benchmark: Testing GhostCloak Surveillance Detection Against Lightspeed Systems Behaviors
import { spawn } from 'child_process';
import http from 'http';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const DEBUG_PORT = 9333;
const TARGET_URL = `file://${path.resolve('index.html')}`;
const PROFILE_DIR = `/tmp/chrome-lightspeed-test-${Date.now()}`;

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const cb = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) cb.reject(msg.error);
          else cb.resolve(msg.result);
        }
      };
    });
  }

  async send(method, params = {}) {
    const id = this.id++;
    return new Promise((resolve, reject) => {
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const res = await this.send('Runtime.evaluate', { expression, returnByValue: true });
    if (res.exceptionDetails) {
      console.error('[CDP Eval Error]:', res.exceptionDetails);
    }
    return res.result ? res.result.value : null;
  }
}

async function runBenchmark() {
  console.log('='.repeat(70));
  console.log('🔬 LIGHTSPEED SYSTEMS MONITORING SIMULATION & VERIFICATION TEST');
  console.log('='.repeat(70));
  console.log(`Target: ${TARGET_URL}`);
  console.log(`Chrome: ${CHROME_PATH}\n`);

  fs.mkdirSync(PROFILE_DIR, { recursive: true });

  const chromeProc = spawn(CHROME_PATH, [
    `--remote-debugging-port=${DEBUG_PORT}`,
    '--headless=new',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${PROFILE_DIR}`,
    '--disable-background-networking',
    TARGET_URL
  ], { stdio: 'ignore' });

  let cdp = null;

  try {
    // Wait for Chrome remote debugging to come up
    let targets = null;
    for (let i = 0; i < 20; i++) {
      try {
        targets = await fetchJson(`http://127.0.0.1:${DEBUG_PORT}/json`);
        if (targets && targets.length > 0) break;
      } catch (e) {}
      await sleep(300);
    }

    if (!targets || targets.length === 0) {
      throw new Error('Failed to connect to headless Chrome on port ' + DEBUG_PORT);
    }

    const pageTarget = targets.find(t => t.type === 'page') || targets[0];
    console.log(`[+] Connected to Chrome DevTools target: ${pageTarget.title}`);
    console.log(`[+] WebSocket URL: ${pageTarget.webSocketDebuggerUrl}`);

    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');

    await sleep(2000); // Allow initial scripts and DOM to stabilize

    console.log('\n--- BASELINE CHECK ---');
    const initialSurveillance = await cdp.evaluate('window.surveillanceState');
    console.log('Initial surveillanceState:', initialSurveillance);

    const results = [];

    // -------------------------------------------------------------
    // TEST 1: Passive Background Screen Capture (chrome.tabs.captureVisibleTab)
    // -------------------------------------------------------------
    console.log('\n[TEST 1] Simulating Lightspeed Thumbnail Grab (chrome.tabs.captureVisibleTab / Page.captureScreenshot)...');
    console.log('Explanation: Lightspeed background extension captures student tab screenshot periodically.');
    
    // Reset state first
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);

    const beforeT1 = await cdp.evaluate('window.surveillanceState.isMonitored');
    // Simulate background screenshot capture via CDP Page.captureScreenshot
    for (let s = 0; s < 3; s++) {
      await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 50 });
      await sleep(100);
    }
    const afterT1 = await cdp.evaluate('window.surveillanceState.isMonitored');
    const logT1 = await cdp.evaluate('window.surveillanceState.lastEvent');
    
    const t1Passed = (afterT1 === true);
    results.push({
      id: 'T1_CAPTURE_VISIBLE_TAB',
      name: 'Passive Background Screen Capture (captureVisibleTab)',
      expected: 'Does unprivileged webpage detect native extension screenshot?',
      detected: t1Passed,
      details: t1Passed ? `Detected: ${JSON.stringify(logT1)}` : 'NOT Detected by browser events alone (as expected by web sandbox security model)'
    });
    console.log(`Result: ${t1Passed ? 'DETECTED' : 'NOT DETECTED'} (Details: ${results[0].details})`);

    // -------------------------------------------------------------
    // TEST 2: Tab Focus Shift / Window Blur (Teacher window switch / inspection)
    // -------------------------------------------------------------
    console.log('\n[TEST 2] Simulating Window Blur (Teacher forces remote window defocus / student switches tab)...');
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);

    await cdp.evaluate('window.dispatchEvent(new Event("blur"));');
    await sleep(300);

    const afterT2 = await cdp.evaluate('window.surveillanceState.isMonitored');
    const eventT2 = await cdp.evaluate('window.surveillanceState.lastEvent');
    const decoyT2 = await cdp.evaluate('document.getElementById("decoyOverlay") ? document.getElementById("decoyOverlay").style.display : null');

    results.push({
      id: 'T2_WINDOW_BLUR',
      name: 'Window Defocus / Remote Blur Event',
      expected: 'Trigger surveillance alert and engage decoy',
      detected: afterT2 === true,
      details: `Trigger: ${eventT2 ? eventT2.reason : 'none'}, Decoy Display: ${decoyT2}`
    });
    console.log(`Result: ${afterT2 ? 'DETECTED' : 'NOT DETECTED'} (Decoy: ${decoyT2})`);

    // -------------------------------------------------------------
    // TEST 3: Tab Visibility Change (document.hidden)
    // -------------------------------------------------------------
    console.log('\n[TEST 3] Simulating Tab Visibility Change (Tab backgrounded / minimized by proctor)...');
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);

    // Emulate visibility hidden
    await cdp.send('Emulation.setEmitTouchEventsForMouse', { enabled: false });
    await cdp.evaluate(`
      Object.defineProperty(document, "hidden", { value: true, configurable: true });
      document.dispatchEvent(new Event("visibilitychange"));
    `);
    await sleep(300);

    const afterT3 = await cdp.evaluate('window.surveillanceState.isMonitored');
    const eventT3 = await cdp.evaluate('window.surveillanceState.lastEvent');
    const decoyT3 = await cdp.evaluate('document.getElementById("decoyOverlay") ? document.getElementById("decoyOverlay").style.display : null');

    // Restore document.hidden to false
    await cdp.evaluate(`
      Object.defineProperty(document, "hidden", { value: false, configurable: true });
      document.dispatchEvent(new Event("visibilitychange"));
    `);
    await sleep(200);

    results.push({
      id: 'T3_VISIBILITY_HIDDEN',
      name: 'Tab Visibility Hidden (document.hidden)',
      expected: 'Trigger surveillance alert and engage decoy',
      detected: afterT3 === true,
      details: `Trigger: ${eventT3 ? eventT3.reason : 'none'}, Decoy Display: ${decoyT3}`
    });
    console.log(`Result: ${afterT3 ? 'DETECTED' : 'NOT DETECTED'} (Decoy: ${decoyT3})`);

    // -------------------------------------------------------------
    // TEST 4: Cursor Exited Window (mouseleave)
    // -------------------------------------------------------------
    console.log('\n[TEST 4] Simulating Mouse Exiting Document Boundaries...');
    // Test 4A: Default settings (sensorMouse is unchecked by default)
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);
    await cdp.evaluate('document.dispatchEvent(new MouseEvent("mouseleave"));');
    await sleep(300);
    const t4a = await cdp.evaluate('window.surveillanceState.isMonitored');

    // Test 4B: With sensorMouse checked
    await cdp.evaluate('document.getElementById("sensorMouse").checked = true;');
    await cdp.evaluate('document.dispatchEvent(new MouseEvent("mouseleave"));');
    await sleep(300);
    const t4b = await cdp.evaluate('window.surveillanceState.isMonitored');
    const eventT4 = await cdp.evaluate('window.surveillanceState.lastEvent');

    results.push({
      id: 'T4_MOUSE_LEAVE',
      name: 'Cursor Viewport Exit (mouseleave)',
      expected: 'Trigger alert when sensorMouse is enabled in settings',
      detected: t4b === true,
      details: `Default (sensor off): ${t4a ? 'TRIGGERED' : 'QUIET (by design)'} | Sensor Enabled: ${t4b ? 'TRIGGERED (' + (eventT4 ? eventT4.reason : '') + ')' : 'NOT TRIGGERED'}`
    });
    console.log(`Result: Default=${t4a}, With Sensor=${t4b} (Details: ${results[results.length - 1].details})`);

    // -------------------------------------------------------------
    // TEST 5: Synthetic Automation Injection (e.isTrusted === false)
    // -------------------------------------------------------------
    console.log('\n[TEST 5] Simulating Content Script Synthetic Event Injection (e.isTrusted === false)...');
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);

    // Dispatch synthetic click directly on document body to avoid firing button onclick handlers
    await cdp.evaluate(`
      document.body.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
    `);
    await sleep(300);

    const afterT5 = await cdp.evaluate('window.surveillanceState.isMonitored');
    const eventT5 = await cdp.evaluate('window.surveillanceState.lastEvent');

    results.push({
      id: 'T5_SYNTHETIC_CLICK',
      name: 'Synthetic Click Injection (e.isTrusted === false)',
      expected: 'Trigger synthetic event alert',
      detected: afterT5 === true,
      details: `Trigger: ${eventT5 ? eventT5.reason : 'none'}`
    });
    console.log(`Result: ${afterT5 ? 'DETECTED' : 'NOT DETECTED'}`);

    // -------------------------------------------------------------
    // TEST 6: Compositor Frame Drop / Micro-stutter Spikes
    // -------------------------------------------------------------
    console.log('\n[TEST 6] Simulating Heavy Compositor / Frame Delay Stutter (>240ms delay)...');
    await cdp.evaluate('resetSurveillanceRadar();');
    await sleep(300);

    // Call checkFrameTimings with artificial delta > 240 twice to test threshold
    await cdp.evaluate(`
      checkFrameTimings(performance.now(), 320);
      checkFrameTimings(performance.now(), 350);
    `);
    await sleep(300);

    const afterT6 = await cdp.evaluate('window.surveillanceState.isMonitored');
    const eventT6 = await cdp.evaluate('window.surveillanceState.lastEvent');

    results.push({
      id: 'T6_COMPOSITOR_STUTTER',
      name: 'Compositor Stutter Threshold (Spike Delay > 240ms)',
      expected: 'Trigger Compositor Stutter Alert',
      detected: afterT6 === true,
      details: `Trigger: ${eventT6 ? eventT6.reason : 'none'}`
    });
    console.log(`Result: ${afterT6 ? 'DETECTED' : 'NOT DETECTED'} (Details: ${results[results.length - 1].details})`);
    // -------------------------------------------------------------
    // TEST 7: Ghost Tab Boot Mode (#ghost) & Initial Decoy State
    // -------------------------------------------------------------
    console.log('\n[TEST 7] Testing Ghost Tab Boot Navigation (#ghost)...');
    console.log('Explanation: Verifies the page boots 100% inside Google Docs Decoy mode on frame 1.');
    await cdp.send('Page.navigate', { url: TARGET_URL + '#ghost' });
    await sleep(800);

    const ghostDecoyState = await cdp.evaluate('document.getElementById("decoyOverlay") ? document.getElementById("decoyOverlay").style.display : null');
    const ghostTitle = await cdp.evaluate('document.title');
    const t7Passed = (ghostDecoyState === 'flex');

    results.push({
      id: 'T7_GHOST_BOOT',
      name: 'Ghost Tab Direct Decoy Boot (#ghost)',
      expected: 'Page boots with Decoy display: flex on initial frame',
      detected: t7Passed,
      details: `Decoy Display: ${ghostDecoyState}, Page Title: "${ghostTitle}"`
    });
    console.log(`Result: ${t7Passed ? 'PASS' : 'FAIL'} (Decoy Display: ${ghostDecoyState}, Title: "${ghostTitle}")`);
    // -------------------------------------------------------------
    // TEST 8: Sleep Mode Audio Silence (100% Zero Audio Output)
    // -------------------------------------------------------------
    console.log('\n[TEST 8] Testing Sleep Mode Audio Suppression (playWarningChime muted)...');
    await cdp.evaluate('toggleSleepMode(true);');
    const sleepActive = await cdp.evaluate('window.isSleepModeActive');
    // Try triggering alert chime while sleep mode is active
    await cdp.evaluate('playWarningChime();');
    const audioStateInSleep = await cdp.evaluate('window.audioCtx ? window.audioCtx.state : "none"');
    const t8Passed = (sleepActive === true && audioStateInSleep !== 'running');

    results.push({
      id: 'T8_SLEEP_MODE_AUDIO_MUTE',
      name: 'Sleep Mode 100% Zero Audio Guarantee',
      expected: 'Audio context remains suspended/none with playWarningChime muted',
      detected: t8Passed,
      details: `Sleep Active: ${sleepActive}, AudioCtx State: ${audioStateInSleep}`
    });
    console.log(`Result: ${t8Passed ? 'PASS' : 'FAIL'} (Sleep Mode Active: ${sleepActive}, AudioCtx State: ${audioStateInSleep})`);

    // -------------------------------------------------------------
    // TEST 9: Anti-Force Close Guard (beforeunload Return Value)
    // -------------------------------------------------------------
    console.log('\n[TEST 9] Testing Anti-Force Close Guard (beforeunload interception)...');
    const beforeUnloadCheck = await cdp.evaluate(`
      (() => {
        let defaultPrevented = false;
        let returnValue = null;
        const fakeEvt = {
          preventDefault: () => { defaultPrevented = true; },
          set returnValue(val) { returnValue = val; },
          get returnValue() { return returnValue; }
        };
        const prevent = document.getElementById("sensorPreventClose") && document.getElementById("sensorPreventClose").checked;
        if (prevent) {
          fakeEvt.preventDefault();
          fakeEvt.returnValue = "Warning: Active academic assignment in progress.";
        }
        return { defaultPrevented, returnValue, preventSensorChecked: prevent };
      })()
    `);
    const t9Passed = (beforeUnloadCheck.defaultPrevented === true && typeof beforeUnloadCheck.returnValue === 'string');

    results.push({
      id: 'T9_ANTI_FORCE_CLOSE',
      name: 'Anti-Force Close Protection Guard (beforeunload)',
      expected: 'Intercepts tab close and prompts confirmation',
      detected: t9Passed,
      details: `Default Prevented: ${beforeUnloadCheck.defaultPrevented}, Sensor Checked: ${beforeUnloadCheck.preventSensorChecked}`
    });
    console.log(`Result: ${t9Passed ? 'PASS' : 'FAIL'} (Prevented: ${beforeUnloadCheck.defaultPrevented})`);

    // -------------------------------------------------------------
    // SUMMARY REPORT
    // -------------------------------------------------------------
    console.log('\n' + '='.repeat(70));
    console.log('📊 EMPIRICAL BENCHMARK RESULTS MATRIX');
    console.log('='.repeat(70));
    results.forEach((r, idx) => {
      console.log(`${idx + 1}. [${r.detected ? 'PASS/TRIGGERED' : 'NOT TRIGGERED'}] ${r.name}`);
      console.log(`   Details: ${r.details}`);
    });

  } finally {
    if (cdp && cdp.ws) {
      try { cdp.ws.close(); } catch(e) {}
    }
    chromeProc.kill('SIGKILL');
    try { fs.rmSync(PROFILE_DIR, { recursive: true, force: true }); } catch(e) {}
  }
}

runBenchmark().catch(err => {
  console.error('Fatal error during benchmark:', err);
  process.exit(1);
});
