'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, Info, XCircle, CheckCircle, BarChart3, Target } from 'lucide-react';

interface DataPreviewProps {
    analysisData: any;
}

const DataPreview: React.FC<DataPreviewProps> = ({ analysisData }) => {
    if (!analysisData?.success) {
        return (
            <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertTitle>Analysis Failed</AlertTitle>
                <AlertDescription>
                    {analysisData?.error || 'Failed to analyze data'}
                </AlertDescription>
            </Alert>
        );
    }

    const { data_info, preview, columns, target_analysis, warnings, recommendations } = analysisData;

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
            case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
            case 'info': return <Info className="h-4 w-4 text-blue-500" />;
            default: return <Info className="h-4 w-4 text-gray-500" />;
        }
    };

    const getSeverityVariant = (severity: string) => {
        switch (severity) {
            case 'error': return 'destructive' as const;
            case 'warning': return 'default' as const;
            case 'info': return 'default' as const;
            default: return null;
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'destructive';
            case 'medium': return 'default';
            case 'low':
            case 'info': return 'secondary';
            default: return 'outline';
        }
    };

    return (
        <div className="space-y-6">
            {/* Dataset Overview */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        Dataset Overview
                    </CardTitle>
                    <CardDescription>Basic information about your dataset</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center">
                            <p className="text-2xl font-bold text-primary">{data_info.n_rows.toLocaleString()}</p>
                            <p className="text-sm text-muted-foreground">Rows</p>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-primary">{data_info.n_cols}</p>
                            <p className="text-sm text-muted-foreground">Columns</p>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-primary">{data_info.memory_usage}</p>
                            <p className="text-sm text-muted-foreground">Memory Usage</p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Tabs defaultValue="preview" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="preview">Data Preview</TabsTrigger>
                    <TabsTrigger value="columns">Column Info</TabsTrigger>
                    <TabsTrigger value="target">Target Analysis</TabsTrigger>
                    <TabsTrigger value="quality">Quality Check</TabsTrigger>
                </TabsList>

                <TabsContent value="preview" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>First 10 Rows</CardTitle>
                            <CardDescription>Preview of your dataset</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="overflow-x-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            {columns?.slice(0, 8).map((col: any) => (
                                                <TableHead key={col.name} className="min-w-[100px]">
                                                    {col.name}
                                                </TableHead>
                                            ))}
                                            {columns?.length > 8 && (
                                                <TableHead className="text-muted-foreground">
                                                    +{columns.length - 8} more...
                                                </TableHead>
                                            )}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {preview?.slice(0, 10).map((row: any, idx: number) => (
                                            <TableRow key={idx}>
                                                {columns?.slice(0, 8).map((col: any) => (
                                                    <TableCell key={col.name} className="max-w-[150px] truncate">
                                                        {row[col.name] ?? 'null'}
                                                    </TableCell>
                                                ))}
                                                {columns?.length > 8 && <TableCell className="text-muted-foreground">...</TableCell>}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                            {preview?.length > 10 && (
                                <p className="text-sm text-muted-foreground mt-2">
                                    Showing first 10 rows of {data_info.n_rows.toLocaleString()} total rows
                                </p>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="columns" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Column Information</CardTitle>
                            <CardDescription>Detailed statistics for each column</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {columns?.map((col: any) => (
                                    <Card key={col.name} className="p-4">
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-medium">{col.name}</h4>
                                            <div className="flex gap-2">
                                                <Badge variant="outline">{col.dtype}</Badge>
                                                {col.null_count > 0 && (
                                                    <Badge variant="secondary">
                                                        {col.null_count} missing
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                            <div>
                                                <span className="text-muted-foreground">Non-null:</span>
                                                <span className="ml-1 font-medium">{col.non_null_count}</span>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Unique:</span>
                                                <span className="ml-1 font-medium">{col.unique_count}</span>
                                            </div>

                                            {col.mean !== undefined && (
                                                <>
                                                    <div>
                                                        <span className="text-muted-foreground">Mean:</span>
                                                        <span className="ml-1 font-medium">{col.mean.toFixed(2)}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-muted-foreground">Std:</span>
                                                        <span className="ml-1 font-medium">{col.std?.toFixed(2) || 'N/A'}</span>
                                                    </div>
                                                </>
                                            )}

                                            {col.top_values && (
                                                <div className="col-span-2 md:col-span-4">
                                                    <span className="text-muted-foreground">Top values:</span>
                                                    <div className="flex flex-wrap gap-1 mt-1">
                                                        {Object.entries(col.top_values).slice(0, 5).map(([value, count]) => (
                                                            <Badge key={value} variant="outline" className="text-xs">
                                                                {value}: {count as number}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {col.sample_values?.length > 0 && (
                                            <div className="mt-2">
                                                <span className="text-sm text-muted-foreground">Sample values:</span>
                                                <div className="flex flex-wrap gap-1 mt-1">
                                                    {col.sample_values.slice(0, 5).map((value: any, idx: number) => (
                                                        <Badge key={idx} variant="secondary" className="text-xs">
                                                            {String(value)}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </Card>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="target" className="space-y-4">
                    {target_analysis ? (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Target className="h-5 w-5" />
                                    Target Column Analysis: {target_analysis.column}
                                </CardTitle>
                                <CardDescription>Analysis of your target variable for classification</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="text-center">
                                        <p className="text-2xl font-bold text-primary">{target_analysis.n_classes}</p>
                                        <p className="text-sm text-muted-foreground">Classes</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-2xl font-bold text-primary">{target_analysis.missing_values}</p>
                                        <p className="text-sm text-muted-foreground">Missing Values</p>
                                    </div>
                                    <div className="text-center">
                                        <Badge variant="outline" className="text-sm">{target_analysis.data_type}</Badge>
                                        <p className="text-sm text-muted-foreground mt-1">Data Type</p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-3">Class Distribution</h4>
                                    <div className="space-y-2">
                                        {Object.entries(target_analysis.class_percentages).map(([class_name, percentage]) => (
                                            <div key={class_name} className="flex items-center justify-between">
                                                <span className="font-medium">{String(class_name)}</span>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-24 bg-secondary rounded-full h-2">
                                                        <div
                                                            className="bg-primary h-2 rounded-full"
                                                            style={{ width: `${percentage}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-sm font-medium min-w-[60px] text-right">
                                                        {(percentage as number).toFixed(1)}%
                                                    </span>
                                                    <span className="text-sm text-muted-foreground min-w-[40px] text-right">
                                                        ({target_analysis.class_counts[class_name]})
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ) : (
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center text-muted-foreground">
                                    <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                    <p>Select a target column to see detailed analysis</p>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="quality" className="space-y-4">
                    {/* Warnings */}
                    {warnings?.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Data Quality Issues</CardTitle>
                                <CardDescription>Potential problems found in your dataset</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {warnings.map((warning: any, idx: number) => (
                                    <Alert key={idx} variant={getSeverityVariant(warning.severity)}>
                                        {getSeverityIcon(warning.severity)}
                                        <AlertTitle>{warning.message}</AlertTitle>
                                        {warning.details && (
                                            <AlertDescription className="mt-2">
                                                <pre className="text-xs bg-muted p-2 rounded mt-2 overflow-x-auto">
                                                    {JSON.stringify(warning.details, null, 2)}
                                                </pre>
                                            </AlertDescription>
                                        )}
                                    </Alert>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {/* Recommendations */}
                    {recommendations?.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500" />
                                    Recommendations
                                </CardTitle>
                                <CardDescription>Suggestions to improve your ML model performance</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {recommendations.map((rec: any, idx: number) => (
                                    <div key={idx} className="flex items-start gap-3 p-3 border rounded-lg">
                                        <Badge variant={getPriorityColor(rec.priority)} className="mt-0.5">
                                            {rec.priority}
                                        </Badge>
                                        <div className="flex-1">
                                            <p className="text-sm">{rec.message}</p>
                                            <Badge variant="outline" className="mt-1 text-xs">
                                                {rec.type}
                                            </Badge>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {(!warnings?.length && !recommendations?.length) && (
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center text-green-600">
                                    <CheckCircle className="h-12 w-12 mx-auto mb-4" />
                                    <p className="font-medium">No major data quality issues found!</p>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Your dataset looks good for machine learning.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default DataPreview;