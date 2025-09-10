import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Rocket, BrainCircuit, TestTube } from 'lucide-react';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <section className="w-full py-20 md:py-32">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 items-center">
            <div className="flex flex-col justify-center space-y-4">
              <h1 className="text-4xl font-headline font-bold tracking-tighter sm:text-5xl xl:text-6xl/none bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                Welcome to PhysicsLab
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl mx-auto">
                Your integrated environment for advanced machine learning and physics simulations. Train models, test hypotheses, and explore complex concepts with powerful, easy-to-use tools.
              </p>
              <div className="w-full max-w-sm space-x-2 mx-auto">
                <Button asChild>
                  <Link href="/ml">
                    <Rocket className="mr-2 h-4 w-4" />
                    Launch ML Lab
                  </Link>
                </Button>
                <Button variant="secondary" asChild>
                  <Link href="/simulation">
                    <TestTube className="mr-2 h-4 w-4" />
                    Start Simulation
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="w-full py-12 md:py-24 bg-muted/40 rounded-lg">
        <div className="container px-4 md:px-6">
          <h2 className="text-3xl font-headline font-bold tracking-tighter mb-12 sm:text-4xl">
            Explore Our Core Features
          </h2>
          <div className="grid grid-cols-1 gap-12">
            <FeatureCard
              icon={<Rocket className="h-10 w-10 text-primary" />}
              title="Machine Learning Lab"
              description="Upload your data to train, test, and download regression and classification models. Get model recommendations tailored to your dataset."
              link="/ml"
              linkText="Explore ML Tools"
              imageUrl="https://picsum.photos/seed/data-science/600/400"
              imageHint="data analysis"
            />
            <FeatureCard
              icon={<TestTube className="h-10 w-10 text-primary" />}
              title="Physics Simulation"
              description="Visualize complex physics equations. Use predefined models or input your own custom equations and variables to see concepts in action."
              link="/simulation"
              linkText="Run a Simulation"
              imageUrl="https://picsum.photos/seed/physics-atoms/600/400"
              imageHint="science experiment"
            />
            <FeatureCard
              icon={<BrainCircuit className="h-10 w-10 text-primary" />}
              title="AI Tutor"
              description="Your personal AI assistant for physics. Get explanations for complex topics and help with your coursework. (Coming Soon!)"
              link="/ai"
              linkText="Meet the Tutor"
              imageUrl="https://picsum.photos/seed/artificial-intelligence/600/400"
              imageHint="robot thinking"
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description, link, linkText, imageUrl, imageHint }: { icon: React.ReactNode, title: string, description: string, link: string, linkText: string, imageUrl: string, imageHint: string }) {
  return (
    <Card className="w-full max-w-4xl mx-auto overflow-hidden shadow-lg hover:shadow-primary/20 transition-all duration-300">
        <div className="grid md:grid-cols-2">
            <div className="relative h-64 md:h-auto">
                <Image src={imageUrl} alt={title} layout="fill" objectFit="cover" data-ai-hint={imageHint} />
            </div>
            <div className="flex flex-col justify-center p-8 text-left">
                <div className="flex items-center gap-4 mb-4">
                    {icon}
                    <CardTitle className="text-3xl">{title}</CardTitle>
                </div>
                <CardDescription className="mb-6 text-base">{description}</CardDescription>
                <Button variant="link" asChild className="mt-auto text-primary p-0 justify-start">
                    <Link href={link}>{linkText} &rarr;</Link>
                </Button>
            </div>
        </div>
    </Card>
  );
}
