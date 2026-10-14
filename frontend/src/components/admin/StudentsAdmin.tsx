import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

type Student = {
  id: string;
  name: string;
  default_grade: number | null;
  entitled_grades: number[];
  unlocked_terms: string[];
  school_name?: string | null;
  gender?: string | null;
  age?: number | null;
  has_pin?: boolean;
  parent_name?: string | null;
  parent_email?: string | null;
};

type FormState = {
  parent_email: string;
  name: string;
  grade: number;
  school_name: string;
  gender: string;
  age: string;
  access_pin: string;
};

const GRADES = Array.from({ length: 12 }, (_, i) => i + 1);
const EMPTY_FORM: FormState = { parent_email: '', name: '', grade: 1, school_name: '', gender: 'Boy', age: '', access_pin: '' };
const inputClass = 'block w-full border border-slate-400 p-2 mt-1';

function StudentForm({ editing, initial, busy, onCancel, onSubmit }: {
  editing: Student | null;
  initial: FormState;
  busy: boolean;
  onCancel: () => void;
  onSubmit: (form: FormState) => void;
}) {
  const [form, setForm] = useState<FormState>(initial);
  const set = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [field]: field === 'grade' ? Number(e.target.value) : e.target.value }));

  return <form
    className="border border-emerald-800 bg-emerald-50 p-4 space-y-3"
    onSubmit={e => { e.preventDefault(); onSubmit(form); }}
  >
    <h3 className="font-bold text-emerald-950">{editing ? `Edit ${editing.name}` : 'Add a new student'}</h3>
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {editing
        ? <div className="text-sm">Parent<div className="mt-1 p-2 text-slate-700 break-all">{editing.parent_name || '—'} · {editing.parent_email}</div></div>
        : <label className="text-sm">Parent email<input required type="email" value={form.parent_email} onChange={set('parent_email')} placeholder="parent@email.com" className={inputClass} /></label>}
      <label className="text-sm">Student name<input required value={form.name} onChange={set('name')} className={inputClass} /></label>
      <label className="text-sm">Grade<select value={form.grade} onChange={set('grade')} className={inputClass}>
        {GRADES.map(g => <option key={g} value={g}>Grade {g}</option>)}
      </select></label>
      <label className="text-sm">School<input value={form.school_name} onChange={set('school_name')} className={inputClass} /></label>
      <label className="text-sm">Gender<select value={form.gender} onChange={set('gender')} className={inputClass}>
        <option value="Boy">Boy</option><option value="Girl">Girl</option>
      </select></label>
      <label className="text-sm">Age<input type="number" min={3} max={20} value={form.age} onChange={set('age')} className={inputClass} /></label>
      <label className="text-sm">{editing ? 'New 4-digit PIN (leave blank to keep)' : 'Student login PIN (4 digits)'}
        <input inputMode="numeric" pattern="\d{4}" maxLength={4} value={form.access_pin} onChange={set('access_pin')} className={inputClass} />
      </label>
    </div>
    {!editing && <p className="text-xs text-slate-600">The parent must already have a JISR account. The student logs in with the parent's email and this PIN.</p>}
    <div className="flex gap-2">
      <button disabled={busy} className="bg-emerald-900 text-white px-4 py-2 disabled:opacity-50">{busy ? 'Saving…' : editing ? 'Save changes' : 'Add student'}</button>
      <button type="button" onClick={onCancel} className="border border-slate-400 px-4 py-2">Cancel</button>
    </div>
  </form>;
}

export function StudentsAdmin({ onOpenParent }: { onOpenParent?: (email: string) => void } = {}) {
  const [query, setQuery] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [pending, setPending] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  // null: form closed; 'new': adding; otherwise the student being edited.
  const [formFor, setFormFor] = useState<Student | 'new' | null>(null);

  const search = async (q: string) => {
    setError('');
    try { setStudents(await api.adminSearchStudents(q)); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { search(''); }, []);

  const run = async (key: string, action: () => Promise<string>) => {
    setBusy(key);
    setError('');
    setNotice('');
    try { setNotice(await action()); }
    catch (e: any) { setError(e.message); }
    finally { setBusy(''); }
  };

  const replace = (updated: Student) => setStudents(list => list.map(s => (s.id === updated.id ? updated : s)));

  const saveGrade = (student: Student) => run(student.id, async () => {
    const updated: Student = await api.adminSetStudentGrade(student.id, pending[student.id]);
    replace(updated);
    setPending(p => { const { [student.id]: _, ...rest } = p; return rest; });
    return `${updated.name} is now in Grade ${updated.default_grade}.`;
  });

  const submitForm = (form: FormState) => run('form', async () => {
    const details = {
      name: form.name.trim(),
      grade: form.grade,
      school_name: form.school_name.trim() || undefined,
      gender: form.gender,
      age: form.age ? Number(form.age) : undefined,
      access_pin: form.access_pin.trim() || undefined,
    };
    if (formFor && formFor !== 'new') {
      const updated: Student = await api.adminUpdateStudent(formFor.id, details);
      replace(updated);
      setFormFor(null);
      return `${updated.name} was updated.`;
    }
    const created: Student = await api.adminCreateStudent({ ...details, parent_email: form.parent_email.trim() });
    setStudents(list => [created, ...list]);
    setFormFor(null);
    return `${created.name} was added in Grade ${created.default_grade}.`;
  });

  const remove = (student: Student) => {
    if (!window.confirm(`Delete ${student.name}? This permanently removes the student and all their progress. Payment records are kept for tax purposes. This cannot be undone.`)) return;
    run(student.id, async () => {
      await api.adminDeleteStudent(student.id);
      setStudents(list => list.filter(s => s.id !== student.id));
      return `${student.name} was deleted.`;
    });
  };

  const formInitial = (s: Student | 'new'): FormState => s === 'new' ? EMPTY_FORM : {
    parent_email: s.parent_email || '',
    name: s.name,
    grade: s.default_grade || 1,
    school_name: s.school_name || '',
    gender: s.gender || 'Boy',
    age: s.age ? String(s.age) : '',
    access_pin: '',
  };

  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Students</h2>
      <button type="button" onClick={() => setFormFor('new')} className="bg-emerald-900 text-white px-4 py-2">+ Add student</button>
    </div>
    <p className="text-sm text-slate-600">Search by student or parent name or email. Changing a grade here does not need payment; the student sees the new grade the next time they open the app.</p>
    {formFor && <StudentForm
      key={formFor === 'new' ? 'new' : formFor.id}
      editing={formFor === 'new' ? null : formFor}
      initial={formInitial(formFor)}
      busy={busy === 'form'}
      onCancel={() => setFormFor(null)}
      onSubmit={submitForm}
    />}
    <form className="flex flex-wrap gap-2" onSubmit={e => { e.preventDefault(); search(query); }}>
      <input
        type="search"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="e.g. Ann Maria or parent@email.com"
        aria-label="Search students"
        className="border border-slate-400 p-2 flex-1 min-w-[12rem]"
      />
      <button className="bg-emerald-900 text-white px-4 py-2">Search</button>
    </form>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {notice && <p role="status" className="text-emerald-800 text-sm font-semibold">{notice}</p>}
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b border-slate-200">
            <th className="py-2 pr-3">Student</th>
            <th className="py-2 pr-3">Parent</th>
            <th className="py-2 pr-3">Grade</th>
            <th className="py-2 pr-3">Paid / registered grades</th>
            <th className="py-2 pr-3">Change grade</th>
            <th className="py-2">Manage</th>
          </tr>
        </thead>
        <tbody>
          {students.map(s => {
            const selected = pending[s.id] ?? s.default_grade ?? '';
            const changed = pending[s.id] !== undefined && pending[s.id] !== s.default_grade;
            return <tr key={s.id} className="border-b border-slate-100 align-top">
              <td className="py-2 pr-3 font-semibold text-slate-900">{s.name}<div className="text-xs font-normal text-slate-500">{s.school_name}</div></td>
              <td className="py-2 pr-3">{s.parent_name || '—'}{s.parent_email && (onOpenParent
                ? <button type="button" onClick={() => onOpenParent(s.parent_email!)} className="block text-left text-xs text-emerald-900 underline break-all" title="Open this parent's profile">{s.parent_email}</button>
                : <div className="text-xs text-slate-500 break-all">{s.parent_email}</div>)}</td>
              <td className="py-2 pr-3 font-bold">{s.default_grade ? `Grade ${s.default_grade}` : '—'}</td>
              <td className="py-2 pr-3">
                {s.entitled_grades.length ? s.entitled_grades.map(g => `G${g}`).join(', ') : '—'}
                {s.unlocked_terms.length > 0 && <div className="text-xs text-slate-500">{s.unlocked_terms.length} paid term{s.unlocked_terms.length === 1 ? '' : 's'}</div>}
              </td>
              <td className="py-2 pr-3">
                <div className="flex gap-2">
                  <select
                    aria-label={`Grade for ${s.name}`}
                    value={selected}
                    onChange={e => setPending(p => ({ ...p, [s.id]: Number(e.target.value) }))}
                    className="border border-slate-400 p-1"
                  >
                    {GRADES.map(g => <option key={g} value={g}>Grade {g}</option>)}
                  </select>
                  <button
                    type="button"
                    disabled={busy === s.id || !changed}
                    title={changed ? undefined : 'Pick a different grade to change it'}
                    onClick={() => saveGrade(s)}
                    className="bg-emerald-900 text-white px-3 py-1 disabled:bg-slate-200 disabled:text-slate-500"
                  >
                    {busy === s.id ? 'Saving…' : changed ? 'Set grade' : 'Current'}
                  </button>
                </div>
              </td>
              <td className="py-2">
                <div className="flex gap-3">
                  <button type="button" onClick={() => setFormFor(s)} className="text-emerald-900 underline">Edit</button>
                  <button type="button" disabled={busy === s.id} onClick={() => remove(s)} className="text-red-700 underline disabled:opacity-50">Delete</button>
                </div>
              </td>
            </tr>;
          })}
          {!students.length && <tr><td colSpan={6} className="py-3 text-slate-500">No students found.</td></tr>}
        </tbody>
      </table>
    </div>
  </section>;
}
