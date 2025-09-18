import React from 'react';

interface TooltipProps {
    children: React.ReactNode;
    text: string;
}

// Legacy simple tooltip kept for reference. Prefer using Radix tooltip (`tooltip.tsx`).
export default function TooltipLegacy({ children, text }: TooltipProps) {
    return (
        <span className="relative inline-block" tabIndex={0} aria-label={text}>
            {children}
            <span className="absolute z-50 hidden group-hover:block group-focus:block w-64 p-2 bg-gray-800 text-white text-xs rounded-md shadow-lg" role="tooltip">
                {text}
            </span>
        </span>
    );
}
