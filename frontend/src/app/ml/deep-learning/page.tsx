'use client';

import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useUser } from '@clerk/nextjs';
import { Rocket, TestTube, Lightbulb, Download, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useModels, useColumns, useTrainModel, useTestModel, useRecommendModel, useSampleInput } from '@/hooks/use-ml-api';
import type { ApiError, ModelType, TrainResponse } from '@/types/api';
import { saveTrainedModel, extractPerformanceMetrics, createDatasetInfo } from '@/lib/model-storage';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import FileUpload from '@/components/ml/file-upload';
import api from '@/lib/api';
import { Tooltip as RadixTooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '@/components/ui/tooltip';
import { paramDescriptions } from '@/app/ml/utils/tooltips';
import { useAnalyzeData } from '@/hooks/use-ml-api';
import DataPreview from '@/components/ml/DataPreview';
import DeepLearningParamsEditor from '@/components/ml/DeepLearningParamsEditor';
import EnhancedResults from '@/components/ml/EnhancedResults';
import CNNImageUpload from '@/components/ml/CNNImageUpload';
import CNNImageTester from '@/components/ml/CNNImageTester';

export default function MlModelTypePage() {
  const { user } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [modelType, setModelType] = useState<ModelType>('deep-learning');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [trainResults, setTrainResults] = useState<TrainResponse | null>(null);
  const [testJson, setTestJson] = useState<string>(JSON.stringify({ feature1: 0, feature2: 0 }, null, 2));
  const [testResults, setTestResults] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<string>('');
  const [epochs, setEpochs] = useState<number>(10);
  const [batchSize, setBatchSize] = useState<number>(32);
  const [configJson, setConfigJson] = useState<string>('');
  const [preset, setPreset] = useState<string>('standard');
  const [downloadModelName, setDownloadModelName] = useState('');
  const [dataAnalysis, setDataAnalysis] = useState<any>(null);
  const [showDataPreview, setShowDataPreview] = useState<boolean>(false);
  const [featureInputs, setFeatureInputs] = useState<Record<string, string>>({});
  const [useJsonEditor, setUseJsonEditor] = useState<boolean>(false);
  // Track models trained in current session
  const [sessionModels, setSessionModels] = useState<Array<{ id: string, name: string, fileName: string }>>([]);

  // CNN Image specific state
  const [isCNNImageMode, setIsCNNImageMode] = useState<boolean>(false);
  const [cnnImageFile, setCnnImageFile] = useState<File | null>(null);
  const [cnnValidation, setCnnValidation] = useState<any>(null);
  const [cnnTrainResults, setCnnTrainResults] = useState<any>(null);

  // Loading states for training
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [isCnnTraining, setIsCnnTraining] = useState<boolean>(false);

  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Deep models are provided by backend at /ml/deep/models
  const [models, setModels] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState<boolean>(false);

  const fetchDeepModels = async () => {
    try {
      setModelsLoading(true);
      const res = await api.get('/ml/deep/models');
      // backend returns { models: [...] }
      const data = res.data;
      if (data && data.models) setModels(data.models);
      else if (Array.isArray(res.data)) setModels(res.data);
    } catch (e) {
      console.error('Error fetching deep models', e);
    } finally {
      setModelsLoading(false);
    }
  };

  // fetch on mount
  useEffect(() => { fetchDeepModels(); }, []);

  // Initialize feature inputs when columns are available
  useEffect(() => {
    if (columns && columns.length > 0) {
      const init: Record<string, string> = {};
      columns.forEach((c) => {
        // Skip target column if set to avoid asking for it during test
        if (c === targetColumn) return;
        init[c] = '';
      });
      setFeatureInputs(init);
    }
  }, [columns, targetColumn]);

  // Re-analyze data when target column changes
  useEffect(() => {
    if (file && targetColumn && showDataPreview) {
      analyzeDataMutation.mutate(
        { file, target_column: targetColumn },
        {
          onSuccess: (analysisData) => setDataAnalysis(analysisData),
          onError: (error: ApiError) => console.warn('Re-analysis failed:', error)
        }
      );
    }
  }, [targetColumn, file, showDataPreview]);

  // Set default config on mount
  useEffect(() => {
    if (!configJson) {
      const defaultConfig = {
        hidden_layers: [128, 64, 32],
        dropout: 0.3,
        learning_rate: 0.001,
        optimizer: 'adam'
      };
      setConfigJson(JSON.stringify(defaultConfig, null, 2));
    }
  }, []);

  // Update CNN mode based on selected model
  useEffect(() => {
    setIsCNNImageMode(selectedModel === 'cnn');
    // Reset CNN-specific state when switching models
    if (selectedModel !== 'cnn') {
      setCnnImageFile(null);
      setCnnValidation(null);
      setCnnTrainResults(null);
    }
  }, [selectedModel]);

  const columnsMutation = useColumns();
  const trainMutation = useTrainModel(modelType);
  const testMutation = useTestModel(modelType);
  const recommendMutation = useRecommendModel();
  const analyzeDataMutation = useAnalyzeData();
  const sampleInputMutation = useSampleInput();

  const handleFileChange = (acceptedFiles: File[]) => {
    const newFile = acceptedFiles[0];
    if (newFile) {
      setFile(newFile);
      setColumns([]);
      setTargetColumn('');
      setTrainResults(null);
      setRecommendation('');
      setDataAnalysis(null);
      setShowDataPreview(false);

      // Get columns first
      columnsMutation.mutate(newFile, {
        onSuccess: (data) => {
          setColumns(data.columns);
          // Automatically analyze data for preview
          analyzeDataMutation.mutate(
            { file: newFile },
            {
              onSuccess: (analysisData) => {
                setDataAnalysis(analysisData);
                setShowDataPreview(true);
              },
              onError: (error: ApiError) => {
                console.warn('Data analysis failed:', error);
              }
            }
          );
        },
        onError: (error: ApiError) => toast({ variant: 'destructive', title: 'Error getting columns', description: error.error }),
      });
    }
  };

  const handleTrain = () => {
    if (!file || !selectedModel) {
      toast({ variant: 'destructive', title: 'Missing file or model' });
      return;
    }

    setIsTraining(true);

    // Build FormData as backend expects file + form fields (epochs, batch_size, config)
    const form = new FormData();
    form.append('file', file);
    form.append('model', selectedModel);
    if (targetColumn) form.append('target_column', targetColumn);
    form.append('epochs', String(epochs));
    form.append('batch_size', String(batchSize));
    if (configJson) form.append('config', configJson);

    // Use backend deep train endpoint
    api.post(`/ml/deep/train`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then(async (res) => {
        setTrainResults(res.data);

        // Extract model name for downloads and session tracking
        let modelFileName = '';
        if (res.data && (res.data.model_path || res.data.model)) {
          const path = res.data.model_path || res.data.model;
          try {
            const base = String(path).split('/').pop() || '';
            // For deep learning models, use the full filename without path
            // Remove file extension but keep the base name
            modelFileName = base.replace(/\.(keras|pkl)$/i, '');
            setDownloadModelName(modelFileName);
          } catch (e) {
            modelFileName = `${selectedModel}_${Date.now()}`;
          }
        } else {
          // If no model path returned, generate a fallback name
          modelFileName = `${selectedModel}_${Date.now()}`;
        }

        // Add the newly trained model to session models for testing and downloading
        const newSessionModel = {
          id: `${selectedModel}_${Date.now()}`, // Unique ID for React keys
          name: `${selectedModel} - ${new Date().toLocaleDateString()}`,
          fileName: modelFileName
        };
        setSessionModels(prev => [...prev, newSessionModel]);

        // Save model to database and Cloudinary (optional - don't fail if this doesn't work)
        if (file && targetColumn && modelFileName) {
          try {
            console.log('Attempting to save model to cloud:', modelFileName);
            toast({ title: 'Training completed! Saving model...', description: 'Your model is being saved to the cloud.' });

            const datasetInfo = await createDatasetInfo(file, columns, targetColumn);
            // Create performance metrics for deep learning models
            const performanceMetrics = extractPerformanceMetrics(res.data, 'deep-learning'); // Deep learning metrics

            const saveResult = await saveTrainedModel(
              modelFileName, // The file name from training
              {
                modelName: `${selectedModel} - ${new Date().toLocaleDateString()}`,
                modelType: 'deep-learning', // Deep learning models
                description: `Trained ${selectedModel} deep learning model on ${file.name}`,
                isPublic: false,
                tags: [selectedModel, 'deep-learning', 'auto-saved'],
                algorithmName: selectedModel,
                hyperparameters: { epochs, batchSize, config: configJson },
                datasetInfo,
                performanceMetrics,
                trainingTime: 120.0 // Default training time in seconds for deep learning
              },
              user?.id // Pass Clerk user ID for authentication
            );

            if (saveResult.success) {
              toast({
                title: 'Model saved successfully!',
                description: 'Your trained model is now available in your dashboard and can be downloaded anytime.'
              });
            } else {
              console.warn('Model save failed:', saveResult.error);
              toast({
                title: 'Model trained successfully!',
                description: 'Model training completed but cloud save failed. You can still test and download the model.'
              });
            }
          } catch (saveError) {
            console.error('Error saving model:', saveError);
            toast({
              title: 'Model trained successfully!',
              description: 'Model training completed but cloud save failed. You can still test and download the model.'
            });
          }
        } else {
          console.warn('Skipping cloud save - missing required data:', { file: !!file, targetColumn, modelFileName });
        }

        toast({ title: 'Training successful!', description: res.data.message || 'Deep model trained' });
        fetchDeepModels();
      })
      .catch((err) => {
        const message = err?.response?.data?.error || err.message || 'Training failed';
        toast({ variant: 'destructive', title: 'Training failed', description: message });
      })
      .finally(() => {
        setIsTraining(false);
      });
  };

  const handleTest = () => {
    if (!downloadModelName) {
      toast({ variant: 'destructive', title: 'Please select a trained model to test' });
      return;
    }
    try {
      // If using the form editor (columns present and not using JSON), build the object from featureInputs
      const parseValue = (v: string) => {
        if (v === 'true') return true;
        if (v === 'false') return false;
        if (!isNaN(Number(v)) && v.trim() !== '') return Number(v);
        return v;
      };

      let input: Record<string, any>;
      if (columns.length > 0 && !useJsonEditor) {
        input = {};
        for (const [k, v] of Object.entries(featureInputs)) {
          // Ignore empty fields
          input[k] = v === '' ? null : parseValue(v);
        }
      } else {
        // Allow users to provide raw JSON (object expected)
        const parsed = JSON.parse(testJson);
        // If user provided an array with a single object, accept it and use the first element
        input = Array.isArray(parsed) ? parsed[0] : parsed;
      }

      // backend deep test endpoint
      api.post(`/ml/deep/test`, { model: downloadModelName, input })
        .then((res) => {
          setTestResults(res.data);
          toast({ title: 'Testing successful!' });
        })
        .catch((err) => {
          const message = err?.response?.data?.error || err.message || 'Testing failed';
          toast({ variant: 'destructive', title: 'Testing failed', description: message });
        });
    } catch (e) {
      toast({ variant: 'destructive', title: 'Invalid JSON', description: 'Please check your test data format.' });
    }
  };

  const handleRecommend = () => {
    if (!file) {
      toast({ variant: 'destructive', title: 'Please upload a file first' });
      return;
    }
    recommendMutation.mutate(file, {
      onSuccess: (data) => {
        setRecommendation(data.recommended_model);
        toast({ title: 'Recommendation received!' });
      },
      onError: (error: ApiError) => toast({ variant: 'destructive', title: 'Recommendation failed', description: error.error }),
    });
  };

  const handleDownload = async (type: ModelType) => {
    if (!downloadModelName) {
      toast({ variant: 'destructive', title: 'Please enter a model name' });
      return;
    }
    try {
      const response = await api.get(`/ml/download/${type}/${downloadModelName}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${downloadModelName}.pkl`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      toast({ title: `Downloading ${downloadModelName}` });
    } catch (err) {
      toast({ variant: 'destructive', title: 'Download failed', description: 'Model not found or server error.' });
    }
  }



  const handleModelTypeChange = (type: ModelType) => {
    setModelType(type);
    setSelectedModel('');
    setTestResults(null);
    setTrainResults(null);
    queryClient.invalidateQueries({ queryKey: ['models', type] });
  }

  const capitalizeFirstLetter = (string: string) => {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
  };

  const suggestParameters = () => {
    if (!dataAnalysis?.data_info) return;

    const numSamples = dataAnalysis.data_info.n_rows;
    const numFeatures = dataAnalysis.data_info.n_cols;

    // Suggest parameters based on dataset size
    let suggestedEpochs = 10;
    let suggestedBatchSize = 32;
    let suggestedPreset = 'standard';

    if (numSamples < 500) {
      suggestedEpochs = 50; // More epochs for small datasets
      suggestedBatchSize = 16; // Smaller batch size
      suggestedPreset = 'simple';
    } else if (numSamples < 2000) {
      suggestedEpochs = 25;
      suggestedBatchSize = 32;
      suggestedPreset = 'simple';
    } else if (numSamples < 10000) {
      suggestedEpochs = 15;
      suggestedBatchSize = 64;
      suggestedPreset = 'standard';
    } else {
      suggestedEpochs = 10;
      suggestedBatchSize = 128;
      suggestedPreset = 'deep';
    }

    setEpochs(suggestedEpochs);
    setBatchSize(suggestedBatchSize);
    setPreset(suggestedPreset);

    // Apply the corresponding preset config
    const presetConfigs = {
      simple: {
        hidden_layers: [64, 32],
        dropout: 0.2,
        learning_rate: 0.001,
        optimizer: 'adam'
      },
      standard: {
        hidden_layers: [128, 64, 32],
        dropout: 0.3,
        learning_rate: 0.001,
        optimizer: 'adam'
      },
      deep: {
        hidden_layers: [256, 128, 64, 32],
        dropout: 0.4,
        learning_rate: 0.0005,
        optimizer: 'adam'
      }
    };

    setConfigJson(JSON.stringify(presetConfigs[suggestedPreset as keyof typeof presetConfigs], null, 2));

    toast({
      title: 'Parameters suggested!',
      description: `${suggestedPreset} network recommended for ${numSamples} samples, ${numFeatures} features`
    });
  };

  const handleGenerateSampleInput = () => {
    if (!file) {
      toast({ variant: 'destructive', title: 'Please upload a training file first' });
      return;
    }

    sampleInputMutation.mutate({ file, target_column: targetColumn }, {
      onSuccess: (data) => {
        if (data.sample_input) {
          if (useJsonEditor) {
            setTestJson(JSON.stringify(data.sample_input, null, 2));
          } else {
            // Fill form inputs with sample data
            const sampleData = data.sample_input;
            const newInputs: Record<string, string> = {};
            Object.entries(featureInputs).forEach(([key]) => {
              newInputs[key] = sampleData[key] !== undefined ? String(sampleData[key]) : '';
            });
            setFeatureInputs(newInputs);
          }
          toast({ title: 'Sample input generated!', description: 'Based on your training data statistics' });
        }
      },
      onError: (error: ApiError) => {
        toast({ variant: 'destructive', title: 'Failed to generate sample', description: error.error });
      }
    });
  };

  // CNN Image handlers
  const handleCNNImageValidated = (file: File, validation: any) => {
    setCnnImageFile(file);
    setCnnValidation(validation);
    setTrainResults(null);
    setCnnTrainResults(null);
  };

  const handleCNNImageRemoved = () => {
    setCnnImageFile(null);
    setCnnValidation(null);
    setCnnTrainResults(null);
  };

  const handleCNNImageTrain = async () => {
    if (!cnnImageFile || !selectedModel) {
      toast({ variant: 'destructive', title: 'Missing file or model' });
      return;
    }

    setIsCnnTraining(true);

    const formData = new FormData();
    formData.append('file', cnnImageFile);
    formData.append('epochs', String(epochs));
    formData.append('batch_size', String(batchSize));
    formData.append('target_size', '224,224'); // Default CNN input size
    formData.append('augment', 'true');
    formData.append('validation_split', '0.2');

    // Add configuration if provided
    if (configJson) {
      formData.append('config', configJson);
    }

    try {
      const response = await api.post('/ml/train/cnn-images', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('CNN Training Response:', response.data);

      // Structure the response data to match what EnhancedResults expects
      const structuredResults = {
        ...response.data,
        // Extract metrics from nested structure for EnhancedResults
        final_accuracy: response.data.training_summary?.final_accuracy || response.data.metadata?.training_history?.final_accuracy,
        final_val_accuracy: response.data.training_summary?.final_val_accuracy || response.data.metadata?.training_history?.final_val_accuracy,
        final_loss: response.data.training_summary?.final_loss || response.data.metadata?.training_history?.final_loss,
        final_val_loss: response.data.training_summary?.final_val_loss || response.data.metadata?.training_history?.final_val_loss,
        epochs_trained: response.data.training_summary?.total_epochs || response.data.metadata?.training_history?.epochs_trained || epochs,
        num_classes: response.data.training_summary?.num_classes,
        total_samples: response.data.training_summary?.total_images,
        classes: response.data.training_summary?.class_names
      };

      setCnnTrainResults(structuredResults);

      // Extract model name for downloads and session tracking
      let modelFileName = '';
      if (response.data && (response.data.model_path || response.data.model_name || response.data.model)) {
        const path = response.data.model_path || response.data.model_name || response.data.model;
        try {
          const base = String(path).split('/').pop() || '';
          // For CNN models, use the full filename without path
          // Remove file extension but keep the base name
          modelFileName = base.replace(/\.(keras|pkl|h5)$/i, '');
          setDownloadModelName(modelFileName);
        } catch (e) {
          modelFileName = `cnn_image_${Date.now()}`;
        }
      } else {
        // If no model path returned, generate a fallback name
        modelFileName = `cnn_image_${Date.now()}`;
      }

      // Add to session models for testing
      const newSessionModel = {
        id: `cnn_${Date.now()}`,
        name: `CNN Image - ${new Date().toLocaleDateString()}`,
        fileName: modelFileName
      };
      setSessionModels(prev => [...prev, newSessionModel]);

      // Save CNN model to database and Cloudinary (optional - don't fail if this doesn't work)
      if (cnnImageFile && cnnValidation && modelFileName) {
        try {
          console.log('Attempting to save CNN model to cloud:', modelFileName);
          toast({ title: 'CNN Training completed! Saving model...', description: 'Your CNN model is being saved to the cloud.' });

          // Create dataset info for CNN (image data) - matching SaveModelRequest interface
          const datasetInfo = {
            columns: ['image', 'class'], // Images and their class labels
            target_column: 'class', // The target is the class/category
            data_shape: {
              rows: cnnValidation.total_images,
              columns: 2 // image and class
            },
            feature_types: {
              'image': 'image',
              'class': 'categorical'
            }
          };

          // Extract performance metrics from CNN training response
          // The backend returns nested structure: training_summary and metadata.training_history
          const trainingSummary = response.data.training_summary || {};
          const trainingHistory = response.data.metadata?.training_history || {};

          const performanceMetrics = {
            accuracy: trainingSummary.final_accuracy || trainingHistory.final_accuracy || null,
            val_accuracy: trainingSummary.final_val_accuracy || trainingHistory.final_val_accuracy || null,
            loss: trainingSummary.final_loss || trainingHistory.final_loss || null,
            val_loss: trainingSummary.final_val_loss || trainingHistory.final_val_loss || null,
            epochs_trained: trainingSummary.total_epochs || trainingHistory.epochs_trained || epochs,
            total_params: response.data.metadata?.training_params?.total_images || null,
            training_time: 120.0, // Default since backend doesn't provide this
            num_classes: trainingSummary.num_classes || null,
            total_images: trainingSummary.total_images || null
          };

          const saveResult = await saveTrainedModel(
            modelFileName, // The file name from training
            {
              modelName: `CNN Image Model - ${new Date().toLocaleDateString()}`,
              modelType: 'deep-learning', // CNN is a type of deep learning
              description: `Trained CNN image classification model on ${cnnImageFile.name} with ${cnnValidation.classes.length} classes`,
              isPublic: false,
              tags: ['cnn', 'image-classification', 'deep-learning', 'auto-saved'],
              algorithmName: 'cnn',
              hyperparameters: { epochs, batchSize, config: configJson, classes: cnnValidation.classes },
              datasetInfo,
              performanceMetrics,
              trainingTime: performanceMetrics.training_time
            },
            user?.id // Pass Clerk user ID for authentication
          );

          if (saveResult.success) {
            toast({
              title: 'CNN Model saved successfully!',
              description: 'Your trained CNN model is now available in your dashboard and can be downloaded anytime.'
            });
          } else {
            console.warn('CNN Model save failed:', saveResult.error);
            toast({
              title: 'CNN Model trained successfully!',
              description: 'CNN training completed but cloud save failed. You can still test and download the model.'
            });
          }
        } catch (saveError) {
          console.error('Error saving CNN model:', saveError);
          toast({
            title: 'CNN Model trained successfully!',
            description: 'CNN training completed but cloud save failed. You can still test and download the model.'
          });
        }
      }

      toast({
        title: 'CNN training successful!',
        description: `Model trained on ${cnnValidation.total_images} images from ${cnnValidation.classes.length} classes.`
      });

    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'CNN training failed';
      toast({
        variant: 'destructive',
        title: 'CNN training failed',
        description: errorMessage,
      });
    } finally {
      setIsCnnTraining(false);
    }
  }; return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-headline font-bold">Deep Learning Models</h1>
        <p className="text-muted-foreground mt-2">Train, test, and analyze your deep learning models.</p>
      </div>
      <Tabs defaultValue="train" className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:grid-cols-4">
          <TabsTrigger value="train"><Rocket className="mr-2 h-4 w-4" />Train Models</TabsTrigger>
          <TabsTrigger value="test"><TestTube className="mr-2 h-4 w-4" />Test Models</TabsTrigger>
          <TabsTrigger value="recommend"><Lightbulb className="mr-2 h-4 w-4" />Recommend</TabsTrigger>
          <TabsTrigger value="download"><Download className="mr-2 h-4 w-4" />Download</TabsTrigger>
        </TabsList>
        <Card className="mt-4">
          <CardContent className="pt-6">
            <TabsContent value="train">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Train a Deep Learning Model</CardTitle>
                <CardDescription>
                  {!isCNNImageMode
                    ? "Upload your dataset and configure neural network parameters. Deep learning works best with larger datasets (1000+ samples)."
                    : "Upload a ZIP file containing your images organized by class folders for CNN training."
                  }
                </CardDescription>
              </CardHeader>

              {/* Model Selection - Show First */}
              <div className="mb-6">
                <Label htmlFor="model-select-main">Select Model Type</Label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger id="model-select-main">
                    <SelectValue placeholder={modelsLoading ? "Loading..." : "Select a model type"} />
                  </SelectTrigger>
                  <SelectContent>
                    {models?.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                  </SelectContent>
                </Select>
                {!selectedModel && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Choose a model type first. Select "cnn" for image classification with ZIP files.
                  </p>
                )}
              </div>

              {/* File Upload - Changes based on model type */}
              {selectedModel && (
                <>
                  {!isCNNImageMode ? (
                    <FileUpload onFileChange={handleFileChange} />
                  ) : (
                    <CNNImageUpload
                      onFileValidated={handleCNNImageValidated}
                      onFileRemoved={handleCNNImageRemoved}
                    />
                  )}
                </>
              )}

              {/* Data Preview */}
              {showDataPreview && dataAnalysis && (
                <div className="mt-6">
                  <DataPreview analysisData={dataAnalysis} />
                </div>
              )}

              {((file && !isCNNImageMode) || (cnnImageFile && isCNNImageMode)) && (
                <div className="mt-4 space-y-4">
                  <p className="text-sm">File: <span className="font-medium text-primary">
                    {isCNNImageMode ? cnnImageFile?.name : file?.name}
                  </span></p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {!isCNNImageMode && (
                      <div>
                        <Label htmlFor="target-select">Target Column</Label>
                        <Select value={targetColumn} onValueChange={setTargetColumn} disabled={columnsMutation.isPending || columns.length === 0}>
                          <SelectTrigger id="target-select" disabled={columnsMutation.isPending || columns.length === 0}>
                            <SelectValue placeholder={columnsMutation.isPending ? "Loading columns..." : "Select target"} />
                          </SelectTrigger>
                          <SelectContent>
                            {columns.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                    {isCNNImageMode && cnnValidation && (
                      <div>
                        <Label>Classes Detected</Label>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {cnnValidation.classes.map((className: string) => (
                            <Badge key={className} variant="outline">
                              {className} ({cnnValidation.class_counts[className]})
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-4">
                    <DeepLearningParamsEditor
                      epochs={epochs}
                      setEpochs={setEpochs}
                      batchSize={batchSize}
                      setBatchSize={setBatchSize}
                      configJson={configJson}
                      setConfigJson={setConfigJson}
                      preset={preset}
                      setPreset={setPreset}
                    />
                  </div>

                  {dataAnalysis && (
                    <div className="mt-4">
                      <Button
                        variant="outline"
                        onClick={suggestParameters}
                        className="w-full md:w-auto"
                      >
                        <Lightbulb className="mr-2 h-4 w-4" />
                        Suggest Parameters
                      </Button>
                      <p className="text-sm text-muted-foreground mt-1">
                        Get parameter suggestions based on your dataset size and characteristics
                      </p>
                    </div>
                  )}

                  <div className="mt-4 space-y-2">
                    <Button
                      onClick={isCNNImageMode ? handleCNNImageTrain : handleTrain}
                      disabled={
                        (isCNNImageMode ? isCnnTraining : isTraining) ||
                        !selectedModel ||
                        (isCNNImageMode ? !cnnImageFile || !cnnValidation?.valid : !targetColumn)
                      }
                      className="w-full md:w-auto"
                    >
                      {(isCNNImageMode ? isCnnTraining : isTraining) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Train {isCNNImageMode ? 'CNN Image' : 'Deep Learning'} Model
                    </Button>
                    {(!selectedModel || (isCNNImageMode ? (!cnnImageFile || !cnnValidation?.valid) : !targetColumn)) && (
                      <p className="text-sm text-muted-foreground">
                        {isCNNImageMode
                          ? "Please select a model and upload a valid ZIP file before training."
                          : "Please select a model and target column before training."
                        }
                      </p>
                    )}
                  </div>
                </div>
              )}
              {(trainResults || cnnTrainResults) && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {isCNNImageMode ? 'CNN Image Training Results' : 'Training Results'}
                  </h3>
                  <EnhancedResults
                    results={isCNNImageMode ? cnnTrainResults : trainResults}
                    modelType="deep-learning"
                  />
                </div>
              )}
            </TabsContent>
            <TabsContent value="test">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Test an Existing Model</CardTitle>
                <CardDescription>
                  {selectedModel === 'cnn'
                    ? "Upload a single image to test with your trained CNN model."
                    : "Provide a model name and new data to get predictions."
                  }
                </CardDescription>
              </CardHeader>

              {/* Show model selection reminder if no model selected */}
              {!selectedModel && (
                <div className="p-4 border-2 border-dashed border-muted-foreground/25 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">
                    Please select a model type in the Train tab first to begin testing.
                  </p>
                </div>
              )}

              {selectedModel === 'cnn' ? (
                <CNNImageTester />
              ) : selectedModel ? (
                <div className="mt-4 space-y-4">
                  {file && (
                    <div className="p-3 bg-muted/50 rounded-lg">
                      <p className="text-sm">
                        <span className="font-medium">Training file loaded:</span> {file.name}
                        {targetColumn && (
                          <span className="ml-2 text-muted-foreground">
                            (Target: <span className="font-medium">{targetColumn}</span>)
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Feature fields are automatically generated from your training data
                      </p>
                    </div>
                  )}
                  <div>
                    <Label htmlFor="model-select-test">Trained Model</Label>
                    <Select value={downloadModelName} onValueChange={setDownloadModelName}>
                      <SelectTrigger id="model-select-test">
                        <SelectValue placeholder={sessionModels.length ? "Select one of your trained models" : "No models trained in this session"} />
                      </SelectTrigger>
                      <SelectContent>
                        {sessionModels.map((model) => <SelectItem key={model.id} value={model.fileName}>{model.name}</SelectItem>)}
                      </SelectContent>
                    </Select>
                    {sessionModels.length === 0 && (
                      <p className="text-sm text-muted-foreground mt-1">
                        You haven't trained any deep learning models in this session yet. Go to the "Train Models" tab to get started.
                      </p>
                    )}
                  </div>
                  <div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="test-data">New Data</Label>
                      <div className="flex items-center gap-2">
                        <input id="use-json" type="checkbox" checked={useJsonEditor} onChange={(e) => setUseJsonEditor(e.target.checked)} />
                        <Label htmlFor="use-json" className="text-sm">Use raw JSON</Label>
                      </div>
                    </div>

                    {columns.length > 0 && !useJsonEditor ? (
                      <div className="space-y-3 mt-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm font-medium">Feature Values</Label>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleGenerateSampleInput}
                            disabled={sampleInputMutation.isPending || !file}
                          >
                            {sampleInputMutation.isPending && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
                            Generate Sample
                          </Button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {Object.keys(featureInputs).length === 0 && (
                            <p className="text-sm text-muted-foreground">No feature inputs detected. Upload a CSV and select target to generate fields.</p>
                          )}
                          {Object.entries(featureInputs).map(([k, v]) => (
                            <div key={k}>
                              <Label className="text-xs">{k}</Label>
                              <Input value={v} onChange={(e) => setFeatureInputs(prev => ({ ...prev, [k]: e.target.value }))} placeholder={`Enter value for ${k}`} />
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-2 space-y-2">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="test-data-json" className="text-xs">JSON Object (single object or array with one object)</Label>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleGenerateSampleInput}
                            disabled={sampleInputMutation.isPending || !file}
                          >
                            {sampleInputMutation.isPending && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
                            Generate Sample
                          </Button>
                        </div>
                        <Textarea
                          id="test-data-json"
                          value={testJson}
                          onChange={(e) => setTestJson(e.target.value)}
                          rows={10}
                          className="font-mono text-sm"
                          placeholder="Enter your test data as JSON object"
                        />
                        <p className="text-sm text-muted-foreground">
                          Example: {JSON.stringify({ feature1: 0, feature2: 1 })}
                        </p>
                      </div>
                    )}

                    <Button
                      onClick={handleTest}
                      disabled={testMutation.isPending || !downloadModelName || sessionModels.length === 0}
                      className="mt-4"
                    >
                      {testMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Test Model
                    </Button>
                  </div>
                </div>
              ) : null}
              {testResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold">Test Results</h3>
                  <Card className="mt-2">
                    <CardHeader>
                      <CardTitle>Deep Learning Prediction</CardTitle>
                      <CardDescription>Model: <span className="font-medium">{downloadModelName}</span></CardDescription>
                    </CardHeader>
                    <CardContent>
                      {Array.isArray(testResults.predictions) ? (
                        <div className="text-center">
                          <div className="text-4xl font-bold mb-2">
                            {typeof testResults.predictions[0] === 'number'
                              ? testResults.predictions[0].toFixed(6)
                              : String(testResults.predictions[0])
                            }
                          </div>
                          {testResults.confidence && (
                            <div className="text-sm text-muted-foreground">
                              Confidence: <span className="font-medium">{(testResults.confidence * 100).toFixed(2)}%</span>
                            </div>
                          )}
                        </div>
                      ) : testResults.predictions !== undefined ? (
                        <div className="text-center">
                          <div className="text-4xl font-bold mb-2">
                            {typeof testResults.predictions === 'number'
                              ? testResults.predictions.toFixed(6)
                              : String(testResults.predictions)
                            }
                          </div>
                        </div>
                      ) : (
                        <div className="text-center text-muted-foreground">
                          No prediction available
                        </div>
                      )}

                      {/* Show additional information if available */}
                      {testResults.probabilities && (
                        <div className="mt-4 pt-4 border-t">
                          <h4 className="text-sm font-medium mb-2">Class Probabilities</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {testResults.probabilities.map((prob: number, idx: number) => (
                              <div key={idx} className="p-2 border rounded text-center">
                                <div className="text-sm text-muted-foreground">Class {idx}</div>
                                <div className="text-lg font-bold">{(prob * 100).toFixed(2)}%</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Raw data for debugging */}
                      <details className="mt-4">
                        <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                          Show raw results
                        </summary>
                        <pre className="text-xs font-mono bg-muted p-3 rounded-md mt-2 overflow-x-auto">
                          {JSON.stringify(testResults, null, 2)}
                        </pre>
                      </details>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>
            <TabsContent value="recommend">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Get a Model Recommendation</CardTitle>
                <CardDescription>Upload your dataset to get a recommendation for the best model to use.</CardDescription>
              </CardHeader>
              <FileUpload onFileChange={handleFileChange} />
              <Button onClick={handleRecommend} disabled={recommendMutation.isPending || !file} className="mt-4">
                {recommendMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Get Recommendation
              </Button>
              {recommendation && (
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle>Recommended Model</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-accent">{recommendation}</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
            <TabsContent value="download">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Download a Trained Model</CardTitle>
                <CardDescription>Enter the name of a trained model to download it as a .pkl file.</CardDescription>
              </CardHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="model-select-download">Your Trained Models</Label>
                  <Select value={downloadModelName} onValueChange={setDownloadModelName}>
                    <SelectTrigger id="model-select-download">
                      <SelectValue placeholder={sessionModels.length ? "Select a model to download" : "No models trained in this session"} />
                    </SelectTrigger>
                    <SelectContent>
                      {sessionModels.map((model) => <SelectItem key={model.id} value={model.fileName}>{model.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  {sessionModels.length === 0 && (
                    <p className="text-sm text-muted-foreground mt-1">
                      You haven't trained any deep learning models in this session yet. Go to the "Train Models" tab to get started.
                    </p>
                  )}
                </div>
                <div className="flex gap-4">
                  <Button
                    onClick={() => handleDownload(modelType)}
                    disabled={!downloadModelName || sessionModels.length === 0}
                  >
                    Download Deep Learning Model
                  </Button>
                </div>
              </div>
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
}
