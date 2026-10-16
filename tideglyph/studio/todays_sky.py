#!/usr/bin/env python3
"""Compute the general sky for a date and pick the day's headline transit.
Self-contained: pyswisseph in Moshier mode, no data files, no network.
Usage: python3 todays_sky.py 2026-10-16   (defaults to today, SAST morning)
Prints a JSON object the caller turns into copy."""
import sys, json, datetime
import swisseph as swe

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
ASPECTS = {0:"conjunction",60:"sextile",90:"square",120:"trine",180:"opposition"}
BODIES = {"Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,"Venus":swe.VENUS,
          "Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN}
FLAG = swe.FLG_MOSEPH | swe.FLG_SPEED

def lon(jd, body):
    xx,_ = swe.calc_ut(jd, body, FLAG)
    return xx[0], xx[3]  # longitude, speed/day

def sep(a, b):
    d = abs(a-b) % 360
    return 360-d if d > 180 else d

def sky(date_str=None):
    if date_str:
        y,m,d = map(int, date_str.split("-"))
    else:
        t = datetime.date.today(); y,m,d = t.year, t.month, t.day
    jd = swe.julday(y, m, d, 4.0)       # 06:00 SAST = 04:00 UT
    jd_next = swe.julday(y, m, d, 4.0) + 1
    pos = {n: lon(jd, b)[0] for n, b in BODIES.items()}
    spd = {n: lon(jd, b)[1] for n, b in BODIES.items()}
    moon_sign = SIGNS[int(pos["Moon"]//30)]
    moon_sign_next = SIGNS[int(lon(jd_next, swe.MOON)[0]//30)]
    # all aspects within 6 deg
    names = list(pos); rows = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]; s = sep(pos[a], pos[b])
            for ang, nm in ASPECTS.items():
                orb = abs(s-ang)
                if orb <= 6:
                    rows.append({"a":a,"b":b,"type":nm,"orb":round(orb,2)})
    rows.sort(key=lambda r: r["orb"])
    # headline: a very tight non-Moon aspect wins; else the Moon's story
    non_moon = [r for r in rows if "Moon" not in (r["a"], r["b"])]
    moon_asp = [r for r in rows if "Moon" in (r["a"], r["b"])]
    if non_moon and non_moon[0]["orb"] <= 2.0:
        head = non_moon[0]; kind = "planet_aspect"
    elif moon_sign != moon_sign_next:
        head = {"a":"Moon","b":moon_sign_next,"type":"enters","orb":0}; kind = "moon_ingress"
    elif moon_asp:
        head = moon_asp[0]; kind = "moon_aspect"
    else:
        head = {"a":"Moon","b":moon_sign,"type":"in","orb":0}; kind = "moon_sign"
    label = (f"{head['a']} {head['type']} {head['b']}" if kind!="moon_ingress"
             else f"Moon enters {head['b']}")
    return {
        "date": f"{y:04d}-{m:02d}-{d:02d}",
        "moon_sign": moon_sign,
        "retrogrades": [n for n,v in spd.items() if v < 0 and n!="Moon"],
        "headline_kind": kind,
        "headline": head,
        "transit_label": label,
        "all_aspects": rows[:6],
    }

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(sky(arg), indent=2))
