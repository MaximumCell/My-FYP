'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
    TrendingUp,
    TrendingDown,
    Activity,
    Zap,
    Target,
    Award,
    User
} from 'lucide-react'; interface EnhancedStatCardProps {
    title: string;
    value: string | number;
    change?: {
        value: number;
        type: 'increase' | 'decrease';
        period: string;
    };
    icon: React.ReactNode;
    color: 'primary' | 'accent' | 'green' | 'blue' | 'purple' | 'orange';
    progress?: number;
}

export function EnhancedStatCard({
    title,
    value,
    change,
    icon,
    color,
    progress
}: EnhancedStatCardProps) {
    const colorClasses = {
        primary: {
            icon: 'text-primary bg-primary/10',
            trend: 'text-primary',
            progress: 'bg-primary'
        },
        accent: {
            icon: 'text-accent bg-accent/10',
            trend: 'text-accent',
            progress: 'bg-accent'
        },
        green: {
            icon: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20',
            trend: 'text-green-600 dark:text-green-400',
            progress: 'bg-green-600'
        },
        blue: {
            icon: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20',
            trend: 'text-blue-600 dark:text-blue-400',
            progress: 'bg-blue-600'
        },
        purple: {
            icon: 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20',
            trend: 'text-purple-600 dark:text-purple-400',
            progress: 'bg-purple-600'
        },
        orange: {
            icon: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/20',
            trend: 'text-orange-600 dark:text-orange-400',
            progress: 'bg-orange-600'
        }
    };

    return (
        <Card className="group relative overflow-hidden hover:shadow-lg transition-all duration-300 card-hover">
            {/* Background glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-br from-${color}-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

            <CardContent className="p-6 relative">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
                        <div className="flex items-baseline gap-2">
                            <p className="text-3xl font-bold">{value}</p>
                            {change && (
                                <div className={`flex items-center gap-1 ${colorClasses[color].trend}`}>
                                    {change.type === 'increase' ? (
                                        <TrendingUp className="h-3 w-3" />
                                    ) : (
                                        <TrendingDown className="h-3 w-3" />
                                    )}
                                    <span className="text-xs font-medium">
                                        {change.value}% {change.period}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className={`p-3 rounded-xl ${colorClasses[color].icon} group-hover:scale-110 transition-transform duration-300`}>
                        {icon}
                    </div>
                </div>

                {progress !== undefined && (
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>Progress</span>
                            <span>{progress}%</span>
                        </div>
                        <Progress value={progress} className="h-2" />
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

interface ActivityFeedProps {
    activities: Array<{
        id: string;
        type: 'model' | 'simulation' | 'achievement';
        title: string;
        timestamp: string;
        status?: 'completed' | 'running' | 'failed';
    }>;
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
    const getIcon = (type: string) => {
        switch (type) {
            case 'model':
                return <Activity className="h-4 w-4 text-blue-500" />;
            case 'simulation':
                return <Zap className="h-4 w-4 text-green-500" />;
            case 'achievement':
                return <Award className="h-4 w-4 text-yellow-500" />;
            default:
                return <Target className="h-4 w-4 text-gray-500" />;
        }
    };

    const getStatusBadge = (status?: string) => {
        if (!status) return null;

        const variants = {
            completed: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
            running: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
            failed: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
        };

        return (
            <Badge variant="secondary" className={variants[status as keyof typeof variants]}>
                {status}
            </Badge>
        );
    };

    return (
        <Card>
            <CardContent className="p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Recent Activity
                </h3>

                <div className="space-y-4">
                    {activities.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p>No recent activity</p>
                            <p className="text-sm">Start a project to see your activity here</p>
                        </div>
                    ) : (
                        activities.map((activity) => (
                            <div key={activity.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors group">
                                <div className="flex items-center gap-2">
                                    <div className="flex-shrink-0">
                                        {getIcon(activity.type)}
                                    </div>
                                    <Avatar className="w-6 h-6">
                                        <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white text-xs">
                                            <User className="h-3 w-3" />
                                        </AvatarFallback>
                                    </Avatar>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-sm truncate">{activity.title}</p>
                                    <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
                                </div>
                                {getStatusBadge(activity.status)}
                            </div>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

interface QuickActionProps {
    title: string;
    description: string;
    icon: React.ReactNode;
    onClick: () => void;
    color: string;
}

export function QuickAction({ title, description, icon, onClick, color }: QuickActionProps) {
    return (
        <Card
            className={`group cursor-pointer hover:shadow-lg transition-all duration-300 card-hover bg-gradient-to-br ${color} text-white overflow-hidden`}
            onClick={onClick}
        >
            <CardContent className="p-6 relative">
                <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -translate-y-12 translate-x-12" />
                <div className="relative">
                    <div className="mb-4 text-white/90">
                        {icon}
                    </div>
                    <h3 className="font-semibold mb-2">{title}</h3>
                    <p className="text-sm text-white/80">{description}</p>
                </div>
            </CardContent>
        </Card>
    );
}

interface UserProfileCardProps {
    userImage?: string;
    userName: string;
    userEmail: string;
    memberSince: string;
    lastActive?: string;
    isOnline?: boolean;
}

export function UserProfileCard({
    userImage,
    userName,
    userEmail,
    memberSince,
    lastActive,
    isOnline = true
}: UserProfileCardProps) {
    return (
        <Card className="relative overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-transparent" />

            <CardContent className="p-6 relative">
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Avatar className="w-16 h-16 border-3 border-white/20 shadow-lg">
                            <AvatarImage src={userImage} alt={userName} className="object-cover" />
                            <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white text-xl font-bold">
                                {userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                            </AvatarFallback>
                        </Avatar>
                        {/* Online status */}
                        <div className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white shadow-sm ${isOnline ? 'bg-green-500' : 'bg-gray-400'
                            }`} />
                    </div>

                    <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg truncate">{userName}</h3>
                        <p className="text-sm text-muted-foreground truncate">{userEmail}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            <span>Member since {memberSince}</span>
                            {lastActive && (
                                <span>Last active {lastActive}</span>
                            )}
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}