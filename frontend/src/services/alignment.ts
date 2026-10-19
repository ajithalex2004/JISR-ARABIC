/**
 * Arabic–English matching highlights: which words of a sentence match which words of its
 * translation, from POST /api/curriculum/alignments. Word indexes count whitespace-separated
 * words, the same way the server splits them.
 */
import { useEffect, useState } from 'react';
import { createApiUrl } from './api';

export interface AlignmentChunk {
  ar: number[];
  en: number[];
}

export type Alignment = AlignmentChunk[] | null;

const cache = new Map<string, Alignment>();
const keyOf = (ar: string, en: string) => `${ar.trim()}\u0000${en.trim()}`;

export function splitWords(text: string): string[] {
  return text.split(/\s+/).filter(Boolean);
}

export async function fetchAlignments(pairs: { ar: string; en: string }[]): Promise<Alignment[]> {
  const wanted = pairs.filter((p) => p.ar.trim() && p.en.trim() && !cache.has(keyOf(p.ar, p.en)));
  const unique = [...new Map(wanted.map((p) => [keyOf(p.ar, p.en), p])).values()].slice(0, 40);
  if (unique.length) {
    try {
      const res = await fetch(createApiUrl('/api/curriculum/alignments').toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pairs: unique }),
      });
      if (res.ok) {
        const data = await res.json();
        unique.forEach((p, i) => {
          const value = data?.alignments?.[i];
          // Only remember answers; a sentence without one may be aligned on a later visit.
          if (Array.isArray(value)) cache.set(keyOf(p.ar, p.en), value);
        });
      }
    } catch {
      // No highlighting is the fallback; the sentences still show normally.
    }
  }
  return pairs.map((p) => cache.get(keyOf(p.ar, p.en)) ?? null);
}

/** Alignments for the given pairs, in order; null entries until (or unless) one is available. */
export function useAlignments(pairs: { ar: string; en: string }[]): Alignment[] {
  const signature = pairs.map((p) => keyOf(p.ar, p.en)).join('\u0001');
  const [alignments, setAlignments] = useState<Alignment[]>(() => pairs.map((p) => cache.get(keyOf(p.ar, p.en)) ?? null));

  useEffect(() => {
    let cancelled = false;
    setAlignments(pairs.map((p) => cache.get(keyOf(p.ar, p.en)) ?? null));
    fetchAlignments(pairs).then((result) => {
      if (!cancelled) setAlignments(result);
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  return alignments;
}
