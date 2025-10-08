import React from 'react';

interface TooltipProps {
    children: React.ReactNode;
    text: string;
}

export default function TooltipOld({ children, text }: TooltipProps) {
    return (
        <span className="relative inline-block" tabIndex={0} aria-label={text}>
            {children}
            <span className="absolute z-50 hidden group-hover:block group-focus:block w-64 p-2 bg-gray-800 text-white text-xs rounded-md shadow-lg" role="tooltip">
                {text}
            </span>
        </span>
    );
}
