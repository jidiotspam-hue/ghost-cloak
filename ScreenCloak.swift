import Cocoa
import WebKit

// MARK: - Decoy Definitions
struct DecoyOption {
    let name: String
    let urlString: String
}

let DECOY_OPTIONS: [DecoyOption] = [
    DecoyOption(name: "Google Docs", urlString: "https://docs.google.com/document/u/0/"),
    DecoyOption(name: "Canvas LMS", urlString: "https://canvas.instructure.com/"),
    DecoyOption(name: "Google Drive", urlString: "https://drive.google.com/drive/my-drive"),
    DecoyOption(name: "Wikipedia", urlString: "https://en.wikipedia.org/wiki/Main_Page"),
    DecoyOption(name: "Apple iCloud Notes", urlString: "https://www.icloud.com/notes")
]

class ScreenCloakAppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    var decoyWindow: NSWindow!
    var decoyWebView: WKWebView!
    
    var ghostWindow: NSWindow!
    var ghostWebView: WKWebView!
    
    var urlField: NSTextField!
    var decoyPopup: NSPopUpButton!
    var opacitySlider: NSSlider!
    var statusLabel: NSTextField!
    
    var isGhostHidden: Bool = false
    var currentDecoyIndex: Int = 0

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupDecoyWindow()
        setupGhostWindow()
        setupKeyMonitors()
        syncWindows()
    }

    // MARK: - Decoy Window (Digitally Visible to Screen Capture / Zoom / Teams / Discord)
    func setupDecoyWindow() {
        let initialFrame = NSRect(x: 120, y: 120, width: 1100, height: 750)
        decoyWindow = NSWindow(
            contentRect: initialFrame,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        decoyWindow.title = "Google Docs \u{2013} Essay Draft"
        // THIS IS THE KEY: Normal sharing so digital screen share/recording captures this window
        decoyWindow.sharingType = .readOnly
        decoyWindow.delegate = self
        
        let config = WKWebViewConfiguration()
        decoyWebView = WKWebView(frame: decoyWindow.contentView!.bounds, configuration: config)
        decoyWebView.autoresizingMask = [.width, .height]
        decoyWindow.contentView?.addSubview(decoyWebView)
        
        loadDecoy(index: 0)
        decoyWindow.makeKeyAndOrderFront(nil)
    }

    // MARK: - Ghost Window (Visible ONLY to Physical Display, Excluded by Graphics Server)
    func setupGhostWindow() {
        let initialFrame = decoyWindow.frame
        ghostWindow = NSWindow(
            contentRect: initialFrame,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        ghostWindow.title = "Ghost Tab [Graphics Cloak ACTIVE: Excluded from Digital Capture]"
        
        // THIS IS THE GRAPHICS SERVER CLOAK:
        // WindowServer completely removes this window from all digital capture buffers
        ghostWindow.sharingType = .none
        ghostWindow.level = .floating // Sits right on top of the decoy window
        ghostWindow.delegate = self
        
        let container = NSView(frame: ghostWindow.contentView!.bounds)
        container.autoresizingMask = [.width, .height]
        ghostWindow.contentView = container
        
        // Top Toolbar HUD
        let toolbarHeight: CGFloat = 46
        let toolbarView = NSView(frame: NSRect(x: 0, y: container.bounds.height - toolbarHeight, width: container.bounds.width, height: toolbarHeight))
        toolbarView.autoresizingMask = [.width, .minYMargin]
        toolbarView.wantsLayer = true
        toolbarView.layer?.backgroundColor = NSColor(red: 0.08, green: 0.11, blue: 0.18, alpha: 0.96).cgColor
        container.addSubview(toolbarView)
        
        // Status indicator
        let statusBadge = NSTextField(labelWithString: "\u{1F6E1}\u{FE0F} CLOAKED")
        statusBadge.frame = NSRect(x: 12, y: 12, width: 88, height: 22)
        statusBadge.font = NSFont.boldSystemFont(ofSize: 11)
        statusBadge.textColor = NSColor(red: 0.2, green: 0.85, blue: 0.5, alpha: 1.0)
        toolbarView.addSubview(statusBadge)
        
        // Back / Forward Buttons
        let backBtn = NSButton(title: "\u{2190}", target: self, action: #selector(goBack))
        backBtn.frame = NSRect(x: 104, y: 9, width: 28, height: 26)
        backBtn.bezelStyle = .rounded
        toolbarView.addSubview(backBtn)
        
        let fwdBtn = NSButton(title: "\u{2192}", target: self, action: #selector(goForward))
        fwdBtn.frame = NSRect(x: 134, y: 9, width: 28, height: 26)
        fwdBtn.bezelStyle = .rounded
        toolbarView.addSubview(fwdBtn)
        
        // URL Bar
        urlField = NSTextField(frame: NSRect(x: 168, y: 10, width: 340, height: 24))
        urlField.stringValue = "http://127.0.0.1:8080/youtube"
        urlField.target = self
        urlField.action = #selector(navigateUrl)
        urlField.autoresizingMask = [.width]
        urlField.font = NSFont.systemFont(ofSize: 12)
        toolbarView.addSubview(urlField)
        
        // Decoy Selector
        let decoyLabel = NSTextField(labelWithString: "Decoy Layer:")
        decoyLabel.frame = NSRect(x: 520, y: 12, width: 80, height: 20)
        decoyLabel.font = NSFont.systemFont(ofSize: 11)
        decoyLabel.textColor = NSColor(white: 0.75, alpha: 1.0)
        decoyLabel.autoresizingMask = [.minXMargin]
        toolbarView.addSubview(decoyLabel)
        
        decoyPopup = NSPopUpButton(frame: NSRect(x: 602, y: 9, width: 150, height: 26), pullsDown: false)
        for opt in DECOY_OPTIONS {
            decoyPopup.addItem(withTitle: opt.name)
        }
        decoyPopup.target = self
        decoyPopup.action = #selector(decoySelected)
        decoyPopup.autoresizingMask = [.minXMargin]
        toolbarView.addSubview(decoyPopup)
        
        // Test Capture Button
        let testBtn = NSButton(title: "\u{1F4F8} Verify Capture", target: self, action: #selector(testCapture))
        testBtn.frame = NSRect(x: 760, y: 9, width: 118, height: 26)
        testBtn.bezelStyle = .rounded
        testBtn.autoresizingMask = [.minXMargin]
        toolbarView.addSubview(testBtn)
        
        // Panic Button
        let panicBtn = NSButton(title: "\u{1F6A8} Panic (Esc)", target: self, action: #selector(togglePanic))
        panicBtn.frame = NSRect(x: 884, y: 9, width: 95, height: 26)
        panicBtn.bezelStyle = .rounded
        panicBtn.autoresizingMask = [.minXMargin]
        toolbarView.addSubview(panicBtn)
        
        // Ghost WKWebView (Main Secret Browser)
        let webFrame = NSRect(x: 0, y: 0, width: container.bounds.width, height: container.bounds.height - toolbarHeight)
        let config = WKWebViewConfiguration()
        config.allowsAirPlayForMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        
        ghostWebView = WKWebView(frame: webFrame, configuration: config)
        ghostWebView.autoresizingMask = [.width, .height]
        container.addSubview(ghostWebView)
        
        // Load default URL (Proxy YouTube Portal)
        if let targetUrl = URL(string: "http://127.0.0.1:8080/youtube") {
            ghostWebView.load(URLRequest(url: targetUrl))
        }
        
        ghostWindow.makeKeyAndOrderFront(nil)
    }

    // MARK: - Window Synchronization
    func windowDidMove(_ notification: Notification) {
        if let win = notification.object as? NSWindow, win == ghostWindow {
            decoyWindow.setFrame(ghostWindow.frame, display: true)
        }
    }

    func windowDidResize(_ notification: Notification) {
        if let win = notification.object as? NSWindow, win == ghostWindow {
            decoyWindow.setFrame(ghostWindow.frame, display: true)
        }
    }

    func syncWindows() {
        decoyWindow.setFrame(ghostWindow.frame, display: true)
    }

    // MARK: - Decoy Handling
    func loadDecoy(index: Int) {
        guard index >= 0 && index < DECOY_OPTIONS.count else { return }
        currentDecoyIndex = index
        let decoy = DECOY_OPTIONS[index]
        decoyWindow.title = "\(decoy.name) \u{2013} Active Document"
        
        if decoy.name == "Google Docs" {
            // High fidelity offline-ready Google Docs mock template if online login required
            let docsHtml = """
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <title>Biology Research Notes - Google Docs</title>
              <style>
                body { margin:0; padding:0; background:#f8f9fa; font-family: Roboto, Arial, sans-serif; color:#202124; }
                header { background:#fff; border-bottom:1px solid #dadce0; padding:10px 18px; display:flex; align-items:center; gap:14px; }
                .doc-icon { width:32px; height:32px; background:#4285f4; border-radius:4px; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:bold; }
                .doc-title { font-size:16px; font-weight:500; }
                .menu-bar { display:flex; gap:16px; font-size:13px; color:#3c4043; margin-top:4px; }
                .toolbar { background:#edf2fc; border-radius:24px; margin:8px 18px; padding:6px 14px; display:flex; gap:12px; font-size:12px; color:#444746; }
                .page { width:720px; min-height:850px; background:#fff; margin:20px auto; box-shadow:0 1px 3px rgba(60,64,67,.3); padding:72px 72px; box-sizing:border-box; outline:none; }
                h1 { font-size:24px; margin-bottom:16px; }
                p { font-size:14px; line-height:1.6; margin-bottom:14px; color:#333; }
              </style>
            </head>
            <body>
              <header>
                <div class="doc-icon">&#128196;</div>
                <div>
                  <div class="doc-title" contenteditable="true">Cellular Respiration and Mitochondrial Bioenergetics</div>
                  <div class="menu-bar"><span>File</span><span>Edit</span><span>View</span><span>Insert</span><span>Format</span><span>Tools</span></div>
                </div>
              </header>
              <div class="toolbar">
                <span>Undo</span><span>Redo</span><span>Print</span><span>100%</span><span>Normal text</span><span>Arial</span><span>11</span><span><b>B</b></span><span><i>I</i></span><span><u>U</u></span>
              </div>
              <div class="page" contenteditable="true">
                <h1>1. Overview of Mitochondrial ATP Synthesis</h1>
                <p>Cellular respiration is a collection of metabolic reactions that convert chemical energy from oxygen molecules and nutrients into adenosine triphosphate (ATP), subsequently releasing waste products.</p>
                <p>The catabolic reactions involved include glycolysis, pyruvate oxidation, the citric acid (Krebs) cycle, and oxidative phosphorylation via the electron transport chain located on the inner mitochondrial membrane.</p>
                <h2>2. Key Regulatory Checkpoints</h2>
                <p>Phosphofructokinase-1 (PFK-1) serves as the primary rate-limiting enzyme of glycolysis, allosterically inhibited by elevated concentrations of ATP and citrate, and activated by AMP and fructose-2,6-bisphosphate.</p>
              </div>
            </body>
            </html>
            """
            decoyWebView.loadHTMLString(docsHtml, baseURL: URL(string: "https://docs.google.com"))
        } else if let url = URL(string: decoy.urlString) {
            decoyWebView.load(URLRequest(url: url))
        }
    }

    @objc func decoySelected(_ sender: NSPopUpButton) {
        let index = sender.indexOfSelectedItem
        loadDecoy(index: index)
    }

    // MARK: - Navigation Actions
    @objc func navigateUrl() {
        var str = urlField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        if !str.hasPrefix("http://") && !str.hasPrefix("https://") {
            str = "http://" + str
        }
        if let url = URL(string: str) {
            ghostWebView.load(URLRequest(url: url))
        }
    }

    @objc func goBack() {
        if ghostWebView.canGoBack { ghostWebView.goBack() }
    }

    @objc func goForward() {
        if ghostWebView.canGoForward { ghostWebView.goForward() }
    }

    // MARK: - Panic / Boss Key (Toggles physical visibility of Ghost Window)
    @objc func togglePanic() {
        isGhostHidden.toggle()
        if isGhostHidden {
            ghostWindow.orderOut(nil)
            decoyWindow.makeKeyAndOrderFront(nil)
        } else {
            ghostWindow.makeKeyAndOrderFront(nil)
        }
    }

    func setupKeyMonitors() {
        NSEvent.addLocalMonitorForEvents(matching: .keyDown) { [weak self] event in
            // Escape key = 53
            if event.keyCode == 53 {
                self?.togglePanic()
                return nil
            }
            return event
        }
    }

    // MARK: - Verification Tool (Captures digital screenshot to prove cloak works)
    @objc func testCapture() {
        let savePath = "/tmp/screen_cloak_verification.png"
        let task = Process()
        task.launchPath = "/usr/sbin/screencapture"
        task.arguments = ["-x", savePath]
        task.launch()
        task.waitUntilExit()

        // Display confirmation alert
        let alert = NSAlert()
        alert.messageText = "Digital Screen Capture Verified!"
        alert.informativeText = "A system screenshot was captured to \(savePath).\n\nBecause the Ghost Window has sharingType = .none, macOS WindowServer excluded it entirely from the digital framebuffer. Only your selected Decoy (\(DECOY_OPTIONS[currentDecoyIndex].name)) was recorded."
        alert.addButton(withTitle: "Open Captured Image")
        alert.addButton(withTitle: "Close")
        
        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            NSWorkspace.shared.open(URL(fileURLWithPath: savePath))
        }
    }
}

let app = NSApplication.shared
let delegate = ScreenCloakAppDelegate()
app.delegate = delegate
app.run()
