"""Original, hand-composed polygon illustration. Build dependency: Pillow only.

The geometry, palette, lighting and deterministic texture are authored here.
Runtime does not import this module. Run: python render.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import math
import random

SIZE = 1024
SS = 2
W = SIZE * SS
RNG = random.Random(84017)
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)


def scaled(points):
    return [(round(x * SS), round(y * SS)) for x, y in points]


def mix(a, b, t):
    return tuple(round(x * (1 - t) + y * t) for x, y in zip(a, b))


# Quiet, deep atmospheric field, with the light originating inside the paper.
bg = Image.new("RGB", (SIZE, SIZE))
pixels = bg.load()
assert pixels is not None
for y in range(SIZE):
    for x in range(SIZE):
        warm = math.exp(-(((x - 497) / 300) ** 2 + ((y - 644) / 340) ** 2))
        cool = math.exp(-(((x - 789) / 490) ** 2 + ((y - 288) / 380) ** 2))
        vignette = max(0, 1 - math.hypot(x - 520, y - 490) / 800)
        n = RNG.uniform(-0.8, 0.8)
        pixels[x, y] = tuple(max(0, min(255, round(v + n))) for v in (
            5 + warm * 21 + cool * 2 + vignette * 2,
            13 + warm * 23 + cool * 12 + vignette * 2,
            27 + warm * 21 + cool * 19 + vignette * 3))
canvas = bg.resize((W, W), Image.Resampling.BICUBIC)


def poly(points, top, bottom=None, edge=None):
    """A local gradient gives each paper plane its own directional shading."""
    global canvas
    p = scaled(points)
    x0 = max(0, min(x for x, y in p))
    y0 = max(0, min(y for x, y in p))
    x1 = min(W, max(x for x, y in p) + 1)
    y1 = min(W, max(y for x, y in p) + 1)
    if x1 <= x0 or y1 <= y0:
        return
    width, height = x1 - x0, y1 - y0
    mask = Image.new("L", (width, height))
    md = ImageDraw.Draw(mask)
    local = [(x - x0, y - y0) for x, y in p]
    md.polygon(local, fill=255)
    gradient = Image.new("RGB", (1, height))
    gp = gradient.load()
    assert gp is not None
    for y in range(height):
        gp[0, y] = mix(top, bottom or top, y / max(1, height - 1))
    gradient = gradient.resize((width, height))
    canvas.paste(gradient, (x0, y0), mask)
    if edge:
        ImageDraw.Draw(canvas).line(p + [p[0]], fill=edge, width=SS)


def line(points, color, width: float = 1):
    ImageDraw.Draw(canvas).line(scaled(points), fill=color, width=max(1, round(width * SS)))


def glow(points, color, radius, strength: float = 1):
    global canvas
    layer = Image.new("RGB", (W, W))
    ImageDraw.Draw(layer).polygon(scaled(points), fill=tuple(round(c * strength) for c in color))
    canvas = ImageChops.screen(canvas, layer.filter(ImageFilter.GaussianBlur(radius * SS)))


# A few far stars, deliberately absent behind the head and wing silhouette.
for i in range(110):
    x, y = RNG.uniform(35, 990), RNG.uniform(35, 760)
    if 140 < x < 920 and 140 < y < 630:
        continue
    brightness = RNG.randint(45, 105)
    r = RNG.choice([0.45, 0.6, 0.8, 1.0])
    ImageDraw.Draw(canvas).ellipse((int((x-r)*SS), int((y-r)*SS), int((x+r)*SS), int((y+r)*SS)), fill=(brightness-15, brightness, brightness+20))

# Distant folded landscape, generous negative space at the foot.
poly([(0, 852), (203, 806), (430, 849), (703, 790), (1024, 824), (1024, 1024), (0, 1024)], (12, 29, 43), (4, 11, 23))
poly([(0, 852), (203, 806), (430, 849), (145, 885)], (22, 42, 53), (7, 21, 34))
poly([(430, 849), (703, 790), (1024, 824), (765, 901)], (31, 50, 58), (8, 22, 34))
poly([(145, 885), (430, 849), (765, 901), (1024, 1024), (0, 1024)], (15, 30, 40), (4, 12, 23))

# Warm scattered light from the impossible box and cold light from the far wing.
glow([(370, 696), (510, 620), (628, 737), (516, 816)], (216, 115, 38), 65, .65)
glow([(169, 255), (473, 368), (588, 483), (373, 432)], (39, 115, 128), 24, .45)
glow([(581, 440), (817, 135), (852, 297)], (178, 136, 62), 28, .5)

# The far wing is a single rising gesture, divided into broad folded feathers.
far_root = (538, 454)
far_feathers = [
    ((555, 355), (813, 86), (747, 302)),
    ((578, 376), (891, 132), (797, 348)),
    ((585, 402), (938, 217), (817, 395)),
    ((580, 425), (925, 313), (778, 444)),
    ((569, 447), (858, 416), (712, 486)),
]
for index, (inner, tip, lower) in enumerate(far_feathers):
    poly([far_root, inner, tip, lower], (249, 234, 177), (152, 82, 39))
    mid = ((inner[0]+lower[0])*.5, (inner[1]+lower[1])*.5)
    poly([far_root, mid, tip], (255, 249, 214), (225, 162, 71))
    poly([mid, tip, lower], (206, 141, 65), (115, 60, 37))
    line([far_root, tip], (255, 225, 155), .65)

# Near wing: long, individually designed cut-paper planes, not random shards.
near_feathers = [
    ((422, 342), (167, 123), (240, 347)),
    ((416, 364), (106, 206), (211, 409)),
    ((435, 395), (78, 310), (221, 458)),
    ((449, 423), (97, 412), (259, 501)),
    ((463, 445), (170, 511), (340, 535)),
]
for index, (inner, tip, lower) in enumerate(near_feathers):
    ridge = ((inner[0]+lower[0])*.5, (inner[1]+lower[1])*.5)
    poly([(525, 468), inner, tip, lower], (235, 244, 220), (54, 116, 128))
    poly([(525, 468), ridge, tip], (255, 250, 219), (142, 185, 177))
    poly([ridge, tip, lower], (115, 170, 171), (27, 75, 101))
    line([tip, ridge, (525, 468)], (191, 213, 189), .6)

# Broad shoulder facets join the wings to a sculptural, rising body.
poly([(167, 123), (422, 342), (522, 423), (345, 324)], (255, 248, 213), (117, 165, 160))
poly([(345, 324), (522, 423), (525, 468), (414, 420)], (178, 203, 184), (67, 118, 127))
poly([(522, 423), (747, 302), (813, 86), (633, 355)], (255, 248, 204), (182, 112, 48))
poly([(522, 423), (633, 355), (581, 470)], (246, 195, 107), (147, 75, 36))

# Origami tail unspools from the tiny folded world: a continuous zigzag ribbon.
poly([(506, 474), (565, 489), (462, 574), (385, 586)], (253, 219, 151), (143, 102, 65))
poly([(506, 474), (462, 574), (430, 557)], (255, 246, 203), (225, 160, 80))
poly([(385, 586), (462, 574), (596, 643), (571, 690)], (238, 179, 98), (168, 83, 43))
poly([(385, 586), (571, 690), (457, 624)], (255, 230, 169), (231, 154, 68))
poly([(571, 690), (596, 643), (500, 743), (466, 739)], (252, 216, 142), (255, 239, 187))
poly([(596, 643), (519, 713), (500, 743)], (254, 242, 196), (172, 97, 44))
line([(430, 557), (385, 586), (571, 690), (500, 743)], (255, 238, 190), 1.2)

# Chest, long neck, head and sharp beak: readable bird anatomy in folded planes.
poly([(488, 424), (533, 382), (580, 393), (602, 457), (554, 523), (506, 492)], (255, 248, 210), (207, 134, 59))
poly([(488, 424), (539, 437), (554, 523), (506, 492)], (232, 181, 101), (121, 73, 47))
poly([(533, 382), (583, 329), (622, 281), (665, 286), (623, 350), (580, 431), (539, 437)], (255, 252, 222), (232, 168, 76))
poly([(583, 329), (622, 281), (623, 350), (580, 431)], (242, 197, 119), (149, 84, 43))
poly([(622, 281), (652, 250), (690, 267), (701, 294), (665, 311)], (255, 252, 224), (230, 170, 86))
poly([(652, 250), (670, 219), (676, 260)], (255, 229, 156), (180, 116, 58))
poly([(639, 266), (633, 225), (656, 250)], (244, 200, 114), (187, 109, 49))
poly([(690, 267), (752, 282), (701, 294)], (255, 234, 173), (172, 101, 47))
poly([(665, 311), (701, 294), (679, 288)], (157, 90, 44), (228, 162, 72))
poly([(677, 271), (691, 275), (679, 280)], (10, 29, 40))
line([(681, 272), (690, 275)], (255, 255, 227), .7)

# Torn-open miniature universe: deep blue exterior, glowing paper interior.
glow([(422, 726), (501, 691), (586, 744), (502, 780)], (255, 180, 82), 18, .7)
poly([(397, 738), (486, 695), (593, 738), (501, 793)], (255, 236, 178), (255, 178, 73))
poly([(397, 738), (501, 779), (501, 861), (397, 809)], (25, 67, 90), (9, 29, 53))
poly([(501, 779), (593, 738), (593, 810), (501, 861)], (19, 47, 75), (7, 21, 43))
# Flaps turn inside out; these carry the scale-changing trick.
poly([(397, 738), (486, 695), (439, 661), (349, 715)], (127, 171, 170), (41, 87, 104))
poly([(397, 738), (349, 715), (369, 765)], (255, 230, 162), (141, 115, 74))
poly([(593, 738), (548, 690), (610, 674), (651, 721)], (255, 244, 199), (201, 137, 66))
poly([(501, 779), (593, 738), (629, 785), (538, 824)], (255, 242, 199), (208, 145, 71))
poly([(501, 779), (397, 738), (365, 786), (464, 825)], (255, 245, 203), (152, 152, 129))
line([(397, 809), (501, 861), (593, 810)], (70, 113, 129), 1)

# Constellations belong to the little universe's walls, not the entire canvas.
for pts in [[(409, 771), (428, 798), (452, 788), (478, 816)], [(519, 823), (537, 835), (563, 817), (579, 783)]]:
    line(pts, (74, 124, 145), .55)
    for x, y in pts:
        ImageDraw.Draw(canvas).ellipse((int((x-1.5)*SS), int((y-1.5)*SS), int((x+1.5)*SS), int((y+1.5)*SS)), fill=(182, 224, 218))

# A contained Saturn-like world emphasizes that the box holds a whole cosmos.
# The orbital ellipse follows the perspective of the left wall.
planet = (443, 794)
orbit = []
for i in range(97):
    angle = i * math.tau / 96
    orbit.append((planet[0] + 25 * math.cos(angle),
                  planet[1] + 10 * math.cos(angle) + 7 * math.sin(angle)))
line(orbit[:49], (81, 147, 164), 1.1)
ImageDraw.Draw(canvas).ellipse((434*SS, 783*SS, 452*SS, 805*SS), fill=(159, 209, 205))
poly([(444, 783), (452, 789), (452, 800), (444, 805), (448, 794)], (80, 151, 164), (26, 80, 109))
line(orbit[48:], (206, 232, 204), 1.3)

# A handful of flying folds track the upward motion, with no particle carpet.
for x, y, s, angle in [(335, 607, 13, -.3), (663, 599, 10, .5), (730, 508, 15, .2), (875, 475, 11, -.6), (315, 226, 7, -.3), (753, 112, 6, .4)]:
    pts = [(x-s, y+s*.4), (x, y-s), (x+s, y), (x, y+s*.5)]
    poly(pts, (248, 212, 148), (111, 132, 125))
    poly([pts[0], pts[1], pts[3]], (255, 240, 189), (188, 131, 70))

# One tiny witness on the paper ridge. A local light pool gives the human
# enough contrast at 300px while leaving the upper two-thirds dominant.
glow([(621, 791), (659, 766), (690, 800), (689, 845), (629, 845)], (150, 118, 66), 21, .7)
poly([(598, 851), (650, 839), (706, 854), (755, 908)], (74, 83, 76), (13, 31, 42))
poly([(646, 851), (681, 849), (719, 909)], (7, 16, 27))
line([(653, 849), (657, 829), (657, 809)], (5, 15, 25), 5.1)
line([(671, 849), (664, 828), (661, 809)], (6, 16, 27), 4.9)
poly([(651, 792), (666, 791), (670, 818), (651, 818)], (7, 19, 30))
line([(653, 798), (643, 808), (635, 798)], (9, 22, 33), 3.4)
line([(666, 797), (676, 790), (677, 778)], (10, 23, 33), 3.4)
ImageDraw.Draw(canvas).ellipse((650*SS, 776*SS, 666*SS, 792*SS), fill=(8, 23, 35))
line([(652, 778), (649, 784), (652, 790)], (255, 209, 139), 1.5)
line([(651, 793), (650, 811), (653, 817)], (231, 177, 103), 1)
line([(646, 848), (674, 848)], (192, 163, 112), 1)

# Supersampling keeps every angled crease clean. No lettering, assets or fonts.
final = canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
final.save(ROOT / "entry.png", optimize=True)
final.resize((300, 300), Image.Resampling.LANCZOS).save(OUT / "thumbnail.png")
print(f"Rendered {ROOT / 'entry.png'}: {final.size}, {(ROOT / 'entry.png').stat().st_size} bytes")
