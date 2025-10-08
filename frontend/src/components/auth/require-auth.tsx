"use client";

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

export default function RequireAuth({ children }: { children: React.ReactNode }) {
    const { isSignedIn, isLoaded } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoaded) return;
        if (!isSignedIn) {
            // redirect to Clerk sign-in page; preserve return path
            router.push('/sign-in');
        }
    }, [isLoaded, isSignedIn, router]);

    if (!isLoaded || !isSignedIn) return null;

    return <>{children}</>;
}
