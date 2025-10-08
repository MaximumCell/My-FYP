import React from 'react';
import Link from 'next/link';
import { Logo } from './icons';
import { Instagram, Facebook, Linkedin, Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-muted/80 text-muted-foreground mt-16">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* About Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Logo className="h-8 w-8 text-primary" />
              <h3 className="text-xl font-bold text-foreground">PhysicsLab</h3>
            </div>
            <p>
              An integrated environment for advanced machine learning and physics simulations.
            </p>
          </div>

          {/* Quick Links Section */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/ml" className="hover:text-primary transition-colors">
                  Machine Learning
                </Link>
              </li>
              <li>
                <Link href="/simulation" className="hover:text-primary transition-colors">
                  Physics Simulations
                </Link>
              </li>
              <li>
                <Link href="/ai" className="hover:text-primary transition-colors">
                  AI Tutor
                </Link>
              </li>
            </ul>
          </div>

          {/* Social Media Section */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground">Follow Us</h3>
            <div className="flex space-x-4">
              <a
                href="https://www.instagram.com/maximum_cell/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                <Instagram className="h-6 w-6" />
              </a>
              <a
                href="https://www.facebook.com/profile.php?id=100040370710046"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                <Facebook className="h-6 w-6" />
              </a>
              <a
                href="https://www.linkedin.com/in/ali-hassan-36a43b318/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                <Linkedin className="h-6 w-6" />
              </a>
              <a
                href="https://github.com/MaximumCell"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                <Github className="h-6 w-6" />
              </a>
            </div>
          </div>

          {/* Contact Section */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground">Contact Us</h3>
            <ul className="space-y-2">
              <li>Email: <a href="mailto:alihassanwinner@gmail.com" className="hover:text-primary">alihassanwinner@gmail.com</a></li>
              <li>Phone: +1 (123) 456-7890</li>
            </ul>
          </div>
        </div>

        {/* Copyright Section */}
        <div className="border-t border-border mt-8 pt-8 text-center">
          <p>
            &copy; {new Date().getFullYear()} PhysicsLab. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
