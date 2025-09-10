'use server';

/**
 * @fileOverview Explains complex physics concepts in a simplified manner.
 *
 * - explainPhysicsConcept - A function that explains physics concepts.
 * - ExplainPhysicsConceptInput - The input type for the explainPhysicsConcept function.
 * - ExplainPhysicsConceptOutput - The return type for the explainPhysicsConcept function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const ExplainPhysicsConceptInputSchema = z.object({
  concept: z.string().describe('The complex physics concept to explain.'),
});

export type ExplainPhysicsConceptInput = z.infer<typeof ExplainPhysicsConceptInputSchema>;

const ExplainPhysicsConceptOutputSchema = z.object({
  explanation: z.string().describe('A simplified explanation of the physics concept.'),
});

export type ExplainPhysicsConceptOutput = z.infer<typeof ExplainPhysicsConceptOutputSchema>;

export async function explainPhysicsConcept(input: ExplainPhysicsConceptInput): Promise<ExplainPhysicsConceptOutput> {
  return explainPhysicsConceptFlow(input);
}

const prompt = ai.definePrompt({
  name: 'explainPhysicsConceptPrompt',
  input: {schema: ExplainPhysicsConceptInputSchema},
  output: {schema: ExplainPhysicsConceptOutputSchema},
  prompt: `You are a helpful AI tutor that explains complex physics concepts in a simplified manner for students to better understand the material.

  Explain the following physics concept:
  {{concept}}`,
});

const explainPhysicsConceptFlow = ai.defineFlow(
  {
    name: 'explainPhysicsConceptFlow',
    inputSchema: ExplainPhysicsConceptInputSchema,
    outputSchema: ExplainPhysicsConceptOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
