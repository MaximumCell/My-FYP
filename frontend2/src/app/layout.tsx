import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';
import { cn } from '@/lib/utils';
import Providers from '@/components/providers';
import Header from '@/components/header';
import Footer from '@/components/footer';

export const metadata: Metadata = {
  title: 'PhysicsLab',
  description: 'An advanced platform for ML and physics simulations.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <head>
          <link rel="icon" href="/favicon.ico" type="image/x-icon" />
          <link rel="icon" href="/logo.jpg?v=1" type="image/jpeg" />
          <link rel="apple-touch-icon" href="/logo.jpg" />
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
          <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap"
            rel="stylesheet"
          />
        </head>
        <body className={cn('font-body antialiased min-h-screen flex flex-col')}>
          <Providers>
            <Header />
            <main className="flex-grow container mx-auto px-4 py-8">
              {children}
            </main>
            <Footer />
          </Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
