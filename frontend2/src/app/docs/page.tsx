'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
    Book,
    Rocket,
    Database,
    Brain,
    Zap,
    Code,
    Globe,
    Shield,
    Gauge,
    Cloud,
    Users,
    ChevronRight,
    ExternalLink,
    Copy,
    Check,
    Server,
    Layers,
    Activity,
    BarChart3,
    FileCode,
    Settings,
    Download,
    Upload,
    Play,
    TestTube2,
    Cpu,
    Network,
    Github
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useToast } from '@/hooks/use-toast';

const PhysicsLabDocs = () => {
    const [copiedCode, setCopiedCode] = useState<string | null>(null);
    const { toast } = useToast();

    const copyToClipboard = async (text: string, id: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedCode(id);
            setTimeout(() => setCopiedCode(null), 2000);
            toast({
                title: "Copied to clipboard",
                description: "Code snippet has been copied successfully.",
            });
        } catch (err) {
            toast({
                variant: "destructive",
                title: "Failed to copy",
                description: "Could not copy to clipboard.",
            });
        }
    };

    const CodeBlock = ({ code, language = 'javascript', id }: { code: string; language?: string; id: string }) => (
        <div className="relative group">
            <Button
                variant="ghost"
                size="sm"
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => copyToClipboard(code, id)}
            >
                {copiedCode === id ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
            <SyntaxHighlighter
                language={language}
                style={oneDark}
                customStyle={{
                    margin: 0,
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
            {/* Hero Section */}
            <div className="relative overflow-hidden border-b bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5">
                <div className="absolute inset-0 bg-grid-white/10" />
                <div className="relative max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <div className="inline-flex items-center gap-3 mb-6 px-4 py-2 bg-primary/10 rounded-full border">
                            <Rocket className="h-5 w-5 text-primary" />
                            <span className="text-sm font-medium text-primary">PhysicsLab v1.0</span>
                        </div>
                        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-6">
                            PhysicsLab Documentation
                        </h1>
                        <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
                            A comprehensive platform for physics simulations, machine learning experiments, and educational tools.
                            Build, train, and deploy ML models while exploring interactive physics simulations.
                        </p>
                        <div className="flex flex-wrap justify-center gap-4">
                            <Button size="lg" className="gap-2" onClick={() => window.location.href = '/'}>
                                <Book className="h-4 w-4" />
                                Get Started
                            </Button>
                            <Button variant="outline" size="lg" className="gap-2" onClick={() => window.open('https://github.com/MaximumCell/My-FYP', '_blank')}>
                                <Github className="h-4 w-4" />
                                View on GitHub
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    <Card className="text-center">
                        <CardContent className="pt-6">
                            <Brain className="h-8 w-8 mx-auto mb-3 text-blue-500" />
                            <div className="text-2xl font-bold">15+</div>
                            <div className="text-sm text-muted-foreground">ML Models</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="pt-6">
                            <Zap className="h-8 w-8 mx-auto mb-3 text-yellow-500" />
                            <div className="text-2xl font-bold">8+</div>
                            <div className="text-sm text-muted-foreground">Simulations</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="pt-6">
                            <Server className="h-8 w-8 mx-auto mb-3 text-green-500" />
                            <div className="text-2xl font-bold">25+</div>
                            <div className="text-sm text-muted-foreground">API Endpoints</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="pt-6">
                            <Cloud className="h-8 w-8 mx-auto mb-3 text-purple-500" />
                            <div className="text-2xl font-bold">100%</div>
                            <div className="text-sm text-muted-foreground">Cloud Ready</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Main Content */}
                <Tabs defaultValue="overview" className="w-full">
                    <TabsList className="grid w-full grid-cols-7">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="ml">ML Lab</TabsTrigger>
                        <TabsTrigger value="simulation">Simulations</TabsTrigger>
                        <TabsTrigger value="api">API Reference</TabsTrigger>
                        <TabsTrigger value="architecture">Architecture</TabsTrigger>
                        <TabsTrigger value="deployment">Deployment</TabsTrigger>
                        <TabsTrigger value="ai">AI Tutor</TabsTrigger>
                    </TabsList>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Layers className="h-5 w-5" />
                                    Platform Overview
                                </CardTitle>
                                <CardDescription>
                                    PhysicsLab is a modern educational platform that combines machine learning and physics simulations
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Core Features</h3>
                                        <div className="space-y-3">
                                            <div className="flex items-start gap-3">
                                                <Brain className="h-5 w-5 text-blue-500 mt-0.5" />
                                                <div>
                                                    <div className="font-medium">Machine Learning Lab</div>
                                                    <div className="text-sm text-muted-foreground">Train regression, classification, and deep learning models</div>
                                                </div>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <Zap className="h-5 w-5 text-yellow-500 mt-0.5" />
                                                <div>
                                                    <div className="font-medium">Physics Simulations</div>
                                                    <div className="text-sm text-muted-foreground">Interactive Matter.js and custom equation simulations</div>
                                                </div>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <BarChart3 className="h-5 w-5 text-green-500 mt-0.5" />
                                                <div>
                                                    <div className="font-medium">Analytics Dashboard</div>
                                                    <div className="text-sm text-muted-foreground">Track usage, performance metrics, and progress</div>
                                                </div>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <Cloud className="h-5 w-5 text-purple-500 mt-0.5" />
                                                <div>
                                                    <div className="font-medium">Cloud Storage</div>
                                                    <div className="text-sm text-muted-foreground">Cloudinary integration for model and simulation storage</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Technology Stack</h3>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="p-3 border rounded-lg">
                                                <div className="font-medium text-sm">Frontend</div>
                                                <div className="text-xs text-muted-foreground">Next.js, React, TypeScript</div>
                                            </div>
                                            <div className="p-3 border rounded-lg">
                                                <div className="font-medium text-sm">Backend</div>
                                                <div className="text-xs text-muted-foreground">Python, Flask, FastAPI</div>
                                            </div>
                                            <div className="p-3 border rounded-lg">
                                                <div className="font-medium text-sm">Database</div>
                                                <div className="text-xs text-muted-foreground">MongoDB</div>
                                            </div>
                                            <div className="p-3 border rounded-lg">
                                                <div className="font-medium text-sm">ML</div>
                                                <div className="text-xs text-muted-foreground">scikit-learn, TensorFlow</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Start Guide</CardTitle>
                                <CardDescription>Get up and running in minutes</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">1</div>
                                        <div>
                                            <div className="font-medium">Set up Authentication</div>
                                            <div className="text-sm text-muted-foreground">Sign up with Clerk authentication system</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">2</div>
                                        <div>
                                            <div className="font-medium">Upload Your Data</div>
                                            <div className="text-sm text-muted-foreground">Upload CSV files for ML training or create custom simulations</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">3</div>
                                        <div>
                                            <div className="font-medium">Train & Simulate</div>
                                            <div className="text-sm text-muted-foreground">Train ML models or run physics simulations</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">4</div>
                                        <div>
                                            <div className="font-medium">Analyze Results</div>
                                            <div className="text-sm text-muted-foreground">View analytics and download results from your dashboard</div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* AI Tutor Tab */}
                    <TabsContent value="ai" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Brain className="h-5 w-5" />
                                    AI Tutor Integration
                                </CardTitle>
                                <CardDescription>
                                    Details about the Physics AI Tutor endpoints, payloads, example requests, and model capabilities.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <h3 className="text-lg font-semibold">Available Endpoints</h3>
                                        <ul className="text-sm space-y-2 mt-3">
                                            <li className="flex items-start gap-3">
                                                <code className="text-xs">POST /api/physics/ask</code>
                                                <span className="text-muted-foreground">— Full-featured Q&A (RAG, preferences, image analysis)</span>
                                            </li>
                                            <li className="flex items-start gap-3">
                                                <code className="text-xs">POST /api/physics/quick-ask</code>
                                                <span className="text-muted-foreground">— Fast, lightweight responses</span>
                                            </li>
                                            <li className="flex items-start gap-3">
                                                <code className="text-xs">POST /api/physics/derivation</code>
                                                <span className="text-muted-foreground">— Step-by-step derivations</span>
                                            </li>
                                            <li className="flex items-start gap-3">
                                                <code className="text-xs">POST /api/physics/explain</code>
                                                <span className="text-muted-foreground">— Level-specific explanations</span>
                                            </li>
                                            <li className="flex items-start gap-3">
                                                <code className="text-xs">GET /api/physics/stats</code>
                                                <span className="text-muted-foreground">— Tutor usage & performance stats</span>
                                            </li>
                                        </ul>
                                    </div>

                                    <div>
                                        <h3 className="text-lg font-semibold">Model Capabilities</h3>
                                        <p className="text-sm text-muted-foreground mt-3">
                                            The AI Tutor uses Google Gemini models (text + vision) with a supervisor model for quality evaluation and can perform RAG using the Qdrant vector DB when available.
                                        </p>
                                        <div className="mt-4 grid grid-cols-1 gap-2 text-sm">
                                            <div className="flex items-center gap-2"><strong>Primary:</strong> gemini-2.0-flash-exp</div>
                                            <div className="flex items-center gap-2"><strong>Vision:</strong> gemini-2.0-flash</div>
                                            <div className="flex items-center gap-2"><strong>Supervisor:</strong> gemini-2.0-pro</div>
                                            <div className="flex items-center gap-2"><strong>Vector DB:</strong> Qdrant (optional)</div>
                                        </div>
                                    </div>
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Example: Ask (Full)</h3>
                                    <p className="text-sm text-muted-foreground">This sends user preferences and optional context for RAG.</p>
                                    <CodeBlock
                                        id="ai-ask-example"
                                        language="javascript"
                                        code={`fetch('/api/physics/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_CLERK_TOKEN' },
  body: JSON.stringify({
    question: 'Explain conservation of energy',
    preferences: { difficulty_level: 'intermediate', response_length: 'medium' },
    include_user_materials: true
  })
}).then(r => r.json()).then(console.log);`}
                                    />

                                    <h4 className="text-sm font-semibold">Typical Response (abridged)</h4>
                                    <CodeBlock
                                        id="ai-ask-response"
                                        language="json"
                                        code={`{
  "response": "Conservation of energy states that...",
  "classification": {"category":"concept","topic":"mechanics","difficulty":"intermediate"},
  "metadata": {"category":"concept","difficulty_level":"intermediate","response_length":"medium","timestamp":"2025-10-01T12:34:56"}
}`}
                                    />
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Example: Image Analysis</h3>
                                    <p className="text-sm text-muted-foreground">Send an image description or image path for diagram/graph analysis.</p>
                                    <CodeBlock
                                        id="ai-image-example"
                                        language="javascript"
                                        code={`fetch('/api/physics/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_CLERK_TOKEN' },
  body: JSON.stringify({
    question: 'What physics concepts are shown?',
    context: { image_description: 'A free body diagram showing forces on an inclined plane' }
  })
}).then(r => r.json()).then(console.log);`}
                                    />
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Quick Links</h3>
                                    <div className="flex flex-wrap gap-3">
                                        <Button size="sm" onClick={() => window.location.href = '/ai'}>
                                            Open AI Chat
                                        </Button>
                                        <Button variant="outline" size="sm" onClick={() => window.open('https://github.com/MaximumCell/My-FYP', '_blank')}>
                                            View Backend Docs
                                        </Button>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* ML Lab Tab */}
                    <TabsContent value="ml" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Brain className="h-5 w-5" />
                                    Machine Learning Laboratory
                                </CardTitle>
                                <CardDescription>
                                    Train, test, and deploy machine learning models with our comprehensive ML platform
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Card className="p-4">
                                        <div className="flex items-center gap-3 mb-3">
                                            <Activity className="h-5 w-5 text-blue-500" />
                                            <h4 className="font-medium">Regression Models</h4>
                                        </div>
                                        <ul className="space-y-1 text-sm text-muted-foreground">
                                            <li>• Linear Regression</li>
                                            <li>• Random Forest</li>
                                            <li>• Gradient Boosting</li>
                                            <li>• Lasso Regression</li>
                                            <li>• Ridge Regression</li>
                                        </ul>
                                    </Card>
                                    <Card className="p-4">
                                        <div className="flex items-center gap-3 mb-3">
                                            <TestTube2 className="h-5 w-5 text-green-500" />
                                            <h4 className="font-medium">Classification</h4>
                                        </div>
                                        <ul className="space-y-1 text-sm text-muted-foreground">
                                            <li>• Logistic Regression</li>
                                            <li>• Random Forest</li>
                                            <li>• SVM</li>
                                            <li>• Naive Bayes</li>
                                            <li>• Decision Trees</li>
                                        </ul>
                                    </Card>
                                    <Card className="p-4">
                                        <div className="flex items-center gap-3 mb-3">
                                            <Cpu className="h-5 w-5 text-purple-500" />
                                            <h4 className="font-medium">Deep Learning</h4>
                                        </div>
                                        <ul className="space-y-1 text-sm text-muted-foreground">
                                            <li>• Neural Networks (MLP)</li>
                                            <li>• CNN for Images</li>
                                            <li>• Custom Architectures</li>
                                            <li>• Transfer Learning</li>
                                            <li>• Model Optimization</li>
                                        </ul>
                                    </Card>
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Training Workflow</h3>
                                    <CodeBlock
                                        id="ml-workflow"
                                        language="python"
                                        code={`# Example: Training a regression model
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# 1. Upload CSV data via the web interface
# 2. Select target column and features
# 3. Choose model type (regression/classification)
# 4. Configure hyperparameters
# 5. Train model

# The platform handles:
data = pd.read_csv('your_data.csv')
X = data.drop('target', axis=1)
y = data['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Automatic performance metrics calculation
# Model saved to Cloudinary with metadata
# Results displayed in dashboard`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Model Features</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2">
                                                <Upload className="h-4 w-4 text-blue-500" />
                                                <span className="font-medium">Automatic Model Storage</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <BarChart3 className="h-4 w-4 text-green-500" />
                                                <span className="font-medium">Performance Metrics</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Download className="h-4 w-4 text-purple-500" />
                                                <span className="font-medium">Model Download</span>
                                            </div>
                                        </div>
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2">
                                                <TestTube2 className="h-4 w-4 text-orange-500" />
                                                <span className="font-medium">Model Testing</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Brain className="h-4 w-4 text-pink-500" />
                                                <span className="font-medium">Model Recommendations</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Activity className="h-4 w-4 text-cyan-500" />
                                                <span className="font-medium">Real-time Analytics</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Simulation Tab */}
                    <TabsContent value="simulation" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Zap className="h-5 w-5" />
                                    Physics Simulations
                                </CardTitle>
                                <CardDescription>
                                    Interactive physics simulations powered by Matter.js and custom equation solvers
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Matter.js Simulations</h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                                    <Activity className="h-4 w-4 text-blue-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Pendulum Simulation</div>
                                                    <div className="text-sm text-muted-foreground">Simple and compound pendulum physics</div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                                    <Zap className="h-4 w-4 text-green-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Collision Dynamics</div>
                                                    <div className="text-sm text-muted-foreground">Elastic and inelastic collisions</div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                                    <Play className="h-4 w-4 text-purple-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Projectile Motion</div>
                                                    <div className="text-sm text-muted-foreground">Ballistic trajectories with gravity</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Custom Equations</h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                                                    <FileCode className="h-4 w-4 text-orange-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Linear Motion</div>
                                                    <div className="text-sm text-muted-foreground">y = mx + c equations</div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                                                    <Activity className="h-4 w-4 text-red-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Quadratic Motion</div>
                                                    <div className="text-sm text-muted-foreground">y = ax² + bx + c equations</div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 p-3 border rounded-lg">
                                                <div className="w-8 h-8 bg-cyan-100 rounded-lg flex items-center justify-center">
                                                    <Network className="h-4 w-4 text-cyan-600" />
                                                </div>
                                                <div>
                                                    <div className="font-medium">Harmonic Motion</div>
                                                    <div className="text-sm text-muted-foreground">y = A·sin(ωx + φ) equations</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Simulation Configuration</h3>
                                    <CodeBlock
                                        id="simulation-config"
                                        language="javascript"
                                        code={`// Example: Custom equation simulation
const simulationConfig = {
  equation: "Linear Motion (y = m*x + c)",
  variables: [
    { key: 'm', value: 2.5 },
    { key: 'c', value: 1.0 }
  ],
  x_min: 0,
  x_max: 10,
  plot_type: "2d"
};

// Matter.js simulation
const matterConfig = {
  simulation_type: "pendulum",
  parameters: {
    length: 200,
    mass: 10,
    gravity: 0.8,
    angle: 45
  },
  canvas_size: { width: 800, height: 600 }
};

// The platform automatically:
// - Generates interactive visualizations
// - Saves results to cloud storage
// - Provides download options
// - Tracks simulation analytics`}
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* API Reference Tab */}
                    <TabsContent value="api" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Server className="h-5 w-5" />
                                    API Reference
                                </CardTitle>
                                <CardDescription>
                                    Complete API documentation for integrating with PhysicsLab
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Card className="p-4">
                                        <h4 className="font-medium mb-3 flex items-center gap-2">
                                            <Users className="h-4 w-4 text-blue-500" />
                                            User Management
                                        </h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">POST</span>
                                                <Badge variant="outline">Auth</Badge>
                                            </div>
                                            <code className="text-xs">/api/users/sync</code>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">GET</span>
                                                <Badge variant="outline">Data</Badge>
                                            </div>
                                            <code className="text-xs">/api/users/dashboard</code>
                                        </div>
                                    </Card>
                                    <Card className="p-4">
                                        <h4 className="font-medium mb-3 flex items-center gap-2">
                                            <Brain className="h-4 w-4 text-green-500" />
                                            ML Models
                                        </h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">POST</span>
                                                <Badge variant="outline">Upload</Badge>
                                            </div>
                                            <code className="text-xs">/api/models/upload</code>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">GET</span>
                                                <Badge variant="outline">List</Badge>
                                            </div>
                                            <code className="text-xs">/api/models</code>
                                        </div>
                                    </Card>
                                    <Card className="p-4">
                                        <h4 className="font-medium mb-3 flex items-center gap-2">
                                            <Zap className="h-4 w-4 text-purple-500" />
                                            Simulations
                                        </h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">POST</span>
                                                <Badge variant="outline">Run</Badge>
                                            </div>
                                            <code className="text-xs">/api/simulation/matter</code>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">GET</span>
                                                <Badge variant="outline">Results</Badge>
                                            </div>
                                            <code className="text-xs">/api/simulations</code>
                                        </div>
                                    </Card>
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Authentication</h3>
                                    <CodeBlock
                                        id="auth-example"
                                        language="javascript"
                                        code={`// All API requests require authentication
const headers = {
  'Authorization': 'Bearer YOUR_CLERK_TOKEN',
  'X-User-ID': 'your_user_id',
  'Content-Type': 'application/json'
};

// Example: Fetch user models
fetch('/api/models', {
  method: 'GET',
  headers: headers
})
.then(response => response.json())
.then(data => console.log(data));`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Model Upload Example</h3>
                                    <CodeBlock
                                        id="model-upload"
                                        language="javascript"
                                        code={`// Upload a trained ML model
const formData = new FormData();
formData.append('model_file', modelFile);
formData.append('model_name', 'House Price Predictor');
formData.append('model_type', 'regression');
formData.append('dataset_info', JSON.stringify({
  columns: ['bedrooms', 'bathrooms', 'sqft'],
  target_column: 'price',
  data_shape: { rows: 1000, columns: 4 }
}));
formData.append('performance_metrics', JSON.stringify({
  mse: 0.05,
  r2_score: 0.95,
  mae: 0.03
}));
formData.append('training_time', '45.2');

fetch('/api/models/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_CLERK_TOKEN',
    'X-User-ID': 'your_user_id'
  },
  body: formData
})`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Simulation API Example</h3>
                                    <CodeBlock
                                        id="simulation-api"
                                        language="javascript"
                                        code={`// Run a custom equation simulation
const simulationData = {
  mode: 'equation',
  equation: '2*x + 1',
  x_min: 0,
  x_max: 10
};

fetch('/api/simulation/plot', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_CLERK_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(simulationData)
})
.then(response => response.json())
.then(result => {
  console.log('Plot URL:', result.png_url);
  console.log('HTML URL:', result.html_url);
});

// Run a Matter.js physics simulation
const matterData = {
  simulation_type: 'pendulum',
  parameters: {
    length: 200,
    mass: 10,
    gravity: 0.8
  }
};

fetch('/api/simulation/matter', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(matterData)
})`}
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Architecture Tab */}
                    <TabsContent value="architecture" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Server className="h-5 w-5" />
                                    System Architecture
                                </CardTitle>
                                <CardDescription>
                                    Technical overview of PhysicsLab's architecture and components
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Backend Architecture</h3>
                                        <div className="space-y-3">
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Server className="h-4 w-4 text-blue-500" />
                                                    Flask Application Server
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• RESTful API endpoints</li>
                                                    <li>• CORS enabled for frontend</li>
                                                    <li>• Blueprint-based routing</li>
                                                    <li>• Error handling & validation</li>
                                                </ul>
                                            </div>
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Database className="h-4 w-4 text-green-500" />
                                                    MongoDB Database
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• Users collection</li>
                                                    <li>• ML models metadata</li>
                                                    <li>• Simulations data</li>
                                                    <li>• Analytics tracking</li>
                                                </ul>
                                            </div>
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Cloud className="h-4 w-4 text-purple-500" />
                                                    Cloudinary Storage
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• Model file storage (.pkl)</li>
                                                    <li>• Simulation plots (HTML/PNG)</li>
                                                    <li>• CDN delivery</li>
                                                    <li>• Automatic cleanup</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Frontend Architecture</h3>
                                        <div className="space-y-3">
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Globe className="h-4 w-4 text-blue-500" />
                                                    Next.js Application
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• Server-side rendering</li>
                                                    <li>• App router architecture</li>
                                                    <li>• TypeScript support</li>
                                                    <li>• Optimized performance</li>
                                                </ul>
                                            </div>
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Shield className="h-4 w-4 text-green-500" />
                                                    Clerk Authentication
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• Secure user management</li>
                                                    <li>• JWT token handling</li>
                                                    <li>• Session management</li>
                                                    <li>• Protected routes</li>
                                                </ul>
                                            </div>
                                            <div className="p-4 border rounded-lg">
                                                <div className="font-medium mb-2 flex items-center gap-2">
                                                    <Gauge className="h-4 w-4 text-purple-500" />
                                                    TanStack Query
                                                </div>
                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                    <li>• Data fetching & caching</li>
                                                    <li>• Optimistic updates</li>
                                                    <li>• Background refetching</li>
                                                    <li>• Error boundaries</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <Separator />

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Database Schema</h3>
                                    <CodeBlock
                                        id="db-schema"
                                        language="javascript"
                                        code={`// MongoDB Collections Structure

// Users Collection
{
  _id: ObjectId,
  clerk_user_id: String (unique),
  email: String,
  name: String,
  created_at: Date,
  updated_at: Date,
  usage_analytics: {
    total_models_trained: Number,
    total_simulations_run: Number,
    total_training_time: Number,
    last_activity: Date
  }
}

// ML Models Collection
{
  _id: ObjectId,
  user_id: ObjectId,
  model_name: String,
  model_type: String, // 'regression' | 'classification' | 'deep-learning'
  file_url: String, // Cloudinary URL
  file_public_id: String,
  dataset_info: {
    columns: Array,
    target_column: String,
    data_shape: { rows: Number, columns: Number }
  },
  performance_metrics: {
    accuracy: Number,
    precision: Number,
    recall: Number,
    f1_score: Number,
    mse: Number,
    r2_score: Number
  },
  training_time: Number,
  algorithm_name: String,
  hyperparameters: Object,
  is_public: Boolean,
  created_at: Date
}

// Simulations Collection
{
  _id: ObjectId,
  user_id: ObjectId,
  simulation_name: String,
  simulation_type: String,
  config: {
    equation: String,
    parameters: Object,
    variables: Array
  },
  plot_html_url: String, // Cloudinary URL
  plot_png_url: String,
  plot_public_id: String,
  execution_time: Number,
  is_public: Boolean,
  created_at: Date
}`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Security & Performance</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-medium mb-3 flex items-center gap-2">
                                                <Shield className="h-4 w-4 text-green-500" />
                                                Security Features
                                            </h4>
                                            <ul className="text-sm text-muted-foreground space-y-1">
                                                <li>• JWT-based authentication</li>
                                                <li>• File upload validation</li>
                                                <li>• CORS protection</li>
                                                <li>• Input sanitization</li>
                                                <li>• Rate limiting</li>
                                            </ul>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-medium mb-3 flex items-center gap-2">
                                                <Gauge className="h-4 w-4 text-blue-500" />
                                                Performance Optimizations
                                            </h4>
                                            <ul className="text-sm text-muted-foreground space-y-1">
                                                <li>• MongoDB indexing</li>
                                                <li>• Cloudinary CDN</li>
                                                <li>• Response caching</li>
                                                <li>• Lazy loading</li>
                                                <li>• Code splitting</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Deployment Tab */}
                    <TabsContent value="deployment" className="space-y-8">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Rocket className="h-5 w-5" />
                                    Deployment Guide
                                </CardTitle>
                                <CardDescription>
                                    Step-by-step guide to deploy PhysicsLab in production
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Environment Setup</h3>
                                    <CodeBlock
                                        id="env-vars"
                                        language="bash"
                                        code={`# Backend Environment Variables (.env)
MONGODB_URI=mongodb://localhost:27017/physicslab
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLERK_SECRET_KEY=your_clerk_secret
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=pkl,html,png

# Frontend Environment Variables (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Backend Deployment</h3>
                                    <CodeBlock
                                        id="backend-deploy"
                                        language="bash"
                                        code={`# 1. Clone and setup backend
git clone <repository>
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
python -c "from utils.database import init_database; init_database()"

# 6. Run the application
python app.py

# Production deployment with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Frontend Deployment</h3>
                                    <CodeBlock
                                        id="frontend-deploy"
                                        language="bash"
                                        code={`# 1. Setup frontend
cd frontend2

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# 4. Build for production
npm run build

# 5. Start production server
npm start

# Deploy to Vercel
npm install -g vercel
vercel --prod

# Deploy to Netlify
npm run build
# Upload dist folder to Netlify`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Docker Deployment</h3>
                                    <CodeBlock
                                        id="docker-deploy"
                                        language="dockerfile"
                                        code={`# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

# Frontend Dockerfile  
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]

# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/physicslab
    depends_on:
      - mongo
      
  frontend:
    build: ./frontend2
    ports:
      - "3000:3000"
    depends_on:
      - backend
      
  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      
volumes:
  mongo_data:`}
                                    />
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Production Checklist</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-3">
                                            <h4 className="font-medium">Security</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>SSL certificates configured</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>Environment variables secured</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>Database access restricted</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>CORS properly configured</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="space-y-3">
                                            <h4 className="font-medium">Performance</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>Database indexes created</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>CDN configured</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>Caching implemented</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-4 h-4 border rounded flex items-center justify-center">
                                                        <Check className="h-3 w-3" />
                                                    </div>
                                                    <span>Load balancing setup</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
};

export default PhysicsLabDocs;