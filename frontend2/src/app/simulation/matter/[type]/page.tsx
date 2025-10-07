"use client";
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import MatterSimulation from '@/components/MatterSimulation';

// Add all possible simulation types for static export
export function generateStaticParams() {
    return [
        { type: 'pendulum' },
        { type: 'collision' },
        { type: 'projectile' },
    ];
}

const simulationTypes = {
    'pendulum': 'Pendulum',
    'collision': 'Collision',
    'projectile': 'Projectile Motion'
};

export default function MatterSimulationPage() {
    const params = useParams();
    const simulationType = params.type as string;

    const simulationName = simulationTypes[simulationType as keyof typeof simulationTypes];

    if (!simulationName) {
        return (
            <div className="text-center">
                <h1 className="text-2xl font-bold mb-4">Simulation Not Found</h1>
                <Link href="/simulation/matter">
                    <Button>Back to Simulations</Button>
                </Link>
            </div>
        );
    }

    return (
        <div>
            <div className="flex items-center gap-4 mb-6">
                <Link href="/simulation/matter">
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Simulations
                    </Button>
                </Link>
                <h1 className="text-3xl font-headline font-bold">
                    {simulationName} Simulation
                </h1>
            </div>

            <MatterSimulation simulationType={simulationType} />
        </div>
    );
}