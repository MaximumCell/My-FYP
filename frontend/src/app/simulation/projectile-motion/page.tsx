"use client";
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

export default function ProjectileMotionPage() {
    return (
        <div className="p-6">
            <div className="mb-6">
                <Link href="/simulation" className="flex items-center text-sm text-primary hover:underline"><ArrowLeft className="mr-2 h-4 w-4" />Back to Simulations</Link>
            </div>
            <Card>
                <CardHeader>
                    <CardTitle>2D Projectile Motion</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">Simulate projectile motion with initial speed, angle and gravity. Placeholder page for later UI and backend integration.</p>
                </CardContent>
            </Card>
        </div>
    );
}
