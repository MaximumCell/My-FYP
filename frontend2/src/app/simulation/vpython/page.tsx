"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Play, Zap, Atom, Waves, Globe, Info, Activity, Sparkles } from 'lucide-react';

type Preset = { name: string; description: string; params?: Record<string, any> };

// Enhanced experiment information
const EXPERIMENT_INFO = {
    electric: {
        icon: <Zap className="h-5 w-5" />,
        title: "Electric Field",
        description: "Coulomb forces between charged particles",
        physics: ["F = k·q₁·q₂/r²", "Electric field lines", "Distance-based interactions"],
        color: "bg-blue-500"
    },
    magnetic: {
        icon: <Atom className="h-5 w-5" />,
        title: "Magnetic Field",
        description: "Lorentz forces on moving charges",
        physics: ["F = q·v×B", "Cyclotron motion", "Velocity-dependent forces"],
        color: "bg-purple-500"
    },
    gravity: {
        icon: <Globe className="h-5 w-5" />,
        title: "Gravitational Field",
        description: "Orbital mechanics and Newton's law",
        physics: ["F = G·m₁·m₂/r²", "Orbital trajectories", "Conservation laws"],
        color: "bg-orange-500"
    }
};

export default function VPythonPage() {
    const { toast } = useToast();
    const [presets, setPresets] = useState<Preset[]>([]);
    const [htmlUrl, setHtmlUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [currentExperiment, setCurrentExperiment] = useState<string | null>(null);
    const [simulationStats, setSimulationStats] = useState({
        particles: 0,
        forces: 0,
        energy: 0
    });

    useEffect(() => {
        let mounted = true;
        console.log('VPython page: Fetching presets...');
        api.get('/simulation/vpython/presets').then(r => {
            if (!mounted) return;
            console.log('VPython page: Presets received:', r.data);
            setPresets(r.data?.presets || []);
        }).catch((error) => {
            console.error('VPython page: Error fetching presets:', error);
            // Show error to user
            toast({
                variant: 'destructive',
                title: 'Connection Error',
                description: 'Failed to load physics experiments. Please check if the backend server is running.'
            });
        });
        return () => { mounted = false; };
    }, [toast]);

    const onSubmit = async (data: any) => {
        setLoading(true);
        setCurrentExperiment(data.preset);
        console.log('VPython page: Submitting simulation request:', data);

        try {
            const resp = await api.post('/simulation/vpython', data);
            const j = resp.data;
            console.log('VPython page: Simulation response:', j);

            if (j?.error) {
                console.error('VPython page: Simulation error:', j.error);
                toast({
                    variant: 'destructive',
                    title: 'Simulation Failed',
                    description: String(j.error)
                });
                setHtmlUrl(null);
                setCurrentExperiment(null);
                return;
            }
            const rawUrl = j.html_url || j.html_path || null;
            console.log('VPython page: Raw URL:', rawUrl);

            if (!rawUrl) {
                console.error('VPython page: No HTML URL returned');
                toast({
                    variant: 'destructive',
                    title: 'Simulation Failed',
                    description: 'No HTML returned'
                });
                setHtmlUrl(null);
                setCurrentExperiment(null);
                return;
            }

            try {
                const filename = String(rawUrl).split('/').pop();
                const base = (api.defaults.baseURL as string) || window.location.origin;
                const preview = `${String(base).replace(/\/$/, '')}/simulation/vpython/preview/${filename}`;
                console.log('VPython page: Preview URL:', preview);
                setHtmlUrl(preview);
            } catch (err) {
                console.log('VPython page: Using raw URL:', rawUrl);
                setHtmlUrl(rawUrl as string);
            }

            const experimentInfo = EXPERIMENT_INFO[data.preset as keyof typeof EXPERIMENT_INFO];
            toast({
                title: `${experimentInfo?.title || 'Physics'} Simulation Ready`,
                description: 'Interactive simulation with realistic particle physics loaded successfully'
            });

        } catch (e: any) {
            console.error('VPython page: Request error:', e);
            toast({ variant: 'destructive', title: 'Error', description: e?.message || String(e) });
            setCurrentExperiment(null);
        } finally {
            setLoading(false);
        }
    };

    const runPreset = (preset: Preset) => {
        const payload: any = { preset: preset.name };
        if (preset.params) Object.assign(payload, preset.params);
        onSubmit(payload);
    };

    const getPresetIcon = (name: string) => {
        if (name.includes('electric')) return <Zap className="h-4 w-4 text-blue-500" />;
        if (name.includes('magnetic')) return <Atom className="h-4 w-4 text-purple-500" />;
        if (name.includes('gravity')) return <Globe className="h-4 w-4 text-orange-500" />;
        if (name.includes('wave') || name.includes('field')) return <Waves className="h-4 w-4 text-cyan-500" />;
        return <Play className="h-4 w-4" />;
    };

    const getExperimentInfo = (name: string) => {
        return EXPERIMENT_INFO[name as keyof typeof EXPERIMENT_INFO] || null;
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
                        Explore realistic physics simulations with distance-based particle interactions and real-time force calculations
                    </p>
                    {currentExperiment && (
                        <Alert className="max-w-2xl mx-auto mt-4">
                            <Info className="h-4 w-4" />
                            <AlertDescription>
                                <strong>{getExperimentInfo(currentExperiment)?.title || 'Physics'} Simulation:</strong> {getExperimentInfo(currentExperiment)?.description || 'Interactive physics simulation'}
                            </AlertDescription>
                        </Alert>
                    )}
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                    {/* Sidebar Controls */}
                    <div className="xl:col-span-1 space-y-6">
                        {/* Experiment Presets */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Sparkles className="h-5 w-5 text-primary" />
                                    Physics Experiments
                                </CardTitle>
                                <CardDescription>
                                    Different physics simulations with realistic particle interactions
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {presets.length === 0 ? (
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Loading experiments...
                                    </div>
                                ) : (
                                    presets.map(preset => {
                                        const info = getExperimentInfo(preset.name);
                                        const isActive = currentExperiment === preset.name;
                                        return (
                                            <Button
                                                key={preset.name}
                                                variant={isActive ? "default" : "outline"}
                                                className={`w-full justify-start h-auto p-4 relative ${isActive ? 'ring-2 ring-primary' : ''}`}
                                                onClick={() => runPreset(preset)}
                                                disabled={loading}
                                            >
                                                {loading && currentExperiment === preset.name && (
                                                    <Loader2 className="absolute top-2 right-2 h-4 w-4 animate-spin" />
                                                )}
                                                <div className="flex items-start gap-3 w-full">
                                                    {getPresetIcon(preset.name)}
                                                    <div className="text-left flex-1">
                                                        <div className="font-medium flex items-center gap-2">
                                                            {preset.name}
                                                            {isActive && (
                                                                <Badge variant="secondary" className="text-xs">
                                                                    Active
                                                                </Badge>
                                                            )}
                                                        </div>
                                                        <div className="text-xs text-muted-foreground mt-1">
                                                            {preset.description}
                                                        </div>
                                                        {info && (
                                                            <div className="text-xs text-muted-foreground mt-2 space-y-1">
                                                                {info.physics.map((formula, idx) => (
                                                                    <div key={idx} className="font-mono">• {formula}</div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </Button>
                                        );
                                    })
                                )}
                            </CardContent>
                        </Card>

                        {/* Physics Information */}
                        {currentExperiment && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Activity className="h-5 w-5 text-green-500" />
                                        Live Physics Data
                                    </CardTitle>
                                    <CardDescription>
                                        Real-time simulation information
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-muted-foreground">Experiment:</span>
                                            <Badge variant="outline" className="flex items-center gap-1">
                                                {getExperimentInfo(currentExperiment)?.icon}
                                                {getExperimentInfo(currentExperiment)?.title}
                                            </Badge>
                                        </div>
                                        <div className="grid grid-cols-2 gap-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Particles:</span>
                                                <span className="font-medium">Dynamic</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Forces:</span>
                                                <span className="font-medium">Real-time</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Physics:</span>
                                                <span className="font-medium">Distance-based</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Interactions:</span>
                                                <span className="font-medium">All particles</span>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Features Overview */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Info className="h-5 w-5 text-blue-500" />
                                    Interactive Features
                                </CardTitle>
                                <CardDescription>
                                    What you can do in the simulations
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3 text-sm">
                                    <div className="flex items-start gap-2">
                                        <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0"></div>
                                        <div>
                                            <strong>Add Particles:</strong> Click "Add Particle" to introduce new charges/masses with custom properties
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-2">
                                        <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                                        <div>
                                            <strong>Real-time Forces:</strong> Watch particles interact through distance-based calculations
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-2">
                                        <div className="w-2 h-2 rounded-full bg-purple-500 mt-2 flex-shrink-0"></div>
                                        <div>
                                            <strong>Adjust Physics:</strong> Control field strength, damping, and simulation speed
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-2">
                                        <div className="w-2 h-2 rounded-full bg-orange-500 mt-2 flex-shrink-0"></div>
                                        <div>
                                            <strong>Visual Effects:</strong> Toggle particle trails, field lines, and force vectors
                                        </div>
                                    </div>
                                </div>
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
                                            Each experiment shows different physics with realistic particle interactions and distance-based calculations
                                        </CardDescription>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {htmlUrl && (
                                            <Badge variant="secondary" className="flex items-center gap-1">
                                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                                Live Simulation
                                            </Badge>
                                        )}
                                        {loading && (
                                            <Badge variant="outline" className="flex items-center gap-1">
                                                <Loader2 className="w-2 h-2 animate-spin" />
                                                Loading
                                            </Badge>
                                        )}
                                    </div>
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
                                            <h3 className="text-lg font-medium mb-2">Ready for Physics Experiments</h3>
                                            <p className="text-sm text-center max-w-sm mb-4">
                                                Select an experiment to explore different physics simulations with realistic particle interactions.
                                            </p>
                                            <div className="grid grid-cols-1 gap-2 text-xs text-center max-w-md">
                                                <div className="flex items-center justify-center gap-2 p-2 rounded bg-blue-50 dark:bg-blue-950/30">
                                                    <Zap className="h-3 w-3 text-blue-500" />
                                                    <span><strong>Electric:</strong> Coulomb forces & field lines</span>
                                                </div>
                                                <div className="flex items-center justify-center gap-2 p-2 rounded bg-purple-50 dark:bg-purple-950/30">
                                                    <Atom className="h-3 w-3 text-purple-500" />
                                                    <span><strong>Magnetic:</strong> Lorentz forces & cyclotron motion</span>
                                                </div>
                                                <div className="flex items-center justify-center gap-2 p-2 rounded bg-orange-50 dark:bg-orange-950/30">
                                                    <Globe className="h-3 w-3 text-orange-500" />
                                                    <span><strong>Gravity:</strong> Orbital mechanics & Newton's law</span>
                                                </div>
                                            </div>
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