/**
 * CNN Image Tester Component
 * Handles single image upload for CNN model testing with preview and results
 */

'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, ImageIcon, Brain, Loader2, TrendingUp, Eye, X, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';
import Image from 'next/image';

interface CNNModel {
    name: string;
    path: string;
    created: number;
    size_mb: number;
    num_classes?: number;
    class_names?: string[];
    input_shape?: number[];
}

interface PredictionResult {
    success: boolean;
    predicted_class: string;
    confidence: number;
    predictions: Array<{
        class: string;
        confidence: number;
        rank?: number;
    }>;
    model_info: {
        model_name: string;
        num_classes: number;
        class_names: string[];
        input_shape: number[];
    };
    image_info: {
        filename: string;
        format: string;
        mode: string;
        size: number[];
        width: number;
        height: number;
    };
}

interface CNNImageTesterProps {
    className?: string;
}

export default function CNNImageTester({ className }: CNNImageTesterProps) {
    const [availableModels, setAvailableModels] = useState<CNNModel[]>([]);
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [isLoadingModels, setIsLoadingModels] = useState(false);
    const [isPredicting, setIsPredicting] = useState(false);
    const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
    const { toast } = useToast();

    // Load available CNN models
    const loadModels = useCallback(async () => {
        setIsLoadingModels(true);
        try {
            const response = await api.get('/ml/models/cnn-images');
            setAvailableModels(response.data.models || []);
        } catch (error: any) {
            const errorMessage = error.response?.data?.error || 'Failed to load models';
            toast({
                variant: 'destructive',
                title: 'Failed to load models',
                description: errorMessage,
            });
        } finally {
            setIsLoadingModels(false);
        }
    }, [toast]);

    // Load models on component mount
    useState(() => {
        loadModels();
    });

    const onImageDrop = useCallback((acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            toast({
                variant: 'destructive',
                title: 'Invalid file type',
                description: 'Please upload a valid image file (JPG, PNG, BMP, TIFF, WebP).',
            });
            return;
        }

        // Check file size (limit to 10MB for single images)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            toast({
                variant: 'destructive',
                title: 'File too large',
                description: 'Please upload an image smaller than 10MB.',
            });
            return;
        }

        setUploadedImage(file);
        setPredictionResult(null);

        // Create image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setImagePreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
    }, [toast]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: onImageDrop,
        accept: {
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/bmp': ['.bmp'],
            'image/tiff': ['.tiff', '.tif'],
            'image/webp': ['.webp'],
        },
        maxFiles: 1,
    });

    const handlePredict = async () => {
        if (!uploadedImage || !selectedModel) {
            toast({
                variant: 'destructive',
                title: 'Missing requirements',
                description: 'Please upload an image and select a model.',
            });
            return;
        }

        setIsPredicting(true);
        try {
            const formData = new FormData();
            formData.append('file', uploadedImage);
            formData.append('model_name', selectedModel);

            const response = await api.post('/ml/test/cnn-images', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setPredictionResult(response.data);

            if (response.data.success) {
                toast({
                    title: 'Prediction successful!',
                    description: `Predicted class: ${response.data.predicted_class} (${(response.data.confidence * 100).toFixed(1)}% confidence)`,
                });
            }
        } catch (error: any) {
            const errorMessage = error.response?.data?.error || 'Prediction failed';
            toast({
                variant: 'destructive',
                title: 'Prediction failed',
                description: errorMessage,
            });
        } finally {
            setIsPredicting(false);
        }
    };

    const handleRemoveImage = () => {
        setUploadedImage(null);
        setImagePreview(null);
        setPredictionResult(null);
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const getConfidenceColor = (confidence: number): string => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfidenceBarColor = (confidence: number): string => {
        if (confidence >= 0.8) return 'bg-green-500';
        if (confidence >= 0.6) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Model Selection */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        Select CNN Model
                    </CardTitle>
                    <CardDescription>
                        Choose a trained CNN model to test with your image
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <Label htmlFor="model-select">Available Models</Label>
                            <Select value={selectedModel} onValueChange={setSelectedModel}>
                                <SelectTrigger id="model-select">
                                    <SelectValue
                                        placeholder={
                                            isLoadingModels
                                                ? "Loading models..."
                                                : availableModels.length === 0
                                                    ? "No CNN models available"
                                                    : "Select a CNN model"
                                        }
                                    />
                                </SelectTrigger>
                                <SelectContent>
                                    {availableModels.map((model) => (
                                        <SelectItem key={model.name} value={model.name}>
                                            <div className="flex flex-col">
                                                <span className="font-medium">{model.name}</span>
                                                <span className="text-sm text-muted-foreground">
                                                    {model.num_classes} classes • {model.size_mb} MB
                                                </span>
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <Button
                            variant="outline"
                            onClick={loadModels}
                            disabled={isLoadingModels}
                            className="mt-6"
                        >
                            {isLoadingModels && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Refresh
                        </Button>
                    </div>

                    {selectedModel && availableModels.length > 0 && (
                        <div className="p-4 border rounded-lg bg-muted/50">
                            {(() => {
                                const model = availableModels.find(m => m.name === selectedModel);
                                if (!model) return null;

                                return (
                                    <div className="space-y-2">
                                        <h4 className="font-medium">Model Information</h4>
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                            <div>
                                                <span className="text-muted-foreground">Classes:</span>
                                                <p className="font-medium">{model.num_classes || 'Unknown'}</p>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Size:</span>
                                                <p className="font-medium">{model.size_mb} MB</p>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Created:</span>
                                                <p className="font-medium">
                                                    {new Date(model.created * 1000).toLocaleDateString()}
                                                </p>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Input:</span>
                                                <p className="font-medium">
                                                    {model.input_shape ? `${model.input_shape[0]}×${model.input_shape[1]}` : 'Unknown'}
                                                </p>
                                            </div>
                                        </div>
                                        {model.class_names && model.class_names.length > 0 && (
                                            <div>
                                                <span className="text-muted-foreground text-sm">Classes:</span>
                                                <div className="flex flex-wrap gap-1 mt-1">
                                                    {model.class_names.map((className) => (
                                                        <Badge key={className} variant="outline" className="text-xs">
                                                            {className}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })()}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Image Upload */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <ImageIcon className="h-5 w-5" />
                        Upload Test Image
                    </CardTitle>
                    <CardDescription>
                        Upload an image to test with the selected CNN model
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {!uploadedImage ? (
                        <div
                            {...getRootProps()}
                            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive
                                    ? 'border-primary bg-primary/10'
                                    : 'border-muted-foreground/25 hover:border-primary hover:bg-primary/5'
                                }`}
                        >
                            <input {...getInputProps()} />
                            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                            <h3 className="text-lg font-semibold mb-2">
                                {isDragActive ? 'Drop your image here' : 'Upload test image'}
                            </h3>
                            <p className="text-muted-foreground mb-4">
                                Drag and drop your image here, or click to browse
                            </p>
                            <div className="text-sm text-muted-foreground space-y-1">
                                <p>• Supported formats: JPG, PNG, BMP, TIFF, WebP</p>
                                <p>• Maximum file size: 10MB</p>
                                <p>• Images will be automatically resized for the model</p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Image Preview */}
                            <div className="flex items-start gap-4 p-4 border rounded-lg">
                                <div className="relative w-32 h-32 border rounded-lg overflow-hidden bg-muted">
                                    {imagePreview && (
                                        <Image
                                            src={imagePreview}
                                            alt="Test image preview"
                                            fill
                                            className="object-cover"
                                        />
                                    )}
                                </div>
                                <div className="flex-1 space-y-2">
                                    <div className="flex items-center justify-between">
                                        <h4 className="font-medium">{uploadedImage.name}</h4>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={handleRemoveImage}
                                        >
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                            <span className="text-muted-foreground">Size:</span>
                                            <p>{formatFileSize(uploadedImage.size)}</p>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground">Type:</span>
                                            <p>{uploadedImage.type}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Predict Button */}
                            <Button
                                onClick={handlePredict}
                                disabled={!selectedModel || isPredicting}
                                className="w-full"
                                size="lg"
                            >
                                {isPredicting && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
                                <Brain className="mr-2 h-5 w-5" />
                                {isPredicting ? 'Predicting...' : 'Predict Image Class'}
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Prediction Results */}
            {predictionResult && predictionResult.success && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5" />
                            Prediction Results
                        </CardTitle>
                        <CardDescription>
                            Model: {predictionResult.model_info.model_name}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* Main Prediction */}
                        <div className="text-center space-y-4">
                            <div className="space-y-2">
                                <h3 className="text-2xl font-bold">
                                    {predictionResult.predicted_class}
                                </h3>
                                <div className="flex items-center justify-center gap-2">
                                    <span className="text-lg font-semibold">Confidence:</span>
                                    <span className={`text-lg font-bold ${getConfidenceColor(predictionResult.confidence)}`}>
                                        {(predictionResult.confidence * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <div className="w-full max-w-md mx-auto">
                                    <div className="bg-muted rounded-full h-3">
                                        <div
                                            className={`h-3 rounded-full transition-all duration-500 ${getConfidenceBarColor(predictionResult.confidence)}`}
                                            style={{ width: `${predictionResult.confidence * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* All Predictions */}
                        {predictionResult.predictions && predictionResult.predictions.length > 1 && (
                            <div className="space-y-3">
                                <h4 className="font-medium">All Class Predictions</h4>
                                <div className="space-y-2">
                                    {predictionResult.predictions.map((pred, index) => (
                                        <div key={index} className="flex items-center justify-between p-3 border rounded">
                                            <div className="flex items-center gap-3">
                                                <span className="font-medium">{pred.class}</span>
                                                {pred.rank && (
                                                    <Badge variant="outline">#{pred.rank}</Badge>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className={`font-semibold ${getConfidenceColor(pred.confidence)}`}>
                                                    {(pred.confidence * 100).toFixed(1)}%
                                                </span>
                                                <div className="w-20 bg-muted rounded-full h-2">
                                                    <div
                                                        className={`h-2 rounded-full ${getConfidenceBarColor(pred.confidence)}`}
                                                        style={{ width: `${pred.confidence * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Image Information */}
                        {predictionResult.image_info && (
                            <div className="space-y-3">
                                <h4 className="font-medium">Image Information</h4>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    <div>
                                        <span className="text-muted-foreground">Dimensions:</span>
                                        <p className="font-medium">
                                            {predictionResult.image_info.width} × {predictionResult.image_info.height}
                                        </p>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground">Format:</span>
                                        <p className="font-medium">{predictionResult.image_info.format}</p>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground">Mode:</span>
                                        <p className="font-medium">{predictionResult.image_info.mode}</p>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground">Model Input:</span>
                                        <p className="font-medium">
                                            {predictionResult.model_info.input_shape[0]} × {predictionResult.model_info.input_shape[1]}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* No Models Available */}
            {!isLoadingModels && availableModels.length === 0 && (
                <Card className="border-dashed">
                    <CardContent className="text-center py-12">
                        <Brain className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No CNN Models Available</h3>
                        <p className="text-muted-foreground mb-4">
                            You need to train a CNN model first before you can test images.
                        </p>
                        <p className="text-sm text-muted-foreground">
                            Go to the "Train Models" tab to upload a ZIP file and train your first CNN model.
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}