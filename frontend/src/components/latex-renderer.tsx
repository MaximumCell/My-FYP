/**
 * LaTeX Renderer Component
 * Displays mathematical equations
 * TODO: Install react-katex for proper rendering: npm install react-katex katex @types/katex
 */

'use client';

import React from 'react';

interface LatexRendererProps {
  content: string;
  inline?: boolean;
}

/**
 * Renders LaTeX equations in content
 * Currently displays equations in formatted code blocks
 * For full LaTeX rendering, install react-katex
 */
export function LatexRenderer({ content, inline = false }: LatexRendererProps) {
  if (inline) {
    return (
      <code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono">
        {content}
      </code>
    );
  }

  // Parse and render LaTeX equations
  const renderContent = () => {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    
    // Match block equations ($$...$$)
    const blockPattern = /\$\$([^$]+)\$\$/g;
    // Match inline equations ($...$)
    const inlinePattern = /\$([^$]+)\$/g;

    let text = content;

    // First, handle block equations
    text = content.replace(blockPattern, (match, latex, offset) => {
      const before = content.substring(lastIndex, offset);
      if (before) {
        parts.push(renderInlineEquations(before, parts.length));
      }
      
      parts.push(
        <div key={`block-${parts.length}`} className="my-4 p-4 bg-muted rounded-lg border">
          <div className="text-xs text-muted-foreground mb-2">Equation:</div>
          <code className="text-sm font-mono block overflow-x-auto">{latex.trim()}</code>
        </div>
      );
      
      lastIndex = offset + match.length;
      return `__BLOCK_${parts.length - 1}__`;
    });

    // Handle remaining content with inline equations
    const remaining = content.substring(lastIndex);
    if (remaining) {
      parts.push(renderInlineEquations(remaining, parts.length));
    }

    return parts.length > 0 ? <>{parts}</> : <>{content}</>;
  };

  // Render inline equations in text
  const renderInlineEquations = (text: string, keyOffset: number) => {
    const inlinePattern = /\$([^$]+)\$/g;
    const segments: React.ReactNode[] = [];
    let lastIdx = 0;
    let match;

    while ((match = inlinePattern.exec(text)) !== null) {
      // Add text before equation
      if (match.index > lastIdx) {
        segments.push(text.substring(lastIdx, match.index));
      }

      // Add equation as inline code
      segments.push(
        <code
          key={`inline-${keyOffset}-${segments.length}`}
          className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono mx-0.5"
        >
          {match[1].trim()}
        </code>
      );

      lastIdx = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIdx < text.length) {
      segments.push(text.substring(lastIdx));
    }

    return segments.length > 0 ? (
      <span key={`segment-${keyOffset}`}>{segments}</span>
    ) : (
      <span key={`segment-${keyOffset}`}>{text}</span>
    );
  };

  return <div className="latex-content whitespace-pre-wrap">{renderContent()}</div>;
}

/**
 * Simple inline equation renderer
 */
export function InlineEquation({ latex }: { latex: string }) {
  return (
    <code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono">
      {latex}
    </code>
  );
}

/**
 * Block equation renderer
 */
export function BlockEquation({ latex }: { latex: string }) {
  return (
    <div className="my-4 p-4 bg-muted rounded-lg border">
      <div className="text-xs text-muted-foreground mb-2">Equation:</div>
      <code className="text-sm font-mono block overflow-x-auto">{latex}</code>
    </div>
  );
}
