// Export a table (columns + rows) as an Excel .xlsx file or a printable PDF, in the browser.
// No library: the .xlsx is a small uncompressed zip of SpreadsheetML parts, and the PDF uses the
// browser's own print-to-PDF, so Arabic names keep their proper shaping in both.

export type Cell = string | number | null | undefined;
export type Table = { title: string; columns: string[]; rows: Cell[][] };

const enc = new TextEncoder();

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(data: Uint8Array): number {
  let crc = 0xffffffff;
  for (let i = 0; i < data.length; i++) crc = CRC_TABLE[(crc ^ data[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

// A zip archive with the files stored (not compressed): enough for Excel to open.
function zip(files: { name: string; data: Uint8Array }[]): Uint8Array {
  const parts: Uint8Array[] = [];
  const central: Uint8Array[] = [];
  let offset = 0;
  for (const file of files) {
    const name = enc.encode(file.name);
    const crc = crc32(file.data);
    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0, 0x04034b50, true);
    local.setUint16(4, 20, true);
    local.setUint16(6, 0x0800, true); // UTF-8 names
    local.setUint32(14, crc, true);
    local.setUint32(18, file.data.length, true);
    local.setUint32(22, file.data.length, true);
    local.setUint16(26, name.length, true);
    parts.push(new Uint8Array(local.buffer), name, file.data);

    const entry = new DataView(new ArrayBuffer(46));
    entry.setUint32(0, 0x02014b50, true);
    entry.setUint16(4, 20, true);
    entry.setUint16(6, 20, true);
    entry.setUint16(8, 0x0800, true);
    entry.setUint32(16, crc, true);
    entry.setUint32(20, file.data.length, true);
    entry.setUint32(24, file.data.length, true);
    entry.setUint16(28, name.length, true);
    entry.setUint32(42, offset, true);
    central.push(new Uint8Array(entry.buffer), name);
    offset += 30 + name.length + file.data.length;
  }
  const centralSize = central.reduce((n, p) => n + p.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true);
  end.setUint16(8, files.length, true);
  end.setUint16(10, files.length, true);
  end.setUint32(12, centralSize, true);
  end.setUint32(16, offset, true);
  const all = [...parts, ...central, new Uint8Array(end.buffer)];
  const out = new Uint8Array(all.reduce((n, p) => n + p.length, 0));
  let at = 0;
  for (const p of all) { out.set(p, at); at += p.length; }
  return out;
}

const xml = (s: string) => s
  .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function columnName(index: number): string {
  let name = '';
  for (let n = index + 1; n > 0; n = Math.floor((n - 1) / 26)) name = String.fromCharCode(65 + ((n - 1) % 26)) + name;
  return name;
}

function cellXml(value: Cell, ref: string, style = 0): string {
  const s = style ? ` s="${style}"` : '';
  if (typeof value === 'number' && Number.isFinite(value)) return `<c r="${ref}"${s}><v>${value}</v></c>`;
  if (value === null || value === undefined || value === '') return `<c r="${ref}"${s}/>`;
  return `<c r="${ref}"${s} t="inlineStr"><is><t xml:space="preserve">${xml(String(value))}</t></is></c>`;
}

export function xlsxBytes(table: Table): Uint8Array {
  const { columns, rows } = table;
  const widths = columns.map((c, i) => Math.min(60, Math.max(c.length, ...rows.map(r => String(r[i] ?? '').length)) + 2));
  const last = `${columnName(columns.length - 1)}${rows.length + 1}`;
  const sheetRows = [
    `<row r="1">${columns.map((c, i) => cellXml(c, `${columnName(i)}1`, 1)).join('')}</row>`,
    ...rows.map((row, r) => `<row r="${r + 2}">${columns.map((_, i) => cellXml(row[i], `${columnName(i)}${r + 2}`)).join('')}</row>`),
  ].join('');
  const sheet = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${widths.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join('')}</cols><sheetData>${sheetRows}</sheetData><autoFilter ref="A1:${last}"/></worksheet>`;
  const sheetName = xml(table.title.slice(0, 31));
  const files: Record<string, string> = {
    '[Content_Types].xml': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>`,
    '_rels/.rels': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
    'xl/workbook.xml': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="${sheetName}" sheetId="1" r:id="rId1"/></sheets><definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">'${sheetName.replace(/'/g, "''")}'!$A$1:$${columnName(columns.length - 1)}$${rows.length + 1}</definedName></definedNames></workbook>`,
    'xl/_rels/workbook.xml.rels': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`,
    'xl/styles.xml': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF064E3B"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>`,
    'xl/worksheets/sheet1.xml': sheet,
  };
  return zip(Object.entries(files).map(([name, text]) => ({ name, data: enc.encode(text) })));
}

function save(bytes: BlobPart, type: string, filename: string) {
  const url = URL.createObjectURL(new Blob([bytes], { type }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function exportFileName(title: string, extension: string) {
  return `jisr-${title.toLowerCase().replace(/\s+/g, '-')}-${new Date().toISOString().slice(0, 10)}.${extension}`;
}

export function downloadXlsx(table: Table) {
  save(xlsxBytes(table) as BlobPart, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', exportFileName(table.title, 'xlsx'));
}

export function tableHtml(table: Table, subtitle = ''): string {
  const esc = (v: Cell) => xml(String(v ?? ''));
  return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(exportFileName(table.title, 'pdf').replace(/\.pdf$/, ''))}</title>
<style>
@page { size: A4 landscape; margin: 12mm; }
body { font-family: "Segoe UI", Tahoma, Arial, "Noto Naskh Arabic", sans-serif; color: #0f172a; margin: 0; }
h1 { font-size: 16px; margin: 0 0 2px; color: #064e3b; }
p { font-size: 10px; margin: 0 0 8px; color: #475569; }
table { border-collapse: collapse; width: 100%; font-size: 9px; }
th { background: #064e3b; color: #fff; text-align: start; padding: 4px; }
td { border-bottom: 1px solid #cbd5e1; padding: 3px 4px; vertical-align: top; unicode-bidi: plaintext; }
tr:nth-child(even) td { background: #f8fafc; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
</style></head><body>
<h1>JISR · ${esc(table.title)}</h1><p>${esc(subtitle)}${subtitle ? ' · ' : ''}${table.rows.length} rows · exported ${esc(new Date().toLocaleString())}</p>
<table><thead><tr>${table.columns.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead>
<tbody>${table.rows.map(r => `<tr>${table.columns.map((_, i) => `<td dir="auto">${esc(r[i])}</td>`).join('')}</tr>`).join('')}</tbody></table>
</body></html>`;
}

// Opens the browser's print dialog for the table; choose "Save as PDF" as the destination.
export function printPdf(table: Table, subtitle = '') {
  const frame = document.createElement('iframe');
  frame.setAttribute('aria-hidden', 'true');
  Object.assign(frame.style, { position: 'fixed', right: '0', bottom: '0', width: '0', height: '0', border: '0' });
  document.body.appendChild(frame);
  const doc = frame.contentWindow!.document;
  doc.open();
  doc.write(tableHtml(table, subtitle));
  doc.close();
  setTimeout(() => {
    frame.contentWindow!.focus();
    frame.contentWindow!.print();
    setTimeout(() => frame.remove(), 60_000);
  }, 300);
}
