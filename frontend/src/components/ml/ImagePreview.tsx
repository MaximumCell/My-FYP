/**
 * Image Preview Component
 * Displays image previews and metadata for CNN training
 */

'use client';

import { useState } from 'react';
import { ImageIcon, ZoomIn, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import Image from 'next/image';

interface ImagePreviewProps {
    src: string;
    alt: string;
    className?: string;
    width?: number;
    height?: number;
    metadata?: {
        filename?: string;
        size?: string;
        dimensions?: string;
        format?: string;
    };
}

interface ImageGridProps {
    images: Array<{
        src: string;
        alt: string;
        metadata?: ImagePreviewProps['metadata'];
    }>;
    className?: string;
    maxImages?: number;
}

interface ClassImageGridProps {
    classes: Array<{
        name: string;
        count: number;
        sampleImages?: Array<{
            src: string;
            alt: string;
        }>;
    }>;
    className?: string;
}

export function ImagePreview({
    src,
    alt,
    className = '',
    width = 200,
    height = 200,
    metadata
}: ImagePreviewProps) {
    return (
        <Dialog>
            <DialogTrigger asChild>
                <div className={`relative group cursor-pointer rounded-lg overflow-hidden border bg-muted hover:bg-muted/80 transition-colors ${className}`}>
                    <div style={{ width, height }} className="relative">
                        <Image
                            src={src}
                            alt={alt}
                            fill
                            className="object-cover"
                            sizes={`${width}px`}
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                            <ZoomIn className="h-6 w-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                    </div>
                    {metadata && (
                        <div className="p-2 space-y-1">
                            <p className="text-xs font-medium truncate">{metadata.filename}</p>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                {metadata.dimensions && <span>{metadata.dimensions}</span>}
                                {metadata.format && <Badge variant="outline" className="text-xs">{metadata.format}</Badge>}
                            </div>
                        </div>
                    )}
                </div>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <ImageIcon className="h-5 w-5" />
                        Image Preview
                    </DialogTitle>
                    <DialogDescription>
                        {alt}
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                    <div className="relative w-full max-h-96 bg-muted rounded-lg overflow-hidden">
                        <Image
                            src={src}
                            alt={alt}
                            width={800}
                            height={600}
                            className="object-contain w-full h-auto max-h-96"
                        />
                    </div>
                    {metadata && (
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-base flex items-center gap-2">
                                    <Info className="h-4 w-4" />
                                    Image Information
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    {metadata.filename && (
                                        <div>
                                            <span className="text-muted-foreground">Filename:</span>
                                            <p className="font-medium break-all">{metadata.filename}</p>
                                        </div>
                                    )}
                                    {metadata.dimensions && (
                                        <div>
                                            <span className="text-muted-foreground">Dimensions:</span>
                                            <p className="font-medium">{metadata.dimensions}</p>
                                        </div>
                                    )}
                                    {metadata.format && (
                                        <div>
                                            <span className="text-muted-foreground">Format:</span>
                                            <p className="font-medium">{metadata.format}</p>
                                        </div>
                                    )}
                                    {metadata.size && (
                                        <div>
                                            <span className="text-muted-foreground">Size:</span>
                                            <p className="font-medium">{metadata.size}</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}

export function ImageGrid({ images, className = '', maxImages = 12 }: ImageGridProps) {
    const displayImages = images.slice(0, maxImages);
    const remainingCount = images.length - maxImages;

    return (
        <div className={`space-y-4 ${className}`}>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {displayImages.map((image, index) => (
                    <ImagePreview
                        key={index}
                        src={image.src}
                        alt={image.alt}
                        metadata={image.metadata}
                        width={150}
                        height={150}
                    />
                ))}
            </div>
            {remainingCount > 0 && (
                <div className="text-center">
                    <Badge variant="secondary">
                        +{remainingCount} more images
                    </Badge>
                </div>
            )}
        </div>
    );
}

export function ClassImageGrid({ classes, className = '' }: ClassImageGridProps) {
    return (
        <div className={`space-y-6 ${className}`}>
            {classes.map((classItem, index) => (
                <Card key={index}>
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center justify-between">
                            <span className="flex items-center gap-2">
                                <ImageIcon className="h-5 w-5" />
                                {classItem.name}
                            </span>
                            <Badge variant="secondary">
                                {classItem.count} images
                            </Badge>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {classItem.sampleImages && classItem.sampleImages.length > 0 ? (
                            <ImageGrid
                                images={classItem.sampleImages}
                                maxImages={8}
                            />
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <ImageIcon className="mx-auto h-12 w-12 mb-2 opacity-50" />
                                <p>No sample images available</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

// Utility function to create image URLs from File objects
export function createImageURL(file: File): string {
    return URL.createObjectURL(file);
}

// Utility function to revoke image URLs
export function revokeImageURL(url: string): void {
    URL.revokeObjectURL(url);
}

// Utility function to get image metadata
export function getImageMetadata(file: File): ImagePreviewProps['metadata'] {
    return {
        filename: file.name,
        size: formatFileSize(file.size),
        format: file.type.split('/')[1]?.toUpperCase() || 'Unknown',
    };
}

function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}