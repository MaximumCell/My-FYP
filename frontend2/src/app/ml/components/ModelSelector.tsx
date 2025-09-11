import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

export default function ModelSelector({ models, selectedModel, setSelectedModel, modelsLoading }: { models?: string[]; selectedModel: string; setSelectedModel: (v: string) => void; modelsLoading: boolean }) {
    return (
        <div>
            <Label htmlFor="model-select">Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger id="model-select">
                    <SelectValue placeholder={modelsLoading ? 'Loading...' : 'Select a model'} />
                </SelectTrigger>
                <SelectContent>
                    {models?.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                </SelectContent>
            </Select>
        </div>
    );
}
