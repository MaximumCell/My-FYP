'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { BarChart3, Target, AlertCircle, CheckCircle } from 'lucide-react';

import type { ModelType } from '@/types/api';

interface EnhancedResultsProps {
    results: any;
    modelType: ModelType;
}

const EnhancedResults: React.FC<EnhancedResultsProps> = ({ results, modelType }) => {
    const getPerformanceColor = (score: number, type: 'accuracy' | 'f1' | 'other') => {
        if (type === 'accuracy' || type === 'f1') {
            if (score >= 0.9) return 'text-green-600';
            if (score >= 0.8) return 'text-blue-600';
            if (score >= 0.7) return 'text-yellow-600';
            return 'text-red-600';
        }
        return 'text-gray-600';
    };

    const getPerformanceVerdict = (score: number, type: 'accuracy' | 'f1') => {
        if (score >= 0.9) return 'Excellent';
        if (score >= 0.8) return 'Good';
        if (score >= 0.7) return 'Fair';
        return 'Poor';
    };

    if (modelType === 'classification') {
        return (
            <div className="space-y-6">
                {/* Main Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Accuracy</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className={`text-3xl font-bold ${getPerformanceColor(results.accuracy, 'accuracy')}`}>
                                {(results.accuracy * 100).toFixed(1)}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                {getPerformanceVerdict(results.accuracy, 'accuracy')}
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">F1 Score</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className={`text-3xl font-bold ${getPerformanceColor(results.f1_score, 'f1')}`}>
                                {(results.f1_score * 100).toFixed(1)}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                {getPerformanceVerdict(results.f1_score, 'f1')}
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Precision</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-blue-600">
                                {(results.precision * 100).toFixed(1)}%
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Recall</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-purple-600">
                                {(results.recall * 100).toFixed(1)}%
                            </p>
                        </CardContent>
                    </Card>
                </div>

                <Tabs defaultValue="overview" className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="confusion">Confusion Matrix</TabsTrigger>
                        <TabsTrigger value="classes">Per-Class Metrics</TabsTrigger>
                        <TabsTrigger value="distribution">Class Distribution</TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5" />
                                    Model Performance Summary
                                </CardTitle>
                                <CardDescription>Overall assessment of your classification model</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <h4 className="font-medium mb-2">Training Statistics</h4>
                                        <div className="space-y-1 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Training samples:</span>
                                                <span className="font-medium">{results.n_train_samples?.toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Test samples:</span>
                                                <span className="font-medium">{results.n_test_samples?.toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Features:</span>
                                                <span className="font-medium">{results.n_features}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Classes:</span>
                                                <span className="font-medium">{results.class_names?.length}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium mb-2">Performance Indicators</h4>
                                        <div className="space-y-2">
                                            {results.accuracy >= 0.8 ? (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">High accuracy achieved</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-2 text-yellow-600">
                                                    <AlertCircle className="h-4 w-4" />
                                                    <span className="text-sm">Accuracy could be improved</span>
                                                </div>
                                            )}

                                            {results.roc_auc && results.roc_auc >= 0.8 && (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">Good ROC-AUC score: {(results.roc_auc * 100).toFixed(1)}%</span>
                                                </div>
                                            )}

                                            {results.f1_score >= 0.8 ? (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">Balanced precision-recall performance</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-2 text-yellow-600">
                                                    <AlertCircle className="h-4 w-4" />
                                                    <span className="text-sm">Consider addressing class imbalance</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="confusion" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Confusion Matrix</CardTitle>
                                <CardDescription>Detailed breakdown of predictions vs actual values</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {results.confusion_matrix && (
                                    <div className="overflow-x-auto">
                                        <Table>
                                            <TableHeader>
                                                <TableRow>
                                                    <TableHead className="w-[100px]">Actual / Predicted</TableHead>
                                                    {results.class_names?.map((className: string) => (
                                                        <TableHead key={className} className="text-center min-w-[80px]">
                                                            {className}
                                                        </TableHead>
                                                    ))}
                                                </TableRow>
                                            </TableHeader>
                                            <TableBody>
                                                {results.confusion_matrix.map((row: number[], rowIndex: number) => (
                                                    <TableRow key={rowIndex}>
                                                        <TableCell className="font-medium">
                                                            {results.class_names?.[rowIndex] || `Class ${rowIndex}`}
                                                        </TableCell>
                                                        {row.map((value: number, colIndex: number) => (
                                                            <TableCell
                                                                key={colIndex}
                                                                className={`text-center ${rowIndex === colIndex ? 'bg-green-50 font-bold' : ''}`}
                                                            >
                                                                {value}
                                                            </TableCell>
                                                        ))}
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="classes" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Per-Class Performance</CardTitle>
                                <CardDescription>Detailed metrics for each class</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {results.classification_report && (
                                    <div className="overflow-x-auto">
                                        <Table>
                                            <TableHeader>
                                                <TableRow>
                                                    <TableHead>Class</TableHead>
                                                    <TableHead className="text-center">Precision</TableHead>
                                                    <TableHead className="text-center">Recall</TableHead>
                                                    <TableHead className="text-center">F1-Score</TableHead>
                                                    <TableHead className="text-center">Support</TableHead>
                                                </TableRow>
                                            </TableHeader>
                                            <TableBody>
                                                {Object.entries(results.classification_report)
                                                    .filter(([key]) => !['accuracy', 'macro avg', 'weighted avg'].includes(key))
                                                    .map(([className, metrics]: [string, any]) => (
                                                        <TableRow key={className}>
                                                            <TableCell className="font-medium">{className}</TableCell>
                                                            <TableCell className="text-center">
                                                                {(metrics.precision * 100).toFixed(1)}%
                                                            </TableCell>
                                                            <TableCell className="text-center">
                                                                {(metrics.recall * 100).toFixed(1)}%
                                                            </TableCell>
                                                            <TableCell className="text-center">
                                                                {(metrics['f1-score'] * 100).toFixed(1)}%
                                                            </TableCell>
                                                            <TableCell className="text-center">{metrics.support}</TableCell>
                                                        </TableRow>
                                                    ))}
                                            </TableBody>
                                        </Table>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="distribution" className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Target className="h-5 w-5" />
                                        Training Set Distribution
                                    </CardTitle>
                                    <CardDescription>Class distribution in training data</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    {results.train_class_distribution && (
                                        <div className="space-y-2">
                                            {Object.entries(results.train_class_distribution).map(([className, count]) => {
                                                const percentage = ((count as number) / results.n_train_samples * 100);
                                                return (
                                                    <div key={className} className="flex items-center justify-between">
                                                        <span className="font-medium">{className}</span>
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-20 bg-secondary rounded-full h-2">
                                                                <div
                                                                    className="bg-primary h-2 rounded-full"
                                                                    style={{ width: `${percentage}%` }}
                                                                />
                                                            </div>
                                                            <span className="text-sm font-medium min-w-[50px] text-right">
                                                                {percentage.toFixed(1)}%
                                                            </span>
                                                            <span className="text-sm text-muted-foreground min-w-[40px] text-right">
                                                                ({String(count)})
                                                            </span>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Target className="h-5 w-5" />
                                        Test Set Distribution
                                    </CardTitle>
                                    <CardDescription>Class distribution in test data</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    {results.test_class_distribution && (
                                        <div className="space-y-2">
                                            {Object.entries(results.test_class_distribution).map(([className, count]) => {
                                                const percentage = ((count as number) / results.n_test_samples * 100);
                                                return (
                                                    <div key={className} className="flex items-center justify-between">
                                                        <span className="font-medium">{className}</span>
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-20 bg-secondary rounded-full h-2">
                                                                <div
                                                                    className="bg-primary h-2 rounded-full"
                                                                    style={{ width: `${percentage}%` }}
                                                                />
                                                            </div>
                                                            <span className="text-sm font-medium min-w-[50px] text-right">
                                                                {percentage.toFixed(1)}%
                                                            </span>
                                                            <span className="text-sm text-muted-foreground min-w-[40px] text-right">
                                                                ({String(count)})
                                                            </span>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
        );
    }

    // For deep learning models, show specialized metrics
    if (modelType === 'deep-learning') {
        // Check if this is a CNN/image classification model (has accuracy metrics)
        const isCNNModel = results.final_accuracy !== undefined || results.accuracy !== undefined ||
            results.final_val_accuracy !== undefined || results.val_accuracy !== undefined;

        return (
            <div className="space-y-6">
                {/* Main Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Training Loss</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-blue-600">
                                {results.final_loss !== undefined ? results.final_loss.toFixed(4) :
                                    results.loss !== undefined ? results.loss.toFixed(4) : 'N/A'}
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Validation Loss</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-purple-600">
                                {results.final_val_loss !== undefined ? results.final_val_loss.toFixed(4) :
                                    results.val_loss !== undefined ? results.val_loss.toFixed(4) : 'N/A'}
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                {isCNNModel ? 'Training Accuracy' : 'Training MAE'}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-green-600">
                                {isCNNModel ?
                                    (results.final_accuracy !== undefined ? `${(results.final_accuracy * 100).toFixed(1)}%` :
                                        results.accuracy !== undefined ? `${(results.accuracy * 100).toFixed(1)}%` : 'N/A') :
                                    (results.final_mae ? results.final_mae.toFixed(4) : 'N/A')
                                }
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">
                                {isCNNModel ? 'Validation Accuracy' : 'Validation MAE'}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-3xl font-bold text-orange-600">
                                {isCNNModel ?
                                    (results.final_val_accuracy !== undefined ? `${(results.final_val_accuracy * 100).toFixed(1)}%` :
                                        results.val_accuracy !== undefined ? `${(results.val_accuracy * 100).toFixed(1)}%` : 'N/A') :
                                    (results.final_val_mae ? results.final_val_mae.toFixed(4) : 'N/A')
                                }
                            </p>
                        </CardContent>
                    </Card>
                </div>

                <Tabs defaultValue="overview" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="overview">Training Overview</TabsTrigger>
                        <TabsTrigger value="architecture">Model Architecture</TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5" />
                                    Training Summary
                                </CardTitle>
                                <CardDescription>Deep learning model training results</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <h4 className="font-medium mb-2">Training Statistics</h4>
                                        <div className="space-y-1 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Epochs trained:</span>
                                                <span className="font-medium">{results.epochs_trained || results.epochs || 'N/A'}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Samples used:</span>
                                                <span className="font-medium">
                                                    {results.samples_used?.toLocaleString() ||
                                                        results.total_samples?.toLocaleString() ||
                                                        results.training_samples?.toLocaleString() || 'N/A'}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">
                                                    {isCNNModel ? 'Classes:' : 'Features:'}
                                                </span>
                                                <span className="font-medium">
                                                    {isCNNModel ?
                                                        (results.num_classes || results.classes?.length || 'N/A') :
                                                        (results.features_used || 'N/A')
                                                    }
                                                </span>
                                            </div>
                                            {results.total_params && (
                                                <div className="flex justify-between">
                                                    <span className="text-muted-foreground">Total parameters:</span>
                                                    <span className="font-medium">{results.total_params.toLocaleString()}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium mb-2">Performance Indicators</h4>
                                        <div className="space-y-2">
                                            {/* Check for overfitting using available loss metrics */}
                                            {(results.final_val_loss !== undefined || results.val_loss !== undefined) &&
                                                (results.final_loss !== undefined || results.loss !== undefined) && (() => {
                                                    const valLoss = results.final_val_loss || results.val_loss;
                                                    const trainLoss = results.final_loss || results.loss;
                                                    const isGoodGeneralization = valLoss < trainLoss * 1.5;
                                                    return (
                                                        <div className={`flex items-center gap-2 ${isGoodGeneralization ? 'text-green-600' : 'text-yellow-600'}`}>
                                                            {isGoodGeneralization ?
                                                                <CheckCircle className="h-4 w-4" /> :
                                                                <AlertCircle className="h-4 w-4" />
                                                            }
                                                            <span className="text-sm">
                                                                {isGoodGeneralization ?
                                                                    'Good generalization (low overfitting)' :
                                                                    'Possible overfitting detected'
                                                                }
                                                            </span>
                                                        </div>
                                                    );
                                                })()}

                                            {/* Accuracy indicators for CNN models */}
                                            {isCNNModel && (results.final_accuracy !== undefined || results.accuracy !== undefined) && (() => {
                                                const accuracy = results.final_accuracy || results.accuracy;
                                                return (
                                                    <div className={`flex items-center gap-2 ${accuracy >= 0.8 ? 'text-green-600' : 'text-yellow-600'}`}>
                                                        {accuracy >= 0.8 ?
                                                            <CheckCircle className="h-4 w-4" /> :
                                                            <AlertCircle className="h-4 w-4" />
                                                        }
                                                        <span className="text-sm">
                                                            {accuracy >= 0.9 ? 'Excellent accuracy achieved' :
                                                                accuracy >= 0.8 ? 'Good accuracy achieved' :
                                                                    'Consider more training or data augmentation'
                                                            }
                                                        </span>
                                                    </div>
                                                );
                                            })()}

                                            {/* MAE indicators for regression models */}
                                            {!isCNNModel && results.final_mae && results.final_mae < 1000 && (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">Low mean absolute error</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="architecture" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Model Architecture</CardTitle>
                                <CardDescription>Neural network structure and hyperparameters</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {results.architecture && (
                                    <div className="space-y-4">
                                        <div>
                                            <h4 className="font-medium mb-2">Layer Configuration</h4>
                                            <div className="space-y-2">
                                                {results.architecture.hidden_layers?.map((units: number, idx: number) => (
                                                    <div key={idx} className="flex items-center justify-between p-2 bg-secondary rounded">
                                                        <span className="text-sm">Hidden Layer {idx + 1}</span>
                                                        <Badge variant="outline">{units} units</Badge>
                                                    </div>
                                                ))}
                                                <div className="flex items-center justify-between p-2 bg-secondary rounded">
                                                    <span className="text-sm">Output Layer</span>
                                                    <Badge variant="outline">1 unit</Badge>
                                                </div>
                                            </div>
                                        </div>

                                        <div>
                                            <h4 className="font-medium mb-2">Hyperparameters</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                                <div className="flex justify-between">
                                                    <span className="text-muted-foreground">Dropout Rate:</span>
                                                    <span className="font-medium">{results.architecture.dropout_rate || 'N/A'}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-muted-foreground">Learning Rate:</span>
                                                    <span className="font-medium">{results.architecture.learning_rate || 'N/A'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        );
    }

    // Format large numbers to avoid overflow
    const formatNumber = (value: number) => {
        if (Math.abs(value) >= 1e9) {
            return (value / 1e9).toFixed(2) + 'B';
        } else if (Math.abs(value) >= 1e6) {
            return (value / 1e6).toFixed(2) + 'M';
        } else if (Math.abs(value) >= 1e3) {
            return (value / 1e3).toFixed(2) + 'K';
        } else if (Math.abs(value) >= 1) {
            return value.toFixed(4);
        } else {
            return value.toExponential(3);
        }
    };

    // Deep learning specific display
    if (modelType === 'deep-learning') {
        return (
            <div className="space-y-6">
                {/* Main Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Final Loss</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-2xl font-bold text-blue-600">
                                {typeof results.final_loss === 'number' ? formatNumber(results.final_loss) : 'N/A'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">Training Loss</p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Val Loss</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-2xl font-bold text-purple-600">
                                {typeof results.final_val_loss === 'number' ? formatNumber(results.final_val_loss) : 'N/A'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">Validation Loss</p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">MAE</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-2xl font-bold text-green-600">
                                {typeof results.final_mae === 'number' ? formatNumber(results.final_mae) : 'N/A'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">Mean Absolute Error</p>
                        </CardContent>
                    </Card>

                    <Card className="text-center">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-muted-foreground">Val MAE</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                            <p className="text-2xl font-bold text-orange-600">
                                {typeof results.final_val_mae === 'number' ? formatNumber(results.final_val_mae) : 'N/A'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">Validation MAE</p>
                        </CardContent>
                    </Card>
                </div>

                <Tabs defaultValue="overview" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="overview">Training Overview</TabsTrigger>
                        <TabsTrigger value="architecture">Model Architecture</TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5" />
                                    Deep Learning Training Summary
                                </CardTitle>
                                <CardDescription>Performance metrics and training statistics</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <h4 className="font-medium mb-2">Training Statistics</h4>
                                        <div className="space-y-1 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Epochs trained:</span>
                                                <span className="font-medium">{results.epochs_trained}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Samples used:</span>
                                                <span className="font-medium">{results.samples_used?.toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Features used:</span>
                                                <span className="font-medium">{results.features_used}</span>
                                            </div>
                                            {results.target_std && (
                                                <div className="flex justify-between">
                                                    <span className="text-muted-foreground">Target std dev:</span>
                                                    <span className="font-medium">{formatNumber(results.target_std)}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium mb-2">Performance Indicators</h4>
                                        <div className="space-y-2">
                                            {results.final_loss < 1 ? (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">Low training loss achieved</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-2 text-yellow-600">
                                                    <AlertCircle className="h-4 w-4" />
                                                    <span className="text-sm">Consider more epochs or data preprocessing</span>
                                                </div>
                                            )}

                                            {results.final_val_loss && results.final_loss &&
                                                Math.abs(results.final_val_loss - results.final_loss) / results.final_loss < 0.2 ? (
                                                <div className="flex items-center gap-2 text-green-600">
                                                    <CheckCircle className="h-4 w-4" />
                                                    <span className="text-sm">Good train-validation balance</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-2 text-yellow-600">
                                                    <AlertCircle className="h-4 w-4" />
                                                    <span className="text-sm">Monitor for overfitting/underfitting</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="architecture" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Neural Network Architecture</CardTitle>
                                <CardDescription>Model structure and hyperparameters</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {results.architecture && (
                                    <div className="space-y-4">
                                        <div>
                                            <h4 className="font-medium mb-2">Layer Configuration</h4>
                                            <div className="bg-muted p-4 rounded-lg">
                                                <div className="space-y-2 text-sm font-mono">
                                                    <div>Input: {results.features_used} features</div>
                                                    {results.architecture.hidden_layers?.map((units: number, idx: number) => (
                                                        <div key={idx}>
                                                            Dense({units}) → ReLU
                                                            {results.architecture.dropout_rate > 0 && (
                                                                <div className="ml-4">Dropout({results.architecture.dropout_rate})</div>
                                                            )}
                                                        </div>
                                                    ))}
                                                    <div>Output: Dense(1)</div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="text-center">
                                                <p className="text-lg font-bold">{results.architecture.learning_rate}</p>
                                                <p className="text-sm text-muted-foreground">Learning Rate</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-lg font-bold">{results.architecture.dropout_rate}</p>
                                                <p className="text-sm text-muted-foreground">Dropout Rate</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-lg font-bold">
                                                    {results.architecture.hidden_layers?.reduce((a: number, b: number) => a + b, 0) + results.features_used + 1}
                                                </p>
                                                <p className="text-sm text-muted-foreground">Total Parameters (approx)</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        );
    }

    // For regression models, keep the existing simple display but with better number formatting
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {Object.entries(results)
                .filter(([key]) => key !== 'message' && key !== 'model_path')
                .map(([key, value]) => (
                    <Card key={key} className="text-center">
                        <CardHeader>
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                {key.replace(/_/g, ' ').toUpperCase()}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-2xl font-bold">
                                {typeof value === 'number' ? formatNumber(value) : String(value)}
                            </p>
                        </CardContent>
                    </Card>
                ))}
        </div>
    );
};

export default EnhancedResults;