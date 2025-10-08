'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';
import {
    syncUserWithBackend,
    getUserDashboard,
    DashboardData,
    checkBackendHealth,
    getUserAnalyticsTrends,
    getUserPerformanceMetrics,
    getAnalyticsComparison,
    getAnalyticsBreakdown,
    invalidateUserCache
} from '@/lib/user-sync';

interface UserContextType {
    isBackendSynced: boolean;
    dashboardData: DashboardData | null;
    isLoading: boolean;
    error: string | null;
    isBackendHealthy: boolean;
    refreshDashboard: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
    const { user, isLoaded } = useUser();
    const [isBackendSynced, setIsBackendSynced] = useState(false);
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isBackendHealthy, setIsBackendHealthy] = useState(true);

    // Check backend health on mount
    useEffect(() => {
        checkBackendHealth().then(setIsBackendHealthy);
    }, []);

    // Sync user with backend when Clerk user is loaded
    useEffect(() => {
        if (isLoaded && user && !isBackendSynced && isBackendHealthy) {
            syncUser();
        }
    }, [isLoaded, user, isBackendSynced, isBackendHealthy]);

    const syncUser = async () => {
        if (!user) return;

        setIsLoading(true);
        setError(null);

        try {
            // Sync user with backend
            const syncResult = await syncUserWithBackend({
                clerk_user_id: user.id,
                email: user.emailAddresses[0]?.emailAddress || '',
                name: user.fullName || user.firstName || 'User',
            });

            if (syncResult) {
                setIsBackendSynced(true);
                console.log('✅ User synced with MongoDB:', syncResult.user.email);

                // Load dashboard data
                await loadDashboard();
            } else {
                setError('Failed to sync user with backend');
                console.error('❌ User sync failed');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
            setError(errorMessage);
            console.error('❌ User sync error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadDashboard = async () => {
        if (!user) return;

        try {
            const dashboard = await getUserDashboard(user.id);
            if (dashboard) {
                setDashboardData(dashboard);
                console.log('✅ Dashboard data loaded');
            }
        } catch (err) {
            console.error('Failed to load dashboard:', err);
        }
    };

    const refreshDashboard = async () => {
        if (!user) return;

        setIsLoading(true);
        await loadDashboard();
        setIsLoading(false);
    };

    const value: UserContextType = {
        isBackendSynced,
        dashboardData,
        isLoading,
        error,
        isBackendHealthy,
        refreshDashboard,
    };

    return (
        <UserContext.Provider value={value}>
            {children}
        </UserContext.Provider>
    );
}

export function useUserSync() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUserSync must be used within a UserProvider');
    }
    return context;
}