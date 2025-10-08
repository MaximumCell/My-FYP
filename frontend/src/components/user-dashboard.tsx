'use client';

import { useState } from 'react';
import { useUserSync } from '@/components/providers/user-provider';
import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { EnhancedStatCard, ActivityFeed, QuickAction } from '@/components/enhanced-dashboard';
import { AdvancedAnalytics } from '@/components/advanced-analytics';
import {
    BarChart3,
    Clock,
    Database,
    RefreshCw,
    TrendingUp,
    Zap,
    Calendar,
    Rocket,
    TestTube,
    BrainCircuit,
    User,
    Star,
    Target
} from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

// Helper function to format training time
const formatTrainingTime = (seconds: number): string => {
    if (seconds === 0) return '0s';
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    if (seconds < 60) return `${seconds.toFixed(2)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
};

export function UserDashboard() {
    const { dashboardData, isLoading, refreshDashboard } = useUserSync();
    const { user: clerkUser } = useUser(); // Get Clerk user for profile image
    const [analyticsExpanded, setAnalyticsExpanded] = useState(false);

    if (isLoading) {
        return <DashboardSkeleton />;
    }

    if (!dashboardData) {
        return null;
    }

    const { user, quick_stats, usage_analytics, performance_overview } = dashboardData;

    // Transform recent activity for ActivityFeed component
    const recentActivities = [
        ...dashboardData.recent_activity.recent_models.map((model: any, index: number) => ({
            id: `model-${index}`,
            type: 'model' as const,
            title: model.name || `Model ${index + 1}`,
            timestamp: 'Recently',
            status: 'completed' as const
        })),
        ...dashboardData.recent_activity.recent_simulations.map((sim: any, index: number) => ({
            id: `sim-${index}`,
            type: 'simulation' as const,
            title: sim.name || `Simulation ${index + 1}`,
            timestamp: 'Recently',
            status: 'completed' as const
        }))
    ];

    return (
        <div className="w-full max-w-7xl mx-auto space-y-8">
            {/* Welcome Header with User Info */}
            <div className="relative">
                <Card className="bg-gradient-to-br from-primary/5 via-transparent to-accent/5 border-0 shadow-lg">
                    <CardContent className="p-8">
                        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                            <div className="flex items-center gap-6">
                                <div className="relative">
                                    <Avatar className="w-20 h-20 border-4 border-white/20 shadow-lg">
                                        <AvatarImage
                                            src={clerkUser?.imageUrl}
                                            alt={user.name}
                                            className="object-cover"
                                        />
                                        <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white text-2xl font-bold">
                                            {user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                                        </AvatarFallback>
                                    </Avatar>
                                    {/* Online status indicator */}
                                    <div className="absolute bottom-1 right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold mb-2">
                                        Welcome back, <span className="text-primary">{user.name}</span>!
                                    </h2>
                                    <div className="flex items-center gap-4 text-muted-foreground">
                                        <span className="flex items-center gap-1">
                                            <Calendar className="h-4 w-4" />
                                            Member since {new Date(user.member_since).toLocaleDateString()}
                                        </span>
                                        {usage_analytics.last_activity && (
                                            <span className="flex items-center gap-1">
                                                <Clock className="h-4 w-4" />
                                                Last active {new Date(usage_analytics.last_activity).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Badge variant="secondary" className="px-3 py-1">
                                    <Star className="h-3 w-3 mr-1" />
                                    Active User
                                </Badge>
                                <Button
                                    variant="outline"
                                    onClick={refreshDashboard}
                                    disabled={isLoading}
                                    className="hover:bg-primary hover:text-primary-foreground"
                                >
                                    <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                                    Refresh
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Enhanced Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                <EnhancedStatCard
                    title="ML Models Created"
                    value={quick_stats.models_count}
                    change={{
                        value: usage_analytics.models_this_week,
                        type: usage_analytics.models_this_week > 0 ? 'increase' : 'decrease',
                        period: 'this week'
                    }}
                    icon={<BarChart3 className="h-6 w-6" />}
                    color="primary"
                    progress={Math.min((quick_stats.models_count / 10) * 100, 100)}
                />
                <EnhancedStatCard
                    title="Simulations Run"
                    value={quick_stats.simulations_count}
                    change={{
                        value: usage_analytics.simulations_this_week,
                        type: usage_analytics.simulations_this_week > 0 ? 'increase' : 'decrease',
                        period: 'this week'
                    }}
                    icon={<Zap className="h-6 w-6" />}
                    color="accent"
                    progress={Math.min((quick_stats.simulations_count / 10) * 100, 100)}
                />
                <EnhancedStatCard
                    title="Training Time"
                    value={formatTrainingTime(usage_analytics.avg_training_time)}
                    change={{
                        value: Math.round((usage_analytics.avg_training_time / 60) * 100) / 100,
                        type: 'increase',
                        period: 'avg'
                    }}
                    icon={<Clock className="h-6 w-6" />}
                    color="green"
                />
                <EnhancedStatCard
                    title="Storage Used"
                    value={quick_stats.storage_used}
                    icon={<Database className="h-6 w-6" />}
                    color="blue"
                    progress={Math.min(45, 100)} // Could be calculated from actual storage limits
                />
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <QuickAction
                    title="Train New Model"
                    description="Upload data and start training"
                    icon={<Rocket className="h-8 w-8" />}
                    color="from-blue-500 to-blue-600"
                    onClick={() => window.location.href = '/ml'}
                />
                <QuickAction
                    title="Run Simulation"
                    description="Visualize physics equations"
                    icon={<TestTube className="h-8 w-8" />}
                    color="from-green-500 to-green-600"
                    onClick={() => window.location.href = '/simulation'}
                />
                <QuickAction
                    title="AI Tutor"
                    description="Get help with concepts"
                    icon={<BrainCircuit className="h-8 w-8" />}
                    color="from-purple-500 to-purple-600"
                    onClick={() => window.location.href = '/ai'}
                />
            </div>

            {/* Saved Items */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <QuickAction
                    title="Saved Models"
                    description={`View your ${quick_stats.models_count} saved ML models`}
                    icon={<BarChart3 className="h-8 w-8" />}
                    color="from-indigo-500 to-indigo-600"
                    onClick={() => window.location.href = '/ml/saved'}
                />
                <QuickAction
                    title="Saved Simulations"
                    description={`Manage your ${quick_stats.simulations_count} saved simulations`}
                    icon={<Zap className="h-8 w-8" />}
                    color="from-emerald-500 to-emerald-600"
                    onClick={() => window.location.href = '/simulation/saved'}
                />
            </div>

            {/* Analytics and Activity */}
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                {/* Performance Overview */}
                <Card className="xl:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5" />
                            Performance Overview
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-primary">{usage_analytics.models_this_month}</div>
                                <div className="text-sm text-muted-foreground">Models this month</div>
                                <div className="text-xs text-muted-foreground mt-1">
                                    {usage_analytics.models_this_week} this week
                                </div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-accent">{usage_analytics.simulations_this_month}</div>
                                <div className="text-sm text-muted-foreground">Simulations this month</div>
                                <div className="text-xs text-muted-foreground mt-1">
                                    {usage_analytics.simulations_this_week} this week
                                </div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-green-600">{formatTrainingTime(usage_analytics.avg_training_time)}</div>
                                <div className="text-sm text-muted-foreground">Avg training time</div>
                                <div className="text-xs text-muted-foreground mt-1">
                                    {performance_overview?.most_used_model_type || 'N/A'}
                                </div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-blue-600">{performance_overview?.success_rate || 98}%</div>
                                <div className="text-sm text-muted-foreground">Success rate</div>
                                <div className="text-xs text-muted-foreground mt-1">
                                    Score: {performance_overview?.productivity_score || 0}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Activity Feed */}
                <ActivityFeed activities={recentActivities} />

                {/* User Profile Summary */}
                <Card className="relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-accent/5 to-transparent" />
                    <CardContent className="p-6 relative">
                        <div className="text-center">
                            <Avatar className="w-16 h-16 mx-auto mb-4 border-4 border-white/20 shadow-lg">
                                <AvatarImage
                                    src={clerkUser?.imageUrl}
                                    alt={user.name}
                                    className="object-cover"
                                />
                                <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white text-xl font-bold">
                                    {user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                                </AvatarFallback>
                            </Avatar>

                            <h3 className="font-semibold text-lg mb-1">{user.name}</h3>
                            <p className="text-sm text-muted-foreground mb-4">{clerkUser?.emailAddresses[0]?.emailAddress}</p>

                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-muted-foreground">Status</span>
                                    <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1" />
                                        Active
                                    </Badge>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-muted-foreground">Plan</span>
                                    <Badge variant="outline">Free</Badge>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-muted-foreground">Projects</span>
                                    <span className="text-sm font-medium">{quick_stats.models_count + quick_stats.simulations_count}</span>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Advanced Analytics */}
            <AdvancedAnalytics
                clerkUserId={clerkUser?.id || ''}
                isExpanded={analyticsExpanded}
                onToggle={() => setAnalyticsExpanded(!analyticsExpanded)}
            />
        </div>
    );
}

function DashboardSkeleton() {
    return (
        <div className="w-full max-w-7xl mx-auto space-y-8">
            {/* Welcome Header Skeleton */}
            <Card>
                <CardContent className="p-8">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                        <div className="flex items-center gap-6">
                            <div className="relative">
                                <Skeleton className="w-20 h-20 rounded-full" />
                                <div className="absolute bottom-1 right-1 w-4 h-4 bg-gray-300 rounded-full" />
                            </div>
                            <div className="space-y-3">
                                <Skeleton className="h-8 w-64" />
                                <Skeleton className="h-4 w-48" />
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Skeleton className="h-6 w-20 rounded-full" />
                            <Skeleton className="h-10 w-24" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Stats Grid Skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {[...Array(4)].map((_, i) => (
                    <Card key={i}>
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="space-y-2 flex-1">
                                    <Skeleton className="h-4 w-24" />
                                    <Skeleton className="h-8 w-16" />
                                    <Skeleton className="h-3 w-20" />
                                </div>
                                <Skeleton className="h-12 w-12 rounded-xl" />
                            </div>
                            <Skeleton className="h-2 w-full rounded-full" />
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Quick Actions Skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[...Array(3)].map((_, i) => (
                    <Card key={i}>
                        <CardContent className="p-6">
                            <div className="space-y-4">
                                <Skeleton className="h-8 w-8" />
                                <div className="space-y-2">
                                    <Skeleton className="h-5 w-32" />
                                    <Skeleton className="h-4 w-40" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Analytics Section Skeleton */}
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                <Card className="xl:col-span-2">
                    <CardHeader>
                        <Skeleton className="h-6 w-40" />
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            {[...Array(4)].map((_, i) => (
                                <div key={i} className="text-center space-y-2">
                                    <Skeleton className="h-8 w-12 mx-auto" />
                                    <Skeleton className="h-3 w-20 mx-auto" />
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <Skeleton className="h-6 w-32 mb-4" />
                        <div className="space-y-4">
                            {[...Array(3)].map((_, i) => (
                                <div key={i} className="flex items-center gap-3 p-3 rounded-lg">
                                    <Skeleton className="h-4 w-4 rounded" />
                                    <div className="flex-1">
                                        <Skeleton className="h-4 w-32 mb-1" />
                                        <Skeleton className="h-3 w-20" />
                                    </div>
                                    <Skeleton className="h-5 w-16 rounded" />
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* User Profile Skeleton */}
                <Card>
                    <CardContent className="p-6">
                        <div className="text-center space-y-4">
                            <Skeleton className="w-16 h-16 rounded-full mx-auto" />
                            <div className="space-y-2">
                                <Skeleton className="h-5 w-32 mx-auto" />
                                <Skeleton className="h-4 w-40 mx-auto" />
                            </div>
                            <div className="space-y-3">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="flex justify-between items-center">
                                        <Skeleton className="h-4 w-16" />
                                        <Skeleton className="h-5 w-12" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}