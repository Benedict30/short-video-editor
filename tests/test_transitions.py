"""Exercise real FFmpeg output when hard cuts precede fades."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

RENDERER = Path(__file__).resolve().parents[1] / 'scripts' / 'render.py'

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg and FFprobe required')
class TransitionTests(unittest.TestCase):
    def test_cuts_and_fades(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / 'source.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                            'testsrc2=size=160x240:rate=30:duration=1',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(src)], check=True)
            for name, transitions in [
                ('cut_then_fade', [0, .2]),
                ('fade_cut_fade', [.2, 0, .2]),
                ('cuts_then_fadeblack', [0, 0, .2]),
                ('all_cuts', [0, 0]),
            ]:
                with self.subTest(name=name):
                    scenes = [{'source': str(src), 'duration': 1, 'volume': 0}]
                    scenes += [{'source': str(src), 'duration': 1, 'volume': 0,
                                'transition': {'duration': d, 'type': 'fadeblack' if name.endswith('fadeblack') else 'fade'}}
                               for d in transitions]
                    timeline = root / f'{name}.json'
                    output = root / f'{name}.mp4'
                    timeline.write_text(json.dumps({'size': [160, 240], 'fps': 30, 'scenes': scenes}))
                    result = subprocess.run([sys.executable, str(RENDERER), str(timeline), '--output', str(output)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    meta = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(output)]))
                    video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
                    expected = len(scenes) - sum(transitions)
                    self.assertEqual(video['r_frame_rate'], '30/1')
                    self.assertEqual(int(video['nb_read_frames']), round(expected * 30))
                    self.assertAlmostEqual(float(video['duration']), expected, places=2)
                    self.assertEqual(json.loads(output.with_suffix('.receipt.json').read_text())['full_decode'], 'passed')

if __name__ == '__main__':
    unittest.main()
