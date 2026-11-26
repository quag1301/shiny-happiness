"""Original, procedurally generated soundtrack (no samples, no copyright issues).
- Bed: slow D-minor pad (i-VI-III-VII) + soft pulse bass, "corporate noir"
- Clock: quiet tick-tock every 0.5 s
- Each card: mechanical time-clock "ka-CHUNK" at the punch, then a stamp hit whose
  colour follows the fate (good = bell, bad = low buzz-thud, twist = rising two-note, neutral = plain thud)
Usage: python3 make_audio.py out/timing.json out/audio.wav
"""
import json, sys, wave
import numpy as np

SR = 44100
info = json.load(open(sys.argv[1]))
DUR = info["duration"]
N = int(DUR * SR) + SR
rng = np.random.default_rng(3)
t = np.arange(N) / SR
mix = np.zeros(N)

def env(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (d * SR)); return e

def add(sig, at, gain=1.0):
    i = int(at * SR)
    if i >= N: return
    n = min(len(sig), N - i); mix[i:i+n] += sig[:n] * gain

def note(f): return 440 * 2 ** ((f - 69) / 12)

# ---------------- pad ----------------
chords = [[50, 57, 62, 65], [46, 53, 58, 62], [53, 57, 60, 65], [48, 55, 60, 64]]  # Dm, Bb, F, C
CH = 9.0
pad = np.zeros(N)
for k in range(int(DUR / CH) + 2):
    ch = chords[k % 4]; start = k * CH; n = int((CH + 2.5) * SR)
    tt = np.arange(n) / SR
    e = np.minimum(1, tt / 2.0) * np.clip((CH + 2.5 - tt) / 2.5, 0, 1)
    s = np.zeros(n)
    for m in ch:
        for det in (-0.12, 0.0, 0.11):
            f = note(m) * 2 ** (det / 12)
            ph = rng.random() * 6.28
            s += np.sin(2*np.pi*f*tt + ph) + 0.35*np.sin(4*np.pi*f*tt + ph) + 0.12*np.sin(6*np.pi*f*tt + ph)
    s *= e * (0.75 + 0.25*np.sin(2*np.pi*0.18*tt))
    i = int(start * SR); m_ = min(n, N - i)
    if m_ > 0: pad[i:i+m_] += s[:m_]
pad /= np.max(np.abs(pad)) + 1e-9
mix += pad * 0.16

# pulse bass on each beat (80 bpm) following chord root
beat = 60 / 80
for k in range(int(DUR / beat)):
    at = k * beat; root = chords[int(at // CH) % 4][0] - 12
    n = int(0.5 * SR); tt = np.arange(n) / SR
    s = np.sin(2*np.pi*note(root)*tt) * env(n, 0.01, 0.18)
    add(s, at, 0.10 if k % 2 == 0 else 0.06)

# ---------------- clock ticks ----------------
def tick(hi):
    n = int(0.03 * SR); nz = rng.standard_normal(n) * env(n, 0.0005, 0.004)
    tt = np.arange(n) / SR; return nz * 0.5 + np.sin(2*np.pi*(3200 if hi else 2400)*tt) * env(n, 0.0005, 0.006)
for k in range(int(DUR / 0.5)):
    add(tick(k % 2 == 0), k * 0.5, 0.05)

# ---------------- sfx ----------------
def chunk():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    click = rng.standard_normal(n) * env(n, 0.0005, 0.012)
    thump = np.sin(2*np.pi*(95 - 40*tt)*tt) * env(n, 0.002, 0.07)
    clank = np.sin(2*np.pi*1450*tt) * env(n, 0.001, 0.03) * 0.3
    s = click * 0.6 + thump * 1.0 + clank
    s2 = np.zeros(n); d = int(0.07 * SR); s2[d:] = (rng.standard_normal(n-d) * env(n-d, 0.0005, 0.01)) * 0.5  # latch release
    return s + s2
def bell(f0=1318.5):
    n = int(1.6 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for r, a, d in ((1, 1, 0.9), (2.76, .5, .45), (5.40, .25, .25), (8.93, .12, .15)):
        s += a * np.sin(2*np.pi*f0*r*tt) * env(n, 0.001, d)
    return s * 0.5
def thud(f=70, dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*(f + 30*np.exp(-tt*30))*tt) * env(n, 0.002, 0.16) + rng.standard_normal(n) * env(n, 0.0005, 0.02) * 0.4
def buzz():
    n = int(0.6 * SR); tt = np.arange(n) / SR
    saw = ((tt * 58) % 1) * 2 - 1; saw2 = ((tt * 61.5) % 1) * 2 - 1
    return (saw + saw2) * 0.35 * env(n, 0.005, 0.22) + thud(55, 0.6)
def twist():
    a = bell(880) * 0.6; b = bell(1174.7) * 0.6; d = int(0.14 * SR)
    out = np.zeros(len(a) + d); out[:len(a)] += a; out[d:] += b; return out

for tp, tone in zip(info["punches"], info["tones"]):
    add(chunk(), tp, 0.9)
    st = tp + 0.38
    add(thud(), st, 0.7)
    if tone == "good": add(bell(), st + 0.02, 0.35)
    elif tone == "bad": add(buzz(), st, 0.45)
    elif tone == "twist": add(twist(), st + 0.02, 0.35)
# final card: bigger hit + double bell
last = info["punches"][-1] + 0.38
add(thud(48, 1.2), last, 1.0); add(bell(1318.5), last + 0.02, 0.5); add(bell(1760), last + 0.25, 0.35)

# ---------------- simple reverb ----------------
irn = int(0.9 * SR); ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / (0.22 * SR)); ir[0] = 0
L = 1 << int(np.ceil(np.log2(N + irn)))
wet = np.fft.irfft(np.fft.rfft(mix, L) * np.fft.rfft(ir, L), L)[:N]
wet /= np.max(np.abs(wet)) + 1e-9
out = mix + wet * np.max(np.abs(mix)) * 0.18
# fades + normalise
fi = int(0.3 * SR); out[:fi] *= np.linspace(0, 1, fi)
fo = int(2.5 * SR); end = int(DUR * SR); out[end - fo:end] *= np.linspace(1, 0, fo); out[end:] = 0
out = out[:end]
out = out / (np.max(np.abs(out)) + 1e-9) * 0.89
st = (np.stack([out, out], 1) * 32767).astype("<i2")
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print("audio", round(DUR, 1), "s")
