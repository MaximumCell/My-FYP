"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Play, Zap, Atom, Waves } from 'lucide-react';

type Preset = { name: string; description: string; params?: Record<string, any> };

export default function VPythonPage() {
    const { toast } = useToast();
    const [presets, setPresets] = useState<Preset[]>([]);
    const [htmlUrl, setHtmlUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        let mounted = true;
        api.get('/simulation/vpython/presets').then(r => {
            if (!mounted) return;
            setPresets(r.data?.presets || []);
        }).catch(() => {
            // ignore
        });
        return () => { mounted = false; };
    }, []);

    const onSubmit = async (data: any) => {
        setLoading(true);
        try {
            const resp = await api.post('/simulation/vpython', data);
            const j = resp.data;
            if (j?.error) {
                toast({ variant: 'destructive', title: 'Simulation Failed', description: String(j.error) });
                setHtmlUrl(null);
                return;
            }
            const rawUrl = j.html_url || j.html_path || null;
            if (!rawUrl) {
                toast({ variant: 'destructive', title: 'Simulation Failed', description: 'No HTML returned' });
                setHtmlUrl(null);
                return;
            }

            try {
                const filename = String(rawUrl).split('/').pop();
                const base = (api.defaults.baseURL as string) || window.location.origin;
                const preview = `${String(base).replace(/\/$/, '')}/simulation/vpython/preview/${filename}`;
                setHtmlUrl(preview);
            } catch (err) {
                setHtmlUrl(rawUrl as string);
            }
            toast({ title: 'Simulation Ready', description: 'Interactive physics simulation loaded successfully' });
        } catch (e: any) {
            toast({ variant: 'destructive', title: 'Error', description: e?.message || String(e) });
        } finally {
            setLoading(false);
        }
    };

    const runPreset = (preset: Preset) => {
        const payload: any = { preset: preset.name };
        if (preset.params) Object.assign(payload, preset.params);
        onSubmit(payload);
    }; const getPresetIcon = (name: string) => {
        if (name.includes('electric')) return <Zap className="h-4 w-4" />;
        if (name.includes('magnetic') || name.includes('dipole')) return <Atom className="h-4 w-4" />;
        if (name.includes('wave') || name.includes('field')) return <Waves className="h-4 w-4" />;
        return <Play className="h-4 w-4" />;
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">
                        Interactive Physics Laboratory
                    </h1>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                        Explore 3D physics simulations with real-time controls and interactive experiments
                    </p>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                    {/* Sidebar Controls */}
                    <div className="xl:col-span-1 space-y-6">
                        {/* Experiment Presets */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Zap className="h-5 w-5 text-primary" />
                                    Physics Experiments
                                </CardTitle>
                                <CardDescription>
                                    Ready-to-run interactive simulations
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {presets.length === 0 ? (
                                    <p className="text-sm text-muted-foreground">Loading experiments...</p>
                                ) : (
                                    presets.map(preset => (
                                        <Button
                                            key={preset.name}
                                            variant="outline"
                                            className="w-full justify-start h-auto p-4"
                                            onClick={() => runPreset(preset)}
                                            disabled={loading}
                                        >
                                            <div className="flex items-start gap-3 w-full">
                                                {getPresetIcon(preset.name)}
                                                <div className="text-left flex-1">
                                                    <div className="font-medium">{preset.name}</div>
                                                    <div className="text-xs text-muted-foreground mt-1">
                                                        {preset.description}
                                                    </div>
                                                </div>
                                            </div>
                                        </Button>
                                    ))
                                )}
                            </CardContent>
                        </Card>
                    </div>                    {/* Main Simulation Area */}
                    <div className="xl:col-span-3">
                        <Card className="h-[80vh]">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle>Interactive Physics Laboratory</CardTitle>
                                        <CardDescription>
                                            Click to add charges, drag to move, right-click to remove
                                        </CardDescription>
                                    </div>
                                    {htmlUrl && (
                                        <Badge variant="secondary" className="flex items-center gap-1">
                                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                            Live Simulation
                                        </Badge>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent className="h-full pb-6">
                                <div className="h-full w-full rounded-lg border bg-muted/5 overflow-hidden">
                                    {htmlUrl ? (
                                        <iframe
                                            src={htmlUrl}
                                            title="Interactive Physics Simulation"
                                            className="w-full h-full block"
                                            style={{
                                                border: 'none',
                                                minHeight: '600px',
                                                backgroundColor: '#000'
                                            }}
                                            allow="fullscreen"
                                        />
                                    ) : (
                                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                                            <div className="p-8 rounded-full bg-muted/50 mb-4">
                                                <Atom className="h-12 w-12" />
                                            </div>
                                            <h3 className="text-lg font-medium mb-2">Ready for Interactive Physics</h3>
                                            <p className="text-sm text-center max-w-sm">
                                                Select an experiment to start interacting with 3D physics simulations.
                                                Click to add charges, drag to move them, and watch field lines flow!
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
