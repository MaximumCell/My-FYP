'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Rocket, BrainCircuit, TestTube, Users, Shield, Zap } from 'lucide-react';
import Image from 'next/image';
import { SignUpButton } from '@clerk/nextjs';

export default function WelcomePage() {
    return (
        <div className="flex flex-col items-center justify-center text-center">
            {/* Hero Section */}
            <section className="relative w-full py-20 md:py-32 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent" />
                <div className="container px-4 md:px-6 relative z-10">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <div className="flex flex-col justify-center space-y-8 order-2 lg:order-1">
                            <div className="space-y-4">
                                <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium">
                                    🚀 Advanced Physics & ML Platform
                                </div>
                                <h1 className="text-4xl font-headline font-bold tracking-tighter sm:text-5xl xl:text-6xl/none bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-primary animate-pulse">
                                    Welcome to PhysicsLab
                                </h1>
                                <p className="max-w-[600px] text-muted-foreground md:text-xl leading-relaxed">
                                    Transform your understanding of physics and machine learning with our cutting-edge platform. Experience interactive simulations, AI-powered insights, and seamless model training.
                                </p>
                            </div>
                            <div className="flex flex-col sm:flex-row gap-4">
                                <SignUpButton>
                                    <Button size="lg" className="text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300">
                                        <Users className="mr-2 h-5 w-5" />
                                        Get Started Free
                                    </Button>
                                </SignUpButton>
                                <Button variant="outline" size="lg" asChild className="text-lg px-8 py-4 hover:bg-primary/5 transition-all duration-300">
                                    <Link href="#features">
                                        <TestTube className="mr-2 h-5 w-5" />
                                        Explore Features
                                    </Link>
                                </Button>
                            </div>
                            <div className="flex items-center gap-6 pt-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                    <span className="text-sm text-muted-foreground">Live Platform</span>
                                </div>
                                <div className="text-sm text-muted-foreground">⭐ Trusted by 10,000+ users</div>
                            </div>
                        </div>
                        <div className="order-1 lg:order-2">
                            <div className="relative">
                                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-3xl blur-3xl" />
                                <div className="relative bg-card rounded-3xl p-8 shadow-2xl border">
                                    <Image
                                        src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                                        alt="Advanced Physics Laboratory"
                                        width={600}
                                        height={400}
                                        className="rounded-2xl w-full h-auto shadow-lg"
                                    />
                                    <div className="absolute -bottom-4 -right-4 bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                                        🧪 Interactive Lab
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="w-full py-16 md:py-28 relative">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-muted/20 to-transparent" />
                <div className="container px-4 md:px-6 relative z-10">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-headline font-bold tracking-tighter mb-4 sm:text-4xl bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                            Why Choose PhysicsLab?
                        </h2>
                        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                            Experience the next generation of scientific computing with our innovative platform
                        </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="group relative">
                            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/5 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                            <div className="relative bg-card rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border hover:border-primary/20">
                                <div className="flex flex-col items-center text-center space-y-6">
                                    <div className="relative">
                                        <div className="p-4 bg-gradient-to-br from-primary/20 to-primary/10 rounded-2xl">
                                            <Zap className="h-8 w-8 text-primary" />
                                        </div>
                                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-accent rounded-full animate-pulse" />
                                    </div>
                                    <h3 className="text-xl font-semibold">Lightning Fast</h3>
                                    <p className="text-muted-foreground leading-relaxed">
                                        Advanced algorithms and optimized performance for real-time simulations and rapid model training with millisecond response times.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="group relative">
                            <div className="absolute inset-0 bg-gradient-to-br from-accent/10 to-primary/5 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                            <div className="relative bg-card rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border hover:border-accent/20">
                                <div className="flex flex-col items-center text-center space-y-6">
                                    <div className="relative">
                                        <div className="p-4 bg-gradient-to-br from-accent/20 to-accent/10 rounded-2xl">
                                            <Shield className="h-8 w-8 text-accent" />
                                        </div>
                                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse" />
                                    </div>
                                    <h3 className="text-xl font-semibold">Secure & Private</h3>
                                    <p className="text-muted-foreground leading-relaxed">
                                        Enterprise-grade security with end-to-end encryption. Your data and models remain completely private and protected.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="group relative">
                            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                            <div className="relative bg-card rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border hover:border-primary/20">
                                <div className="flex flex-col items-center text-center space-y-6">
                                    <div className="relative">
                                        <div className="p-4 bg-gradient-to-br from-primary/20 to-accent/10 rounded-2xl">
                                            <BrainCircuit className="h-8 w-8 text-primary" />
                                        </div>
                                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full animate-pulse" />
                                    </div>
                                    <h3 className="text-xl font-semibold">AI-Powered</h3>
                                    <p className="text-muted-foreground leading-relaxed">
                                        Intelligent recommendations and automated insights powered by cutting-edge AI to accelerate your research journey.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="w-full py-12">
                <div className="container px-4 md:px-6">
                    <h2 className="text-3xl font-headline font-bold tracking-tighter mb-12 sm:text-4xl">
                        Explore Our Core Features
                    </h2>
                    <div className="grid grid-cols-1 gap-12">
                        <FeatureCard
                            icon={<Rocket className="h-10 w-10 text-primary" />}
                            title="Machine Learning Lab"
                            description="Upload your data to train, test, and download regression and classification models. Get model recommendations tailored to your dataset."
                            features={[
                                "Automated model selection",
                                "Real-time training visualization",
                                "One-click model deployment",
                                "Performance analytics"
                            ]}
                            imageUrl="https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                            imageHint="machine learning dashboard"
                            comingSoon={false}
                            actionHref="/ml"
                            actionLabel="Open ML Lab"
                        />
                        <FeatureCard
                            icon={<TestTube className="h-10 w-10 text-primary" />}
                            title="Physics Simulation"
                            description="Visualize complex physics equations. Use predefined models or input your own custom equations and variables to see concepts in action."
                            features={[
                                "Interactive 3D visualizations",
                                "Custom equation support",
                                "Real-time parameter adjustment",
                                "Export simulation results"
                            ]}
                            imageUrl="https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                            imageHint="physics simulation visualization"
                            comingSoon={false}
                            actionHref="/simulation"
                            actionLabel="Open Simulation"
                        />
                        <FeatureCard
                            icon={<BrainCircuit className="h-10 w-10 text-primary" />}
                            title="AI Tutor"
                            description="Your personal AI assistant for physics. Get explanations for complex topics and help with your coursework."
                            features={[
                                "24/7 AI assistance",
                                "Personalized learning paths",
                                "Step-by-step explanations",
                                "Interactive problem solving"
                            ]}
                            imageUrl="https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                            imageHint="AI assistant interface"
                            comingSoon={false}
                            actionHref="/ai"
                            actionLabel="Open AI Tutor"
                        />
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="relative w-full py-24 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/15 via-accent/10 to-primary/5" />
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent" />
                <div className="container px-4 md:px-6 text-center relative z-10">
                    <div className="max-w-4xl mx-auto">
                        <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
                            🎯 Start Your Journey Today
                        </div>
                        <h2 className="text-4xl font-headline font-bold tracking-tighter mb-6 sm:text-5xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-primary">
                            Ready to Transform Your Learning?
                        </h2>
                        <p className="max-w-[700px] text-muted-foreground md:text-xl mx-auto mb-8 leading-relaxed">
                            Join thousands of students, researchers, and professionals who are already using PhysicsLab to advance their understanding of physics and machine learning.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                            <SignUpButton>
                                <Button size="lg" className="text-lg px-10 py-4 shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105">
                                    <Users className="mr-2 h-5 w-5" />
                                    Create Your Free Account
                                </Button>
                            </SignUpButton>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Shield className="h-4 w-4" />
                                No credit card required
                            </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
                            <div className="flex flex-col items-center space-y-2">
                                <div className="text-2xl font-bold text-primary">10,000+</div>
                                <div className="text-sm text-muted-foreground">Active Users</div>
                            </div>
                            <div className="flex flex-col items-center space-y-2">
                                <div className="text-2xl font-bold text-accent">99.9%</div>
                                <div className="text-sm text-muted-foreground">Uptime</div>
                            </div>
                            <div className="flex flex-col items-center space-y-2">
                                <div className="text-2xl font-bold text-primary">24/7</div>
                                <div className="text-sm text-muted-foreground">Support</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

function FeatureCard({
    icon,
    title,
    description,
    features,
    imageUrl,
    imageHint,
    comingSoon,
    actionHref,
    actionLabel
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    features: string[];
    imageUrl: string;
    imageHint: string;
    comingSoon: boolean;
    actionHref?: string;
    actionLabel?: string;
}) {
    return (
        <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-500" />
            <Card className="relative w-full max-w-6xl mx-auto overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-500 border-0 bg-card/80 backdrop-blur-sm group-hover:scale-[1.02]">
                <div className="grid md:grid-cols-2">
                    <div className="relative h-80 md:h-auto overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/10 z-10" />
                        <Image
                            src={imageUrl}
                            alt={title}
                            fill
                            style={{ objectFit: 'cover' }}
                            data-ai-hint={imageHint}
                            className="transition-transform duration-500 group-hover:scale-110"
                        />
                        {comingSoon && (
                            <div className="absolute top-6 right-6 bg-gradient-to-r from-accent to-accent/80 text-accent-foreground px-4 py-2 rounded-full text-sm font-medium shadow-lg z-20 animate-pulse">
                                ✨ Coming Soon
                            </div>
                        )}
                        <div className="absolute bottom-6 left-6 z-20">
                            <div className="p-3 bg-card/80 backdrop-blur-sm rounded-2xl shadow-lg">
                                {icon}
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col justify-center p-8 md:p-12 text-left space-y-6">
                        <div className="space-y-3">
                            <CardTitle className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                                {title}
                            </CardTitle>
                            <CardDescription className="text-base md:text-lg leading-relaxed text-muted-foreground">
                                {description}
                            </CardDescription>
                        </div>
                        <div className="space-y-3">
                            {features.map((feature, index) => (
                                <div key={index} className="flex items-center space-x-3 group/item">
                                    <div className="w-3 h-3 bg-gradient-to-r from-primary to-accent rounded-full flex-shrink-0 group-hover/item:scale-125 transition-transform duration-300" />
                                    <span className="text-sm md:text-base text-muted-foreground group-hover/item:text-foreground transition-colors duration-300">
                                        {feature}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="pt-4">
                            {actionHref ? (
                                <Link href={actionHref} className="w-full md:w-auto">
                                    <Button
                                        size="lg"
                                        className="w-full md:w-auto shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90"
                                    >
                                        {actionLabel ?? 'Open'}
                                    </Button>
                                </Link>
                            ) : (
                                <SignUpButton>
                                    <Button
                                        size="lg"
                                        className="w-full md:w-auto shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90"
                                    >
                                        Get Started &rarr;
                                    </Button>
                                </SignUpButton>
                            )}
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}