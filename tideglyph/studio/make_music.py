#!/usr/bin/env python3
"""Generate Tideglyph's own ambient bed: a slow, warm pad with a soft bell line.
Fully synthesised here, so Tideglyph owns it outright (no licence, no library).
Usage: python3 make_music.py out.m4a [seconds] [seed]
Four chords of 8 s each loop (Dmaj9, Bm9, Gmaj7#11, Asus2), soft and quiet,
mixed under every Reel by make_reel.py."""
import sys, subprocess, tempfile, pathlib
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile

SR = 44100

def hz(n):  # midi note to Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def pad_voice(f, dur, rng):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for det in (-0.07, 0.0, 0.06):  # three slightly detuned voices
        ff = f * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        # soft sawtooth from a few harmonics
        for k in range(1, 7):
            out += np.sin(2 * np.pi * ff * k * t + ph * k) / (k ** 1.6)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t + rng.uniform(0, 6))
    return out * lfo

def env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    e[:ai] = np.linspace(0, 1, ai) ** 2
    e[-ri:] = np.linspace(1, 0, ri) ** 2
    return e

def bell(f, dur):
    t = np.arange(int(dur * SR)) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.01 * t) + 0.1 * np.sin(2 * np.pi * f * 3.0 * t)
    return tone * np.exp(-t * 1.6) * np.minimum(1, t * 200)

def reverb(x, rng):
    y = x.copy()
    for d, g in ((0.031, .5), (0.047, .45), (0.071, .4), (0.113, .35), (0.173, .3), (0.257, .25), (0.379, .2)):
        k = int(d * SR)
        y[k:] += g * x[:-k]
    b, a = butter(1, 3500 / (SR / 2))
    return lfilter(b, a, y)

def main(out, seconds=64.0, seed=7):
    rng = np.random.default_rng(seed)
    chords = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 57, 61], [45, 52, 57, 59, 64]]
    seg = 8.0
    n = int(seconds * SR)
    L = np.zeros(n + int(4 * SR)); R = np.zeros_like(L)
    i = 0; pos = 0.0
    while pos < seconds:
        ch = chords[i % 4]
        s = int(pos * SR)
        for j, note in enumerate(ch):
            v = pad_voice(hz(note), seg + 3, rng) * env(int((seg + 3) * SR), 2.5, 3.5)
            pan = 0.3 + 0.4 * (j / (len(ch) - 1))
            amp = 0.06 if note < 50 else 0.035
            L[s:s + len(v)] += v * amp * (1 - pan)
            R[s:s + len(v)] += v * amp * pan
        # a few soft bell notes from the chord, an octave up
        for b_i in range(3):
            bt = pos + 1.0 + b_i * 2.4 + rng.uniform(0, 0.4)
            note = ch[rng.integers(2, len(ch))] + 12
            bv = bell(hz(note), 4.0) * 0.05
            bs = int(bt * SR)
            p = rng.uniform(0.25, 0.75)
            L[bs:bs + len(bv)] += bv * (1 - p); R[bs:bs + len(bv)] += bv * p
        i += 1; pos += seg
    b, a = butter(2, 2600 / (SR / 2))
    L = reverb(lfilter(b, a, L), rng)[:n]; R = reverb(lfilter(b, a, R), rng)[:n]
    st = np.stack([L, R], 1)
    st *= env(n, 1.5, 3.0)[:, None]
    st /= np.max(np.abs(st)) / 0.7
    tmp = pathlib.Path(tempfile.mkdtemp()) / "bed.wav"
    wavfile.write(tmp, SR, (st * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-c:a", "aac", "-b:a", "160k", out], check=True)
    print("wrote", out)

if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 64.0, int(sys.argv[3]) if len(sys.argv) > 3 else 7)
