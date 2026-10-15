import React, { useEffect, useRef, useState } from 'react';
import { ExportButtons } from './ExportButtons';
import { api } from '../../services/api';
import { Payment, PaymentsTable, formatDate, usd } from './PaymentsAdmin';

type Student = { id: string; name: string; default_grade: number | null; entitled_grades: number[]; unlocked_terms: string[]; school_name?: string | null };

type Parent = {
  id: string;
  full_name?: string | null;
  email: string;
  phone_number?: string | null;
  role: string;
  is_verified: boolean;
  weekly_report_email: boolean;
  created_at?: string | null;
  students_count: number;
  students: Student[];
  payments_count: number;
  paid_count: number;
  total_paid_usd: number;
  voucher_redemptions: number;
  last_payment_at?: string | null;
  payments?: Payment[];
};

type FormState = { email: string; full_name: string; phone_number: string; password: string; weekly_report_email: boolean };

const inputClass = 'block w-full border border-slate-400 p-2 mt-1';

function ParentForm({ editing, busy, onCancel, onSubmit }: {
  editing: Parent | null;
  busy: boolean;
  onCancel: () => void;
  onSubmit: (form: FormState) => void;
}) {
  const [form, setForm] = useState<FormState>({
    email: editing?.email || '',
    full_name: editing?.full_name || '',
    phone_number: editing?.phone_number || '',
    password: '',
    weekly_report_email: editing?.weekly_report_email || false,
  });
  const set = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [field]: field === 'weekly_report_email' ? e.target.checked : e.target.value }));

  return <form className="border border-emerald-800 bg-emerald-50 p-4 space-y-3" onSubmit={e => { e.preventDefault(); onSubmit(form); }}>
    <h3 className="font-bold text-emerald-950">{editing ? `Edit ${editing.full_name || editing.email}` : 'Add a new parent'}</h3>
    <div className="grid gap-3 sm:grid-cols-2">
      <label className="text-sm">Email<input required type="email" value={form.email} onChange={set('email')} className={inputClass} /></label>
      <label className="text-sm">Full name<input value={form.full_name} onChange={set('full_name')} className={inputClass} /></label>
      <label className="text-sm">Phone<input value={form.phone_number} onChange={set('phone_number')} className={inputClass} /></label>
      <label className="text-sm">{editing ? 'New password (leave blank to keep)' : 'Password (at least 8 characters)'}
        <input type="password" required={!editing} minLength={8} value={form.password} onChange={set('password')} autoComplete="new-password" className={inputClass} />
      </label>
    </div>
    {editing && <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.weekly_report_email} onChange={set('weekly_report_email')} /> Email the weekly progress report to this parent</label>}
    {!editing && <p className="text-xs text-slate-600">Share the email and password with the parent; they can change the password with "Forgot password". Add their children from the Students tab.</p>}
    <div className="flex gap-2">
      <button disabled={busy} className="bg-emerald-900 text-white px-4 py-2 disabled:opacity-50">{busy ? 'Saving…' : editing ? 'Save changes' : 'Add parent'}</button>
      <button type="button" onClick={onCancel} className="border border-slate-400 px-4 py-2">Cancel</button>
    </div>
  </form>;
}

function ParentDetails({ parentId }: { parentId: string }) {
  const [detail, setDetail] = useState<Parent | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { api.adminGetParent(parentId).then(setDetail).catch(e => setError(e.message)); }, [parentId]);
  if (error) return <p role="alert" className="text-red-700 text-sm">{error}</p>;
  if (!detail) return <p className="text-sm text-slate-500">Loading…</p>;
  return <div className="space-y-3 bg-slate-50 border border-slate-200 p-3">
    <div className="grid gap-2 sm:grid-cols-4 text-sm">
      <div><span className="text-slate-500">Phone</span><div>{detail.phone_number || '—'}</div></div>
      <div><span className="text-slate-500">Registered</span><div>{formatDate(detail.created_at)}</div></div>
      <div><span className="text-slate-500">Weekly report email</span><div>{detail.weekly_report_email ? 'On' : 'Off'}</div></div>
      <div><span className="text-slate-500">Verified</span><div>{detail.is_verified ? 'Yes' : 'No'}</div></div>
    </div>
    <div>
      <h4 className="font-bold text-sm text-slate-800">Students</h4>
      {detail.students.length ? <ul className="text-sm list-disc list-inside">
        {detail.students.map(s => <li key={s.id}>{s.name}: Grade {s.default_grade ?? '—'}
          {' · '}open grades {s.entitled_grades.map(g => `G${g}`).join(', ') || '—'}
          {s.unlocked_terms.length > 0 && ` · paid terms: ${s.unlocked_terms.map(t => t.replace('grade_', 'G').replace('_term_', ' T')).join(', ')}`}
        </li>)}
      </ul> : <p className="text-sm text-slate-500">No students yet.</p>}
    </div>
    <div>
      <h4 className="font-bold text-sm text-slate-800">Payments</h4>
      <PaymentsTable payments={detail.payments || []} showFamily={false} />
    </div>
  </div>;
}

export function ParentsAdmin({ initialQuery = '' }: { initialQuery?: string }) {
  const [query, setQuery] = useState(initialQuery);
  const [students, setStudents] = useState('');
  const [parents, setParents] = useState<Parent[]>([]);
  const [total, setTotal] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [formFor, setFormFor] = useState<Parent | 'new' | null>(null);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  // Only the latest search may update the list (an earlier, slower one must not overwrite it).
  const latest = useRef(0);
  const search = async (q: string, more = false) => {
    setError('');
    const seq = ++latest.current;
    try {
      const res = await api.adminListParents({ q, students, offset: more ? parents.length : 0 });
      if (seq !== latest.current) return;
      setParents(list => (more ? [...list, ...res.parents] : res.parents));
      setTotal(res.total);
    } catch (e: any) { setError(e.message); }
  };
  useEffect(() => { setQuery(initialQuery); }, [initialQuery]);
  useEffect(() => { search(initialQuery || query); }, [students, initialQuery]);

  const run = async (key: string, action: () => Promise<string>) => {
    setBusy(key);
    setError('');
    setNotice('');
    try { setNotice(await action()); }
    catch (e: any) { setError(e.message); }
    finally { setBusy(''); }
  };

  const submitForm = (form: FormState) => run('form', async () => {
    if (formFor && formFor !== 'new') {
      await api.adminUpdateParent(formFor.id, {
        email: form.email.trim(),
        full_name: form.full_name.trim(),
        phone_number: form.phone_number.trim(),
        password: form.password || undefined,
        weekly_report_email: form.weekly_report_email,
      });
      setFormFor(null);
      await search(query);
      return `${form.full_name || form.email} was updated.`;
    }
    await api.adminCreateParent({ email: form.email.trim(), password: form.password, full_name: form.full_name.trim() || undefined, phone_number: form.phone_number.trim() || undefined });
    setFormFor(null);
    await search(query);
    return `${form.full_name || form.email} was added.`;
  });

  const remove = (p: Parent) => {
    const label = p.full_name || p.email;
    if (!window.confirm(`Delete ${label}'s account and their ${p.students_count} student(s)? All progress is removed permanently. Payment records are kept for tax purposes. This cannot be undone.`)) return;
    run(p.id, async () => {
      const res = await api.adminDeleteParent(p.id);
      setParents(list => list.filter(x => x.id !== p.id));
      setTotal(t => t - 1);
      return res.message;
    });
  };

  const totals = parents.reduce((t, p) => ({ students: t.students + p.students_count, paid: t.paid + p.total_paid_usd }), { students: 0, paid: 0 });

  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Parents</h2>
      <span className="flex flex-wrap items-center gap-3">
        <ExportButtons kind="parents" filters={{ q: query.trim(), students }} subtitle={[query.trim() && `Search: ${query.trim()}`, students === 'with' ? 'With students' : students === 'without' ? 'Without students' : ''].filter(Boolean).join(' · ') || 'All parents'} />
        <button type="button" onClick={() => setFormFor('new')} className="bg-emerald-900 text-white px-4 py-2">+ Add parent</button>
      </span>
    </div>
    <p className="text-sm text-slate-600">Registered families with their students, grades and payments. Search by parent name, email, phone or a child's name. Click a row's "Details" for the full payment history.</p>
    {formFor && <ParentForm key={formFor === 'new' ? 'new' : formFor.id} editing={formFor === 'new' ? null : formFor} busy={busy === 'form'} onCancel={() => setFormFor(null)} onSubmit={submitForm} />}
    <form className="flex flex-wrap gap-2" onSubmit={e => { e.preventDefault(); search(query); }}>
      <input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="e.g. Alex or parent@email.com" aria-label="Search parents" className="border border-slate-400 p-2 flex-1 min-w-[12rem]" />
      <select aria-label="Show" value={students} onChange={e => setStudents(e.target.value)} className="border border-slate-400 p-2">
        <option value="">All parents</option><option value="with">With students</option><option value="without">Without students</option>
      </select>
      <button className="bg-emerald-900 text-white px-4 py-2">Search</button>
    </form>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {notice && <p role="status" className="text-emerald-800 text-sm font-semibold">{notice}</p>}
    <p className="text-xs text-slate-500">Showing {parents.length} of {total} parent{total === 1 ? '' : 's'} (families with students first) · {totals.students} student{totals.students === 1 ? '' : 's'} · {usd(totals.paid)} paid</p>
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b border-slate-200">
            <th className="py-2 pr-3">Parent</th>
            <th className="py-2 pr-3">Students & grades</th>
            <th className="py-2 pr-3">Payments</th>
            <th className="py-2 pr-3">Registered</th>
            <th className="py-2">Manage</th>
          </tr>
        </thead>
        <tbody>
          {parents.map(p => <React.Fragment key={p.id}>
            <tr className="border-b border-slate-100 align-top">
              <td className="py-2 pr-3 font-semibold text-slate-900">{p.full_name || '—'}{p.role !== 'parent' && <span className="ml-1 text-xs font-normal text-slate-500">({p.role})</span>}
                <div className="text-xs font-normal text-slate-500 break-all">{p.email}</div>
                {p.phone_number && <div className="text-xs font-normal text-slate-500">{p.phone_number}</div>}
              </td>
              <td className="py-2 pr-3">
                <div className="font-semibold">{p.students_count} student{p.students_count === 1 ? '' : 's'}</div>
                {p.students.map(s => <div key={s.id} className="text-xs text-slate-600">{s.name}: Grade {s.default_grade ?? '—'}{s.entitled_grades.length > 1 && ` (also ${s.entitled_grades.filter(g => g !== s.default_grade).map(g => `G${g}`).join(', ')})`}</div>)}
              </td>
              <td className="py-2 pr-3">
                <div className="font-mono">{usd(p.total_paid_usd)}</div>
                <div className="text-xs text-slate-500">{p.paid_count} paid{p.voucher_redemptions ? ` · ${p.voucher_redemptions} voucher${p.voucher_redemptions === 1 ? '' : 's'}` : ''}</div>
                {p.last_payment_at && <div className="text-xs text-slate-500">Last: {formatDate(p.last_payment_at)}</div>}
              </td>
              <td className="py-2 pr-3 whitespace-nowrap">{formatDate(p.created_at)}</td>
              <td className="py-2">
                <div className="flex flex-wrap gap-3">
                  <button type="button" onClick={() => setExpanded(expanded === p.id ? null : p.id)} className="text-emerald-900 underline">{expanded === p.id ? 'Hide' : 'Details'}</button>
                  <button type="button" onClick={() => setFormFor(p)} className="text-emerald-900 underline">Edit</button>
                  {p.role === 'parent' && <button type="button" disabled={busy === p.id} onClick={() => remove(p)} className="text-red-700 underline disabled:opacity-50">Delete</button>}
                </div>
              </td>
            </tr>
            {expanded === p.id && <tr><td colSpan={5} className="pb-3"><ParentDetails parentId={p.id} /></td></tr>}
          </React.Fragment>)}
          {!parents.length && <tr><td colSpan={5} className="py-3 text-slate-500">No parents found.</td></tr>}
        </tbody>
      </table>
    </div>
    {parents.length < total && <button type="button" onClick={() => search(query, true)} className="border border-slate-400 px-4 py-2 text-sm">Load more ({total - parents.length} more)</button>}
  </section>;
}
