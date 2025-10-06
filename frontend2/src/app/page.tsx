import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Rocket, BrainCircuit, TestTube, Star, ArrowRight } from 'lucide-react';
import Image from 'next/image';
import { SignedIn, SignedOut } from '@clerk/nextjs';
import WelcomePage from '@/components/welcome-page';
import { UserDashboard } from '@/components/user-dashboard';

export default function Home() {
  return (
    <>
      {/* Show welcome page for non-authenticated users */}
      <SignedOut>
        <WelcomePage />
      </SignedOut>

      {/* Show dashboard for authenticated users */}
      <SignedIn>
        <AuthenticatedHome />
      </SignedIn>
    </>
  );
}

function AuthenticatedHome() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Hero Section with Dashboard Integration */}
      <section className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-4 h-4 bg-primary/20 rounded-full float-animation" style={{ animationDelay: '0s' }} />
        <div className="absolute top-40 right-20 w-6 h-6 bg-accent/20 rounded-full float-animation" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-primary/30 rounded-full float-animation" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-20 right-10 w-5 h-5 bg-accent/30 rounded-full float-animation" style={{ animationDelay: '1s' }} />

        <div className="relative container mx-auto px-4 py-12 md:py-20">
          {/* Welcome Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
              System Online
            </div>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-headline font-bold tracking-tight mb-6">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-primary to-accent">
                Welcome Back
              </span>
              <br />
              <span className="text-foreground/80">to PhysicsLab</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
              Continue your research journey with powerful ML tools, advanced simulations, and AI-powered assistance.
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap justify-center gap-4 mb-16">
            <Button size="lg" className="h-14 px-8 text-lg font-semibold" asChild>
              <Link href="/ml">
                <Rocket className="mr-3 h-6 w-6" />
                Launch ML Lab
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="h-14 px-8 text-lg font-semibold" asChild>
              <Link href="/simulation">
                <TestTube className="mr-3 h-6 w-6" />
                Start Simulation
              </Link>
            </Button>
            <Button size="lg" variant="ghost" className="h-14 px-8 text-lg font-semibold" asChild>
              <Link href="/ai">
                <BrainCircuit className="mr-3 h-6 w-6" />
                AI Tutor
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Enhanced Dashboard Section */}
      <section className="relative py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-headline font-bold mb-4">Your Research Dashboard</h2>
            <p className="text-muted-foreground">Track your progress and manage your projects</p>
          </div>
          <UserDashboard />
        </div>
      </section>

      {/* Tools & Resources Section - Redesigned */}
      <section className="relative py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-headline font-bold mb-4">
              Powerful Tools at Your Fingertips
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to advance your physics research and machine learning projects
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <EnhancedFeatureCard
              icon={<Rocket className="h-12 w-12" />}
              title="Machine Learning Lab"
              description="Upload datasets, train models, and download trained classifiers. Get intelligent model recommendations based on your data characteristics."
              features={["Smart Model Recommendations", "Real-time Training", "Export Ready Models"]}
              link="/ml"
              linkText="Explore ML Tools"
              gradient="from-blue-500 to-purple-600"
            />
            <EnhancedFeatureCard
              icon={<TestTube className="h-12 w-12" />}
              title="Physics Simulation"
              description="Visualize complex equations and physics concepts. Use predefined models or create custom simulations with your own parameters."
              features={["Interactive Visualizations", "Custom Equations", "Real-time Physics"]}
              link="/simulation"
              linkText="Run Simulation"
              gradient="from-green-500 to-teal-600"
            />
            <EnhancedFeatureCard
              icon={<BrainCircuit className="h-12 w-12" />}
              title="AI Tutor"
              description="Your personal AI assistant for physics concepts. Get detailed explanations, solve problems, and enhance your understanding."
              features={["Concept Explanations", "Problem Solving", "Personalized Learning"]}
              link="/ai"
              linkText="Meet AI Tutor"
              gradient="from-orange-500 to-red-600"
              comingSoon={false}
            />
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="relative py-16 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-headline font-bold mb-6">
              Ready to Push the Boundaries?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of researchers using PhysicsLab to accelerate their discoveries
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button size="lg" className="h-14 px-8" asChild>
                <Link href="/ml">Start Your First Project</Link>
              </Button>
              <Button size="lg" variant="outline" className="h-14 px-8" asChild>
                <Link href="/docs">View Documentation</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function EnhancedFeatureCard({
  icon,
  title,
  description,
  features,
  link,
  linkText,
  gradient,
  comingSoon = false
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  features: string[];
  link: string;
  linkText: string;
  gradient: string;
  comingSoon?: boolean;
}) {
  return (
    <Card className="group relative overflow-hidden bg-card/50 backdrop-blur border-border/50 hover:border-primary/20 transition-all duration-500 hover:shadow-2xl hover:shadow-primary/10">
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

      {/* Coming Soon Badge */}
      {comingSoon && (
        <div className="absolute top-4 right-4 z-10">
          <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-medium">
            Coming Soon
          </div>
        </div>
      )}

      <CardContent className="relative p-8 h-full flex flex-col">
        {/* Icon */}
        <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${gradient} text-white mb-6 w-fit group-hover:scale-110 transition-transform duration-300`}>
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1">
          <CardTitle className="text-2xl font-bold mb-4 group-hover:text-primary transition-colors">
            {title}
          </CardTitle>
          <CardDescription className="text-base mb-6 leading-relaxed">
            {description}
          </CardDescription>

          {/* Features List */}
          <ul className="space-y-2 mb-8">
            {features.map((feature, index) => (
              <li key={index} className="flex items-center text-sm text-muted-foreground">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mr-3 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </div>

        {/* Action Button */}
        <Button
          asChild
          className={`w-full bg-gradient-to-r ${gradient} border-0 text-white hover:shadow-lg hover:shadow-primary/25 transition-all duration-300 ${comingSoon ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={comingSoon}
        >
          <Link href={comingSoon ? '#' : link}>
            {linkText}
            {!comingSoon && <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>}
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
