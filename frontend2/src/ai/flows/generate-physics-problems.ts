'use server';

/**
 * @fileOverview This file defines a Genkit flow for generating physics problems based on a given topic.
 *
 * The flow takes a physics topic as input and returns a set of practice problems related to that topic.
 * It exports:
 *   - generatePhysicsProblems: An async function that takes a topic as input and returns a promise of physics problems.
 *   - GeneratePhysicsProblemsInput: The input type for the generatePhysicsProblems function.
 *   - GeneratePhysicsProblemsOutput: The output type for the generatePhysicsProblems function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GeneratePhysicsProblemsInputSchema = z.object({
  topic: z.string().describe('The physics topic to generate problems for.'),
});
export type GeneratePhysicsProblemsInput = z.infer<typeof GeneratePhysicsProblemsInputSchema>;

const GeneratePhysicsProblemsOutputSchema = z.object({
  problems: z.array(z.string()).describe('An array of physics problems related to the topic.'),
});
export type GeneratePhysicsProblemsOutput = z.infer<typeof GeneratePhysicsProblemsOutputSchema>;

export async function generatePhysicsProblems(input: GeneratePhysicsProblemsInput): Promise<GeneratePhysicsProblemsOutput> {
  return generatePhysicsProblemsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generatePhysicsProblemsPrompt',
  input: {schema: GeneratePhysicsProblemsInputSchema},
  output: {schema: GeneratePhysicsProblemsOutputSchema},
  prompt: `You are a physics tutor. Generate a set of practice problems related to the following topic: {{{topic}}}. The problems should be challenging but solvable by a student who understands the topic. Return the problems as a JSON array of strings.\n\nExample:\n{
  "problems": [
    "A car accelerates from rest to 60 m/s in 10 seconds. What is its acceleration?",
    "A ball is thrown vertically upwards with an initial velocity of 20 m/s. What is the maximum height it reaches?",
    "A block of mass 5 kg is placed on a horizontal surface. A force of 10 N is applied to the block. If the coefficient of friction between the block and the surface is 0.2, what is the acceleration of the block?"
  ]
}`,
});

const generatePhysicsProblemsFlow = ai.defineFlow(
  {
    name: 'generatePhysicsProblemsFlow',
    inputSchema: GeneratePhysicsProblemsInputSchema,
    outputSchema: GeneratePhysicsProblemsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
