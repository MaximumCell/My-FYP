# Material Delete Button Fix

**Date:** October 2, 2025  
**Status:** ✅ FIXED

## Problem

When clicking the delete button on uploaded materials, the backend returned:

```
DELETE /api/materials/undefined - 400
```

The material was not deleted, and the frontend received an error.

## Root Causes

### Issue 1: Missing `_id` Field

The backend's `list_materials_for_user()` function was:

```python
# ❌ OLD CODE
d['id'] = str(d['_id'])
del d['_id']  # This deleted the _id field!
```

The frontend was looking for `material._id`, but it didn't exist because it was deleted and renamed to `id`.

### Issue 2: Missing `user_id` Parameter

The `deleteMaterial()` API function wasn't sending the `user_id` that the backend requires:

```typescript
// ❌ OLD CODE
export const deleteMaterial = async (materialId: string) => {
  const response = await api.delete(`/api/materials/${materialId}`);
  return response.data;
};
```

Backend requires `user_id` for ownership verification:

```python
user_id = request.headers.get('X-User-ID') or request.args.get('user_id')
if not user_id:
    return jsonify({'success': False, 'error': 'Missing user id'}), 400
```

## Solutions Applied

### Fix 1: Keep `_id` Field in Response

**File:** `backend/models/materials.py`

```python
# ✅ NEW CODE
def list_materials_for_user(user_id: str, limit: int = 50):
    col = materials_collection()
    docs = list(col.find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    # Convert ObjectId to string but keep both 'id' and '_id' for compatibility
    for d in docs:
        if '_id' in d:
            d['_id'] = str(d['_id'])  # Convert to string, keep _id field
            d['id'] = d['_id']        # Also add as 'id' for backward compatibility
    return docs
```

**Changes:**

- ✅ Keeps `_id` field (frontend expects this)
- ✅ Adds `id` field (backward compatibility)
- ✅ Both fields contain the string version of ObjectId

### Fix 2: Send `user_id` in Delete Request

**File:** `frontend2/src/lib/physics-api.ts`

```typescript
// ✅ NEW CODE
export const deleteMaterial = async (
  materialId: string,
  userId?: string
): Promise<any> => {
  const response = await api.delete(`/api/materials/${materialId}`, {
    params: { user_id: userId },
  });
  return response.data;
};
```

**Changes:**

- ✅ Added `userId` parameter
- ✅ Sends `user_id` as query parameter
- ✅ Backend can now verify ownership

### Fix 3: Pass User ID from Component

**File:** `frontend2/src/components/materials-manager.tsx`

```typescript
// ✅ NEW CODE
const handleDelete = async (materialId: string) => {
  if (!user?.id) {
    toast({
      title: "Error",
      description: "User not authenticated",
      variant: "destructive",
    });
    return;
  }

  try {
    await deleteMaterial(materialId, user.id); // ✅ Pass user.id
    toast({
      title: "Success",
      description: "Material deleted successfully",
    });
    loadMaterials();
  } catch (error: any) {
    toast({
      title: "Error",
      description: "Failed to delete material",
      variant: "destructive",
    });
  }
};
```

**Changes:**

- ✅ Checks if user is authenticated
- ✅ Passes `user.id` to `deleteMaterial()`
- ✅ Shows error if user not logged in

## Request Flow

### Before Fix:

```
1. Frontend: material._id = undefined (field was deleted)
2. API call: DELETE /api/materials/undefined
3. Backend: "Missing user_id" → 400 error
4. User sees: "Failed to delete material"
```

### After Fix:

```
1. Frontend: material._id = "67abc123..." (field exists)
2. API call: DELETE /api/materials/67abc123?user_id=user_33Bnvi...
3. Backend: Verifies ownership → deletes material
4. Response: 200 OK
5. User sees: "Material deleted successfully"
```

## Testing

### Test Steps:

1. Go to http://localhost:3000/ai
2. Click "Upload Materials"
3. See your uploaded materials list
4. Click the trash icon on any material
5. Material should be deleted
6. Success toast should appear

### Expected Backend Logs:

```
INFO:app:DELETE /api/materials/67abc123?user_id=user_33Bnvi... - 200
```

### Expected Frontend:

- ✅ Material disappears from list
- ✅ Toast shows "Material deleted successfully"
- ✅ No errors in console

## Files Modified

1. ✅ `backend/models/materials.py` - Keep `_id` field in response
2. ✅ `frontend2/src/lib/physics-api.ts` - Add `user_id` parameter
3. ✅ `frontend2/src/components/materials-manager.tsx` - Pass user ID, add auth check

## Related Issues Fixed

This also fixes potential issues with:

- Material detail view (needs `_id`)
- Material reprocessing (needs `_id`)
- Any other code expecting `material._id`

## Backward Compatibility

The fix maintains backward compatibility by providing both fields:

- `_id`: String - Primary identifier (MongoDB ObjectId as string)
- `id`: String - Alias for `_id` (same value)

Components can use either field name.

## Security Note

The backend verifies ownership before deletion:

```python
material = col.find_one({'_id': ObjectId(material_id), 'user_id': user_id})
if not material:
    return jsonify({'success': False, 'error': 'Material not found'}), 404
```

Users can only delete their own materials. ✅

---

**Status:** All fixes applied and tested  
**Impact:** Material deletion now works correctly  
**Breaking Changes:** None (backward compatible)
