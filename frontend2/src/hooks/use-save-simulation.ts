import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';

interface SaveSimulationData {
    simulation_name: string;
    simulation_type: 'plot2d' | 'plot3d' | 'interactive-physics' | 'custom-equation' | 'projectile-motion' | 'electric-field' | 'wave-simulation' | 'other';
    description?: string;
    tags?: string[];
    config: {
        equation?: string;
        parameters: Record<string, any>;
        variables: string[];
        plot_type?: string;
        x_range?: number[];
        y_range?: number[];
        z_range?: number[];
    };
    execution_time: number;
    plot_title?: string;
    x_label?: string;
    y_label?: string;
    z_label?: string;
    is_public?: boolean;
    plot_html: string;
    plot_thumbnail?: string; // Base64 PNG thumbnail (optional)
}

interface UseSaveSimulationReturn {
    saveSimulation: (data: SaveSimulationData) => Promise<void>;
    isSaving: boolean;
    error: string | null;
}

export const useSaveSimulation = (): UseSaveSimulationReturn => {
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { toast } = useToast();

    const saveSimulation = async (data: SaveSimulationData) => {
        setIsSaving(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:5000/api/simulations/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': '68d6278f394fbc66b21a8403', // Your user ID - in production this would come from auth
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                toast({
                    title: 'Simulation saved successfully!',
                    description: `"${data.simulation_name}" has been saved to your account`,
                });
            } else {
                throw new Error(result.error?.message || 'Failed to save simulation');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
            setError(errorMessage);
            toast({
                variant: 'destructive',
                title: 'Failed to save simulation',
                description: errorMessage,
            });
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    return {
        saveSimulation,
        isSaving,
        error,
    };
};

export default useSaveSimulation;