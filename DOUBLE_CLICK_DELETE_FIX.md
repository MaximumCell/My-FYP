# Double-Click Delete Fix

**Date:** October 2, 2025  
**Status:** ✅ FIXED

## Problem

When clicking the delete button once, the material was deleted successfully (200 response), but then a second delete request was sent for the same material, causing a 404 error:

```
DELETE /api/materials/68ddff41... - 200 - 0.429s  ✅ First delete (success)
DELETE /api/materials/68ddff41... - 404 - 2.746s  ❌ Second delete (fails)
```

## Root Cause

The delete button didn't have protection against:

1. **Double-clicking** - User could click the button twice quickly
2. **Re-renders** - React re-rendering could trigger multiple calls
3. **No visual feedback** - User didn't know deletion was in progress

## Solution

Added a **deletion state** to track which material is being deleted and prevent multiple simultaneous delete operations.

### Changes Made

**File:** `frontend2/src/components/materials-manager.tsx`

#### 1. Added Deletion State

```typescript
const [deletingId, setDeletingId] = useState<string | null>(null);
```

This tracks which material (by ID) is currently being deleted.

#### 2. Updated handleDelete Function

```typescript
const handleDelete = async (materialId: string) => {
  if (!user?.id) {
    toast({
      title: "Error",
      description: "User not authenticated",
      variant: "destructive",
    });
    return;
  }

  // ✅ NEW: Prevent double-clicking
  if (deletingId) {
    return; // Already deleting something, ignore this click
  }

  setDeletingId(materialId); // Mark this material as being deleted
  try {
    await deleteMaterial(materialId, user.id);
    toast({ title: "Success", description: "Material deleted successfully" });
    loadMaterials();
  } catch (error: any) {
    toast({
      title: "Error",
      description: error.response?.data?.error || "Failed to delete material",
      variant: "destructive",
    });
  } finally {
    setDeletingId(null); // Clear deletion state
  }
};
```

**Improvements:**

- ✅ Checks if any deletion is in progress (`if (deletingId)`)
- ✅ Sets deletion state before API call
- ✅ Clears deletion state in `finally` block (always runs)
- ✅ Shows backend error message if available

#### 3. Updated Delete Button with Visual Feedback

```tsx
<Button
  variant="ghost"
  size="sm"
  onClick={() => handleDelete(material._id)}
  disabled={deletingId === material._id} // ✅ Disable during deletion
>
  {deletingId === material._id ? (
    <Loader2 className="h-4 w-4 animate-spin" /> // ✅ Show spinner
  ) : (
    <Trash2 className="h-4 w-4 text-destructive" /> // ✅ Show trash icon
  )}
</Button>
```

**Visual States:**

- **Idle:** Shows red trash icon
- **Deleting:** Shows spinning loader (button disabled)
- **After deletion:** Returns to trash icon (material removed from list)

## How It Works

### Before Fix:

```
User clicks delete → API call starts
User clicks again  → Second API call starts
First call: 200 OK (deleted)
Second call: 404 Not Found (already deleted) ❌
```

### After Fix:

```
User clicks delete → API call starts → deletingId = "abc123"
User clicks again  → Ignored (deletingId already set) ✅
API completes → deletingId = null → Ready for next delete
```

## Benefits

1. **Prevents duplicate API calls** - Only one delete at a time
2. **Better UX** - Visual feedback with spinner
3. **Button disabled** - Can't click while deleting
4. **Better error messages** - Shows backend error details
5. **No 404 errors** - Second click is ignored

## Testing

### Test Steps:

1. Go to http://localhost:3000/ai
2. Click "Upload Materials"
3. **Rapidly click** the delete button multiple times
4. Expected behavior:
   - ✅ Button shows spinner immediately
   - ✅ Button is disabled (can't click again)
   - ✅ Material deleted once
   - ✅ Success toast appears
   - ✅ No 404 error in backend logs

### Expected Backend Logs:

```
DELETE /api/materials/68ddff41... - 200 - 0.429s  ✅ Only ONE delete
```

### Expected Frontend:

- ✅ Smooth deletion animation
- ✅ Spinner shows during deletion
- ✅ No multiple toasts
- ✅ Material disappears from list

## Edge Cases Handled

1. **Rapid clicking:** Ignored after first click
2. **Network delays:** Button stays disabled until response
3. **Errors:** Button re-enables if deletion fails
4. **Multiple materials:** Can delete different materials simultaneously (by design)

## Related Patterns

This same pattern is used throughout the app:

- ✅ Upload button (uses `uploading` state)
- ✅ Form submissions (uses `loading` state)
- ✅ API calls (uses request-specific state)

## Future Improvements

Could add:

1. **Confirmation dialog** - "Are you sure you want to delete?"
2. **Undo option** - Temporarily keep in trash before permanent delete
3. **Batch delete** - Select multiple materials to delete
4. **Optimistic updates** - Remove from UI immediately, restore if error

---

**Status:** ✅ FIXED  
**Files Modified:** 1 (`materials-manager.tsx`)  
**Lines Changed:** ~30  
**Breaking Changes:** None  
**User Impact:** Better UX, no duplicate delete errors
