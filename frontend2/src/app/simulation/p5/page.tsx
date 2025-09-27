"use client";
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const simulationTypes = [
    {
        id: 'electric_field',
        name: 'Electric Field',
        description: 'Interactive electric field visualization showing field lines, equipotential surfaces, and charge interactions.'
    },
    {
        id: 'magnetic_field',
        name: 'Magnetic Field',
        description: 'Magnetic field simulation demonstrating Lorentz force and cyclotron motion of charged particles.'
    },
    {
        id: 'wave_motion',
        name: 'Wave Motion',
        description: 'Traveling and standing wave simulations with adjustable frequency, amplitude, and wavelength.'
    },
    {
        id: 'oscillation',
        name: 'Oscillation',
        description: 'Simple harmonic motion and coupled oscillator systems with phase relationships.'
    },
    {
        id: 'em_wave',
        name: 'Electromagnetic Wave',
        description: 'Combined electric and magnetic field propagation showing wave characteristics and polarization.'
    }
];

export default function P5PhysicsPage() {

    return (
        <div>
            <div className="flex items-center gap-4 mb-8">
                <Link href="/simulation">
                    <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <ArrowLeft className="h-4 w-4" />
                        Back to Simulation Lab
                    </Button>
                </Link>
                <div>
                    <h1 className="text-4xl font-headline font-bold">p5.js Electromagnetic Physics</h1>
                    <p className="text-muted-foreground mt-2">
                        Interactive electromagnetic and wave physics simulations powered by p5.js
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {simulationTypes.map((sim) => (
                    <Card
                        key={sim.id}
                        className="transition-all duration-300 hover:shadow-lg hover:shadow-primary/20"
                    >
                        <CardHeader>
                            <CardTitle>{sim.name}</CardTitle>
                            <CardDescription>{sim.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Link href={`/simulation/p5/${sim.id}`}>
                                <Button className="w-full">
                                    Launch {sim.name} Simulation
                                </Button>
                            </Link>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}