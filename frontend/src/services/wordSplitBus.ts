/** Opens the word splitter window (mounted once in App) from any word pop-up in the app. */
const EVENT = 'jisr:split-word';

export function openWordSplit(word: string): void {
  window.dispatchEvent(new CustomEvent(EVENT, { detail: { word } }));
}

export function onWordSplit(handler: (word: string) => void): () => void {
  const listener = (e: Event) => {
    const word = (e as CustomEvent<{ word?: string }>).detail?.word;
    if (word) handler(word);
  };
  window.addEventListener(EVENT, listener);
  return () => window.removeEventListener(EVENT, listener);
}
