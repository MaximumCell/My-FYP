'use client';

import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import type { ApiError, SimulationParams, SimulationResponse } from '@/types/api';

export const useRunSimulation = () => {
  return useMutation<SimulationResponse, ApiError, SimulationParams>({
    mutationFn: async (params) => {
      // backend exposes /simulation/plot2d for 2D equation plotting
      const { data } = await api.post('/simulation/plot2d', params);
      return data as SimulationResponse;
    },
  });
};
