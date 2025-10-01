/**
 * User sync utilities for integrating Clerk with MongoDB backend
 */

const API_BASE_URL = process.env.NODE_ENV === 'production'
    ? process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-url.com'
    : 'http://localhost:5000';

export interface UserSyncData {
    clerk_user_id: string;
    email: string;
    name: string;
}

export interface UserSyncResponse {
    message: string;
    user: {
        id: string;
        clerk_user_id: string;
        email: string;
        name: string;
        created_at: string;
        updated_at: string;
        usage_analytics: {
            total_models_trained: number;
            total_simulations_run: number;
            total_training_time: number;
            last_activity: string | null;
        };
    };
}

export interface DashboardData {
    user: {
        name: string;
        email: string;
        member_since: string;
    };
    quick_stats: {
        models_count: number;
        simulations_count: number;
        total_training_time: string;
        storage_used: string;
    };
    recent_activity: {
        recent_models: Array<{
            id: string;
            name: string;
            type: string;
            created_at: string;
            performance?: any;
        }>;
        recent_simulations: Array<{
            id: string;
            name: string;
            type: string;
            created_at: string;
            execution_time?: number;
        }>;
    };
    usage_analytics: {
        models_this_month: number;
        simulations_this_month: number;
        models_this_week: number;
        simulations_this_week: number;
        avg_training_time: number;
        last_activity: string | null;
    };
    performance_overview: {
        total_projects: number;
        success_rate: number;
        most_used_model_type: string;
        productivity_score: number;
    };
}

/**
 * Sync user with MongoDB backend
 */
export async function syncUserWithBackend(userData: UserSyncData): Promise<UserSyncResponse | null> {
    try {
        console.log('Syncing user with backend:', userData.email);

        const response = await fetch(`${API_BASE_URL}/api/users/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result: UserSyncResponse = await response.json();
        console.log('User synced successfully:', result.user.email);
        return result;
    } catch (error) {
        console.error('Failed to sync user with backend:', error);
        return null;
    }
}

/**
 * Get user dashboard data
 */
export async function getUserDashboard(clerkUserId: string): Promise<DashboardData | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/dashboard?clerk_user_id=${clerkUserId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If JSON parsing fails, try to get text
                try {
                    const errorText = await response.text();
                    if (errorText) {
                        errorMessage = errorText;
                    }
                } catch (textError) {
                    // Keep default error message
                }
            }
            console.error('Dashboard API error:', errorMessage);
            throw new Error(errorMessage);
        }

        const result: DashboardData = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get dashboard data:', error);
        return null;
    }
}

/**
 * Get user analytics
 */
export async function getUserAnalytics(clerkUserId: string): Promise<any | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics?clerk_user_id=${clerkUserId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get analytics:', error);
        return null;
    }
}

/**
 * Update user analytics (internal use)
 */
export async function updateUserAnalytics(clerkUserId: string, analytics: Record<string, any>): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                clerk_user_id: clerkUserId,
                analytics,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return true;
    } catch (error) {
        console.error('Failed to update analytics:', error);
        return false;
    }
}

/**
 * Check backend health
 */
export async function checkBackendHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            timeout: 5000,
        } as RequestInit);

        return response.ok;
    } catch (error) {
        console.error('Backend health check failed:', error);
        return false;
    }
}

/**
 * Get user analytics trends
 */
export async function getUserAnalyticsTrends(clerkUserId: string, days: number = 30, granularity: string = 'daily'): Promise<any | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics/trends?clerk_user_id=${clerkUserId}&days=${days}&granularity=${granularity}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get analytics trends:', error);
        return null;
    }
}

/**
 * Get user performance metrics
 */
export async function getUserPerformanceMetrics(clerkUserId: string, period: string = 'month'): Promise<any | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics/performance?clerk_user_id=${clerkUserId}&period=${period}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get performance metrics:', error);
        return null;
    }
}

/**
 * Get analytics comparison
 */
export async function getAnalyticsComparison(clerkUserId: string, period: string = 'month', compareWith: string = 'previous'): Promise<any | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics/compare?clerk_user_id=${clerkUserId}&period=${period}&compare_with=${compareWith}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get analytics comparison:', error);
        return null;
    }
}

/**
 * Get analytics breakdown
 */
export async function getAnalyticsBreakdown(clerkUserId: string, type: string = 'model_types', period: string = 'month'): Promise<any | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/analytics/breakdown?clerk_user_id=${clerkUserId}&type=${type}&period=${period}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Failed to get analytics breakdown:', error);
        return null;
    }
}

/**
 * Invalidate user cache
 */
export async function invalidateUserCache(clerkUserId: string): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/cache/invalidate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ clerk_user_id: clerkUserId }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return true;
    } catch (error) {
        console.error('Failed to invalidate cache:', error);
        return false;
    }
}