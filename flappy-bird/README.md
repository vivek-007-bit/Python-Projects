# 🐦 Flappy Bird — Web-Native Edition (FastAPI + HTML5 Canvas)

A complete, high-performance web-native **Flappy Bird** arcade game built with **FastAPI**, **HTML5 Canvas**, **Vanilla JavaScript**, and **CSS3**. 

Designed for instant browser loading at 60 FPS without heavy WebAssembly or Pygame emulators, and architected for seamless zero-config deployment to **Vercel**.

---

## 🌟 Key Features & Mechanics

* **Authentic 60 FPS Physics**:
  * Gravity: $0.42\text{ px/frame}^2$
  * Flap Impulse: $-8.2\text{ px/frame}$ upward velocity
  * Terminal Velocity: $10.5\text{ px/frame}$
  * Fluid pitch rotation: Tilts upward on jump ($+28^\circ$) and pitches down into a dive smoothly (up to $-85^\circ$).
* **Exact Dimensions & Scaling**:
  * Logical $400 \times 700$ px resolution.
  * Responsive aspect-ratio letterboxing adapting cleanly to desktop, laptop, tablet, and mobile screens.
* **Sprite Animation & Environments**:
  * 3-frame animated flapping bird wings.
  * Parallax scrolling sky background ($0.6\text{ px/frame}$) and seamless scrolling ground ($3.0\text{ px/frame}$).
  * Inset collision hitboxes for forgiving, fair gameplay.
* **Visual Polish & Particles**:
  * Flap dust puffs, golden score sparkles, and floating "+1" score indicators.
  * Screen-shake ($10\text{ px}$ impact) and hit flash effects on collision.
  * Feather bursts upon game over.
* **Medals & High Scores**:
  * Arcade Medals: **Bronze** ($\ge 10$), **Silver** ($\ge 20$), **Gold** ($\ge 30$), and **Platinum** ($\ge 40$).
  * Persistent high score tracking via browser `localStorage`.
* **Sound Engine**:
  * Web Audio API & HTML5 Audio with fallback sound synthesizer for zero-latency flap, point, hit, and die sound effects.
  * Interactive on-canvas mute toggle (`M`) and pause toggle (`P` / `Esc`).

---

## 🏗️ Architecture & Technology Stack

```text
Browser Client
   ├── HTML5 Canvas (Logical 400x700 2D context)
   ├── Vanilla JavaScript Game Loop (requestAnimationFrame)
   └── Web Audio API & Particle Systems
         │
         ▼ (HTTP / Static Requests)
FastAPI Server / Vercel Zero-Config
   ├── main.py (Root ASGI discovery entrypoint)
   ├── app/main.py (FastAPI App & Static asset mounts)
   └── app/templates/index.html (Jinja2 Template)
```

### Project Structure

```text
Flappy-Bird/
├── main.py                 # Root ASGI discovery entrypoint
├── pyproject.toml          # Vercel entrypoint configuration
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application & static mount
│   ├── routes/
│   │   ├── __init__.py
│   │   └── game.py         # Primary route handler & favicon
│   ├── templates/
│   │   └── index.html      # Jinja2 Canvas template
│   └── static/
│       ├── css/
│       │   └── game.css    # Responsive arcade styling
│       ├── js/
│       │   └── game.js     # 60 FPS HTML5 Canvas engine
│       └── assets/
│           ├── images/     # Sprites (bird, pipe, background, ground)
│           └── sounds/     # Audio effects (flap, point, hit, die)
├── requirements.txt        # fastapi, uvicorn, jinja2
├── .gitignore              # Git ignore rules
└── README.md
```

---

## 🚀 Local Development

### 1. Prerequisites
* Python 3.10+
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

### 4. Run the Development Server

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

---

## 🎮 Controls

| Action | Desktop Keyboard / Mouse | Mobile / Tablet Touch |
| :--- | :--- | :--- |
| **Flap / Jump** | `Spacebar`, `Up Arrow`, `Left Click` | `Tap anywhere on canvas` |
| **Start / Restart** | `Spacebar`, `Up Arrow`, `Left Click` | `Tap anywhere on canvas` |
| **Pause / Resume** | `P`, `Esc`, or Click `Pause Icon` | Tap `Pause Icon` (top-left) |
| **Mute / Unmute** | `M` or Click `Speaker Icon` | Tap `Speaker Icon` (top-right) |

---

## ☁️ Deployment to Vercel

This project is configured for seamless zero-configuration deployment on **Vercel**:

### Option A: Deploy via GitHub (Recommended)
1. Push this repository to GitHub.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Select your repository.
4. Vercel automatically detects the FastAPI application from `pyproject.toml` and `main.py`, serving both the HTML5 Canvas game and static assets natively.

### Option B: Deploy via Vercel CLI
```bash
npm install -g vercel
vercel
```
