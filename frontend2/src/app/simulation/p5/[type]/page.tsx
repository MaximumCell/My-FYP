"use client";
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import P5Simulation from '@/components/P5Simulation';

const simulationTypes = {
    'electric_field': 'Electric Field',
    'magnetic_field': 'Magnetic Field',
    'wave_motion': 'Wave Motion',
    'oscillation': 'Oscillation',
    'em_wave': 'Electromagnetic Wave'
};

export default function P5SimulationPage() {
    const params = useParams();
    const simulationType = params.type as string;

    const simulationName = simulationTypes[simulationType as keyof typeof simulationTypes];

    if (!simulationName) {
        return (
            <div className="text-center">
                <h1 className="text-2xl font-bold mb-4">Simulation Not Found</h1>
                <Link href="/simulation/p5">
                    <Button>Back to Simulations</Button>
                </Link>
            </div>
        );
    }

    return (
        <div>
            <div className="flex items-center gap-4 mb-6">
                <Link href="/simulation/p5">
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

            <P5Simulation simulationType={simulationType} />
        </div>
    );
}