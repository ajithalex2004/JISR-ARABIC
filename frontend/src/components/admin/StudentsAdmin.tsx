import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

type Student = {
  id: string;
  name: string;
  default_grade: number | null;
  entitled_grades: number[];
  unlocked_terms: string[];
  school_name?: string | null;
  parent_name?: string | null;
  parent_email?: string | null;
};

const GRADES = Array.from({ length: 12 }, (_, i) => i + 1);

export function StudentsAdmin() {
  const [query, setQuery] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [pending, setPending] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const search = async (q: string) => {
    setError('');
    try { setStudents(await api.adminSearchStudents(q)); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { search(''); }, []);

  const saveGrade = async (student: Student) => {
    const grade = pending[student.id];
    if (!grade || grade === student.default_grade) return;
    setBusy(student.id);
    setError('');
    setNotice('');
    try {
      const updated: Student = await api.adminSetStudentGrade(student.id, grade);
      setStudents(list => list.map(s => (s.id === updated.id ? updated : s)));
      setPending(p => { const { [student.id]: _, ...rest } = p; return rest; });
      setNotice(`${updated.name} is now in Grade ${updated.default_grade}.`);
    } catch (e: any) { setError(e.message); }
    finally { setBusy(''); }
  };

  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <h2 className="font-bold text-emerald-950">Students</h2>
    <p className="text-sm text-slate-600">Search by student or parent name or email. Changing a grade here does not need payment; the student sees the new grade the next time they open the app.</p>
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
            <th className="py-2">Change grade</th>
          </tr>
        </thead>
        <tbody>
          {students.map(s => {
            const selected = pending[s.id] ?? s.default_grade ?? '';
            return <tr key={s.id} className="border-b border-slate-100 align-top">
              <td className="py-2 pr-3 font-semibold text-slate-900">{s.name}<div className="text-xs font-normal text-slate-500">{s.school_name}</div></td>
              <td className="py-2 pr-3">{s.parent_name || '—'}<div className="text-xs text-slate-500 break-all">{s.parent_email}</div></td>
              <td className="py-2 pr-3 font-bold">{s.default_grade ? `Grade ${s.default_grade}` : '—'}</td>
              <td className="py-2 pr-3">
                {s.entitled_grades.length ? s.entitled_grades.map(g => `G${g}`).join(', ') : '—'}
                {s.unlocked_terms.length > 0 && <div className="text-xs text-slate-500">{s.unlocked_terms.length} paid term{s.unlocked_terms.length === 1 ? '' : 's'}</div>}
              </td>
              <td className="py-2">
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
                    disabled={busy === s.id || !pending[s.id] || pending[s.id] === s.default_grade}
                    onClick={() => saveGrade(s)}
                    className="bg-emerald-900 text-white px-3 py-1 disabled:opacity-40"
                  >
                    {busy === s.id ? 'Saving…' : 'Set grade'}
                  </button>
                </div>
              </td>
            </tr>;
          })}
          {!students.length && <tr><td colSpan={5} className="py-3 text-slate-500">No students found.</td></tr>}
        </tbody>
      </table>
    </div>
  </section>;
}
