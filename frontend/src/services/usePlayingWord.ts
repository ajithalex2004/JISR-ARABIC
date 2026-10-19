import { useEffect, useState } from 'react';
import { audioManager } from './audio';
import { localWordIndex } from './playbackWords';

/** The index of the word of `text` being spoken right now, or -1. */
export function usePlayingWordIndex(text: string): number {
  const [index, setIndex] = useState(-1);
  useEffect(
    () =>
      audioManager.subscribe((state) => {
        setIndex(state.isPlaying ? localWordIndex(state.text, state.activeWordIndex, text) : -1);
      }),
    [text]
  );
  return index;
}
