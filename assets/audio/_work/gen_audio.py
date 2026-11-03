#!/usr/bin/env python3
"""墨點江湖 — 自製合成音效／BGM（無第三方樣本、無版權風險）"""
import math, wave, struct, os, random

SR = 22050
OUT_SFX = "/workspace/wuxia-inn/assets/audio/_work/wav_sfx"
OUT_BGM = "/workspace/wuxia-inn/assets/audio/_work/wav_bgm"
os.makedirs(OUT_SFX, exist_ok=True)
os.makedirs(OUT_BGM, exist_ok=True)
rng = random.Random(42)  # 可重現

def clamp(x, lo=-1.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x

def write_wav(path, samples, sr=SR):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = b"".join(struct.pack("<h", int(clamp(s) * 32767)) for s in samples)
        w.writeframes(frames)

def env_adsr(n, a=0.01, d=0.05, s=0.6, r=0.1, sr=SR):
    """Return envelope list length n"""
    na, nd, nr = int(a*sr), int(d*sr), int(r*sr)
    ns = max(0, n - na - nd - nr)
    e = []
    for i in range(na):
        e.append(i / max(1, na))
    for i in range(nd):
        e.append(1.0 - (1.0 - s) * (i / max(1, nd)))
    for _ in range(ns):
        e.append(s)
    for i in range(nr):
        e.append(s * (1.0 - i / max(1, nr)))
    while len(e) < n:
        e.append(0.0)
    return e[:n]

def noise(n):
    return [rng.uniform(-1, 1) for _ in range(n)]

def soft_clip(x):
    return math.tanh(x)

# ---------- SFX ----------

def sfx_door_wood():
    # 短木門吱呀 + 輕碰：低頻吱 + 瞬態噪聲
    dur = 0.55
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        # squeak chirp
        f = 180 + 90 * math.sin(2 * math.pi * 3.2 * t) + 40 * t
        sq = 0.35 * math.sin(2 * math.pi * f * t) * math.exp(-3.2 * t)
        # wood knock at start
        kn = 0.0
        if t < 0.04:
            kn = 0.55 * rng.uniform(-1, 1) * (1 - t / 0.04)
        # latch click near end
        if 0.38 < t < 0.42:
            kn += 0.4 * rng.uniform(-1, 1) * (1 - abs(t - 0.4) / 0.02)
        out.append(soft_clip(sq + kn * 0.7))
    return out

def sfx_footstep():
    dur = 0.18
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        # soft thud + brief noise
        body = 0.7 * math.sin(2 * math.pi * 90 * t) * math.exp(-28 * t)
        grit = 0.35 * rng.uniform(-1, 1) * math.exp(-40 * t)
        out.append(soft_clip(body + grit))
    return out

def sfx_tea_pour():
    # 倒水沙沙：帶通噪聲 + 輕微起伏
    dur = 0.7
    n = int(SR * dur)
    out = []
    lp = 0.0
    for i in range(n):
        t = i / SR
        raw = rng.uniform(-1, 1)
        # simple high-ish noise filter
        lp = lp * 0.55 + raw * 0.45
        hiss = (raw - lp) * 0.55
        amp = 0.15 + 0.55 * (0.5 + 0.5 * math.sin(2 * math.pi * 2.5 * t))
        amp *= min(1.0, t / 0.08) * min(1.0, (dur - t) / 0.12)
        # soft bubble blip
        bub = 0.0
        if int(t * 14) % 3 == 0 and (t * 14) % 1 < 0.08:
            bub = 0.12 * math.sin(2 * math.pi * 520 * t) * math.exp(-80 * ((t * 14) % 1))
        out.append(soft_clip(hiss * amp + bub))
    return out

def sfx_coin():
    # 銀兩叮：金屬泛音短響
    dur = 0.35
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        a = math.exp(-9 * t)
        s = (0.45 * math.sin(2 * math.pi * 2100 * t)
             + 0.28 * math.sin(2 * math.pi * 3150 * t)
             + 0.18 * math.sin(2 * math.pi * 4200 * t)
             + 0.12 * math.sin(2 * math.pi * 980 * t))
        # second bounce softer
        if t > 0.08:
            t2 = t - 0.08
            a2 = 0.45 * math.exp(-12 * t2)
            s += a2 * (0.3 * math.sin(2 * math.pi * 2400 * t2) + 0.2 * math.sin(2 * math.pi * 3600 * t2))
        out.append(soft_clip(s * a * 0.9))
    return out

def sfx_sword_slash():
    # 刀斬：快速掃頻噪聲 + 金屬尖
    dur = 0.32
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        # whoosh sweep
        f = 800 + 2400 * math.exp(-18 * t)
        whoosh = rng.uniform(-1, 1) * 0.5 * math.exp(-10 * t)
        # band-ish by mixing
        metal = 0.35 * math.sin(2 * math.pi * f * t) * math.exp(-14 * t)
        tip = 0.25 * math.sin(2 * math.pi * 3200 * t) * math.exp(-22 * t)
        out.append(soft_clip(whoosh + metal + tip))
    return out

def sfx_parry():
    # 招架：兩金屬短撞
    dur = 0.28
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        a = math.exp(-16 * t)
        clang = (0.5 * math.sin(2 * math.pi * 1650 * t)
                 + 0.35 * math.sin(2 * math.pi * 2450 * t)
                 + 0.2 * math.sin(2 * math.pi * 3800 * t)
                 + 0.15 * rng.uniform(-1, 1) * math.exp(-40 * t))
        if t > 0.04:
            t2 = t - 0.04
            clang += 0.55 * math.exp(-20 * t2) * (
                0.4 * math.sin(2 * math.pi * 1900 * t2)
                + 0.3 * math.sin(2 * math.pi * 2900 * t2))
        out.append(soft_clip(clang * a * 1.1))
    return out

def sfx_hit():
    # 受擊：低頓 + 短噪
    dur = 0.28
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        thud = 0.75 * math.sin(2 * math.pi * 110 * t) * math.exp(-22 * t)
        thud += 0.35 * math.sin(2 * math.pi * 55 * t) * math.exp(-18 * t)
        flesh = 0.4 * rng.uniform(-1, 1) * math.exp(-30 * t)
        out.append(soft_clip(thud + flesh))
    return out

def sfx_guest_sit():
    # 入座：木椅輕吱 + 布料輕擦
    dur = 0.4
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        creak = 0.3 * math.sin(2 * math.pi * (140 + 30 * math.sin(12 * t)) * t) * math.exp(-6 * t)
        if 0.05 < t < 0.18:
            creak += 0.25 * rng.uniform(-1, 1) * math.exp(-25 * (t - 0.05))
        cloth = 0.12 * rng.uniform(-1, 1) * math.exp(-8 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 8 * t))
        out.append(soft_clip(creak + cloth))
    return out

def sfx_victory():
    # 勝利短句：五聲音階上行
    # 宮商角徵羽 approx: C4 E4 G4 A4 C5
    notes = [261.63, 329.63, 392.00, 440.00, 523.25]
    step = 0.12
    dur = step * len(notes) + 0.25
    n = int(SR * dur)
    out = [0.0] * n
    for ni, f0 in enumerate(notes):
        start = int(ni * step * SR)
        length = int(0.28 * SR)
        for i in range(length):
            if start + i >= n:
                break
            t = i / SR
            a = math.exp(-4.5 * t) * (1.0 if t > 0.005 else t / 0.005)
            s = 0.4 * math.sin(2 * math.pi * f0 * t)
            s += 0.15 * math.sin(2 * math.pi * f0 * 2 * t)
            s += 0.08 * math.sin(2 * math.pi * f0 * 3 * t)
            out[start + i] += s * a
    return [soft_clip(x * 0.95) for x in out]

def sfx_defeat():
    # 失敗短句：下行低沉
    notes = [392.00, 329.63, 261.63, 196.00]
    step = 0.16
    dur = step * len(notes) + 0.3
    n = int(SR * dur)
    out = [0.0] * n
    for ni, f0 in enumerate(notes):
        start = int(ni * step * SR)
        length = int(0.35 * SR)
        for i in range(length):
            if start + i >= n:
                break
            t = i / SR
            a = math.exp(-3.2 * t)
            s = 0.45 * math.sin(2 * math.pi * f0 * t)
            s += 0.2 * math.sin(2 * math.pi * f0 * 0.5 * t)
            out[start + i] += s * a
    return [soft_clip(x * 0.9) for x in out]

def sfx_ui_click():
    # 可選 UI 點擊（P1）
    dur = 0.08
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        s = 0.4 * math.sin(2 * math.pi * 880 * t) * math.exp(-55 * t)
        s += 0.15 * rng.uniform(-1, 1) * math.exp(-80 * t)
        out.append(soft_clip(s))
    return out

# ---------- BGM (20–40s loopable) ----------

def pentatonic(root, degree):
    # major pentatonic intervals in semis: 0,2,4,7,9
    scale = [0, 2, 4, 7, 9]
    octv, d = divmod(degree, 5)
    return root * (2 ** ((scale[d] + 12 * octv) / 12.0))

def tone(t, f, amp=0.1):
    # soft triangle-ish
    ph = (t * f) % 1.0
    tri = 4 * abs(ph - 0.5) - 1
    return amp * (0.7 * tri + 0.3 * math.sin(2 * math.pi * f * t))

def bgm_inn(day=True, seconds=28.0):
    """客棧氛圍：慢五聲、低木聲、輕噪。loop 友好：頭尾接近靜音/同一根音"""
    n = int(SR * seconds)
    root = 196.0 if day else 146.83  # G3 / D3
    out = []
    # simple pattern degrees cycling
    melody = [0, 2, 4, 2, 3, 1, 0, 2, 4, 3, 2, 0, 1, 3, 4, 2]
    bass = [0, 0, 3, 3, 1, 1, 0, 0]
    beat = 0.7  # seconds per melody step
    for i in range(n):
        t = i / SR
        # fade edges for loop
        edge = min(1.0, t / 0.8, (seconds - t) / 0.8)
        # drone
        dr = 0.06 * math.sin(2 * math.pi * root * 0.5 * t)
        dr += 0.04 * math.sin(2 * math.pi * root * t)
        # bass
        bi = int(t / (beat * 2)) % len(bass)
        bf = pentatonic(root * 0.5, bass[bi])
        bs = tone(t, bf, 0.07) * (0.7 + 0.3 * math.sin(2 * math.pi * (1 / (beat * 2)) * t))
        # melody
        mi = int(t / beat) % len(melody)
        mf = pentatonic(root, melody[mi])
        # gentle attack within step
        local = (t / beat) % 1.0
        ma = 0.55 + 0.45 * math.sin(math.pi * min(1.0, local * 1.2))
        mel = tone(t, mf, 0.09 * ma)
        # soft wood tick every 4 beats (day) / quieter night
        tick = 0.0
        if day and (t % (beat * 4)) < 0.03:
            tick = 0.04 * rng.uniform(-1, 1) * (1 - (t % (beat * 4)) / 0.03)
        # night: add soft low pulse
        night = 0.0
        if not day:
            night = 0.03 * math.sin(2 * math.pi * 0.25 * t) * math.sin(2 * math.pi * root * 0.25 * t)
        # room tone
        room = 0.012 * rng.uniform(-1, 1)
        s = (dr + bs + mel + tick + night + room) * edge * (0.95 if day else 0.85)
        out.append(soft_clip(s))
    return out

def bgm_combat(seconds=24.0):
    """戰鬥緊張：較快脈衝、低五聲緊張進行、短打擊點"""
    n = int(SR * seconds)
    root = 110.0  # A2
    out = []
    # darker pentatonic-ish degrees with tension
    riff = [0, 0, 1, 0, 3, 2, 0, 1, 4, 3, 1, 0, 2, 3, 1, 0]
    beat = 0.28
    for i in range(n):
        t = i / SR
        edge = min(1.0, t / 0.5, (seconds - t) / 0.5)
        # driving pulse
        pulse = (1.0 if (t % beat) < beat * 0.35 else 0.35)
        bi = int(t / beat) % len(riff)
        f = pentatonic(root, riff[bi])
        bass = 0.14 * math.sin(2 * math.pi * f * t) * pulse
        bass += 0.08 * math.sin(2 * math.pi * f * 2 * t) * pulse * 0.6
        # octave stab
        hi = pentatonic(root * 2, riff[(bi + 2) % len(riff)])
        stab_env = math.exp(-12 * ((t % beat)))
        stab = 0.07 * math.sin(2 * math.pi * hi * t) * stab_env
        # snare-ish noise every other beat
        sn = 0.0
        if int(t / beat) % 2 == 1 and (t % beat) < 0.06:
            sn = 0.09 * rng.uniform(-1, 1) * (1 - (t % beat) / 0.06)
        # low drone tension
        drone = 0.05 * math.sin(2 * math.pi * root * 0.5 * t)
        s = (bass + stab + sn + drone) * edge
        out.append(soft_clip(s))
    return out

# Generate all
sfx_map = {
    "door_wood": sfx_door_wood,
    "footstep": sfx_footstep,
    "tea_pour": sfx_tea_pour,
    "coin": sfx_coin,
    "sword_slash": sfx_sword_slash,
    "parry": sfx_parry,
    "hit": sfx_hit,
    "guest_sit": sfx_guest_sit,
    "victory": sfx_victory,
    "defeat": sfx_defeat,
    "ui_click": sfx_ui_click,
}

for name, fn in sfx_map.items():
    samples = fn()
    path = os.path.join(OUT_SFX, name + ".wav")
    write_wav(path, samples)
    print(f"SFX {name}: {len(samples)/SR:.3f}s -> {path}")

for name, samples in [
    ("bgm_inn_day", bgm_inn(True, 28.0)),
    ("bgm_inn_night", bgm_inn(False, 32.0)),
    ("bgm_combat", bgm_combat(24.0)),
]:
    path = os.path.join(OUT_BGM, name + ".wav")
    write_wav(path, samples)
    print(f"BGM {name}: {len(samples)/SR:.3f}s -> {path}")

print("DONE")
