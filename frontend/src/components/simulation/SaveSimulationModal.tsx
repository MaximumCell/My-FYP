import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { X, Save, Loader2 } from 'lucide-react';
import { useSaveSimulation } from '@/hooks/use-save-simulation';

interface SaveSimulationModalProps {
    isOpen: boolean;
    onClose: () => void;
    plotHtml: string;
    defaultConfig: {
        equation?: string;
        parameters: Record<string, any>;
        variables: string[];
        plot_type?: string;
        x_range?: number[];
        y_range?: number[];
        z_range?: number[];
    };
    defaultMetadata?: {
        simulation_name?: string;
        simulation_type?: 'plot2d' | 'plot3d' | 'interactive-physics' | 'custom-equation' | 'projectile-motion' | 'electric-field' | 'wave-simulation' | 'other';
        plot_title?: string;
        x_label?: string;
        y_label?: string;
        z_label?: string;
    };
    executionTime: number;
}

export default function SaveSimulationModal({
    isOpen,
    onClose,
    plotHtml,
    defaultConfig,
    defaultMetadata,
    executionTime
}: SaveSimulationModalProps) {
    const [simulationName, setSimulationName] = useState('');
    const [description, setDescription] = useState('');
    const [tagInput, setTagInput] = useState('');
    const [tags, setTags] = useState<string[]>([]);
    const [isPublic, setIsPublic] = useState(false);
    const [plotTitle, setPlotTitle] = useState('');
    const [xLabel, setXLabel] = useState('');
    const [yLabel, setYLabel] = useState('');
    const [zLabel, setZLabel] = useState('');

    const { saveSimulation, isSaving } = useSaveSimulation();

    // Reset form when modal opens/closes or when defaultMetadata changes
    useEffect(() => {
        if (isOpen) {
            setSimulationName(defaultMetadata?.simulation_name || '');
            setDescription('');
            setTags([]);
            setTagInput('');
            setIsPublic(false);
            setPlotTitle(defaultMetadata?.plot_title || '');
            setXLabel(defaultMetadata?.x_label || '');
            setYLabel(defaultMetadata?.y_label || '');
            setZLabel(defaultMetadata?.z_label || '');
        }
    }, [isOpen, defaultMetadata]);

    const handleAddTag = () => {
        const trimmedTag = tagInput.trim();
        if (trimmedTag && !tags.includes(trimmedTag)) {
            setTags([...tags, trimmedTag]);
            setTagInput('');
        }
    };

    const handleRemoveTag = (tagToRemove: string) => {
        setTags(tags.filter(tag => tag !== tagToRemove));
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddTag();
        }
    };

    const handleSave = async () => {
        if (!simulationName.trim()) {
            return;
        }

        try {
            await saveSimulation({
                simulation_name: simulationName.trim(),
                simulation_type: defaultMetadata?.simulation_type || 'other',
                description: description.trim() || undefined,
                tags: tags.length > 0 ? tags : undefined,
                config: defaultConfig,
                execution_time: executionTime,
                plot_title: plotTitle.trim() || undefined,
                x_label: xLabel.trim() || undefined,
                y_label: yLabel.trim() || undefined,
                z_label: zLabel.trim() || undefined,
                is_public: isPublic,
                plot_html: plotHtml,
            });

            // Close modal on successful save
            onClose();
        } catch (error) {
            // Error is handled by the hook
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[525px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Save Simulation</DialogTitle>
                    <DialogDescription>
                        Save this simulation to your account for future viewing and sharing.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Simulation Name */}
                    <div className="space-y-2">
                        <Label htmlFor="simulation-name">Simulation Name *</Label>
                        <Input
                            id="simulation-name"
                            value={simulationName}
                            onChange={(e) => setSimulationName(e.target.value)}
                            placeholder="Enter a descriptive name for your simulation"
                            disabled={isSaving}
                        />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Optional description of what this simulation shows"
                            rows={3}
                            disabled={isSaving}
                        />
                    </div>

                    {/* Plot Labels */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="plot-title">Plot Title</Label>
                            <Input
                                id="plot-title"
                                value={plotTitle}
                                onChange={(e) => setPlotTitle(e.target.value)}
                                placeholder="Plot title"
                                disabled={isSaving}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="x-label">X-axis Label</Label>
                            <Input
                                id="x-label"
                                value={xLabel}
                                onChange={(e) => setXLabel(e.target.value)}
                                placeholder="X-axis label"
                                disabled={isSaving}
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="y-label">Y-axis Label</Label>
                            <Input
                                id="y-label"
                                value={yLabel}
                                onChange={(e) => setYLabel(e.target.value)}
                                placeholder="Y-axis label"
                                disabled={isSaving}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="z-label">Z-axis Label</Label>
                            <Input
                                id="z-label"
                                value={zLabel}
                                onChange={(e) => setZLabel(e.target.value)}
                                placeholder="Z-axis label (if applicable)"
                                disabled={isSaving}
                            />
                        </div>
                    </div>

                    {/* Tags */}
                    <div className="space-y-2">
                        <Label htmlFor="tags">Tags</Label>
                        <div className="flex gap-2">
                            <Input
                                id="tags"
                                value={tagInput}
                                onChange={(e) => setTagInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Add tags (press Enter to add)"
                                disabled={isSaving}
                            />
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleAddTag}
                                disabled={!tagInput.trim() || isSaving}
                            >
                                Add
                            </Button>
                        </div>
                        {tags.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-2">
                                {tags.map((tag) => (
                                    <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                                        {tag}
                                        <X
                                            className="h-3 w-3 cursor-pointer"
                                            onClick={() => handleRemoveTag(tag)}
                                        />
                                    </Badge>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Public checkbox */}
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="public"
                            checked={isPublic}
                            onCheckedChange={(checked) => setIsPublic(checked === true)}
                            disabled={isSaving}
                        />
                        <Label
                            htmlFor="public"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Make this simulation public (others can view it)
                        </Label>
                    </div>

                    {/* Simulation Info */}
                    <div className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
                        <div className="grid grid-cols-2 gap-2">
                            <div>Type: {defaultMetadata?.simulation_type || 'other'}</div>
                            <div>Execution time: {executionTime.toFixed(2)}s</div>
                            {defaultConfig.equation && (
                                <div className="col-span-2 font-mono text-xs">
                                    Equation: {defaultConfig.equation}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={onClose} disabled={isSaving}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSave}
                        disabled={!simulationName.trim() || isSaving}
                    >
                        {isSaving ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="mr-2 h-4 w-4" />
                                Save Simulation
                            </>
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}