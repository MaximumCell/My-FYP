import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, FunctionSquare, Pilcrow, BrainCircuit } from 'lucide-react';
import Image from 'next/image';

const modelTypes = [
  {
    name: 'Regression',
    description: 'Predict continuous values. Regression models are used to predict a numerical value, such as the price of a house or the temperature.',
    link: '/ml/regression',
    icon: <FunctionSquare className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/regression-chart/600/400',
    imageHint: 'line graph'
  },
  {
    name: 'Classification',
    description: 'Predict a category. Classification models are used to assign a label to an input, like identifying spam or recognizing images.',
    link: '/ml/classification',
    icon: <Pilcrow className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/classification-tree/600/400',
    imageHint: 'decision tree'
  },
  {
    name: 'Deep Learning',
    description: 'Unlock the power of neural networks for complex tasks like image recognition and natural language processing.',
    link: '/ml/deep-learning',
    icon: <BrainCircuit className="h-8 w-8 text-primary" />,
    image: 'https://picsum.photos/seed/neural-network/600/400',
    imageHint: 'neural network',
    disabled: false
  },
];

export default function MlPage() {
  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-headline font-bold">Machine Learning Lab</h1>
        <p className="text-muted-foreground mt-2">Choose a model type to get started.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {modelTypes.map((model) => (
          <Card key={model.name} className={`flex flex-col overflow-hidden transition-all duration-300 ${model.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg hover:shadow-primary/20'}`}>
            <div className="relative h-48 w-full">
              <Image src={model.image} alt={model.name} layout="fill" objectFit="cover" data-ai-hint={model.imageHint} />
            </div>
            <CardHeader className="flex-row gap-4 items-center">
                {model.icon}
                <CardTitle>{model.name}</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow">
              <CardDescription>{model.description}</CardDescription>
            </CardContent>
             <CardContent>
                 <Link href={model.disabled ? '#' : model.link} className={`flex items-center text-sm font-semibold ${model.disabled ? 'text-muted-foreground' : 'text-primary hover:underline'}`}>
                    {model.disabled ? 'Coming Soon' : `Go to ${model.name}`}
                    {!model.disabled && <ArrowRight className="ml-2 h-4 w-4" />}
                </Link>
             </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
