---
name: short-video-editor
description: Edit supplied clips or screen captures into concise vertical videos for TikTok, Reels, or Shorts, including hook, pacing, titles, transitions, privacy masks, and an exported MP4. Use for editing existing footage; screen recording is optional.
---

# Short Video Editor

Produce the actual edited video, using the user's clips, reference style and accepted copy. A plan or storyboard alone is not the deliverable.

## Set up missing tools

Handle dependency setup as part of the edit; the user does not need a separate setup prompt.

- Before invoking the renderer, identify the execution environment and check for a working Python 3 interpreter, FFmpeg and FFprobe. Reuse compatible tools already installed or provided by the environment. Check Python directly first: the renderer cannot check dependencies if Python is missing. On Windows, `py -3` or `python` may be the available Python 3 command.
- If a required tool is missing, briefly explain what you will install and install only the missing dependencies within the session's authorization and permissions. Prefer the environment's existing package manager and trusted repositories. Verify the package names for that platform; do not upgrade unrelated packages or replace a working Python installation.
- If there is no suitable package manager, use an official installer or an official-project-linked portable distribution suited to the platform. Inspect the provider's current installation instructions before running them. Do not install a new system package manager merely to complete this edit. If installation requires a password, elevation, network access or an approval that is unavailable, report the specific blocker and the minimum user action needed. Do not bypass a denial or claim setup completed.
- After installation, resolve the executable paths again in the current session. Use the resolved Python 3 interpreter for `scripts/render.py --check`; use a session-local PATH for FFmpeg and FFprobe if necessary. Confirm the required FFmpeg features and a usable font when titles are needed. Continue editing once the checks pass. If a compatible tool already exists, do not reinstall it because it was absent from the initial PATH.
- Do not install OBS for editing existing footage. Only consider it for a requested OBS recording.

## Edit

- Inspect the footage, duration, audio and representative frames. Identify the outcome worth showing first and one simple narrative. Preserve approved wording and masks across revisions.
- Infer reasonable defaults from the request. For a short vertical demo, start around 15–20 seconds at 1080 × 1920, 30 fps, with readable text and restrained motion. Adapt duration and style to the material rather than forcing every edit into a template.
- Use an outcome-led hook that the footage supports. Keep one dominant headline per shot. A video within the video should play actual moving footage and retain a clear visual hierarchy.
- Let viewers see an action and its result. Shorten waiting, not every meaningful action. Avoid a rapid source transition immediately followed by an outro transition; let the last image settle and ease the music out.
- Preserve source audio unless the brief calls for music or silence. Use only supplied or licensed audio.
- Apply requested redactions before reframing or scaling. Do not reconstruct hidden identifiers. Represent app use with genuine captures; label explanatory reenactments and speed changes when needed.

## Render

After setup, use `python3 scripts/render.py --check` (or the resolved Python 3 command) to check FFmpeg, FFprobe and caption font availability. No extra Python packages are required. The installed FFmpeg must support `libx264`, `xfade`, `acrossfade`, and `drawtext` when adding titles. OBS is only needed when the task includes an OBS recording.

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
