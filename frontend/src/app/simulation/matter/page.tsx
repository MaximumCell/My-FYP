"use client";
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const simulationTypes = [
    {
        id: 'pendulum',
        name: 'Pendulum',
        description: 'Simple and compound pendulum simulations with adjustable length, mass, and gravity.'
    },
    {
        id: 'collision',
        name: 'Collision',
        description: 'Elastic and inelastic collision simulations with conservation of momentum and energy.'
    },
    {
        id: 'projectile',
        name: 'Projectile Motion',
        description: 'Ballistic trajectory simulations with air resistance and gravity effects.'
    }
];

export default function MatterPhysicsPage() {

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
                    <h1 className="text-4xl font-headline font-bold">Matter.js Mechanical Physics</h1>
                    <p className="text-muted-foreground mt-2">
                        Interactive mechanical physics simulations powered by Matter.js
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                            <Link href={`/simulation/matter/${sim.id}`}>
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