import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tooltip as RadixTooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '@/components/ui/tooltip';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, Settings, Zap } from 'lucide-react';

interface DeepLearningParamsEditorProps {
    epochs: number;
    setEpochs: (v: number) => void;
    batchSize: number;
    setBatchSize: (v: number) => void;
    configJson: string;
    setConfigJson: (v: string) => void;
    preset: string;
    setPreset: (v: string) => void;
}

const deepLearningDescriptions = {
    epochs: 'Number of complete passes through the training dataset. More epochs can improve performance but may cause overfitting.',
    batch_size: 'Number of samples processed before updating model weights. Larger batches use more memory but can be more stable.',
    hidden_layers: 'List of neurons in each hidden layer. More layers = deeper network. Example: [128, 64, 32]',
    dropout: 'Dropout rate (0-1) to prevent overfitting. Higher values = more regularization. Typical: 0.1-0.5',
    learning_rate: 'Step size for weight updates. Lower = more stable but slower. Typical: 0.001-0.01',
    activation: 'Activation function for hidden layers. ReLU is most common, tanh/sigmoid for specific cases.',
    optimizer: 'Algorithm for updating weights. Adam is most popular, SGD for simpler cases.'
};

export default function DeepLearningParamsEditor({
    epochs,
    setEpochs,
    batchSize,
    setBatchSize,
    configJson,
    setConfigJson,
    preset,
    setPreset
}: DeepLearningParamsEditorProps) {

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
        },
        custom: null
    };

    const applyPreset = (presetName: string) => {
        setPreset(presetName);
        if (presetName !== 'custom' && presetConfigs[presetName as keyof typeof presetConfigs]) {
            setConfigJson(JSON.stringify(presetConfigs[presetName as keyof typeof presetConfigs], null, 2));
        }
    };

    const getPresetDescription = (presetName: string) => {
        switch (presetName) {
            case 'simple': return 'Lightweight network for small datasets (<1000 samples)';
            case 'standard': return 'Balanced network for medium datasets (1000-10000 samples)';
            case 'deep': return 'Complex network for large datasets (>10000 samples)';
            case 'custom': return 'Manual JSON configuration for advanced users';
            default: return '';
        }
    };

    return (
        <TooltipProvider>
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        Deep Learning Parameters
                    </CardTitle>
                    <CardDescription>Configure your neural network architecture and training parameters</CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="basic" className="w-full">
                        <TabsList className="grid w-full grid-cols-3">
                            <TabsTrigger value="basic">
                                <Zap className="h-4 w-4 mr-2" />
                                Basic
                            </TabsTrigger>
                            <TabsTrigger value="architecture">
                                <Brain className="h-4 w-4 mr-2" />
                                Architecture
                            </TabsTrigger>
                            <TabsTrigger value="advanced">
                                <Settings className="h-4 w-4 mr-2" />
                                Advanced
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="basic" className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="epochs-input">
                                        <RadixTooltip>
                                            <TooltipTrigger asChild>
                                                <span className="cursor-help border-b border-dotted">Epochs</span>
                                            </TooltipTrigger>
                                            <TooltipContent side="top">{deepLearningDescriptions.epochs}</TooltipContent>
                                        </RadixTooltip>
                                    </Label>
                                    <Input
                                        id="epochs-input"
                                        type="number"
                                        min={1}
                                        max={1000}
                                        value={epochs}
                                        onChange={(e) => setEpochs(Number(e.target.value))}
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">Recommended: 10-50 for most datasets</p>
                                </div>

                                <div>
                                    <Label htmlFor="batch-size-input">
                                        <RadixTooltip>
                                            <TooltipTrigger asChild>
                                                <span className="cursor-help border-b border-dotted">Batch Size</span>
                                            </TooltipTrigger>
                                            <TooltipContent side="top">{deepLearningDescriptions.batch_size}</TooltipContent>
                                        </RadixTooltip>
                                    </Label>
                                    <Input
                                        id="batch-size-input"
                                        type="number"
                                        min={1}
                                        max={512}
                                        value={batchSize}
                                        onChange={(e) => setBatchSize(Number(e.target.value))}
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">Common: 16, 32, 64, 128</p>
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="architecture" className="space-y-4">
                            <div>
                                <Label htmlFor="preset-select">Network Architecture Preset</Label>
                                <Select value={preset} onValueChange={applyPreset}>
                                    <SelectTrigger id="preset-select">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="simple">
                                            <div className="flex flex-col items-start">
                                                <span>Simple Network</span>
                                                <span className="text-xs text-muted-foreground">2 layers: [64, 32]</span>
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="standard">
                                            <div className="flex flex-col items-start">
                                                <span>Standard Network</span>
                                                <span className="text-xs text-muted-foreground">3 layers: [128, 64, 32]</span>
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="deep">
                                            <div className="flex flex-col items-start">
                                                <span>Deep Network</span>
                                                <span className="text-xs text-muted-foreground">4 layers: [256, 128, 64, 32]</span>
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="custom">
                                            <div className="flex flex-col items-start">
                                                <span>Custom Configuration</span>
                                                <span className="text-xs text-muted-foreground">Manual JSON setup</span>
                                            </div>
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                                {preset !== 'custom' && (
                                    <div className="mt-2 p-3 bg-muted rounded-md">
                                        <p className="text-sm text-muted-foreground">{getPresetDescription(preset)}</p>
                                        {preset !== 'custom' && presetConfigs[preset as keyof typeof presetConfigs] && (
                                            <div className="flex flex-wrap gap-1 mt-2">
                                                {Object.entries(presetConfigs[preset as keyof typeof presetConfigs] || {}).map(([key, value]) => (
                                                    <Badge key={key} variant="outline" className="text-xs">
                                                        {key}: {Array.isArray(value) ? `[${value.join(', ')}]` : String(value)}
                                                    </Badge>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </TabsContent>

                        <TabsContent value="advanced" className="space-y-4">
                            <div>
                                <Label htmlFor="config-json">
                                    <RadixTooltip>
                                        <TooltipTrigger asChild>
                                            <span className="cursor-help border-b border-dotted">Custom Configuration (JSON)</span>
                                        </TooltipTrigger>
                                        <TooltipContent side="top">
                                            Advanced neural network parameters in JSON format
                                        </TooltipContent>
                                    </RadixTooltip>
                                </Label>
                                <Textarea
                                    id="config-json"
                                    value={configJson}
                                    onChange={(e) => {
                                        setConfigJson(e.target.value);
                                        setPreset('custom');
                                    }}
                                    rows={8}
                                    className="font-mono text-sm"
                                    placeholder='{\n  "hidden_layers": [128, 64, 32],\n  "dropout": 0.3,\n  "learning_rate": 0.001,\n  "optimizer": "adam"\n}'
                                />
                                <div className="mt-2 space-y-1">
                                    <p className="text-xs text-muted-foreground">Available parameters:</p>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                        {Object.entries(deepLearningDescriptions).slice(2).map(([key, desc]) => (
                                            <RadixTooltip key={key}>
                                                <TooltipTrigger asChild>
                                                    <div className="cursor-help p-2 border rounded text-muted-foreground hover:bg-muted">
                                                        <code className="font-mono">{key}</code>
                                                    </div>
                                                </TooltipTrigger>
                                                <TooltipContent side="top" className="max-w-xs">
                                                    {desc}
                                                </TooltipContent>
                                            </RadixTooltip>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>
        </TooltipProvider>
    );
}