import subprocess, json, sys
R = lambda *a: subprocess.run(list(a), check=True)
dur = lambda f: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
M = json.load(open('meta_v2.json'))
def ev(shot, prefix, nth=0):
    hits = [e['t'] for e in M[shot]['events'] if e['name'].startswith(prefix)]
    return hits[nth] if len(hits) > nth else None
VO = {k: dur(f'vo/{k}.wav') for k in ['vo1','vo2','vo3','vo4','vo5','vo6','vo7','vo8']}
W1, W06, S2 = dur('aud/word_1.mp3'), dur('aud/word_06.mp3'), dur('aud/sent2.mp3')
for s in ['A_lesson','B_tapword','C_slow','E_drill']:
    R('ffmpeg','-loglevel','error','-y','-f','concat','-i',f'shots2/{s}/list.txt','-vf','fps=30,format=yuv420p','-c:v','libx264','-crf','16','-preset','medium',f'shots2/{s}.mp4')
V = '-c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -an'.split()
def seg(name, inputs, fc): R('ffmpeg','-loglevel','error','-y',*inputs,'-filter_complex',fc,'-map','[v]',*V,f'seg2_{name}.mp4')
ov = lambda base,cap,a,b,out: f"[{base}][{cap}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[{out}]"
audio = []   # (file, absolute start, volume)
T = 0.0
# 1 hook
L1 = 7.1
seg('1',['-i','cap/sheet.png','-i','cap/hook1.png','-i','cap/hook2.png'],
  "[0]scale=2592:4608,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=213:s=1080x1920:fps=30[z];"+ov('z','1',0,3.3,'a')+';'+ov('a','2',3.3,7.2,'w')+';[w]trim=duration=7.1[v]')
audio += [('vo/vo1.wav', 0.35, 1), ('vo/vo2.wav', 3.5, 1)]; T += L1
# 2 lesson
L2 = max(4.2, VO['vo3'] + 0.5); dA = dur('shots2/A_lesson.mp4')
seg('2',['-i','shots2/A_lesson.mp4','-i','cap/s3.png'], f"[0]fps=30,tpad=stop_mode=clone:stop_duration={max(0,L2-dA)+0.1:.2f},trim=duration={L2:.2f}[b];"+ov('b','1',0,L2,'v'))
audio += [('vo/vo3.wav', T + 0.2, 1)]; T += L2
# 3 tap word
dB = dur('shots2/B_tapword.mp4'); pB = (ev('B_tapword','audio:') or ev('B_tapword','tap:') + 0.3) + 0.12
v4 = pB + W1 + 0.15; L3 = v4 + VO['vo4'] + 0.3
seg('3',['-i','shots2/B_tapword.mp4','-i','cap/s4.png'], f"[0]fps=30,tpad=stop_mode=clone:stop_duration={max(0,L3-dB)+0.1:.2f},trim=duration={L3:.2f}[b];"+ov('b','1',v4-0.1,L3,'v'))
audio += [('aud/word_1.mp3', T + pB, .9), ('vo/vo4.wav', T + v4, 1)]; T += L3
# 4 slow: hold first frame so the voiceover finishes before the slowed word plays
dC = dur('shots2/C_slow.mp4'); tW = ev('C_slow','tap:word'); pC = (ev('C_slow','audio:') or tW + 0.3) + 0.12
H = max(0.4, VO['vo5'] + 0.25 - pC); L4 = H + pC + W06 + 0.35
seg('4',['-i','shots2/C_slow.mp4','-i','cap/s5.png'], f"[0]fps=30,tpad=start_mode=clone:start_duration={H:.2f}:stop_mode=clone:stop_duration={max(0,L4-H-dC)+0.1:.2f},trim=duration={L4:.2f}[b];"+ov('b','1',0,VO['vo5']+0.15,'v'))
audio += [('vo/vo5.wav', T + 0.1, 1), ('aud/word_06.mp3', T + H + pC, .9)]; T += L4
# 5 sentence drill
dE = dur('shots2/E_drill.mp4'); pE = (ev('E_drill','audio:') or ev('E_drill','tap:') + 0.3) + 0.12
H5 = max(0.3, VO['vo6'] + 0.3 - pE); s_end = H5 + pE + S2; v7 = s_end + 0.2; L5 = v7 + VO['vo7'] + 0.35
seg('5',['-i','shots2/E_drill.mp4','-i','cap/s6.png','-i','cap/s7.png'],
  f"[0]fps=30,tpad=start_mode=clone:start_duration={H5:.2f}:stop_mode=clone:stop_duration={max(0,L5-H5-dE)+0.1:.2f},trim=duration={L5:.2f}[b];"+ov('b','1',0,VO['vo6']+0.2,'c')+';'+ov('c','2',v7-0.1,L5,'v'))
audio += [('vo/vo6.wav', T + 0.1, 1), ('aud/sent2.mp3', T + H5 + pE, .9), ('vo/vo7.wav', T + v7, 1)]; T += L5
# 6 end card
L6 = 3.4
seg('6',['-loop','1','-t',str(L6),'-i','cap/endcard.png'], "[0]fps=30,format=yuv420p,fade=t=in:st=0:d=0.35[v]")
audio += [('vo/vo8.wav', T + 0.3, 1)]; T += L6
open('segs2.txt','w').write(''.join(f"file 'seg2_{i}.mp4'\n" for i in range(1,7)))
R('ffmpeg','-loglevel','error','-y','-f','concat','-i','segs2.txt','-c','copy','video2_noaudio.mp4')
inp=[]; fc=''
for i,(f,t,v) in enumerate(audio):
    inp += ['-i', f]; ms = int(t*1000); fc += f"[{i}]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[a{i}];"
fc += ''.join(f'[a{i}]' for i in range(len(audio))) + f"amix=inputs={len(audio)}:normalize=0,apad,atrim=0:{T:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
R('ffmpeg','-loglevel','error','-y',*inp,'-filter_complex',fc,'-map','[aout]','-c:a','pcm_s16le','audio2.wav')
R('ffmpeg','-loglevel','error','-y','-i','video2_noaudio.mp4','-i','audio2.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','final2.mp4')
print('total', round(T,2), 'scenes', [round(x,2) for x in (L1,L2,L3,L4,L5,L6)])
json.dump([(f,round(t,2)) for f,t,_ in audio], open('audio_plan.json','w'), indent=1)
