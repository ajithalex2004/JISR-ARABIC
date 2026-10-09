import React from 'react';
import { Smartphone, Monitor } from 'lucide-react';

interface MobileFrameSimulatorProps {
  children: React.ReactNode;
  enabled: boolean;
  onToggle: () => void;
}

export const MobileFrameSimulator: React.FC<MobileFrameSimulatorProps> = ({
  children,
  enabled,
  onToggle
}) => {
  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-slate-800 py-6 px-4 flex flex-col items-center justify-center">
      {/* Simulator Toolbar */}
      <div className="mb-4 bg-slate-900 border border-slate-700 px-4 py-2 flex items-center justify-between gap-4 text-xs text-white max-w-[420px] w-full">
        <div className="flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-emerald-400" />
          <span className="font-bold">Mobile Viewport (390 × 844)</span>
        </div>
        <button
          onClick={onToggle}
          className="px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 border border-slate-600 text-[11px] font-semibold flex items-center gap-1"
        >
          <Monitor className="w-3 h-3" />
          <span>Exit to Web</span>
        </button>
      </div>

      {/* Phone Frame */}
      <div className="w-full max-w-[410px] bg-slate-900 border-4 border-slate-950 shadow-2xl overflow-hidden flex flex-col h-[850px] relative">
        {/* Status Bar */}
        <div className="bg-slate-950 text-slate-300 text-[11px] px-5 py-1.5 flex justify-between items-center select-none font-mono">
          <span>9:41</span>
          <div className="flex items-center gap-1.5 text-[10px]">
            <span>5G</span>
            <span>100%</span>
          </div>
        </div>

        {/* Scaled App Window */}
        <div className="flex-1 overflow-y-auto bg-white">
          {children}
        </div>
      </div>
    </div>
  );
};
