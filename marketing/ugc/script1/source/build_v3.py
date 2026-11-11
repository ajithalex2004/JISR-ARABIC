import subprocess, json, sys
R = lambda *a: subprocess.run(list(a), check=True)
dur = lambda f: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
M = json.load(open('meta_v2.json'))
def ev(shot, prefix, nth=0):
    hits = [e['t'] for e in M[shot]['events'] if e['name'].startswith(prefix)]
    return hits[nth] if len(hits) > nth else None
VO = {k: dur(f'vo3/{k}.wav') for k in ['h1','p1','d1','f1','f2','f3','f4','e1','c1','c2']}
W1, W06, S2 = dur('aud/word_1.mp3'), dur('aud/word_06.mp3'), dur('aud/sent2.mp3')
for s in []:
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',f'shots2/{s}/list.txt','-vf','fps=30,format=yuv420p','-c:v','libx264','-crf','16','-preset','medium',f'shots2/{s}.mp4')
V = '-c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -an'.split()
def seg(name, inputs, fc): R('ffmpeg','-loglevel','error','-y',*inputs,'-filter_complex',fc,'-map','[v]',*V,f'seg3_{name}.mp4')
ov = lambda base,cap,a,b,out: f"[{base}][{cap}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[{out}]"
audio = []   # (file, absolute start, volume)
T = 0.0
# 1 hook
p1s = 0.3 + VO['h1'] + 0.35; L1 = round(p1s + VO['p1'] + 0.35, 2); NF = int(L1 * 30) + 2
seg('1',['-i','cap3/sheet.png','-i','cap3/hook1.png','-i','cap3/hook2.png'],
  f"[0]scale=2592:4608,zoompan=z='1+0.0004*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={NF}:s=1080x1920:fps=30[z];"+ov('z','1',0,p1s-0.1,'a')+';'+ov('a','2',p1s-0.1,L1+0.1,'w')+f';[w]trim=duration={L1}[v]')
audio += [('vo3/h1.wav', 0.3, 1), ('vo3/p1.wav', p1s, 1)]; T += L1
# 2 lesson
f1s = 0.2 + VO['d1'] + 0.3; L2 = f1s + VO['f1'] + 0.35; dA = dur('shots2/A_lesson.mp4')
seg('2',['-i','shots2/A_lesson.mp4','-i','cap3/s3.png','-i','cap3/s3b.png'], f"[0]fps=30,tpad=stop_mode=clone:stop_duration={max(0,L2-dA)+0.1:.2f},trim=duration={L2:.2f}[b];"+ov('b','1',0,f1s-0.05,'c')+';'+ov('c','2',f1s-0.05,L2,'v'))
audio += [('vo3/d1.wav', T + 0.2, 1), ('vo3/f1.wav', T + f1s, 1)]; T += L2
# 3 tap word
dB = dur('shots2/B_tapword.mp4'); pB = (ev('B_tapword','audio:') or ev('B_tapword','tap:') + 0.3) + 0.12
v4 = pB + W1 + 0.15; L3 = v4 + VO['f2'] + 0.3
seg('3',['-i','shots2/B_tapword.mp4','-i','cap3/s4.png'], f"[0]fps=30,tpad=stop_mode=clone:stop_duration={max(0,L3-dB)+0.1:.2f},trim=duration={L3:.2f}[b];"+ov('b','1',v4-0.1,L3,'v'))
audio += [('aud/word_1.mp3', T + pB, .9), ('vo3/f2.wav', T + v4, 1)]; T += L3
# 4 slow: hold first frame so the voiceover finishes before the slowed word plays
dC = dur('shots2/C_slow.mp4'); tW = ev('C_slow','tap:word'); pC = (ev('C_slow','audio:') or tW + 0.3) + 0.12
H = max(0.4, VO['f3'] + 0.25 - pC); L4 = H + pC + W06 + 0.35
seg('4',['-i','shots2/C_slow.mp4','-i','cap3/s5.png'], f"[0]fps=30,tpad=start_mode=clone:start_duration={H:.2f}:stop_mode=clone:stop_duration={max(0,L4-H-dC)+0.1:.2f},trim=duration={L4:.2f}[b];"+ov('b','1',0,VO['f3']+0.15,'v'))
audio += [('vo3/f3.wav', T + 0.1, 1), ('aud/word_06.mp3', T + H + pC, .9)]; T += L4
# 5 sentence drill
dE = dur('shots2/E_drill.mp4'); pE = (ev('E_drill','audio:') or ev('E_drill','tap:') + 0.3) + 0.12
H5 = max(0.3, VO['f4'] + 0.3 - pE); s_end = H5 + pE + S2; v7 = s_end + 0.2; L5 = v7 + VO['e1'] + 0.45
seg('5',['-i','shots2/E_drill.mp4','-i','cap3/s6.png','-i','cap3/s7.png'],
  f"[0]fps=30,tpad=start_mode=clone:start_duration={H5:.2f}:stop_mode=clone:stop_duration={max(0,L5-H5-dE)+0.1:.2f},trim=duration={L5:.2f}[b];"+ov('b','1',0,VO['f4']+0.2,'c')+';'+ov('c','2',v7-0.1,L5,'v'))
audio += [('vo3/f4.wav', T + 0.1, 1), ('aud/sent2.mp3', T + H5 + pE, .9), ('vo3/e1.wav', T + v7, 1)]; T += L5
# 6 end card
c2s = 0.3 + VO['c1'] + 0.3; L6 = round(c2s + VO['c2'] + 0.7, 2)
seg('6',['-loop','1','-t',str(L6),'-i','cap3/endcard.png'], "[0]fps=30,format=yuv420p,fade=t=in:st=0:d=0.35[v]")
audio += [('vo3/c1.wav', T + 0.3, 1), ('vo3/c2.wav', T + c2s, 1)]; T += L6
open('segs3.txt','w').write(''.join(f"file 'seg3_{i}.mp4'\n" for i in range(1,7)))
R('ffmpeg','-loglevel','error','-y','-f','concat','-i','segs3.txt','-c','copy','video3_noaudio.mp4')
inp=[]; fc=''
for i,(f,t,v) in enumerate(audio):
    inp += ['-i', f]; ms = int(t*1000); fc += f"[{i}]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[a{i}];"
fc += ''.join(f'[a{i}]' for i in range(len(audio))) + f"amix=inputs={len(audio)}:normalize=0,apad,atrim=0:{T:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
R('ffmpeg','-loglevel','error','-y',*inp,'-filter_complex',fc,'-map','[aout]','-c:a','pcm_s16le','audio3.wav')
R('ffmpeg','-loglevel','error','-y','-i','video3_noaudio.mp4','-i','audio3.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','final3.mp4')
print('total', round(T,2), 'scenes', [round(x,2) for x in (L1,L2,L3,L4,L5,L6)])
json.dump([(f,round(t,2)) for f,t,_ in audio], open('audio_plan3.json','w'), indent=1)
