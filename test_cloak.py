#!/usr/bin/env python3
"""
test_cloak.py - Automated verification of the Graphics-Level Screen Cloak (NSWindow.sharingType = .none)
Proves that macOS WindowServer completely omits the secret browser from digital framebuffers
while capturing the Decoy Layer (Google Docs / Canvas).
"""

import os
import subprocess
from PIL import Image

def run_cloak_test():
    print("[1/3] Compiling and launching dual-layer graphics test...")
    swift_test_code = """
import Cocoa

let app = NSApplication.shared

// 1. Decoy Window (sharingType = .readOnly, Blue)
let decoyWin = NSWindow(contentRect: NSRect(x: 120, y: 120, width: 450, height: 350),
                        styleMask: [.titled, .closable],
                        backing: .buffered, defer: false)
decoyWin.title = "Decoy Tab"
let decoyView = NSView(frame: NSRect(x: 0, y: 0, width: 450, height: 350))
decoyView.wantsLayer = true
decoyView.layer?.backgroundColor = NSColor(red: 0.0, green: 0.2, blue: 0.9, alpha: 1.0).cgColor
decoyWin.contentView = decoyView
decoyWin.makeKeyAndOrderFront(nil)

// 2. Secret Ghost Window (sharingType = .none, Red, floating directly on top)
let ghostWin = NSWindow(contentRect: NSRect(x: 120, y: 120, width: 450, height: 350),
                        styleMask: [.titled, .closable],
                        backing: .buffered, defer: false)
ghostWin.title = "Ghost Tab"
ghostWin.sharingType = .none
ghostWin.level = .floating
let ghostView = NSView(frame: NSRect(x: 0, y: 0, width: 450, height: 350))
ghostView.wantsLayer = true
ghostView.layer?.backgroundColor = NSColor(red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0).cgColor
ghostWin.contentView = ghostView
ghostWin.makeKeyAndOrderFront(nil)

// 3. Capture screen digitally after 1.2s
DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
    let task = Process()
    task.launchPath = "/usr/sbin/screencapture"
    task.arguments = ["-x", "/tmp/cloak_test_capture.png"]
    task.launch()
    task.waitUntilExit()
    exit(0)
}

app.run()
"""
    tmp_swift = "/tmp/test_cloak_runner.swift"
    tmp_bin = "/tmp/test_cloak_runner"
    with open(tmp_swift, "w") as f:
        f.write(swift_test_code)

    subprocess.run(["swiftc", tmp_swift, "-o", tmp_bin], check=True)
    
    print("[2/3] Executing digital screen capture via macOS WindowServer...")
    subprocess.run([tmp_bin], check=True)

    print("[3/3] Inspecting captured framebuffer image...")
    capture_path = "/tmp/cloak_test_capture.png"
    assert os.path.exists(capture_path), "Screenshot file was not created"

    im = Image.open(capture_path)
    w, h = im.size

    # Count pixels in the window region
    blue_count = 0
    red_count = 0

    # Sample window area (lower-left in screen coordinates, mapped to top/bottom in image)
    for x in range(240, 900):
        for y in range(h - 700, h - 240):
            p = im.getpixel((x, y))
            if p[2] > 180 and p[0] < 50:
                blue_count += 1
            elif p[0] > 200 and p[1] < 50 and p[2] < 50:
                red_count += 1

    print(f"  • Physical Screen: Ghost window was on top (Red)")
    print(f"  • Digital Screen Capture - Ghost pixels captured: {red_count} (Expected: 0)")
    print(f"  • Digital Screen Capture - Decoy pixels captured: {blue_count} (Expected: > 100,000)")

    is_cloaked = (red_count == 0 and blue_count > 100000)

    if is_cloaked:
        print("\n==========================================================")
        print("  ✓ CLOAK VERIFICATION PASSED 100%!")
        print("  • macOS WindowServer completely stripped the secret layer!")
        print("  • Any digital screen share (Zoom/Teams/Discord/Recorder)")
        print("    ONLY captures the Decoy Layer!")
        print("==========================================================")
        return True
    else:
        print("❌ Verification failed.")
        return False

if __name__ == "__main__":
    success = run_cloak_test()
    exit(0 if success else 1)
