export type MathToken = {
    key: string;
    label: string;
    snippet: string;
    description?: string;
};

export const MATH_TOKENS: MathToken[] = [
    { key: 'sin', label: 'sin()', snippet: 'sin()', description: 'Sine function' },
    { key: 'cos', label: 'cos()', snippet: 'cos()', description: 'Cosine function' },
    { key: 'tan', label: 'tan()', snippet: 'tan()', description: 'Tangent function' },
    { key: 'exp', label: 'exp()', snippet: 'exp()', description: 'Exponential e^x' },
    { key: 'log', label: 'log()', snippet: 'log()', description: 'Natural logarithm' },
    { key: 'sqrt', label: 'sqrt()', snippet: 'sqrt()', description: 'Square root' },
    { key: 'pow', label: '** (power)', snippet: '**', description: 'Power operator (e.g. x**2)' },
    { key: 'pi', label: 'pi', snippet: 'pi', description: 'Pi constant' },
    { key: 'e', label: 'e', snippet: 'E', description: 'Euler constant' },
    { key: 'abs', label: 'abs()', snippet: 'abs()', description: 'Absolute value' },
    { key: 'frac', label: '/', snippet: '/', description: 'Division operator' },
    { key: 'mul', label: '*', snippet: '*', description: 'Multiplication operator' }
];

export default MATH_TOKENS;
