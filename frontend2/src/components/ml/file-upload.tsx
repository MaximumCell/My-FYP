'use client';

import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, X } from 'lucide-react';
import { useCallback } from 'react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileChange: (files: File[]) => void;
  className?: string;
}

export default function FileUpload({ onFileChange, className }: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFileChange(acceptedFiles);
  }, [onFileChange]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles, fileRejections } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
  });

  const isFileAccepted = acceptedFiles.length > 0;
  
  return (
    <div className={cn("space-y-2", className)}>
        <div
          {...getRootProps()}
          className={cn(
            'flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted',
            isDragActive && 'border-primary',
            isFileAccepted && 'border-green-500'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <UploadCloud className="w-8 h-8 mb-2 text-muted-foreground" />
            {isDragActive ? (
              <p className="font-semibold text-primary">Drop the file here ...</p>
            ) : (
              <>
                <p className="mb-2 text-sm text-muted-foreground">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-muted-foreground">CSV files only</p>
              </>
            )}
          </div>
        </div>
        
        {isFileAccepted && (
            <div className="flex items-center justify-between p-2 mt-2 bg-green-100 dark:bg-green-900/50 rounded-md">
                <div className="flex items-center space-x-2">
                    <File className="w-5 h-5 text-green-700 dark:text-green-300"/>
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">{acceptedFiles[0].name}</span>
                </div>
                {/* Could add a remove button here if needed */}
            </div>
        )}

        {fileRejections.length > 0 && (
             <div className="flex items-center justify-between p-2 mt-2 bg-red-100 dark:bg-red-900/50 rounded-md">
                <div className="flex items-center space-x-2">
                    <X className="w-5 h-5 text-red-700 dark:text-red-300"/>
                    <span className="text-sm font-medium text-red-800 dark:text-red-200">
                        {fileRejections[0].errors[0].message} (File: {fileRejections[0].file.name})
                    </span>
                </div>
            </div>
        )}
    </div>
  );
}
