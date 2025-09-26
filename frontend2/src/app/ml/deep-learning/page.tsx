'use client';

import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Rocket, TestTube, Lightbulb, Download, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useModels, useColumns, useTrainModel, useTestModel, useRecommendModel, useSampleInput } from '@/hooks/use-ml-api';
import type { ApiError, ModelType, TrainResponse } from '@/types/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import FileUpload from '@/components/ml/file-upload';
import api from '@/lib/api';
import { Tooltip as RadixTooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '@/components/ui/tooltip';
import { paramDescriptions } from '@/app/ml/utils/tooltips';
import { useAnalyzeData } from '@/hooks/use-ml-api';
import DataPreview from '@/components/ml/DataPreview';
import DeepLearningParamsEditor from '@/components/ml/DeepLearningParamsEditor';
import EnhancedResults from '@/components/ml/EnhancedResults';

export default function MlModelTypePage() {
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
      .then((res) => {
        setTrainResults(res.data);
        toast({ title: 'Training successful!', description: res.data.message || 'Deep model trained' });
        fetchDeepModels();
      })
      .catch((err) => {
        const message = err?.response?.data?.error || err.message || 'Training failed';
        toast({ variant: 'destructive', title: 'Training failed', description: message });
      });
  };

  const handleTest = () => {
    if (!selectedModel) {
      toast({ variant: 'destructive', title: 'Missing model' });
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
      api.post(`/ml/deep/test`, { model: selectedModel, input })
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
                  Upload your dataset and configure neural network parameters. Deep learning works best with larger datasets (1000+ samples).
                </CardDescription>
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
                      <Label htmlFor="model-select">Model</Label>
                      <Select value={selectedModel} onValueChange={setSelectedModel}>
                        <SelectTrigger id="model-select">
                          <SelectValue placeholder={modelsLoading ? "Loading..." : "Select a model"} />
                        </SelectTrigger>
                        <SelectContent>
                          {models?.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
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
                      onClick={handleTrain}
                      disabled={trainMutation.isPending || !selectedModel || !targetColumn}
                      className="w-full md:w-auto"
                    >
                      {trainMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Train Deep Learning Model
                    </Button>
                    {(!selectedModel || !targetColumn) && (
                      <p className="text-sm text-muted-foreground">
                        Please select a model and target column before training.
                      </p>
                    )}
                  </div>
                </div>
              )}
              {trainResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Training Results</h3>
                  <EnhancedResults results={trainResults} modelType="deep-learning" />
                </div>
              )}
            </TabsContent>
            <TabsContent value="test">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Test an Existing Model</CardTitle>
                <CardDescription>Provide a model name and new data to get predictions.</CardDescription>
              </CardHeader>
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
                  <Label htmlFor="model-select-test">Model</Label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger id="model-select-test">
                      <SelectValue placeholder={modelsLoading ? "Loading..." : "Select a model to test"} />
                    </SelectTrigger>
                    <SelectContent>
                      {models?.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                    </SelectContent>
                  </Select>
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

                  <Button onClick={handleTest} disabled={testMutation.isPending} className="mt-4">
                    {testMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Test Model
                  </Button>
                </div>
              </div>
              {testResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold">Test Results</h3>
                  <Card className="mt-2">
                    <CardHeader>
                      <CardTitle>Deep Learning Prediction</CardTitle>
                      <CardDescription>Model: <span className="font-medium">{selectedModel}</span></CardDescription>
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
                  <Label htmlFor="model-name-download">Model Name</Label>
                  <Input id="model-name-download" value={downloadModelName} onChange={(e) => setDownloadModelName(e.target.value)} placeholder="e.g., cnn_1678886400" />
                </div>
                <div className="flex gap-4">
                  <Button onClick={() => handleDownload(modelType)}>Download Deep Learning Model</Button>
                </div>
              </div>
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
}
