import React, { useRef } from 'react';
import { STORY_LINES, STORY_STEPS } from './content';
import { useActiveStep } from './useReveal';

/** The product in three states: the printed page, the page with English under each line, practice. */
function StoryVisual({ step }: { step: number }) {
  return (
    <div className={`jl-page jl-page--s${step}`} aria-hidden="true">
      <div className="jl-page__bar"><span>Class 5 · Term 1 · Page 9</span><span lang="ar">الدَّرْسُ الأَوَّلُ</span></div>
      <ol className="jl-page__lines">
        {STORY_LINES.map((l, i) => (
          <li key={i} className={`jl-line${l.head ? ' jl-line--head' : ''}${l.example ? ' jl-line--ex' : ''}`} style={{ ['--i' as string]: i }}>
            <span className="jl-line__ar" lang="ar" dir="rtl">{l.ar}</span>
            <span className="jl-line__en">{l.en}</span>
          </li>
        ))}
      </ol>
      <div className="jl-page__practice">
        <div className="jl-quiz">
          <p className="jl-quiz__q"><span lang="ar">إِنْسَانٌ</span> means…</p>
          <div className="jl-quiz__opts"><span>Animal</span><span className="is-right">Human ✓</span><span>House</span></div>
        </div>
        <div className="jl-ring" style={{ ['--p' as string]: 0.82 }}><span>82%</span><small>mastered</small></div>
      </div>
    </div>
  );
}

export function ScrollStory() {
  const refs = useRef<(HTMLElement | null)[]>([]);
  const active = useActiveStep(refs, STORY_STEPS.length);
  return (
    <section id="how" className="jl-section jl-story" aria-labelledby="jl-story-title">
      <div className="jl-wrap">
        <header className="jl-head" data-reveal>
          <p className="jl-kicker">How it works</p>
          <h2 id="jl-story-title" className="jl-h2">From the page to <em>understanding</em>, in three steps.</h2>
        </header>
        <div className="jl-story__grid">
          <div className="jl-story__sticky"><StoryVisual step={active} /></div>
          <ol className="jl-story__steps">
            {STORY_STEPS.map((s, i) => (
              <li key={s.kicker} ref={(n) => { refs.current[i] = n; }} data-step={i} className={`jl-step${active === i ? ' is-active' : ''}`}>
                <p className="jl-step__kicker">{s.kicker}</p>
                <h3 className="jl-h3">{s.title}</h3>
                <p className="jl-step__body">{s.body}</p>
                <div className="jl-step__visual"><StoryVisual step={i} /></div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
