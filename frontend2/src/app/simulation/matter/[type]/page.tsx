import ClientMatterSimulationPage from './ClientMatterSimulationPage';

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

export default function MatterSimulationPage({ params }: { params: { type: string } }) {
    const simulationType = params.type;
    const simulationName = simulationTypes[simulationType as keyof typeof simulationTypes];

    if (!simulationName) {
        return (
            <div className="text-center">
                <h1 className="text-2xl font-bold mb-4">Simulation Not Found</h1>
                <a href="/simulation/matter">
                    <button>Back to Simulations</button>
                </a>
            </div>
        );
    }

    // Render the client component for the simulation
    return <ClientMatterSimulationPage simulationType={simulationType} simulationName={simulationName} />;
}