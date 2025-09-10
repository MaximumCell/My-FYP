'use server';

/**
 * @fileOverview An AI agent to analyze simulation results.
 *
 * - analyzeSimulationResults - A function that handles the simulation result analysis process.
 * - AnalyzeSimulationResultsInput - The input type for the analyzeSimulationResults function.
 * - AnalyzeSimulationResultsOutput - The return type for the analyzeSimulationResults function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AnalyzeSimulationResultsInputSchema = z.object({
  simulationData: z
    .string()
    .describe('The simulation data to analyze, as a data URI that must include a MIME type and use Base64 encoding. Expected format: \'data:<mimetype>;base64,<encoded_data>\'.'),
});
export type AnalyzeSimulationResultsInput = z.infer<typeof AnalyzeSimulationResultsInputSchema>;

const AnalyzeSimulationResultsOutputSchema = z.object({
  analysis: z
    .string()
    .describe('The analysis of the simulation results, including identified patterns and insights.'),
});
export type AnalyzeSimulationResultsOutput = z.infer<typeof AnalyzeSimulationResultsOutputSchema>;

export async function analyzeSimulationResults(
  input: AnalyzeSimulationResultsInput
): Promise<AnalyzeSimulationResultsOutput> {
  return analyzeSimulationResultsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'analyzeSimulationResultsPrompt',
  input: {schema: AnalyzeSimulationResultsInputSchema},
  output: {schema: AnalyzeSimulationResultsOutputSchema},
  prompt: `You are an expert researcher, skilled at analyzing simulation data to identify patterns and insights.

  Analyze the simulation data provided to identify key patterns, trends, and insights.

  Simulation Data: {{simulationData}}
  `,
});

const analyzeSimulationResultsFlow = ai.defineFlow(
  {
    name: 'analyzeSimulationResultsFlow',
    inputSchema: AnalyzeSimulationResultsInputSchema,
    outputSchema: AnalyzeSimulationResultsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
