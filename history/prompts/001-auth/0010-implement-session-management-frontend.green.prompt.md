---
id: 0010
title: Implement session management frontend
stage: green
date: 2026-03-14
surface: agent
model: claude-sonnet-4.5
feature: 001-auth
branch: 001-auth
user: saifullah
command: implementation
labels: ["frontend", "session-management", "logout", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /home/saifullah/projects/agentic-ai/hackathon-2-learning-platform/frontend/hooks/useAuth.tsx
  - /home/saifullah/projects/agentic-ai/hackathon-2-learning-platform/frontend/components/Navigation.tsx
tests:
  - TypeScript compilation check passed
---

## Prompt

Implement the session management frontend for Phase 9 (Tasks T102-T103):

**Context:**
- Backend logout endpoints will be implemented in parallel
- Need to add logout functionality to frontend
- This is part of User Story 6: Session Management & Logout (P2)

**Tasks to Complete:**

**T102: Implement logout functionality in useAuth hook**
- File: `frontend/hooks/useAuth.tsx`
- Add logout() function to AuthContext
- Call POST /api/auth/logout endpoint
- Clear tokens from localStorage
- Clear user state
- Redirect to login page
- Handle errors gracefully

**T103: Add logout button to navigation**
- File: `frontend/components/Navigation.tsx`
- Add logout button in user menu/dropdown
- Call logout() from useAuth hook
- Show confirmation dialog before logout (optional but recommended)
- Use Shadcn UI Button and DropdownMenu components
- Add loading state during logout

**Requirements:**
- Use TypeScript with proper types
- Follow existing patterns from useAuth hook
- Handle loading and error states
- Clear all authentication state on logout
- Redirect to /auth/login after successful logout
- Use Shadcn UI components for consistent design
- Add proper ARIA labels for accessibility
- Consider adding "Logout from all devices" option (calls /api/auth/logout-all)

**API Endpoints to Use:**
- POST /api/auth/logout (no body required, uses token from Authorization header)
- POST /api/auth/logout-all (optional, for logout from all devices)

**Existing Code References:**
- useAuth hook: `frontend/hooks/useAuth.tsx`
- Navigation component: `frontend/components/Navigation.tsx`

Please implement these tasks and ensure they integrate properly with the existing authentication system.

## Response snapshot

Enhanced the existing logout implementation with the following improvements:

**T102: useAuth Hook Enhancements**
- Added `isLoggingOut` state to track logout progress
- Updated `logout()` function to accept optional `fromAllDevices` parameter
- Implemented support for both `/api/auth/logout` and `/api/auth/logout-all` endpoints
- Added proper loading state management with `setIsLoggingOut()`
- Maintained error handling and token cleanup in finally block
- Exposed `isLoggingOut` in AuthContext for UI consumption

**T103: Navigation Component Enhancements**
- Added confirmation dialog using Shadcn Dialog component
- Implemented "Logout from all devices" checkbox option
- Added loading states to logout button (shows "Logging out..." text)
- Disabled buttons during logout operation
- Added proper ARIA labels for accessibility
- Implemented three handler functions:
  - `handleLogoutClick()` - Opens confirmation dialog
  - `handleConfirmLogout()` - Executes logout with selected option
  - `handleCancelLogout()` - Closes dialog and resets state

**Design Features:**
- Polished dialog UI with clear messaging
- Checkbox styled with proper focus states and transitions
- Descriptive text explaining "logout from all devices" option
- Consistent button styling with disabled states
- Responsive text (hides "Logout" text on small screens)

## Outcome

- ✅ Impact: Completed Phase 9 session management frontend (T102-T103). Added logout functionality with confirmation dialog, loading states, and "logout from all devices" option.
- 🧪 Tests: TypeScript compilation passed with no errors
- 📁 Files: Modified 2 files (useAuth.tsx, Navigation.tsx)
- 🔁 Next prompts: Backend logout endpoints implementation, integration testing
- 🧠 Reflection: Implementation follows existing patterns and enhances UX with confirmation dialog and multi-device logout option. All requirements met including TypeScript types, error handling, loading states, and accessibility.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): TypeScript compilation PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test logout flow with backend integration once endpoints are implemented
