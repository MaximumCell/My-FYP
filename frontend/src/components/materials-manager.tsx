/**
 * Materials Upload Component
 * Upload and manage physics learning materials (PDFs, notes, textbooks)
 */

'use client';

import React, { useState, useCallback } from 'react';
import { useUser } from '@clerk/nextjs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Upload,
  FileText,
  Loader2,
  CheckCircle2,
  XCircle,
  Trash2,
  BookOpen,
  AlertCircle,
} from 'lucide-react';
import { uploadMaterial, listMaterials, deleteMaterial, Material } from '@/lib/physics-api';
import { useToast } from '@/hooks/use-toast';

export function MaterialsManager() {
  const { user } = useUser();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Form state
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [materialType, setMaterialType] = useState<'notes' | 'textbook_chapter' | 'reference'>('notes');
  const [bookInfo, setBookInfo] = useState({
    title: '',
    author: '',
    edition: '',
    chapter: '',
  });

  // Load materials when dialog opens
  const loadMaterials = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const data = await listMaterials(user.id);
      setMaterials(data);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to load materials',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [user?.id, toast]);

  // Handle file upload
  const handleUpload = async () => {
    if (!file || !title.trim() || !user?.id) {
      toast({
        title: 'Error',
        description: 'Please provide a file and title',
        variant: 'destructive',
      });
      return;
    }

    setUploading(true);
    try {
      await uploadMaterial({
        file,
        title: title.trim(),
        material_type: materialType,
        user_id: user?.id,
        book_info: materialType === 'textbook_chapter' ? bookInfo : undefined,
      });

      toast({
        title: 'Success',
        description: 'Material uploaded successfully! Processing in background...',
      });

      // Reset form
      setFile(null);
      setTitle('');
      setBookInfo({ title: '', author: '', edition: '', chapter: '' });

      // Reload materials
      loadMaterials();
    } catch (error: any) {
      toast({
        title: 'Upload Failed',
        description: error.message || 'Failed to upload material',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle delete
  const handleDelete = async (materialId: string) => {
    if (!user?.id) {
      toast({
        title: 'Error',
        description: 'User not authenticated',
        variant: 'destructive',
      });
      return;
    }

    // Prevent double-clicking
    if (deletingId) {
      return;
    }

    setDeletingId(materialId);
    try {
      await deleteMaterial(materialId, user.id);
      toast({
        title: 'Success',
        description: 'Material deleted successfully',
      });
      loadMaterials();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to delete material',
        variant: 'destructive',
      });
    } finally {
      setDeletingId(null);
    }
  };

  // Handle dialog open
  const handleOpenChange = (isOpen: boolean) => {
    setOpen(isOpen);
    if (isOpen) {
      loadMaterials();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Upload className="h-4 w-4 mr-2" />
          Upload Materials
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Physics Learning Materials</DialogTitle>
          <DialogDescription>
            Upload your notes, textbooks, or reference materials. They'll be used to provide
            personalized explanations.
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-6">
          {/* Upload Form */}
          <div className="space-y-4">
            <h3 className="font-semibold text-sm">Upload New Material</h3>

            <div className="space-y-3">
              <div>
                <Label htmlFor="file">File (PDF, PNG, JPG, DOCX, PPTX)</Label>
                <Input
                  id="file"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.docx,.pptx"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  disabled={uploading}
                />
                {file && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="e.g., Classical Mechanics Notes"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={uploading}
                />
              </div>

              <div>
                <Label htmlFor="type">Material Type</Label>
                <Select
                  value={materialType}
                  onValueChange={(value: any) => setMaterialType(value)}
                  disabled={uploading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="notes">Personal Notes</SelectItem>
                    <SelectItem value="textbook_chapter">Textbook Chapter</SelectItem>
                    <SelectItem value="reference">Reference Material</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {materialType === 'textbook_chapter' && (
                <div className="space-y-3 p-3 bg-muted rounded-lg">
                  <Label className="text-sm">Book Information</Label>
                  <Input
                    placeholder="Book Title"
                    value={bookInfo.title}
                    onChange={(e) =>
                      setBookInfo({ ...bookInfo, title: e.target.value })
                    }
                    disabled={uploading}
                  />
                  <Input
                    placeholder="Author"
                    value={bookInfo.author}
                    onChange={(e) =>
                      setBookInfo({ ...bookInfo, author: e.target.value })
                    }
                    disabled={uploading}
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      placeholder="Edition"
                      value={bookInfo.edition}
                      onChange={(e) =>
                        setBookInfo({ ...bookInfo, edition: e.target.value })
                      }
                      disabled={uploading}
                    />
                    <Input
                      placeholder="Chapter"
                      value={bookInfo.chapter}
                      onChange={(e) =>
                        setBookInfo({ ...bookInfo, chapter: e.target.value })
                      }
                      disabled={uploading}
                    />
                  </div>
                </div>
              )}

              <Button
                onClick={handleUpload}
                disabled={uploading || !file || !title.trim()}
                className="w-full"
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Material
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Materials List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm">Your Materials</h3>
              <Badge variant="secondary">{materials.length} items</Badge>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : materials.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No materials uploaded yet</p>
                </CardContent>
              </Card>
            ) : (
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-2">
                  {materials.map((material) => (
                    <Card key={material._id}>
                      <CardContent className="p-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-grow min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <FileText className="h-4 w-4 flex-shrink-0" />
                              <h4 className="font-medium text-sm truncate">
                                {material.title}
                              </h4>
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="outline" className="text-xs">
                                {material.material_type.replace('_', ' ')}
                              </Badge>
                              <ProcessingStatus
                                status={material.upload_metadata.processing_status}
                              />
                            </div>
                            {material.book_info?.title && (
                              <p className="text-xs text-muted-foreground truncate">
                                {material.book_info.title}
                                {material.book_info.author &&
                                  ` - ${material.book_info.author}`}
                              </p>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(material._id)}
                            disabled={deletingId === material._id}
                          >
                            {deletingId === material._id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4 text-destructive" />
                            )}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Processing Status Badge
function ProcessingStatus({ status }: { status: string }) {
  const getStatusDisplay = () => {
    switch (status) {
      case 'completed':
        return {
          icon: <CheckCircle2 className="h-3 w-3" />,
          label: 'Processed',
          variant: 'default' as const,
        };
      case 'pending':
        return {
          icon: <Loader2 className="h-3 w-3 animate-spin" />,
          label: 'Processing',
          variant: 'secondary' as const,
        };
      case 'failed':
        return {
          icon: <XCircle className="h-3 w-3" />,
          label: 'Failed',
          variant: 'destructive' as const,
        };
      default:
        return {
          icon: <AlertCircle className="h-3 w-3" />,
          label: status,
          variant: 'outline' as const,
        };
    }
  };

  const { icon, label, variant } = getStatusDisplay();

  return (
    <Badge variant={variant} className="text-xs flex items-center gap-1">
      {icon}
      {label}
    </Badge>
  );
}
