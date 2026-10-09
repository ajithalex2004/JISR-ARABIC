import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

type Assignment = { tutor_id: string; child_id: string };
type Person = { id: string; name: string; school_name?: string };

export function TutorAssignments() {
  const [options, setOptions] = useState<{ tutors: Person[]; learners: Person[] }>({ tutors: [], learners: [] });
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [tutor, setTutor] = useState('');
  const [child, setChild] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const refresh = async () => {
    const [people, grants] = await Promise.all([api.tutorAssignmentOptions(), api.tutorAssignments()]);
    setOptions(people);
    setAssignments(grants);
  };
  useEffect(() => { refresh().catch(e => setError(e.message)); }, []);
  const update = async (tutorId: string, childId: string, enabled: boolean) => {
    setBusy(true);
    setError('');
    try {
      await api.setTutorAssignment(tutorId, childId, enabled);
      await refresh();
    } catch (e: any) { setError(e.message); }
    finally { setBusy(false); }
  };
  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <h2 className="font-bold text-emerald-950">Tutor access assignments</h2>
    <p className="text-sm text-slate-600">Tutors can view and review only the learners assigned here. Removing an assignment revokes access immediately.</p>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    <form className="flex flex-wrap gap-3 items-end" onSubmit={e => { e.preventDefault(); update(tutor, child, true); }}>
      <label className="text-sm">Tutor<select required value={tutor} onChange={e => setTutor(e.target.value)} className="block border border-slate-400 p-2 max-w-full">
        <option value="">Select tutor</option>{options.tutors.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select></label>
      <label className="text-sm">Learner<select required value={child} onChange={e => setChild(e.target.value)} className="block border border-slate-400 p-2 max-w-full">
        <option value="">Select learner</option>{options.learners.map(p => <option key={p.id} value={p.id}>{p.name} · {p.school_name}</option>)}
      </select></label>
      <button disabled={busy || !tutor || !child} className="bg-emerald-900 text-white px-4 py-2 disabled:opacity-50">Assign tutor</button>
    </form>
    <ul className="space-y-2" aria-live="polite">
      {assignments.map(a => <li key={`${a.tutor_id}/${a.child_id}`} className="flex flex-wrap justify-between gap-2 border-t border-slate-200 pt-2 text-sm">
        <span>{options.tutors.find(p => p.id === a.tutor_id)?.name || 'Tutor'} → {options.learners.find(p => p.id === a.child_id)?.name || 'Learner'}</span>
        <button disabled={busy} type="button" className="text-red-700 underline" onClick={() => update(a.tutor_id, a.child_id, false)}>Revoke access</button>
      </li>)}
      {!assignments.length && <li className="text-sm text-slate-500">No tutor assignments.</li>}
    </ul>
  </section>;
}
