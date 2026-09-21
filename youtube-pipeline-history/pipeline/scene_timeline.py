"""Turns a pool of Scenes into a fixed-cadence cut list (default: a new
scene every 3 seconds) covering the full video duration, by cycling
through the pool in a freshly-shuffled order each pass so a scene that
recurs later in a long video doesn't repeat in the same sequence twice in
a row. Cut timing is intentionally decoupled from narration/caption
timing — captions are overlaid separately on top of whatever scene is
showing.
"""
import random
from dataclasses import dataclass

from .scene_pool import Scene


@dataclass
class TimelineEntry:
    scene: Scene
    zoom_in: bool
    start_s: float
    duration_s: float


def build_timeline(pool: list[Scene], total_duration: float, scene_seconds: float) -> list[TimelineEntry]:
    if not pool:
        raise RuntimeError("No visuals available to build a scene timeline from.")

    n_slots = max(int(total_duration // scene_seconds) + 1, 1)
    order: list[Scene] = []
    rng = random.Random(42)
    while len(order) < n_slots:
        cycle = pool[:]
        rng.shuffle(cycle)
        order.extend(cycle)
    order = order[:n_slots]

    timeline: list[TimelineEntry] = []
    t = 0.0
    for i, scene in enumerate(order):
        duration = min(scene_seconds, total_duration - t)
        if duration <= 0:
            break
        timeline.append(TimelineEntry(scene=scene, zoom_in=(i % 2 == 0), start_s=t, duration_s=duration))
        t += duration
    return timeline
