"use client";
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Calculator, Zap, Spline, Atom, Move } from 'lucide-react';
import Image from 'next/image';

const simulationTypes = [
  {
    name: 'Custom Equation Plotter',
    description: 'Input your own mathematical equations and variables to generate custom plots and visualize functions.',
    link: '/simulation/custom',
    icon: <Calculator className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&h=600&fit=crop&crop=center',
    imageHint: 'mathematical equations and graphs',
    disabled: false
  },
  {
    name: '2D Plotter (Equation or CSV)',
    description: 'Generate 2D plots either from equations or by uploading a CSV with x/y columns.',
    link: '/simulation/plot2d',
    icon: <Spline className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop&crop=center',
    imageHint: '2D data visualization and charts',
    disabled: false
  },
  {
    name: '3D Plotter (Equation)',
    description: 'Interactive 3D surface or parametric plots based on user-provided expressions.',
    link: '/simulation/plot3d',
    icon: <Zap className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&h=600&fit=crop&crop=center',
    imageHint: '3D visualization and mathematical surfaces',
    disabled: false
  },
  {
    name: 'Matter.js Mechanical Physics',
    description: 'Interactive mechanical physics simulations including pendulums, collisions, springs, and projectile motion.',
    link: '/simulation/matter',
    icon: <Move className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800&h=600&fit=crop&crop=center',
    imageHint: 'mechanical physics and motion',
    disabled: false
  },
  {
    name: 'p5.js Electromagnetic Physics',
    description: 'Electromagnetic and wave physics simulations with electric fields, magnetic fields, and wave motion.',
    link: '/simulation/p5',
    icon: <Atom className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&h=600&fit=crop&crop=center',
    imageHint: 'electromagnetic fields and energy',
    disabled: false
  },
  {
    name: 'Pygame Particle Simulation',
    description: 'Headless Pygame particle sims — returns frames and optional GIFs.',
    link: '/simulation/pygame',
    icon: <Zap className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&h=600&fit=crop&crop=center',
    imageHint: 'particle physics and cosmic effects',
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
          <Card key={sim.name} className={`group flex flex-col overflow-hidden transition-all duration-300 border-border/50 hover:border-primary/20 ${sim.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1'}`}>
            <div className="relative h-48 w-full overflow-hidden">
              <Image
                src={sim.image}
                alt={sim.name}
                fill
                style={{ objectFit: 'cover' }}
                data-ai-hint={sim.imageHint}
                className="transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
            <CardHeader className="flex-row gap-4 items-center">
              <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors duration-300">
                {sim.icon}
              </div>
              <CardTitle className="group-hover:text-primary transition-colors duration-300">{sim.name}</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow">
              <CardDescription className="leading-relaxed">{sim.description}</CardDescription>
            </CardContent>
            <CardContent className="pt-0">
              <Link
                href={sim.disabled ? '#' : sim.link}
                className={`flex items-center justify-between w-full p-3 rounded-lg text-sm font-semibold transition-all duration-300 ${sim.disabled
                    ? 'text-muted-foreground bg-muted/30'
                    : 'text-primary hover:bg-primary hover:text-primary-foreground group-hover:shadow-md'
                  }`}
              >
                <span>{sim.disabled ? 'Coming Soon' : 'Launch Simulator'}</span>
                {!sim.disabled && <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />}
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
