import React from 'react';

export interface FahimRobotMascotProps {
  className?: string;
  size?: number;
}

export type FaheemRobotMascotProps = FahimRobotMascotProps;

export const FahimRobotMascot: React.FC<FahimRobotMascotProps> = ({
  className = '',
  size = 120,
}) => {
  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-md select-none"
      >
        <defs>
          <linearGradient id="helmetGrad" x1="100" y1="20" x2="100" y2="160" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="65%" stopColor="#F1F5F9" />
            <stop offset="100%" stopColor="#CBD5E1" />
          </linearGradient>

          <linearGradient id="faceOrangeGrad" x1="100" y1="50" x2="100" y2="140" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FF9E68" />
            <stop offset="40%" stopColor="#FF7336" />
            <stop offset="100%" stopColor="#E64A19" />
          </linearGradient>

          <linearGradient id="earGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FFA06B" />
            <stop offset="100%" stopColor="#D84315" />
          </linearGradient>

          <radialGradient id="eyeGrad" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#5D4037" />
            <stop offset="60%" stopColor="#3E2723" />
            <stop offset="100%" stopColor="#1A0C08" />
          </radialGradient>
        </defs>

        {/* Ears */}
        <path d="M36 78 C24 74, 18 85, 24 100 C28 108, 38 110, 42 104 Z" fill="url(#earGrad)" />
        <circle cx="32" cy="92" r="7" fill="#D84315" />
        <path d="M164 78 C176 74, 182 85, 176 100 C172 108, 162 110, 158 104 Z" fill="url(#earGrad)" />
        <circle cx="168" cy="92" r="7" fill="#D84315" />

        {/* Top Nubs */}
        <path d="M84 34 L88 20 Q90 18 93 21 L94 34 Z" fill="url(#earGrad)" />
        <path d="M116 34 L112 20 Q110 18 107 21 L106 34 Z" fill="url(#earGrad)" />

        {/* Helmet */}
        <rect x="32" y="30" width="136" height="118" rx="58" fill="url(#helmetGrad)" stroke="#E2E8F0" strokeWidth="2" />
        <ellipse cx="100" cy="44" rx="45" ry="9" fill="white" opacity="0.7" />

        {/* Face Screen */}
        <rect x="46" y="46" width="108" height="86" rx="43" fill="url(#faceOrangeGrad)" />
        <ellipse cx="100" cy="58" rx="35" ry="7" fill="white" opacity="0.25" />

        {/* Left Eye */}
        <g>
          <ellipse cx="78" cy="86" rx="17" ry="19" fill="url(#eyeGrad)" />
          <ellipse cx="82" cy="79" rx="6" ry="7" fill="white" />
          <circle cx="73" cy="94" r="3" fill="white" opacity="0.7" />
          <ellipse cx="78" cy="86" rx="15" ry="17" stroke="#FFB74D" strokeWidth="1.5" opacity="0.4" fill="none" />
        </g>

        {/* Right Eye */}
        <g>
          <ellipse cx="122" cy="86" rx="17" ry="19" fill="url(#eyeGrad)" />
          <ellipse cx="126" cy="79" rx="6" ry="7" fill="white" />
          <circle cx="117" cy="94" r="3" fill="white" opacity="0.7" />
          <ellipse cx="122" cy="86" rx="15" ry="17" stroke="#FFB74D" strokeWidth="1.5" opacity="0.4" fill="none" />
        </g>

        {/* Smile */}
        <path d="M92 108 Q100 116 108 108" stroke="#5D2E12" strokeWidth="3.5" strokeLinecap="round" fill="none" />

        {/* Cheeks */}
        <ellipse cx="59" cy="98" rx="6" ry="4" fill="#D84315" opacity="0.45" />
        <ellipse cx="141" cy="98" rx="6" ry="4" fill="#D84315" opacity="0.45" />

        {/* Collar */}
        <g>
          <path d="M65 142 C65 142, 75 168, 100 168 C125 168, 135 142, 135 142 Z" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="2" />
          <path d="M78 143 C84 153, 116 153, 122 143" stroke="#FF7043" strokeWidth="4" strokeLinecap="round" />
          <rect x="92" y="152" width="16" height="5" rx="2.5" fill="#475569" />
          <circle cx="84" cy="154.5" r="1.5" fill="#94A3B8" />
          <circle cx="116" cy="154.5" r="1.5" fill="#94A3B8" />
        </g>
      </svg>
    </div>
  );
};

export const FaheemRobotMascot = FahimRobotMascot;
