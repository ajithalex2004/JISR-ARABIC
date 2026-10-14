import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { formatDate } from './PaymentsAdmin';

type Failure = { at: string; detail: string };
type Component = {
  key: string;
  label: string;
  failures_in_window: number;
  recent_failures: Failure[];
  last_alert?: { at: string; subject: string; delivered_to: string[]; errors: string[] } | null;
};
type Health = {
  threshold: number;
  window_minutes: number;
  cooldown_minutes: number;
  email_configured: boolean;
  recipients: string[];
  webhook_configured: boolean;
  gemini_configured: boolean;
  components: Component[];
  last_gemini_check?: { ok: boolean; model: string; error?: string | null; latency_ms?: number; at: string } | null;
  schema?: { missing_columns: string[]; error?: string };
  last_weekly_reports?: { week: string; sent: number; skipped: number; failed: number; error?: string; at: string } | null;
};

export function SystemHealth() {
  const [health, setHealth] = useState<Health | null>(null);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = async () => {
    try { setHealth(await api.adminSystemHealth()); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  const act = async (action: 'check-gemini' | 'test-alert' | 'send-weekly-reports') => {
    setBusy(action);
    setError('');
    setNotice('');
    try {
      const res = await api.adminSystemAction(action);
      if (action === 'check-gemini') {
        setNotice(res.ok ? `Gemini (${res.model}) is working · ${res.latency_ms} ms` : `Gemini (${res.model}) failed: ${res.error}`);
      } else if (action === 'test-alert') {
        setNotice(res.delivered_to.length ? `Test alert sent to ${res.delivered_to.join(', ')}` : `Test alert could not be delivered: ${res.errors.join('; ')}`);
      } else {
        setNotice(res.error ? `Weekly reports not sent: ${res.error}` : `Weekly reports for ${res.week}: ${res.sent} sent, ${res.skipped} already sent, ${res.failed} failed`);
      }
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setBusy(''); }
  };

  const gemini = health?.last_gemini_check;
  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">System health & alerts</h2>
      <button type="button" onClick={load} className="border border-slate-400 px-3 py-1.5 text-sm">Refresh</button>
    </div>
    {health && <p className="text-sm text-slate-600">
      An alert is emailed when a service fails {health.threshold} times within {health.window_minutes} minutes, at most once every {health.cooldown_minutes} minutes per service.
      Gemini is checked automatically every 20 minutes.
    </p>}
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {notice && <p role="status" className="text-emerald-800 text-sm font-semibold">{notice}</p>}
    {health && <>
      <div className="grid gap-2 sm:grid-cols-3 text-sm">
        <div className="border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Alerts go to</div>
          <div className="break-all">{health.email_configured ? (health.recipients.join(', ') || 'No admin emails found') : 'Email is not configured'}</div>
          {health.webhook_configured && <div className="text-xs text-slate-500">+ chat webhook</div>}
        </div>
        <div className="border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Last Gemini check</div>
          {gemini ? <div className={gemini.ok ? 'text-emerald-800 font-semibold' : 'text-red-700 font-semibold'}>
            {gemini.ok ? 'Working' : 'Failing'} · {formatDate(gemini.at)}
            {!gemini.ok && gemini.error && <div className="text-xs font-normal break-words">{gemini.error}</div>}
          </div> : <div>{health.gemini_configured ? 'Not checked yet' : 'GEMINI_API_KEY is not set'}</div>}
        </div>
        <div className="border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Last weekly parent emails</div>
          {health.last_weekly_reports ? <div>{health.last_weekly_reports.week}: {health.last_weekly_reports.sent} sent, {health.last_weekly_reports.failed} failed
            <div className="text-xs text-slate-500">{formatDate(health.last_weekly_reports.at)}</div></div>
            : <div>Sent every Sunday at 08:00 UAE time</div>}
        </div>
      </div>
      {health.schema && <div className={`border p-3 text-sm ${health.schema.missing_columns.length || health.schema.error ? 'border-red-300 bg-red-50' : 'border-slate-200 bg-slate-50'}`}>
        <span className="text-xs text-slate-500 block">Database</span>
        {health.schema.error ? <span className="text-red-700">Could not check: {health.schema.error}</span>
          : health.schema.missing_columns.length
            ? <span className="text-red-700 font-semibold">Missing columns: {health.schema.missing_columns.join(', ')}. They are added automatically on the next deploy.</span>
            : <span className="text-emerald-800 font-semibold">Matches the app (no missing columns)</span>}
      </div>}
      <div className="flex flex-wrap gap-2">
        <button type="button" disabled={!!busy} onClick={() => act('check-gemini')} className="bg-emerald-900 text-white px-3 py-1.5 text-sm disabled:opacity-50">{busy === 'check-gemini' ? 'Checking…' : 'Check Gemini now'}</button>
        <button type="button" disabled={!!busy} onClick={() => act('test-alert')} className="border border-slate-400 px-3 py-1.5 text-sm disabled:opacity-50">{busy === 'test-alert' ? 'Sending…' : 'Send test alert'}</button>
        <button type="button" disabled={!!busy} onClick={() => { if (window.confirm('Email this week\'s progress report now to every parent who opted in and has not received it yet this week?')) act('send-weekly-reports'); }} className="border border-slate-400 px-3 py-1.5 text-sm disabled:opacity-50">{busy === 'send-weekly-reports' ? 'Sending…' : 'Send weekly reports now'}</button>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {health.components.map(c => <div key={c.key} className={`border p-3 ${c.failures_in_window ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}>
          <div className="flex justify-between gap-2">
            <span className="font-semibold text-slate-900">{c.label}</span>
            <span className={`text-xs font-bold px-2 py-0.5 ${c.failures_in_window ? 'bg-red-200 text-red-900' : 'bg-emerald-100 text-emerald-900'}`}>
              {c.failures_in_window ? `${c.failures_in_window} failure${c.failures_in_window === 1 ? '' : 's'} recently` : 'OK'}
            </span>
          </div>
          {c.last_alert && <div className="text-xs text-slate-600 mt-1">Last alert {formatDate(c.last_alert.at)}{c.last_alert.delivered_to.length ? ` to ${c.last_alert.delivered_to.join(', ')}` : ' (not delivered)'}</div>}
          {c.recent_failures.length > 0 ? <ul className="mt-2 space-y-1 text-xs text-slate-700 max-h-40 overflow-y-auto">
            {c.recent_failures.slice(0, 5).map((f, i) => <li key={i}><span className="text-slate-500">{formatDate(f.at)}</span> · <span className="break-words">{f.detail}</span></li>)}
          </ul> : <p className="mt-2 text-xs text-slate-500">No failures recorded in the last 7 days.</p>}
        </div>)}
      </div>
    </>}
  </section>;
}
