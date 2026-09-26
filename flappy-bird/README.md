# 🐦 Flappy Bird - Python + Pygame + WebAssembly

A complete, polished **Flappy Bird** game built with **Python** and **pygame-ce**, packaged for modern web browsers via **pygbag / WebAssembly**, and ready for instant deployment to **Vercel**.

---

## 🌟 Key Features

* **Authentic Physics & Controls:** Smooth gravity, instantaneous flap impulse, and fluid pitch tilt based on vertical velocity.
* **Dual-Platform Architecture:** Runs as a native desktop application or as a WebAssembly browser game.
* **Responsive Aspect-Ratio Scaling:** Renders at a logical $400 \times 700$ resolution and scales dynamically to any desktop, tablet, or mobile viewport with letterboxing.
* **First-Class Mobile Touch & Desktop Inputs:**
  * **Desktop:** Spacebar, Up Arrow, Left Mouse Click.
  * **Mobile:** Tap anywhere on the viewport.
  * **Utility Keys:** `P` / `Esc` for Pause, `M` for Mute/Unmute.
* **Clean State Management:** Robust transitions between `MENU`, `PLAYING`, `PAUSED`, and `GAME_OVER`.
* **Visual Polish & Effects:**
  * Multi-frame animated bird wings.
  * Parallax scrolling sky background and seamless ground animation.
  * Flap dust puffs, golden score sparkle bursts, floating "+1" popups, and impact feather bursts.
  * Subtle screen-shake and hit flash feedback on collision.
  * Arcade medal awards (Bronze, Silver, Gold, Platinum) based on achieved scores.
* **Robust Sound System:** Safe PCM audio engine with sound effects for flap, score, collision, and game over, complete with in-game mute toggle and graceful audio fallbacks.
* **High Score Persistence:** Local storage / session best score tracking.

---

## 🏗️ Architecture & Technology Stack

```text
Python 3 (pygame-ce)
        ↓
    pygbag
        ↓
 WebAssembly (Wasm)
        ↓
  Modern Browser
        ↓
 Vercel Static CDN
```

### Project Structure

```text
Flappy Bird/
├── build/
│   └── web/                   # Generated WebAssembly browser package
│       ├── index.html
│       ├── favicon.png
│       ├── flappy.bird.apk
│       └── flappy.bird.tar.gz
├── game/
│   ├── assets/
│   │   ├── images/            # Sprites (bird, pipe, background, ground)
│   │   └── sounds/            # WebAssembly-compatible OGG audio (flap, point, hit, die)
│   ├── __init__.py
│   ├── game.py                # State machine, UI rendering, score, polish
│   ├── main.py                # Main async game loop & viewport scaler
│   ├── particles.py           # Particle effects & floating text popups
│   ├── pipe.py                # Pipe obstacle manager & collision boxes
│   ├── player.py              # Bird physics, rotation, & animation frames
│   ├── settings.py            # Global constants & game configuration
│   └── sound_manager.py       # Audio loading, volume, & mute controller
├── tests/
│   └── test_game.py           # Automated unit test suite
├── tools/
│   └── generate_assets.py     # Asset & audio synthesizer script
├── build.py                   # Pygbag build script
├── main.py                    # Root entry point
├── requirements.txt           # Python dependencies (pygame-ce, pygbag)
├── vercel.json                # Vercel static hosting configuration
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
* Python 3.10+ (Python 3.11 - 3.14 supported)
* `pip`

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Activate on Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Game Locally

```bash
python main.py
```
*(Or `python game/main.py`)*

---

## 🎮 Game Controls

| Action | Desktop Controls | Mobile / Touch |
| :--- | :--- | :--- |
| **Flap / Jump** | `Space`, `Up Arrow`, `Left Click` | `Tap anywhere` |
| **Start / Restart** | `Space`, `Up Arrow`, `Left Click` | `Tap anywhere` |
| **Pause / Resume** | `P`, `Esc`, or Click `Pause Icon` | Tap `Pause Icon` (top-left) |
| **Mute / Unmute** | `M` or Click `Speaker Icon` | Tap `Speaker Icon` (top-right) |

---

## 🌐 Building for Web with Pygbag

The project uses **pygbag** to compile the Python/Pygame codebase into WebAssembly.

### Build the Web Package

Run the provided build helper:
```bash
python build.py
```
Or directly via the CLI:
```bash
python -m pygbag --build .
```

This packages the application into the `build/web/` directory containing:
* `index.html` (WebAssembly loader and HTML5 Canvas interface)
* `flappy.bird.apk` / `flappy.bird.tar.gz` (Packaged assets and Python bytecode)
* `favicon.png`

### Test Web Build Locally

To test the browser game locally in your browser with a live test server:
```bash
python -m pygbag .
```
Then navigate to `http://localhost:8000` in your web browser.

---

## ☁️ Deployment to Vercel

Vercel serves the generated WebAssembly static build (`build/web/`) through its global edge CDN.

### Option A: Automated Git Deployment (Recommended)

1. Push this repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: complete Flappy Bird web game"
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Vercel will automatically detect `vercel.json` and serve the `build/web` directory with the proper WebAssembly headers (`Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`).
5. Click **Deploy**.

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Build the WebAssembly bundle
python build.py

# Deploy to Vercel
vercel --prod
```

---

## 🧪 Running Automated Tests

Run the unit test suite to verify physics calculations, state transitions, pipe collisions, sound safety, and viewport mapping:

```bash
python -m unittest tests/test_game.py
```

---

## ⚙️ Configuration & Customization

All gameplay constants are centralized in `game/settings.py`:

```python
GAME_WIDTH = 400            # Logical game canvas width
GAME_HEIGHT = 700           # Logical game canvas height
FPS = 60                    # Target frame rate

GRAVITY = 0.42              # Bird downward gravitational pull
FLAP_STRENGTH = -8.2        # Bird upward flap velocity
MAX_FALL_SPEED = 10.5       # Terminal velocity

PIPE_WIDTH = 70             # Width of green pipes
PIPE_GAP = 175              # Vertical gap between top and bottom pipe
PIPE_SPEED = 3.0            # Horizontal scroll speed
PIPE_SPAWN_DISTANCE = 230   # Spacing between consecutive pipe pairs

MASTER_VOLUME = 0.7         # Sound effects master volume
```

---

## 🛠️ Troubleshooting

* **Black borders on screen:** This is the intentional aspect-ratio letterboxing ensuring the game retains its $400 \times 700$ geometry without distortion on wide or tall monitors.
* **Audio disabled or silent:** Ensure sound is not muted in-game (press `M` or check the speaker icon). The game includes built-in fallbacks and will continue running smoothly even if host audio hardware is unavailable.
