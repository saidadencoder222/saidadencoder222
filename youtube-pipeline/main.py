"""Orchestrates one full run: pick a ready topic -> countdown script ->
per-moment voiceover -> assemble video from real clip_bank footage ->
thumbnail -> title/description/tags -> upload -> record state.

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

from pipeline import clip_bank, metadata as metadata_mod, script_writer, state, thumbnail, video_builder, voiceover
from pipeline import topics as topics_mod
from pipeline import youtube_uploader

load_dotenv()


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_once(cfg: dict, anthropic_client, elevenlabs_key: str | None, dry_run: bool) -> None:
    topic = topics_mod.next_topic(cfg, anthropic_client)
    print(f"[topic] {topic['title']} (clip_tag={topic['clip_tag']})")

    clip_paths = clip_bank.list_clips(cfg["clip_bank"]["dir"], topic["clip_tag"], cfg["clip_bank"]["max_moments"])
    clip_labels = [clip_bank.clip_label(p) for p in clip_paths]
    print(f"[clips] {len(clip_paths)} clips: {clip_labels}")

    script = script_writer.generate_script(cfg, anthropic_client, topic["title"], clip_paths, clip_labels)
    print(f"[script] intro + {len(script.moments)} moments")

    workdir = tempfile.mkdtemp(prefix="ytpipeline_")
    try:
        intro_audio_path = os.path.join(workdir, "intro.mp3")
        intro_vo = voiceover.generate_voiceover(cfg, script.intro_narration, intro_audio_path, elevenlabs_key)
        print(f"[voiceover] intro {intro_vo.duration_s:.1f}s")

        moment_segments = []
        for m in script.moments:
            seg_audio_path = os.path.join(workdir, f"moment_{m.rank}.mp3")
            vo = voiceover.generate_voiceover(cfg, m.narration, seg_audio_path, elevenlabs_key)
            moment_segments.append((m.clip_path, vo, f"#{m.rank}"))
            print(f"[voiceover] #{m.rank} {vo.duration_s:.1f}s")

        video_path = os.path.join(workdir, "video.mp4")
        video_builder.build_video(cfg, intro_vo, moment_segments, music_path=None, out_path=video_path)
        print(f"[video] built {video_path}")

        meta = metadata_mod.generate_metadata(cfg, anthropic_client, topic["title"], script.full_text)
        print(f"[metadata] title: {meta.title}")

        thumb_bg_path = os.path.join(workdir, "thumb_bg.jpg")
        top_clip_path = script.moments[-1].clip_path  # rank #1, shown last
        clip_bank.extract_thumbnail_frame(top_clip_path, thumb_bg_path)
        thumb_path = os.path.join(workdir, "thumbnail.jpg")
        thumbnail.build_thumbnail(cfg, thumb_bg_path, meta.title, thumb_path)
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

        state.record_upload(cfg["niche"]["state_file"], topic=topic["title"], video_id=video_id, title=meta.title)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None, help="Videos to produce this run")
    parser.add_argument("--dry-run", action="store_true", help="Skip the YouTube upload step")
    args = parser.parse_args()

    cfg = load_config()
    count = args.count or cfg["run"]["videos_per_invocation"]

    anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")

    for i in range(count):
        print(f"=== video {i + 1}/{count} ===")
        run_once(cfg, anthropic_client, elevenlabs_key, args.dry_run)


if __name__ == "__main__":
    main()
