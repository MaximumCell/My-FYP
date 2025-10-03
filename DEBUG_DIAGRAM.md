# Debugging Diagram Display Issue

## Quick Diagnosis Commands

### 1. Check if images are being saved

```bash
cd /home/itz_sensei/Documents/FypProject/backend
ls -lh static/generated_images/
```

### 2. Test backend API directly

```bash
curl -X POST http://localhost:5000/api/physics/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"description": "test electric field"}' \
  | jq '.image_url, .success'
```

### 3. Test if Flask serves static files

```bash
# Get the actual image filename from step 1, then:
curl -I http://localhost:5000/static/generated_images/physics_diagram_XXXXXX.png
```

## Frontend Browser Console Checks

Open browser DevTools (F12) and check:

### Console Tab

Look for errors like:

- `Failed to load resource: net::ERR_CONNECTION_REFUSED`
- `CORS policy` errors
- `404 Not Found` for images

### Network Tab

1. Filter by "Img" or "XHR"
2. Look for requests to `/static/generated_images/`
3. Check response status (should be 200)
4. Click failed requests to see error details

### React Component Tab

1. Inspect the message object
2. Check if `message.diagram` exists
3. Verify `message.diagram.image_base64` has data
4. Check `message.diagram.image_url` format

## Common Issues & Fixes

### Issue 1: Image URL is Relative

**Symptom:** URL is `/static/...` instead of `http://localhost:5000/static/...`

**Fix:** Update backend to return full URL:

```python
# In enhanced_physics_tutor.py, line ~623
'image_url': f"http://localhost:5000/static/generated_images/{filename}",
```

### Issue 2: CORS Blocking Images

**Symptom:** Console shows CORS error for image requests

**Fix:** Images should work with existing CORS setup, but verify `app.py` has:

```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

### Issue 3: Base64 Not Rendering

**Symptom:** No error, but image doesn't show

**Check:**

- Is `image_base64` actually in the response?
- Is the `<img src="data:image/png;base64,..."` syntax correct?

**Test in browser console:**

```javascript
// Check if base64 data exists in last message
const lastMsg = messages[messages.length - 1];
console.log("Has diagram:", !!lastMsg.diagram);
console.log("Has base64:", lastMsg.diagram?.image_base64?.substring(0, 50));
console.log("Has URL:", lastMsg.diagram?.image_url);
```

### Issue 4: Frontend Not Detecting Diagram

**Symptom:** No diagram render section at all

**Check `handleSend` function:**

```typescript
// Should detect keywords and call requestDiagram
const hasDiagramKeyword = diagramKeywords.some((kw) => lowerInput.includes(kw));
```

## Testing the Full Flow

### Step 1: Backend Test

```bash
cd /home/itz_sensei/Documents/FypProject/backend
python -c "
from ai.enhanced_physics_tutor import EnhancedPhysicsAITutor
import asyncio

async def test():
    tutor = EnhancedPhysicsAITutor()
    result = await tutor.generate_physics_diagram('test')
    print('Success:', result.get('success'))
    print('Has Base64:', bool(result.get('image_base64')))
    print('Image URL:', result.get('image_url'))

asyncio.run(test())
"
```

### Step 2: Frontend Test

In browser console:

```javascript
// Test API call
fetch("http://localhost:5000/api/physics/generate-diagram", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ description: "test electric field" }),
})
  .then((r) => r.json())
  .then((d) => {
    console.log("Success:", d.success);
    console.log("Has Base64:", !!d.image_base64);
    console.log("URL:", d.image_url);
  });
```

### Step 3: Test Image Display

In browser console:

```javascript
// Create test image element
const testImg = document.createElement("img");
testImg.src = "data:image/png;base64,YOUR_BASE64_HERE";
document.body.appendChild(testImg);
```

## Restart Everything

```bash
# Backend
cd /home/itz_sensei/Documents/FypProject/backend
pkill -f "python app.py"
python app.py

# Frontend (in new terminal)
cd /home/itz_sensei/Documents/FypProject/frontend2
npm run dev
```

Then test in browser at http://localhost:3000/ai

## Expected Behavior

When you type "draw electric field":

1. Message appears: "Generate diagram: draw electric field"
2. Loading indicator shows
3. AI response appears with text explanation
4. Image appears below the text in a bordered box
5. Image should be ~360KB (as confirmed by test)

## If Still Not Working

Check these files for manual inspection:

1. `/frontend2/src/hooks/use-physics-chat.ts` - line 317 (`requestDiagram`)
2. `/frontend2/src/components/physics-ai-chat.tsx` - line 401 (diagram render)
3. `/backend/ai/enhanced_physics_tutor.py` - line 619 (return format)
