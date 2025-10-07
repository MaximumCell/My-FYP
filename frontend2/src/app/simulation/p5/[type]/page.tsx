import ClientP5SimulationPage from './ClientP5SimulationPage';

// Add all possible simulation types for static export
export function generateStaticParams() {
    return [
        { type: 'electric_field' },
        { type: 'magnetic_field' },
        { type: 'wave_motion' },
        { type: 'oscillation' },
        { type: 'em_wave' },
    ];
}

const simulationTypes = {
    'electric_field': 'Electric Field',
    'magnetic_field': 'Magnetic Field',
    'wave_motion': 'Wave Motion',
    'oscillation': 'Oscillation',
    'em_wave': 'Electromagnetic Wave'
};

export default function P5SimulationPage({ params }: { params: { type: string } }) {
    const simulationType = params.type;
    const simulationName = simulationTypes[simulationType as keyof typeof simulationTypes];

    if (!simulationName) {
        return (
            <div className="text-center">
                <h1 className="text-2xl font-bold mb-4">Simulation Not Found</h1>
                <a href="/simulation/p5">
                    <button>Back to Simulations</button>
                </a>
            </div>
        );
    }

    // Render the client component for the simulation
    return <ClientP5SimulationPage simulationType={simulationType} simulationName={simulationName} />;
}