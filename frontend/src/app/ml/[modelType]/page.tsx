'use client';

import React, { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useUser } from '@clerk/nextjs';
import { Rocket, TestTube, Lightbulb, Download, Loader2 } from 'lucide-react';
import { notFound } from 'next/navigation';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useModels, useColumns, useTrainModel, useTestModel, useRecommendModel, useAnalyzeData, useSampleInput } from '@/hooks/use-ml-api';
import type { ApiError, ModelType, TrainResponse } from '@/types/api';
import { saveTrainedModel, extractPerformanceMetrics, createDatasetInfo } from '@/lib/model-storage';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import FileUpload from '@/components/ml/file-upload';
import DataPreview from '@/components/ml/DataPreview';
import EnhancedResults from '@/components/ml/EnhancedResults';
import api from '@/lib/api';
import ModelSelector from '../components/ModelSelector';
import HyperparamsEditor from '../components/HyperparamsEditor';
import { suggestHyperparamsForModel } from '../utils/suggestHyperparams';
import EvalSummary from '../components/EvalSummary';

const validModelTypes: ModelType[] = ['regression', 'classification'];

export default function MlModelTypePage({ params }: { params: Promise<{ modelType: string }> }) {
  const { user } = useUser();
  // `params` is a Promise in newer Next.js versions — unwrap it using React.use().
  // Use a loose cast to avoid TypeScript complaints if React typings don't include `use`.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const resolvedParams = (React as any).use ? (React as any).use(params) : undefined;
  const modelTypeParam = (resolvedParams?.modelType ?? (params as unknown as { modelType: string }).modelType) as ModelType;

  if (!validModelTypes.includes(modelTypeParam)) {
    notFound();
  }

  const [file, setFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [modelType, setModelType] = useState<ModelType>(modelTypeParam);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [testSize, setTestSize] = useState<number>(0.2);
  const [scalingMethod, setScalingMethod] = useState<string>('standard');
  const [hyperparamsPreset, setHyperparamsPreset] = useState<string>('default');
  const [hyperparamsList, setHyperparamsList] = useState<Array<{ key: string; value: string }>>([]);
  const [trainResults, setTrainResults] = useState<TrainResponse | null>(null);
  const [testJson, setTestJson] = useState<string>(JSON.stringify({ feature1: 0, feature2: 0 }, null, 2));
  const [testResults, setTestResults] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<string>('');
  const [featureInputs, setFeatureInputs] = useState<Record<string, string>>({});
  const [useJsonEditor, setUseJsonEditor] = useState<boolean>(false);
  const [downloadModelName, setDownloadModelName] = useState('');
  const [dataAnalysis, setDataAnalysis] = useState<any>(null);
  const [showDataPreview, setShowDataPreview] = useState<boolean>(false);
  // Track models trained in current session
  const [sessionModels, setSessionModels] = useState<Array<{ id: string, name: string, fileName: string }>>([]);

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: models, isLoading: modelsLoading } = useModels(modelType);

  // When models change, pre-select the first available model to ease testing
  useEffect(() => {
    if (!selectedModel && models && models.length > 0) {
      setSelectedModel(models[0]);
    }
  }, [models, selectedModel]);

  // When session models change, pre-select the latest one for testing
  useEffect(() => {
    if (sessionModels.length > 0) {
      const latestModel = sessionModels[sessionModels.length - 1];
      setSelectedModel(latestModel.fileName);
      setDownloadModelName(latestModel.fileName);
    }
  }, [sessionModels]);

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

  // Keep downloadModelName in sync with selectedModel when user hasn't manually changed it
  useEffect(() => {
    if (selectedModel) {
      setDownloadModelName((prev) => (prev ? prev : selectedModel));
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
                // Don't show error toast, just continue without preview
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
    // For regression models, ensure a target column is selected
    if (modelType === 'regression' && !targetColumn) {
      toast({ variant: 'destructive', title: 'Please select a target column for regression' });
      return;
    }
    // Build hyperparams from preset and custom key/value list
    const buildValue = (v: string) => {
      if (v === 'true') return true;
      if (v === 'false') return false;
      if (!isNaN(Number(v)) && v.trim() !== '') return Number(v);
      return v;
    };

    const presetMap: Record<string, Record<string, any>> = {
      default: {},
      fast: { n_estimators: 10, max_depth: 5 },
      accurate: { n_estimators: 200, max_depth: null }
    };

    let hyperparams: Record<string, any> = { ...(presetMap[hyperparamsPreset] || {}) };
    for (const p of hyperparamsList) {
      if (p.key.trim() === '') continue;
      hyperparams[p.key] = buildValue(p.value);
    }

    trainMutation.mutate(
      { file, model: selectedModel, target_column: targetColumn || undefined, test_size: testSize, scaling_method: scalingMethod, hyperparams },
      {
        onSuccess: async (data) => {
          setTrainResults(data);

          // Extract model name for downloads
          let modelFileName = '';
          if (data && (data.model_path || data.model)) {
            const path = data.model_path || data.model;
            try {
              const base = String(path).split('/').pop() || '';
              modelFileName = base.replace(/(_classifier_pipeline|_pipeline)?\.pkl$/i, '');
              setDownloadModelName(modelFileName);
            } catch (e) {
              modelFileName = `${selectedModel}_${Date.now()}`;
            }
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
              // Only save models for regression and classification
              if (modelType === 'regression' || modelType === 'classification') {
                const performanceMetrics = extractPerformanceMetrics(data, modelType);

                const saveResult = await saveTrainedModel(
                  modelFileName, // The file name from training
                  {
                    modelName: `${selectedModel} - ${new Date().toLocaleDateString()}`,
                    modelType: modelType,
                    description: `Trained ${selectedModel} model on ${file.name}`,
                    isPublic: false,
                    tags: [selectedModel, modelType, 'auto-saved'],
                    algorithmName: selectedModel,
                    hyperparameters: hyperparams,
                    datasetInfo,
                    performanceMetrics,
                    trainingTime: 60.0 // Default training time in seconds (will be replaced with actual timing later)
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

          // refresh models list so UI shows newly trained models
          queryClient.invalidateQueries({ queryKey: ['models', modelType] });
          toast({ title: 'Training successful!', description: data.message });
        },
        onError: (error: ApiError) => toast({ variant: 'destructive', title: 'Training failed', description: error.error }),
      }
    );
  };

  // Suggest sensible hyperparameters based on dataset size and feature count
  const suggestHyperparams = async () => {
    if (!file) {
      toast({ variant: 'destructive', title: 'Upload a file first' });
      return;
    }
    try {
      const text = await file.text();
      const lines = text.split(/\r?\n/).filter(l => l.trim() !== '');
      const rows = Math.max(0, lines.length - 1);
      const nFeatures = columns.length || (lines[0] ? lines[0].split(',').length - 1 : 0);
      const suggestions = suggestHyperparamsForModel({ selectedModel: selectedModel || '', rows, nFeatures });
      const list = Object.entries(suggestions).map(([k, v]) => ({ key: k, value: String(v) }));
      setHyperparamsPreset('recommended');
      setHyperparamsList(list);
      toast({ title: 'Recommended hyperparameters applied', description: 'You can tweak these values before training.' });
    } catch (e) {
      toast({ variant: 'destructive', title: 'Could not read file', description: 'Make sure the uploaded file is a valid CSV.' });
    }
  };

  const handleTest = () => {
    if (!selectedModel || !testJson) {
      toast({ variant: 'destructive', title: 'Missing model or test data' });
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

      let new_data: Record<string, any>;
      if (columns.length > 0 && !useJsonEditor) {
        new_data = {};
        for (const [k, v] of Object.entries(featureInputs)) {
          // Ignore empty fields
          new_data[k] = v === '' ? null : parseValue(v);
        }
      } else {
        // Allow users to provide raw JSON (object expected)
        const parsed = JSON.parse(testJson);
        // If user provided an array with a single object, accept it and use the first element
        new_data = Array.isArray(parsed) ? parsed[0] : parsed;
      }

      testMutation.mutate({ model: selectedModel, new_data },
        {
          onSuccess: (data) => {
            setTestResults(data);
            toast({ title: 'Testing successful!' });
          },
          onError: (error: ApiError) => toast({ variant: 'destructive', title: 'Testing failed', description: error.error }),
        })
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
        // if recommendation matches available models, pre-select it for convenience
        if (data.recommended_model) {
          setSelectedModel(data.recommended_model);
        }
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
      const modelToDownload = downloadModelName || selectedModel;
      const response = await api.get(`/ml/download/${type}/${modelToDownload}`, {
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

  const renderMetrics = (results: TrainResponse) => {
    const metrics = Object.entries(results).filter(([key]) => key !== 'message' && key !== 'model_path');
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {metrics.map(([key, value]) => (
          <Card key={key} className="text-center">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-muted-foreground">{key.replace(/_/g, ' ').toUpperCase()}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{typeof value === 'number' ? value.toFixed(4) : value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  // Produce a user-friendly evaluation from metrics returned by backend
  const generateEvaluation = (results: TrainResponse, type: ModelType) => {
    // Default
    let percent = null as number | null;
    let verdict = 'Insufficient metrics to evaluate model quality.';
    let advice = 'Inspect raw metrics for more details.';

    if (type === 'regression') {
      // Prefer r2_score when available (higher is better, 1.0 is perfect)
      const r2 = typeof results.r2_score === 'number' ? results.r2_score : null;
      const mae = typeof results.mean_absolute_error === 'number' ? results.mean_absolute_error : null;
      if (r2 !== null) {
        percent = Math.max(0, Math.min(1, r2)) * 100;
        if (r2 >= 0.9) { verdict = 'Excellent fit'; advice = 'Model explains most of the variance. Consider using for predictions.'; }
        else if (r2 >= 0.75) { verdict = 'Good fit'; advice = 'Model performs well, but test on more data to confirm.'; }
        else if (r2 >= 0.5) { verdict = 'Fair fit'; advice = 'Model has moderate predictive power; try feature engineering or different algorithms.'; }
        else { verdict = 'Poor fit'; advice = 'Consider more data, different features, or alternative models.'; }
      } else if (mae !== null) {
        // Without r2, interpret MAE: lower is better — provide relative guidance (heuristic)
        percent = null;
        if (mae === 0) { verdict = 'Perfect predictions'; advice = 'MAE is 0 — unlikely on real data.'; }
        else if (mae < 1) { verdict = 'Good (low error)'; advice = 'MAE is low; check units and deploy carefully.'; }
        else if (mae < 10) { verdict = 'Acceptable'; advice = 'Error is moderate — consider improvements.'; }
        else { verdict = 'High error'; advice = 'MAE is large relative to expected targets; try different models.'; }
      }
    } else if (type === 'classification') {
      const acc = typeof results.accuracy === 'number' ? results.accuracy : null;
      const f1 = typeof results.f1_score === 'number' ? results.f1_score : null;
      if (acc !== null) {
        percent = Math.max(0, Math.min(1, acc)) * 100;
        if (acc >= 0.9) { verdict = 'Excellent classifier'; advice = 'High accuracy — good candidate for production.'; }
        else if (acc >= 0.8) { verdict = 'Good classifier'; advice = 'Solid performance; validate on holdout data.'; }
        else if (acc >= 0.7) { verdict = 'Fair classifier'; advice = 'Performance is okay; consider more data or tuning.'; }
        else { verdict = 'Poor classifier'; advice = 'Consider feature engineering, balancing classes, or different models.'; }
      } else if (f1 !== null) {
        percent = Math.max(0, Math.min(1, f1)) * 100;
        if (f1 >= 0.9) { verdict = 'Excellent (F1)'; advice = 'Strong precision/recall balance.'; }
        else if (f1 >= 0.8) { verdict = 'Good (F1)'; advice = 'Acceptable balance of precision and recall.'; }
        else if (f1 >= 0.7) { verdict = 'Fair (F1)'; advice = 'Could improve by tuning thresholds or model.'; }
        else { verdict = 'Poor (F1)'; advice = 'Low F1; check class imbalance and feature quality.'; }
      }
    }

    return { percent, verdict, advice };
  };

  const handleModelTypeChange = (type: ModelType) => {
    setModelType(type);
    setSelectedModel('');
    setTestResults(null);
    setTrainResults(null);
    queryClient.invalidateQueries({ queryKey: ['models', type] });
  }

  const capitalizeFirstLetter = (string: string) => {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-headline font-bold">{capitalizeFirstLetter(modelType)} Models</h1>
        <p className="text-muted-foreground mt-2">Train, test, and analyze your {modelType} models with ease.</p>
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
                <CardTitle>Train a New Model</CardTitle>
                <CardDescription>Upload your dataset, choose a model, and start training.</CardDescription>
              </CardHeader>
              <FileUpload onFileChange={handleFileChange} />

              {/* Data Preview */}
              {showDataPreview && dataAnalysis && (
                <div className="mt-6">
                  <DataPreview analysisData={dataAnalysis} />
                </div>
              )}

              {file && (
                <div className="mt-4 space-y-4">
                  <p className="text-sm">File: <span className="font-medium text-primary">{file.name}</span></p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <ModelSelector models={models} selectedModel={selectedModel} setSelectedModel={setSelectedModel} modelsLoading={modelsLoading} />
                    </div>
                    <div>
                      <Label htmlFor="target-select">Target Column</Label>
                      <Select value={targetColumn} onValueChange={setTargetColumn}>
                        <SelectTrigger id="target-select" disabled={columnsMutation.isPending || columns.length === 0}>
                          <SelectValue placeholder={columnsMutation.isPending ? "Loading columns..." : "Select target"} />
                        </SelectTrigger>
                        <SelectContent>
                          {columns.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                        </SelectContent>
                      </Select>
                      {!targetColumn && <p className="text-xs text-destructive mt-1">Please select a target column before training.</p>}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <Label htmlFor="test-size">Test size (0-1)</Label>
                      <Input id="test-size" type="number" step="0.05" min="0.01" max="0.9" value={testSize} onChange={(e) => setTestSize(Number(e.target.value))} />
                    </div>
                    <div>
                      <Label htmlFor="scaling-method">Scaling method</Label>
                      <Select value={scalingMethod} onValueChange={setScalingMethod}>
                        <SelectTrigger id="scaling-method"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="standard">standard</SelectItem>
                          <SelectItem value="minmax">minmax</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <div className="flex items-start gap-3">
                        <div className="flex-1">
                          <HyperparamsEditor preset={hyperparamsPreset} setPreset={setHyperparamsPreset} list={hyperparamsList} setList={setHyperparamsList} />
                        </div>
                        <div className="pt-2">
                          <Button variant="outline" onClick={suggestHyperparams} disabled={!selectedModel}>Suggest</Button>
                        </div>
                      </div>
                    </div>
                    <Button onClick={handleTrain} disabled={trainMutation.isPending || !targetColumn}>
                      {trainMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Train Model
                    </Button>
                  </div>
                </div>
              )}
              {trainResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Training Results</h3>
                  <EnhancedResults results={trainResults} modelType={modelType as 'regression' | 'classification'} />
                  {(() => {
                    const ev = generateEvaluation(trainResults, modelType);
                    return <EvalSummary percent={ev.percent} verdict={ev.verdict} advice={ev.advice} />;
                  })()}
                </div>
              )}
            </TabsContent>
            <TabsContent value="test">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Test Model</CardTitle>
                <CardDescription>Provide a model name and new data to get predictions.</CardDescription>
              </CardHeader>
              <div className="mt-4 space-y-4">
                <div>
                  <Label htmlFor="model-select-test">Model</Label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger id="model-select-test">
                      <SelectValue placeholder={sessionModels.length ? "Select one of your trained models" : "No models trained in this session"} />
                    </SelectTrigger>
                    <SelectContent>
                      {sessionModels.map((model) => <SelectItem key={model.id} value={model.fileName}>{model.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  {sessionModels.length === 0 && (
                    <p className="text-sm text-muted-foreground mt-1">
                      You haven't trained any {modelType} models in this session yet. Go to the "Train Models" tab to get started.
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
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
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
                  ) : (
                    <div className="mt-2">
                      <Label htmlFor="test-data-json" className="text-xs">JSON Object (single object or array with one object)</Label>
                      <Textarea id="test-data-json" value={testJson} onChange={(e) => setTestJson(e.target.value)} rows={10} className="font-code mt-2" />
                      <p className="text-sm text-muted-foreground mt-1">Example: {JSON.stringify({ feature1: 0, feature2: 1 })}</p>
                    </div>
                  )}

                  <Button
                    onClick={handleTest}
                    disabled={testMutation.isPending || !selectedModel || sessionModels.length === 0}
                    className="mt-4"
                  >
                    {testMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Test Model
                  </Button>
                </div>
              </div>
              {testResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold">Test Results</h3>
                  {/* Friendly rendering for regression and classification */}
                  {modelType === 'regression' ? (
                    <Card className="mt-2">
                      <CardHeader>
                        <CardTitle>Predicted Value</CardTitle>
                        <CardDescription>Model: <span className="font-medium">{selectedModel}</span></CardDescription>
                      </CardHeader>
                      <CardContent>
                        {Array.isArray(testResults.predictions) ? (
                          <div className="text-center">
                            <p className="text-4xl font-bold">{typeof testResults.predictions[0] === 'number' ? testResults.predictions[0].toFixed(4) : String(testResults.predictions[0])}</p>
                            {testResults.probabilities && <p className="text-sm text-muted-foreground mt-2">(additional info available)</p>}
                          </div>
                        ) : (
                          <p className="text-lg">{String(testResults.predictions)}</p>
                        )}
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-3">
                      <Card className="mt-2">
                        <CardHeader>
                          <CardTitle>Predicted Class</CardTitle>
                          <CardDescription>Model: <span className="font-medium">{selectedModel}</span></CardDescription>
                        </CardHeader>
                        <CardContent>
                          {Array.isArray(testResults.predictions) ? (
                            <div>
                              <p className="text-2xl font-semibold">{Array.isArray(testResults.predictions) ? (testResults.class_names ? testResults.predictions[0] : testResults.predictions[0]) : String(testResults.predictions)}</p>
                              {testResults.class_names && Array.isArray(testResults.predictions) && (
                                <p className="text-sm text-muted-foreground mt-1">Label: <span className="font-medium">{testResults.class_names[testResults.predictions[0]] ?? testResults.predictions[0]}</span></p>
                              )}
                            </div>
                          ) : (
                            <p className="text-lg">{String(testResults.predictions)}</p>
                          )}
                        </CardContent>
                      </Card>

                      {testResults.probabilities && Array.isArray(testResults.probabilities) && (
                        <Card>
                          <CardHeader>
                            <CardTitle>Probabilities</CardTitle>
                            <CardDescription>Class probabilities for the provided input</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {testResults.probabilities[0].map((p: number, idx: number) => (
                                <div key={idx} className="p-2 border rounded">
                                  <div className="text-sm text-muted-foreground">{testResults.class_names ? testResults.class_names[idx] : `class ${idx}`}</div>
                                  <div className="text-lg font-bold">{(p * 100).toFixed(2)}%</div>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  )}
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
                <CardDescription>Select one of your trained models to download as a .pkl file.</CardDescription>
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
                      You haven't trained any {modelType} models in this session yet. Go to the "Train Models" tab to get started.
                    </p>
                  )}
                </div>
                <div className="flex gap-4">
                  <Button
                    onClick={() => handleDownload(modelType)}
                    disabled={!downloadModelName || sessionModels.length === 0}
                  >
                    Download {capitalizeFirstLetter(modelType)} Model
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
