# DOCX and PPTX File Upload Support

## Implementation Summary

Successfully added support for uploading Microsoft Word (DOCX) and PowerPoint (PPTX) files to the Physics Learning Materials section.

## Changes Made

### 1. Frontend Changes (`frontend2/src/app/ai/page.tsx`)

- **File Input Accept Attribute**: Updated to include `.docx` and `.pptx`
  ```typescript
  accept = ".pdf,.png,.jpg,.jpeg,.docx,.pptx";
  ```
- **File Label**: Updated to show "File (PDF, PNG, JPG, DOCX, PPTX)"
- Users can now select DOCX and PPTX files from the file picker

### 2. Backend Route Changes (`backend/routes/physics_advanced_routes.py`)

- **Allowed Extensions**: Added 'docx' and 'pptx' to the allowed file types
  ```python
  ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'pptx'}
  ```
- Files are validated before processing

### 3. OCR Processor Enhancement (`backend/ai/ocr_processor.py`)

- **New Dependencies**:

  - `python-docx` (v1.2.0) - for DOCX processing
  - `python-pptx` (v1.0.2) - for PowerPoint processing
  - `lxml` (v6.0.2) - XML processing (dependency)
  - `XlsxWriter` (v3.2.9) - Excel support (dependency)

- **New Methods**:

  1. `extract_text_from_docx()` - Extracts text from Word documents

     - Reads paragraphs
     - Reads table content
     - Preserves document structure

  2. `extract_text_from_pptx()` - Extracts text from PowerPoint presentations
     - Iterates through all slides
     - Extracts text from all shapes
     - Includes slide numbers for context

- **Updated `extract_text()` method**: Now routes to appropriate extractor based on file extension

## Package Installation

```bash
pip install python-docx python-pptx
```

**Installed Packages:**

- ✅ python-docx==1.2.0
- ✅ python-pptx==1.0.2
- ✅ lxml==6.0.2 (dependency)
- ✅ XlsxWriter==3.2.9 (dependency)

## How It Works

### DOCX Processing

1. User uploads a `.docx` file
2. Backend validates file extension
3. OCR processor opens document using `python-docx`
4. Extracts text from:
   - All paragraphs in order
   - All tables (cell by cell)
5. Returns combined text for AI processing

### PPTX Processing

1. User uploads a `.pptx` file
2. Backend validates file extension
3. OCR processor opens presentation using `python-pptx`
4. Extracts text from:
   - All slides in sequence
   - All text shapes on each slide
5. Returns formatted text with slide numbers

## Features

### Supported File Types (Complete List)

- ✅ PDF (`.pdf`)
- ✅ PNG Images (`.png`)
- ✅ JPEG Images (`.jpg`, `.jpeg`)
- ✅ Word Documents (`.docx`) **NEW**
- ✅ PowerPoint Presentations (`.pptx`) **NEW**

### Content Extraction

- **DOCX**:
  - Body text and paragraphs
  - Tables and structured data
  - Maintains reading order
- **PPTX**:
  - Slide content
  - Text boxes and shapes
  - Maintains slide sequence
  - Includes slide numbers

### AI Integration

- Extracted text is processed by the Physics AI tutor
- Content is used for RAG (Retrieval-Augmented Generation)
- Materials are stored in the vector database
- AI can reference uploaded materials in responses

## Testing

### Test DOCX Upload

1. Go to http://localhost:3000/ai
2. Click "Physics Learning Materials" button
3. Click "Choose File"
4. Select a `.docx` file (e.g., physics notes, textbook chapter)
5. Enter title (e.g., "Classical Mechanics Notes")
6. Select material type (e.g., "Personal Notes")
7. Click "Upload Material"
8. ✅ File should upload successfully

### Test PPTX Upload

1. Go to http://localhost:3000/ai
2. Click "Physics Learning Materials" button
3. Click "Choose File"
4. Select a `.pptx` file (e.g., lecture slides)
5. Enter title (e.g., "Electromagnetism Lecture")
6. Select material type (e.g., "Lecture Slides")
7. Click "Upload Material"
8. ✅ File should upload successfully

### Verify AI Can Use Materials

1. Upload a DOCX/PPTX with physics content
2. Ask a question related to that content
3. AI should reference the uploaded material in its response

## Error Handling

### Invalid File Types

- Frontend: File picker restricts to allowed extensions
- Backend: Validates extension before processing
- Error message: "File type not allowed"

### Processing Errors

- DOCX: Handles corrupted documents gracefully
- PPTX: Handles missing text shapes
- Falls back to empty string on errors
- Logs errors for debugging

### File Size

- No explicit limit (uses Flask default)
- Large files may take longer to process
- OCR processor handles large documents efficiently

## Technical Details

### File Storage

- Uploaded files saved to: `backend/uploads/materials/`
- Filename format: `{timestamp}_{original_name}`
- Files persisted for future reference

### Text Extraction Flow

```
User Upload → Flask Route → File Validation → OCR Processor
              ↓                                      ↓
         File Saved                          Text Extraction
              ↓                                      ↓
    Vector Database ← Embeddings ← Text Content ← Document
```

### Dependencies Version Matrix

| Package           | Version | Purpose                     |
| ----------------- | ------- | --------------------------- |
| python-docx       | 1.2.0   | DOCX parsing                |
| python-pptx       | 1.0.2   | PPTX parsing                |
| lxml              | 6.0.2   | XML processing              |
| XlsxWriter        | 3.2.9   | Excel support               |
| Pillow            | 11.3.0  | Image processing (existing) |
| typing_extensions | 4.15.0  | Type hints (existing)       |

## Benefits

1. **Broader Format Support**: Users can upload their notes and presentations directly
2. **No Conversion Needed**: Works with native Microsoft Office formats
3. **Better Context**: AI has access to more comprehensive learning materials
4. **Efficient Extraction**: Fast text extraction from structured documents
5. **Error Resilient**: Handles various document structures and errors gracefully

## Future Enhancements

Potential improvements:

- [ ] Add support for `.doc` (older Word format)
- [ ] Add support for `.ppt` (older PowerPoint format)
- [ ] Extract images from DOCX/PPTX for diagram analysis
- [ ] Support for Excel files (`.xlsx`)
- [ ] Extract formatting and structure (bold, headers, etc.)
- [ ] Handle embedded equations in Word documents
- [ ] Support for Google Docs/Slides (via export)

## Troubleshooting

### Issue: "File type not allowed"

**Solution**: Ensure file has correct extension (.docx or .pptx)

### Issue: "No text extracted"

**Solution**: Check if document contains actual text (not just images)

### Issue: Upload fails silently

**Solution**: Check backend logs for errors, verify file isn't corrupted

### Issue: AI doesn't reference uploaded material

**Solution**: Wait for embedding process, try asking specific questions about content

## Restart Instructions

If you made changes, restart the backend:

```bash
# Stop backend
pkill -f "python app.py"

# Restart backend
cd /home/itz_sensei/Documents/FypProject/backend
python app.py
```

Frontend should auto-reload with the changes.

## Verification Checklist

- ✅ Frontend accepts .docx and .pptx files
- ✅ Backend validates docx/pptx extensions
- ✅ python-docx package installed
- ✅ python-pptx package installed
- ✅ OCR processor has DOCX extraction method
- ✅ OCR processor has PPTX extraction method
- ✅ extract_text() routes to correct handler
- ✅ Error handling in place
- ✅ Requirements.txt updated

## Files Modified

1. `/frontend2/src/app/ai/page.tsx` - File input component
2. `/backend/routes/physics_advanced_routes.py` - Allowed extensions
3. `/backend/ai/ocr_processor.py` - Text extraction logic
4. `/backend/requirements.txt` - Package dependencies

---

**Status**: ✅ Implementation Complete
**Date**: October 2, 2025
**Feature**: DOCX and PPTX file upload support
**Ready for Testing**: Yes
