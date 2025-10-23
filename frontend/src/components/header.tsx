'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { Menu } from 'lucide-react';
import { useState } from 'react';
import { ThemeToggle } from './theme-toggle';
import {
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs';

const navLinks = [
  { href: '/ml', label: 'ML Lab' },
  { href: '/simulation', label: 'Simulation' },
  { href: '/ai', label: 'AI Tutor' },
  { href: '/docs', label: 'Docs' },
];

export default function Header() {
  const pathname = usePathname();
  const [isSheetOpen, setSheetOpen] = useState(false);

  const closeSheet = () => setSheetOpen(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 hidden md:flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Image
              src="/logo.jpg"
              alt="PhysicsLab Logo"
              width={24}
              height={24}
              className="h-6 w-6 rounded"
            />
            <span className="hidden font-bold sm:inline-block">PhysicsLab</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            {/* Public links */}
            <Link href="/docs" className={cn('transition-colors hover:text-foreground/80', pathname === '/docs' ? 'text-foreground' : 'text-foreground/60')}>
              Docs
            </Link>

            {/* Auth-only links */}
            <SignedIn>
              {navLinks.filter(l => l.href !== '/docs').map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'transition-colors hover:text-foreground/80',
                    pathname === link.href ? 'text-foreground' : 'text-foreground/60'
                  )}
                >
                  {link.label}
                </Link>
              ))}
            </SignedIn>
            <SignedOut>
              {/* Show static labels for unauthenticated users (not clickable) */}
              {navLinks.filter(l => l.href !== '/docs').map((link) => (
                <span key={link.href} className="text-foreground/40 cursor-not-allowed">
                  {link.label}
                </span>
              ))}
            </SignedOut>
          </nav>
        </div>

        <div className="md:hidden">
          <Sheet open={isSheetOpen} onOpenChange={setSheetOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent side="left">
              <Link href="/" className="flex items-center space-x-2" onClick={closeSheet}>
                <Image
                  src="/logo.jpg"
                  alt="PhysicsLab Logo"
                  width={24}
                  height={24}
                  className="h-6 w-6 rounded"
                />
                <span className="font-bold">PhysicsLab</span>
              </Link>
              <div className="mt-8 flex flex-col space-y-4">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={cn(
                      'text-lg transition-colors hover:text-foreground/80',
                      pathname === link.href ? 'text-foreground font-semibold' : 'text-foreground/60'
                    )}
                    onClick={closeSheet}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </SheetContent>
          </Sheet>
        </div>

        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="flex items-center gap-4">
            <SignedOut>
              <Link href="/auth/sign-in">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/sign-up">
                <Button size="sm">
                  Sign Up
                </Button>
              </Link>
            </SignedOut>
            <SignedIn>
              <UserButton
                appearance={{
                  elements: {
                    avatarBox: "h-8 w-8"
                  }
                }}
              />
            </SignedIn>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
}
