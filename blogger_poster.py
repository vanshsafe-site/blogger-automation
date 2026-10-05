"""
Blogger auto-poster (PyAutoGUI). Posts TOFU -> MOFU -> BOFU from posts.json.

Setup:   see setup.sh (Debian/XFCE, X11)
Step 1:  python blogger_poster.py calibrate   (records screen coords once)
Step 2:  python blogger_poster.py post        (runs the posts)

Pre-req: logged into Blogger in your browser, blog's post list open
         (blogger.com/blog/posts/<id>), browser maximized, same zoom as calibration.
Abort:   slam mouse into any screen corner (PyAutoGUI failsafe).
"""
import json, sys, time, platform, subprocess, shutil
from pathlib import Path
import pyautogui, pyperclip

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4
BASE = Path(__file__).parent
CFG, POSTS = BASE / "config.json", BASE / "posts.json"
MOD = "command" if platform.system() == "Darwin" else "ctrl"

# name -> prompt shown during calibration
POINTS = {
    "new_post": "the 'New post' button on the posts list",
    "title": "the post TITLE field (in the editor)",
    "html_toggle": "the Compose/HTML view toggle (pencil icon) -- switch to HTML view first, then hover the body",
    "body": "the post BODY area (in HTML view)",
    "publish": "the 'Publish' button (top right of editor)",
    "confirm": "the 'Confirm' button in the publish popup (hover it after clicking Publish once; skip by hovering Publish again if none)",
}

def focus_firefox():
    """Raise + maximize the Firefox window (needs wmctrl; skipped if missing)."""
    if shutil.which("wmctrl"):
        subprocess.run(["wmctrl", "-a", "Mozilla Firefox"], check=False)
        time.sleep(0.5)
        subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"], check=False)
        time.sleep(1)

def launch_firefox(url, cfg):
    """Open url in a new window of your real Firefox ESR profile (stays logged in)."""
    exe = cfg.get("firefox_cmd", "firefox-esr")
    if not shutil.which(exe): sys.exit(f"'{exe}' not found in PATH")
    print(f"[1] Launching {exe} -> {url}")
    subprocess.Popen([exe, "--new-window", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(cfg["page_load_wait"] + 6)
    focus_firefox()

def goto(url, cfg):
    focus_firefox()
    pyautogui.hotkey("ctrl", "l"); time.sleep(0.5)
    paste(url); pyautogui.press("enter")
    time.sleep(cfg["page_load_wait"])

def countdown(msg, s=5):
    print(f"\n-> Hover over {msg}")
    for i in range(s, 0, -1):
        print(f"   {i}...", end="\r"); time.sleep(1)
    p = pyautogui.position(); print(f"   saved {p.x},{p.y}   ")
    return [p.x, p.y]

def calibrate():
    cfg = {"blog_posts_url": input("Blogger posts list URL: ").strip(),
           "firefox_cmd": "firefox-esr", "page_load_wait": 4, "between_posts_sec": 20}
    launch_firefox(cfg["blog_posts_url"], cfg)
    print("Firefox opened. Open any post editor, switch to HTML view, then hover as asked.")
    cfg["points"] = {k: countdown(v) for k, v in POINTS.items()}
    CFG.write_text(json.dumps(cfg, indent=2))
    print("Saved config.json")

def paste(text):
    pyperclip.copy(text); time.sleep(0.2)
    pyautogui.hotkey(MOD, "v"); time.sleep(0.5)

def click(cfg, name):
    pyautogui.click(*cfg["points"][name])

def post_one(cfg, p):
    print(f"\n=== [{p['stage'].upper()}] {p['title']} ===")
    print("[2] Opening posts list");        goto(cfg["blog_posts_url"], cfg)
    print("[3] Clicking New post");         click(cfg, "new_post"); time.sleep(cfg["page_load_wait"])
    print("[4] Pasting title");             click(cfg, "title"); paste(p["title"])
    print("[5] Pasting body (HTML view)");  click(cfg, "body"); pyautogui.hotkey(MOD, "a"); paste(p["html"])
    time.sleep(1)
    print("[6] Publishing");                click(cfg, "publish"); time.sleep(2)
    print("[7] Confirming");                click(cfg, "confirm"); time.sleep(cfg["page_load_wait"])
    print("    done")

def run(only=None):
    cfg = json.loads(CFG.read_text())
    posts = json.loads(POSTS.read_text())
    order = {"tofu": 0, "mofu": 1, "bofu": 2}
    posts = sorted(posts, key=lambda p: order[p["stage"].lower()])
    if only: posts = [p for p in posts if p["stage"].lower() == only]
    launch_firefox(cfg["blog_posts_url"], cfg)
    print("Starting in 8s -- don't touch mouse/keyboard. Corner-slam to abort.")
    time.sleep(8)
    for i, p in enumerate(posts):
        post_one(cfg, p)
        if i < len(posts) - 1: time.sleep(cfg["between_posts_sec"])
    print("Done.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "post"
    if cmd == "calibrate": calibrate()
    else: run(sys.argv[2].lower() if len(sys.argv) > 2 else None)
