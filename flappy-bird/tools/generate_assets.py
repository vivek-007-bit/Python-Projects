import os
import math
import struct
import wave
import pygame

def generate_sounds(sounds_dir):
    import soundfile as sf
    import numpy as np
    sample_rate = 44100

    def write_ogg(filename, samples):
        path = os.path.join(sounds_dir, filename)
        arr = np.array(samples, dtype=np.float32)
        sf.write(path, arr, sample_rate, format='OGG', subtype='VORBIS')
        print(f"Generated {filename}")

    # 1. flap.ogg (0.12s quick rising chirp)
    duration = 0.12
    total_frames = int(sample_rate * duration)
    flap_samples = []
    for i in range(total_frames):
        t = i / sample_rate
        progress = i / total_frames
        freq = 300 + 450 * (progress ** 0.6)
        env = math.sin(progress * math.pi) ** 0.7
        val = env * math.sin(2 * math.pi * freq * t)
        flap_samples.append(val * 0.7)
    write_ogg("flap.ogg", flap_samples)

    # 2. point.ogg (0.28s two-tone chime)
    duration = 0.28
    total_frames = int(sample_rate * duration)
    point_samples = []
    for i in range(total_frames):
        t = i / sample_rate
        if t < 0.08:
            freq = 784.0  # G5
            env = (1.0 - (t / 0.08) * 0.2)
        else:
            freq = 1046.5 # C6
            t2 = t - 0.08
            env = math.exp(-t2 * 8.0)
        val = env * math.sin(2 * math.pi * freq * t)
        val += 0.3 * env * math.sin(4 * math.pi * freq * t)
        point_samples.append(val * 0.6)
    write_ogg("point.ogg", point_samples)

    # 3. hit.ogg (0.18s impact thud + crunch)
    import random
    duration = 0.18
    total_frames = int(sample_rate * duration)
    hit_samples = []
    rand = random.Random(42)
    for i in range(total_frames):
        t = i / sample_rate
        progress = i / total_frames
        freq = 240 * (1.0 - progress * 0.8)
        env = (1.0 - progress) ** 2
        tone = math.sin(2 * math.pi * freq * t)
        noise = (rand.random() * 2 - 1) * (0.6 if progress < 0.3 else 0.1)
        val = env * (0.7 * tone + 0.5 * noise)
        hit_samples.append(val * 0.8)
    write_ogg("hit.ogg", hit_samples)

    # 4. die.ogg (0.35s descending slide)
    duration = 0.35
    total_frames = int(sample_rate * duration)
    die_samples = []
    for i in range(total_frames):
        t = i / sample_rate
        progress = i / total_frames
        freq = 520 * (1.0 - progress * 0.75)
        env = (1.0 - progress) ** 1.5
        val = env * math.sin(2 * math.pi * freq * t)
        die_samples.append(val * 0.7)
    write_ogg("die.ogg", die_samples)

    # Remove legacy .wav files
    for wav_file in ["flap.wav", "point.wav", "hit.wav", "die.wav"]:
        wav_path = os.path.join(sounds_dir, wav_file)
        if os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"Removed legacy {wav_file}")

def generate_images(images_dir):
    pygame.init()

    # 1. background.png (400x700)
    bg = pygame.Surface((400, 700), pygame.SRCALPHA)
    # Sky gradient (Deep sky blue at top to soft light cyan near horizon)
    for y in range(700):
        factor = y / 700.0
        r = int(78 + (175 - 78) * factor)
        g = int(192 + (230 - 192) * factor)
        b = int(210 + (245 - 210) * factor)
        pygame.draw.line(bg, (r, g, b), (0, y), (400, y))

    # Distant mountains / cityscape
    city_color = (130, 205, 185, 200)
    building_rects = [
        (10, 480, 45, 120), (60, 450, 40, 150), (105, 490, 50, 110),
        (160, 430, 55, 170), (220, 470, 45, 130), (270, 440, 60, 160),
        (335, 460, 55, 140)
    ]
    for rx, ry, rw, rh in building_rects:
        pygame.draw.rect(bg, city_color, (rx, ry, rw, rh), border_top_left_radius=4, border_top_right_radius=4)
        # Windows
        for wx in range(rx + 6, rx + rw - 6, 12):
            for wy in range(ry + 10, ry + rh - 10, 16):
                pygame.draw.rect(bg, (230, 245, 220, 140), (wx, wy, 6, 8), border_radius=1)

    # Distant soft hills
    pygame.draw.circle(bg, (115, 200, 130), (80, 600), 120)
    pygame.draw.circle(bg, (100, 190, 115), (250, 610), 140)
    pygame.draw.circle(bg, (110, 195, 125), (380, 605), 110)

    # Fluffy decorative clouds
    def draw_cloud(surf, cx, cy, scale=1.0):
        cloud_color = (255, 255, 255, 220)
        pygame.draw.circle(surf, cloud_color, (int(cx), int(cy)), int(22 * scale))
        pygame.draw.circle(surf, cloud_color, (int(cx + 25 * scale), int(cy - 10 * scale)), int(28 * scale))
        pygame.draw.circle(surf, cloud_color, (int(cx + 55 * scale), int(cy - 6 * scale)), int(25 * scale))
        pygame.draw.circle(surf, cloud_color, (int(cx + 80 * scale), int(cy + 2 * scale)), int(18 * scale))
        pygame.draw.ellipse(surf, cloud_color, (int(cx - 5 * scale), int(cy - 2 * scale), int(95 * scale), int(30 * scale)))

    draw_cloud(bg, 40, 120, 1.1)
    draw_cloud(bg, 230, 80, 0.9)
    draw_cloud(bg, 160, 240, 0.7)
    draw_cloud(bg, 310, 310, 0.8)

    pygame.image.save(bg, os.path.join(images_dir, "background.png"))
    print("Generated background.png")

    # 2. ground.png (480x112 for seamless repeating scroll)
    ground_w, ground_h = 480, 112
    ground = pygame.Surface((ground_w, ground_h))
    ground.fill((222, 215, 150)) # base sand

    # Soil texture stripes
    for y in range(16, ground_h, 8):
        pygame.draw.line(ground, (210, 200, 135), (0, y), (ground_w, y), 2)

    # Diagonal dirt pattern
    for x in range(-50, ground_w + 50, 20):
        pygame.draw.line(ground, (190, 175, 110), (x, 18), (x + 30, ground_h), 4)

    # Top grass layer
    pygame.draw.rect(ground, (115, 190, 45), (0, 0, ground_w, 14))
    pygame.draw.rect(ground, (140, 215, 55), (0, 0, ground_w, 6)) # grass highlight
    pygame.draw.rect(ground, (85, 145, 30), (0, 14, ground_w, 3)) # grass shadow

    # Grass blade teeth
    for x in range(0, ground_w, 12):
        pts = [(x, 14), (x + 6, 20), (x + 12, 14)]
        pygame.draw.polygon(ground, (115, 190, 45), pts)
        pts_shadow = [(x + 2, 14), (x + 6, 20), (x + 10, 14)]
        pygame.draw.polygon(ground, (85, 145, 30), pts_shadow)

    pygame.image.save(ground, os.path.join(images_dir, "ground.png"))
    print("Generated ground.png")

    # 3. pipe.png (70x600 for top/bottom rendering)
    pipe_w, pipe_h = 70, 600
    pipe = pygame.Surface((pipe_w, pipe_h), pygame.SRCALPHA)
    # Pipe main body
    body_rect = (4, 0, 62, pipe_h)
    pygame.draw.rect(pipe, (115, 190, 45), body_rect)
    # Pipe vertical highlights and shadows
    pygame.draw.rect(pipe, (160, 230, 75), (8, 0, 8, pipe_h))   # bright shine
    pygame.draw.rect(pipe, (135, 210, 60), (16, 0, 12, pipe_h))  # light green
    pygame.draw.rect(pipe, (85, 145, 30), (52, 0, 10, pipe_h))   # shadow
    pygame.draw.rect(pipe, (55, 100, 20), (62, 0, 4, pipe_h))    # deep edge
    pygame.draw.rect(pipe, (35, 65, 15), body_rect, 3)           # dark outline

    # Pipe Cap (at top of sprite, height 36)
    cap_rect = (0, 0, 70, 36)
    pygame.draw.rect(pipe, (115, 190, 45), cap_rect, border_radius=3)
    pygame.draw.rect(pipe, (160, 230, 75), (4, 3, 10, 30), border_radius=2)  # cap highlight
    pygame.draw.rect(pipe, (85, 145, 30), (56, 3, 10, 30))                   # cap shadow
    pygame.draw.rect(pipe, (35, 65, 15), cap_rect, 3, border_radius=3)       # cap outline
    # Cap bottom lip shadow
    pygame.draw.line(pipe, (55, 100, 20), (3, 34), (67, 34), 2)

    pygame.image.save(pipe, os.path.join(images_dir, "pipe.png"))
    print("Generated pipe.png")

    # 4. bird frames (bird_up.png, bird_mid.png, bird_down.png, and bird.png)
    def draw_bird_frame(wing_pos):
        # wing_pos: 'up', 'mid', 'down'
        bw, bh = 46, 34
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)

        # Outer outline / body (golden yellow)
        # Main body ellipse
        body_rect = (4, 4, 34, 26)
        pygame.draw.ellipse(surf, (35, 35, 35), (2, 2, 38, 30)) # outline
        pygame.draw.ellipse(surf, (250, 190, 35), body_rect)    # base yellow
        # Belly highlight / gradient
        pygame.draw.ellipse(surf, (255, 225, 75), (8, 6, 26, 16)) # lighter top

        # Belly white patch
        pygame.draw.ellipse(surf, (245, 240, 220), (8, 16, 20, 12))

        # Eye
        pygame.draw.ellipse(surf, (35, 35, 35), (24, 6, 14, 15)) # eye outline
        pygame.draw.ellipse(surf, (255, 255, 255), (26, 7, 11, 13)) # eye white
        pygame.draw.circle(surf, (35, 35, 35), (33, 13), 3) # pupil
        pygame.draw.circle(surf, (255, 255, 255), (34, 11), 1) # pupil shine

        # Beak (orange with outline)
        beak_pts = [(33, 16), (44, 21), (33, 27)]
        pygame.draw.polygon(surf, (35, 35, 35), [(32, 14), (46, 21), (32, 29)])
        pygame.draw.polygon(surf, (245, 110, 30), beak_pts)
        pygame.draw.line(surf, (190, 70, 15), (33, 22), (43, 21), 2) # beak line

        # Cheerful rosy cheek
        pygame.draw.circle(surf, (250, 130, 90, 180), (22, 21), 4)

        # Wing
        if wing_pos == 'up':
            wing_pts = [(8, 16), (18, 5), (22, 16)]
            pygame.draw.polygon(surf, (35, 35, 35), [(6, 17), (18, 3), (24, 17)])
            pygame.draw.polygon(surf, (255, 255, 255), wing_pts)
            pygame.draw.polygon(surf, (230, 220, 210), [(10, 16), (18, 8), (21, 16)])
        elif wing_pos == 'mid':
            wing_rect = (6, 13, 18, 11)
            pygame.draw.ellipse(surf, (35, 35, 35), (5, 12, 20, 13))
            pygame.draw.ellipse(surf, (255, 255, 255), wing_rect)
            pygame.draw.ellipse(surf, (230, 220, 210), (8, 15, 14, 8))
        else: # 'down'
            wing_pts = [(8, 14), (18, 26), (22, 15)]
            pygame.draw.polygon(surf, (35, 35, 35), [(6, 13), (18, 28), (24, 14)])
            pygame.draw.polygon(surf, (255, 255, 255), wing_pts)
            pygame.draw.polygon(surf, (230, 220, 210), [(10, 15), (18, 23), (21, 15)])

        return surf

    bird_up = draw_bird_frame('up')
    bird_mid = draw_bird_frame('mid')
    bird_down = draw_bird_frame('down')

    pygame.image.save(bird_up, os.path.join(images_dir, "bird_up.png"))
    pygame.image.save(bird_mid, os.path.join(images_dir, "bird_mid.png"))
    pygame.image.save(bird_down, os.path.join(images_dir, "bird_down.png"))
    pygame.image.save(bird_mid, os.path.join(images_dir, "bird.png")) # default bird
    print("Generated bird sprite frames")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sounds_dir = os.path.join(base_dir, "game", "assets", "sounds")
    images_dir = os.path.join(base_dir, "game", "assets", "images")
    generate_sounds(sounds_dir)
    generate_images(images_dir)
