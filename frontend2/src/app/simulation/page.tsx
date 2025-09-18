"use client";
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Calculator, Zap, Spline } from 'lucide-react';
import Image from 'next/image';

const simulationTypes = [
  {
    name: 'Custom Equation Plotter',
    description: 'Input your own mathematical equations and variables to generate custom plots and visualize functions.',
    link: '/simulation/custom',
    icon: <Calculator className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/math-graph/600/400',
    imageHint: 'math graph',
    disabled: false
  },
  {
    name: '2D Plotter (Equation or CSV)',
    description: 'Generate 2D plots either from equations or by uploading a CSV with x/y columns.',
    link: '/simulation/plot2d',
    icon: <Spline className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/plot2d/600/400',
    imageHint: '2d plot',
    disabled: false
  },
  {
    name: '3D Plotter (Equation)',
    description: 'Interactive 3D surface or parametric plots based on user-provided expressions.',
    link: '/simulation/plot3d',
    icon: <Zap className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/plot3d/600/400',
    imageHint: '3d plot',
    disabled: false
  },
  {
    name: 'VPython (GlowScript) Simulations',
    description: 'Interactive VPython/GlowScript simulations (vector fields, orbits, presets).',
    link: '/simulation/vpython',
    icon: <Calculator className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/vpython/600/400',
    imageHint: 'vpython',
    disabled: false
  },
  {
    name: 'Pygame Particle Simulation',
    description: 'Headless Pygame particle sims — returns frames and optional GIFs.',
    link: '/simulation/pygame',
    icon: <Zap className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/pygame/600/400',
    imageHint: 'particles',
    disabled: false
  },
];

export default function SimulationPage() {
  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-headline font-bold">Physics Simulation Lab</h1>
        <p className="text-muted-foreground mt-2">Choose a simulation type to get started.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {simulationTypes.map((sim) => (
          <Card key={sim.name} className={`flex flex-col overflow-hidden transition-all duration-300 ${sim.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg hover:shadow-primary/20'}`}>
            <div className="relative h-48 w-full">
              <Image src={sim.image} alt={sim.name} layout="fill" objectFit="cover" data-ai-hint={sim.imageHint} />
            </div>
            <CardHeader className="flex-row gap-4 items-center">
              {sim.icon}
              <CardTitle>{sim.name}</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow">
              <CardDescription>{sim.description}</CardDescription>
            </CardContent>
            <CardContent>
              <Link href={sim.disabled ? '#' : sim.link} className={`flex items-center text-sm font-semibold ${sim.disabled ? 'text-muted-foreground' : 'text-primary hover:underline'}`}>
                {sim.disabled ? 'Coming Soon' : 'Launch Simulator'}
                {!sim.disabled && <ArrowRight className="ml-2 h-4 w-4" />}
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
