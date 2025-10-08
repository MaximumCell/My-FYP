"use client";
import React from 'react';
import { MATH_TOKENS, MathToken } from '@/lib/mathTokens';
import { Button } from '@/components/ui/button';

type Props = {
    onInsert: (snippet: string) => void;
    compact?: boolean;
};

export default function MathTokenPicker({ onInsert, compact = false }: Props) {
    return (
        <div className={`flex flex-wrap gap-2`}>
            {MATH_TOKENS.map((t: MathToken) => (
                <Button key={t.key} variant="outline" size={compact ? 'sm' : 'sm'} onClick={() => onInsert(t.snippet)} title={t.description}>
                    {t.label}
                </Button>
            ))}
        </div>
    );
}
