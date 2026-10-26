"""High-Definition Razor-Sharp Video Recorder with Vector Mouse Pointer & Zero Blank Start.

Enhancements:
1. Eliminates initial blank screen via exact FFmpeg start-trim (-ss).
2. Crystal-clear vector rendering with Lanczos scaling, unsharp filter, and 8 Mbps bitrate (zero blur).
3. Realistic SVG arrow cursor with illuminated click-ripple animations.
4. Human-like gradual Bezier trajectories and smooth viewport scrolling.
"""

import os
import sys
import time
import subprocess
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

CURRENT_MOUSE_POS = [960, 540]

def inject_virtual_cursor(page):
    """Inject a razor-sharp SVG pointer arrow with expanding click ripple rings."""
    js_code = """
    (() => {
        if (document.getElementById('playwright-cursor-container')) return;

        // Container
        const container = document.createElement('div');
        container.id = 'playwright-cursor-container';
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '2147483647';
        document.body.appendChild(container);

        // SVG Mouse Arrow
        const cursor = document.createElement('div');
        cursor.id = 'playwright-cursor';
        cursor.style.position = 'fixed';
        cursor.style.width = '28px';
        cursor.style.height = '28px';
        cursor.style.pointerEvents = 'none';
        cursor.style.transform = 'translate(-2px, -2px)';
        cursor.style.transition = 'transform 0.08s ease';
        cursor.innerHTML = `
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 2L22 13L13.5 15.5L10 24L4 2Z" fill="#00e5ff" stroke="#ffffff" stroke-width="2.5" stroke-linejoin="round"/>
        </svg>
        `;
        container.appendChild(cursor);

        // Move event
        window.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        // Click ripple animation
        window.addEventListener('mousedown', (e) => {
            cursor.style.transform = 'translate(-2px, -2px) scale(0.85)';
            
            const ripple = document.createElement('div');
            ripple.style.position = 'fixed';
            ripple.style.left = e.clientX + 'px';
            ripple.style.top = e.clientY + 'px';
            ripple.style.width = '12px';
            ripple.style.height = '12px';
            ripple.style.borderRadius = '50%';
            ripple.style.backgroundColor = 'rgba(239, 68, 68, 0.4)';
            ripple.style.border = '2px solid #ef4444';
            ripple.style.boxShadow = '0 0 16px #ef4444';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.pointerEvents = 'none';
            ripple.style.transition = 'width 0.35s cubic-bezier(0.1, 0.8, 0.2, 1), height 0.35s cubic-bezier(0.1, 0.8, 0.2, 1), opacity 0.35s ease-out';
            container.appendChild(ripple);

            requestAnimationFrame(() => {
                ripple.style.width = '55px';
                ripple.style.height = '55px';
                ripple.style.opacity = '0';
            });

            setTimeout(() => ripple.remove(), 400);
        });

        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-2px, -2px) scale(1)';
        });
    })();
    """
    page.evaluate(js_code)

def smooth_move(page, target_x, target_y, steps=25, delay=0.015):
    """Generate human-like smooth cursor motion."""
    global CURRENT_MOUSE_POS
    start_x, start_y = CURRENT_MOUSE_POS

    for i in range(1, steps + 1):
        t = i / steps
        # Smooth easeInOut quad curve
        t_smooth = 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
        cur_x = start_x + (target_x - start_x) * t_smooth
        cur_y = start_y + (target_y - start_y) * t_smooth
        page.mouse.move(cur_x, cur_y)
        time.sleep(delay)

    CURRENT_MOUSE_POS = [target_x, target_y]

def smooth_click(page, selector, hover_time=0.4):
    """Smooth move to element, hover, and trigger click with visual ripple."""
    loc = page.locator(selector).first
    box = loc.bounding_box()
    if box:
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        smooth_move(page, target_x, target_y, steps=26)
        time.sleep(hover_time)
        page.mouse.down()
        time.sleep(0.12)
        page.mouse.up()
        time.sleep(0.35)
    else:
        page.click(selector)

def smooth_scroll(page, delta_y, steps=20, delay=0.02):
    """Smooth gradual scrolling."""
    step_delta = delta_y / steps
    for _ in range(steps):
        page.mouse.wheel(0, step_delta)
        time.sleep(delay)

def record():
    output_dir = os.path.abspath("recorded_video")
    os.makedirs(output_dir, exist_ok=True)

    print("[*] Launching Chromium (1920x1080) for Master Quality Recording...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=output_dir,
            record_video_size={"width": 1920, "height": 1080}
        )

        page = context.new_page()
        url = "https://aegis-ops-livid.vercel.app/"
        print(f"[*] Navigating to {url} and waiting for full render...")
        page.goto(url, wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        inject_virtual_cursor(page)
        
        # Initial stabilization pause (this will be cleanly trimmed by FFmpeg)
        BLANK_TRIM_SECONDS = 3.5
        print(f"[*] Stabilizing DOM for {BLANK_TRIM_SECONDS}s (will be trimmed)...")
        time.sleep(BLANK_TRIM_SECONDS)

        # -------------------------------------------------------------
        # SEGMENT 1 (0:00 - 0:25): Header & Overview
        # -------------------------------------------------------------
        print("[>] Segment 1: Header, Tags, and Status Pill...")
        smooth_move(page, 420, 55, steps=30)  # Move to logo
        time.sleep(4)
        smooth_move(page, 760, 55, steps=25)  # Hover over tags (#strands-decider-2b)
        time.sleep(5)
        smooth_move(page, 1140, 55, steps=25) # Status pill
        time.sleep(6)

        # -------------------------------------------------------------
        # SEGMENT 2 (0:25 - 0:50): Dual-Brain Architecture Showcase
        # -------------------------------------------------------------
        print("[>] Segment 2: Dual-Brain Architecture cards...")
        smooth_scroll(page, 380, steps=25)
        time.sleep(2)
        inject_virtual_cursor(page)

        # Hover System 1 card (Decider 2B)
        smooth_move(page, 480, 620, steps=30)
        time.sleep(8)

        # Hover System 2 card (Amazon Bedrock)
        smooth_move(page, 1420, 620, steps=35)
        time.sleep(8)

        # Smooth scroll back up to Launchpad
        smooth_scroll(page, -380, steps=25)
        time.sleep(3)

        # -------------------------------------------------------------
        # SEGMENT 3 (0:50 - 1:25): Demo 1 - DDoS Traffic Surge & Auto-Remediation
        # -------------------------------------------------------------
        print("[>] Segment 3: Demo 1 - DDoS Traffic Surge...")
        smooth_click(page, "button:has-text('DDoS Traffic Surge')")
        time.sleep(3)

        # Click Run Dual-Brain Agent
        smooth_click(page, "#runBtn")
        print("    Waiting for Decider 2B response...")
        time.sleep(4)

        # Hover metrics bar & Decider 2B verdict
        smooth_move(page, 280, 480, steps=25)  # Hover 77ms latency metric
        time.sleep(3)
        smooth_move(page, 1100, 480, steps=25) # Hover PROTECTED status
        time.sleep(3)

        # Scroll to Bedrock forensic post-mortem
        smooth_scroll(page, 320, steps=20)
        smooth_move(page, 1400, 750, steps=30) # Point to Bedrock report
        time.sleep(8)

        # Scroll back up to launchpad
        smooth_scroll(page, -320, steps=20)
        time.sleep(2)

        # -------------------------------------------------------------
        # SEGMENT 4 (1:25 - 1:55): Demo 2 - Adversarial Prompt Injection Defense
        # -------------------------------------------------------------
        print("[>] Segment 4: Demo 2 - Adversarial Prompt Injection Defense...")
        smooth_click(page, "button:has-text('Adversarial Prompt Injection')")
        time.sleep(3)

        # Click Run Dual-Brain Agent
        smooth_click(page, "#runBtn")
        print("    Waiting for Decider 2B attack interception...")
        time.sleep(4)

        # Hover ATTACK BLOCKED and DENY verdict
        smooth_move(page, 1100, 480, steps=25) # ATTACK BLOCKED badge
        time.sleep(4)
        smooth_scroll(page, 280, steps=15)
        smooth_move(page, 620, 680, steps=25)  # DENY (98% confidence)
        time.sleep(6)

        # Scroll back up
        smooth_scroll(page, -280, steps=15)
        time.sleep(2)

        # -------------------------------------------------------------
        # SEGMENT 5 (1:55 - 2:20): Demo 3 - High-Frequency Chaos Alert Storm
        # -------------------------------------------------------------
        print("[>] Segment 5: Demo 3 - High-Frequency Chaos Alert Storm...")
        smooth_click(page, "#chaosBtn")
        time.sleep(3)

        # Smooth scroll to Chaos stats grid
        smooth_scroll(page, 450, steps=25)
        time.sleep(2)

        # Glide cursor across the Chaos stat cards
        smooth_move(page, 360, 680, steps=25)  # 50 Incidents
        time.sleep(3)
        smooth_move(page, 650, 680, steps=25)  # Decider duration (3.0s)
        time.sleep(3)
        smooth_move(page, 950, 680, steps=25)  # Throughput (16.4/s)
        time.sleep(3)
        smooth_move(page, 1250, 680, steps=25) # Attacks blocked (12)
        time.sleep(3)
        smooth_move(page, 1550, 680, steps=25) # Dollars saved ($1.50)
        time.sleep(4)

        # -------------------------------------------------------------
        # SEGMENT 6 (2:20 - 2:40): Demo 4 - Latency & Cost Benchmark Report
        # -------------------------------------------------------------
        print("[>] Segment 6: Demo 4 - Benchmark Suite Table...")
        smooth_scroll(page, -450, steps=20)
        time.sleep(2)
        smooth_click(page, "#benchBtn")
        time.sleep(3)

        # Scroll to benchmark table
        smooth_scroll(page, 600, steps=25)
        time.sleep(2)

        # Glide cursor down the benchmark rows showing the 32x speedup
        smooth_move(page, 950, 700, steps=25)
        time.sleep(3)
        smooth_move(page, 950, 820, steps=25)
        time.sleep(4)

        # -------------------------------------------------------------
        # CLOSING (2:40 - 2:48): Smooth scroll back to top header
        # -------------------------------------------------------------
        print("[>] Closing: Scrolling back to top header...")
        smooth_scroll(page, -800, steps=30)
        smooth_move(page, 960, 200, steps=25)
        time.sleep(6)

        # Close page to flush video
        page.close()
        video_path = page.video.path()
        context.close()
        browser.close()

    print(f"\n[+] Raw video saved: {video_path}")
    
    # -------------------------------------------------------------
    # MASTER QUALITY ENCODING: Trim Blank Start + Unsharp Sharpening Filter
    # -------------------------------------------------------------
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mp4_path = os.path.join(output_dir, "AegisOps_Demo_Walkthrough.mp4")
    print(f"[*] Trimming initial blank frames and encoding crystal-clear 1080p MP4...")

    # -ss 00:00:03.5 skips initial blank loading
    # -vf unsharp=5:5:0.8:5:5:0.4 applies subtle edge sharpening for razor-sharp text
    # -b:v 8M and -crf 14 provides master broadcast quality with zero blur
    cmd = [
        ffmpeg,
        "-y",
        "-ss", "00:00:03.5",
        "-i", video_path,
        "-vf", "scale=1920:1080:flags=lanczos,unsharp=5:5:0.8:5:5:0.4",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "14",
        "-b:v", "8M",
        "-maxrate", "12M",
        "-bufsize", "24M",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        mp4_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        file_size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        print(f"[SUCCESS] Master 1080p MP4 Created: {mp4_path} ({file_size_mb:.2f} MB)")
    else:
        print("[!] Advanced encode failed, falling back to standard encode:", res.stderr)
        cmd_fallback = [ffmpeg, "-y", "-ss", "00:00:03.5", "-i", video_path, "-c:v", "libx264", "-crf", "18", mp4_path]
        subprocess.run(cmd_fallback)

if __name__ == "__main__":
    record()
