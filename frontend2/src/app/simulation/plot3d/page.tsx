"use client";

import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import NextImage from 'next/image';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, UploadCloud, Download, FileText, Settings, ChevronDown, Palette, ImageIcon, Zap, ArrowLeftRight } from 'lucide-react';
import dynamic from 'next/dynamic';
const MathTokenPicker = dynamic(() => import('@/components/math/MathTokenPicker'), { ssr: false });

const equationSchema = z.object({
    equation: z.string().min(1, 'Equation is required'),
    x_min: z.coerce.number().default(-5),
    x_max: z.coerce.number().default(5),
    y_min: z.coerce.number().default(-5),
    y_max: z.coerce.number().default(5),
    resolution: z.coerce.number().default(80),
    // Plot customization options
    width: z.coerce.number().default(1200),
    height: z.coerce.number().default(800),
    dpi: z.coerce.number().default(300),
    line_width: z.coerce.number().default(2),
    line_color: z.string().default('#2563eb'),
    background_color: z.string().default('#ffffff'),
    grid: z.boolean().default(true),
    grid_alpha: z.coerce.number().default(0.3),
    title: z.string().default(''),
    xlabel: z.string().default(''),
    ylabel: z.string().default(''),
    zlabel: z.string().default(''),
    font_size: z.coerce.number().default(12),
    style: z.enum(['default', 'seaborn', 'ggplot', 'dark_background', 'bmh']).default('default'),
    format: z.enum(['png', 'svg', 'pdf']).default('png'),
    colormap: z.string().default('viridis')
});

const csvSchema = z.object({
    file: z.any(),
    x_col: z.string().min(1),
    y_col: z.string().min(1),
    z_col: z.string().min(1),
    // Same customization options for CSV
    width: z.coerce.number().default(1200),
    height: z.coerce.number().default(800),
    dpi: z.coerce.number().default(300),
    line_width: z.coerce.number().default(2),
    line_color: z.string().default('#2563eb'),
    background_color: z.string().default('#ffffff'),
    grid: z.boolean().default(true),
    grid_alpha: z.coerce.number().default(0.3),
    title: z.string().default(''),
    xlabel: z.string().default(''),
    ylabel: z.string().default(''),
    zlabel: z.string().default(''),
    font_size: z.coerce.number().default(12),
    style: z.enum(['default', 'seaborn', 'ggplot', 'dark_background', 'bmh']).default('default'),
    format: z.enum(['png', 'svg', 'pdf']).default('png'),
    colormap: z.string().default('viridis'),
    marker_style: z.enum(['none', 'o', 's', '^', 'v', 'D', '*']).default('none'),
    marker_size: z.coerce.number().default(4)
});

type EquationForm = z.infer<typeof equationSchema>;
type CsvForm = z.infer<typeof csvSchema>;

export default function Plot3DPage() {
    const [plotUrl, setPlotUrl] = useState<string | null>(null);
    const [lastResponse, setLastResponse] = useState<any>(null);
    const [equationMode, setEquationMode] = useState(true);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const { toast } = useToast();
    const eqForm = useForm<EquationForm>({
        resolver: zodResolver(equationSchema),
        defaultValues: {
            equation: 'sin(x)*cos(y)',
            x_min: -5,
            x_max: 5,
            y_min: -5,
            y_max: 5,
            resolution: 80,
            width: 1200,
            height: 800,
            dpi: 300,
            line_width: 2,
            line_color: '#2563eb',
            background_color: '#ffffff',
            grid: true,
            grid_alpha: 0.3,
            title: '',
            xlabel: '',
            ylabel: '',
            zlabel: '',
            font_size: 12,
            style: 'default',
            format: 'png',
            colormap: 'viridis'
        }
    });
    const csvForm = useForm<CsvForm>({
        resolver: zodResolver(csvSchema),
        defaultValues: {
            x_col: '',
            y_col: '',
            z_col: '',
            width: 1200,
            height: 800,
            dpi: 300,
            line_width: 2,
            line_color: '#2563eb',
            background_color: '#ffffff',
            grid: true,
            grid_alpha: 0.3,
            title: '',
            xlabel: '',
            ylabel: '',
            zlabel: '',
            font_size: 12,
            style: 'default',
            format: 'png',
            colormap: 'viridis',
            marker_style: 'none',
            marker_size: 4
        }
    });
    const [loading, setLoading] = useState(false);

    const onSubmitEquation = async (data: EquationForm) => {
        setLoading(true);
        try {
            const resp = await api.post('/simulation/plot3d', {
                mode: '3d_surface',
                equation: data.equation,
                x_min: data.x_min,
                x_max: data.x_max,
                y_min: data.y_min,
                y_max: data.y_max,
                resolution: data.resolution,
                // Plot customization
                width: data.width,
                height: data.height,
                dpi: data.dpi,
                line_width: data.line_width,
                line_color: data.line_color,
                background_color: data.background_color,
                grid: data.grid,
                grid_alpha: data.grid_alpha,
                title: data.title,
                xlabel: data.xlabel,
                ylabel: data.ylabel,
                zlabel: data.zlabel,
                font_size: data.font_size,
                style: data.style,
                format: data.format,
                colormap: data.colormap
            });
            const j = resp.data;
            const url = j.html_url || j.png_url || j.svg_url || j.pdf_url || j.plot_url || null;
            if (url) {
                setPlotUrl(url);
                setLastResponse(j);
                const isInteractive = url.includes('.html');
                toast({
                    title: isInteractive ? 'Interactive 3D plot generated' : 'High-resolution 3D plot generated',
                    description: isInteractive ? 'Rotate, zoom, and explore your 3D surface' : `${data.width}x${data.height} at ${data.dpi} DPI`
                });
            } else {
                setPlotUrl(null);
                const msg = j.error || j.message || 'Server did not return a plot. Check your equation.';
                toast({ variant: 'destructive', title: '3D plot failed', description: msg });
                console.error('Plot3D: server response without url', j);
            }
        } catch (e: any) {
            toast({ variant: 'destructive', title: '3D plot failed', description: e?.message || String(e) });
        } finally {
            setLoading(false);
        }
    };

    const insertTokenToEquation = (snippet: string) => {
        const current = eqForm.getValues('equation') || '';
        const withToken = current ? `${current} ${snippet}` : snippet;
        eqForm.setValue('equation', withToken);
    };

    const swapXYColumns = () => {
        const currentX = csvForm.getValues('x_col');
        const currentY = csvForm.getValues('y_col');

        if (!currentX || !currentY) {
            toast({ variant: 'destructive', title: 'Cannot swap', description: 'Both X and Y columns must be selected' });
            return;
        }

        // Swap the values
        csvForm.setValue('x_col', currentY);
        csvForm.setValue('y_col', currentX);

        // Also swap the labels if they match the column names
        const currentXLabel = csvForm.getValues('xlabel');
        const currentYLabel = csvForm.getValues('ylabel');

        if (currentXLabel === currentX || currentXLabel === '') {
            csvForm.setValue('xlabel', currentY);
        }
        if (currentYLabel === currentY || currentYLabel === '') {
            csvForm.setValue('ylabel', currentX);
        }

        // Update title if it's auto-generated
        const currentTitle = csvForm.getValues('title');
        if (currentTitle === `${currentY} vs ${currentX}` || currentTitle === '') {
            csvForm.setValue('title', `${currentX} vs ${currentY}`);
        }

        toast({
            title: 'Axes swapped',
            description: `X-axis: ${currentY} → Y-axis: ${currentX}`
        });

        // If there's already a file loaded, regenerate the plot automatically
        const fileData = csvForm.getValues('file');
        if (fileData && fileData[0] && plotUrl) {
            const formData = csvForm.getValues();
            onSubmitCsv({
                ...formData,
                x_col: currentY,
                y_col: currentX
            });
        }
    };

    const onSubmitCsv = async (data: CsvForm) => {
        setLoading(true);
        const formData = new FormData();

        if (data.file && data.file[0]) {
            formData.append('mode', 'csv');
            formData.append('file', data.file[0]);
            formData.append('x_col', data.x_col);
            formData.append('y_col', data.y_col);
            formData.append('z_col', data.z_col);

            // Add customization parameters
            formData.append('width', data.width?.toString() || '1200');
            formData.append('height', data.height?.toString() || '800');
            formData.append('dpi', data.dpi?.toString() || '300');
            formData.append('format', data.format || 'png');
            formData.append('style', data.style || 'default');
            formData.append('line_color', data.line_color || '#2563eb');
            formData.append('background_color', data.background_color || '#ffffff');
            formData.append('line_width', data.line_width?.toString() || '2');
            formData.append('marker_style', data.marker_style || 'none');
            formData.append('marker_size', data.marker_size?.toString() || '4');
            formData.append('font_size', data.font_size?.toString() || '12');
            formData.append('title', data.title || '');
            formData.append('xlabel', data.xlabel || '');
            formData.append('ylabel', data.ylabel || '');
            formData.append('zlabel', data.zlabel || '');
            formData.append('grid', data.grid ? 'true' : 'false');
            formData.append('grid_alpha', data.grid_alpha?.toString() || '0.3');
            formData.append('colormap', data.colormap || 'viridis');

            try {
                const response = await fetch('http://localhost:5000/simulation/plot_csv', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();

                    // Prioritize interactive HTML over static images
                    const url = result.html_url || result.png_url || result.svg_url || result.pdf_url || null;
                    if (url) {
                        setPlotUrl(url);
                        setLastResponse(result);
                        toast({ title: 'Interactive CSV 3D plot generated', description: `${data.width}x${data.height} with rotation and zoom capabilities` });
                    } else {
                        throw new Error('No plot URL returned from server');
                    }
                } else {
                    const errorText = await response.text();
                    let errorMessage = 'Failed to generate 3D plot';
                    try {
                        const errorJson = JSON.parse(errorText);
                        errorMessage = errorJson.error || errorMessage;
                    } catch {
                        errorMessage = errorText || errorMessage;
                    }
                    console.error('CSV 3D Plot Error:', errorMessage);
                    toast({ variant: 'destructive', title: '3D plot failed', description: errorMessage });
                    throw new Error(errorMessage);
                }
            } catch (error: any) {
                console.error('Error uploading CSV for 3D plot:', error);
                toast({ variant: 'destructive', title: 'CSV Upload Error', description: error?.message || String(error) });
            }
        }
        setLoading(false);
    };

    // Parse CSV header and a few sample rows to auto-detect numeric columns.
    const handleCsvFileChange = (files: FileList | null) => {
        if (!files || files.length === 0) return;
        const file = files[0];
        // set the raw file into the form
        csvForm.setValue('file', files as any);

        const reader = new FileReader();
        reader.onload = () => {
            const text = String(reader.result || '');
            const lines = text.split(/\r?\n/).filter(Boolean);
            if (lines.length === 0) return;
            const headerLine = lines[0];
            // simple CSV split - handles basic cases
            const headers = headerLine.split(',').map(h => h.replace(/^['\"]|['\"]$/g, '').trim());
            const sample = lines.slice(1, 11);
            const numericCounts = headers.map(() => 0);
            for (const line of sample) {
                const cols = line.split(',');
                for (let i = 0; i < headers.length; i++) {
                    const v = (cols[i] || '').trim();
                    if (v !== '') {
                        const n = Number(v.replace(/[^0-9eE+\-.]/g, ''));
                        if (!Number.isNaN(n) && Number.isFinite(n)) numericCounts[i]++;
                    }
                }
            }

            const lname = headers.map(h => h.toLowerCase());
            const findIndexByNames = (names: string[]) => names.reduce((acc, name) => acc >= 0 ? acc : lname.findIndex(h => h === name), -1);

            let xi = findIndexByNames(['x', 'time', 't']);
            let yi = findIndexByNames(['y', 'value', 'v']);
            let zi = findIndexByNames(['z', 'z_value', 'zvalue', 'value2']);

            // fallback: pick top numeric columns
            const sorted = numericCounts.map((c, i) => ({ c, i })).sort((a, b) => b.c - a.c).map(o => o.i);
            const pickNext = (exclude: number[]) => sorted.find(i => !exclude.includes(i)) ?? -1;

            if (xi < 0) xi = pickNext([]);
            if (yi < 0) yi = pickNext([xi]);
            if (zi < 0) zi = pickNext([xi, yi]);

            // ensure indices are valid
            xi = xi >= 0 && xi < headers.length ? xi : 0;
            yi = yi >= 0 && yi < headers.length ? yi : Math.min(1, headers.length - 1);
            zi = zi >= 0 && zi < headers.length ? zi : Math.min(2, headers.length - 1);

            const x_col = headers[xi] ?? headers[0];
            const y_col = headers[yi] ?? headers[1] ?? headers[0];
            const z_col = headers[zi] ?? headers[2] ?? headers[0];

            csvForm.setValue('x_col', x_col);
            csvForm.setValue('y_col', y_col);
            csvForm.setValue('z_col', z_col);

            // auto-submit with current form values
            const currentValues = csvForm.getValues();
            onSubmitCsv({
                ...currentValues,
                file: files as any,
                x_col,
                y_col,
                z_col
            });
        };
        reader.readAsText(file);
    };

    return (
        <div className="max-w-7xl mx-auto">
            <div className="text-center mb-6">
                <h1 className="text-3xl font-bold">3D Interactive Plotter</h1>
                <p className="text-muted-foreground">Create interactive 3D surface plots with rotation, zoom, and exploration capabilities</p>
            </div>

            <div className="space-y-6">
                {/* Input Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>{equationMode ? '3D Surface Equation' : 'CSV 3D Plot'}</CardTitle>
                        <CardDescription>{equationMode ? 'Enter an expression in x and y (e.g., sin(x)*cos(y))' : 'Upload CSV with x, y, z columns'}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="mb-4">
                            <Button variant="ghost" onClick={() => setEquationMode(!equationMode)}>
                                {equationMode ? 'Switch to CSV' : 'Switch to Equation'}
                            </Button>
                        </div>

                        {equationMode ? (
                            <Form {...eqForm}>
                                <form onSubmit={eqForm.handleSubmit(onSubmitEquation)}>
                                    <FormField control={eqForm.control} name="equation" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>3D Surface Equation</FormLabel>
                                            <FormControl><Input {...field} /></FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )} />
                                    <div className="mt-2">
                                        <MathTokenPicker onInsert={insertTokenToEquation} />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 mt-2">
                                        <FormField control={eqForm.control} name="x_min" render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>X Min</FormLabel>
                                                <FormControl><Input type="number" {...field} /></FormControl>
                                            </FormItem>
                                        )} />
                                        <FormField control={eqForm.control} name="x_max" render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>X Max</FormLabel>
                                                <FormControl><Input type="number" {...field} /></FormControl>
                                            </FormItem>
                                        )} />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 mt-2">
                                        <FormField control={eqForm.control} name="y_min" render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Y Min</FormLabel>
                                                <FormControl><Input type="number" {...field} /></FormControl>
                                            </FormItem>
                                        )} />
                                        <FormField control={eqForm.control} name="y_max" render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Y Max</FormLabel>
                                                <FormControl><Input type="number" {...field} /></FormControl>
                                            </FormItem>
                                        )} />
                                    </div>
                                    <FormField control={eqForm.control} name="resolution" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Resolution (grid points)</FormLabel>
                                            <FormControl><Input type="number" {...field} /></FormControl>
                                        </FormItem>
                                    )} />

                                    {/* Advanced Customization */}
                                    <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced} className="mt-4">
                                        <CollapsibleTrigger asChild>
                                            <Button variant="outline" className="w-full mb-4">
                                                <Settings className="mr-2 h-4 w-4" />
                                                Advanced Plot Options
                                                <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                                            </Button>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent className="space-y-4">
                                            {/* Size & Quality */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <ImageIcon className="h-4 w-4" />
                                                    <Label className="font-semibold">Size & Quality</Label>
                                                </div>
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={eqForm.control} name="width" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Width (px)</FormLabel>
                                                            <FormControl><Input type="number" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="height" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Height (px)</FormLabel>
                                                            <FormControl><Input type="number" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={eqForm.control} name="dpi" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>DPI</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={(value) => field.onChange(Number(value))} value={field.value?.toString()}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="150">150 DPI (Web)</SelectItem>
                                                                        <SelectItem value="300">300 DPI (Print)</SelectItem>
                                                                        <SelectItem value="600">600 DPI (High-res)</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="format" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Format</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={field.onChange} value={field.value}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="png">PNG (Raster)</SelectItem>
                                                                        <SelectItem value="svg">SVG (Vector)</SelectItem>
                                                                        <SelectItem value="pdf">PDF (Vector)</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                            </div>

                                            {/* Styling */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <Palette className="h-4 w-4" />
                                                    <Label className="font-semibold">Styling</Label>
                                                </div>
                                                <FormField control={eqForm.control} name="style" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Plot Style</FormLabel>
                                                        <FormControl>
                                                            <Select onValueChange={field.onChange} value={field.value}>
                                                                <SelectTrigger>
                                                                    <SelectValue />
                                                                </SelectTrigger>
                                                                <SelectContent>
                                                                    <SelectItem value="default">Default</SelectItem>
                                                                    <SelectItem value="seaborn">Seaborn</SelectItem>
                                                                    <SelectItem value="ggplot">GGPlot</SelectItem>
                                                                    <SelectItem value="dark_background">Dark Theme</SelectItem>
                                                                    <SelectItem value="bmh">BMH</SelectItem>
                                                                </SelectContent>
                                                            </Select>
                                                        </FormControl>
                                                    </FormItem>
                                                )} />
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={eqForm.control} name="colormap" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Color Map</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={field.onChange} value={field.value}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="viridis">Viridis</SelectItem>
                                                                        <SelectItem value="plasma">Plasma</SelectItem>
                                                                        <SelectItem value="inferno">Inferno</SelectItem>
                                                                        <SelectItem value="magma">Magma</SelectItem>
                                                                        <SelectItem value="coolwarm">Cool Warm</SelectItem>
                                                                        <SelectItem value="jet">Jet</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="background_color" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Background</FormLabel>
                                                            <FormControl>
                                                                <div className="flex gap-2">
                                                                    <Input type="color" {...field} className="w-12 h-10 p-1" />
                                                                    <Input {...field} placeholder="#ffffff" />
                                                                </div>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <FormField control={eqForm.control} name="font_size" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Font Size</FormLabel>
                                                        <FormControl><Input type="number" {...field} /></FormControl>
                                                    </FormItem>
                                                )} />
                                            </div>

                                            {/* Labels & Grid */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <FileText className="h-4 w-4" />
                                                    <Label className="font-semibold">Labels & Grid</Label>
                                                </div>
                                                <FormField control={eqForm.control} name="title" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Plot Title</FormLabel>
                                                        <FormControl><Input {...field} placeholder="Enter plot title" /></FormControl>
                                                    </FormItem>
                                                )} />
                                                <div className="grid grid-cols-3 gap-2">
                                                    <FormField control={eqForm.control} name="xlabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>X-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="x" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="ylabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Y-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="y" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="zlabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Z-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="z" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <FormField control={eqForm.control} name="grid" render={({ field }) => (
                                                        <FormItem className="flex items-center space-x-2">
                                                            <FormControl>
                                                                <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                                                            </FormControl>
                                                            <FormLabel>Show Grid</FormLabel>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={eqForm.control} name="grid_alpha" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Grid Opacity</FormLabel>
                                                            <FormControl><Input type="number" step="0.1" min="0" max="1" {...field} className="w-20" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                            </div>
                                        </CollapsibleContent>
                                    </Collapsible>

                                    <div className="mt-4">
                                        <Button type="submit" disabled={loading} className="w-full">
                                            {loading ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : <Zap className="h-4 w-4 mr-2" />}
                                            Generate Interactive 3D Plot
                                        </Button>
                                    </div>
                                </form>
                            </Form>
                        ) : (
                            <Form {...csvForm}>
                                <form onSubmit={csvForm.handleSubmit(onSubmitCsv)}>
                                    <FormField control={csvForm.control} name="file" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>CSV File</FormLabel>
                                            <FormControl>
                                                <input type="file" accept=".csv" onChange={(e) => { field.onChange(e.target.files); handleCsvFileChange(e.target.files); }} />
                                            </FormControl>
                                        </FormItem>
                                    )} />
                                    <FormField control={csvForm.control} name="x_col" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>X Column Name</FormLabel>
                                            <FormControl><Input {...field} /></FormControl>
                                        </FormItem>
                                    )} />
                                    <FormField control={csvForm.control} name="y_col" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Y Column Name</FormLabel>
                                            <FormControl><Input {...field} /></FormControl>
                                        </FormItem>
                                    )} />

                                    {/* Swap X/Y Button */}
                                    <div className="flex justify-center mt-2 mb-2">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="sm"
                                            onClick={swapXYColumns}
                                            className="flex items-center gap-2"
                                            disabled={!csvForm.getValues('x_col') || !csvForm.getValues('y_col')}
                                        >
                                            <ArrowLeftRight className="h-4 w-4" />
                                            Swap X ↔ Y Axes
                                        </Button>
                                    </div>

                                    <FormField control={csvForm.control} name="z_col" render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Z Column Name</FormLabel>
                                            <FormControl><Input {...field} /></FormControl>
                                        </FormItem>
                                    )} />

                                    {/* Advanced Customization for CSV */}
                                    <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced} className="mt-4">
                                        <CollapsibleTrigger asChild>
                                            <Button variant="outline" className="w-full mb-4">
                                                <Settings className="mr-2 h-4 w-4" />
                                                Advanced Plot Options
                                                <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                                            </Button>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent className="space-y-4">
                                            {/* Size & Quality */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <ImageIcon className="h-4 w-4" />
                                                    <Label className="font-semibold">Size & Quality</Label>
                                                </div>
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={csvForm.control} name="width" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Width (px)</FormLabel>
                                                            <FormControl><Input type="number" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="height" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Height (px)</FormLabel>
                                                            <FormControl><Input type="number" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={csvForm.control} name="dpi" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>DPI</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={(value) => field.onChange(Number(value))} value={field.value?.toString()}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="150">150 DPI (Web)</SelectItem>
                                                                        <SelectItem value="300">300 DPI (Print)</SelectItem>
                                                                        <SelectItem value="600">600 DPI (High-res)</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="format" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Format</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={field.onChange} value={field.value}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="png">PNG (Raster)</SelectItem>
                                                                        <SelectItem value="svg">SVG (Vector)</SelectItem>
                                                                        <SelectItem value="pdf">PDF (Vector)</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                            </div>

                                            {/* Styling */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <Palette className="h-4 w-4" />
                                                    <Label className="font-semibold">Styling</Label>
                                                </div>
                                                <FormField control={csvForm.control} name="style" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Plot Style</FormLabel>
                                                        <FormControl>
                                                            <Select onValueChange={field.onChange} value={field.value}>
                                                                <SelectTrigger>
                                                                    <SelectValue />
                                                                </SelectTrigger>
                                                                <SelectContent>
                                                                    <SelectItem value="default">Default</SelectItem>
                                                                    <SelectItem value="seaborn">Seaborn</SelectItem>
                                                                    <SelectItem value="ggplot">GGPlot</SelectItem>
                                                                    <SelectItem value="dark_background">Dark Theme</SelectItem>
                                                                    <SelectItem value="bmh">BMH</SelectItem>
                                                                </SelectContent>
                                                            </Select>
                                                        </FormControl>
                                                    </FormItem>
                                                )} />
                                                <div className="grid grid-cols-2 gap-2">
                                                    <FormField control={csvForm.control} name="colormap" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Color Map</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={field.onChange} value={field.value}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="viridis">Viridis</SelectItem>
                                                                        <SelectItem value="plasma">Plasma</SelectItem>
                                                                        <SelectItem value="inferno">Inferno</SelectItem>
                                                                        <SelectItem value="magma">Magma</SelectItem>
                                                                        <SelectItem value="coolwarm">Cool Warm</SelectItem>
                                                                        <SelectItem value="jet">Jet</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="background_color" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Background</FormLabel>
                                                            <FormControl>
                                                                <div className="flex gap-2">
                                                                    <Input type="color" {...field} className="w-12 h-10 p-1" />
                                                                    <Input {...field} placeholder="#ffffff" />
                                                                </div>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <div className="grid grid-cols-3 gap-2">
                                                    <FormField control={csvForm.control} name="line_width" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Line Width</FormLabel>
                                                            <FormControl><Input type="number" step="0.5" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="marker_style" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Markers</FormLabel>
                                                            <FormControl>
                                                                <Select onValueChange={field.onChange} value={field.value}>
                                                                    <SelectTrigger>
                                                                        <SelectValue />
                                                                    </SelectTrigger>
                                                                    <SelectContent>
                                                                        <SelectItem value="none">None</SelectItem>
                                                                        <SelectItem value="o">Circle</SelectItem>
                                                                        <SelectItem value="s">Square</SelectItem>
                                                                        <SelectItem value="^">Triangle</SelectItem>
                                                                        <SelectItem value="D">Diamond</SelectItem>
                                                                        <SelectItem value="*">Star</SelectItem>
                                                                    </SelectContent>
                                                                </Select>
                                                            </FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="marker_size" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Marker Size</FormLabel>
                                                            <FormControl><Input type="number" {...field} /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <FormField control={csvForm.control} name="font_size" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Font Size</FormLabel>
                                                        <FormControl><Input type="number" {...field} /></FormControl>
                                                    </FormItem>
                                                )} />
                                            </div>

                                            {/* Labels & Grid */}
                                            <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <FileText className="h-4 w-4" />
                                                    <Label className="font-semibold">Labels & Grid</Label>
                                                </div>
                                                <FormField control={csvForm.control} name="title" render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Plot Title</FormLabel>
                                                        <FormControl><Input {...field} placeholder="Enter plot title" /></FormControl>
                                                    </FormItem>
                                                )} />
                                                <div className="grid grid-cols-3 gap-2">
                                                    <FormField control={csvForm.control} name="xlabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>X-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="x" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="ylabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Y-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="y" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="zlabel" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Z-axis Label</FormLabel>
                                                            <FormControl><Input {...field} placeholder="z" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <FormField control={csvForm.control} name="grid" render={({ field }) => (
                                                        <FormItem className="flex items-center space-x-2">
                                                            <FormControl>
                                                                <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                                                            </FormControl>
                                                            <FormLabel>Show Grid</FormLabel>
                                                        </FormItem>
                                                    )} />
                                                    <FormField control={csvForm.control} name="grid_alpha" render={({ field }) => (
                                                        <FormItem>
                                                            <FormLabel>Grid Opacity</FormLabel>
                                                            <FormControl><Input type="number" step="0.1" min="0" max="1" {...field} className="w-20" /></FormControl>
                                                        </FormItem>
                                                    )} />
                                                </div>
                                            </div>
                                        </CollapsibleContent>
                                    </Collapsible>

                                    <div className="mt-4">
                                        <Button type="submit" disabled={loading} className="w-full">
                                            {loading ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : <UploadCloud className="mr-2 h-4 w-4" />}
                                            Generate Interactive CSV 3D Plot
                                        </Button>
                                    </div>
                                </form>
                            </Form>
                        )}
                    </CardContent>
                </Card>

                {/* Output Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>3D Plot Output</CardTitle>
                        <CardDescription>Interactive 3D plot with rotation, zoom, and exploration capabilities</CardDescription>
                    </CardHeader>
                    <CardContent className="p-0">
                        {plotUrl ? (
                            plotUrl.endsWith('.html') ? (
                                <div className="w-full h-[600px] lg:h-[700px]">
                                    <iframe
                                        src={plotUrl}
                                        title="Interactive 3D Plot"
                                        className="w-full h-full border-0 rounded-lg"
                                        style={{ minHeight: '600px' }}
                                    />
                                </div>
                            ) : plotUrl.endsWith('.png') || plotUrl.endsWith('.svg') || plotUrl.endsWith('.pdf') ? (
                                <div className="p-6">
                                    <div className="relative w-full h-[500px]">
                                        <NextImage
                                            src={plotUrl}
                                            alt="3d-plot"
                                            fill
                                            style={{ objectFit: 'contain' }}
                                            unoptimized
                                        />
                                    </div>
                                </div>
                            ) : (
                                <div className="w-full h-[600px] lg:h-[700px]">
                                    <iframe
                                        src={plotUrl}
                                        title="Interactive 3D Plot"
                                        className="w-full h-full border-0 rounded-lg"
                                    />
                                </div>
                            )
                        ) : (
                            <div className="flex items-center justify-center h-[400px] p-6">
                                <div className="text-center">
                                    <p className="text-muted-foreground mb-4">Generate a 3D plot to see the interactive preview</p>
                                    <p className="text-sm text-muted-foreground">Interactive 3D plots support rotation, zoom, pan, and data exploration</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                    {plotUrl && (
                        <CardFooter>
                            <Button asChild><a href={plotUrl} target="_blank" rel="noreferrer"><Download className="mr-2 h-4 w-4" />Open</a></Button>
                        </CardFooter>
                    )}
                </Card>
            </div>
        </div>
    );
}
