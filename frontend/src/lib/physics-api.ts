/**
 * Physics AI Tutor API Service
 * Handles all Phase 7.1-7.3 backend integrations
 */

import api from './api';

// ============================================
// Types & Interfaces
// ============================================

export interface PhysicsQuestion {
  question: string;
  user_id?: string;
  session_id?: string;
  preferences?: {
    length?: 'short' | 'medium' | 'long';
    level?: 'beginner' | 'intermediate' | 'advanced';
  };
}

export interface QuickAskRequest {
  question: string;
  length?: 'short' | 'medium' | 'long';
}

export interface DerivationRequest {
  concept: string;
  user_id?: string;
  level?: 'beginner' | 'intermediate' | 'advanced';
}

export interface ExplainRequest {
  concept: string;
  level: 'beginner' | 'intermediate' | 'advanced';
}

export interface PhysicsResponse {
  success: boolean;
  response: {
    content: string;
    formatted?: string;
    steps?: Array<{ step_number: number; content: string }>;
    complexity_level?: string;
    response_length?: string;
  };
  metadata?: {
    topic?: string;
    query_type?: string;
    sources_used?: number;
    quality_score?: number;
    key_concepts?: string[];
  };
  learning_aids?: {
    follow_up_questions?: string[];
    prerequisites?: string[];
    key_equations?: string[];
  };
  citations?: Array<{
    source_type: string;
    title: string;
    author?: string;
    reference?: string;
    confidence?: number;
  }>;
  session_id?: string;
  timestamp?: string;
}

export interface QuickAskResponse {
  success: boolean;
  answer: string;
  classification?: {
    category: string;
    topic: string;
  };
  context_items_used?: number;
}

interface BookInfo {
  title: string;
  author: string;
  edition: string;
  chapter: string;
}

interface MaterialUpload {
  file: File;
  title: string;
  material_type: string;
  user_id?: string;
  book_info?: BookInfo;
}

export interface Material {
  _id: string;
  user_id: string;
  title: string;
  material_type: string;
  content?: string;
  book_info?: any;
  upload_metadata: {
    file_url: string;
    file_type: string;
    processing_status: string;
  };
  created_at: string;
}

export interface PhysicsBook {
  _id: string;
  title: string;
  author: string;
  edition?: string;
  subject_areas: string[];
  difficulty_level: string;
  popularity_score?: number;
}

export interface PhysicsStats {
  success: boolean;
  statistics: {
    enhanced_tutor_stats: {
      total_enhanced_queries: number;
      rag_queries: number;
      average_context_relevance: number;
    };
  };
}

export interface DiagramRequest {
  description: string;
  diagram_type?: 'force' | 'circuit' | 'wave' | 'energy' | 'motion' | 'field' | 'vector' | 'graph' | 'general';
  style?: 'educational' | 'technical' | 'sketch' | 'colorful' | 'minimal';
  include_labels?: boolean;
  session_id?: string;
}

export interface DiagramResponse {
  success: boolean;
  image_base64?: string;
  image_url?: string;
  explanation?: string;
  diagram_type?: string;
  style?: string;
  timestamp?: string;
  error?: string;
}

// ============================================
// Physics Chat API
// ============================================

/**
 * Ask an enhanced physics question with all features
 */
export const askPhysicsQuestion = async (
  data: PhysicsQuestion
): Promise<PhysicsResponse> => {
  const response = await api.post('/api/physics/ask', data);
  return response.data;
};

/**
 * Quick ask for faster responses without advanced features
 */
export const quickAsk = async (
  data: QuickAskRequest
): Promise<QuickAskResponse> => {
  const response = await api.post('/api/physics/quick-ask', data);
  return response.data;
};

/**
 * Request a step-by-step derivation
 */
export const getDerivation = async (
  data: DerivationRequest
): Promise<PhysicsResponse> => {
  const response = await api.post('/api/physics/derivation', data);
  return response.data;
};

/**
 * Get explanation at specific level
 */
export const explainConcept = async (
  data: ExplainRequest
): Promise<PhysicsResponse> => {
  const response = await api.post('/api/physics/explain', data);
  return response.data;
};

/**
 * Get tutor statistics
 */
export const getPhysicsStats = async (): Promise<PhysicsStats> => {
  const response = await api.get('/api/physics/stats');
  return response.data;
};

/**
 * Generate physics diagram using AI
 */
export const generateDiagram = async (
  data: DiagramRequest
): Promise<DiagramResponse> => {
  const response = await api.post('/api/physics/generate-diagram', data);
  return response.data;
};

// ============================================
// Learning Materials API
// ============================================

/**
 * Upload physics learning material (PDF/images/DOCX/PPTX)
 */
export const uploadMaterial = async (data: MaterialUpload): Promise<any> => {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('title', data.title);
  formData.append('material_type', data.material_type);

  // Add user_id - in production this would come from auth context
  // For now, use a default user_id
  formData.append('user_id', data.user_id || 'default_user');

  if (data.book_info) {
    formData.append('book_info', JSON.stringify(data.book_info));
  }

  const response = await api.post('/api/materials/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * List user's uploaded materials
 */
export const listMaterials = async (userId: string): Promise<Material[]> => {
  const response = await api.get(`/api/materials/list?user_id=${userId}`);
  return response.data.materials || [];
};

/**
 * Get specific material details
 */
export const getMaterial = async (materialId: string): Promise<Material> => {
  const response = await api.get(`/api/materials/${materialId}`);
  return response.data.material;
};

/**
 * Delete material
 */
export const deleteMaterial = async (materialId: string, userId?: string): Promise<any> => {
  const response = await api.delete(`/api/materials/${materialId}`, {
    params: { user_id: userId },
  });
  return response.data;
};

/**
 * Re-process material with OCR
 */
export const processMaterial = async (materialId: string): Promise<any> => {
  const response = await api.post(`/api/materials/${materialId}/process`);
  return response.data;
};

// ============================================
// Physics Books API
// ============================================

/**
 * Get book recommendations for topic
 */
export const recommendBooks = async (params: {
  topic?: string;
  difficulty?: string;
  limit?: number;
}): Promise<PhysicsBook[]> => {
  const queryParams = new URLSearchParams(params as any).toString();
  const response = await api.get(`/api/books/recommend?${queryParams}`);
  return response.data.recommendations || [];
};

/**
 * Search physics books
 */
export const searchBooks = async (query: string): Promise<PhysicsBook[]> => {
  const response = await api.get(`/api/books/search?q=${query}`);
  return response.data.books || [];
};

/**
 * List all available physics books
 */
export const listBooks = async (): Promise<PhysicsBook[]> => {
  const response = await api.get('/api/books/list');
  return response.data.books || [];
};

/**
 * Select preferred book for session
 */
export const selectPreferredBook = async (
  userId: string,
  bookId: string
): Promise<any> => {
  const response = await api.post('/api/books/select', {
    user_id: userId,
    book_id: bookId,
  });
  return response.data;
};

// ============================================
// Session Management
// ============================================

/**
 * Get current session or create new one
 */
export const getOrCreateSession = async (userId: string): Promise<string> => {
  const response = await api.post('/api/physics/session', { user_id: userId });
  return response.data.session_id;
};

/**
 * Clear chat session
 */
export const clearSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/api/physics/session/${sessionId}`);
};
