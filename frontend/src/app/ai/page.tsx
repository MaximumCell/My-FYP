import { PhysicsAIChat } from '@/components/physics-ai-chat';
import { MaterialsManager } from '@/components/materials-manager';
import { BrainCircuit, BookOpen, Sparkles } from 'lucide-react';
import RequireAuth from '@/components/auth/require-auth';

export default function AiTutorPage() {
  return (
    <RequireAuth>
      <div className="flex flex-col items-center">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-2">
            <BrainCircuit className="h-10 w-10 text-primary" />
            <h1 className="text-4xl font-headline font-bold">Physics AI Tutor</h1>
          </div>
          <p className="text-muted-foreground mt-2">
            Your intelligent physics assistant with step-by-step explanations
          </p>
          <div className="flex items-center justify-center gap-2 mt-4">
            <MaterialsManager />
          </div>
        </div>

        {/* Features Banner */}
        <div className="w-full max-w-5xl mb-6 grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-lg p-4 text-center">
            <Sparkles className="h-6 w-6 mx-auto mb-2 text-purple-500" />
            <h3 className="font-semibold text-sm mb-1">Adaptive Responses</h3>
            <p className="text-xs text-muted-foreground">
              Short, medium, or long explanations tailored to your level
            </p>
          </div>
          <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4 text-center">
            <BookOpen className="h-6 w-6 mx-auto mb-2 text-blue-500" />
            <h3 className="font-semibold text-sm mb-1">Source-Based Learning</h3>
            <p className="text-xs text-muted-foreground">
              Uses your uploaded materials for personalized answers
            </p>
          </div>
          <div className="bg-gradient-to-br from-cyan-500/10 to-teal-500/10 border border-cyan-500/20 rounded-lg p-4 text-center">
            <BrainCircuit className="h-6 w-6 mx-auto mb-2 text-cyan-500" />
            <h3 className="font-semibold text-sm mb-1">Step-by-Step Derivations</h3>
            <p className="text-xs text-muted-foreground">
              Complete derivations with prerequisites and follow-ups
            </p>
          </div>
        </div>

        {/* Main Chat Interface */}
        <PhysicsAIChat />
      </div>
    </RequireAuth>
  );
}
