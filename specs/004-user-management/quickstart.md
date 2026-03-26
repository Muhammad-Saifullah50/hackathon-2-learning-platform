# Quickstart: User Management Implementation

**Feature**: 004-user-management
**Date**: 2026-03-15
**Phase**: 1 - Design & Contracts

## Overview

This quickstart guide provides step-by-step instructions for implementing the User Management feature. Follow the order below to build profile management, preferences configuration, and account deletion functionality.

## Prerequisites

- ✅ F01 (Authentication) completed - JWT auth and dependencies available
- ✅ F02 (Database Schema) completed - User, UserProfile models and repositories exist
- ✅ Python 3.11+ with FastAPI, SQLAlchemy, Pydantic installed
- ✅ Next.js 14+ with TypeScript configured
- ✅ PostgreSQL database running (Neon)

## Implementation Order

### Phase 1: Backend - Service Layer (Day 1)

**Goal**: Implement business logic for profile operations

**Files to create**:
- `backend/src/services/user_profile_service.py`

**Steps**:

1. **Create UserProfileService class**:
```python
# backend/src/services/user_profile_service.py
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository, UserProfileRepository
from src.models.user import User, UserProfile

class UserProfileService:
    """Business logic for user profile operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.profile_repo = UserProfileRepository(db)
```

2. **Implement get_profile method**:
```python
async def get_profile(self, user_id: UUID) -> dict:
    """Get user profile with preferences."""
    user = await self.user_repo.get_by_id(str(user_id))
    if not user:
        raise ValueError("User not found")

    profile = await self.profile_repo.get_by_user_id(str(user_id))

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "bio": profile.bio if profile else None,
        "preferences": user.preferences or {},
        "email_verified_at": user.email_verified_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
```

3. **Implement update_profile method with display_name fallback**:
```python
async def update_profile(
    self,
    user_id: UUID,
    display_name: Optional[str] = None,
    bio: Optional[str] = None
) -> dict:
    """Update user profile (display_name and bio)."""
    user = await self.user_repo.get_by_id(str(user_id))
    if not user:
        raise ValueError("User not found")

    # Apply display_name fallback rule
    if display_name is not None:
        display_name = display_name.strip()
        if not display_name:
            display_name = user.email  # Fallback to email
        user.display_name = display_name

    # Update bio in profile
    if bio is not None:
        profile = await self.profile_repo.get_by_user_id(str(user_id))
        if profile:
            profile.bio = bio.strip() if bio else None
        else:
            # Create profile if doesn't exist
            profile = UserProfile(user_id=user_id, bio=bio.strip() if bio else None)
            await self.profile_repo.create(profile)

    await self.db.commit()
    return await self.get_profile(user_id)
```

4. **Implement update_preferences method**:
```python
async def update_preferences(
    self,
    user_id: UUID,
    learning_pace: Optional[str] = None,
    difficulty_level: Optional[str] = None
) -> dict:
    """Update user learning preferences."""
    user = await self.user_repo.get_by_id(str(user_id))
    if not user:
        raise ValueError("User not found")

    preferences = user.preferences or {}

    if learning_pace:
        preferences["learning_pace"] = learning_pace
    if difficulty_level:
        preferences["difficulty_level"] = difficulty_level

    await self.user_repo.update_preferences(str(user_id), preferences)
    return preferences
```

5. **Implement hard_delete_account method**:
```python
async def hard_delete_account(self, user_id: UUID, password: str) -> bool:
    """Hard delete user account with password confirmation."""
    import bcrypt

    user = await self.user_repo.get_by_id(str(user_id))
    if not user:
        raise ValueError("User not found")

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise ValueError("Incorrect password")

    # Hard delete (cascades to all related tables)
    await self.db.delete(user)
    await self.db.commit()
    return True
```

**Testing**:
```bash
# Run unit tests
pytest backend/tests/unit/test_user_profile_service.py -v
```

---

### Phase 2: Backend - Pydantic Schemas (Day 1)

**Goal**: Define request/response validation schemas

**Files to create**:
- `backend/src/schemas/user_profile.py`

**Steps**:

1. **Create Pydantic schemas**:
```python
# backend/src/schemas/user_profile.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class LearningPace(str, Enum):
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

class PreferencesUpdateRequest(BaseModel):
    learning_pace: Optional[LearningPace] = None
    difficulty_level: Optional[DifficultyLevel] = None

class AccountDeleteRequest(BaseModel):
    password: str = Field(min_length=8)

class ProfileResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    bio: Optional[str] = None
    preferences: dict
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Testing**:
```python
# Test enum validation
request = PreferencesUpdateRequest(learning_pace="invalid")  # Should raise ValidationError
```

---

### Phase 3: Backend - API Routes (Day 2)

**Goal**: Implement FastAPI endpoints

**Files to create**:
- `backend/src/api/routes/profile.py`
- `backend/src/api/routes/admin.py`

**Steps**:

1. **Create profile routes**:
```python
# backend/src/api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.services.user_profile_service import UserProfileService
from src.schemas.user_profile import (
    ProfileResponse,
    ProfileUpdateRequest,
    PreferencesUpdateRequest,
    AccountDeleteRequest,
)

router = APIRouter(prefix="/api", tags=["Profile"])

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's profile."""
    service = UserProfileService(db)
    profile = await service.get_profile(current_user.id)
    return profile

@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    service = UserProfileService(db)
    profile = await service.update_profile(
        current_user.id,
        display_name=request.display_name,
        bio=request.bio,
    )
    return profile

@router.patch("/preferences")
async def update_preferences(
    request: PreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user learning preferences."""
    service = UserProfileService(db)
    preferences = await service.update_preferences(
        current_user.id,
        learning_pace=request.learning_pace,
        difficulty_level=request.difficulty_level,
    )
    return {"preferences": preferences}

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    request: AccountDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete user account permanently (GDPR compliance)."""
    service = UserProfileService(db)
    try:
        await service.hard_delete_account(current_user.id, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return None
```

2. **Create admin routes**:
```python
# backend/src/api/routes/admin.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.models.user import User as UserModel

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    role: str = Query(None, pattern="^(student|teacher|admin)$"),
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only, paginated)."""
    page_size = 50
    offset = (page - 1) * page_size

    # Build query
    query = select(UserModel).where(UserModel.deleted_at.is_(None))
    if role:
        query = query.where(UserModel.role == role)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.order_by(UserModel.created_at.desc()).limit(page_size).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "display_name": u.display_name,
                "role": u.role,
                "email_verified_at": u.email_verified_at,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
```

3. **Register routes in main app**:
```python
# backend/src/main.py
from src.api.routes import profile, admin

app.include_router(profile.router)
app.include_router(admin.router)
```

**Testing**:
```bash
# Run integration tests
pytest backend/tests/integration/test_profile_routes.py -v
pytest backend/tests/integration/test_admin_routes.py -v
```

---

### Phase 4: Frontend - API Client (Day 3)

**Goal**: Create TypeScript API client for profile endpoints

**Files to create**:
- `frontend/src/lib/api/profile.ts`

**Steps**:

1. **Create API client**:
```typescript
// frontend/src/lib/api/profile.ts
import { getSession } from '@/lib/auth'; // Better Auth session helper

export interface ProfileResponse {
  id: string;
  email: string;
  display_name: string;
  role: 'student' | 'teacher' | 'admin';
  bio?: string;
  preferences: {
    learning_pace?: 'slow' | 'normal' | 'fast';
    difficulty_level?: 'beginner' | 'intermediate' | 'advanced';
    theme?: 'dark';
  };
  email_verified_at?: string;
  created_at: string;
  updated_at: string;
}

export async function getProfile(): Promise<ProfileResponse> {
  const session = await getSession();
  const response = await fetch('/api/profile', {
    headers: {
      'Authorization': `Bearer ${session.accessToken}`,
    },
  });
  if (!response.ok) throw new Error('Failed to fetch profile');
  return response.json();
}

export async function updateProfile(data: {
  display_name?: string;
  bio?: string;
}): Promise<ProfileResponse> {
  const session = await getSession();
  const response = await fetch('/api/profile', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update profile');
  return response.json();
}

export async function updatePreferences(data: {
  learning_pace?: 'slow' | 'normal' | 'fast';
  difficulty_level?: 'beginner' | 'intermediate' | 'advanced';
}): Promise<{ preferences: ProfileResponse['preferences'] }> {
  const session = await getSession();
  const response = await fetch('/api/preferences', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update preferences');
  return response.json();
}

export async function deleteAccount(password: string): Promise<void> {
  const session = await getSession();
  const response = await fetch('/api/account', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete account');
  }
}
```

---

### Phase 5: Frontend - Components (Day 3-4)

**Goal**: Build React components for profile forms

**Files to create**:
- `frontend/src/components/ProfileForm.tsx`
- `frontend/src/components/PreferencesForm.tsx`
- `frontend/src/components/AccountDeleteDialog.tsx`

**Steps**:

1. **Create ProfileForm component**:
```typescript
// frontend/src/components/ProfileForm.tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { updateProfile } from '@/lib/api/profile';

interface ProfileFormProps {
  initialData: {
    display_name: string;
    bio?: string;
  };
  onSuccess?: () => void;
}

export function ProfileForm({ initialData, onSuccess }: ProfileFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: initialData,
  });

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      await updateProfile(data);
      onSuccess?.();
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="display_name" className="block text-sm font-medium">
          Display Name
        </label>
        <input
          id="display_name"
          {...register('display_name', { maxLength: 100 })}
          className="mt-1 block w-full rounded-md border-gray-300"
        />
        {errors.display_name && (
          <p className="text-red-500 text-sm">Max 100 characters</p>
        )}
      </div>

      <div>
        <label htmlFor="bio" className="block text-sm font-medium">
          Bio
        </label>
        <textarea
          id="bio"
          {...register('bio', { maxLength: 500 })}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300"
        />
        {errors.bio && (
          <p className="text-red-500 text-sm">Max 500 characters</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        {isSubmitting ? 'Saving...' : 'Save Profile'}
      </button>
    </form>
  );
}
```

2. **Create PreferencesForm component** (similar pattern)

3. **Create AccountDeleteDialog component** with password confirmation

---

### Phase 6: Frontend - Pages (Day 4)

**Goal**: Create Next.js pages for profile management

**Files to create**:
- `frontend/src/app/profile/page.tsx`
- `frontend/src/app/preferences/page.tsx`
- `frontend/src/app/admin/users/page.tsx`

**Steps**:

1. **Create profile page**:
```typescript
// frontend/src/app/profile/page.tsx
import { getProfile } from '@/lib/api/profile';
import { ProfileForm } from '@/components/ProfileForm';

export default async function ProfilePage() {
  const profile = await getProfile();

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Profile Settings</h1>
      <ProfileForm
        initialData={{
          display_name: profile.display_name,
          bio: profile.bio,
        }}
      />
    </div>
  );
}
```

2. **Create preferences page** (similar pattern)

3. **Create admin users page** with pagination and filtering

---

### Phase 7: Testing (Day 5)

**Goal**: Write comprehensive tests

**Test files to create**:
- `backend/tests/unit/test_user_profile_service.py`
- `backend/tests/integration/test_profile_routes.py`
- `backend/tests/integration/test_admin_routes.py`
- `frontend/tests/components/ProfileForm.test.tsx`
- `frontend/tests/e2e/profile-update.spec.ts`

**Run all tests**:
```bash
# Backend
pytest backend/tests/ -v --cov=src

# Frontend
npm run test
npm run test:e2e
```

---

## API Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/profile` | User | Get current user's profile |
| PATCH | `/api/profile` | User | Update profile (display_name, bio) |
| PATCH | `/api/preferences` | User | Update learning preferences |
| DELETE | `/api/account` | User | Delete account permanently |
| GET | `/api/admin/users` | Admin | List all users (paginated) |

## Common Issues & Solutions

### Issue: Display name shows email instead of custom name
**Solution**: Check that display_name is not empty string. Service layer should fallback to email only if empty.

### Issue: Account deletion fails with foreign key constraint
**Solution**: Verify CASCADE is configured on all User relationships in SQLAlchemy models.

### Issue: Admin user list returns 403
**Solution**: Ensure JWT token has `role: 'admin'` claim. Use `require_role(['admin'])` dependency.

### Issue: Preferences not persisting
**Solution**: Check that `User.preferences` JSONB field is being updated correctly. Verify JSON serialization.

## Performance Checklist

- [ ] Profile GET query uses LEFT JOIN (< 40ms)
- [ ] Admin user list uses pagination (50 per page)
- [ ] Admin user list filters use indexed `role` column
- [ ] Account deletion completes in < 5s
- [ ] All queries use existing indexes (no new indexes needed)

## Security Checklist

- [ ] All endpoints require JWT authentication
- [ ] Users can only access their own profile (user_id from token)
- [ ] Admin endpoints require admin role check
- [ ] Account deletion requires password confirmation
- [ ] Bio and display_name are escaped in frontend (XSS prevention)
- [ ] SQL injection prevented by SQLAlchemy ORM

## Next Steps

After completing this feature:
1. Run full test suite and verify 80%+ coverage
2. Test E2E flows with Playwright
3. Update CLAUDE.md with new endpoints
4. Create PR and request review
5. Deploy to staging and verify

## References

- [Feature Spec](./spec.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/)
- [F01 Auth Documentation](../001-auth/)
- [F02 Database Schema](../002-database-schema/)
