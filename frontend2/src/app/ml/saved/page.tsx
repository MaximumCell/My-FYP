'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Download, Trash2, Eye, Calendar, Target, Gauge } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import DeleteConfirmationModal from '@/components/ui/delete-confirmation-modal';

interface SavedModel {
    id: string;
    model_name: string;
    model_type: 'classification' | 'regression' | 'deep-learning';
    description?: string;
    algorithm_name?: string;
    file_url: string;
    file_size: number;
    performance_metrics: Record<string, number>;
    dataset_info: {
        columns: string[];
        target_column: string;
        data_shape: { rows: number; columns: number };
    };
    tags: string[];
    training_time: number;
    created_at: string;
    is_public: boolean;
}

interface SavedModelsResponse {
    success: boolean;
    data?: {
        models: SavedModel[];
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

export default function SavedModelsPage() {
    const [models, setModels] = useState<SavedModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deleteModal, setDeleteModal] = useState<{
        isOpen: boolean;
        model: SavedModel | null;
        isDeleting: boolean;
    }>({ isOpen: false, model: null, isDeleting: false });
    const { toast } = useToast();

    useEffect(() => {
        fetchSavedModels();
    }, []);

    const fetchSavedModels = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/models', {
                headers: {
                    'X-User-ID': '68d6278f394fbc66b21a8403', // Your user ID
                },
            });

            const result: SavedModelsResponse = await response.json();

            if (result.success && result.data) {
                setModels(result.data.models);
                setError(null);
            } else {
                setError(result.error?.message || 'Failed to fetch models');
            }
        } catch (err) {
            setError('Network error: Could not connect to server');
            console.error('Error fetching models:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async (model: SavedModel) => {
        try {
            const response = await fetch(`http://localhost:5000/api/models/${model.id}/download`, {
                headers: {
                    'X-User-ID': '68d6278f394fbc66b21a8403',
                },
            });

            if (!response.ok) {
                throw new Error('Download failed');
            }

            const result = await response.json();
            if (result.success && result.data?.download_url) {
                // Open download URL in new tab
                window.open(result.data.download_url, '_blank');
                toast({ title: 'Download started', description: `Downloading ${model.model_name}` });
            } else {
                throw new Error(result.error?.message || 'Download failed');
            }
        } catch (err) {
            toast({
                variant: 'destructive',
                title: 'Download failed',
                description: err instanceof Error ? err.message : 'Unknown error'
            });
        }
    };

    const handleDeleteClick = (model: SavedModel) => {
        setDeleteModal({
            isOpen: true,
            model,
            isDeleting: false
        });
    };

    const handleDeleteConfirm = async () => {
        if (!deleteModal.model) return;

        setDeleteModal(prev => ({ ...prev, isDeleting: true }));

        try {
            const response = await fetch(`http://localhost:5000/api/models/${deleteModal.model.id}`, {
                method: 'DELETE',
                headers: {
                    'X-User-ID': '68d6278f394fbc66b21a8403',
                },
            });

            const result = await response.json();

            if (result.success) {
                setModels(models.filter(m => m.id !== deleteModal.model!.id));
                toast({
                    title: 'Model deleted successfully',
                    description: `${deleteModal.model.model_name} has been permanently deleted`
                });
                setDeleteModal({ isOpen: false, model: null, isDeleting: false });
            } else {
                throw new Error(result.error?.message || 'Delete failed');
            }
        } catch (err) {
            toast({
                variant: 'destructive',
                title: 'Failed to delete model',
                description: err instanceof Error ? err.message : 'An unexpected error occurred'
            });
        } finally {
            setDeleteModal(prev => ({ ...prev, isDeleting: false }));
        }
    };

    const handleDeleteCancel = () => {
        setDeleteModal({ isOpen: false, model: null, isDeleting: false });
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

    const getMainMetric = (model: SavedModel) => {
        if (model.model_type === 'classification') {
            return {
                name: 'Accuracy',
                value: model.performance_metrics.accuracy || 0,
                format: (v: number) => `${(v * 100).toFixed(1)}%`
            };
        } else if (model.model_type === 'deep-learning') {
            // For deep learning models, show Loss as the main metric
            const loss = model.performance_metrics.final_loss || model.performance_metrics.loss || 0;
            return {
                name: 'Loss',
                value: loss,
                format: (v: number) => v.toFixed(4)
            };
        } else {
            // For regression models, show R² Score
            return {
                name: 'R² Score',
                value: model.performance_metrics.r2_score || model.performance_metrics.r_squared || 0,
                format: (v: number) => v.toFixed(3)
            };
        }
    };

    if (loading) {
        return (
            <div className="container mx-auto py-8">
                <h1 className="text-3xl font-bold mb-8">Your Saved Models</h1>
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">Loading your models...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto py-8">
                <h1 className="text-3xl font-bold mb-8">Your Saved Models</h1>
                <Card className="max-w-md mx-auto">
                    <CardHeader>
                        <CardTitle className="text-destructive">Error</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p>{error}</p>
                        <Button onClick={fetchSavedModels} className="mt-4">Try Again</Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="container mx-auto py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Your Saved Models</h1>
                    <p className="text-muted-foreground mt-2">
                        {models.length} model{models.length !== 1 ? 's' : ''} saved to your account
                    </p>
                </div>
                <Button onClick={fetchSavedModels} variant="outline">
                    Refresh
                </Button>
            </div>

            {models.length === 0 ? (
                <Card className="max-w-md mx-auto text-center">
                    <CardHeader>
                        <CardTitle>No Models Found</CardTitle>
                        <CardDescription>
                            Train some models in the ML Lab to see them here!
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button asChild>
                            <a href="/ml">Go to ML Lab</a>
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {models.map((model) => {
                        const mainMetric = getMainMetric(model);
                        return (
                            <Card key={model.id} className="flex flex-col">
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <CardTitle className="text-lg mb-2">{model.model_name}</CardTitle>
                                            <div className="flex gap-2 mb-3">
                                                <Badge variant={model.model_type === 'classification' ? 'default' : 'secondary'}>
                                                    {model.model_type}
                                                </Badge>
                                                {model.algorithm_name && (
                                                    <Badge variant="outline">{model.algorithm_name}</Badge>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    {model.description && (
                                        <CardDescription className="text-sm">{model.description}</CardDescription>
                                    )}
                                </CardHeader>

                                <CardContent className="flex-1">
                                    <div className="space-y-4">
                                        {/* Performance Metric */}
                                        <div className="flex items-center gap-2">
                                            <Gauge className="h-4 w-4 text-muted-foreground" />
                                            <span className="text-sm text-muted-foreground">{mainMetric.name}:</span>
                                            <span className="text-sm font-semibold">{mainMetric.format(mainMetric.value)}</span>
                                        </div>

                                        {/* Dataset Info */}
                                        <div className="flex items-center gap-2">
                                            <Target className="h-4 w-4 text-muted-foreground" />
                                            <span className="text-sm text-muted-foreground">Target:</span>
                                            <span className="text-sm font-medium">{model.dataset_info.target_column}</span>
                                        </div>

                                        <div className="text-xs text-muted-foreground">
                                            {model.dataset_info.data_shape.rows} rows × {model.dataset_info.data_shape.columns} columns
                                        </div>

                                        {/* Tags */}
                                        {model.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-1">
                                                {model.tags.slice(0, 3).map((tag, idx) => (
                                                    <Badge key={idx} variant="outline" className="text-xs">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                                {model.tags.length > 3 && (
                                                    <Badge variant="outline" className="text-xs">
                                                        +{model.tags.length - 3}
                                                    </Badge>
                                                )}
                                            </div>
                                        )}

                                        {/* Created Date */}
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                            <Calendar className="h-3 w-3" />
                                            {formatDate(model.created_at)}
                                        </div>

                                        <div className="text-xs text-muted-foreground">
                                            Size: {formatFileSize(model.file_size)}
                                        </div>
                                    </div>
                                </CardContent>

                                <CardContent className="pt-0">
                                    <div className="flex gap-2">
                                        <Button
                                            onClick={() => handleDownload(model)}
                                            size="sm"
                                            className="flex-1"
                                        >
                                            <Download className="h-4 w-4 mr-1" />
                                            Download
                                        </Button>
                                        <Button
                                            onClick={() => handleDeleteClick(model)}
                                            size="sm"
                                            variant="destructive"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            <DeleteConfirmationModal
                isOpen={deleteModal.isOpen}
                onClose={handleDeleteCancel}
                onConfirm={handleDeleteConfirm}
                title="Delete Model"
                description={`Are you sure you want to permanently delete "${deleteModal.model?.model_name}"?`}
                itemName={deleteModal.model?.model_name || ''}
                isLoading={deleteModal.isDeleting}
            />
        </div>
    );
}