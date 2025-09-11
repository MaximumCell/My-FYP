// Shared types
export type ModelType = 'regression' | 'classification' | 'deep-learning';
export type ApiError = { error: string };

// /ml/models/*
export type ModelList = string[];

// /ml/get_columns
export type ColumnsResponse = { columns: string[] };

// /ml/train/*
export interface TrainParams {
  file: File;
  model: string;
  target_column?: string;
  test_size?: number;
  scaling_method?: string;
  hyperparams?: Record<string, any>;
}
export interface TrainResponse {
  message: string;
  model_path: string;
  mean_squared_error?: number;
  mean_absolute_error?: number;
  r2_score?: number;
  accuracy?: number;
  [key: string]: any; // For any other metrics
}

// /ml/test/*
export interface TestParams {
  model: string;
  // single example object (backend expects a dict of feature->value)
  new_data: Record<string, any>;
}

export interface TestRegressionResponse {
  predictions: number[];
}

export interface TestClassificationResponse {
  predictions: (string | number)[];
  probabilities: number[][];
  class_names: (string | number)[];
}

// /ml/recommend
export interface RecommendResponse {
  recommended_model: string;
}

// /simulation/simulation
export interface SimulationParams {
  equation: string;
  x_min: number;
  x_max: number;
  variables: Record<string, number>;
}
export interface SimulationResponse {
  message: string;
  plot_url: string;
  equation: string;
}
