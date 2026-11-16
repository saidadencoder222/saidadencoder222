import numpy as np, cv2
def room_grade(raw, strength=1.0):
    """cool, cinematic grade that matches the room: wall/shadows pushed to cool steel-blue, warm skin and the orange/red posters kept rich and slightly boosted"""
    a = raw.astype(np.float32) / 255
    # 1) neutralise the tungsten cast first (about 75%), so the cool grade starts from a clean wall
    wall = np.array([.53, .64, .76], np.float32); g = wall.mean() / wall; a = a * (1 + (g - 1) * .75)
    a = np.clip(a, 0, 1)
    lum = (a[..., 0] * .114 + a[..., 1] * .587 + a[..., 2] * .299)[..., None]
    # 2) contrast: gentle S-curve + slightly deeper blacks
    a = np.clip(a + (a - .5) * (1 - np.abs(a - .5) * 2) * .35, 0, 1); a = np.clip((a - .03) / .97, 0, 1)
    lum = (a[..., 0] * .114 + a[..., 1] * .587 + a[..., 2] * .299)[..., None]
    # 3) split tone (BGR): shadows + low-saturation walls go steel-blue/teal, highlights stay warm
    hsv = cv2.cvtColor((a * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    skin = np.clip(1 - np.abs(h - 11) / 9, 0, 1) * np.clip(s * 3, 0, 1) * np.clip(v * 1.6, 0, 1)                 # orange hues (skin, posters): protect from the cool push
    cool = (1 - skin[..., None] * .85) * strength
    sh = np.clip(1 - lum * 1.55, 0, 1) ** 1.3
    a = a + cool * sh * np.array([.11, .05, -.05], np.float32)                                                    # shadows to teal-blue
    mid = (1 - np.abs(lum - .55) * 1.6).clip(0, 1) * (1 - s[..., None] * 1.3).clip(0, 1)
    a = a + cool * mid * np.array([.10, .035, -.075], np.float32)                                                    # grey walls to cool steel
    hi = np.clip(lum * 1.4 - .55, 0, 1)
    a = a + hi * skin[..., None] * np.array([-.03, .004, .035], np.float32) * strength                                                  # highlights warm
    # 4) colour: boost the oranges/reds (posters, skin) a touch, calm the rest
    hsv = cv2.cvtColor((np.clip(a, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); h = hsv[..., 0]
    warm = np.clip(1 - np.minimum(np.abs(h - 8), np.abs(h - 176)) / 16, 0, 1)
    hsv[..., 1] = np.clip(hsv[..., 1] * (.94 + .2 * warm), 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255
    # 5) soft vignette
    H, W = out.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = ((xx - W / 2) / (W * .8)) ** 2 + ((yy - H * .48) / (H * .75)) ** 2
    out = out * (1 - .22 * np.clip(d, 0, 1))[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
def warm_grade(raw):
    """natural, soft and WARM (the inspo's look: gentle contrast, slightly lifted blacks, creamy highlights); the room's tungsten warmth is kept, not removed"""
    a = raw.astype(np.float32) / 255
    wall = np.array([.55, .64, .76], np.float32); g = wall.mean() / wall; a = np.clip(a * (1 + (g - 1) * .30), 0, 1)             # remove only ~30% of the cast
    a = np.clip(a + (a - .5) * (1 - np.abs(a - .5) * 2) * .22, 0, 1)                                                           # soft contrast
    a = .035 + a * .965                                                                                                         # lifted blacks (matte-soft)
    lum = (a[..., 0] * .114 + a[..., 1] * .587 + a[..., 2] * .299)[..., None]
    a = a + np.clip(lum * 1.3 - .45, 0, 1) * np.array([-.025, .006, .03], np.float32)                                           # creamy warm highlights
    a = a + np.clip(1 - lum * 1.6, 0, 1) * np.array([.006, .0, -.012], np.float32)                                             # barely-warm shadows
    hsv = cv2.cvtColor((np.clip(a, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.07, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
