import React, { useState } from 'react';
import { StudentsAdmin } from './StudentsAdmin';
import { ParentsAdmin } from './ParentsAdmin';
import { PaymentsAdmin } from './PaymentsAdmin';
import { PromoCodesAdmin, SubscriptionsAdmin } from './PromoCodesAdmin';
import { SystemHealth } from './SystemHealth';
import { ContentProgress } from './ContentProgress';
import { TutorAssignments } from './TutorAssignments';

type TabProps = { openParent: (email: string) => void; parentQuery: string };

const TABS = [
  { key: 'students', label: 'Students', render: ({ openParent }: TabProps) => <StudentsAdmin onOpenParent={openParent} /> },
  { key: 'parents', label: 'Parents', render: ({ parentQuery }: TabProps) => <ParentsAdmin initialQuery={parentQuery} /> },
  { key: 'payments', label: 'Payments', render: () => <PaymentsAdmin /> },
  { key: 'subscriptions', label: 'Subscriptions', render: () => <SubscriptionsAdmin /> },
  { key: 'promos', label: 'Promo codes', render: () => <PromoCodesAdmin /> },
  { key: 'content', label: 'Content', render: () => <ContentProgress /> },
  { key: 'health', label: 'System health', render: () => <SystemHealth /> },
  { key: 'tutors', label: 'Tutors', render: () => <TutorAssignments /> },
] as const;

type TabKey = typeof TABS[number]['key'];
const STORAGE_KEY = 'jisr.admin.tab';

function initialTab(): TabKey {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && TABS.some(t => t.key === saved)) return saved as TabKey;
  } catch {}
  return 'students';
}

export function AdminManagement() {
  const [tab, setTab] = useState<TabKey>(initialTab);
  const [parentQuery, setParentQuery] = useState('');
  const choose = (key: TabKey) => {
    if (key !== 'parents') setParentQuery('');
    setTab(key);
    try { localStorage.setItem(STORAGE_KEY, key); } catch {}
  };
  return <div className="space-y-3">
    <div role="tablist" aria-label="Admin management" className="flex flex-wrap gap-1 border-b-2 border-emerald-900">
      {TABS.map(t => <button
        key={t.key}
        role="tab"
        type="button"
        aria-selected={tab === t.key}
        onClick={() => choose(t.key)}
        className={`px-4 py-2 text-sm font-bold ${tab === t.key ? 'bg-emerald-900 text-white' : 'bg-white text-emerald-950 hover:bg-emerald-50 border border-b-0 border-slate-300'}`}
      >{t.label}</button>)}
    </div>
    {TABS.find(t => t.key === tab)!.render({ openParent: email => { setParentQuery(email); setTab('parents'); }, parentQuery })}
  </div>;
}
