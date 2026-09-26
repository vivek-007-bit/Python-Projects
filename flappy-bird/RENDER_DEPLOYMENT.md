# Flappy Bird — Render Static Site Deployment Guide

This document provides step-by-step instructions for deploying the **Flappy Bird** Python/Pygame game as a high-performance **Static Site** on [Render](https://render.com).

---

## 1. Architecture Overview

```text
GitHub Push (Python-Projects repository)
   │
   ▼
Render Build Environment (Linux Container)
   ├── 1. Install dependencies: pip install -r requirements.txt
   └── 2. Compile WebAssembly: python -m pygbag --ume_block 0 --build main.py
   │
   ▼
Generates 'build/web/' static bundle
   ├── index.html (Arcade loading screen + Pygbag runtime)
   ├── flappy-bird.tar.gz (Packaged Python game & assets)
   ├── flappy-bird.apk (WebAssembly filesystem)
   └── favicon.png
   │
   ▼
Render Static Site CDN (Serves build/web directly)
   │
   ▼
User Browser (Executes Python via CPython 3.12 WebAssembly)
```

> [!NOTE]
> **No Python Server at Runtime**: Python is only used during the **Build Phase** on Render to compile the game assets into WebAssembly and HTML/JS bundles. At runtime, Render serves pure static files over its global CDN.

---

## 2. Render Service Configuration

When creating a new service on Render:

| Field | Setting |
| :--- | :--- |
| **Service Type** | **Static Site** |
| **Repository** | `Python-Projects` |
| **Branch** | `main` |
| **Root Directory** | `flappy-bird` |
| **Build Command** | `pip install -r requirements.txt && python -m pygbag --ume_block 0 --build main.py` |
| **Publish Directory** | `build/web` |
| **Environment** | Python 3 |

---

## 3. Key Configuration Details

### Pygbag Version & Flag
- **Version**: `pygbag==0.9.3` (pinned in `requirements.txt`).
- **`--ume_block 0`**: Ensures the game runtime does not block waiting for legacy user media activation clicks, enabling seamless instant loading.

### Why `build/web` is not in Git
Render automatically runs the build command on every push to your GitHub repository, compiling fresh WebAssembly archives directly from the Python source code and assets. Thus, generated binary files (`build/`) are ignored in `.gitignore` to keep the repository lightweight and clean.

### Core Build Artifacts Served
- `index.html`: Entry point featuring the custom retro arcade loading interface.
- `flappy-bird.tar.gz`: The compressed game code and sprite/audio assets unpacked by the WebAssembly runtime.
- `favicon.png`: Game favicon.

---

## 4. Step-by-Step Deployment Instructions

1. **Push to GitHub**:
   Ensure all changes in `flappy-bird/` are committed and pushed to your GitHub repository (`Python-Projects`).

2. **Open Render Dashboard**:
   Go to [dashboard.render.com](https://dashboard.render.com) and click **"New +"** $\rightarrow$ **"Static Site"**.

3. **Connect Your Repository**:
   Select your `Python-Projects` repository.

4. **Fill Service Settings**:
   - **Name**: `flappy-bird` (or your preferred name)
   - **Root Directory**: `flappy-bird`
   - **Build Command**: `pip install -r requirements.txt && python -m pygbag --ume_block 0 --build main.py`
   - **Publish Directory**: `build/web`

5. **Deploy**:
   Click **"Create Static Site"**. Render will clone the repo, install `pygame-ce` and `pygbag`, build the web package, and deploy the live site.

---

## 5. Local Testing & Verification

Before pushing, you can simulate Render's build and test the static site locally:

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the exact Render build command
python -m pygbag --ume_block 0 --build main.py

# 3. Serve the static output locally
python -m http.server 5500 --directory build/web
```

Open `http://localhost:5500` in your browser to verify the game.
