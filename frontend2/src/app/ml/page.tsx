import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, FunctionSquare, Pilcrow, BrainCircuit, Save } from 'lucide-react';
import Image from 'next/image';

const modelTypes = [
  {
    name: 'Regression',
    description: 'Predict continuous values. Regression models are used to predict a numerical value, such as the price of a house or the temperature.',
    link: '/ml/regression',
    icon: <FunctionSquare className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop&crop=center',
    imageHint: 'data analytics and regression charts'
  },
  {
    name: 'Classification',
    description: 'Predict a category. Classification models are used to assign a label to an input, like identifying spam or recognizing images.',
    link: '/ml/classification',
    icon: <Pilcrow className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600&fit=crop&crop=center',
    imageHint: 'classification and data categorization'
  },
  {
    name: 'Deep Learning',
    description: 'Unlock the power of neural networks for complex tasks like image recognition and natural language processing.',
    link: '/ml/deep-learning',
    icon: <BrainCircuit className="h-8 w-8 text-primary" />,
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop&crop=center',
    imageHint: 'artificial intelligence and neural networks',
    disabled: false
  },
];

export default function MlPage() {
  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-headline font-bold">Machine Learning Lab</h1>
        <p className="text-muted-foreground mt-2">Choose a model type to get started.</p>
        <div className="mt-6">
          <Button asChild variant="outline">
            <Link href="/ml/saved">
              <Save className="mr-2 h-4 w-4" />
              View Saved Models
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {modelTypes.map((model) => (
          <Card key={model.name} className={`group flex flex-col overflow-hidden transition-all duration-300 border-border/50 hover:border-primary/20 ${model.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1'}`}>
            <div className="relative h-48 w-full overflow-hidden">
              <Image
                src={model.image}
                alt={model.name}
                fill
                style={{ objectFit: 'cover' }}
                data-ai-hint={model.imageHint}
                className="transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
            <CardHeader className="flex-row gap-4 items-center">
              <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors duration-300">
                {model.icon}
              </div>
              <CardTitle className="group-hover:text-primary transition-colors duration-300">{model.name}</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow">
              <CardDescription className="leading-relaxed">{model.description}</CardDescription>
            </CardContent>
            <CardContent className="pt-0">
              <Link
                href={model.disabled ? '#' : model.link}
                className={`flex items-center justify-between w-full p-3 rounded-lg text-sm font-semibold transition-all duration-300 ${model.disabled
                  ? 'text-muted-foreground bg-muted/30'
                  : 'text-primary hover:bg-primary hover:text-primary-foreground group-hover:shadow-md'
                  }`}
              >
                <span>{model.disabled ? 'Coming Soon' : `Go to ${model.name}`}</span>
                {!model.disabled && <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />}
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
