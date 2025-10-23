'use client';

import React from 'react';
import { SignUp } from '@clerk/nextjs';
import Link from 'next/link';

export default function SignUpPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
            <div className="w-full max-w-md">
                {/* Header Section */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                        PhysicsLab
                    </h1>
                    <p className="text-gray-400 text-lg">Join our physics learning community</p>
                </div>

                {/* Sign-Up Card */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl shadow-2xl p-8 mb-6">
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-white mb-2">Create Your Account</h2>
                        <p className="text-gray-400">Get started with advanced physics learning and simulations</p>
                    </div>

                    {/* Clerk Sign-Up Component */}
                    <div className="[&>div]:w-full [&>div]:max-w-none">
                        <SignUp
                            appearance={{
                                elements: {
                                    rootBox: 'w-full',
                                    card: 'bg-transparent border-0 shadow-none',
                                    formButtonPrimary:
                                        'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-2 rounded-lg transition-all duration-200 w-full',
                                    formFieldInput:
                                        'bg-slate-700 border border-slate-600 text-white placeholder-gray-400 rounded-lg focus:bg-slate-600 focus:border-blue-400 focus:outline-none',
                                    formFieldLabel: 'text-gray-300 font-medium',
                                    footerActionLink: 'text-blue-400 hover:text-blue-300 font-medium',
                                    dividerLine: 'bg-slate-600',
                                    dividerText: 'text-gray-400',
                                    socialButtonsBlockButton:
                                        'border border-slate-600 bg-slate-700 hover:bg-slate-600 text-white rounded-lg',
                                    socialButtonsBlockButtonText: 'font-medium',
                                    headerTitle: 'hidden',
                                    headerSubtitle: 'hidden',
                                    identifierInputField:
                                        'bg-slate-700 border border-slate-600 text-white rounded-lg focus:bg-slate-600 focus:border-blue-400',
                                },
                            }}
                            redirectUrl="/ai"
                            routing="path"
                            path="/auth/sign-up"
                            signInUrl="/auth/sign-in"
                        />
                    </div>
                </div>

                {/* Features Section */}
                <div className="bg-slate-700/30 border border-slate-600/30 rounded-xl p-6">
                    <h3 className="text-white font-semibold mb-4">Why join PhysicsLab?</h3>
                    <ul className="space-y-3">
                        <li className="flex items-start">
                            <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-gray-300">AI-powered physics tutoring</span>
                        </li>
                        <li className="flex items-start">
                            <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-gray-300">Interactive simulations</span>
                        </li>
                        <li className="flex items-start">
                            <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-gray-300">Personalized learning path</span>
                        </li>
                        <li className="flex items-start">
                            <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-gray-300">Community support</span>
                        </li>
                    </ul>
                </div>

                {/* Footer Text */}
                <p className="text-center text-gray-400 text-sm mt-6">
                    Already have an account?{' '}
                    <Link href="/auth/sign-in" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                        Sign in here
                    </Link>
                </p>
            </div>
        </div>
    );
}
