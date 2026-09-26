"""
Generates the customized default.tmpl for Pygbag with an arcade-style Flappy Bird loading UI.
"""
import os
import base64

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_template(output_paths):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, "game", "assets", "images")

    bird_up_b64 = get_base64(os.path.join(img_dir, "bird_up.png"))
    bird_mid_b64 = get_base64(os.path.join(img_dir, "bird_mid.png"))
    bird_down_b64 = get_base64(os.path.join(img_dir, "bird_down.png"))

    template_content = f"""<html lang="en-us"><script src="{{{{cookiecutter.cdn}}}}pythons.js" type=module id="site" data-python="python{{{{cookiecutter.PYBUILD}}}}" data-LINES=42 data-COLUMNS=132 data-os="vtx,snd,gui" async defer>#<!--

print(\"\"\"
Loading {{{{cookiecutter.title}}}} from {{{{cookiecutter.archive}}}}.apk
    Pygbag Version : {{{{cookiecutter.version}}}}
    Template Version : 0.9.3
    Python  : {{{{cookiecutter.PYBUILD}}}}
    CDN URL : {{{{cookiecutter.cdn}}}}
    Screen  : {{{{cookiecutter.width}}}}x{{{{cookiecutter.height}}}}
    Title   : {{{{cookiecutter.title}}}}
    Folder  : {{{{cookiecutter.directory}}}}
    Authors : {{{{cookiecutter.authors}}}}
    SPDX-License-Identifier: {{{{cookiecutter.spdx}}}}

\"\"\")

import sys
import asyncio
import platform
import json
from pathlib import Path

# do not rename
async def custom_site():
    import embed
    platform.document.body.style.background = "#4ec0ca"

    platform.window.transfer.hidden = true
    platform.window.canvas.style.visibility = "visible"

    bundle = "{{{{cookiecutter.archive}}}}"

    # the C or js loader could do that but be explicit.
    appdir = Path(f"/data/data/{{bundle}}") # /data/data/{{{{cookiecutter.archive}}}}
    appdir.mkdir()

    # unpack filesystem from compressed archive into work dir
    if platform.window.location.host.find('.itch.zone')>0:
        import zipfile
        async with platform.fopen("{{{{cookiecutter.archive}}}}.apk", "rb") as archive:
            with zipfile.ZipFile(archive) as zip_ref:
                zip_ref.extractall(appdir.as_posix())
    else:
        import tarfile
        async with platform.fopen("{{{{cookiecutter.archive}}}}.tar.gz", "rb") as archive:
            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()

    # preloader will change to work dir and prepend it to sys.path
    platform.run_main(PyConfig, loaderhome= appdir / "assets", loadermain=None)

    # wait preloading complete : that includes images and wasm compilation of bundled modules
    while embed.counter()<0:
        await asyncio.sleep(.1)

    main = appdir / "assets" / "main.py"

    # test/wait user media interaction
    if not platform.window.MM.UME:
        __import__(__name__).__file__ = main
        msg = "Click anywhere to Play!"
        platform.window.infobox.innerText = msg

        while not platform.window.MM.UME:
            await asyncio.sleep(.1)

    # start async top level machinery if not started
    await TopLevel_async_handler.start_toplevel(platform.shell, console=window.python.config.debug)
    __import__(__name__).__file__ = main

    def ui_callback(pkg):
        platform.window.infobox.innerText = f"Installing {{pkg}}..."

    # Hide custom loading screen smoothly
    platform.window.eval("if (window.hideLoadingScreen) window.hideLoadingScreen();")

    await shell.source(main, callback=ui_callback)

    platform.window.infobox.style.display = "none"
    platform.window.config.gui_divider = 1
    platform.window.window_resize()
    print("default.tmpl: done")

    shell.interactive()

asyncio.run( custom_site() )

# BEGIN BLOCK
# --></script><head>
    <title>{{{{cookiecutter.title}}}}</title>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <link rel="icon" type="image/png" href="favicon.png" sizes="16x16">

    <script type="application/javascript">
    config = {{
        xtermjs : "{{{{cookiecutter.xtermjs}}}}" ,
        _sdl2 : "canvas",
        user_canvas : 0,
        user_canvas_managed : 0,
        gui_divider : 2,
        ume_block : {{{{cookiecutter.ume_block}}}},
        can_close : {{{{cookiecutter.can_close}}}},
        archive : "{{{{cookiecutter.archive}}}}",
        gui_debug : 2,
        cdn : "{{{{cookiecutter.cdn}}}}",
        autorun : {{{{cookiecutter.autorun}}}},
        PYBUILD : "{{{{cookiecutter.PYBUILD}}}}",
        fb_ar   :  1.77,
        fb_width : "{{{{cookiecutter.width}}}}",
        fb_height : "{{{{cookiecutter.height}}}}"
    }};

    function show_infobox() {{
        infobox.style.display = "block";
    }}
    </script>

    <style>
        * {{
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
        }}

        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #4ec0ca;
            font-family: 'Trebuchet MS', 'Segoe UI', Arial, sans-serif;
        }}

        /* Sky & Background Clouds Animation */
        .sky-bg {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, #4ec0ca 0%, #a0e8f0 75%, #ded895 75%, #ded895 100%);
            z-index: 1;
            overflow: hidden;
        }}

        .cloud {{
            position: absolute;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 50px;
            pointer-events: none;
        }}
        .cloud::before, .cloud::after {{
            content: '';
            position: absolute;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 50%;
        }}
        .cloud-1 {{
            width: 120px;
            height: 40px;
            top: 15%;
            left: -130px;
            animation: moveClouds 18s linear infinite;
        }}
        .cloud-1::before {{ width: 50px; height: 50px; top: -20px; left: 18px; }}
        .cloud-1::after {{ width: 40px; height: 40px; top: -14px; left: 55px; }}

        .cloud-2 {{
            width: 160px;
            height: 50px;
            top: 35%;
            left: -170px;
            animation: moveClouds 24s linear infinite 5s;
        }}
        .cloud-2::before {{ width: 65px; height: 65px; top: -26px; left: 24px; }}
        .cloud-2::after {{ width: 52px; height: 52px; top: -18px; left: 75px; }}

        .cloud-3 {{
            width: 100px;
            height: 35px;
            top: 55%;
            left: -110px;
            animation: moveClouds 15s linear infinite 2s;
        }}
        .cloud-3::before {{ width: 42px; height: 42px; top: -16px; left: 15px; }}
        .cloud-3::after {{ width: 34px; height: 34px; top: -12px; left: 45px; }}

        @keyframes moveClouds {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(calc(100vw + 200px)); }}
        }}

        /* Loading Screen Overlay Card */
        #loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            transition: opacity 0.5s ease, transform 0.5s ease;
        }}

        .loading-card {{
            background: rgba(255, 255, 255, 0.94);
            border: 4px solid #543847;
            border-radius: 24px;
            padding: 32px 28px;
            width: 90%;
            max-width: 360px;
            text-align: center;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28), 0 0 0 4px #e09f3e inset;
            position: relative;
            backdrop-filter: blur(8px);
            animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}

        @keyframes popIn {{
            0% {{ transform: scale(0.85); opacity: 0; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}

        /* Bird Flapping Animation */
        .bird-anim {{
            width: 58px;
            height: 42px;
            margin: 0 auto 12px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            animation: flapWings 0.35s steps(1) infinite, birdHover 1.6s ease-in-out infinite alternate;
        }}

        @keyframes flapWings {{
            0%, 100% {{ background-image: url('data:image/png;base64,{bird_up_b64}'); }}
            33% {{ background-image: url('data:image/png;base64,{bird_mid_b64}'); }}
            66% {{ background-image: url('data:image/png;base64,{bird_down_b64}'); }}
        }}

        @keyframes birdHover {{
            0% {{ transform: translateY(0px) rotate(-4deg); }}
            100% {{ transform: translateY(-12px) rotate(6deg); }}
        }}

        /* Title */
        .game-title {{
            font-family: 'Impact', 'Arial Black', sans-serif;
            font-size: 34px;
            color: #f7b731;
            letter-spacing: 1.5px;
            margin: 0;
            text-shadow: 2px 2px 0 #543847, -2px -2px 0 #543847, 2px -2px 0 #543847, -2px 2px 0 #543847, 0 4px 0 #543847;
        }}

        .game-subtitle {{
            display: inline-block;
            background: #e74c3c;
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            padding: 3px 10px;
            border-radius: 12px;
            border: 2px solid #543847;
            margin-top: 4px;
            margin-bottom: 22px;
            text-transform: uppercase;
        }}

        /* Progress Bar */
        .progress-wrapper {{
            margin: 16px 0 10px;
        }}

        .progress-track {{
            width: 100%;
            height: 22px;
            background: #ded895;
            border: 3px solid #543847;
            border-radius: 14px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }}

        .progress-fill {{
            height: 100%;
            width: 12%;
            background: linear-gradient(90deg, #f39c12, #f1c40f, #2ecc71);
            background-size: 200% 100%;
            border-radius: 10px;
            transition: width 0.25s ease-out;
            animation: shimmer 1.8s linear infinite;
        }}

        @keyframes shimmer {{
            0% {{ background-position: 100% 0; }}
            100% {{ background-position: -100% 0; }}
        }}

        .progress-text {{
            font-size: 13px;
            font-weight: 800;
            color: #543847;
            margin-top: 6px;
        }}

        .status-msg {{
            font-size: 14px;
            font-weight: 700;
            color: #705864;
            min-height: 20px;
            margin-bottom: 4px;
        }}

        .footer-note {{
            font-size: 11px;
            color: #8c7b83;
            margin-top: 14px;
            font-weight: 600;
        }}

        /* Hidden default elements */
        #transfer, #status, #progress, #infobox, #crt {{
            display: none !important;
        }}

        /* Canvas sizing */
        canvas.emscripten {{
            border: 0px none;
            background-color: transparent;
            width: 100%;
            height: 100%;
            z-index: 5;
            padding: 0;
            margin: 0 auto;
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            right: 0;
        }}
    </style>

    <script src="{{{{cookiecutter.cdn}}}}/browserfs.min.js"></script>
</head>

<body>
    <!-- Animated Sky Background -->
    <div class="sky-bg">
        <div class="cloud cloud-1"></div>
        <div class="cloud cloud-2"></div>
        <div class="cloud cloud-3"></div>
    </div>

    <!-- Polished Flappy Bird Loading UI -->
    <div id="loading-overlay">
        <div class="loading-card" id="interactive-card">
            <div class="bird-anim"></div>
            <h1 class="game-title">FLAPPY BIRD</h1>
            <div class="game-subtitle">Web Edition</div>

            <div class="status-msg" id="custom-status">Loading assets...</div>

            <div class="progress-wrapper">
                <div class="progress-track">
                    <div class="progress-fill" id="custom-progress-bar"></div>
                </div>
                <div class="progress-text" id="custom-progress-num">15%</div>
            </div>

            <div class="footer-note">Powered by Python &amp; Pygame-ce</div>
        </div>
    </div>

    <!-- Hidden compatibility elements required by pygbag -->
    <div id="transfer"><div id="status"></div><progress id="progress"></progress></div>
    <div id="infobox"></div>

    <!-- Game Canvas -->
    <canvas class="emscripten" id="canvas" width="1px" height="1px" oncontextmenu="event.preventDefault()" tabindex=1></canvas>
    <canvas class="emscripten" id="canvas3d" width="{{{{cookiecutter.width}}}}px" height="{{{{cookiecutter.height}}}}px" oncontextmenu="event.preventDefault()" tabindex=1 hidden></canvas>

    <script>
        let currentProgress = 15;
        const progressBar = document.getElementById('custom-progress-bar');
        const progressNum = document.getElementById('custom-progress-num');
        const statusMsg = document.getElementById('custom-status');
        const overlay = document.getElementById('loading-overlay');

        // Smoothly advance progress
        const milestones = [
            {{ pct: 28, text: "Downloading WebAssembly..." }},
            {{ pct: 45, text: "Extracting game assets..." }},
            {{ pct: 68, text: "Compiling Python bytecode..." }},
            {{ pct: 88, text: "Initializing Pygame engine..." }},
            {{ pct: 98, text: "Ready to fly!" }}
        ];

        let mIdx = 0;
        const progressTimer = setInterval(() => {{
            if (mIdx < milestones.length) {{
                currentProgress = Math.min(milestones[mIdx].pct, currentProgress + 4);
                if (progressBar) progressBar.style.width = currentProgress + '%';
                if (progressNum) progressNum.innerText = currentProgress + '%';
                if (statusMsg) statusMsg.innerText = milestones[mIdx].text;
                if (currentProgress >= milestones[mIdx].pct) mIdx++;
            }}
        }}, 220);

        // Click/tap anywhere on card or window to trigger UME
        document.addEventListener('pointerdown', function() {{
            if (window.MM) window.MM.UME = true;
        }}, {{ once: false }});

        window.hideLoadingScreen = function() {{
            clearInterval(progressTimer);
            if (progressBar) progressBar.style.width = '100%';
            if (progressNum) progressNum.innerText = '100%';
            if (statusMsg) statusMsg.innerText = 'Ready!';
            
            setTimeout(() => {{
                if (overlay) {{
                    overlay.style.opacity = '0';
                    overlay.style.transform = 'scale(1.04)';
                    overlay.style.pointerEvents = 'none';
                    setTimeout(() => {{
                        overlay.style.display = 'none';
                    }}, 500);
                }}
            }}, 150);
        }};
    </script>
</body>
</html>
"""
    for out_path in output_paths:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(template_content)
        print(f"Template written to {out_path}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = [
        os.path.join(base, "default.tmpl"),
        os.path.join(base, "build", "web-cache", "27613e24ba16d44f2a5c88150c6d64e5.tmpl")
    ]
    generate_template(targets)
