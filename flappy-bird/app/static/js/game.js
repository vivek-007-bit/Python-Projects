/**
 * ==============================================================================
 * Flappy Bird — Web-Native 60 FPS Canvas Game Engine
 * Recreated with exact Pygame physics, state machine, particle effects & medals.
 * ==============================================================================
 */

(function () {
    'use strict';

    // --- Logical Constants & Settings (Matching Pygame settings.py) ---
    const GAME_WIDTH = 400;
    const GAME_HEIGHT = 700;
    const FPS = 60;

    const GRAVITY = 0.42;
    const FLAP_STRENGTH = -8.2;
    const MAX_FALL_SPEED = 10.5;

    const PLAYER_START_X = 90;
    const PLAYER_START_Y = 290;
    const BIRD_WIDTH = 44;
    const BIRD_HEIGHT = 32;
    const BIRD_FLAP_ANIM_SPEED = 0.18;

    const GROUND_HEIGHT = 112;
    const GROUND_Y = GAME_HEIGHT - GROUND_HEIGHT; // 588
    const GROUND_SPEED = 3.0;
    const BG_SPEED = 0.6;

    const PIPE_WIDTH = 70;
    const PIPE_GAP = 175;
    const PIPE_SPEED = 3.0;
    const PIPE_MIN_TOP_HEIGHT = 80;
    const PIPE_MAX_TOP_HEIGHT = 350;
    const PIPE_SPAWN_DISTANCE = 230;

    const STATE_MENU = 'MENU';
    const STATE_PLAYING = 'PLAYING';
    const STATE_PAUSED = 'PAUSED';
    const STATE_GAME_OVER = 'GAME_OVER';

    const HIGH_SCORE_KEY = 'flappy_bird_high_score';

    // Color Palette
    const COLORS = {
        white: '#ffffff',
        black: '#000000',
        skyBlue: '#64c3dc',
        groundSand: '#ded796',
        grassGreen: '#73be2d',
        pipeGreen: '#73be2d',
        gold: '#ffd700',
        bronze: '#cd7f32',
        silver: '#c0c0c0',
        platinum: '#e5e4e2',
        cardBg: '#ebdcb9',
        cardBorder: '#735028',
        uiShadow: '#232d37',
        dangerRed: '#f5503c'
    };

    // --- Sound Manager (Web Audio API + HTML5 Audio Fallback) ---
    class SoundManager {
        constructor() {
            this.muted = false;
            this.audioCtx = null;
            this.sounds = {};
            this.audioBuffers = {};
            this.unlocked = false;

            const soundFiles = {
                flap: '/static/assets/sounds/flap.ogg',
                point: '/static/assets/sounds/point.ogg',
                hit: '/static/assets/sounds/hit.ogg',
                die: '/static/assets/sounds/die.ogg'
            };

            for (const [key, src] of Object.entries(soundFiles)) {
                const audio = new Audio();
                audio.src = src;
                audio.preload = 'auto';
                this.sounds[key] = audio;
            }

            this.initWebAudio();
        }

        initWebAudio() {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (AudioContext) {
                    this.audioCtx = new AudioContext();
                }
            } catch (e) {
                console.warn('Web Audio API not supported, using HTML5 Audio fallback.');
            }
        }

        unlock() {
            if (this.audioCtx && this.audioCtx.state === 'suspended') {
                this.audioCtx.resume();
            }
            this.unlocked = true;
        }

        play(name) {
            if (this.muted) return;
            this.unlock();

            const audio = this.sounds[name];
            if (audio) {
                try {
                    audio.currentTime = 0;
                    audio.volume = 0.7;
                    const playPromise = audio.play();
                    if (playPromise !== undefined) {
                        playPromise.catch(() => {
                            this.playSynthesizedFallback(name);
                        });
                    }
                } catch (e) {
                    this.playSynthesizedFallback(name);
                }
            } else {
                this.playSynthesizedFallback(name);
            }
        }

        playSynthesizedFallback(name) {
            if (this.muted || !this.audioCtx) return;
            try {
                const ctx = this.audioCtx;
                const now = ctx.currentTime;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);

                if (name === 'flap') {
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(320, now);
                    osc.frequency.exponentialRampToValueAtTime(640, now + 0.08);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
                    osc.start(now);
                    osc.stop(now + 0.08);
                } else if (name === 'point') {
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(580, now);
                    osc.frequency.setValueAtTime(880, now + 0.08);
                    gain.gain.setValueAtTime(0.35, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.22);
                    osc.start(now);
                    osc.stop(now + 0.22);
                } else if (name === 'hit') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(180, now);
                    osc.frequency.linearRampToValueAtTime(60, now + 0.12);
                    gain.gain.setValueAtTime(0.4, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.12);
                    osc.start(now);
                    osc.stop(now + 0.12);
                } else if (name === 'die') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(240, now);
                    osc.frequency.exponentialRampToValueAtTime(40, now + 0.28);
                    gain.gain.setValueAtTime(0.35, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.28);
                    osc.start(now);
                    osc.stop(now + 0.28);
                }
            } catch (e) {
                // Ignore audio synthesis errors
            }
        }

        toggleMute() {
            this.muted = !this.muted;
            return this.muted;
        }
    }

    // --- Particle System ---
    class Particle {
        constructor(x, y, vx, vy, size, color, lifetime, shrink = true, gravity = 0.0) {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.size = size;
            this.maxSize = size;
            this.color = color;
            this.lifetime = lifetime;
            this.maxLifetime = lifetime;
            this.shrink = shrink;
            this.gravity = gravity;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.vy += this.gravity;
            this.lifetime -= 1;
            if (this.shrink && this.maxLifetime > 0) {
                this.size = Math.max(0.5, this.maxSize * (this.lifetime / this.maxLifetime));
            }
        }

        get isAlive() {
            return this.lifetime > 0 && this.size > 0.4;
        }

        draw(ctx) {
            if (!this.isAlive) return;
            const alpha = Math.max(0, Math.min(1, this.lifetime / this.maxLifetime));
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    class FloatingText {
        constructor(text, x, y, color = COLORS.gold, lifetime = 35) {
            this.text = text;
            this.x = x;
            this.y = y;
            this.color = color;
            this.lifetime = lifetime;
            this.maxLifetime = lifetime;
        }

        update() {
            this.y -= 1.2;
            this.lifetime -= 1;
        }

        get isAlive() {
            return this.lifetime > 0;
        }

        draw(ctx) {
            if (!this.isAlive) return;
            const alpha = Math.max(0, Math.min(1, this.lifetime / this.maxLifetime));
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.font = 'bold 22px "Trebuchet MS", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            // Shadow
            ctx.fillStyle = '#000000';
            ctx.fillText(this.text, this.x + 2, this.y + 2);

            // Text
            ctx.fillStyle = this.color;
            ctx.fillText(this.text, this.x, this.y);
            ctx.restore();
        }
    }

    class ParticleManager {
        constructor() {
            this.particles = [];
            this.floatingTexts = [];
        }

        clear() {
            this.particles = [];
            this.floatingTexts = [];
        }

        emitFlap(x, y) {
            for (let i = 0; i < 4; i++) {
                const vx = -(Math.random() * 2.0 + 0.5);
                const vy = Math.random() * 2.0 + 0.5;
                const size = Math.random() * 3.0 + 3.0;
                const lifetime = Math.floor(Math.random() * 8) + 12;
                this.particles.push(new Particle(x - 12, y + 6, vx, vy, size, '#ffffff', lifetime, true));
            }
        }

        emitScore(x, y) {
            for (let i = 0; i < 12; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 3.5 + 2.0;
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const size = Math.random() * 2.5 + 2.5;
                const colors = [COLORS.gold, '#fff096', '#fff8c8'];
                const color = colors[Math.floor(Math.random() * colors.length)];
                const lifetime = Math.floor(Math.random() * 12) + 18;
                this.particles.push(new Particle(x, y, vx, vy, size, color, lifetime, true, 0.15));
            }
            this.floatingTexts.push(new FloatingText('+1', x, y - 10, COLORS.gold, 35));
        }

        emitDeath(x, y) {
            const colors = ['#ffc823', '#f08c1e', '#ffffff', '#d23228'];
            for (let i = 0; i < 20; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 4.0 + 2.0;
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const size = Math.random() * 3.5 + 3.0;
                const color = colors[Math.floor(Math.random() * colors.length)];
                const lifetime = Math.floor(Math.random() * 18) + 20;
                this.particles.push(new Particle(x, y, vx, vy, size, color, lifetime, true, 0.2));
            }
        }

        update() {
            for (let i = this.particles.length - 1; i >= 0; i--) {
                const p = this.particles[i];
                p.update();
                if (!p.isAlive) this.particles.splice(i, 1);
            }

            for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
                const ft = this.floatingTexts[i];
                ft.update();
                if (!ft.isAlive) this.floatingTexts.splice(i, 1);
            }
        }

        draw(ctx) {
            for (const p of this.particles) p.draw(ctx);
            for (const ft of this.floatingTexts) ft.draw(ctx);
        }
    }

    // --- Bird (Player) Class ---
    class Bird {
        constructor(images) {
            this.images = images;
            this.startX = PLAYER_START_X;
            this.startY = PLAYER_START_Y;
            this.x = this.startX;
            this.y = this.startY;
            this.width = BIRD_WIDTH;
            this.height = BIRD_HEIGHT;
            this.velY = 0.0;
            this.angle = 0.0;
            this.targetAngle = 0.0;

            this.isAlive = true;
            this.hoverTimer = 0.0;
            this.animFrame = 0.0;

            this.frames = [images.birdUp, images.birdMid, images.birdDown];
        }

        reset() {
            this.x = this.startX;
            this.y = this.startY;
            this.velY = 0.0;
            this.angle = 0.0;
            this.targetAngle = 0.0;
            this.isAlive = true;
            this.hoverTimer = 0.0;
            this.animFrame = 0.0;
        }

        flap() {
            if (!this.isAlive) return false;
            this.velY = FLAP_STRENGTH;
            this.targetAngle = 28.0;
            this.angle = 28.0;
            return true;
        }

        updateHover() {
            this.hoverTimer += 0.08;
            this.y = this.startY + Math.sin(this.hoverTimer) * 6.5;
            this.angle = Math.sin(this.hoverTimer) * 4.0;
            this.animFrame = (this.animFrame + BIRD_FLAP_ANIM_SPEED) % this.frames.length;
        }

        update() {
            // Gravity
            this.velY += GRAVITY;
            if (this.velY > MAX_FALL_SPEED) {
                this.velY = MAX_FALL_SPEED;
            }

            this.y += this.velY;

            // Ceiling clamp
            if (this.y < -15) {
                this.y = -15;
                this.velY = Math.max(0.0, this.velY);
            }

            // Ground clamp
            if (this.y + this.height >= GROUND_Y) {
                this.y = GROUND_Y - this.height;
                this.velY = 0.0;
                if (this.isAlive) {
                    this.isAlive = false;
                }
            }

            // Smooth rotation physics
            if (this.velY < 0) {
                this.targetAngle = 25.0;
                this.angle += (this.targetAngle - this.angle) * 0.25;
            } else {
                this.targetAngle = Math.max(-85.0, -this.velY * 11.0);
                this.angle += (this.targetAngle - this.angle) * 0.12;
            }

            // Wing animation
            if (this.isAlive) {
                this.animFrame = (this.animFrame + BIRD_FLAP_ANIM_SPEED) % this.frames.length;
            } else {
                this.animFrame = 1.0; // Freeze on mid frame
            }
        }

        getHitbox() {
            const insetX = 6;
            const insetY = 5;
            return {
                x: this.x + insetX,
                y: this.y + insetY,
                width: this.width - insetX * 2,
                height: this.height - insetY * 2
            };
        }

        draw(ctx) {
            const currentImg = this.frames[Math.floor(this.animFrame)] || this.images.birdMid;
            ctx.save();
            ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
            // Invert angle for Canvas coordinate system (-tilt in degrees)
            ctx.rotate((-this.angle * Math.PI) / 180);
            if (currentImg && currentImg.complete && currentImg.naturalWidth > 0) {
                ctx.drawImage(currentImg, -this.width / 2, -this.height / 2, this.width, this.height);
            } else {
                // Procedural fallback
                ctx.fillStyle = '#ffc823';
                ctx.beginPath();
                ctx.ellipse(0, 0, this.width / 2, this.height / 2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }
    }

    // --- Pipe Pair Class ---
    class PipePair {
        constructor(x, topHeight, pipeImg, gap = PIPE_GAP) {
            this.x = x;
            this.topHeight = topHeight;
            this.gap = gap;
            this.width = PIPE_WIDTH;
            this.speed = PIPE_SPEED;
            this.passed = false;
            this.pipeImg = pipeImg;

            this.bottomY = this.topHeight + this.gap;
            this.bottomHeight = GROUND_Y - this.bottomY;
        }

        update() {
            this.x -= this.speed;
        }

        get isOffscreen() {
            return this.x + this.width < -10;
        }

        collidesWith(hitbox) {
            const insetX = 2; // Inflate(-4, 0)
            const topBox = {
                x: this.x + insetX,
                y: 0,
                width: this.width - insetX * 2,
                height: this.topHeight
            };
            const bottomBox = {
                x: this.x + insetX,
                y: this.bottomY,
                width: this.width - insetX * 2,
                height: this.bottomHeight
            };

            const rectIntersect = (r1, r2) => {
                return (
                    r1.x < r2.x + r2.width &&
                    r1.x + r1.width > r2.x &&
                    r1.y < r2.y + r2.height &&
                    r1.y + r1.height > r2.y
                );
            };

            return rectIntersect(topBox, hitbox) || rectIntersect(bottomBox, hitbox);
        }

        checkPassed(playerX) {
            if (!this.passed && playerX > this.x + this.width / 2) {
                this.passed = true;
                return true;
            }
            return false;
        }

        draw(ctx) {
            if (this.pipeImg && this.pipeImg.complete && this.pipeImg.naturalWidth > 0) {
                const imgH = this.pipeImg.height || 500;
                // Draw Top Pipe (inverted/flipped vertically)
                ctx.save();
                ctx.translate(this.x + this.width / 2, this.topHeight);
                ctx.scale(1, -1);
                ctx.drawImage(this.pipeImg, -this.width / 2, 0, this.width, imgH);
                ctx.restore();

                // Draw Bottom Pipe
                ctx.drawImage(this.pipeImg, this.x, this.bottomY, this.width, imgH);
            } else {
                // Procedural Pipe fallback
                ctx.fillStyle = COLORS.pipeGreen;
                ctx.strokeStyle = '#23410f';
                ctx.lineWidth = 3;

                // Top
                ctx.fillRect(this.x, 0, this.width, this.topHeight);
                ctx.strokeRect(this.x, 0, this.width, this.topHeight);

                // Bottom
                ctx.fillRect(this.x, this.bottomY, this.width, this.bottomHeight);
                ctx.strokeRect(this.x, this.bottomY, this.width, this.bottomHeight);
            }
        }
    }

    // --- Pipe Manager Class ---
    class PipeManager {
        constructor(pipeImg) {
            this.pipeImg = pipeImg;
            this.pipes = [];
        }

        reset() {
            this.pipes = [];
        }

        spawnPipe(x = GAME_WIDTH + 60) {
            const topHeight = Math.floor(Math.random() * (PIPE_MAX_TOP_HEIGHT - PIPE_MIN_TOP_HEIGHT + 1)) + PIPE_MIN_TOP_HEIGHT;
            this.pipes.push(new PipePair(x, topHeight, this.pipeImg));
        }

        update(playerX) {
            if (this.pipes.length === 0) {
                this.spawnPipe(GAME_WIDTH + 60);
            } else {
                let rightmostX = -Infinity;
                for (const p of this.pipes) {
                    if (p.x > rightmostX) rightmostX = p.x;
                }
                if (rightmostX <= GAME_WIDTH + 60 - PIPE_SPAWN_DISTANCE) {
                    this.spawnPipe(GAME_WIDTH + 60);
                }
            }

            let scoreInc = 0;
            for (let i = this.pipes.length - 1; i >= 0; i--) {
                const pipe = this.pipes[i];
                pipe.update();
                if (pipe.checkPassed(playerX)) {
                    scoreInc++;
                }
                if (pipe.isOffscreen) {
                    this.pipes.splice(i, 1);
                }
            }

            return scoreInc;
        }

        checkCollision(birdHitbox) {
            for (const pipe of this.pipes) {
                if (pipe.collidesWith(birdHitbox)) {
                    return true;
                }
            }
            return false;
        }

        draw(ctx) {
            for (const pipe of this.pipes) {
                pipe.draw(ctx);
            }
        }
    }

    // --- Core Flappy Bird Game Engine ---
    class FlappyBirdEngine {
        constructor(canvas, loadingOverlay, loadingBar, loadingText) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.loadingOverlay = loadingOverlay;
            this.loadingBar = loadingBar;
            this.loadingText = loadingText;

            this.images = {};
            this.sound = new SoundManager();
            this.particles = new ParticleManager();

            this.state = STATE_MENU;
            this.score = 0;
            this.bestScore = this.loadHighScore();
            this.isNewHighScore = false;

            this.bgX = 0.0;
            this.groundX = 0.0;
            this.scoreScaleTimer = 0;
            this.screenShake = 0;
            this.flashAlpha = 0;
            this.menuPulseTimer = 0.0;
            this.gameOverTimer = 0;

            // UI Button hitboxes (in logical 400x700 coordinates)
            this.btnSound = { x: GAME_WIDTH - 48, y: 16, width: 34, height: 34 };
            this.btnPause = { x: 14, y: 16, width: 34, height: 34 };

            this.initAssetsAndStart();
        }

        loadHighScore() {
            try {
                const stored = localStorage.getItem(HIGH_SCORE_KEY);
                return stored ? parseInt(stored, 10) || 0 : 0;
            } catch (e) {
                return 0;
            }
        }

        saveHighScore() {
            try {
                localStorage.setItem(HIGH_SCORE_KEY, this.bestScore.toString());
            } catch (e) {
                // Ignore storage errors
            }
        }

        initAssetsAndStart() {
            const assetList = [
                { key: 'background', src: '/static/assets/images/background.png' },
                { key: 'ground', src: '/static/assets/images/ground.png' },
                { key: 'pipe', src: '/static/assets/images/pipe.png' },
                { key: 'bird', src: '/static/assets/images/bird.png' },
                { key: 'birdUp', src: '/static/assets/images/bird_up.png' },
                { key: 'birdMid', src: '/static/assets/images/bird_mid.png' },
                { key: 'birdDown', src: '/static/assets/images/bird_down.png' }
            ];

            let loadedCount = 0;
            const totalAssets = assetList.length;

            const onAssetLoad = () => {
                loadedCount++;
                const pct = Math.floor((loadedCount / totalAssets) * 100);
                if (this.loadingBar) this.loadingBar.style.width = `${pct}%`;
                if (this.loadingText) this.loadingText.innerText = `Loading sprites (${loadedCount}/${totalAssets})...`;

                if (loadedCount >= totalAssets) {
                    this.onAllAssetsReady();
                }
            };

            for (const item of assetList) {
                const img = new Image();
                img.onload = onAssetLoad;
                img.onerror = () => {
                    console.warn(`Failed to load sprite: ${item.src}, using procedural fallback.`);
                    onAssetLoad();
                };
                img.src = item.src;
                this.images[item.key] = img;
            }
        }

        onAllAssetsReady() {
            this.bird = new Bird(this.images);
            this.pipeManager = new PipeManager(this.images.pipe);

            // Hide loading overlay smoothly
            setTimeout(() => {
                if (this.loadingOverlay) {
                    this.loadingOverlay.style.opacity = '0';
                    this.loadingOverlay.style.transform = 'scale(1.04)';
                    setTimeout(() => {
                        this.loadingOverlay.style.display = 'none';
                    }, 350);
                }
            }, 100);

            this.setupInputListeners();
            this.lastTimestamp = performance.now();
            requestAnimationFrame((ts) => this.gameLoop(ts));
        }

        setupInputListeners() {
            // Keyboard controls
            window.addEventListener('keydown', (e) => {
                if (e.code === 'Space' || e.key === ' ' || e.code === 'ArrowUp') {
                    e.preventDefault();
                    this.triggerFlap();
                } else if (e.code === 'KeyP' || e.key === 'p' || e.key === 'P' || e.code === 'Escape') {
                    e.preventDefault();
                    this.togglePause();
                } else if (e.code === 'KeyM' || e.key === 'm' || e.key === 'M') {
                    e.preventDefault();
                    this.sound.toggleMute();
                }
            });

            // Pointer / Touch / Click mapping to logical 400x700 coordinates
            const handlePointer = (e) => {
                this.sound.unlock();
                const rect = this.canvas.getBoundingClientRect();
                const scaleX = GAME_WIDTH / rect.width;
                const scaleY = GAME_HEIGHT / rect.height;

                const lx = (e.clientX - rect.left) * scaleX;
                const ly = (e.clientY - rect.top) * scaleY;

                // Check Sound button click
                if (
                    lx >= this.btnSound.x &&
                    lx <= this.btnSound.x + this.btnSound.width &&
                    ly >= this.btnSound.y &&
                    ly <= this.btnSound.y + this.btnSound.height
                ) {
                    this.sound.toggleMute();
                    return;
                }

                // Check Pause button click
                if (this.state === STATE_PLAYING || this.state === STATE_PAUSED) {
                    if (
                        lx >= this.btnPause.x &&
                        lx <= this.btnPause.x + this.btnPause.width &&
                        ly >= this.btnPause.y &&
                        ly <= this.btnPause.y + this.btnPause.height
                    ) {
                        this.togglePause();
                        return;
                    }
                }

                if (this.state === STATE_PAUSED) {
                    this.togglePause();
                } else {
                    this.triggerFlap();
                }
            };

            this.canvas.addEventListener('pointerdown', handlePointer);
        }

        resetGame() {
            this.bird.reset();
            this.pipeManager.reset();
            this.particles.clear();
            this.score = 0;
            this.isNewHighScore = false;
            this.flashAlpha = 0;
            this.screenShake = 0;
            this.scoreScaleTimer = 0;
            this.gameOverTimer = 0;
        }

        triggerFlap() {
            if (this.state === STATE_MENU) {
                this.state = STATE_PLAYING;
                this.resetGame();
                if (this.bird.flap()) {
                    this.sound.play('flap');
                    this.particles.emitFlap(this.bird.x, this.bird.y + this.bird.height / 2);
                }
            } else if (this.state === STATE_PLAYING) {
                if (this.bird.flap()) {
                    this.sound.play('flap');
                    this.particles.emitFlap(this.bird.x, this.bird.y + this.bird.height / 2);
                }
            } else if (this.state === STATE_GAME_OVER) {
                // Safety debounce of 25 frames
                if (this.gameOverTimer > 25) {
                    this.state = STATE_PLAYING;
                    this.resetGame();
                    if (this.bird.flap()) {
                        this.sound.play('flap');
                        this.particles.emitFlap(this.bird.x, this.bird.y + this.bird.height / 2);
                    }
                }
            }
        }

        togglePause() {
            if (this.state === STATE_PLAYING) {
                this.state = STATE_PAUSED;
            } else if (this.state === STATE_PAUSED) {
                this.state = STATE_PLAYING;
            }
        }

        handleGameOver(hitGround) {
            this.state = STATE_GAME_OVER;
            this.bird.isAlive = false;
            this.screenShake = 10;
            this.flashAlpha = 180;
            this.particles.emitDeath(this.bird.x + this.bird.width / 2, this.bird.y + this.bird.height / 2);

            this.sound.play('hit');
            if (!hitGround) {
                this.sound.play('die');
            }

            if (this.score > this.bestScore) {
                this.bestScore = this.score;
                this.isNewHighScore = true;
                this.saveHighScore();
            }
        }

        update() {
            this.menuPulseTimer += 0.06;

            // Decay visual polish effects
            if (this.screenShake > 0) this.screenShake -= 1;
            if (this.flashAlpha > 0) this.flashAlpha = Math.max(0, this.flashAlpha - 18);
            if (this.scoreScaleTimer > 0) this.scoreScaleTimer -= 1;

            if (this.state === STATE_MENU) {
                this.bird.updateHover();
                const groundWidth = this.images.ground?.width || 480;
                this.groundX = (this.groundX + GROUND_SPEED) % groundWidth;
                this.bgX = (this.bgX + BG_SPEED) % GAME_WIDTH;
            } else if (this.state === STATE_PLAYING) {
                const groundWidth = this.images.ground?.width || 480;
                this.groundX = (this.groundX + GROUND_SPEED) % groundWidth;
                this.bgX = (this.bgX + BG_SPEED) % GAME_WIDTH;

                this.bird.update();

                const scoreInc = this.pipeManager.update(this.bird.x);
                if (scoreInc > 0) {
                    this.score += scoreInc;
                    this.sound.play('point');
                    this.particles.emitScore(this.bird.x + this.bird.width / 2, this.bird.y);
                    this.scoreScaleTimer = 12;

                    if (this.score > this.bestScore) {
                        this.bestScore = this.score;
                        this.isNewHighScore = true;
                        this.saveHighScore();
                    }
                }

                // Collisions
                const birdHitbox = this.bird.getHitbox();
                const hitPipe = this.pipeManager.checkCollision(birdHitbox);
                const hitGround = this.bird.y + this.bird.height >= GROUND_Y;

                if (hitPipe || hitGround) {
                    this.handleGameOver(hitGround);
                }

                this.particles.update();
            } else if (this.state === STATE_GAME_OVER) {
                this.gameOverTimer += 1;
                if (this.bird.y + this.bird.height < GROUND_Y) {
                    this.bird.update();
                }
                this.particles.update();
            }
        }

        drawTextWithShadow(text, font, color, x, y, shadowColor = '#000000', offsetX = 2, offsetY = 2, align = 'center') {
            const ctx = this.ctx;
            ctx.save();
            ctx.font = font;
            ctx.textAlign = align;
            ctx.textBaseline = 'middle';

            // Shadow
            ctx.fillStyle = shadowColor;
            ctx.fillText(text, x + offsetX, y + offsetY);

            // Foreground Text
            ctx.fillStyle = color;
            ctx.fillText(text, x, y);
            ctx.restore();
        }

        draw() {
            const ctx = this.ctx;
            ctx.save();

            // 1. Screen Shake
            let shakeX = 0;
            let shakeY = 0;
            if (this.screenShake > 0) {
                shakeX = (Math.random() - 0.5) * 2 * this.screenShake;
                shakeY = (Math.random() - 0.5) * 2 * this.screenShake;
                ctx.translate(shakeX, shakeY);
            }

            // 2. Parallax Sky Background
            if (this.images.background && this.images.background.complete) {
                ctx.drawImage(this.images.background, -this.bgX, 0, GAME_WIDTH, GAME_HEIGHT);
                ctx.drawImage(this.images.background, GAME_WIDTH - this.bgX, 0, GAME_WIDTH, GAME_HEIGHT);
            } else {
                ctx.fillStyle = COLORS.skyBlue;
                ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
            }

            // 3. Pipes
            this.pipeManager.draw(ctx);

            // 4. Scrolling Ground
            const gw = this.images.ground?.width || 480;
            if (this.images.ground && this.images.ground.complete) {
                ctx.drawImage(this.images.ground, -this.groundX, GROUND_Y, gw, GROUND_HEIGHT);
                ctx.drawImage(this.images.ground, gw - this.groundX, GROUND_Y, gw, GROUND_HEIGHT);
                ctx.drawImage(this.images.ground, gw * 2 - this.groundX, GROUND_Y, gw, GROUND_HEIGHT);
            } else {
                ctx.fillStyle = COLORS.groundSand;
                ctx.fillRect(0, GROUND_Y, GAME_WIDTH, GROUND_HEIGHT);
                ctx.fillStyle = COLORS.grassGreen;
                ctx.fillRect(0, GROUND_Y, GAME_WIDTH, 14);
            }

            // 5. Particles
            this.particles.draw(ctx);

            // 6. Bird
            this.bird.draw(ctx);

            // 7. UI Overlays by State
            if (this.state === STATE_MENU) {
                this.drawMenu();
            } else if (this.state === STATE_PLAYING) {
                this.drawPlayingUI();
            } else if (this.state === STATE_PAUSED) {
                this.drawPlayingUI();
                this.drawPausedUI();
            } else if (this.state === STATE_GAME_OVER) {
                this.drawGameOverUI();
            }

            // 8. Hit Flash Overlay
            if (this.flashAlpha > 0) {
                ctx.fillStyle = `rgba(255, 255, 255, ${this.flashAlpha / 255})`;
                ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
            }

            // 9. Top Controls (Sound & Pause)
            this.drawTopButtons();

            ctx.restore();
        }

        drawTopButtons() {
            const ctx = this.ctx;

            // Sound button
            this.drawRoundedRect(this.btnSound.x, this.btnSound.y, this.btnSound.width, this.btnSound.height, 8, '#19232d', COLORS.white, 2);
            const sx = this.btnSound.x + this.btnSound.width / 2;
            const sy = this.btnSound.y + this.btnSound.height / 2;

            // Speaker cone
            ctx.fillStyle = COLORS.white;
            ctx.beginPath();
            ctx.moveTo(sx - 8, sy - 4);
            ctx.lineTo(sx - 4, sy - 4);
            ctx.lineTo(sx + 2, sy - 9);
            ctx.lineTo(sx + 2, sy + 9);
            ctx.lineTo(sx - 4, sy + 4);
            ctx.lineTo(sx - 8, sy + 4);
            ctx.closePath();
            ctx.fill();

            if (this.sound.muted) {
                // Red slash
                ctx.strokeStyle = '#eb3c3c';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(sx - 9, sy - 9);
                ctx.lineTo(sx + 9, sy + 9);
                ctx.stroke();
            } else {
                // Sound waves
                ctx.strokeStyle = COLORS.white;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(sx + 1, sy, 7, -Math.PI / 3, Math.PI / 3, false);
                ctx.stroke();
            }

            // Pause button (visible in PLAYING & PAUSED)
            if (this.state === STATE_PLAYING || this.state === STATE_PAUSED) {
                this.drawRoundedRect(this.btnPause.x, this.btnPause.y, this.btnPause.width, this.btnPause.height, 8, '#19232d', COLORS.white, 2);
                const px = this.btnPause.x + this.btnPause.width / 2;
                const py = this.btnPause.y + this.btnPause.height / 2;

                if (this.state === STATE_PAUSED) {
                    // Play triangle
                    ctx.fillStyle = COLORS.white;
                    ctx.beginPath();
                    ctx.moveTo(px - 4, py - 7);
                    ctx.lineTo(px + 6, py);
                    ctx.lineTo(px - 4, py + 7);
                    ctx.closePath();
                    ctx.fill();
                } else {
                    // Double bar
                    ctx.fillStyle = COLORS.white;
                    ctx.fillRect(px - 6, py - 6, 4, 12);
                    ctx.fillRect(px + 2, py - 6, 4, 12);
                }
            }
        }

        drawRoundedRect(x, y, w, h, radius, fill, stroke, strokeWidth = 1) {
            const ctx = this.ctx;
            ctx.beginPath();
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + w - radius, y);
            ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
            ctx.lineTo(x + w, y + h - radius);
            ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
            ctx.lineTo(x + radius, y + h);
            ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
            ctx.lineTo(x, y + radius);
            ctx.quadraticCurveTo(x, y, x + radius, y);
            ctx.closePath();

            if (fill) {
                ctx.fillStyle = fill;
                ctx.fill();
            }
            if (stroke) {
                ctx.strokeStyle = stroke;
                ctx.lineWidth = strokeWidth;
                ctx.stroke();
            }
        }

        drawMenu() {
            const titleY = 150 + Math.sin(this.menuPulseTimer) * 4;
            this.drawTextWithShadow('FLAPPY BIRD', '900 48px "Trebuchet MS", sans-serif', COLORS.gold, GAME_WIDTH / 2, titleY, '#321e00', 3, 3);

            if (this.bestScore > 0) {
                this.drawRoundedRect(GAME_WIDTH / 2 - 70, 360, 140, 32, 16, '#19232d', COLORS.gold, 2);
                this.drawTextWithShadow(`BEST: ${this.bestScore}`, 'bold 18px "Trebuchet MS", sans-serif', COLORS.white, GAME_WIDTH / 2, 376, '#000000', 1, 1);
            }

            const pulseAlpha = (180 + 75 * Math.sin(this.menuPulseTimer * 2.5)) / 255;
            this.ctx.save();
            this.ctx.globalAlpha = pulseAlpha;
            this.drawTextWithShadow('TAP / PRESS SPACE', 'bold 24px "Trebuchet MS", sans-serif', COLORS.white, GAME_WIDTH / 2, 440, '#000000', 2, 2);
            this.ctx.restore();

            this.drawTextWithShadow('Desktop: Space / Up / Click', '18px "Trebuchet MS", sans-serif', '#f0f0f0', GAME_WIDTH / 2, 490, '#000000', 1, 1);
            this.drawTextWithShadow('Mobile: Tap Anywhere', '18px "Trebuchet MS", sans-serif', '#f0f0f0', GAME_WIDTH / 2, 514, '#000000', 1, 1);
            this.drawTextWithShadow('P: Pause | M: Mute', '18px "Trebuchet MS", sans-serif', '#dcdcdc', GAME_WIDTH / 2, 538, '#000000', 1, 1);
        }

        drawPlayingUI() {
            const scaleBonus = this.scoreScaleTimer > 0 ? 6 : 0;
            const fontSize = 54 + scaleBonus;
            this.drawTextWithShadow(this.score.toString(), `900 ${fontSize}px "Trebuchet MS", sans-serif`, COLORS.white, GAME_WIDTH / 2, 60, '#141e28', 3, 3);
        }

        drawPausedUI() {
            const ctx = this.ctx;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
            ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

            const cardX = GAME_WIDTH / 2 - 110;
            const cardY = GAME_HEIGHT / 2 - 80;
            this.drawRoundedRect(cardX, cardY, 220, 160, 12, COLORS.cardBg, COLORS.cardBorder, 4);

            this.drawTextWithShadow('PAUSED', 'bold 36px "Trebuchet MS", sans-serif', '#503214', GAME_WIDTH / 2, GAME_HEIGHT / 2 - 40, '#c8be96', 2, 2);
            this.drawTextWithShadow('Tap / Press P to Resume', '18px "Trebuchet MS", sans-serif', '#644628', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 10, '#ffffff', 1, 1);
            this.drawTextWithShadow(`Score: ${this.score}`, 'bold 24px "Trebuchet MS", sans-serif', '#3c280f', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 45, '#ffffff', 1, 1);
        }

        drawGameOverUI() {
            const ctx = this.ctx;

            // Banner GAME OVER
            this.drawTextWithShadow('GAME OVER', '900 48px "Trebuchet MS", sans-serif', '#f5503c', GAME_WIDTH / 2, 160, '#3c0f0a', 3, 3);

            // Score Card
            const cardW = 280;
            const cardH = 170;
            const cardX = (GAME_WIDTH - cardW) / 2;
            const cardY = 215;
            this.drawRoundedRect(cardX, cardY, cardW, cardH, 14, COLORS.cardBg, COLORS.cardBorder, 4);

            // Medal Section
            const medalCx = cardX + 58;
            const medalCy = cardY + cardH / 2 + 6;
            this.drawTextWithShadow('MEDAL', 'bold 18px "Trebuchet MS", sans-serif', '#785a3c', medalCx, cardY + 32, '#ffffff', 1, 1);

            let medalColor = null;
            if (this.score >= 40) medalColor = COLORS.platinum;
            else if (this.score >= 30) medalColor = COLORS.gold;
            else if (this.score >= 20) medalColor = COLORS.silver;
            else if (this.score >= 10) medalColor = COLORS.bronze;

            // Medal Socket
            ctx.fillStyle = '#b4a57d';
            ctx.beginPath();
            ctx.arc(medalCx, medalCy, 26, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.cardBorder;
            ctx.lineWidth = 3;
            ctx.stroke();

            if (medalColor) {
                ctx.fillStyle = medalColor;
                ctx.beginPath();
                ctx.arc(medalCx, medalCy, 23, 0, Math.PI * 2);
                ctx.fill();

                // Sparkle shine
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.beginPath();
                ctx.arc(medalCx - 6, medalCy - 6, 6, 0, Math.PI * 2);
                ctx.fill();
            }

            // Scores on Right
            const rightX = cardX + cardW - 54;
            this.drawTextWithShadow('SCORE', 'bold 18px "Trebuchet MS", sans-serif', '#966432', rightX, cardY + 28, '#ffffff', 1, 1);
            this.drawTextWithShadow(this.score.toString(), '900 36px "Trebuchet MS", sans-serif', '#32281e', rightX, cardY + 60, '#ffffff', 1, 1);

            this.drawTextWithShadow('BEST', 'bold 18px "Trebuchet MS", sans-serif', '#966432', rightX, cardY + 98, '#ffffff', 1, 1);
            this.drawTextWithShadow(this.bestScore.toString(), '900 36px "Trebuchet MS", sans-serif', '#32281e', rightX, cardY + 130, '#ffffff', 1, 1);

            // NEW High Score Badge
            if (this.isNewHighScore && this.score > 0) {
                this.drawRoundedRect(rightX - 62, cardY + 88, 38, 18, 4, '#f53c28', null, 0);
                this.drawTextWithShadow('NEW', 'bold 13px "Trebuchet MS", sans-serif', '#ffffff', rightX - 43, cardY + 97, '#3c0a0a', 1, 1);
            }

            // Pulsing Restart Button
            const pulseAlpha = (180 + 75 * Math.sin(this.menuPulseTimer * 3)) / 255;
            ctx.save();
            ctx.globalAlpha = pulseAlpha;
            this.drawTextWithShadow('TAP / SPACE TO RESTART', 'bold 22px "Trebuchet MS", sans-serif', COLORS.white, GAME_WIDTH / 2, 435, '#000000', 2, 2);
            ctx.restore();
        }

        gameLoop(timestamp) {
            this.update();
            this.draw();
            requestAnimationFrame((ts) => this.gameLoop(ts));
        }
    }

    // Initialize once DOM is ready
    window.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('game-canvas');
        const overlay = document.getElementById('loading-overlay');
        const bar = document.getElementById('loading-bar');
        const text = document.getElementById('loading-text');

        if (canvas) {
            window.flappyGame = new FlappyBirdEngine(canvas, overlay, bar, text);
        }
    });
})();
