#!/usr/bin/env python3
"""Portable timeline renderer. Python standard library + FFmpeg/FFprobe."""
import argparse,json,math,os,shutil,subprocess,sys,tempfile
from pathlib import Path
IMAGES={'.png','.jpg','.jpeg','.webp','.bmp'}
def binary(name):
 p=shutil.which(name)
 if not p:raise ValueError(f'{name} was not found. Install FFmpeg/FFprobe in this environment.')
 return p
def probe(p,fp):
 r=subprocess.run([fp,'-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,text=True,check=True)
 return json.loads(r.stdout)
def font_path(custom=None):
 candidates=[custom] if custom else []
 candidates += ['/System/Library/Fonts/Supplemental/Arial Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arialbd.ttf')]
 return next((Path(p) for p in candidates if p and Path(p).is_file()),None)
def positive(v,label):
 f=float(v)
 if not math.isfinite(f) or f<=0:raise ValueError(f'{label} must be positive')
 return f
def rect(v,label):
 if not isinstance(v,list) or len(v)!=4:raise ValueError(f'{label} needs [x,y,width,height]')
 x,y,w,h=map(int,v)
 if min(x,y)<0 or min(w,h)<=0:raise ValueError(f'{label} is invalid')
 return x,y,w,h
def color(v):
 s=str(v)
 if not all(c.isalnum() or c in '#@.' for c in s):raise ValueError('Invalid color')
 return s
def tempo(v):
 parts=[]
 while v>2:parts.append('atempo=2');v/=2
 while v<0.5:parts.append('atempo=0.5');v*=2
 return ','.join(parts+[f'atempo={v}'])
def render(args):
 ff=binary('ffmpeg');fp=binary('ffprobe')
 if args.check:
  filters=subprocess.run([ff,'-hide_banner','-filters'],capture_output=True,text=True,check=True).stdout
  encoders=subprocess.run([ff,'-hide_banner','-encoders'],capture_output=True,text=True,check=True).stdout
  required={n:n in filters for n in ['xfade','acrossfade','drawtext']};required['libx264']='libx264' in encoders
  print(json.dumps({'ffmpeg':ff,'ffprobe':fp,'font':str(font_path() or ''),'features':required},indent=2))
  return 0 if all(required.values()) else 1
 if not args.timeline or not args.output:raise ValueError('Provide timeline.json and --output final.mp4')
 timeline=Path(args.timeline).resolve();cfg=json.loads(timeline.read_text());root=timeline.parent
 def resolve(p):
  p=Path(p);p=p if p.is_absolute() else root/p
  if not p.is_file():raise ValueError(f'Missing source: {p}')
  return p.resolve()
 out=Path(args.output).resolve()
 if out.exists() and not args.overwrite:raise ValueError('Output exists; choose a new name or use --overwrite')
 width,height=map(int,cfg.get('size',[1080,1920]));fps=int(cfg.get('fps',30));crf=int(cfg.get('crf',16))
 if min(width,height)<=0 or width%2 or height%2 or not 1<=fps<=60 or not 0<=crf<=35:raise ValueError('Invalid output size, fps or CRF')
 scenes=cfg.get('scenes',[])
 if not scenes:raise ValueError('At least one scene is required')
 info=[];needs_font=False
 for i,s in enumerate(scenes):
  src=resolve(s['source']);meta=probe(src,fp);video=next((x for x in meta['streams'] if x['codec_type']=='video'),None)
  if not video:raise ValueError(f'{src} has no video')
  d=positive(s['duration'],'duration');speed=positive(s.get('speed',1),'speed');start=float(s.get('start',0))
  if not math.isfinite(start) or start<0:raise ValueError('start cannot be negative')
  still=src.suffix.lower() in IMAGES
  if not still:
   available=float(video.get('duration') or meta['format']['duration'])
   if start+d*speed>available+1/fps:raise ValueError(f'Scene {i}: insufficient footage ({start+d*speed:.3f}s requested, {available:.3f}s available)')
  sw,sh=int(video['width']),int(video['height'])
  for box in ([s['crop']] if 'crop' in s else [])+s.get('redactions',[]):
   x,y,w,h=rect(box,'source box')
   if x+w>sw or y+h>sh:raise ValueError(f'Scene {i}: source box is out of bounds')
  x,y,w,h=rect(s.get('box',[0,0,width,height]),'output box')
  if x+w>width or y+h>height:raise ValueError('Output box is out of bounds')
  if s.get('fit','contain') not in ['contain','cover']:raise ValueError('fit must be contain or cover')
  needs_font |= bool(s.get('captions'))
  volume=float(s.get('volume',1))
  if not math.isfinite(volume) or not 0<=volume<=10:raise ValueError('Invalid volume')
  info.append({'path':src,'duration':d,'start':start,'speed':speed,'still':still,'audio':any(x['codec_type']=='audio' for x in meta['streams']),'box':(x,y,w,h)})
 music=cfg.get('music');music_path=resolve(music['source']) if music else None
 if out in [i['path'] for i in info]+([music_path] if music_path else []):raise ValueError('Refusing to overwrite an input')
 overlaps=[0.0];types=['fade']
 for i in range(1,len(info)):
  t=scenes[i].get('transition',{});over=float(t.get('duration',min(.35,info[i-1]['duration']/2,info[i]['duration']/2)));typ=t.get('type','fade')
  if not math.isfinite(over) or over<0 or over>min(info[i-1]['duration'],info[i]['duration'])/2:raise ValueError('Transition must be no longer than half either adjacent scene')
  if typ not in ['fade','fadeblack']:raise ValueError('Unsupported transition')
  overlaps.append(over);types.append(typ)
 total=sum(i['duration'] for i in info)-sum(overlaps)
 if music:
  mm=probe(music_path,fp)
  if not any(x['codec_type']=='audio' for x in mm['streams']):raise ValueError('Music has no audio stream')
  if not music.get('loop',False) and float(mm['format']['duration'])+1/fps<total:raise ValueError('Music is shorter than the output')
 font=font_path(str(resolve(cfg['font'])) if cfg.get('font') else None)
 if needs_font and not font:raise ValueError('No caption font found; supply a font path in the timeline')
 out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='short-video-',dir=out.parent) as temp:
  wd=Path(temp)
  if font:shutil.copyfile(font,wd/'font.ttf')
  def run(a):subprocess.run([ff,'-hide_banner','-loglevel','error',*a],check=True,cwd=wd)
  clips=[]
  for i,(s,z) in enumerate(zip(scenes,info)):
   d=z['duration'];x,y,w,h=z['box'];dest=wd/f'scene-{i}.mkv';clips.append(dest)
   a=['-filter_complex_threads','1','-f','lavfi','-i',f'color=c={color(s.get("background","black"))}:s={width}x{height}:r={fps}:d={d}']
   if z['still']:a+=['-loop','1','-framerate',str(fps),'-i',str(z['path'])]
   else:a+=['-ss',str(z['start']),'-t',str(d*z['speed']),'-i',str(z['path'])]
   vf=[f'setpts=(PTS-STARTPTS)/{z["speed"]}',f'fps={fps}']
   for red in s.get('redactions',[]):
    rx,ry,rw,rh=rect(red,'redaction');vf.append(f'drawbox=x={rx}:y={ry}:w={rw}:h={rh}:color=black:t=fill')
   if 'crop' in s:
    cx,cy,cw,ch=rect(s['crop'],'crop');vf.append(f'crop={cw}:{ch}:{cx}:{cy}')
   vf += ['format=yuv444p']
   if s.get('fit','contain')=='cover':vf += [f'scale={w}:{h}:force_original_aspect_ratio=increase',f'crop={w}:{h}']
   else:vf += [f'scale={w}:{h}:force_original_aspect_ratio=decrease','format=yuv444p',f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={color(s.get("background","black"))}']
   vf+=['setsar=1'];g=['[1:v]'+','.join(vf)+'[clip]',f'[0:v][clip]overlay={x}:{y}:shortest=1[placed]'];after=[]
   for panel in s.get('panels',[]):
    px,py,pw,ph=rect(panel['box'],'panel');after.append(f'drawbox=x={px}:y={py}:w={pw}:h={ph}:color={color(panel.get("color","black"))}:t=fill')
   for j,c in enumerate(s.get('captions',[])):
    (wd/f'caption-{i}-{j}.txt').write_text(c['text'],encoding='utf-8');xx=str(int(c['x'])) if 'x' in c else '(w-tw)/2';yy=int(c.get('y',180));size=int(c.get('size',76))
    begin=float(c.get('start',0));end=float(c.get('end',d))
    if not 0<=begin<=end<=d or not 1<=size<=500:raise ValueError('Invalid caption times or size')
    after.append(f"drawtext=fontfile=font.ttf:textfile=caption-{i}-{j}.txt:expansion=none:fontsize={size}:fontcolor={color(c.get('color','white'))}:x={xx}:y={yy}:line_spacing=12:enable='between(t,{begin},{end})'")
   g.append('[placed]'+','.join(after+['format=yuv420p'])+'[v]')
   if z['audio'] and not z['still']:
    g.append(f'[1:a]asetpts=PTS-STARTPTS,{tempo(z["speed"])},aresample=48000,aformat=channel_layouts=stereo,volume={float(s.get("volume",1))},apad,atrim=duration={d}[a]')
   else:g.append(f'anullsrc=r=48000:cl=stereo,atrim=duration={d}[a]')
   run(a+['-filter_complex',';'.join(g),'-map','[v]','-map','[a]','-t',str(d),'-c:v','ffv1','-c:a','pcm_s16le','-y',str(dest)])
   print(f'Rendered scene {i+1}/{len(scenes)}',flush=True)
  a=['-filter_complex_threads','1']
  for p in clips:a+=['-i',str(p)]
  if music:a+=(['-stream_loop','-1'] if music.get('loop',False) else [])+['-i',str(music_path)]
  g=[]
  for i in range(len(clips)):g += [f'[{i}:v]settb=1/{fps},setpts=PTS-STARTPTS[v{i}]',f'[{i}:a]asetpts=PTS-STARTPTS[a{i}]']
  pv,pa='v0','a0';elapsed=info[0]['duration']
  for i in range(1,len(info)):
   ov=overlaps[i]
   if ov:g += [f'[{pv}][v{i}]xfade=transition={types[i]}:duration={ov}:offset={elapsed-ov}[vx{i}]',f'[{pa}][a{i}]acrossfade=d={ov}:c1=tri:c2=tri[ax{i}]']
   # concat changes the timebase and frame-rate metadata; a later xfade needs CFR.
   else:g += [f'[{pv}][v{i}]concat=n=2:v=1:a=0,fps={fps},settb=1/{fps},setpts=PTS-STARTPTS[vx{i}]',f'[{pa}][a{i}]concat=n=2:v=0:a=1[ax{i}]']
   pv,pa=f'vx{i}',f'ax{i}';elapsed+=info[i]['duration']-ov
  if music:
   mv=float(music.get('volume',.25));fade=min(total,float(music.get('fade_out',1.2)))
   if not math.isfinite(mv) or not 0<=mv<=10 or fade<0:raise ValueError('Invalid music settings')
   g += [f'[{len(clips)}:a]atrim=duration={total},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={mv},afade=t=out:st={total-fade}:d={fade}[music]',f'[{pa}][music]amix=inputs=2:duration=first:normalize=0[mix]'];pa='mix'
  final=wd/'final.mp4'
  run(a+['-filter_complex',';'.join(g),'-map',f'[{pv}]','-map',f'[{pa}]','-t',str(total),'-c:v','libx264','-preset','slow','-crf',str(crf),'-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-y',str(final)])
  run(['-i',str(final),'-f','null','-']);meta=probe(final,fp);actual=float(meta['format']['duration'])
  if abs(actual-total)>max(2/fps,.1):raise ValueError(f'Unexpected duration: {actual} vs {total}')
  shutil.move(str(final),str(out))
 receipt={'skill':'short-video-editor','output':str(out),'timeline':str(timeline),'duration':actual,'expected_duration':total,'size':[width,height],'fps':fps,'sources':[str(z['path']) for z in info],'full_decode':'passed'}
 out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('timeline',nargs='?');p.add_argument('--output');p.add_argument('--check',action='store_true');p.add_argument('--overwrite',action='store_true')
 try:sys.exit(render(p.parse_args()))
 except (ValueError,KeyError,subprocess.CalledProcessError,OSError) as e:print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
