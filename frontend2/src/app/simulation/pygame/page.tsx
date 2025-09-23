"use client";

import { useState } from 'react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form';
import { useForm } from 'react-hook-form';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Download } from 'lucide-react';
import Image from 'next/image';

type FormValues = { n?: number; steps?: number; width?: number; height?: number; radius?: number; save_gif?: boolean };

export default function PygamePage() {
    const { toast } = useToast();
    const [lastResponse, setLastResponse] = useState<any>(null);
    const [gifUrl, setGifUrl] = useState<string | null>(null);
    const [frames, setFrames] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);

    const form = useForm<FormValues>({ defaultValues: { n: 10, steps: 60, width: 640, height: 480, radius: 6, save_gif: true } });

    const onSubmit = async (data: FormValues) => {
        setLoading(true);
        try {
            const resp = await api.post('/simulation/pygame', data);
            const j = resp.data;
            setLastResponse(j);
            if (j?.error) {
                toast({ variant: 'destructive', title: 'Simulation failed', description: String(j.error) });
                setGifUrl(null);
                setFrames([]);
                return;
            }
            // frames are server-side paths; backend returns gif_url if host available
            setFrames(j.frames || []);
            setGifUrl(j.gif_url || null);
            toast({ title: 'Simulation completed' });
        } catch (e: any) {
            toast({ variant: 'destructive', title: 'Simulation failed', description: e?.message || String(e) });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="text-center mb-6">
                <h1 className="text-3xl font-bold">Pygame Particle Simulation</h1>
                <p className="text-muted-foreground">Run headless particle sims and get frames or an animated GIF.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Parameters</CardTitle>
                        <CardDescription>Adjust simulation size and particles</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-2">
                                <FormField control={form.control} name="n" render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Particles</FormLabel>
                                        <FormControl><Input {...field} type="number" /></FormControl>
                                    </FormItem>
                                )} />
                                <FormField control={form.control} name="steps" render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Frames</FormLabel>
                                        <FormControl><Input {...field} type="number" /></FormControl>
                                    </FormItem>
                                )} />
                                <FormField control={form.control} name="save_gif" render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Save GIF</FormLabel>
                                        <FormControl>
                                            <input
                                                type="checkbox"
                                                checked={Boolean(field.value)}
                                                onChange={(e) => field.onChange(e.target.checked)}
                                                onBlur={field.onBlur}
                                                name={field.name}
                                                ref={field.ref}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )} />
                                <div className="pt-2">
                                    <Button type="submit" disabled={loading}>{loading ? <Loader2 className="animate-spin h-4 w-4" /> : 'Run Simulation'}</Button>
                                </div>
                            </form>
                        </Form>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Output</CardTitle>
                        <CardDescription>GIF preview or frames</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {gifUrl ? (
                            <div className="w-full h-[360px] flex items-center justify-center"><img src={gifUrl} alt="gif" className="max-h-80" /></div>
                        ) : frames.length > 0 ? (
                            <div className="grid grid-cols-2 gap-2">
                                {frames.map((f: string) => (
                                    <div key={f} className="relative aspect-video w-full h-40"><Image src={f} alt="frame" layout="fill" objectFit="contain" unoptimized /></div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-muted-foreground">Run the simulation to see frames or a GIF here.</p>
                        )}
                    </CardContent>
                </Card>

                {lastResponse && (
                    <Card className="lg:col-span-2">
                        <CardHeader>
                            <CardTitle>Server response (debug)</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(lastResponse, null, 2)}</pre>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
