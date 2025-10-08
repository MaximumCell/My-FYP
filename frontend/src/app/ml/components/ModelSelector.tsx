import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Tooltip as RadixTooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '@/components/ui/tooltip';
import { modelDescriptions } from '@/app/ml/utils/tooltips';

export default function ModelSelector({ models, selectedModel, setSelectedModel, modelsLoading }: { models?: string[]; selectedModel: string; setSelectedModel: (v: string) => void; modelsLoading: boolean }) {
    return (
        <div>
            <Label htmlFor="model-select">Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger id="model-select">
                    <SelectValue placeholder={modelsLoading ? 'Loading...' : 'Select a model'} />
                </SelectTrigger>
                <SelectContent>
                    <TooltipProvider>
                        {models?.map(m => (
                            <SelectItem key={m} value={m}>
                                <RadixTooltip>
                                    <TooltipTrigger asChild>
                                        <span className="cursor-default">{m}</span>
                                    </TooltipTrigger>
                                    <TooltipContent side="top">
                                        {modelDescriptions[m] ?? modelDescriptions[m.toLowerCase()] ?? 'Model'}
                                    </TooltipContent>
                                </RadixTooltip>
                            </SelectItem>
                        ))}
                    </TooltipProvider>
                </SelectContent>
            </Select>
        </div>
    );
}
