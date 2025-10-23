import React from 'react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Authentication - PhysicsLab',
    description: 'Sign in or create an account on PhysicsLab',
};

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {children}
        </div>
    );
}
