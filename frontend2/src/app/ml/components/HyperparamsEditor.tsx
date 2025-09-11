import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function HyperparamsEditor({ preset, setPreset, list, setList }: { preset: string; setPreset: (v: string) => void; list: Array<{ key: string; value: string }>; setList: (s: Array<{ key: string; value: string }>) => void }) {
    return (
        <div>
            <Label htmlFor="hyperparams-preset">Hyperparameter Preset</Label>
            <Select value={preset} onValueChange={(v) => setPreset(v)}>
                <SelectTrigger id="hyperparams-preset"><SelectValue /></SelectTrigger>
                <SelectContent>
                    <SelectItem value="default">Default</SelectItem>
                    <SelectItem value="fast">Fast (lower complexity)</SelectItem>
                    <SelectItem value="accurate">Accurate (higher complexity)</SelectItem>
                </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground mt-2">Choose a preset or add simple key/value hyperparameters below.</p>
            <div className="space-y-2 mt-2">
                {list.map((p, i) => (
                    <div key={i} className="flex gap-2">
                        <Input value={p.key} placeholder="param" onChange={(e) => {
                            const next = [...list];
                            next[i] = { ...next[i], key: e.target.value };
                            setList(next);
                        }} />
                        <Input value={p.value} placeholder="value" onChange={(e) => {
                            const next = [...list];
                            next[i] = { ...next[i], value: e.target.value };
                            setList(next);
                        }} />
                        <Button variant="ghost" onClick={() => {
                            const next = list.filter((_, idx) => idx !== i);
                            setList(next);
                        }}>Remove</Button>
                    </div>
                ))}
                <Button variant="secondary" onClick={() => setList([...list, { key: '', value: '' }])}>Add parameter</Button>
            </div>
        </div>
    );
}
