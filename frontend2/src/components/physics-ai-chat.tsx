/**
 * Physics AI Chat Component
 * Main chat interface with message display and controls
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Send,
  Loader2,
  Settings,
  Lightbulb,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Brain,
  Image,
} from 'lucide-react';
import { usePhysicsChat, ChatMessage } from '@/hooks/use-physics-chat';
import { LatexRenderer } from '@/components/latex-renderer';
import { cn } from '@/lib/utils';
import { useRef as reactUseRef } from 'react';

export function PhysicsAIChat() {
  const {
    messages,
    isLoading,
    preferences,
    askQuestion,
    requestDerivation,
    requestDiagram,
    clearChat,
    updatePreferences,
  } = usePhysicsChat();

  const [input, setInput] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      const lowerInput = input.toLowerCase();

      // Check if user is requesting a diagram/image
      const diagramKeywords = [
        'draw', 'diagram', 'image', 'picture', 'visualiz', 'illustrat',
        'sketch', 'show me', 'generate', 'create'
      ];
      const physicsVisuals = [
        'field', 'circuit', 'force', 'vector', 'wave', 'motion',
        'energy', 'graph', 'electric', 'magnetic'
      ];

      const hasDiagramKeyword = diagramKeywords.some(kw => lowerInput.includes(kw));
      const hasPhysicsVisual = physicsVisuals.some(kw => lowerInput.includes(kw));

      if (hasDiagramKeyword || (hasPhysicsVisual && lowerInput.includes('of'))) {
        // User wants a diagram
        requestDiagram(input.trim());
      } else {
        // Regular question
        askQuestion(input.trim());
      }
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="w-full max-w-5xl h-[80vh] flex flex-col">
      {/* Header */}
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar className="h-10 w-10 bg-gradient-to-br from-purple-500 to-blue-500">
              <AvatarFallback className="text-white">
                <Brain className="h-5 w-5" />
              </AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-lg">Physics AI Tutor</CardTitle>
              <p className="text-sm text-muted-foreground">
                {preferences.level} • {preferences.length} responses
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm" onClick={clearChat}>
              Clear Chat
            </Button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 p-4 bg-muted rounded-lg space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Response Length
                </label>
                <Select
                  value={preferences.length}
                  onValueChange={(value: any) =>
                    updatePreferences({ length: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="short">Short (~150 words)</SelectItem>
                    <SelectItem value="medium">Medium (Standard)</SelectItem>
                    <SelectItem value="long">Long (Comprehensive)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Complexity Level
                </label>
                <Select
                  value={preferences.level}
                  onValueChange={(value: any) =>
                    updatePreferences({ level: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        )}
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-grow overflow-hidden p-0">
        <ScrollArea className="h-full px-4" ref={scrollRef}>
          <div className="py-4 space-y-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </div>
        </ScrollArea>
      </CardContent>

      {/* Input */}
      <CardFooter className="border-t pt-4">
        <div className="flex w-full items-end gap-2">
          <div className="flex-grow">
            <Input
              placeholder="Ask a physics question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              className="min-h-[40px]"
            />
          </div>
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

// ============================================
// Message Bubble Component
// ============================================

function MessageBubble({ message }: { message: ChatMessage }) {
  const [expandedSteps, setExpandedSteps] = useState(false);
  const [expandedAids, setExpandedAids] = useState(false);

  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {!isUser && (
        <Avatar className="h-8 w-8 bg-gradient-to-br from-purple-500 to-blue-500 flex-shrink-0">
          <AvatarFallback className="text-white">
            <Sparkles className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-3 space-y-3',
          isUser
            ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
            : 'bg-muted'
        )}
      >
        {/* Loading State */}
        {message.isLoading && (
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        {/* Error State */}
        {message.error && (
          <div className="text-sm text-red-500">
            Error: {message.error}
          </div>
        )}

        {/* Message Content */}
        {!message.isLoading && !message.error && (
          <>
            <div className="text-sm leading-relaxed">
              <LatexRenderer content={message.content} />
            </div>

            {/* Metadata Badges */}
            {message.metadata && (
              <div className="flex flex-wrap gap-2">
                {message.metadata.topic && (
                  <Badge variant="secondary" className="text-xs">
                    {message.metadata.topic}
                  </Badge>
                )}
                {message.metadata.sources_used !== undefined && (
                  <Badge variant="outline" className="text-xs">
                    {Array.isArray(message.metadata.sources_used)
                      ? message.metadata.sources_used.length
                      : message.metadata.sources_used} sources
                  </Badge>
                )}
                {message.metadata.quality_score !== undefined && (
                  <Badge variant="outline" className="text-xs">
                    Quality: {message.metadata.quality_score.toFixed(1)}/10
                  </Badge>
                )}
              </div>
            )}

            {/* Step-by-Step Derivation */}
            {message.steps && message.steps.length > 0 && (
              <div className="mt-3">
                <button
                  onClick={() => setExpandedSteps(!expandedSteps)}
                  className="flex items-center gap-2 text-sm font-medium hover:underline"
                >
                  <BookOpen className="h-4 w-4" />
                  Step-by-Step Derivation ({message.steps.length} steps)
                  {expandedSteps ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </button>
                {expandedSteps && (
                  <div className="mt-2 space-y-2">
                    {message.steps.map((step) => (
                      <div
                        key={step.step_number}
                        className="pl-4 border-l-2 border-primary/20"
                      >
                        <div className="text-xs font-medium text-muted-foreground">
                          Step {step.step_number}
                        </div>
                        <div className="text-sm">
                          <LatexRenderer content={step.content} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Learning Aids */}
            {message.learning_aids && (
              <div className="mt-3">
                <button
                  onClick={() => setExpandedAids(!expandedAids)}
                  className="flex items-center gap-2 text-sm font-medium hover:underline"
                >
                  <Lightbulb className="h-4 w-4" />
                  Learning Aids
                  {expandedAids ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </button>
                {expandedAids && (
                  <div className="mt-2 space-y-3">
                    {message.learning_aids.follow_up_questions &&
                      message.learning_aids.follow_up_questions.length > 0 && (
                        <div>
                          <div className="text-xs font-medium mb-1">
                            Follow-up Questions:
                          </div>
                          <ul className="text-sm space-y-1">
                            {message.learning_aids.follow_up_questions.map(
                              (q, i) => (
                                <li key={i} className="ml-4 list-disc">
                                  {q}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    {message.learning_aids.prerequisites &&
                      message.learning_aids.prerequisites.length > 0 && (
                        <div>
                          <div className="text-xs font-medium mb-1">
                            Prerequisites:
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {message.learning_aids.prerequisites.map((p, i) => (
                              <Badge
                                key={i}
                                variant="outline"
                                className="text-xs"
                              >
                                {p}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    {message.learning_aids.key_equations &&
                      message.learning_aids.key_equations.length > 0 && (
                        <div>
                          <div className="text-xs font-medium mb-1">
                            Key Equations:
                          </div>
                          <div className="text-sm font-mono bg-background/50 p-2 rounded">
                            {message.learning_aids.key_equations.join(', ')}
                          </div>
                        </div>
                      )}
                  </div>
                )}
              </div>
            )}

            {/* Generated Diagram */}
            {message.diagram && (message.diagram.image_base64 || message.diagram.image_url) && (
              <div className="mt-3 p-3 bg-background/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Image className="h-4 w-4" />
                  <span className="text-sm font-medium">
                    {message.diagram.diagram_type ? `${message.diagram.diagram_type} diagram` : 'Generated Diagram'}
                  </span>
                </div>
                <div className="relative rounded-lg overflow-hidden border border-border">
                  <img
                    src={
                      message.diagram.image_url
                        ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}${message.diagram.image_url}`
                        : `data:image/png;base64,${message.diagram.image_base64}`
                    }
                    alt={message.diagram.explanation || 'Physics diagram'}
                    className="w-full h-auto"
                    onError={(e) => {
                      // Fallback to base64 if URL fails
                      if (message.diagram?.image_base64) {
                        e.currentTarget.src = `data:image/png;base64,${message.diagram.image_base64}`;
                      }
                    }}
                  />
                </div>
                {message.diagram.explanation && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {message.diagram.explanation}
                  </p>
                )}
              </div>
            )}

            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-primary/10">
                <div className="text-xs font-medium mb-2">Sources:</div>
                <div className="space-y-1">
                  {message.citations.map((citation: any, i: number) => {
                    // Support multiple citation shapes coming from backend
                    const title = citation?.title || citation?.citation || citation?.citation_text || citation?.citation_text || citation?.source_id || 'Untitled';
                    const author = citation?.author || citation?.metadata?.author || null;
                    const conf = typeof citation?.confidence === 'number'
                      ? citation.confidence
                      : (typeof citation?.confidence === 'string' && !isNaN(Number(citation.confidence)))
                        ? Number(citation.confidence)
                        : (typeof citation?.confidence === 'undefined' && typeof citation?.confidence !== 'number')
                          ? (citation?.confidence || 0)
                          : 0;

                    return (
                      <div key={i} className="text-xs text-muted-foreground">
                        • {title}
                        {author && ` - ${author}`}
                        {conf !== undefined && conf !== null && (
                          <span className="ml-2">({(conf * 100).toFixed(0)}% relevant)</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {isUser && (
        <Avatar className="h-8 w-8 flex-shrink-0">
          <AvatarFallback>You</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
function useRef<T>(initialValue: T | null) {
  return reactUseRef<T>(initialValue);
}

