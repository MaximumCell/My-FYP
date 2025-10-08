// lib/model-storage.ts
import api from './api';

export interface SaveModelRequest {
    modelName: string;
    modelType: 'classification' | 'regression' | 'deep-learning';
    description?: string;
    isPublic?: boolean;
    tags?: string[];
    algorithmName?: string;
    hyperparameters?: Record<string, any>;
    datasetInfo: {
        columns: string[];
        target_column: string;
        data_shape: {
            rows: number;
            columns: number;
        };
        feature_types?: Record<string, string>;
    };
    performanceMetrics: Record<string, number>;
    trainingTime: number;
}

export interface SaveModelResponse {
    success: boolean;
    data?: {
        id: string;
        model_name: string;
        file_url: string;
        created_at: string;
    };
    message?: string;
    error?: {
        code: string;
        message: string;
    };
}

/**
 * Save a trained model to the backend (MongoDB + Cloudinary)
 * This downloads the model from the old backend and uploads it to the new system
 */
export async function saveTrainedModel(
    modelFilePath: string, // Path to the .pkl file from training
    modelData: SaveModelRequest,
    userToken?: string // Clerk token for authentication
): Promise<SaveModelResponse> {
    try {
        // Step 1: Download the trained model file from the old backend
        console.log('Downloading model file:', modelFilePath, 'for model type:', modelData.modelType);

        // Map modelType to correct download endpoint
        const downloadEndpoint = modelData.modelType === 'deep-learning'
            ? `/ml/download/deep-learning/${modelFilePath}`
            : `/ml/download/${modelData.modelType}/${modelFilePath}`;

        console.log('Using download endpoint:', downloadEndpoint);

        const modelResponse = await api.get(downloadEndpoint, {
            responseType: 'blob',
        });

        console.log('Model download successful, blob size:', modelResponse.data.size);

        // Step 2: Create a File object from the blob
        const modelBlob = new Blob([modelResponse.data], { type: 'application/octet-stream' });

        // Determine correct file extension based on model type
        let fileExtension = '.pkl'; // default
        if (modelData.modelType === 'deep-learning') {
            // For deep learning, try to preserve original extension if it's keras
            if (modelFilePath.toLowerCase().includes('.keras')) {
                fileExtension = '.keras';
            }
        }

        const modelFile = new File([modelBlob], `${modelData.modelName}${fileExtension}`, { type: 'application/octet-stream' });
        console.log('Created model file:', modelFile.name, 'size:', modelFile.size);

        // Step 3: Prepare form data for the new API
        const formData = new FormData();
        formData.append('file', modelFile);
        formData.append('model_name', modelData.modelName);
        formData.append('model_type', modelData.modelType);
        formData.append('dataset_info', JSON.stringify(modelData.datasetInfo));
        formData.append('performance_metrics', JSON.stringify(modelData.performanceMetrics));
        formData.append('training_time', modelData.trainingTime.toString());

        if (modelData.description) {
            formData.append('description', modelData.description);
        }

        if (modelData.tags && modelData.tags.length > 0) {
            formData.append('tags', modelData.tags.join(','));
        }

        if (modelData.algorithmName) {
            formData.append('algorithm_name', modelData.algorithmName);
        }

        if (modelData.hyperparameters) {
            formData.append('hyperparameters', JSON.stringify(modelData.hyperparameters));
        }

        formData.append('is_public', (modelData.isPublic || false).toString());

        // Step 4: Upload to the new model management API
        const headers: Record<string, string> = {
            // Don't set Content-Type for FormData - let the browser set it with boundary
        };

        // Add authentication if available
        if (userToken) {
            headers['Authorization'] = `Bearer ${userToken}`;
        }

        // For now, we'll use a test user ID header until Clerk integration is complete
        // This should be replaced with proper Clerk user ID extraction
        headers['X-User-ID'] = '68d6278f394fbc66b21a8403'; // Your actual user ID

        console.log('Uploading model to new API...');
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
        const uploadResponse = await fetch(`${apiUrl}/api/models/upload`, {
            method: 'POST',
            headers,
            body: formData,
        });

        const result = await uploadResponse.json();
        console.log('Upload response status:', uploadResponse.status);
        console.log('Upload response data:', result);

        if (!uploadResponse.ok) {
            console.error('Upload failed with status:', uploadResponse.status);
            console.error('Error details:', result);
            throw new Error(result.error?.message || result.message || 'Upload failed');
        }

        console.log('Model saved successfully:', result);
        return result;

    } catch (error) {
        console.error('Error saving model:', error);
        return {
            success: false,
            error: {
                code: 'SAVE_FAILED',
                message: error instanceof Error ? error.message : 'Unknown error occurred'
            }
        };
    }
}

/**
 * Extract performance metrics from training results
 */
export function extractPerformanceMetrics(
    trainResults: any,
    modelType: 'classification' | 'regression' | 'deep-learning'
): Record<string, number> {
    const metrics: Record<string, number> = {};

    if (modelType === 'classification') {
        // Classification metrics
        if (typeof trainResults.accuracy === 'number') metrics.accuracy = trainResults.accuracy;
        if (typeof trainResults.precision === 'number') metrics.precision = trainResults.precision;
        if (typeof trainResults.recall === 'number') metrics.recall = trainResults.recall;
        if (typeof trainResults.f1_score === 'number') metrics.f1_score = trainResults.f1_score;
    } else if (modelType === 'regression') {
        // Regression metrics
        if (typeof trainResults.r2_score === 'number') metrics.r2_score = trainResults.r2_score;
        if (typeof trainResults.mean_squared_error === 'number') metrics.mse = trainResults.mean_squared_error;
        if (typeof trainResults.mean_absolute_error === 'number') metrics.mae = trainResults.mean_absolute_error;
        if (typeof trainResults.root_mean_squared_error === 'number') metrics.rmse = trainResults.root_mean_squared_error;
    } else if (modelType === 'deep-learning') {
        // Deep learning metrics (neural network training metrics)
        if (typeof trainResults.final_loss === 'number') metrics.final_loss = trainResults.final_loss;
        if (typeof trainResults.final_val_loss === 'number') metrics.final_val_loss = trainResults.final_val_loss;
        if (typeof trainResults.final_mae === 'number') metrics.final_mae = trainResults.final_mae;
        if (typeof trainResults.final_val_mae === 'number') metrics.final_val_mae = trainResults.final_val_mae;

        // Also support legacy format if available
        if (typeof trainResults.loss === 'number') metrics.loss = trainResults.loss;
        if (typeof trainResults.val_loss === 'number') metrics.val_loss = trainResults.val_loss;
        if (typeof trainResults.mae === 'number') metrics.mae = trainResults.mae;
        if (typeof trainResults.val_mae === 'number') metrics.val_mae = trainResults.val_mae;
    }

    return metrics;
}

/**
 * Create dataset info from file and columns
 */
export async function createDatasetInfo(
    file: File,
    columns: string[],
    targetColumn: string
): Promise<SaveModelRequest['datasetInfo']> {
    try {
        const text = await file.text();
        const lines = text.split(/\r?\n/).filter(l => l.trim() !== '');
        const rows = Math.max(0, lines.length - 1); // Subtract header row

        return {
            columns,
            target_column: targetColumn,
            data_shape: {
                rows,
                columns: columns.length
            },
            feature_types: {} // Could be enhanced to detect types
        };
    } catch (error) {
        console.error('Error analyzing dataset:', error);
        return {
            columns,
            target_column: targetColumn,
            data_shape: {
                rows: 0,
                columns: columns.length
            }
        };
    }
}