'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
    getUserAnalyticsTrends,
    getUserPerformanceMetrics,
    getAnalyticsComparison,
    getAnalyticsBreakdown
} from '@/lib/user-sync';
// Helper function to format training time
const formatTrainingTime = (seconds: number): string => {
    if (seconds === 0) return '0s';
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    if (seconds < 60) return `${seconds.toFixed(2)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
};

import {
    TrendingUp,
    TrendingDown,
    BarChart3,
    PieChart,
    Calendar,
    Zap,
    Target,
    Award,
    RefreshCw,
    ChevronDown,
    ChevronUp
} from 'lucide-react';

interface AdvancedAnalyticsProps {
    clerkUserId: string;
    isExpanded?: boolean;
    onToggle?: () => void;
}

export function AdvancedAnalytics({ clerkUserId, isExpanded = false, onToggle }: AdvancedAnalyticsProps) {
    const [trends, setTrends] = useState<any>(null);
    const [performance, setPerformance] = useState<any>(null);
    const [comparison, setComparison] = useState<any>(null);
    const [breakdown, setBreakdown] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [period, setPeriod] = useState('month');

    const loadAnalytics = async () => {
        if (!isExpanded || !clerkUserId) return;

        setLoading(true);
        try {
            const [trendsData, performanceData, comparisonData, breakdownData] = await Promise.all([
                getUserAnalyticsTrends(clerkUserId, 30, 'daily'),
                getUserPerformanceMetrics(clerkUserId, period),
                getAnalyticsComparison(clerkUserId, period),
                getAnalyticsBreakdown(clerkUserId, 'model_types', period)
            ]);

            setTrends(trendsData);
            setPerformance(performanceData);
            setComparison(comparisonData);
            setBreakdown(breakdownData);
        } catch (error) {
            console.error('Failed to load advanced analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAnalytics();
    }, [isExpanded, clerkUserId, period]);

    const handleRefresh = () => {
        loadAnalytics();
    };

    const getChangeIcon = (type: string) => {
        return type === 'increase' ?
            <TrendingUp className="h-3 w-3 text-green-500" /> :
            type === 'decrease' ?
                <TrendingDown className="h-3 w-3 text-red-500" /> :
                <Target className="h-3 w-3 text-gray-500" />;
    };

    if (!isExpanded) {
        return (
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onToggle}>
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <BarChart3 className="h-5 w-5 text-primary" />
                            <div>
                                <h3 className="font-semibold">Advanced Analytics</h3>
                                <p className="text-sm text-muted-foreground">View detailed trends and insights</p>
                            </div>
                        </div>
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        <CardTitle>Advanced Analytics</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                        <select
                            value={period}
                            onChange={(e) => setPeriod(e.target.value)}
                            className="text-sm border rounded px-2 py-1"
                        >
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                            <option value="quarter">This Quarter</option>
                        </select>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleRefresh}
                            disabled={loading}
                        >
                            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={onToggle}>
                            <ChevronUp className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-6">
                {loading ? (
                    <AnalyticsSkeleton />
                ) : (
                    <>
                        {/* Comparison Card */}
                        {comparison && (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Card>
                                    <CardContent className="p-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium">Models</p>
                                                <p className="text-2xl font-bold">{comparison.current_period.models_count}</p>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                {getChangeIcon(comparison.changes.models.type)}
                                                <span className="text-sm font-medium">
                                                    {comparison.changes.models.value}%
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            vs previous {period}
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardContent className="p-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium">Simulations</p>
                                                <p className="text-2xl font-bold">{comparison.current_period.simulations_count}</p>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                {getChangeIcon(comparison.changes.simulations.type)}
                                                <span className="text-sm font-medium">
                                                    {comparison.changes.simulations.value}%
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            vs previous {period}
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardContent className="p-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium">Total Projects</p>
                                                <p className="text-2xl font-bold">{comparison.current_period.total_projects}</p>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                {getChangeIcon(comparison.changes.total_projects.type)}
                                                <span className="text-sm font-medium">
                                                    {comparison.changes.total_projects.value}%
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            vs previous {period}
                                        </p>
                                    </CardContent>
                                </Card>
                            </div>
                        )}

                        {/* Performance Metrics */}
                        {performance && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg flex items-center gap-2">
                                        <Award className="h-5 w-5" />
                                        Performance Metrics
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="text-center">
                                            <div className="text-xl font-bold text-blue-600">
                                                {performance.models.avg_accuracy}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Avg Model Accuracy</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold text-green-600">
                                                {formatTrainingTime(performance.models.avg_training_time)}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Avg Training Time</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold text-purple-600">
                                                {formatTrainingTime(performance.simulations.avg_execution_time)}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Avg Execution Time</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold text-orange-600">
                                                {performance.productivity.projects_per_day}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Projects per Day</div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Breakdown */}
                        {breakdown && breakdown.breakdown && breakdown.breakdown.length > 0 && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg flex items-center gap-2">
                                        <PieChart className="h-5 w-5" />
                                        Model Types Breakdown
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        {breakdown.breakdown.map((item: any, index: number) => (
                                            <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                                                <div className="flex items-center gap-3">
                                                    <Badge variant="secondary">{item.category}</Badge>
                                                    <span className="font-medium">{item.count} models</span>
                                                </div>
                                                <div className="text-right">
                                                    <div className="font-bold">{item.percentage}%</div>
                                                    {item.avg_accuracy && (
                                                        <div className="text-xs text-muted-foreground">
                                                            Avg: {item.avg_accuracy}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Trends Chart Placeholder */}
                        {trends && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg flex items-center gap-2">
                                        <Calendar className="h-5 w-5" />
                                        Activity Trends
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-center p-8 text-muted-foreground">
                                        <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                        <p className="text-sm">Chart visualization coming soon</p>
                                        <p className="text-xs mt-1">
                                            {trends.models.total_count} models, {trends.simulations.total_count} simulations in last {trends.period.days} days
                                        </p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </>
                )}
            </CardContent>
        </Card>
    );
}

function AnalyticsSkeleton() {
    return (
        <div className="space-y-6">
            {/* Comparison Cards Skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[...Array(3)].map((_, i) => (
                    <Card key={i}>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div className="space-y-2">
                                    <Skeleton className="h-4 w-16" />
                                    <Skeleton className="h-8 w-12" />
                                </div>
                                <div className="flex items-center gap-1">
                                    <Skeleton className="h-3 w-3" />
                                    <Skeleton className="h-4 w-8" />
                                </div>
                            </div>
                            <Skeleton className="h-3 w-20 mt-1" />
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Performance Skeleton */}
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-40" />
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="text-center space-y-2">
                                <Skeleton className="h-6 w-12 mx-auto" />
                                <Skeleton className="h-4 w-20 mx-auto" />
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Breakdown Skeleton */}
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-40" />
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <Skeleton className="h-5 w-16" />
                                    <Skeleton className="h-4 w-20" />
                                </div>
                                <div className="text-right space-y-1">
                                    <Skeleton className="h-4 w-8" />
                                    <Skeleton className="h-3 w-12" />
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}