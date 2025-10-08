import React from 'react';

export default function EvalSummary({ percent, verdict, advice }: { percent: number | null; verdict: string; advice: string }) {
    const color = percent === null ? 'text-foreground' : percent >= 80 ? 'text-green-600' : percent >= 60 ? 'text-yellow-600' : 'text-red-600';
    return (
        <div className="mt-4 p-4 bg-muted/50 rounded-md">
            <h4 className="text-md font-semibold">Summary: <span className={color}>{verdict}</span></h4>
            {percent !== null && <p className="text-2xl font-bold mt-2">{percent.toFixed(1)}% estimated quality</p>}
            <p className="text-sm mt-2 text-muted-foreground">{advice}</p>
        </div>
    );
}
