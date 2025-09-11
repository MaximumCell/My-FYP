'use client';

import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Rocket, TestTube, Lightbulb, Download, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useModels, useColumns, useTrainModel, useTestModel, useRecommendModel } from '@/hooks/use-ml-api';
import type { ApiError, ModelType, TrainResponse } from '@/types/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import FileUpload from '@/components/ml/file-upload';
import api from '@/lib/api';

export default function MlModelTypePage() {
  const [file, setFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [modelType, setModelType] = useState<ModelType>('deep-learning');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [trainResults, setTrainResults] = useState<TrainResponse | null>(null);
  const [testJson, setTestJson] = useState('[\n  {\n    "feature1": 0,\n    "feature2": 0\n  }\n]');
  const [testResults, setTestResults] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<string>('');
  const [epochs, setEpochs] = useState<number>(5);
  const [batchSize, setBatchSize] = useState<number>(32);
  const [configJson, setConfigJson] = useState<string>('');
  const [downloadModelName, setDownloadModelName] = useState('');

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

  const columnsMutation = useColumns();
  const trainMutation = useTrainModel(modelType);
  const testMutation = useTestModel(modelType);
  const recommendMutation = useRecommendModel();

  const handleFileChange = (acceptedFiles: File[]) => {
    const newFile = acceptedFiles[0];
    if (newFile) {
      setFile(newFile);
      setColumns([]);
      setTargetColumn('');
      setTrainResults(null);
      setRecommendation('');
      columnsMutation.mutate(newFile, {
        onSuccess: (data) => setColumns(data.columns),
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
    if (!selectedModel || !testJson) {
      toast({ variant: 'destructive', title: 'Missing model or test data' });
      return;
    }
    try {
      const input = JSON.parse(testJson);

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
  }

  return (
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
                <CardTitle>Train a New Model</CardTitle>
                <CardDescription>Upload your dataset, choose a model, and start training.</CardDescription>
              </CardHeader>
              <FileUpload onFileChange={handleFileChange} />
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
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
                    <div>
                      <Label htmlFor="epochs">Epochs</Label>
                      <Input id="epochs" type="number" min={1} value={epochs} onChange={(e) => setEpochs(Number(e.target.value))} />
                    </div>
                    <div>
                      <Label htmlFor="batch">Batch size</Label>
                      <Input id="batch" type="number" min={1} value={batchSize} onChange={(e) => setBatchSize(Number(e.target.value))} />
                    </div>
                    <div>
                      <Label htmlFor="config">Config (JSON)</Label>
                      <Textarea id="config" value={configJson} onChange={(e) => setConfigJson(e.target.value)} rows={3} />
                    </div>
                  </div>
                  <div className="mt-4">
                    <Button onClick={handleTrain} disabled={trainMutation.isPending}>
                      {trainMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Train Model
                    </Button>
                  </div>
                </div>
              )}
              {trainResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold">Training Results</h3>
                  {renderMetrics(trainResults)}
                </div>
              )}
            </TabsContent>
            <TabsContent value="test">
              <CardHeader className="p-0 mb-4">
                <CardTitle>Test an Existing Model</CardTitle>
                <CardDescription>Provide a model name and new data to get predictions.</CardDescription>
              </CardHeader>
              <div className="mt-4 space-y-4">
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
                  <Label htmlFor="test-data">New Data (JSON format)</Label>
                  <Textarea id="test-data" value={testJson} onChange={(e) => setTestJson(e.target.value)} rows={10} className="font-code" />
                </div>
                <Button onClick={handleTest} disabled={testMutation.isPending}>
                  {testMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Test Model
                </Button>
              </div>
              {testResults && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold">Test Results</h3>
                  <Card className="mt-2">
                    <CardContent className="p-4">
                      <pre className="text-sm font-code bg-muted p-4 rounded-md overflow-x-auto">{JSON.stringify(testResults, null, 2)}</pre>
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
