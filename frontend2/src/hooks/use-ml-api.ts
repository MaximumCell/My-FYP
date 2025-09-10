'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import type { 
  ApiError,
  ModelList,
  ColumnsResponse,
  TrainParams,
  TrainResponse,
  TestParams,
  TestRegressionResponse,
  TestClassificationResponse,
  RecommendResponse,
  ModelType
} from '@/types/api';

// Fetch available models
export const useModels = (type: ModelType) => {
  return useQuery<ModelList, ApiError>({
    queryKey: ['models', type],
    queryFn: async () => {
      const { data } = await api.get(`/ml/models/${type}`);
      return data;
    },
  });
};

// Get columns from a CSV file
export const useColumns = () => {
  return useMutation<ColumnsResponse, ApiError, File>({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post('/ml/get_columns', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
  });
};

// Train a model
export const useTrainModel = (type: ModelType) => {
  return useMutation<TrainResponse, ApiError, TrainParams>({
    mutationFn: async (params) => {
      const formData = new FormData();
      formData.append('file', params.file);
      formData.append('model', params.model);
      if (params.target_column) {
        formData.append('target_column', params.target_column);
      }
      const { data } = await api.post(`/ml/train/${type}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
  });
};

// Test a model
export const useTestModel = (type: ModelType) => {
  return useMutation<TestRegressionResponse | TestClassificationResponse, ApiError, TestParams>({
    mutationFn: async (params) => {
      const { data } = await api.post(`/ml/test/${type}`, params);
      return data;
    },
  });
};

// Get model recommendation
export const useRecommendModel = () => {
  return useMutation<RecommendResponse, ApiError, File>({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post('/ml/recommend', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
  });
};
