import React from 'react';
import { formatDate } from './PaymentsAdmin';

type Row = { name: string; calls: number; ok: number; input_tokens: number; output_tokens: number; cost_usd: number };
export type AIProvider = {
  name: string;
  configured: boolean;
  switched_until: string | null;
  consecutive_failures: number;
  models?: { fast: string; strong: string };
};
export type AIUsageReport = {
  month: string;
  budget_usd: number | null;
  budget_used_pct?: number;
  daily_limit: number;
  hard_stop: boolean;
  prices_configured: string[];
  calls: number;
  failed_calls: number;
  fallback_calls: number;
  unpriced_calls: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  by_feature: Row[];
  by_provider: Row[];
  error?: string;
};
export type AISection = { providers: AIProvider[]; usage: AIUsageReport | null; error?: string };

const FEATURES: Record<string, string> = {
  ask_fahim: 'Ask Fahim',
  learn_with_fahim: 'Learn with Fahim',
  paper_solver: 'Question paper solver',
  textbook_reading: 'Textbook page reading',
  lesson_drafting: 'Lesson drafting',
  word_meaning: 'Word meanings',
  model_answer: 'Model answers',
  health_check: 'Health checks',
};
const PROVIDERS: Record<string, string> = { gemini: 'Gemini (Google)', anthropic: 'Claude (Anthropic)' };

const usd = (n: number) => `$${n < 1 ? n.toFixed(4) : n.toFixed(2)}`;
const tokens = (n: number) => n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(n);

function Table({ title, rows, labels }: { title: string; rows: Row[]; labels: Record<string, string> }) {
  return <div className="overflow-x-auto">
    <table className="w-full text-sm border-collapse">
      <thead><tr className="text-left text-xs text-slate-500 border-b border-slate-200">
        <th className="py-1 pr-2">{title}</th><th className="py-1 px-2 text-right">Calls</th><th className="py-1 px-2 text-right">Failed</th>
        <th className="py-1 px-2 text-right">Tokens in / out</th><th className="py-1 pl-2 text-right">Cost</th>
      </tr></thead>
      <tbody>{rows.map(r => <tr key={r.name} className="border-b border-slate-100">
        <td className="py-1 pr-2">{labels[r.name] || r.name}</td>
        <td className="py-1 px-2 text-right">{r.calls}</td>
        <td className={`py-1 px-2 text-right ${r.calls - r.ok ? 'text-red-700' : 'text-slate-400'}`}>{r.calls - r.ok}</td>
        <td className="py-1 px-2 text-right">{tokens(r.input_tokens)} / {tokens(r.output_tokens)}</td>
        <td className="py-1 pl-2 text-right">{usd(r.cost_usd)}</td>
      </tr>)}</tbody>
    </table>
  </div>;
}

export function AICostPanel({ ai }: { ai: AISection }) {
  const u = ai.usage;
  const pct = u?.budget_used_pct ?? 0;
  return <div className="border border-slate-200 p-3 space-y-3 text-sm">
    <div className="font-semibold text-slate-900">AI providers & spending</div>
    {ai.error && <p className="text-red-700">Could not load: {ai.error}</p>}
    <div className="grid gap-2 sm:grid-cols-2">
      {ai.providers.map((p, i) => {
        const active = p.configured && !p.switched_until;
        return <div key={p.name} className={`border p-2 ${p.switched_until ? 'border-amber-300 bg-amber-50' : 'border-slate-200 bg-slate-50'}`}>
          <div className="flex justify-between gap-2">
            <span className="font-semibold">{PROVIDERS[p.name] || p.name}{i === 0 ? ' · main' : ' · fallback'}</span>
            <span className={`text-xs font-bold px-2 py-0.5 ${!p.configured ? 'bg-slate-200 text-slate-700' : active ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-200 text-amber-900'}`}>
              {!p.configured ? 'Not set up' : active ? 'In use' : 'Set aside'}
            </span>
          </div>
          {p.switched_until && <div className="text-xs text-amber-900 mt-1">Requests go to the next provider until {formatDate(p.switched_until)}</div>}
          {p.consecutive_failures > 0 && <div className="text-xs text-red-700 mt-1">{p.consecutive_failures} failure{p.consecutive_failures === 1 ? '' : 's'} in a row</div>}
          {!p.configured && p.name === 'anthropic' && <div className="text-xs text-slate-500 mt-1">Set ANTHROPIC_API_KEY to turn on automatic fallback.</div>}
          {p.configured && p.models && <div className="text-xs text-slate-500 mt-1">Chat: {p.models.fast} · Reading/drafting: {p.models.strong}</div>}
        </div>;
      })}
    </div>
    <p className="text-xs text-slate-500">
      After a credit or quota error, or 3 failures in a row, a provider is set aside for 10 minutes, requests go to the next one and an alert is emailed.
    </p>
    {u && <>
      {u.error && <p className="text-red-700">Usage could not be read: {u.error}</p>}
      <div className="grid gap-2 grid-cols-2 sm:grid-cols-4">
        <div className="border border-slate-200 bg-slate-50 p-2"><div className="text-xs text-slate-500">Cost in {u.month}</div><div className="text-lg font-bold">{usd(u.cost_usd)}</div>
          {u.budget_usd ? <div className="text-xs">{pct}% of {usd(u.budget_usd)} budget</div> : <div className="text-xs text-slate-500">No monthly budget set</div>}</div>
        <div className="border border-slate-200 bg-slate-50 p-2"><div className="text-xs text-slate-500">AI calls</div><div className="text-lg font-bold">{u.calls}</div>
          <div className="text-xs">{u.failed_calls} failed</div></div>
        <div className="border border-slate-200 bg-slate-50 p-2"><div className="text-xs text-slate-500">Answered by fallback</div><div className="text-lg font-bold">{u.fallback_calls}</div></div>
        <div className="border border-slate-200 bg-slate-50 p-2"><div className="text-xs text-slate-500">Tokens in / out</div><div className="text-lg font-bold">{tokens(u.input_tokens)} / {tokens(u.output_tokens)}</div></div>
      </div>
      {u.budget_usd && <div className="h-2 bg-slate-100" aria-label={`${pct}% of the monthly budget used`}>
        <div className={`h-2 ${pct >= 100 ? 'bg-red-600' : pct >= 80 ? 'bg-amber-500' : 'bg-emerald-600'}`} style={{ width: `${Math.min(100, pct)}%` }} />
      </div>}
      <p className="text-xs text-slate-500">
        Learners can use Ask Fahim, Learn with Fahim and the paper solver {u.daily_limit ? `${u.daily_limit} times a day` : 'without a daily limit'}.
        {u.budget_usd ? ` Alerts are emailed at 50%, 80% and 100% of the budget${u.hard_stop ? '; at 100% these learner features pause until next month' : ''}.` : ' Set FAHIM_AI_MONTHLY_BUDGET_USD to get budget alerts.'}
      </p>
      {u.unpriced_calls > 0 && <p className="text-xs text-amber-800">
        {u.unpriced_calls} call{u.unpriced_calls === 1 ? ' has' : 's have'} no price, so the cost above is incomplete. Add the models' prices per million tokens in FAHIM_AI_PRICES.
      </p>}
      {u.by_feature.length > 0 ? <>
        <Table title="Feature" rows={u.by_feature} labels={FEATURES} />
        <Table title="Provider" rows={u.by_provider} labels={PROVIDERS} />
      </> : <p className="text-xs text-slate-500">No AI calls recorded this month yet.</p>}
    </>}
  </div>;
}
