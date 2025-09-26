'use client';

import { useUserSync } from '@/components/providers/user-provider';
import { useUser } from '@clerk/nextjs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle, Loader2, RefreshCw, Wifi, WifiOff } from 'lucide-react';

export function UserSyncStatus() {
    const { user, isLoaded } = useUser();
    const {
        isBackendSynced,
        isLoading,
        error,
        isBackendHealthy,
        refreshDashboard
    } = useUserSync();

    // Don't show anything if user is not loaded or not signed in
    if (!isLoaded || !user) {
        return null;
    }

    // Backend health check failed
    if (!isBackendHealthy) {
        return (
            <Alert variant="destructive" className="mb-4">
                <WifiOff className="h-4 w-4" />
                <AlertTitle>Backend Unavailable</AlertTitle>
                <AlertDescription>
                    Unable to connect to the backend service. Some features may not work properly.
                </AlertDescription>
            </Alert>
        );
    }

    // Loading state
    if (isLoading && !isBackendSynced) {
        return (
            <Alert className="mb-4">
                <Loader2 className="h-4 w-4 animate-spin" />
                <AlertTitle>Syncing Account</AlertTitle>
                <AlertDescription>
                    Setting up your account data...
                </AlertDescription>
            </Alert>
        );
    }

    // Error state
    if (error && !isBackendSynced) {
        return (
            <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Sync Failed</AlertTitle>
                <AlertDescription className="flex items-center justify-between">
                    <span>Failed to sync your account: {error}</span>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={refreshDashboard}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <Loader2 className="h-3 w-3 animate-spin mr-1" />
                        ) : (
                            <RefreshCw className="h-3 w-3 mr-1" />
                        )}
                        Retry
                    </Button>
                </AlertDescription>
            </Alert>
        );
    }

    // Success state - don't show notification for successful sync
    if (isBackendSynced && !error) {
        return null;
    }

    return null;
}

// Debug component for development (disabled for cleaner UX)
export function UserSyncDebug() {
    // Debug component is now disabled for cleaner user experience
    return null;
}