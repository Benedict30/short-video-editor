---
name: short-video-editor
description: Edit supplied clips or screen captures into concise vertical videos for TikTok, Reels, or Shorts, including hook, pacing, titles, transitions, privacy masks, and an exported MP4. Use for editing existing footage; screen recording is optional.
---

# Short Video Editor

Produce the actual edited video, using the user's clips, reference style and accepted copy. A plan or storyboard alone is not the deliverable.

## Edit

- Inspect the footage, duration, audio and representative frames. Identify the outcome worth showing first and one simple narrative. Preserve approved wording and masks across revisions.
- Infer reasonable defaults from the request. For a short vertical demo, start around 15–20 seconds at 1080 × 1920, 30 fps, with readable text and restrained motion. Adapt duration and style to the material rather than forcing every edit into a template.
- Use an outcome-led hook that the footage supports. Keep one dominant headline per shot. A video within the video should play actual moving footage and retain a clear visual hierarchy.
- Let viewers see an action and its result. Shorten waiting, not every meaningful action. Avoid a rapid source transition immediately followed by an outro transition; let the last image settle and ease the music out.
- Preserve source audio unless the brief calls for music or silence. Use only supplied or licensed audio.
- Apply requested redactions before reframing or scaling. Do not reconstruct hidden identifiers. Represent app use with genuine captures; label explanatory reenactments and speed changes when needed.

## Render

Use `python3 scripts/render.py --check` to check Python, FFmpeg, FFprobe and caption font availability. No Python packages are required. The installed FFmpeg must support `libx264`, `xfade`, `acrossfade`, and `drawtext` when adding titles. OBS is only needed when the task includes an OBS recording.

Create a timeline JSON following [references/timeline.md](references/timeline.md), then run:

```text
python3 scripts/render.py timeline.json --output final.mp4
```

The renderer accepts existing scene clips, photos, source crops, opaque privacy masks, titles, audio and crossfades. Use another suitable editing tool when its capabilities better fit the request; keep the same verification and deliverable standards. Do not silently overwrite source files.

## Optional OBS capture

Only use this mode when recording is requested. OBS captures and frames the screen; the editing/export tools make the final cut.

Use the computer-control tool available in the current environment. Check that it can actually operate OBS before promising unattended recording. Capture only the agreed app or window, inspect microphones and audio, and record genuine actions. Save the capture, stop recording, and restore temporary scene transforms and viewport changes. If controls are unavailable, use existing footage or explain what must be captured manually. Do not simulate successful clicks or describe a screenshot montage as continuous raw recording.

## Finish

Play or inspect the opening, action beats, and every changed transition. Verify a complete decode, duration, dimensions, frame rate, readable text and preserved redactions. Review at phone size. Export an H.264 MP4 with AAC when audio is present, plus the render receipt. Give a direct video preview/download link. Publish or send elsewhere only when requested.
