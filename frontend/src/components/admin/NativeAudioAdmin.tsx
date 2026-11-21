import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Download, Mic, Play, Square, Trash2, Upload } from 'lucide-react';
import { api, API_BASE } from '../../services/api';

type ScriptItem = { text: string; group: string; hint: string; recording_id: string | null; url: string | null; speaker: string | null };
type Script = { total: number; recorded: number; items: ScriptItem[] };

const PAGE = 60;
const SPEAKER_KEY = 'jisr.admin.audioSpeaker';

function preferredMime(): string {
  const options = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
  if (typeof MediaRecorder === 'undefined') return '';
  return options.find((m) => MediaRecorder.isTypeSupported?.(m)) || '';
}

function extensionFor(mime: string): string {
  if (mime.includes('mp4')) return 'm4a';
  if (mime.includes('ogg')) return 'ogg';
  if (mime.includes('mpeg')) return 'mp3';
  if (mime.includes('wav')) return 'wav';
  return 'webm';
}

/**
 * Native-speaker recordings for the Basic Foundation course. Each clip is recorded for one exact
 * text (letter name, syllable, word or sentence); wherever the app plays that text, the recording is
 * used instead of the synthetic voice.
 */
export function NativeAudioAdmin() {
  const [script, setScript] = useState<Script | null>(null);
  const [group, setGroup] = useState('all');
  const [status, setStatus] = useState<'missing' | 'recorded' | 'all'>('missing');
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(PAGE);
  const [speaker, setSpeaker] = useState(() => { try { return localStorage.getItem(SPEAKER_KEY) || ''; } catch { return ''; } });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [recordingText, setRecordingText] = useState<string | null>(null);
  const [busyText, setBusyText] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const player = useRef<HTMLAudioElement | null>(null);

  const load = async () => {
    try { setScript(await api.adminListRecordings()); } catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);
  useEffect(() => { try { localStorage.setItem(SPEAKER_KEY, speaker); } catch { /* private mode */ } }, [speaker]);

  const groups = useMemo(() => Array.from(new Set((script?.items || []).map((i) => i.group))), [script]);
  const shown = useMemo(() => (script?.items || []).filter((i) =>
    (group === 'all' || i.group === group) &&
    (status === 'all' || (status === 'recorded') === !!i.recording_id) &&
    (!query.trim() || i.text.includes(query.trim()) || i.hint.toLowerCase().includes(query.trim().toLowerCase()))), [script, group, status, query]);

  const play = (url: string) => {
    if (!player.current) player.current = new Audio();
    player.current.src = url.startsWith('http') ? url : `${API_BASE}${url}`;
    player.current.play().catch(() => setError('Could not play the clip.'));
  };

  const save = async (text: string, blob: Blob, fileName: string) => {
    setBusyText(text);
    setError('');
    try {
      await api.adminSaveRecording(text, blob, fileName, speaker);
      setNotice(`Saved: ${text}`);
      await load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusyText(null);
    }
  };

  const startRecording = async (text: string) => {
    setError('');
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setError('This browser cannot record audio. Use Upload instead, or a recent Chrome, Edge or Safari.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = preferredMime();
      const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      chunks.current = [];
      rec.ondataavailable = (e) => { if (e.data.size) chunks.current.push(e.data); };
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const type = (rec.mimeType || mime || 'audio/webm').split(';')[0];
        const blob = new Blob(chunks.current, { type });
        setRecordingText(null);
        save(text, blob, `recording.${extensionFor(type)}`);
      };
      recorder.current = rec;
      rec.start();
      setRecordingText(text);
    } catch {
      setError('Microphone access was refused. Allow the microphone for this site and try again.');
    }
  };

  const stopRecording = () => recorder.current?.stop();

  const remove = async (item: ScriptItem) => {
    if (!item.recording_id || !window.confirm(`Delete the recording of "${item.text}"? The synthetic voice will be used again.`)) return;
    try { await api.adminDeleteRecording(item.recording_id); await load(); } catch (e: any) { setError(e.message); }
  };

  const downloadScript = () => {
    const rows = [['group', 'text', 'hint', 'recorded'], ...(script?.items || []).map((i) => [i.group, i.text, i.hint, i.recording_id ? 'yes' : 'no'])];
    const csv = '﻿' + rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url; a.download = 'jisr-foundation-recording-script.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  const pct = script ? Math.round((script.recorded / Math.max(script.total, 1)) * 100) : 0;

  return <div className="space-y-4">
    <div className="bg-white border border-slate-200 p-4 space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-black text-emerald-950 flex items-center gap-1.5"><Mic className="w-4 h-4" /> Native audio</h2>
          <p className="text-xs text-slate-600 max-w-3xl">
            Record a native speaker for each letter, syllable, word and sentence of the Basic Foundation course. Wherever the app plays that
            exact text, learners hear the recording instead of the synthetic voice, and the audio bar shows "Native speaker".
          </p>
        </div>
        <button type="button" onClick={downloadScript} disabled={!script} className="px-3 py-1.5 text-xs font-bold border border-slate-300 inline-flex items-center gap-1.5 disabled:opacity-50">
          <Download className="w-3.5 h-3.5" /> Recording script (CSV)
        </button>
      </div>
      {script && <div className="text-sm">
        <b>{script.recorded}</b> of {script.total} recorded ({pct}%)
        <div className="w-full max-w-md h-2 bg-slate-100 mt-1"><div className="h-2 bg-emerald-700" style={{ width: `${pct}%` }} /></div>
      </div>}
      <div className="flex flex-wrap items-end gap-2 text-xs">
        <label className="font-bold text-slate-700">Speaker
          <input value={speaker} onChange={(e) => setSpeaker(e.target.value)} placeholder="e.g. Ustadha Huda" className="block border border-slate-300 px-2 py-1 text-sm font-normal" />
        </label>
        <label className="font-bold text-slate-700">Group
          <select value={group} onChange={(e) => { setGroup(e.target.value); setLimit(PAGE); }} className="block border border-slate-300 px-2 py-1 text-sm font-normal">
            <option value="all">All</option>
            {groups.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
        <label className="font-bold text-slate-700">Show
          <select value={status} onChange={(e) => { setStatus(e.target.value as any); setLimit(PAGE); }} className="block border border-slate-300 px-2 py-1 text-sm font-normal">
            <option value="missing">Not recorded yet</option><option value="recorded">Recorded</option><option value="all">All</option>
          </select>
        </label>
        <label className="font-bold text-slate-700">Search
          <input value={query} onChange={(e) => { setQuery(e.target.value); setLimit(PAGE); }} className="block border border-slate-300 px-2 py-1 text-sm font-normal" />
        </label>
      </div>
      <p className="text-[11px] text-slate-500">Tips: record in a quiet room, say exactly the text shown with its vowel marks, leave half a second of silence before and after. Each clip can be up to 2 MB.</p>
      {notice && <p className="text-xs text-emerald-900 bg-emerald-50 border border-emerald-200 px-3 py-2">{notice}</p>}
      {error && <p role="alert" className="text-xs text-red-800 bg-red-50 border border-red-200 px-3 py-2">{error}</p>}
    </div>

    <div className="bg-white border border-slate-200 divide-y divide-slate-100">
      {script === null && <p className="p-3 text-sm text-slate-500">Loading…</p>}
      {script && shown.length === 0 && <p className="p-3 text-sm text-slate-500">Nothing to show with these filters.</p>}
      {shown.slice(0, limit).map((item) => {
        const isRecording = recordingText === item.text;
        return (
          <div key={item.text} className="flex flex-wrap items-center gap-3 px-3 py-2">
            <span className="text-2xl font-arabic font-bold text-slate-900 min-w-[6rem]" dir="rtl">{item.text}</span>
            <span className="text-[11px] text-slate-500 flex-1 min-w-[8rem]">{item.group} · {item.hint}</span>
            {item.recording_id
              ? <span className="text-[11px] font-bold text-emerald-800">✓ Recorded{item.speaker ? ` (${item.speaker})` : ''}</span>
              : <span className="text-[11px] font-bold text-amber-800">Synthetic voice</span>}
            <div className="flex items-center gap-1.5">
              {item.url && <button type="button" onClick={() => play(item.url!)} aria-label={`Play the recording of ${item.text}`} className="p-1.5 border border-slate-300"><Play className="w-4 h-4" /></button>}
              {isRecording ? (
                <button type="button" onClick={stopRecording} className="px-2 py-1 text-xs font-bold bg-red-700 text-white inline-flex items-center gap-1 animate-pulse"><Square className="w-3.5 h-3.5" /> Stop & save</button>
              ) : (
                <button type="button" onClick={() => startRecording(item.text)} disabled={!!recordingText || busyText === item.text}
                  className="px-2 py-1 text-xs font-bold bg-emerald-900 text-white inline-flex items-center gap-1 disabled:opacity-50"><Mic className="w-3.5 h-3.5" /> {item.recording_id ? 'Re-record' : 'Record'}</button>
              )}
              <label className="px-2 py-1 text-xs font-bold border border-slate-300 inline-flex items-center gap-1 cursor-pointer">
                <Upload className="w-3.5 h-3.5" /> Upload
                <input type="file" accept="audio/*" className="hidden" onChange={(e) => {
                  const f = e.target.files?.[0];
                  e.target.value = '';
                  if (f) save(item.text, f, f.name);
                }} />
              </label>
              {item.recording_id && <button type="button" onClick={() => remove(item)} aria-label={`Delete the recording of ${item.text}`} className="p-1.5 border border-red-200 text-red-700"><Trash2 className="w-4 h-4" /></button>}
            </div>
          </div>
        );
      })}
      {shown.length > limit && (
        <button type="button" onClick={() => setLimit(limit + PAGE)} className="w-full py-2 text-xs font-bold text-emerald-900">Show more ({shown.length - limit} left)</button>
      )}
    </div>
  </div>;
}
