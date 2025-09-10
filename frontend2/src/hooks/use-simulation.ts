'use client';

import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import type { ApiError, SimulationParams, SimulationResponse } from '@/types/api';

export const useRunSimulation = () => {
  return useMutation<SimulationResponse, ApiError, SimulationParams>({
    mutationFn: async (params) => {
      const { data } = await api.post('/simulation/simulation', params);
      return data;
    },
  });
};
