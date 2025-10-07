"use client";
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import MatterSimulation from '@/components/MatterSimulation';

export default function ClientMatterSimulationPage({ simulationType, simulationName }: { simulationType: string, simulationName: string }) {
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
