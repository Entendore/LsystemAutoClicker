import pygame
import math
import colorsys
import time
import random
import json
import os
import numpy as np

# --- Configuration ---
WIDTH, HEIGHT = 1000, 800
FPS = 60
SAVE_FILE = "l_system_apex_save.json"
MAX_MORPH_SEGMENTS = 1500

# --- L-System Presets ---
L_SYSTEMS = {
    "1": {"name": "Bushy Tree", "axiom": "F", "rules": [{"F": "FF+[+F-F-F]-[-F+F+F]"}], "base_angle": 22.5, "base_length": 4.0, "max_safe_iter": 5, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT - 120)},
    "2": {"name": "Coral Blooms", "axiom": "F", "rules": [{"F": "F[+F][-F][+F]F"}], "base_angle": 25.0, "base_length": 5.0, "max_safe_iter": 4, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT - 120)},
    "3": {"name": "Crystal Matrix", "axiom": "F", "rules": [{"F": "F+F-F-F+F"}], "base_angle": 90.0, "base_length": 3.0, "max_safe_iter": 5, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT - 200)},
    "4": {"name": "Dragon Curve", "axiom": "FX", "rules": [{"X": "X+YF+", "Y": "-FX-Y"}], "base_angle": 90.0, "base_length": 5.0, "max_safe_iter": 12, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT // 2)},
    "5": {"name": "Barnsley Fern", "axiom": "X", "rules": [{"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}], "base_angle": 25.0, "base_length": 2.5, "max_safe_iter": 6, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT - 120)},
    "6": {"name": "Hilbert Curve", "axiom": "A", "rules": [{"A": "+BF-AFA-FB+", "B": "-AF+BFB+FA-"}], "base_angle": 90.0, "base_length": 12.0, "max_safe_iter": 6, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT // 2)},
    "7": {"name": "Gosper Curve", "axiom": "A", "rules": [{"A": "A-B--B+A++AA+B", "B": "+A-BB--B-A++A+B"}], "base_angle": 60.0, "base_length": 4.0, "max_safe_iter": 4, "draw_chars": ["A", "B"], "base_pos": (WIDTH // 3, HEIGHT // 2 + 100)},
    "8": {"name": "Koch Snowflake", "axiom": "F++F++F", "rules": [{"F": "F-F++F-F"}], "base_angle": 60.0, "base_length": 12.0, "max_safe_iter": 5, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT // 2 + 100)},
    "9": {"name": "Sierpinski Arrow", "axiom": "X", "rules": [{"X": "YF+XF+Y", "Y": "XF-YF-X"}], "base_angle": 60.0, "base_length": 10.0, "max_safe_iter": 6, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT // 2)},
    "0": {"name": "Pentigree", "axiom": "F-F-F-F-F", "rules": [{"F": "F-F--F-F"}], "base_angle": 72.0, "base_length": 8.0, "max_safe_iter": 5, "draw_chars": ["F"], "base_pos": (WIDTH // 3, HEIGHT // 2 + 100)}
}

# --- Color Palettes ---
PALETTES = [
    {"name": "Rainbow", "func": lambda h, s, v: colorsys.hsv_to_rgb(h, s, v)},
    {"name": "Inferno", "func": lambda h, s, v: colorsys.hsv_to_rgb((h * 0.15) % 1.0, s, v)},
    {"name": "Toxic", "func": lambda h, s, v: colorsys.hsv_to_rgb((h * 0.2 + 0.25) % 1.0, s, v)},
    {"name": "Cyberpunk", "func": lambda h, s, v: colorsys.hsv_to_rgb((h * 0.2 + 0.8) % 1.0, s, v)},
    {"name": "Mono", "func": lambda h, s, v: (v, v, v)}
]

# --- Helper Functions ---
def generate_l_system(axiom, rules_list, iterations):
    current_string = axiom
    for _ in range(iterations):
        next_string = ""
        for char in current_string:
            applied = False
            for rule_dict, prob in rules_list:
                if char in rule_dict and random.random() < prob:
                    next_string += rule_dict[char]
                    applied = True
                    break
            if not applied:
                next_string += char
        current_string = next_string
    return current_string

def format_number(num):
    if num < 1000: return str(int(num))
    elif num < 1_000_000: return f"{num/1000:.1f}K"
    elif num < 1_000_000_000: return f"{num/1_000_000:.1f}M"
    else: return f"{num/1_000_000_000:.1f}B"

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def ease_in_out_cubic(t):
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2)**3 / 2

def ease_out_elastic(t):
    if t == 0 or t == 1: return t
    return 2**(-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1

def get_palette_color(hue, sat=0.9, val=1.0):
    return PALETTES[current_palette_idx]["func"](hue, sat, val)

# --- Highly Complex Procedural Audio Generation ---
print("Initializing Audio Engine & Generating Complex Waveforms...")
def generate_sounds():
    sounds = {}
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        sr = 44100
        
        def to_stereo(wave):
            wave = np.clip(wave, -1, 1)
            stereo = np.column_stack((wave, wave))
            return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))
                
        # Click: Phase-distorted sine + noise transient
        t = np.linspace(0, 0.05, int(sr * 0.05))
        noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 100)
        phase = t * 1200
        pd_wave = np.sin(2 * np.pi * phase + 0.8 * np.sin(4 * np.pi * phase))
        wave = 0.4 * pd_wave * np.exp(-t * 60) + 0.3 * noise
        sounds['click'] = to_stereo(wave)
        
        # Passive: Soft triangle wave thud
        t = np.linspace(0, 0.15, int(sr * 0.15))
        tri = 2.0 * np.abs(2.0 * (t * 150 - np.floor(t * 150 + 0.5))) - 1.0
        wave = 0.4 * tri * np.exp(-t * 15)
        sounds['passive'] = to_stereo(wave)
        
        # Crit: 3-Operator FM Bass Drop + Comb-filtered noise burst
        t = np.linspace(0, 0.5, int(sr * 0.5))
        f_c = 80 + 120 * np.exp(-t * 8) 
        f_m1 = f_c * 2.0
        f_m2 = f_c * 4.0
        i_m1 = 5.0 * np.exp(-t * 5)
        i_m2 = 3.0 * np.exp(-t * 10)
        mod1 = i_m1 * np.sin(2 * np.pi * f_m1 * t + i_m2 * np.sin(2 * np.pi * f_m2 * t))
        fm_bass = 0.7 * np.sin(2 * np.pi * f_c * t + mod1) * np.exp(-t * 4)
        
        noise = np.random.uniform(-1, 1, len(t))
        d = int(sr * 0.01)
        comb = np.copy(noise)
        for i in range(d, len(noise)): comb[i] += comb[i-d] * 0.7
        noise_burst = 0.4 * comb * np.exp(-t * 15)
        sounds['crit'] = to_stereo(fm_bass + noise_burst)
        
        # Blossom: Additive Rhodes Piano + FM Bell
        t = np.linspace(0, 0.8, int(sr * 0.8))
        f = 660
        wave_add = np.zeros_like(t)
        for h, amp in [(1, 1.0), (2, 0.5), (3, 0.25), (4, 0.1)]:
            wave_add += amp * np.sin(2 * np.pi * (f * h) * t) * np.exp(-t * (4 + h))
        f_c = 880
        f_m = 1100
        i_f = 5 + 3 * np.exp(-t * 5)
        wave_fm = 0.3 * np.sin(2 * np.pi * f_c * t + i_f * np.sin(2 * np.pi * f_m * t)) * np.exp(-t * 3)
        sounds['blossom'] = to_stereo(wave_add + wave_fm)

        # Overdrive: Ascending Supersaw + Phaser LFO
        t = np.linspace(0, 0.8, int(sr * 0.8))
        f = 200 + 400 * t
        wave = np.zeros_like(t)
        for detune in [-0.5, -0.2, 0, 0.2, 0.5]:
            saw = 2.0 * (t * (f + detune) - np.floor(0.5 + t * (f + detune)))
            wave += 0.1 * saw
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 8 * t)
        wave = wave * lfo * np.exp(-t * 2)
        sounds['overdrive'] = to_stereo(wave)

        # Prestige: Shepard Tone (Descending) + Sub Bass + Resonant Noise
        t = np.linspace(0, 2.5, int(sr * 2.5))
        shepard = np.zeros_like(t)
        for octave in range(0, 7):
            f = 50 * (2**octave)
            env = np.exp(-((np.log2(f) - np.log2(200))**2) / 2.0)
            shepard += env * np.sin(2 * np.pi * f * t)
        shepard /= np.max(np.abs(shepard))
        sub = 0.6 * np.sin(2 * np.pi * 40 * t) * np.exp(-t * 1.5)
        noise = np.random.uniform(-1, 1, len(t))
        d = int(sr * 0.05)
        comb = np.copy(noise)
        for i in range(d, len(noise)): comb[i] += comb[i-d] * 0.6
        res_noise = 0.3 * comb * np.exp(-t * 2)
        sounds['prestige'] = to_stereo(shepard + sub + res_noise)
        
        # Morph: Granular Synthesis (Pitch sliding grains)
        duration = 1.5
        t_total = np.linspace(0, duration, int(sr * duration))
        out = np.zeros_like(t_total)
        grain_size = 0.04
        for i in range(0, int(duration / grain_size)):
            start = int(i * grain_size * sr)
            end = start + int(grain_size * sr)
            if end > len(out): break
            gt = np.linspace(0, grain_size, end - start)
            f = 300 + i * 40
            grain = 0.4 * np.sin(2 * np.pi * f * gt + 5 * np.sin(2 * np.pi * (f*1.5) * gt))
            grain *= np.sin(np.pi * gt / grain_size) 
            out[start:end] += grain
        sounds['morph'] = to_stereo(out)
        
        # Powerup: Major Chord Additive Synthesis
        t = np.linspace(0, 1.0, int(sr * 1.0))
        freqs = [261.6, 329.6, 392.0, 523.2]
        wave = np.zeros_like(t)
        for i, f in enumerate(freqs):
            start = i * 0.1
            mask = t >= start
            t_local = t - start
            pluck = np.zeros_like(t_local)
            for h, amp in [(1, 1.0), (2, 0.4), (3, 0.2)]:
                pluck += amp * np.sin(2 * np.pi * (f * h) * t_local)
            wave[mask] += 0.2 * pluck[mask] * np.exp(-t_local[mask] * 4)
        wave += 0.3 * np.sin(2 * np.pi * 130.8 * t) * np.exp(-t * 2)
        sounds['powerup'] = to_stereo(wave)
        
    except Exception as e:
        print(f"Audio disabled: {e}")
    return sounds

def generate_ambient_music(foam_level):
    print("Generating Evolving Ambient Soundscape (Phase Distortion, Supersaw, Comb Filters)...")
    try:
        sr = 44100
        duration = 16.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # 1. Deep Sub-Bass Drone (Additive: Sine + 3rd + 5th harmonic)
        bass_freq = 55.0 + foam_level * 2.0
        wave_bass = 0.3 * np.sin(2 * np.pi * bass_freq * t) + 0.15 * np.sin(2 * np.pi * (bass_freq * 3) * t) + 0.05 * np.sin(2 * np.pi * (bass_freq * 5) * t)
        
        # 2. Evolving Pad (Phase Distortion morphing Sine to Saw over time)
        f_c = 165.0 + foam_level * 5.0
        phase = t * f_c
        pd_amount = 0.4 + 0.4 * np.sin(2 * np.pi * (1/16) * t)
        distorted_phase = phase + pd_amount * np.sin(2 * np.pi * phase)
        wave_pad = 0.2 * np.sin(2 * np.pi * distorted_phase)
        
        # 3. Supersaw Shimmer (8 detuned saws, 4 Left / 4 Right)
        shimmer_freq = 440.0 + foam_level * 10.0
        wave_shimmer_L = np.zeros_like(t)
        wave_shimmer_R = np.zeros_like(t)
        detunes_L = [-0.7, -0.4, -0.1, 0.2]
        detunes_R = [0.7, 0.4, 0.1, -0.2]
        for dt_l, dt_r in zip(detunes_L, detunes_R):
            saw_l = 2.0 * (t * (shimmer_freq + dt_l) - np.floor(0.5 + t * (shimmer_freq + dt_l)))
            saw_r = 2.0 * (t * (shimmer_freq + dt_r) - np.floor(0.5 + t * (shimmer_freq + dt_r)))
            wave_shimmer_L += 0.02 * saw_l
            wave_shimmer_R += 0.02 * saw_r
        fast_trem = 0.5 + 0.5 * np.sin(2 * np.pi * 6.0 * t)
        wave_shimmer_L *= fast_trem
        wave_shimmer_R *= fast_trem
        
        # 4. Ambient Wind (Comb-filtered noise)
        noise = np.random.uniform(-1, 1, len(t))
        d = int(sr * 0.03)
        comb = np.copy(noise)
        for i in range(d, len(noise)): comb[i] += comb[i-d] * 0.5
        slow_lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t)
        wave_wind = 0.06 * comb * slow_lfo
        
        # 5. Arpeggiator (Stereo Panned, Additive Plucks)
        wave_pluck_L = np.zeros_like(t)
        wave_pluck_R = np.zeros_like(t)
        pluck_interval = 2.0
        num_plucks = int(duration / pluck_interval)
        pluck_notes = [261.6, 329.6, 392.0, 523.2, 659.2] # C Maj Pentatonic
        
        for i in range(num_plucks):
            pt = i * pluck_interval
            idx = int(pt * sr)
            if idx < len(t):
                pluck_t = t[:len(t)-idx]
                f = random.choice(pluck_notes) * (1.0 + foam_level * 0.02)
                
                # Additive pluck (3 harmonics)
                pluck = np.zeros_like(pluck_t)
                for h, amp in [(1, 1.0), (2, 0.4), (3, 0.2)]:
                    pluck += amp * np.sin(2 * np.pi * (f * h) * pluck_t)
                    
                decay = np.exp(-pluck_t * 5.0)
                pluck_signal = 0.12 * pluck * decay
                
                if random.random() > 0.5:
                    wave_pluck_L[idx:] += pluck_signal * 0.8
                    wave_pluck_R[idx:] += pluck_signal * 0.2
                else:
                    wave_pluck_L[idx:] += pluck_signal * 0.2
                    wave_pluck_R[idx:] += pluck_signal * 0.8
                    
        # Mix all layers
        wave_L = wave_bass + wave_pad + wave_shimmer_L + wave_wind + wave_pluck_L
        wave_R = wave_bass + wave_pad + wave_shimmer_R + wave_wind + wave_pluck_R
        
        # Master fade in/out for seamless looping
        fade = np.ones_like(t)
        fade_len = int(sr * 2.0)
        fade[:fade_len] = np.linspace(0, 1, fade_len)
        fade[-fade_len:] = np.linspace(1, 0, fade_len)
        
        wave_L = wave_L * fade
        wave_R = wave_R * fade
        
        wave_L = np.clip(wave_L, -1.0, 1.0)
        wave_R = np.clip(wave_R, -1.0, 1.0)
        
        stereo = np.column_stack((wave_L, wave_R))
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))
    except Exception as e:
        print(f"Music gen failed: {e}")
        return None

# --- Save/Load System ---
def save_game(state):
    data = {
        "total_clicks": state["total_clicks"],
        "upgrades": state["upgrades"],
        "current_l_system_key": state["current_l_system_key"],
        "quantum_foam": state["quantum_foam"],
        "achievements": state["achievements"],
        "stats": state["stats"],
        "current_palette_idx": state["current_palette_idx"],
        "save_time": time.time()
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except: pass
    return None

def get_default_upgrades():
    return {
        "cps": {"level": 1, "cost": 50, "cost_mult": 1.5},
        "iter": {"level": 3, "cost": 500, "cost_mult": 5.0, "max": 6},
        "scale": {"level": 0, "cost": 2000, "cost_mult": 4.0, "max": 5},
        "time_warp": {"level": 0, "cost": 1500, "cost_mult": 2.5, "max": 5},
        "passive": {"level": 0, "cost": 200, "cost_mult": 1.8},
        "mutagen": {"level": 0, "cost": 1000, "cost_mult": 3.0, "max": 5},
        "crit": {"level": 0, "cost": 800, "cost_mult": 2.0, "max": 5},
        "auto_od": {"level": 0, "cost": 5000, "cost_mult": 1.0, "max": 1},
        "auto_morph": {"level": 0, "cost": 3000, "cost_mult": 1.0, "max": 1},
        "morph_speed": {"level": 0, "cost": 800, "cost_mult": 1.5, "max": 5}
    }

def get_default_stats():
    return {
        "lifetime_clicks": 0,
        "lifetime_crits": 0,
        "total_morphs": 0,
        "time_played": 0.0
    }

# --- Pygame Setup ---
pygame.init()
SOUNDS = generate_sounds()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("L-System Autoclicker: Apex")
clock = pygame.time.Clock()
font_main = pygame.font.SysFont("Consolas", 22)
font_small = pygame.font.SysFont("Consolas", 16)
font_large = pygame.font.SysFont("Consolas", 28, bold=True)
font_mono = pygame.font.SysFont("Consolas", 14)

trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
particle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# --- Game State ---
running = True
is_clicking = False
last_click_time = 0
last_passive_time = 0
last_save_time = time.time()
last_orb_spawn = time.time()
next_orb_delay = random.uniform(15, 30)
auto_morph_timer = 0.0

click_effects = []
particles = []
floating_texts = []
golden_orbs = []
stars = []
matrix_drops = []
mouse_trail = []
active_blossoms = []

energy = 0
screen_shake = 0
quantum_foam = 0
is_overdriving = False
overdrive_timer = 0
prestige_confirm_timer = 0
current_bg = 0
current_palette_idx = 0

frenzy_timer = 0
auto_crit_timer = 0

ambient_sound = None
music_enabled = True

combo_timer = 0
combo_mult = 1.0

offline_earnings = 0
offline_popup_timer = 0

morph_active = False
morph_timer = 0.0
base_morph_duration = 2.5
old_l_system_key = "1"
target_l_system_key = "1"
old_poly = []
new_poly = []
bezier_ctrl = []
active_string = ""

achievements = {
    "first_click": {"name": "Genesis", "desc": "First Click", "unlocked": False},
    "1k_clicks": {"name": "Kilo-Clicker", "desc": "1,000 Total Clicks", "unlocked": False},
    "100k_clicks": {"name": "Fractal Master", "desc": "100,000 Total Clicks", "unlocked": False},
    "first_crit": {"name": "Critical Mass", "desc": "First Critical Click", "unlocked": False},
    "first_orb": {"name": "Gold Rush", "desc": "Click a Golden Orb", "unlocked": False},
    "first_blossom": {"name": "Green Thumb", "desc": "Harvest a Blossom", "unlocked": False},
    "first_od": {"name": "Ludicrous Speed", "desc": "Trigger Overdrive", "unlocked": False},
    "first_prestige": {"name": "Quantum Physicist", "desc": "Collapse Reality", "unlocked": False},
    "first_morph": {"name": "Shapeshifter", "desc": "Morph an L-System", "unlocked": False}
}
achievement_popup_timer = 0

for _ in range(150): stars.append({'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'z': random.uniform(0.2, 1.0), 'size': random.uniform(1, 3)})
for _ in range(40): matrix_drops.append({'x': random.randint(0, WIDTH), 'y': random.uniform(-HEIGHT, 0), 'speed': random.uniform(200, 500), 'len': random.randint(20, 50)})

upgrades = get_default_upgrades()
stats = get_default_stats()
total_clicks = 0
current_l_system_key = "1"
start_time = time.time()

saved_data = load_game()
if saved_data:
    total_clicks = saved_data.get("total_clicks", 0)
    current_l_system_key = saved_data.get("current_l_system_key", "1")
    target_l_system_key = current_l_system_key
    old_l_system_key = current_l_system_key
    quantum_foam = saved_data.get("quantum_foam", 0)
    current_palette_idx = saved_data.get("current_palette_idx", 0)
    loaded_up = saved_data.get("upgrades", {})
    for key in upgrades:
        if key in loaded_up:
            upgrades[key]["level"] = loaded_up[key]["level"]
            upgrades[key]["cost"] = loaded_up[key]["cost"]
    loaded_ach = saved_data.get("achievements", {})
    for key in achievements:
        if key in loaded_ach:
            achievements[key]["unlocked"] = loaded_ach[key]["unlocked"]
    loaded_stats = saved_data.get("stats", {})
    for key in stats:
        if key in loaded_stats:
            stats[key] = loaded_stats[key]
            
    save_time = saved_data.get("save_time", time.time())
    delta = min(time.time() - save_time, 8 * 3600)
    if delta > 60:
        p_cps = int(upgrades["passive"]["level"] * 1 * (1.0 + (quantum_foam * 0.15)))
        if p_cps > 0:
            offline_earnings = int(delta * p_cps * 0.5)
            total_clicks += offline_earnings
            stats["lifetime_clicks"] += offline_earnings
            offline_popup_timer = 6.0

def get_active_rules(key):
    preset = L_SYSTEMS[key]
    rules_list = [(preset["rules"][0], 1.0 - (upgrades["mutagen"]["level"] * 0.15))]
    if upgrades["mutagen"]["level"] > 0:
        rules_list.append(({"F": "F[+F]F[-F]F"}, upgrades["mutagen"]["level"] * 0.15))
    return rules_list

def regenerate_string(key):
    global active_string
    max_allowed = L_SYSTEMS[key].get("max_safe_iter", 5)
    actual_iter = min(upgrades["iter"]["level"], max_allowed)
    active_string = generate_l_system(L_SYSTEMS[key]["axiom"], get_active_rules(key), actual_iter)

def get_polyline(string, target_angle, target_length, draw_chars, base_pos, max_segments):
    poly = []
    x, y = base_pos
    angle = -90
    stack = []
    for i, char in enumerate(string):
        if char in draw_chars:
            rad = math.radians(angle)
            x2 = x + target_length * math.cos(rad)
            y2 = y + target_length * math.sin(rad)
            depth = len(stack)
            poly.append((x, y, x2, y2, depth, i/len(string)))
            x, y = x2, y2
        elif char == '+': angle += target_angle
        elif char == '-': angle -= target_angle
        elif char == '[': stack.append((x, y, angle))
        elif char == ']':
            if stack: x, y, angle = stack.pop()
        if len(poly) >= max_segments: break
    while len(poly) < max_segments:
        if poly:
            x, y, x2, y2, d, i = poly[-1]
            poly.append((x2, y2, x2, y2, d, 1.0))
        else:
            poly.append((base_pos[0], base_pos[1], base_pos[0], base_pos[1], 0, 1.0))
    return poly

def precompute_bezier():
    global bezier_ctrl
    bezier_ctrl = []
    for i in range(MAX_MORPH_SEGMENTS):
        ox1, oy1, ox2, oy2, od, oi = old_poly[i]
        nx1, ny1, nx2, ny2, nd, ni = new_poly[i]
        dist1 = math.hypot(nx1 - ox1, ny1 - oy1)
        mid1_x = (ox1 + nx1) / 2 + random.uniform(-1, 1) * (dist1 * 0.4 + 30)
        mid1_y = (oy1 + ny1) / 2 + random.uniform(-1, 1) * (dist1 * 0.4 + 30)
        dist2 = math.hypot(nx2 - ox2, ny2 - oy2)
        mid2_x = (ox2 + nx2) / 2 + random.uniform(-1, 1) * (dist2 * 0.4 + 30)
        mid2_y = (oy2 + ny2) / 2 + random.uniform(-1, 1) * (dist2 * 0.4 + 30)
        bezier_ctrl.append((mid1_x, mid1_y, mid2_x, mid2_y))

regenerate_string(current_l_system_key)

shop_buttons = [
    {"rect": pygame.Rect(WIDTH - 260, 90, 240, 32), "key": "cps", "label": "Auto CPS"},
    {"rect": pygame.Rect(WIDTH - 260, 125, 240, 32), "key": "passive", "label": "Passive Income"},
    {"rect": pygame.Rect(WIDTH - 260, 160, 240, 32), "key": "iter", "label": "Fractal Detail"},
    {"rect": pygame.Rect(WIDTH - 260, 195, 240, 32), "key": "scale", "label": "Fractal Scale"},
    {"rect": pygame.Rect(WIDTH - 260, 230, 240, 32), "key": "time_warp", "label": "Time Dilation"},
    {"rect": pygame.Rect(WIDTH - 260, 265, 240, 32), "key": "crit", "label": "Crit Chance"},
    {"rect": pygame.Rect(WIDTH - 260, 300, 240, 32), "key": "mutagen", "label": "Mutagen (DNA)"},
    {"rect": pygame.Rect(WIDTH - 260, 335, 240, 32), "key": "auto_od", "label": "Auto-Overdrive"},
    {"rect": pygame.Rect(WIDTH - 260, 370, 240, 32), "key": "auto_morph", "label": "Auto-Morph"},
    {"rect": pygame.Rect(WIDTH - 260, 405, 240, 32), "key": "morph_speed", "label": "Temporal Flux"},
    {"rect": pygame.Rect(WIDTH - 260, 450, 240, 45), "key": "prestige", "label": "Quantum Collapse"}
]

def calc_prestige_gain(clicks):
    return int(math.sqrt(max(0, clicks) / 5000))

def do_prestige():
    global total_clicks, upgrades, quantum_foam, energy, active_string, ambient_sound
    gain = calc_prestige_gain(total_clicks)
    if gain > 0:
        quantum_foam += gain
        total_clicks = 0
        upgrades = get_default_upgrades()
        energy = 0
        regenerate_string(current_l_system_key)
        trail_surface.fill((0, 0, 0, 0))
        if 'prestige' in SOUNDS: SOUNDS['prestige'].play()
        floating_texts.append({'x': WIDTH//2, 'y': HEIGHT//2, 'text': f"REALITY COLLAPSED! +{gain} Foam", 'alpha': 255, 'vy': -1.0, 'color': (200, 100, 255)})
        achievements["first_prestige"]["unlocked"] = True
        if music_enabled:
            ambient_sound = generate_ambient_music(quantum_foam)
            if ambient_sound: ambient_sound.play(loops=-1)

def check_achievements():
    global achievement_popup_timer
    if not achievements["first_click"]["unlocked"] and stats["lifetime_clicks"] > 0:
        achievements["first_click"]["unlocked"] = True
        achievement_popup_timer = 3.0
    if not achievements["1k_clicks"]["unlocked"] and stats["lifetime_clicks"] >= 1000:
        achievements["1k_clicks"]["unlocked"] = True
        achievement_popup_timer = 3.0
    if not achievements["100k_clicks"]["unlocked"] and stats["lifetime_clicks"] >= 100000:
        achievements["100k_clicks"]["unlocked"] = True
        achievement_popup_timer = 3.0

def unlock_achievement(key):
    global achievement_popup_timer
    if not achievements[key]["unlocked"]:
        achievements[key]["unlocked"] = True
        achievement_popup_timer = 3.0

def draw_background(bg_id, time_elapsed, dt):
    if bg_id == 0: 
        screen.fill((5, 5, 15))
        for star in stars:
            star['x'] -= 0.2 * star['z']
            if star['x'] < 0: star['x'] = WIDTH
            s_color = int(100 + 155 * star['z'])
            pygame.draw.circle(screen, (s_color, s_color, s_color), (int(star['x']), int(star['y'])), int(star['size']))
    elif bg_id == 1: 
        screen.fill((10, 0, 20))
        vanish_x, vanish_y = WIDTH // 3, HEIGHT - 120
        for i in range(-15, 16):
            x_bot = vanish_x + i * 80
            pygame.draw.line(screen, (255, 0, 150), (x_bot, HEIGHT), (vanish_x, vanish_y), 2)
        scroll = (time_elapsed * 0.5) % 1.0
        for i in range(1, 25):
            y_norm = (i + scroll) / 25.0
            y = vanish_y + (y_norm**2 * 900)
            if y < HEIGHT: pygame.draw.line(screen, (0, 255, 255), (0, y), (WIDTH, y), 2)
    elif bg_id == 2: 
        screen.fill((0, 10, 0))
        for drop in matrix_drops:
            drop['y'] += drop['speed'] * dt
            if drop['y'] - drop['len'] > HEIGHT:
                drop['y'] = random.uniform(-HEIGHT, -50)
                drop['x'] = random.randint(0, WIDTH)
            for j in range(drop['len']):
                color = (0, min(255, 100 + j*10), 0)
                if j == 0: color = (200, 255, 200) 
                pygame.draw.rect(screen, color, (drop['x'], drop['y'] - j*5, 3, 5))
    elif bg_id == 3: 
        screen.fill((5, 5, 10))
        nebula_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(6):
            t = time_elapsed * 0.2 + i * 1.2
            x = WIDTH//2 + math.cos(t) * 250
            y = HEIGHT//2 + math.sin(t * 1.5) * 200
            hue = (time_elapsed * 0.05 + i * 0.15) % 1.0
            r, g, b = get_palette_color(hue, 0.8, 1.0)
            pygame.draw.circle(nebula_surf, (int(r*255), int(g*255), int(b*255), 40), (int(x), int(y)), 300)
        screen.blit(nebula_surf, (0, 0))
    elif bg_id == 4: 
        screen.fill((0, 5, 15))
        aurora_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(4):
            hue = (0.3 + i * 0.1 + time_elapsed * 0.05) % 1.0
            r, g, b = get_palette_color(hue, 0.7, 1.0)
            points = []
            for x in range(0, WIDTH + 20, 20):
                y_base = 200 + i * 50
                y = y_base + math.sin((x / 150) + time_elapsed * (0.5 + i * 0.2) + i) * 60
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(aurora_surf, (int(r*255), int(g*255), int(b*255), 80), False, points, 15)
                pygame.draw.lines(aurora_surf, (int(r*255), int(g*255), int(b*255), 150), False, points, 4)
        screen.blit(aurora_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

def draw_system_string(surface, string, time_elapsed, base_pos, energy_level, passive_level, scale, offset_x, hue_shift, alpha, is_overdriving, mutagen_level, time_warp_level, target_angle, target_length, draw_chars):
    global active_blossoms
    x, y = base_pos[0] + offset_x, base_pos[1]
    local_time = time_elapsed * (1.0 + (time_warp_level * 0.5))
    wind_sway = math.sin(local_time * 0.5 + offset_x * 0.01) * 10.0
    angle = -90 + wind_sway 
    stack = []
    scale_mult = 1.0 + (upgrades["scale"]["level"] * 0.15)
    length = (target_length + math.sin(local_time * 1.2) * 0.5 + (energy_level * 0.02)) * scale * scale_mult
    morph_angle = target_angle + math.sin(local_time * 0.8) * 8.0
    base_hue = (local_time * 0.05 + hue_shift) % 1.0
    if mutagen_level > 0 and scale < 1.0: base_hue = (0.3 + mutagen_level * 0.05) % 1.0
    if scale > 0.9: active_blossoms.clear()
    
    for i, char in enumerate(string):
        if char in draw_chars:
            rad = math.radians(angle)
            x2 = x + length * math.cos(rad)
            y2 = y + length * math.sin(rad)
            hue = (base_hue + (i / len(string)) * 0.8) % 1.0
            r, g, b = get_palette_color(hue, 0.9, 1.0)
            if is_overdriving or frenzy_timer > 0: r, g, b = 255, 255, 255 if is_overdriving else (200, 100, 255)
            depth = len(stack)
            thickness = max(1, int((6 - depth) * scale))
            pygame.draw.line(surface, (int(r*255), int(g*255), int(b*255), alpha), (x, y), (x2, y2), thickness)
            x, y = x2, y2
        elif char == '+': angle += morph_angle
        elif char == '-': angle -= morph_angle
        elif char == '[': stack.append((x, y, angle))
        elif char == ']':
            if stack:
                x, y, angle = stack.pop()
                if len(stack) < 3 and passive_level > 0 and scale > 0.9:
                    pulse = math.sin(local_time * 4 + i * 0.5) * 2 + (3 + passive_level * scale)
                    blossom_hue = (base_hue + 0.5) % 1.0
                    r, g, b = get_palette_color(blossom_hue, 1.0, 1.0)
                    if is_overdriving: r, g, b = 255, 255, 255
                    a = min(255, 100 + (passive_level * 15))
                    pygame.draw.circle(surface, (int(r*255), int(g*255), int(b*255), a), (int(x), int(y)), int(pulse))
                    active_blossoms.append({'x': x, 'y': y, 'rad': pulse + 5})

def bezier(p0, p1, p2, t):
    u = 1 - t
    return (u*u * p0[0] + 2*u*t * p1[0] + t*t * p2[0],
            u*u * p0[1] + 2*u*t * p1[1] + t*t * p2[1])

def draw_system_morph(surface, time_elapsed, is_overdriving, time_warp_level, morph_progress):
    local_time = time_elapsed * (1.0 + (time_warp_level * 0.5))
    scale_mult = 1.0 + (upgrades["scale"]["level"] * 0.15)
    base_hue = (local_time * 0.05) % 1.0
    cx, cy = WIDTH // 3, HEIGHT // 2
    chroma_offset = math.sin(morph_progress * math.pi) * 5.0
    
    for i in range(MAX_MORPH_SEGMENTS):
        ox1, oy1, ox2, oy2, od, oi = old_poly[i]
        nx1, ny1, nx2, ny2, nd, ni = new_poly[i]
        mc1x, mc1y, mc2x, mc2y = bezier_ctrl[i]
        
        dist_to_center = math.hypot((ox1+ox2)/2 - cx, (oy1+oy2)/2 - cy) / 400.0
        local_t = max(0.0, min(1.0, (morph_progress * 1.8) - dist_to_center * 0.4))
        p = ease_out_elastic(local_t)
        
        x1, y1 = bezier((ox1, oy1), (mc1x, mc1y), (nx1, ny1), p)
        x2, y2 = bezier((ox2, oy2), (mc2x, mc2y), (nx2, ny2), p)
        
        v1 = bezier((ox1, oy1), (mc1x, mc1y), (nx1, ny1), min(1.0, p + 0.01))
        vel = math.hypot(x1 - v1[0], y1 - v1[1]) * 10.0
        
        hue = (base_hue + (i / MAX_MORPH_SEGMENTS) * 0.8) % 1.0
        sat, val = 1.0, 1.0
        if vel > 1.0: hue = 0.0
        if vel > 5.0: sat = 0; val = 1.0
            
        r, g, b = get_palette_color(hue, sat, val)
        if is_overdriving: r, g, b = 255, 255, 255
            
        depth = min(od, nd)
        thickness = max(1, int((6 - depth) * 1.0 * scale_mult))
        alpha = 180
        
        pygame.draw.line(surface, (int(r*255), 0, 0, alpha), (x1 - chroma_offset, y1), (x2 - chroma_offset, y2), thickness)
        pygame.draw.line(surface, (0, int(g*255), 0, alpha), (x1, y1), (x2, y2), thickness)
        pygame.draw.line(surface, (0, 0, int(b*255), alpha), (x1 + chroma_offset, y1), (x2 + chroma_offset, y2), thickness)

# --- Main Loop ---
if music_enabled:
    ambient_sound = generate_ambient_music(quantum_foam)
    if ambient_sound: ambient_sound.play(loops=-1)

while running:
    current_time = time.time()
    dt = clock.tick(FPS) / 1000.0
    time_elapsed = current_time - start_time
    mouse_pos = pygame.mouse.get_pos()
    
    stats["time_played"] += dt
    
    mouse_trail.append({'x': mouse_pos[0], 'y': mouse_pos[1], 'life': 1.0})
    if len(mouse_trail) > 10: mouse_trail.pop(0)
    for t in mouse_trail: t['life'] -= dt * 3

    if current_time - last_save_time >= 15.0:
        save_game({"total_clicks": total_clicks, "upgrades": upgrades, "current_l_system_key": current_l_system_key, "quantum_foam": quantum_foam, "achievements": achievements, "stats": stats, "current_palette_idx": current_palette_idx})
        last_save_time = current_time
        floating_texts.append({'x': WIDTH//2, 'y': 50, 'text': "Game Saved", 'alpha': 255, 'vy': -1.0, 'color': (200, 200, 255)})

    if prestige_confirm_timer > 0: prestige_confirm_timer -= dt
    if achievement_popup_timer > 0: achievement_popup_timer -= dt
    if offline_popup_timer > 0: offline_popup_timer -= dt
    if combo_timer > 0: combo_timer -= dt
    else: combo_mult = max(1.0, combo_mult - dt * 2.0)
    if frenzy_timer > 0: frenzy_timer -= dt
    if auto_crit_timer > 0: auto_crit_timer -= dt

    if morph_active:
        morph_timer += dt
        actual_morph_duration = base_morph_duration - (upgrades["morph_speed"]["level"] * 0.4)
        if morph_timer >= actual_morph_duration:
            morph_active = False
            old_l_system_key = target_l_system_key
            current_l_system_key = target_l_system_key
            old_poly = []
            new_poly = []
            bezier_ctrl = []
            trail_surface.fill((0, 0, 0, 0)) 

    if upgrades["auto_morph"]["level"] > 0 and not morph_active:
        auto_morph_timer += dt
        if auto_morph_timer >= 20.0:
            auto_morph_timer = 0.0
            keys = list(L_SYSTEMS.keys())
            keys.remove(target_l_system_key)
            old_l_system_key = target_l_system_key
            target_l_system_key = random.choice(keys)
            old_preset = L_SYSTEMS[old_l_system_key]
            new_preset = L_SYSTEMS[target_l_system_key]
            old_str = generate_l_system(old_preset["axiom"], get_active_rules(old_l_system_key), min(upgrades["iter"]["level"], old_preset.get("max_safe_iter", 5)))
            new_str = generate_l_system(new_preset["axiom"], get_active_rules(target_l_system_key), min(upgrades["iter"]["level"], new_preset.get("max_safe_iter", 5)))
            old_poly = get_polyline(old_str, old_preset["base_angle"], old_preset["base_length"], old_preset["draw_chars"], old_preset["base_pos"], MAX_MORPH_SEGMENTS)
            new_poly = get_polyline(new_str, new_preset["base_angle"], new_preset["base_length"], new_preset["draw_chars"], new_preset["base_pos"], MAX_MORPH_SEGMENTS)
            precompute_bezier()
            active_string = new_str
            morph_active = True
            morph_timer = 0.0
            trail_surface.fill((0, 0, 0, 0))
            if 'morph' in SOUNDS: SOUNDS['morph'].play()
            unlock_achievement("first_morph")
            stats["total_morphs"] += 1

    check_achievements()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game({"total_clicks": total_clicks, "upgrades": upgrades, "current_l_system_key": current_l_system_key, "quantum_foam": quantum_foam, "achievements": achievements, "stats": stats, "current_palette_idx": current_palette_idx})
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: is_clicking = True
            elif event.key == pygame.K_ESCAPE:
                save_game({"total_clicks": total_clicks, "upgrades": upgrades, "current_l_system_key": current_l_system_key, "quantum_foam": quantum_foam, "achievements": achievements, "stats": stats, "current_palette_idx": current_palette_idx})
                running = False
            elif event.key == pygame.K_m:
                music_enabled = not music_enabled
                if ambient_sound:
                    if music_enabled: ambient_sound.play(loops=-1)
                    else: ambient_sound.stop()
            elif event.key == pygame.K_c:
                current_palette_idx = (current_palette_idx + 1) % len(PALETTES)
                trail_surface.fill((0, 0, 0, 0))
                floating_texts.append({'x': WIDTH//2, 'y': 100, 'text': f"Palette: {PALETTES[current_palette_idx]['name']}", 'alpha': 255, 'vy': -1.0, 'color': (255, 255, 255)})
            elif event.key == pygame.K_b: 
                current_bg = (current_bg + 1) % 5
                trail_surface.fill((0, 0, 0, 0))
            elif event.key in L_SYSTEMS.keys():
                if event.key != target_l_system_key and not morph_active:
                    old_l_system_key = target_l_system_key
                    target_l_system_key = event.key
                    old_preset = L_SYSTEMS[old_l_system_key]
                    new_preset = L_SYSTEMS[target_l_system_key]
                    old_str = generate_l_system(old_preset["axiom"], get_active_rules(old_l_system_key), min(upgrades["iter"]["level"], old_preset.get("max_safe_iter", 5)))
                    new_str = generate_l_system(new_preset["axiom"], get_active_rules(target_l_system_key), min(upgrades["iter"]["level"], new_preset.get("max_safe_iter", 5)))
                    old_poly = get_polyline(old_str, old_preset["base_angle"], old_preset["base_length"], old_preset["draw_chars"], old_preset["base_pos"], MAX_MORPH_SEGMENTS)
                    new_poly = get_polyline(new_str, new_preset["base_angle"], new_preset["base_length"], new_preset["draw_chars"], new_preset["base_pos"], MAX_MORPH_SEGMENTS)
                    precompute_bezier()
                    active_string = new_str
                    morph_active = True
                    morph_timer = 0.0
                    trail_surface.fill((0, 0, 0, 0))
                    if 'morph' in SOUNDS: SOUNDS['morph'].play()
                    unlock_achievement("first_morph")
                    stats["total_morphs"] += 1
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                if energy >= 100 and not is_overdriving:
                    is_overdriving = True
                    overdrive_timer = 5.0
                    energy = 0
                    if 'overdrive' in SOUNDS: SOUNDS['overdrive'].play()
                    screen_shake = 20
                    unlock_achievement("first_od")
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE: is_clicking = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_shop = False
                for btn in shop_buttons:
                    if btn["rect"].collidepoint(event.pos):
                        clicked_shop = True
                        u = upgrades[btn["key"]] if btn["key"] != "prestige" else None
                        if btn["key"] == "prestige":
                            gain = calc_prestige_gain(total_clicks)
                            if gain > 0:
                                if prestige_confirm_timer <= 0: prestige_confirm_timer = 3.0
                                else:
                                    do_prestige()
                                    prestige_confirm_timer = 0
                        elif u:
                            max_allowed = L_SYSTEMS[current_l_system_key].get("max_safe_iter", 5)
                            is_maxed_for_shape = btn["key"] == "iter" and u.get("level", 0) >= max_allowed
                            if total_clicks >= u["cost"] and u.get("level", 0) < u.get("max", 999) and not is_maxed_for_shape:
                                total_clicks -= u["cost"]
                                u["level"] += 1
                                u["cost"] = int(u["cost"] * u["cost_mult"])
                                if btn["key"] in ("iter", "mutagen"):
                                    regenerate_string(target_l_system_key)
                                    trail_surface.fill((0, 0, 0, 0))
                
                if not clicked_shop:
                    hit_orb = False
                    for orb in golden_orbs[:]:
                        if math.hypot(event.pos[0] - orb['x'], event.pos[1] - orb['y']) < orb['radius'] + 10:
                            if 'powerup' in SOUNDS: SOUNDS['powerup'].play()
                            if orb['type'] == 'wealth':
                                bonus = max(50, int(current_cps * 10))
                                total_clicks += bonus
                                stats["lifetime_clicks"] += bonus
                                floating_texts.append({'x': orb['x'], 'y': orb['y'], 'text': f"+{format_number(bonus)}!", 'alpha': 255, 'vy': -2.0, 'color': (255, 215, 0)})
                                for _ in range(20): particles.append({'x': orb['x'], 'y': orb['y'], 'vx': random.uniform(-4, 4), 'vy': random.uniform(-4, 4), 'life': 1.0, 'hue': 0.15})
                            elif orb['type'] == 'frenzy':
                                frenzy_timer = 10.0
                                floating_texts.append({'x': orb['x'], 'y': orb['y'], 'text': "FRENZY!", 'alpha': 255, 'vy': -2.0, 'color': (200, 100, 255)})
                                for _ in range(20): particles.append({'x': orb['x'], 'y': orb['y'], 'vx': random.uniform(-4, 4), 'vy': random.uniform(-4, 4), 'life': 1.0, 'hue': 0.8})
                            elif orb['type'] == 'surge':
                                energy = 100
                                auto_crit_timer = 5.0
                                floating_texts.append({'x': orb['x'], 'y': orb['y'], 'text': "SURGE!", 'alpha': 255, 'vy': -2.0, 'color': (0, 255, 255)})
                                for _ in range(20): particles.append({'x': orb['x'], 'y': orb['y'], 'vx': random.uniform(-4, 4), 'vy': random.uniform(-4, 4), 'life': 1.0, 'hue': 0.5})
                                
                            golden_orbs.remove(orb)
                            hit_orb = True
                            unlock_achievement("first_orb")
                            break
                    
                    if not hit_orb:
                        for blos in active_blossoms[:]:
                            if math.hypot(event.pos[0] - blos['x'], event.pos[1] - blos['y']) < blos['rad'] + 8:
                                bonus = max(10, passive_cps * 5)
                                total_clicks += bonus
                                stats["lifetime_clicks"] += bonus
                                floating_texts.append({'x': blos['x'], 'y': blos['y'], 'text': f"+{format_number(bonus)}", 'alpha': 255, 'vy': -2.0, 'color': (100, 255, 150)})
                                if 'blossom' in SOUNDS: SOUNDS['blossom'].play()
                                active_blossoms.remove(blos)
                                for _ in range(10): particles.append({'x': blos['x'], 'y': blos['y'], 'vx': random.uniform(-3, 3), 'vy': random.uniform(-3, 3), 'life': 1.0, 'hue': 0.33})
                                unlock_achievement("first_blossom")
                                break

    foam_mult = 1.0 + (quantum_foam * 0.15)
    base_cps = upgrades["cps"]["level"] * 2
    frenzy_mult = 3.0 if frenzy_timer > 0 else 1.0
    current_cps = int(base_cps * foam_mult * (5.0 if is_overdriving else 1.0) * frenzy_mult)
    crit_chance = upgrades["crit"]["level"] * 0.05
    crit_mult = 5 + upgrades["crit"]["level"] * 5
    
    if upgrades["auto_od"]["level"] > 0 and energy >= 100 and not is_overdriving:
        is_overdriving = True
        overdrive_timer = 5.0
        energy = 0
        if 'overdrive' in SOUNDS: SOUNDS['overdrive'].play()
        screen_shake = 20
        unlock_achievement("first_od")

    if is_clicking:
        click_interval = 1.0 / current_cps if current_cps > 0 else 1.0
        if current_time - last_click_time >= click_interval:
            last_click_time = current_time
            combo_mult = min(5.0, combo_mult + 0.05)
            combo_timer = 0.2
            is_crit = random.random() < crit_chance or auto_crit_timer > 0
            base_val = (crit_mult if is_crit else 1) * (5 if is_overdriving else 1)
            click_value = int(base_val * combo_mult)
            total_clicks += click_value
            stats["lifetime_clicks"] += click_value
            if is_crit: stats["lifetime_crits"] += 1
            if not is_overdriving: energy = min(energy + (5 if is_crit else 3), 100)
            
            if is_crit:
                screen_shake = 15 + combo_mult * 2
                if 'crit' in SOUNDS: SOUNDS['crit'].play()
                floating_texts.append({'x': WIDTH // 3, 'y': HEIGHT - 150, 'text': f"CRIT! +{click_value}", 'alpha': 255, 'vy': -2.0, 'color': (255, 50, 50)})
                for _ in range(10): particles.append({'x': WIDTH // 3, 'y': HEIGHT - 120, 'vx': random.uniform(-3, 3), 'vy': random.uniform(-8, -4), 'life': 1.5, 'hue': 0.0})
                unlock_achievement("first_crit")
            else:
                if 'click' in SOUNDS and random.random() < 0.2: SOUNDS['click'].play()
                
            click_effects.append({'x': WIDTH // 3, 'y': HEIGHT - 120, 'radius': 10, 'alpha': 255, 'color': (255,50,50) if is_crit else (255,255,255)})
            p_count = int(8 * combo_mult) if is_overdriving else int(3 * combo_mult)
            for _ in range(p_count):
                particles.append({'x': WIDTH // 3 + random.uniform(-10, 10), 'y': HEIGHT - 120, 'vx': random.uniform(-2, 2), 'vy': random.uniform(-7, -3), 'life': 1.0, 'hue': random.random()})

    passive_cps = int(upgrades["passive"]["level"] * 1 * foam_mult)
    if passive_cps > 0:
        if current_time - last_passive_time >= 1.0:
            last_passive_time = current_time
            total_clicks += passive_cps
            stats["lifetime_clicks"] += passive_cps
            if 'passive' in SOUNDS: SOUNDS['passive'].play()
            floating_texts.append({'x': WIDTH // 3 + random.uniform(-20, 20), 'y': HEIGHT - 140, 'text': f"+{passive_cps}", 'alpha': 255, 'vy': -1.5, 'color': (100, 255, 150)})

    if is_overdriving:
        overdrive_timer -= dt
        if overdrive_timer <= 0: is_overdriving = False

    if current_time - last_orb_spawn >= next_orb_delay:
        last_orb_spawn = current_time
        next_orb_delay = random.uniform(15, 30)
        orb_type = random.choices(['wealth', 'frenzy', 'surge'], weights=[60, 20, 20])[0]
        colors = {'wealth': (255, 215, 0), 'frenzy': (200, 100, 255), 'surge': (0, 255, 255)}
        golden_orbs.append({'x': WIDTH // 3 + random.uniform(-150, 150), 'y': HEIGHT - 120 + random.uniform(-300, -100), 'radius': 12, 'life': 8.0, 'type': orb_type, 'color': colors[orb_type]})

    if not is_clicking and energy > 0 and not is_overdriving:
        energy = max(0, energy - 20 * dt)
    if screen_shake > 0:
        screen_shake -= 40 * dt

    fade_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_mask.fill((0, 0, 0, 25 if not is_overdriving else 60))
    trail_surface.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    for effect in click_effects[:]:
        effect['radius'] += 100 * dt
        effect['alpha'] -= 300 * dt
        if effect['alpha'] <= 0: click_effects.remove(effect)

    particle_surface.fill((0,0,0,0))
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.2
        p['life'] -= dt * 1.5
        if p['life'] <= 0: particles.remove(p)
        else:
            r, g, b = get_palette_color(p['hue'], 1.0, 1.0)
            if is_overdriving: r, g, b = 255, 255, 255
            pygame.draw.circle(particle_surface, (int(r*255), int(g*255), int(b*255), int(p['life']*255)), (int(p['x']), int(p['y'])), 3)

    for ft in floating_texts[:]:
        ft['y'] += ft['vy']
        ft['alpha'] -= 80 * dt
        if ft['alpha'] <= 0: floating_texts.remove(ft)
        
    for orb in golden_orbs[:]:
        orb['life'] -= dt
        if orb['life'] <= 0: golden_orbs.remove(orb)

    if morph_active:
        progress = morph_timer / (base_morph_duration - (upgrades["morph_speed"]["level"] * 0.4))
        draw_system_morph(trail_surface, time_elapsed, is_overdriving, upgrades["time_warp"]["level"], progress)
    else:
        preset = L_SYSTEMS[current_l_system_key]
        draw_system_string(trail_surface, active_string, time_elapsed, preset["base_pos"], energy, 0, 1.15, -40, 0.2, 60, is_overdriving, upgrades["mutagen"]["level"], upgrades["time_warp"]["level"], preset["base_angle"], preset["base_length"], preset["draw_chars"])
        draw_system_string(trail_surface, active_string, time_elapsed, preset["base_pos"], energy, upgrades["passive"]["level"], 1.0, 0, 0.0, 180, is_overdriving, 0, upgrades["time_warp"]["level"], preset["base_angle"], preset["base_length"], preset["draw_chars"])

    shake_x = random.uniform(-screen_shake, screen_shake) if screen_shake > 0 else 0
    shake_y = random.uniform(-screen_shake, screen_shake) if screen_shake > 0 else 0

    if is_overdriving:
        flash = abs(math.sin(current_time * 20)) * 60
        screen.fill((flash, flash, flash))
    else:
        draw_background(current_bg, time_elapsed, dt)

    screen.blit(trail_surface, (shake_x, shake_y), special_flags=pygame.BLEND_RGBA_ADD)
    screen.blit(particle_surface, (shake_x, shake_y), special_flags=pygame.BLEND_RGBA_ADD)

    for i, t in enumerate(mouse_trail):
        if t['life'] > 0:
            r = 5 + i
            alpha = int(t['life'] * 100)
            pygame.draw.circle(screen, (255, 255, 255, alpha), (int(t['x']), int(t['y'])), r)

    for effect in click_effects:
        ripple_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(ripple_surface, (*effect['color'], int(effect['alpha'])), (int(effect['x'] + shake_x), int(effect['y'] + shake_y)), int(effect['radius']), 2)
        screen.blit(ripple_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    for orb in golden_orbs:
        pulse = math.sin(current_time * 8) * 3
        rad = orb['radius'] + pulse
        orb_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(orb_surf, (*orb['color'], 100), (int(orb['x'] + shake_x), int(orb['y'] + shake_y)), int(rad * 2.5))
        pygame.draw.circle(orb_surf, (*orb['color'], 255), (int(orb['x'] + shake_x), int(orb['y'] + shake_y)), int(rad))
        screen.blit(orb_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        timer_ratio = orb['life'] / 8.0
        pygame.draw.arc(screen, (255,255,255), (orb['x']-rad-5+shake_x, orb['y']-rad-5+shake_y, (rad+5)*2, (rad+5)*2), 0, timer_ratio * 2 * math.pi, 3)

    for ft in floating_texts:
        txt_color = ft.get('color', (255, 255, 255))
        text_surf = font_main.render(ft['text'], True, txt_color)
        text_surf.set_alpha(int(ft['alpha']))
        screen.blit(text_surf, (int(ft['x'] + shake_x), int(ft['y'] + shake_y)))

    # --- UI: Left Stats Panel ---
    pygame.draw.rect(screen, (20, 20, 30, 200), (0, 0, 350, 160))
    pygame.draw.rect(screen, (60, 60, 80), (0, 0, 350, 160), 2)
    screen.blit(font_large.render(f"Clicks: {format_number(total_clicks)}", True, (255, 255, 255)), (20, 20))
    screen.blit(font_main.render(f"Auto CPS: {current_cps} {'[FRENZY]' if frenzy_timer > 0 else ''}", True, (200, 100, 255) if frenzy_timer > 0 else (0, 255, 150)), (20, 60))
    screen.blit(font_main.render(f"Passive: {passive_cps}/sec", True, (100, 200, 255)), (20, 85))
    crit_txt = f"{int(crit_chance*100)}% (x{crit_mult})" if crit_chance > 0 else "Locked"
    if auto_crit_timer > 0: crit_txt = "100% (SURGE)"
    screen.blit(font_main.render(f"Crit: {crit_txt}", True, (0, 255, 255) if auto_crit_timer > 0 else (255, 100, 100)), (20, 110))
    screen.blit(font_main.render(f"Quantum Foam: {quantum_foam} (+{int(foam_mult*100-100)}% All)", True, (200, 100, 255)), (20, 135))
    
    # --- UI: Top Center Stats Dashboard ---
    stat_rect = pygame.Rect(WIDTH//2 - 200, 10, 400, 70)
    pygame.draw.rect(screen, (20, 20, 30, 200), stat_rect, border_radius=5)
    pygame.draw.rect(screen, (60, 60, 80), stat_rect, 2, border_radius=5)
    screen.blit(font_small.render("LIFETIME STATISTICS", True, (200, 200, 200)), (stat_rect.x + 15, stat_rect.y + 5))
    screen.blit(font_mono.render(f"Clicks: {format_number(stats['lifetime_clicks'])}", True, (255, 255, 255)), (stat_rect.x + 15, stat_rect.y + 25))
    screen.blit(font_mono.render(f"Crits: {format_number(stats['lifetime_crits'])}", True, (255, 100, 100)), (stat_rect.x + 15, stat_rect.y + 45))
    screen.blit(font_mono.render(f"Morphs: {stats['total_morphs']}", True, (0, 255, 255)), (stat_rect.x + 150, stat_rect.y + 25))
    screen.blit(font_mono.render(f"Time: {format_time(stats['time_played'])}", True, (100, 200, 255)), (stat_rect.x + 150, stat_rect.y + 45))
    screen.blit(font_mono.render(f"Palette [C]: {PALETTES[current_palette_idx]['name']}", True, (200, 255, 100)), (stat_rect.x + 270, stat_rect.y + 25))
    screen.blit(font_mono.render(f"Music [M]: {'ON' if music_enabled else 'OFF'}", True, (200, 255, 100)), (stat_rect.x + 270, stat_rect.y + 45))
    
    # --- UI: Bottom Bars ---
    pygame.draw.rect(screen, (40, 40, 40), (20, HEIGHT - 140, 200, 20))
    pygame.draw.rect(screen, (0, 255, 255), (20, HEIGHT - 140, int(2 * energy), 20))
    if not is_overdriving and energy >= 100: 
        screen.blit(font_small.render("OVERDRIVE READY! [SHIFT]", True, (0, 255, 255)), (20, HEIGHT - 145))
    elif is_overdriving:
        pygame.draw.rect(screen, (255, 255, 0), (20, HEIGHT - 140, int(40 * overdrive_timer), 20))
        screen.blit(font_small.render(f"OVERDRIVE! {overdrive_timer:.1f}s", True, (255, 255, 0)), (20, HEIGHT - 145))

    pygame.draw.rect(screen, (40, 40, 40), (20, HEIGHT - 115, 200, 15))
    combo_color = (255, 100, 255) if combo_mult > 1.0 else (100, 100, 100)
    pygame.draw.rect(screen, combo_color, (20, HEIGHT - 115, int(40 * (combo_mult - 1.0)), 15))
    if combo_mult > 1.05:
        screen.blit(font_small.render(f"COMBO x{combo_mult:.1f}", True, combo_color), (20, HEIGHT - 120))

    screen.blit(font_main.render(f"Shape [1-0]: {L_SYSTEMS[target_l_system_key]['name']}", True, (255, 200, 0) if not morph_active else (0, 255, 255)), (20, HEIGHT - 60))
    bg_names = ["Cosmic Drift", "Synthwave Grid", "Matrix Rain", "Plasma Nebula", "Aurora Borealis"]
    screen.blit(font_small.render(f"Iter: {upgrades['iter']['level']} | Warp: {upgrades['time_warp']['level']} | BG [B]: {bg_names[current_bg]}", True, (200, 200, 200)), (20, HEIGHT - 30))

    # --- UI: Shop ---
    pygame.draw.rect(screen, (20, 20, 30), (WIDTH - 300, 0, 300, HEIGHT))
    pygame.draw.rect(screen, (60, 60, 80), (WIDTH - 300, 0, 300, HEIGHT), 2)
    screen.blit(font_large.render("APEX HUB", True, (255, 255, 0)), (WIDTH - 260, 20))
    screen.blit(font_small.render("Progress auto-saves.", True, (150, 150, 150)), (WIDTH - 260, 55))

    for btn in shop_buttons:
        u = upgrades.get(btn["key"], None)
        is_hovered = btn["rect"].collidepoint(mouse_pos)
        
        if btn["key"] == "prestige":
            gain = calc_prestige_gain(total_clicks)
            can_prestige = gain > 0
            is_confirming = prestige_confirm_timer > 0
            
            if is_confirming:
                color = (150, 0, 0) if is_hovered else (200, 50, 50)
                txt = f"CONFIRM? ({int(prestige_confirm_timer)})"
                sub_txt = f"+{gain} Foam. Click again!"
            elif can_prestige:
                color = (80, 40, 80) if is_hovered else (40, 20, 40)
                txt = "Quantum Collapse"
                sub_txt = f"Reset for +{gain} Foam"
            else:
                color = (30, 30, 30)
                txt = "Quantum Collapse"
                sub_txt = f"Needs {format_number(5000)} clicks"
                
            pygame.draw.rect(screen, color, btn["rect"], border_radius=5)
            pygame.draw.rect(screen, (200, 100, 255), btn["rect"], 2, border_radius=5)
            screen.blit(font_main.render(txt, True, (255, 255, 255)), (btn["rect"].x + 10, btn["rect"].y + 5))
            screen.blit(font_small.render(sub_txt, True, (255, 200, 255)), (btn["rect"].x + 10, btn["rect"].y + 25))
            continue

        can_afford = total_clicks >= u["cost"]
        is_maxed_global = u.get("level", 0) >= u.get("max", 999)
        max_allowed = L_SYSTEMS[current_l_system_key].get("max_safe_iter", 5)
        is_maxed_for_shape = btn["key"] == "iter" and u.get("level", 0) >= max_allowed
        
        if is_maxed_global or is_maxed_for_shape: color = (40, 40, 40)
        elif is_hovered and can_afford: color = (40, 80, 40)
        elif can_afford: color = (30, 30, 40)
        else: color = (20, 20, 25)
            
        pygame.draw.rect(screen, color, btn["rect"], border_radius=5)
        pygame.draw.rect(screen, (100, 100, 120), btn["rect"], 2, border_radius=5)
        
        level_text = f"Lvl {u['level']}" if btn['key'] != 'iter' else f"Iter {u['level']}"
        if is_maxed_global: level_text = "MAXED"
        elif is_maxed_for_shape: level_text = "MAX (Safe)"
        
        screen.blit(font_main.render(f"{btn['label']}", True, (255, 255, 255)), (btn["rect"].x + 10, btn["rect"].y + 2))
        screen.blit(font_small.render(f"{level_text}", True, (180, 180, 180)), (btn["rect"].x + 10, btn["rect"].y + 18))
        
        if not is_maxed_global and not is_maxed_for_shape:
            cost_color = (0, 255, 100) if can_afford else (255, 80, 80)
            screen.blit(font_main.render(f"{format_number(u['cost'])}", True, cost_color), (btn["rect"].x + 150, btn["rect"].y + 18))

    if achievement_popup_timer > 0:
        for key, val in achievements.items():
            if val["unlocked"] and achievement_popup_timer > 2.5:
                popup_rect = pygame.Rect(WIDTH//2 - 150, 90, 300, 50)
                pygame.draw.rect(screen, (20,20,30), popup_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 215, 0), popup_rect, 2, border_radius=5)
                screen.blit(font_main.render("ACHIEVEMENT UNLOCKED", True, (255, 215, 0)), (popup_rect.x + 10, popup_rect.y + 5))
                screen.blit(font_small.render(f"{val['name']} - {val['desc']}", True, (255, 255, 255)), (popup_rect.x + 10, popup_rect.y + 25))
                break

    if offline_popup_timer > 0:
        popup_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 60, 400, 120)
        pygame.draw.rect(screen, (20, 20, 40), popup_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 255, 200), popup_rect, 3, border_radius=10)
        screen.blit(font_large.render("WELCOME BACK", True, (100, 255, 200)), (popup_rect.x + 120, popup_rect.y + 10))
        screen.blit(font_main.render(f"You earned {format_number(offline_earnings)} clicks", True, (255, 255, 255)), (popup_rect.x + 80, popup_rect.y + 50))
        screen.blit(font_small.render("while you were away (50% efficiency)", True, (180, 180, 180)), (popup_rect.x + 80, popup_rect.y + 80))

    instr = "[SPACE] Click. [SHIFT] Overdrive. [1-0] Morph. [B] BG. [C] Palette. [M] Music. [CLICK] Orbs. [ESC] Quit."
    screen.blit(font_small.render(instr, True, (150, 150, 150)), (20, HEIGHT - 80))

    pygame.display.flip()

pygame.quit()