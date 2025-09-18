"use client";

import { useState } from 'react';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Image from 'next/image';
import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useRunSimulation } from '@/hooks/use-simulation';
import { useToast } from '@/hooks/use-toast';
import type { ApiError } from '@/types/api';
import { Loader2, PlusCircle, Trash2, Download, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';

const predefinedEquations = [
  { label: "Linear Motion", value: "Linear Motion (y = m*x + c)", defaultVars: [{ key: 'm', value: 2 }, { key: 'c', value: 1 }] },
  { label: "Quadratic Motion", value: "Quadratic Motion (y = a*x^2 + b*x + c)", defaultVars: [{ key: 'a', value: 1 }, { key: 'b', value: -5 }, { key: 'c', value: 6 }] },
  { label: "Simple Harmonic Motion", value: "SHM (y = A*sin(w*x + p))", defaultVars: [{ key: 'A', value: 5 }, { key: 'w', value: 1 }, { key: 'p', value: 0 }] },
];

const formSchema = z.object({
  equation: z.string().min(1, 'Equation is required.'),
  x_min: z.coerce.number(),
  x_max: z.coerce.number(),
  variables: z.array(z.object({
    key: z.string().min(1, 'Key is required.'),
    value: z.coerce.number(),
  })),
}).refine(data => data.x_max > data.x_min, {
  message: "Max X must be greater than Min X",
  path: ["x_max"],
});

type SimulationFormValues = z.infer<typeof formSchema>;

export default function CustomSimulationPage() {
  const [simulationResult, setSimulationResult] = useState<{ plotUrl: string, equation: string } | null>(null);
  const { toast } = useToast();
  const simulationMutation = useRunSimulation();

  const form = useForm<SimulationFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      equation: predefinedEquations[0].value,
      x_min: 0,
      x_max: 10,
      variables: predefinedEquations[0].defaultVars,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "variables",
  });

  const handleEquationChange = (value: string) => {
    form.setValue('equation', value);
    const selectedEq = predefinedEquations.find(eq => eq.value === value);
    if (selectedEq) {
      form.setValue('variables', selectedEq.defaultVars);
    } else {
      form.setValue('variables', [{ key: '', value: 0 }]);
    }
  };

  const onSubmit = (data: SimulationFormValues) => {
    const variablesObject = data.variables.reduce((obj, item) => {
      obj[item.key] = item.value;
      return obj;
    }, {} as Record<string, number>);

    // templates for predefined labels -> expressions (match backend PREDEFINED_EQUATIONS)
    const PREDEFINED_EXPR: Record<string, string> = {
      "Linear Motion (y = m*x + c)": "m*x + c",
      "Quadratic Motion (y = a*x^2 + b*x + c)": "a*x**2 + b*x + c",
      "SHM (y = A*sin(w*x + p))": "A*sin(w*x + p)",
      "Simple Harmonic Motion": "A*sin(w*x + p)",
    };

    let exprToSend = '';
    if (PREDEFINED_EXPR[data.equation]) {
      exprToSend = PREDEFINED_EXPR[data.equation];
    } else {
      // assume user provided direct math expression
      exprToSend = data.equation;
    }

    // substitute variable values (word-boundary replacement)
    Object.entries(variablesObject).forEach(([k, v]) => {
      try {
        const re = new RegExp(`\\b${k}\\b`, 'g');
        exprToSend = exprToSend.replace(re, String(v));
      } catch (e) {
        // ignore bad regex
      }
    });

    // send the concrete expression to the backend for equation plotting
    simulationMutation.mutate({ mode: 'equation', equation: exprToSend, x_min: data.x_min, x_max: data.x_max }, {
      onSuccess: (result) => {
        const plotUrl = result.png_url || result.html_url || result.plot_url || '';
        setSimulationResult({
          plotUrl,
          equation: result.equation || exprToSend,
        });
        toast({ title: 'Simulation complete!' });
      },
      onError: (error: ApiError) => {
        toast({ variant: 'destructive', title: 'Simulation failed', description: error.error });
      }
    });
  };

  const handleDownloadPlot = () => {
    if (simulationResult?.plotUrl) {
      const link = document.createElement('a');
      link.href = simulationResult.plotUrl;
      link.setAttribute('download', 'simulation_plot.png');
      link.setAttribute('target', '_blank'); // For cross-origin safety
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="flex flex-col items-center">
      <div className="mb-6 w-full max-w-5xl">
        <Link href="/simulation" className="flex items-center text-sm text-primary hover:underline"><ArrowLeft className="mr-2 h-4 w-4" />Back to Simulations</Link>
      </div>

      <div className="text-center mb-8">
        <h1 className="text-4xl font-headline font-bold">Custom Equation Simulator</h1>
        <p className="text-muted-foreground mt-2">Visualize any equation and see physics in action.</p>
      </div>

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <CardHeader>
                <CardTitle>Simulation Parameters</CardTitle>
                <CardDescription>Define your equation and variables to run the simulation.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <FormField
                  control={form.control}
                  name="equation"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Equation</FormLabel>
                      <Select onValueChange={(value) => { field.onChange(value); handleEquationChange(value); }} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a predefined equation" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {predefinedEquations.map(eq => (
                            <SelectItem key={eq.value} value={eq.value}>{eq.label}</SelectItem>
                          ))}
                          <SelectItem value="custom">Custom Equation</SelectItem>
                        </SelectContent>
                      </Select>
                      {form.watch('equation') === 'custom' &&
                        <Input placeholder="e.g. 2*x + 1" className="mt-2" {...field} />
                      }
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="x_min" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Min X</FormLabel>
                      <FormControl><Input type="number" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                  />
                  <FormField control={form.control} name="x_max" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Max X</FormLabel>
                      <FormControl><Input type="number" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                  />
                </div>

                <div>
                  <FormLabel>Variables</FormLabel>
                  <div className="space-y-2 mt-2">
                    {fields.map((field, index) => (
                      <div key={field.id} className="flex items-center gap-2">
                        <Controller render={({ field }) => <Input placeholder="key" {...field} />} name={`variables.${index}.key`} control={form.control} />
                        <Controller render={({ field }) => <Input type="number" placeholder="value" {...field} />} name={`variables.${index}.value`} control={form.control} />
                        <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    ))}
                    <Button type="button" variant="outline" size="sm" onClick={() => append({ key: '', value: 0 })}>
                      <PlusCircle className="mr-2 h-4 w-4" /> Add Variable
                    </Button>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit" disabled={simulationMutation.isPending}>
                  {simulationMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Run Simulation
                </Button>
              </CardFooter>
            </form>
          </Form>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Simulation Output</CardTitle>
            <CardDescription>The generated plot will appear here.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center min-h-[400px] bg-muted/50 rounded-lg">
            {simulationMutation.isPending ? (
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            ) : simulationResult ? (
              <div className="w-full space-y-4">
                <div className="w-full">
                  {/* If backend returned a PNG URL, show as image; otherwise if HTML URL provided, embed in iframe */}
                  {simulationResult.plotUrl?.endsWith('.png') ? (
                    <div className="relative aspect-video w-full">
                      <Image src={simulationResult.plotUrl} alt="Simulation Plot" layout="fill" objectFit="contain" unoptimized />
                    </div>
                  ) : simulationResult.plotUrl ? (
                    <div className="w-full h-[480px]">
                      <iframe src={simulationResult.plotUrl} title="Simulation Plot" className="w-full h-full border" />
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No plot URL returned from backend.</p>
                  )}
                </div>
                <p className="text-center font-code bg-background p-2 rounded">
                  Equation: {simulationResult.equation}
                </p>
              </div>
            ) : (
              <p className="text-muted-foreground">Run a simulation to see the plot.</p>
            )}
          </CardContent>
          {simulationResult && (
            <CardFooter>
              <Button onClick={handleDownloadPlot} variant="secondary">
                <Download className="mr-2 h-4 w-4" />
                Download Plot
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  );
}
