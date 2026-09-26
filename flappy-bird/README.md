# 🐦 Flappy Bird - Python + Pygame + WebAssembly

A complete, polished **Flappy Bird** game built with **Python** and **pygame-ce**, packaged for modern web browsers via **pygbag / WebAssembly**, and ready for automated deployment to **Render**.

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
 Render Static Site CDN
```

### Project Structure

```text
flappy-bird/
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
│   ├── create_template.py     # Custom arcade loading UI template generator
│   └── generate_assets.py     # Asset & audio synthesizer script
├── default.tmpl               # Custom arcade loading screen Pygbag template
├── build.py                   # Pygbag build script
├── main.py                    # Root entry point
├── requirements.txt           # Python dependencies (pygame-ce, pygbag)
├── RENDER_DEPLOYMENT.md       # Render Static Site deployment guide
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
python -m pygbag --ume_block 0 --build main.py
```

This packages the application into the `build/web/` directory containing:
* `index.html` (WebAssembly loader and retro arcade loading interface)
* `flappy-bird.apk` / `flappy-bird.tar.gz` (Packaged assets and Python bytecode)
* `favicon.png`

### Test Web Build Locally

To test the browser game locally with a static web server:
```bash
python -m http.server 5500 --directory build/web
```
Then navigate to `http://localhost:5500` in your web browser.

---

## ☁️ Deployment to Render

The game deploys automatically as a **Render Static Site**. On every GitHub push, Render runs `pygbag` to build fresh WebAssembly assets and serves them globally.

### Render Static Site Settings:
* **Service Type**: Static Site
* **Root Directory**: `flappy-bird`
* **Build Command**: `pip install -r requirements.txt && python -m pygbag --ume_block 0 --build main.py`
* **Publish Directory**: `build/web`

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed deployment setup and instructions.

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
