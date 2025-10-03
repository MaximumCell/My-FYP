/**
 * Physics AI Chat Hook
 * Manages chat state, API calls, and message history
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';
import {
  askPhysicsQuestion,
  quickAsk,
  getDerivation,
  explainConcept,
  generateDiagram,
  PhysicsResponse,
  QuickAskResponse,
  DiagramRequest,
} from '@/lib/physics-api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    topic?: string;
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
  steps?: Array<{ step_number: number; content: string }>;
  diagram?: {
    image_base64?: string;
    image_url?: string;
    explanation?: string;
    diagram_type?: string;
  };
  isLoading?: boolean;
  error?: string;
}

export interface ChatPreferences {
  length: 'short' | 'medium' | 'long';
  level: 'beginner' | 'intermediate' | 'advanced';
}

export const usePhysicsChat = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<ChatPreferences>({
    length: 'medium',
    level: 'intermediate',
  });

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content:
            "Hello! I'm your Physics AI Tutor. I can help you understand complex physics concepts, provide step-by-step derivations, and answer your questions. What would you like to learn today?",
          timestamp: new Date(),
        },
      ]);
    }
  }, [messages.length]);

  /**
   * Ask enhanced physics question
   */
  const askQuestion = useCallback(
    async (question: string, mode: 'enhanced' | 'quick' = 'enhanced') => {
      if (!question.trim()) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: question,
        timestamp: new Date(),
      };

      // Add loading message
      const loadingMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMessage, loadingMessage]);
      setIsLoading(true);

      try {
        let response: PhysicsResponse | QuickAskResponse;

        if (mode === 'quick') {
          response = await quickAsk({
            question,
            length: preferences.length,
          });
        } else {
          response = await askPhysicsQuestion({
            question,
            user_id: user?.id,
            session_id: sessionId || undefined,
            preferences,
          });
        }

        // Update with actual response
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const aiMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content:
              'response' in response
                ? response.response.formatted || response.response.content
                : response.answer,
            timestamp: new Date(),
            metadata: 'metadata' in response ? response.metadata : undefined,
            learning_aids:
              'learning_aids' in response ? response.learning_aids : undefined,
            citations: 'citations' in response ? response.citations : undefined,
            steps:
              'response' in response ? response.response.steps : undefined,
          };
          return [...filtered, aiMessage];
        });

        // Update session ID if provided
        if ('session_id' in response && response.session_id) {
          setSessionId(response.session_id);
        }
      } catch (error: any) {
        console.error('Error asking question:', error);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const errorMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            timestamp: new Date(),
            error: error.message,
          };
          return [...filtered, errorMessage];
        });
      } finally {
        setIsLoading(false);
      }
    },
    [user, sessionId, preferences]
  );

  /**
   * Request step-by-step derivation
   */
  const requestDerivation = useCallback(
    async (concept: string) => {
      if (!concept.trim()) return;

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: `Show me the derivation for: ${concept}`,
        timestamp: new Date(),
      };

      const loadingMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMessage, loadingMessage]);
      setIsLoading(true);

      try {
        const response = await getDerivation({
          concept,
          user_id: user?.id,
          level: preferences.level,
        });

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const aiMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.response.formatted || response.response.content,
            timestamp: new Date(),
            steps: response.response.steps,
            learning_aids: response.learning_aids,
            citations: response.citations,
          };
          return [...filtered, aiMessage];
        });
      } catch (error: any) {
        console.error('Error requesting derivation:', error);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const errorMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: 'Sorry, I encountered an error getting the derivation.',
            timestamp: new Date(),
            error: error.message,
          };
          return [...filtered, errorMessage];
        });
      } finally {
        setIsLoading(false);
      }
    },
    [user, preferences.level]
  );

  /**
   * Explain concept at specific level
   */
  const explainAtLevel = useCallback(
    async (concept: string, level: 'beginner' | 'intermediate' | 'advanced') => {
      if (!concept.trim()) return;

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: `Explain ${concept} at ${level} level`,
        timestamp: new Date(),
      };

      const loadingMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMessage, loadingMessage]);
      setIsLoading(true);

      try {
        const response = await explainConcept({ concept, level });

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const aiMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.response.content,
            timestamp: new Date(),
            learning_aids: response.learning_aids,
            citations: response.citations,
          };
          return [...filtered, aiMessage];
        });
      } catch (error: any) {
        console.error('Error explaining concept:', error);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const errorMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: 'Sorry, I encountered an error explaining the concept.',
            timestamp: new Date(),
            error: error.message,
          };
          return [...filtered, errorMessage];
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Clear chat history
   */
  const clearChat = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "Chat cleared! I'm ready to help you with physics. What would you like to learn?",
        timestamp: new Date(),
      },
    ]);
    setSessionId(null);
  }, []);

  /**
   * Request diagram generation
   */
  const requestDiagram = useCallback(
    async (description: string, options?: Partial<DiagramRequest>) => {
      if (!description.trim()) return;

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: `Generate diagram: ${description}`,
        timestamp: new Date(),
      };

      const loadingMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Generating diagram...',
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMessage, loadingMessage]);
      setIsLoading(true);

      try {
        const response = await generateDiagram({
          description,
          session_id: sessionId || undefined,
          ...options,
        });

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const aiMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.explanation || 'Here is your diagram:',
            timestamp: new Date(),
            diagram: {
              image_base64: response.image_base64,
              image_url: response.image_url,
              explanation: response.explanation,
              diagram_type: response.diagram_type,
            },
          };
          return [...filtered, aiMessage];
        });
      } catch (error: any) {
        console.error('Error generating diagram:', error);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== loadingMessage.id);
          const errorMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: 'Sorry, I encountered an error generating the diagram.',
            timestamp: new Date(),
            error: error.message,
          };
          return [...filtered, errorMessage];
        });
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  /**
   * Update preferences
   */
  const updatePreferences = useCallback(
    (newPreferences: Partial<ChatPreferences>) => {
      setPreferences((prev) => ({ ...prev, ...newPreferences }));
    },
    []
  );

  return {
    messages,
    isLoading,
    preferences,
    askQuestion,
    requestDerivation,
    requestDiagram,
    explainAtLevel,
    clearChat,
    updatePreferences,
  };
};
