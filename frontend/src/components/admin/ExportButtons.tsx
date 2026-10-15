import React, { useState } from 'react';
import { api } from '../../services/api';
import { downloadXlsx, printPdf } from '../../services/exportTable';

type Kind = 'students' | 'parents' | 'payments';

// "Excel" and "PDF" buttons that export every row matching the current search and filters.
export function ExportButtons({ kind, filters, subtitle }: { kind: Kind; filters: Record<string, string | number | undefined>; subtitle?: string }) {
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');

  const run = async (format: 'xlsx' | 'pdf') => {
    setBusy(format);
    setError('');
    try {
      const table = await api.adminExport(kind, filters);
      if (!table.rows.length) { setError('Nothing to export for this search.'); return; }
      if (format === 'xlsx') downloadXlsx(table); else printPdf(table, subtitle);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy('');
    }
  };

  return <span className="inline-flex flex-wrap items-center gap-2">
    <span className="text-xs text-slate-500">Export:</span>
    <button type="button" disabled={!!busy} onClick={() => run('xlsx')} className="border border-emerald-700 text-emerald-900 px-3 py-1.5 text-sm disabled:opacity-50" title="Download every matching row as an Excel file">
      {busy === 'xlsx' ? 'Preparing…' : 'Excel'}
    </button>
    <button type="button" disabled={!!busy} onClick={() => run('pdf')} className="border border-emerald-700 text-emerald-900 px-3 py-1.5 text-sm disabled:opacity-50" title="Open a print view: choose “Save as PDF”">
      {busy === 'pdf' ? 'Preparing…' : 'PDF'}
    </button>
    {error && <span role="alert" className="text-red-700 text-xs">{error}</span>}
  </span>;
}
