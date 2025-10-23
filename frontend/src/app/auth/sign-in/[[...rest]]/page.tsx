'use client';

import React from 'react';
import { SignIn } from '@clerk/nextjs';
import Link from 'next/link';

export default function SignInPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
            <div className="w-full max-w-md">
                {/* Header Section */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                        PhysicsLab
                    </h1>
                    <p className="text-gray-400 text-lg">Welcome back</p>
                </div>

                {/* Sign-In Card */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl shadow-2xl p-8 mb-6">
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-white mb-2">Sign In</h2>
                        <p className="text-gray-400">Continue your physics learning journey</p>
                    </div>

                    {/* Clerk Sign-In Component */}
                    <div className="[&>div]:w-full [&>div]:max-w-none">
                        <SignIn
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
                                    formResendCodeLink: 'text-blue-400 hover:text-blue-300',
                                },
                            }}
                            redirectUrl="/ai"
                            routing="path"
                            path="/auth/sign-in"
                            signUpUrl="/auth/sign-up"
                        />
                    </div>
                </div>

                {/* Security Info */}
                <div className="bg-blue-900/20 border border-blue-700/30 rounded-xl p-4 mb-6">
                    <div className="flex items-start">
                        <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="text-blue-300 text-sm font-medium">Secure Login</p>
                            <p className="text-blue-200/70 text-xs">Your data is protected with industry-standard encryption</p>
                        </div>
                    </div>
                </div>

                {/* Footer Text */}
                <div className="space-y-2 text-center">
                    <p className="text-gray-400 text-sm">
                        Don't have an account?{' '}
                        <Link href="/auth/sign-up" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                            Create one now
                        </Link>
                    </p>
                    <p className="text-gray-500 text-xs">
                        <Link href="/" className="hover:text-gray-400 transition-colors">
                            Back to home
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
