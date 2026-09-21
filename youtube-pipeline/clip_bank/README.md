# Clip bank

This is where the pipeline gets its actual movie footage from. **Nothing in
this repo downloads or scrapes movie clips for you** — that would mean
building a copyright-infringement tool, which this project deliberately
does not do (see the root README's "Copyright — read this" section).

## How to populate it

For each countdown topic in `data/topics_pool.yaml`, there's a `clip_tag`
(e.g. `hulk`). Create a matching folder here and drop in clips you have the
legal right to use:

```
clip_bank/
  hulk/
    01_hulk_first_transformation.mp4
    02_hulk_vs_loki_avengers.mp4
    03_hulk_smash_abomination.mp4
    ...
```

Notes:

- **Name files descriptively.** The filename (minus a leading number/underscore)
  is the *only* information Claude gets about what happens in that clip when
  writing narration — it does not watch the footage. `03_hulk_vs_loki_avengers.mp4`
  becomes the hint `"hulk vs loki avengers"`.
- Up to `clip_bank.max_moments` clips (default 10, see `config.yaml`) are used
  per video, picked at random from the folder each run so repeat topics don't
  produce an identical video.
- Any common video format works (`.mp4`, `.mov`, `.mkv`, `.webm`).
- **Never commit clip files to this git repo** — `.gitignore` at the repo root
  already excludes `clip_bank/**/*.mp4` etc. Pushing copyrighted footage to
  GitHub is redistribution, is against GitHub's terms, and this pipeline is
  not built to do that. Keep clip files local (or in your own private
  storage — see the root README's automation note on self-hosted runners).
- If a topic's folder is missing or empty when the pipeline runs, it's
  skipped in favor of a topic that does have clips, not force-run.
