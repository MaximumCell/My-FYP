/**
 * CNN Image Upload Component
 * Handles ZIP file upload for CNN image training with drag & drop, validation, and preview
 */

'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileArchive, AlertCircle, CheckCircle, ImageIcon, FolderIcon, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

interface ValidationResult {
    valid: boolean;
    classes: string[];
    total_images: number;
    class_counts: { [key: string]: number };
    errors: string[];
    warnings: string[];
}

interface CNNImageUploadProps {
    onFileValidated: (file: File, validation: ValidationResult) => void;
    onFileRemoved: () => void;
    disabled?: boolean;
}

export default function CNNImageUpload({
    onFileValidated,
    onFileRemoved,
    disabled = false
}: CNNImageUploadProps) {
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [isValidating, setIsValidating] = useState(false);
    const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const { toast } = useToast();

    const validateZipStructure = async (file: File): Promise<ValidationResult> => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/ml/validate/zip-structure', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress(progress);
                    }
                },
            });

            return response.data;
        } catch (error: any) {
            const errorMessage = error.response?.data?.error || 'Validation failed';
            throw new Error(errorMessage);
        }
    };

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (disabled) return;

        const file = acceptedFiles[0];
        if (!file) return;

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.zip')) {
            toast({
                variant: 'destructive',
                title: 'Invalid file type',
                description: 'Please upload a ZIP file containing your images organized by class folders.',
            });
            return;
        }

        // Check file size (limit to 100MB)
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file.size > maxSize) {
            toast({
                variant: 'destructive',
                title: 'File too large',
                description: 'Please upload a ZIP file smaller than 100MB.',
            });
            return;
        }

        setUploadedFile(file);
        setValidationResult(null);
        setIsValidating(true);
        setUploadProgress(0);

        try {
            const validation = await validateZipStructure(file);
            setValidationResult(validation);

            if (validation.valid) {
                onFileValidated(file, validation);
                toast({
                    title: 'ZIP file validated!',
                    description: `Found ${validation.total_images} images in ${validation.classes.length} classes.`,
                });
            } else {
                toast({
                    variant: 'destructive',
                    title: 'Invalid ZIP structure',
                    description: validation.errors.join(', '),
                });
            }
        } catch (error: any) {
            toast({
                variant: 'destructive',
                title: 'Validation failed',
                description: error.message,
            });
            setValidationResult(null);
        } finally {
            setIsValidating(false);
            setUploadProgress(0);
        }
    }, [disabled, onFileValidated, toast]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/zip': ['.zip'],
            'application/x-zip-compressed': ['.zip'],
        },
        maxFiles: 1,
        disabled,
    });

    const handleRemoveFile = () => {
        setUploadedFile(null);
        setValidationResult(null);
        setIsValidating(false);
        setUploadProgress(0);
        onFileRemoved();
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <ImageIcon className="h-5 w-5" />
                    CNN Image Dataset Upload
                </CardTitle>
                <CardDescription>
                    Upload a ZIP file containing your images organized by class folders for CNN training.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {!uploadedFile ? (
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive
                                ? 'border-primary bg-primary/10'
                                : 'border-muted-foreground/25 hover:border-primary hover:bg-primary/5'
                            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        <input {...getInputProps()} />
                        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="text-lg font-semibold mb-2">
                            {isDragActive ? 'Drop your ZIP file here' : 'Upload ZIP file'}
                        </h3>
                        <p className="text-muted-foreground mb-4">
                            Drag and drop your ZIP file here, or click to browse
                        </p>
                        <div className="text-sm text-muted-foreground space-y-1">
                            <p>• ZIP file containing image folders (one folder per class)</p>
                            <p>• Supported formats: JPG, PNG, BMP, TIFF, WebP</p>
                            <p>• Maximum file size: 100MB</p>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {/* File Info */}
                        <div className="flex items-center justify-between p-4 border rounded-lg bg-muted/50">
                            <div className="flex items-center gap-3">
                                <FileArchive className="h-8 w-8 text-primary" />
                                <div>
                                    <p className="font-medium">{uploadedFile.name}</p>
                                    <p className="text-sm text-muted-foreground">
                                        {formatFileSize(uploadedFile.size)}
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleRemoveFile}
                                disabled={isValidating}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        {/* Upload Progress */}
                        {isValidating && (
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Validating ZIP structure...</span>
                                    <span className="text-sm text-muted-foreground">{uploadProgress}%</span>
                                </div>
                                <Progress value={uploadProgress} className="w-full" />
                            </div>
                        )}

                        {/* Validation Results */}
                        {validationResult && (
                            <div className="space-y-4">
                                {validationResult.valid ? (
                                    <Alert className="border-green-200 bg-green-50 dark:bg-green-950/20">
                                        <CheckCircle className="h-4 w-4 text-green-600" />
                                        <AlertDescription className="text-green-800 dark:text-green-200">
                                            ZIP file structure is valid and ready for CNN training!
                                        </AlertDescription>
                                    </Alert>
                                ) : (
                                    <Alert variant="destructive">
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            Invalid ZIP structure: {validationResult.errors.join(', ')}
                                        </AlertDescription>
                                    </Alert>
                                )}

                                {/* Dataset Summary */}
                                {validationResult.valid && (
                                    <Card>
                                        <CardHeader className="pb-3">
                                            <CardTitle className="text-base">Dataset Summary</CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-3">
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                                <div className="space-y-1">
                                                    <p className="text-2xl font-bold text-primary">
                                                        {validationResult.total_images}
                                                    </p>
                                                    <p className="text-sm text-muted-foreground">Total Images</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-2xl font-bold text-primary">
                                                        {validationResult.classes.length}
                                                    </p>
                                                    <p className="text-sm text-muted-foreground">Classes</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-2xl font-bold text-primary">
                                                        {Math.min(...Object.values(validationResult.class_counts))}
                                                    </p>
                                                    <p className="text-sm text-muted-foreground">Min per Class</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-2xl font-bold text-primary">
                                                        {Math.max(...Object.values(validationResult.class_counts))}
                                                    </p>
                                                    <p className="text-sm text-muted-foreground">Max per Class</p>
                                                </div>
                                            </div>

                                            {/* Class Distribution */}
                                            <div className="space-y-2">
                                                <h4 className="font-medium flex items-center gap-2">
                                                    <FolderIcon className="h-4 w-4" />
                                                    Class Distribution
                                                </h4>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                    {validationResult.classes.map((className) => (
                                                        <div
                                                            key={className}
                                                            className="flex items-center justify-between p-2 border rounded"
                                                        >
                                                            <span className="font-medium">{className}</span>
                                                            <Badge variant="secondary">
                                                                {validationResult.class_counts[className]} images
                                                            </Badge>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}

                                {/* Warnings */}
                                {validationResult.warnings && validationResult.warnings.length > 0 && (
                                    <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
                                        <AlertCircle className="h-4 w-4 text-yellow-600" />
                                        <AlertDescription className="text-yellow-800 dark:text-yellow-200">
                                            <strong>Warnings:</strong>
                                            <ul className="list-disc list-inside mt-1">
                                                {validationResult.warnings.map((warning, index) => (
                                                    <li key={index}>{warning}</li>
                                                ))}
                                            </ul>
                                        </AlertDescription>
                                    </Alert>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Expected Structure Guide */}
                {!uploadedFile && (
                    <Card className="border-muted">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">Expected ZIP Structure</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="font-mono text-sm space-y-1">
                                <div>📁 dataset.zip</div>
                                <div className="ml-4">├── 📁 class1/</div>
                                <div className="ml-8">├── 📸 image1.jpg</div>
                                <div className="ml-8">├── 📸 image2.png</div>
                                <div className="ml-8">└── 📸 ...</div>
                                <div className="ml-4">├── 📁 class2/</div>
                                <div className="ml-8">├── 📸 image3.jpg</div>
                                <div className="ml-8">└── 📸 ...</div>
                                <div className="ml-4">└── 📁 class3/</div>
                                <div className="ml-8">└── 📸 ...</div>
                            </div>
                            <p className="text-sm text-muted-foreground mt-3">
                                Each folder represents a class, and should contain images of that class.
                            </p>
                        </CardContent>
                    </Card>
                )}
            </CardContent>
        </Card>
    );
}