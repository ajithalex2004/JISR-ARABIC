"""Script 3 'Tap. Hear. Understand.': phone-frame video per class, master (~22 s) and short cut (~10 s)."""
import json, glob, os, subprocess, sys
R = lambda *a: subprocess.run(list(a), check=True)
dur = lambda f: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, '..', 'apicache'); CAP = os.path.join(HERE, 'cap')
END = os.path.join(HERE, '..', 'cap', 'endcard.png')

def mp3(name):
    for f in glob.glob(os.path.join(CACHE, '*.json')):
        if json.load(open(f))['path'].endswith(name):
            return f[:-5] + '.body'
    raise SystemExit(f'audio {name} not cached')

def build(g):
    base = os.path.join(HERE, 'shots', f'g{g}'); meta = json.load(open(os.path.join(base, 'meta.json')))
    work = os.path.join(base, 'build'); os.makedirs(work, exist_ok=True)
    scenes = []   # (name, length, [(audio file, start within scene, tempo)])
    def evs(s): return meta[s]['events']
    def first(s, prefix, after=0.0):
        return next((e['t'] for e in evs(s) if e['name'].startswith(prefix) and e['t'] >= after), None)
    def audio_after(s, tap_t):
        for e in evs(s):
            if e['name'].startswith('audio:') and e['t'] >= tap_t - 0.05:
                return mp3(e['name'][6:]), e['t'] + 0.1
        return None, tap_t + 0.25
    plan = {}
    # S1 headword
    t = first('S1_word', 'tap:word'); f, a = audio_after('S1_word', t)
    plan['S1_word'] = ([(f, a, 1.0)], max(meta['S1_word']['duration'], a + dur(f) + 0.5), t)
    # S2 two example words (the second may reuse a cached clip: fall back to the first clip's file only if needed)
    t1 = first('S2_words', 'tap:w1'); t2 = first('S2_words', 'tap:w2')
    f1, a1 = audio_after('S2_words', t1); f2, a2 = audio_after('S2_words', t2)
    clips = [(f1, a1, 1.0)] + ([(f2, a2, 1.0)] if f2 and f2 != f1 else [])
    plan['S2_words'] = (clips, max(meta['S2_words']['duration'], a2 + (dur(f2) if f2 else 1) + 0.4), None)
    # S3 sentence
    t = first('S3_sentence', 'tap:sentence'); f, a = audio_after('S3_sentence', t)
    plan['S3_sentence'] = ([(f, a, 1.0)], max(meta['S3_sentence']['duration'], a + dur(f) + 0.5), None)
    # S4 slowed headword (same clip as S1, played at 0.6x)
    t = first('S4_slow', 'tap:word'); f, a = audio_after('S4_slow', t); f = f or plan['S1_word'][0][0][0]
    plan['S4_slow'] = ([(f, a, 0.6)], max(meta['S4_slow']['duration'], a + dur(f) / 0.6 + 0.4), None)
    plan['S5_build'] = ([], meta['S5_build']['duration'] + 0.6, None)

    order = ['S1_word', 'S2_words', 'S3_sentence', 'S4_slow', 'S5_build']
    for s in order:
        clips, length, _ = plan[s]
        R('ffmpeg','-loglevel','error','-y','-f','concat','-i',os.path.join(base, s, 'list.txt'),
          '-vf', f"fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={length:.3f},setpts=PTS-STARTPTS",
          '-c:v','libx264','-crf','14','-preset','medium', os.path.join(work, s + '.mp4'))
    starts, T = {}, 0.0
    for s in order:
        starts[s] = T; T += plan[s][1]
    open(os.path.join(work, 'screen.txt'), 'w').write(''.join(f"file '{s}.mp4'\n" for s in order))
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',os.path.join(work,'screen.txt'),'-c','copy',os.path.join(work,'screen.mp4'))
    # Caption windows (absolute seconds)
    s1tap = starts['S1_word'] + plan['S1_word'][2]
    caps = [('c_hook', 0, s1tap + 0.15), ('c_now', s1tap + 0.25, starts['S2_words']),
            ('c_tap', starts['S2_words'], starts['S3_sentence']), (f'c_book{g}', starts['S3_sentence'], starts['S4_slow']),
            ('c_slow', starts['S4_slow'], starts['S5_build']), ('c_build', starts['S5_build'], T)]
    def composite(src, out, windows, length):
        inputs = ['-loop','1','-t',f'{length:.3f}','-i',os.path.join(CAP,'bg.png'), '-i', src,
                  '-loop','1','-t',f'{length:.3f}','-i',os.path.join(CAP,'mask.png')]
        for c,_,_ in windows: inputs += ['-i', os.path.join(CAP, c + '.png')]
        fc = ("[1]scale=778:1382:flags=lanczos,format=rgba[scr];"
              "[2]crop=778:1382:151:452,format=gray[m];[scr][m]alphamerge[ph];[0][ph]overlay=151:452:shortest=1[v0]")
        for i,(c,a,b) in enumerate(windows):
            fc += f";[v{i}][{3+i}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{i+1}]"
        fc += f";[v{len(windows)}]fps=30,format=yuv420p[v]"
        R('ffmpeg','-loglevel','error','-y',*inputs,'-filter_complex',fc,'-map','[v]','-t',f'{length:.3f}',
          '-c:v','libx264','-crf','17','-preset','medium',out)
    composite(os.path.join(work,'screen.mp4'), os.path.join(work,'body.mp4'), caps, T)
    end_len = 3.0
    R('ffmpeg','-loglevel','error','-y','-loop','1','-t',str(end_len),'-i',END,'-vf','fps=30,format=yuv420p,fade=t=in:st=0:d=0.3',
      '-c:v','libx264','-crf','17',os.path.join(work,'end.mp4'))
    open(os.path.join(work,'all.txt'),'w').write("file 'body.mp4'\nfile 'end.mp4'\n")
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',os.path.join(work,'all.txt'),'-c','copy',os.path.join(work,'video.mp4'))
    total = T + end_len
    clips = [(f, starts[s] + a, tempo) for s in order for (f, a, tempo) in plan[s][0]]
    def mix(clips, length, out):
        inp, fc = [], ''
        for i,(f,a,tempo) in enumerate(clips):
            inp += ['-i', f]; ms = int(a*1000)
            fc += f"[{i}]aresample=48000,aformat=channel_layouts=stereo,{'atempo=%.2f,' % tempo if tempo != 1 else ''}adelay={ms}|{ms}[a{i}];"
        fc += ''.join(f'[a{i}]' for i in range(len(clips))) + f"amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{length:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[out]"
        R('ffmpeg','-loglevel','error','-y',*inp,'-filter_complex',fc,'-map','[out]','-c:a','pcm_s16le',out)
    mix(clips, total, os.path.join(work,'audio.wav'))
    final = os.path.join(HERE, f'jisr-script3-class{g}-1080x1920.mp4')
    R('ffmpeg','-loglevel','error','-y','-i',os.path.join(work,'video.mp4'),'-i',os.path.join(work,'audio.wav'),'-map','0:v','-map','1:a',
      '-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',final)
    # Short cut: hook + sentence scene + end card (about 10 s)
    cut_order = ['S1_word', 'S3_sentence']
    open(os.path.join(work,'cut_screen.txt'),'w').write(''.join(f"file '{s}.mp4'\n" for s in cut_order))
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',os.path.join(work,'cut_screen.txt'),'-c','copy',os.path.join(work,'cut_screen.mp4'))
    L1, L3 = plan['S1_word'][1], plan['S3_sentence'][1]
    composite(os.path.join(work,'cut_screen.mp4'), os.path.join(work,'cut_body.mp4'),
              [('c_hook', 0, s1tap + 0.15), ('c_now', s1tap + 0.25, L1), (f'c_book{g}', L1, L1 + L3)], L1 + L3)
    R('ffmpeg','-loglevel','error','-y','-loop','1','-t','2.5','-i',END,'-vf','fps=30,format=yuv420p,fade=t=in:st=0:d=0.3','-c:v','libx264','-crf','17',os.path.join(work,'cut_end.mp4'))
    open(os.path.join(work,'cut_all.txt'),'w').write("file 'cut_body.mp4'\nfile 'cut_end.mp4'\n")
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',os.path.join(work,'cut_all.txt'),'-c','copy',os.path.join(work,'cut_video.mp4'))
    cut_clips = [(f, a, t) for (f, a, t) in plan['S1_word'][0]] + [(f, L1 + a, t) for (f, a, t) in plan['S3_sentence'][0]]
    mix(cut_clips, L1 + L3 + 2.5, os.path.join(work,'cut_audio.wav'))
    cut = os.path.join(HERE, f'jisr-script3-class{g}-short-1080x1920.mp4')
    R('ffmpeg','-loglevel','error','-y','-i',os.path.join(work,'cut_video.mp4'),'-i',os.path.join(work,'cut_audio.wav'),'-map','0:v','-map','1:a',
      '-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',cut)
    json.dump({'scenes': {s: round(plan[s][1],2) for s in order}, 'captions': [(c, round(a,2), round(b,2)) for c,a,b in caps],
               'audio': [(os.path.basename(f), round(a,2), t) for f,a,t in clips]}, open(os.path.join(work,'plan.json'),'w'), indent=1)
    print(f'Class {g}: master {total:.1f}s, short {L1+L3+2.5:.1f}s')

for g in map(int, sys.argv[1:] or [5, 2, 8]):
    build(g)
