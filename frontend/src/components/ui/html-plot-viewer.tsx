'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, X, Maximize2, Download, ExternalLink } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface HtmlPlotViewerProps {
    isOpen: boolean;
    onClose: () => void;
    simulationId: string;
    simulationName: string;
    plotTitle?: string;
}

interface ViewResponse {
    success: boolean;
    data?: {
        view_url: string;
        simulation_name: string;
        plot_title?: string;
        expires_in: number;
    };
    message?: string;
    error?: {
        code: string;
        message: string;
    };
}

export default function HtmlPlotViewer({
    isOpen,
    onClose,
    simulationId,
    simulationName,
    plotTitle
}: HtmlPlotViewerProps) {
    const [htmlContent, setHtmlContent] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [viewUrl, setViewUrl] = useState<string>('');
    const [isFullscreen, setIsFullscreen] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        if (isOpen && simulationId) {
            fetchHtmlContent();
        }
    }, [isOpen, simulationId]);

    const fetchHtmlContent = async () => {
        setLoading(true);
        setError(null);

        try {
            // First, get the view URL from the backend
            const { userId } = useAuth();
            const headers: Record<string, string> = {};
            if (userId) headers['X-User-ID'] = userId;

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/simulations/${simulationId}/view?mode=url`,
                { headers }
            );

            const result: ViewResponse = await response.json();

            if (!result.success || !result.data?.view_url) {
                throw new Error(result.error?.message || 'Failed to get view URL');
            }

            setViewUrl(result.data.view_url);

            // Now fetch the HTML content from the Cloudinary URL
            const htmlResponse = await fetch(result.data.view_url);

            if (!htmlResponse.ok) {
                throw new Error(`Failed to fetch HTML content: ${htmlResponse.status}`);
            }

            const htmlText = await htmlResponse.text();
            setHtmlContent(htmlText);

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            toast({
                variant: 'destructive',
                title: 'Failed to load plot',
                description: errorMessage
            });
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (viewUrl) {
            window.open(viewUrl, '_blank');
        }
    };

    const handleOpenExternal = () => {
        if (viewUrl) {
            window.open(viewUrl, '_blank');
        }
    };

    const toggleFullscreen = () => {
        setIsFullscreen(!isFullscreen);
    };

    const handleClose = () => {
        setHtmlContent('');
        setViewUrl('');
        setError(null);
        setIsFullscreen(false);
        onClose();
    };

    return (
        <Dialog open={isOpen} onOpenChange={handleClose}>
            <DialogContent
                className={`${isFullscreen ? 'max-w-[95vw] max-h-[95vh]' : 'max-w-4xl max-h-[80vh]'} p-0`}
            >
                <DialogHeader className="px-6 py-4 border-b">
                    <div className="flex items-center justify-between">
                        <div>
                            <DialogTitle className="text-lg font-semibold">
                                {plotTitle || simulationName}
                            </DialogTitle>
                            {plotTitle && (
                                <p className="text-sm text-muted-foreground mt-1">
                                    {simulationName}
                                </p>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={toggleFullscreen}
                                title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                            >
                                <Maximize2 className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleOpenExternal}
                                disabled={!viewUrl}
                                title="Open in new tab"
                            >
                                <ExternalLink className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleDownload}
                                disabled={!viewUrl}
                                title="Download HTML file"
                            >
                                <Download className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleClose}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </DialogHeader>

                <div className={`${isFullscreen ? 'h-[calc(95vh-80px)]' : 'h-[60vh]'} overflow-hidden`}>
                    {loading && (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                                <p className="text-sm text-muted-foreground">Loading plot...</p>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="flex items-center justify-center h-full p-6">
                            <div className="text-center">
                                <p className="text-destructive font-medium mb-2">Failed to load plot</p>
                                <p className="text-sm text-muted-foreground mb-4">{error}</p>
                                <Button onClick={fetchHtmlContent} size="sm">
                                    Try Again
                                </Button>
                            </div>
                        </div>
                    )}

                    {!loading && !error && htmlContent && (
                        <iframe
                            srcDoc={htmlContent}
                            className="w-full h-full border-0"
                            title={plotTitle || simulationName}
                            sandbox="allow-scripts allow-same-origin"
                        />
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}