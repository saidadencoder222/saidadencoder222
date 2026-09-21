"""Orchestrates one full run: pick topic -> script -> voiceover -> build a
mixed visual pool (Internet Archive clips + Wikimedia Commons stills) ->
cut a fixed-cadence scene timeline from it -> assemble video -> thumbnail
-> title/description/tags -> upload -> record state.

Usage:
    python main.py                 # one video, uploads to YouTube
    python main.py --count 3       # three videos in one process
    python main.py --dry-run       # build everything, skip the YouTube upload
"""
import argparse
import os
import shutil
import tempfile

import anthropic
import yaml
from dotenv import load_dotenv

from pipeline import ai_clips, metadata as metadata_mod
from pipeline import scene_pool, scene_timeline, script_writer, state, thumbnail, video_builder, voiceover
from pipeline import topics as topics_mod
from pipeline import youtube_uploader

load_dotenv()


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _maybe_animate_pool(cfg: dict, pool: list[scene_pool.Scene], workdir: str, stability_key: str | None) -> None:
    fraction = cfg["visuals"].get("ai_animate_fraction", 0.0)
    if not fraction or not stability_key:
        return
    image_scenes = [s for s in pool if s.kind == "image"]
    n_to_animate = int(len(image_scenes) * fraction)
    for i, scene in enumerate(image_scenes[:n_to_animate]):
        out_path = os.path.join(workdir, f"ai_clip_{i:03d}.mp4")
        if ai_clips.animate_image(scene.path, out_path, stability_key):
            scene.kind = "video"
            scene.path = out_path


def run_once(
    cfg: dict,
    anthropic_client,
    elevenlabs_key: str | None,
    stability_key: str | None,
    dry_run: bool,
    topic_override: str | None = None,
    script_file: str | None = None,
    metadata_file: str | None = None,
) -> None:
    if topic_override:
        topic = topic_override
    else:
        topic = topics_mod.next_topic(cfg, anthropic_client)
    print(f"[topic] {topic}")

    if script_file:
        script = script_writer.load_script_from_file(script_file, topic)
        print(f"[script] loaded from {script_file}")
    else:
        if anthropic_client is None:
            raise RuntimeError(
                "No ANTHROPIC_API_KEY set and no --script-file given — nothing to write the "
                "script with. Either set the key, or pass --script-file (and --topic)."
            )
        script = script_writer.generate_script(cfg, anthropic_client, topic)
    print(f"[script] {len(script.narration.split())} words, {len(script.visual_cues)} visual cues")

    workdir = tempfile.mkdtemp(prefix="ytpipeline_")
    try:
        audio_path = os.path.join(workdir, "voiceover.mp3")
        vo = voiceover.generate_voiceover(cfg, script.narration, audio_path, elevenlabs_key)
        print(f"[voiceover] {vo.duration_s:.1f}s")

        pool = scene_pool.build_pool(cfg, script.visual_cues, os.path.join(workdir, "visuals"))
        n_video = sum(1 for s in pool if s.kind == "video")
        print(f"[visuals] pool of {len(pool)} ({n_video} archival clips, {len(pool) - n_video} stills)")

        _maybe_animate_pool(cfg, pool, workdir, stability_key)

        timeline = scene_timeline.build_timeline(pool, vo.duration_s, cfg["video"]["scene_seconds"])
        print(f"[timeline] {len(timeline)} scene cuts over {vo.duration_s:.1f}s")

        video_path = os.path.join(workdir, "video.mp4")
        video_builder.build_video(cfg, vo, timeline, music_path=None, out_path=video_path)
        print(f"[video] built {video_path}")

        used_images = [s.attribution for s in pool if s.kind == "image" and s.attribution]
        if metadata_file:
            meta = metadata_mod.load_metadata_from_file(metadata_file, used_images)
            print(f"[metadata] loaded from {metadata_file}")
        else:
            if anthropic_client is None:
                raise RuntimeError(
                    "No ANTHROPIC_API_KEY set and no --metadata-file given — nothing to write "
                    "the title/description with. Either set the key, or pass --metadata-file."
                )
            meta = metadata_mod.generate_metadata(cfg, anthropic_client, topic, script.narration, used_images)
        print(f"[metadata] title: {meta.title}")

        thumb_bg = next((s.path for s in pool if s.kind == "image"), None)
        thumb_path = os.path.join(workdir, "thumbnail.jpg")
        if thumb_bg:
            thumbnail.build_thumbnail(cfg, thumb_bg, meta.title, thumb_path)
        else:
            # Pool was entirely video clips: grab a frame from the first one.
            from moviepy import VideoFileClip

            clip = VideoFileClip(pool[0].path)
            frame_path = os.path.join(workdir, "thumb_frame.jpg")
            clip.save_frame(frame_path, t=clip.duration / 2)
            clip.close()
            thumbnail.build_thumbnail(cfg, frame_path, meta.title, thumb_path)
        print(f"[thumbnail] built {thumb_path}")

        video_id = None
        if not dry_run:
            video_id = youtube_uploader.upload_video(
                client_id=os.environ["YOUTUBE_CLIENT_ID"],
                client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
                refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
                video_path=video_path,
                thumbnail_path=thumb_path,
                title=meta.title,
                description=meta.description,
                tags=meta.tags,
                category_id=cfg["youtube"]["category_id"],
                privacy_status=cfg["youtube"]["privacy_status"],
                made_for_kids=cfg["youtube"]["made_for_kids"],
            )
            print(f"[upload] https://youtu.be/{video_id}")
        else:
            out_dir = "dry_run_output"
            os.makedirs(out_dir, exist_ok=True)
            shutil.copy(video_path, os.path.join(out_dir, "video.mp4"))
            shutil.copy(thumb_path, os.path.join(out_dir, "thumbnail.jpg"))
            with open(os.path.join(out_dir, "metadata.txt"), "w", encoding="utf-8") as f:
                f.write(f"Title: {meta.title}\n\nDescription:\n{meta.description}\n\nTags: {meta.tags}\n")
            print(f"[dry-run] output saved to {out_dir}/")

        state.record_upload(cfg["niche"]["state_file"], topic=topic, video_id=video_id, title=meta.title)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None, help="Videos to produce this run")
    parser.add_argument("--dry-run", action="store_true", help="Skip the YouTube upload step")
    parser.add_argument(
        "--topic", default=None,
        help="Use this exact topic instead of picking one from data/topics_pool.yaml",
    )
    parser.add_argument(
        "--script-file", default=None,
        help="Use a pre-written script (e.g. pasted from a Claude chat) instead of calling "
             "the Anthropic API. Requires --topic. Same [VISUAL: ...] cue format as the "
             "auto-generated scripts.",
    )
    parser.add_argument(
        "--metadata-file", default=None,
        help='Use pre-written title/description/tags instead of calling the API. JSON: '
             '{"title": "...", "description": "...", "tags": [...]}',
    )
    args = parser.parse_args()

    if args.script_file and not args.topic:
        parser.error("--script-file requires --topic")

    cfg = load_config()
    count = args.count or cfg["run"]["videos_per_invocation"]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    anthropic_client = anthropic.Anthropic(api_key=api_key) if api_key else None
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    stability_key = os.environ.get("STABILITY_API_KEY")

    for i in range(count):
        print(f"=== video {i + 1}/{count} ===")
        run_once(
            cfg, anthropic_client, elevenlabs_key, stability_key, args.dry_run,
            topic_override=args.topic, script_file=args.script_file, metadata_file=args.metadata_file,
        )


if __name__ == "__main__":
    main()
