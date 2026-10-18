# Timeline format

Paths are relative to the timeline JSON unless absolute. Python 3 plus FFmpeg/FFprobe are required; the renderer uses no Python packages. A font is required only for titles. Run `--check` first. Common Linux, macOS and Windows font locations are detected; a `font` path overrides them.

```json
{
  "size": [1080, 1920],
  "fps": 30,
  "crf": 16,
  "scenes": [
    {
      "source": "clip.mp4",
      "start": 0,
      "duration": 3,
      "speed": 1,
      "fit": "contain",
      "volume": 1,
      "captions": [{"text": "A clear outcome.", "y": 180, "size": 76}]
    },
    {
      "source": "second.mp4",
      "start": 1,
      "duration": 4,
      "transition": {"duration": 0.5, "type": "fade"}
    }
  ]
}
```

This example is 6.5 seconds: transition overlap reduces total duration. `duration` is output time; a 3-second scene at speed 2 consumes 6 source seconds. The renderer rejects insufficient source duration instead of silently freezing. `start` and `speed` apply to audio too. Sources without audio get silence; source audio is otherwise retained by default. Photos use the entire scene duration.

Optional scene fields:
- `crop`: `[x,y,width,height]`, in original source pixels.
- `redactions`: arrays of `[x,y,width,height]` in original source pixels, painted black before crop/scale.
- `box`: `[x,y,width,height]` on the output canvas. Default is the whole canvas.
- `fit`: `contain` (letterbox) or `cover` (center crop). Choose an explicit source crop when important content is off-center.
- `background`: FFmpeg color, default `black`.
- `panels`: `[{"box":[x,y,width,height],"color":"black"}]`, painted after source placement and before titles. Useful when replacing an existing title in a known safe area.
- `captions`: `[{"text":"Line one\nLine two","y":180,"size":76,"color":"white"}]`. Captions are centered; line breaks are deliberate. `x` can be a numeric pixel coordinate. `start`/`end` are optional times within the scene.
- `transition`: applies on entry. `type` is `fade` or `fadeblack`; default is `fade`. Default duration is 0.35s, clamped to half the adjacent scene durations. Set duration 0 for a direct cut.

Optional global fields:
- `font`: caption font path. Use a font installed in the execution environment; do not assume the creator's local paths exist.
- `music`: `{ "source":"music.mp4", "volume":0.25, "fade_out":1.2 }`. Music is mixed with scene audio, not substituted. Set scene `volume` to 0 when silence is intended. Ensure the music source has enough duration; it is not looped automatically.

The output path must differ from every input. Existing outputs require `--overwrite`. Successful renders create `final.receipt.json` containing the resolved sources, timing, format, and full-decode result. The renderer does not install software, control OBS, upload, or post.

For music shorter than the edit, set `music.loop` to `true` to repeat the supplied track. The final mix still trims and fades to the output duration.
