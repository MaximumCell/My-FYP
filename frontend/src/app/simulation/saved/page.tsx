'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Trash2, Calendar, Clock, Target, Gauge } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import DeleteConfirmationModal from '@/components/ui/delete-confirmation-modal';
import HtmlPlotViewer from '@/components/ui/html-plot-viewer';

interface SavedSimulation {
    id: string;
    simulation_name: string;
    simulation_type: 'plot2d' | 'plot3d' | 'interactive-physics' | 'custom-equation' | 'projectile-motion' | 'electric-field' | 'wave-simulation' | 'other';
    description?: string;
    plot_html_url: string;
    plot_public_id: string;
    plot_thumbnail_url?: string;
    file_size: number;
    config: {
        equation?: string;
        parameters: Record<string, any>;
        variables: string[];
        plot_type?: string;
        x_range?: number[];
        y_range?: number[];
        z_range?: number[];
    };
    execution_time: number;
    plot_title?: string;
    x_label?: string;
    y_label?: string;
    z_label?: string;
    tags: string[];
    created_at: string;
    is_public: boolean;
}

interface SavedSimulationsResponse {
    success: boolean;
    data?: {
        simulations: SavedSimulation[];
        total_count: number;
        page: number;
        total_pages: number;
    };
    message?: string;
    error?: {
        code: string;
        message: string;
    };
}

export default function SavedSimulationsPage() {
    const { userId, isLoaded } = useAuth();
    const [simulations, setSimulations] = useState<SavedSimulation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deleteModal, setDeleteModal] = useState<{
        isOpen: boolean;
        simulation: SavedSimulation | null;
        isDeleting: boolean;
    }>({ isOpen: false, simulation: null, isDeleting: false });
    const [plotViewer, setPlotViewer] = useState<{
        isOpen: boolean;
        simulation: SavedSimulation | null;
    }>({ isOpen: false, simulation: null });
    const { toast } = useToast();

    useEffect(() => {
        // Wait for Clerk auth to load and provide a userId before fetching
        if (!isLoaded) return;
        fetchSavedSimulations();
    }, [isLoaded, userId]);

    const fetchSavedSimulations = async () => {
        try {
            setLoading(true);
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
            const headers: Record<string, string> = {};
            if (userId) headers['X-User-ID'] = userId;

            const response = await fetch(`${apiUrl}/api/simulations`, {
                headers,
            });

            const result: SavedSimulationsResponse = await response.json();

            if (result.success && result.data) {
                setSimulations(result.data.simulations);
                setError(null);
            } else {
                setError(result.error?.message || 'Failed to fetch simulations');
            }
        } catch (err) {
            setError('Network error: Could not connect to server');
            console.error('Error fetching simulations:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleView = (simulation: SavedSimulation) => {
        setPlotViewer({
            isOpen: true,
            simulation
        });
    };

    const handleDeleteClick = (simulation: SavedSimulation) => {
        setDeleteModal({
            isOpen: true,
            simulation,
            isDeleting: false
        });
    };

    const handleDeleteConfirm = async () => {
        if (!deleteModal.simulation) return;

        setDeleteModal(prev => ({ ...prev, isDeleting: true }));

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
            const headers: Record<string, string> = {};
            if (userId) headers['X-User-ID'] = userId;

            const response = await fetch(`${apiUrl}/api/simulations/${deleteModal.simulation.id}`, {
                method: 'DELETE',
                headers,
            });

            const result = await response.json();

            if (result.success) {
                setSimulations(simulations.filter(s => s.id !== deleteModal.simulation!.id));
                toast({
                    title: 'Simulation deleted successfully',
                    description: `${deleteModal.simulation.simulation_name} has been permanently deleted`
                });
                setDeleteModal({ isOpen: false, simulation: null, isDeleting: false });
            } else {
                throw new Error(result.error?.message || 'Delete failed');
            }
        } catch (err) {
            toast({
                variant: 'destructive',
                title: 'Failed to delete simulation',
                description: err instanceof Error ? err.message : 'An unexpected error occurred'
            });
        } finally {
            setDeleteModal(prev => ({ ...prev, isDeleting: false }));
        }
    };

    const handleDeleteCancel = () => {
        setDeleteModal({ isOpen: false, simulation: null, isDeleting: false });
    };

    const handlePlotViewerClose = () => {
        setPlotViewer({ isOpen: false, simulation: null });
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatExecutionTime = (seconds: number) => {
        if (seconds < 1) {
            return `${(seconds * 1000).toFixed(0)}ms`;
        } else if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
        }
    };

    const getSimulationTypeColor = (type: string) => {
        const colors = {
            'plot2d': 'default',
            'plot3d': 'secondary',
            'interactive-physics': 'destructive',
            'custom-equation': 'outline',
            'projectile-motion': 'default',
            'electric-field': 'secondary',
            'wave-simulation': 'destructive',
            'other': 'outline'
        } as const;
        return colors[type as keyof typeof colors] || 'outline';
    };

    const getSimulationTypeLabel = (type: string) => {
        const labels = {
            'plot2d': '2D Plot',
            'plot3d': '3D Plot',
            'interactive-physics': 'Interactive Physics',
            'custom-equation': 'Custom Equation',
            'projectile-motion': 'Projectile Motion',
            'electric-field': 'Electric Field',
            'wave-simulation': 'Wave Simulation',
            'other': 'Other'
        };
        return labels[type as keyof typeof labels] || type;
    };

    if (loading) {
        return (
            <div className="container mx-auto py-8">
                <h1 className="text-3xl font-bold mb-8">Your Saved Simulations</h1>
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">Loading your simulations...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto py-8">
                <h1 className="text-3xl font-bold mb-8">Your Saved Simulations</h1>
                <Card className="max-w-md mx-auto">
                    <CardHeader>
                        <CardTitle className="text-destructive">Error</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p>{error}</p>
                        <Button onClick={fetchSavedSimulations} className="mt-4">Try Again</Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="container mx-auto py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Your Saved Simulations</h1>
                    <p className="text-muted-foreground mt-2">
                        {simulations.length} simulation{simulations.length !== 1 ? 's' : ''} saved to your account
                    </p>
                </div>
                <Button onClick={fetchSavedSimulations} variant="outline">
                    Refresh
                </Button>
            </div>

            {simulations.length === 0 ? (
                <Card className="max-w-md mx-auto text-center">
                    <CardHeader>
                        <CardTitle>No Simulations Found</CardTitle>
                        <CardDescription>
                            Run some simulations in the Physics Lab to see them here!
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button asChild>
                            <a href="/simulation">Go to Physics Lab</a>
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {simulations.map((simulation) => (
                        <Card key={simulation.id} className="flex flex-col">
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <CardTitle className="text-lg mb-2">{simulation.simulation_name}</CardTitle>
                                        <div className="flex gap-2 mb-3">
                                            <Badge variant={getSimulationTypeColor(simulation.simulation_type)}>
                                                {getSimulationTypeLabel(simulation.simulation_type)}
                                            </Badge>
                                            {simulation.is_public && (
                                                <Badge variant="outline">Public</Badge>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                {simulation.description && (
                                    <CardDescription className="text-sm">{simulation.description}</CardDescription>
                                )}
                            </CardHeader>

                            <CardContent className="flex-1">
                                <div className="space-y-4">
                                    {/* Plot Title */}
                                    {simulation.plot_title && (
                                        <div className="flex items-center gap-2">
                                            <Target className="h-4 w-4 text-muted-foreground" />
                                            <span className="text-sm text-muted-foreground">Plot:</span>
                                            <span className="text-sm font-medium">{simulation.plot_title}</span>
                                        </div>
                                    )}

                                    {/* Execution Time */}
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-4 w-4 text-muted-foreground" />
                                        <span className="text-sm text-muted-foreground">Runtime:</span>
                                        <span className="text-sm font-semibold">{formatExecutionTime(simulation.execution_time)}</span>
                                    </div>

                                    {/* Equation or Config */}
                                    {simulation.config.equation && (
                                        <div className="text-xs text-muted-foreground font-mono bg-muted p-2 rounded">
                                            {simulation.config.equation}
                                        </div>
                                    )}

                                    {/* Variables */}
                                    {simulation.config.variables && simulation.config.variables.length > 0 && (
                                        <div className="text-xs text-muted-foreground">
                                            Variables: {simulation.config.variables.join(', ')}
                                        </div>
                                    )}

                                    {/* Labels */}
                                    {(simulation.x_label || simulation.y_label || simulation.z_label) && (
                                        <div className="text-xs text-muted-foreground">
                                            {simulation.x_label && `X: ${simulation.x_label}`}
                                            {simulation.y_label && `, Y: ${simulation.y_label}`}
                                            {simulation.z_label && `, Z: ${simulation.z_label}`}
                                        </div>
                                    )}

                                    {/* Tags */}
                                    {simulation.tags.length > 0 && (
                                        <div className="flex flex-wrap gap-1">
                                            {simulation.tags.slice(0, 3).map((tag, idx) => (
                                                <Badge key={idx} variant="outline" className="text-xs">
                                                    {tag}
                                                </Badge>
                                            ))}
                                            {simulation.tags.length > 3 && (
                                                <Badge variant="outline" className="text-xs">
                                                    +{simulation.tags.length - 3}
                                                </Badge>
                                            )}
                                        </div>
                                    )}

                                    {/* Created Date */}
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                        <Calendar className="h-3 w-3" />
                                        {formatDate(simulation.created_at)}
                                    </div>

                                    <div className="text-xs text-muted-foreground">
                                        Size: {formatFileSize(simulation.file_size)}
                                    </div>
                                </div>
                            </CardContent>

                            <CardContent className="pt-0">
                                <div className="flex gap-2">
                                    <Button
                                        onClick={() => handleView(simulation)}
                                        size="sm"
                                        className="flex-1"
                                    >
                                        <Eye className="h-4 w-4 mr-1" />
                                        View
                                    </Button>
                                    <Button
                                        onClick={() => handleDeleteClick(simulation)}
                                        size="sm"
                                        variant="destructive"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            <DeleteConfirmationModal
                isOpen={deleteModal.isOpen}
                onClose={handleDeleteCancel}
                onConfirm={handleDeleteConfirm}
                title="Delete Simulation"
                description={`Are you sure you want to permanently delete "${deleteModal.simulation?.simulation_name}"?`}
                itemName={deleteModal.simulation?.simulation_name || ''}
                isLoading={deleteModal.isDeleting}
            />

            {/* HTML Plot Viewer Modal */}
            {plotViewer.simulation && (
                <HtmlPlotViewer
                    isOpen={plotViewer.isOpen}
                    onClose={handlePlotViewerClose}
                    simulationId={plotViewer.simulation.id}
                    simulationName={plotViewer.simulation.simulation_name}
                    plotTitle={plotViewer.simulation.plot_title}
                />
            )}
        </div>
    );
}