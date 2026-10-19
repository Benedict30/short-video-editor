# Short Video Editor

Turn your clips into a short vertical video with Codex: a clear hook, readable titles, smooth transitions and an MP4 ready to post.

**[Download skill](https://github.com/Benedict30/short-video-editor/raw/main/skill.zip)**

## Try it

1. Put the skill ZIP and your video in a folder. Open that folder in Codex with local file and tool access.
2. Paste:

> Install this skill. Use $short-video-editor to make a short vertical video with a strong hook and smooth transitions. Export an MP4.

3. Follow any setup prompts, then review your MP4.

## What you need

- **Setup is included:** Codex checks for Python 3 and FFmpeg (including FFprobe), installs missing tools where permitted, verifies them, then continues editing. No extra Python packages are needed. Titles require a font.
- **OBS is optional:** install it only if you want to record your screen with OBS. It captures footage; Python and FFmpeg make the final edit.
- Automated OBS recording also needs a supported computer-control tool. Existing clips do not need OBS or a Chrome plugin.

You do not need a separate setup prompt. Setup runs through Codex when you use the skill; downloading the ZIP alone does not install software. Your computer may still require an installation approval or administrator password. If setup is blocked, Codex explains the specific action needed.

## Included

- `SKILL.md`: editing and review workflow.
- `scripts/render.py`: local renderer for clips, photos, titles, crops, privacy masks, source audio, music and crossfades.
- `references/timeline.md`: timeline format and options.
- `agents/openai.yaml`: skill display information.

Default output is a vertical 1080 × 1920, 30 fps H.264 MP4, with AAC when audio is present. Each render is checked by decoding the complete video and includes a receipt. Review the final cut before posting.

The renderer does not upload or post your footage.
