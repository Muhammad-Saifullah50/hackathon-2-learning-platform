# Data Model: Python Code Sandbox

## Entity: CodeSubmission

**Description**: Represents a student's code execution attempt in the learning platform. Only successful executions are persisted for progress tracking and analytics.

### Fields
- `id` (UUID, Primary Key) - Unique identifier for the submission
- `user_id` (UUID, Foreign Key) - References the authenticated user who submitted the code
- `module_id` (UUID, Optional) - References the curriculum module this code relates to
- `lesson_id` (UUID, Optional) - References the specific lesson this code relates to
- `exercise_id` (UUID, Optional) - References the exercise this code is a solution for
- `code_content` (Text) - The actual Python code submitted by the student
- `language` (String, Default: "python") - Programming language of the submission
- `execution_output` (Text, Optional) - Captured program output from successful execution
- `error_message` (Text, Optional) - Error message if execution failed
- `execution_time_ms` (Integer) - Time taken for execution in milliseconds
- `status` (Enum: "success", "timeout", "error", "blocked") - Execution result status
- `error_type` (String, Optional) - Classification of error (e.g., "SyntaxError", "NameError")
- `memory_used_bytes` (Integer, Optional) - Peak memory usage during execution
- `created_at` (DateTime, Default: now) - Timestamp when submission was created
- `updated_at` (DateTime, Default: now) - Timestamp when record was last updated

### Validation Rules
- `code_content` must be 1-10,000 characters (enforced before execution)
- `execution_time_ms` must be 0-8000 (max 8 seconds including overhead)
- `status` must be one of the allowed enum values
- `memory_used_bytes` must be 0-100MB if provided
- `user_id` must reference a valid user record
- Only records with `status = "success"` are persisted (other statuses are logged but not stored)

### Relationships
- **One-to-Many**: User → CodeSubmission (one user can have many code submissions)
- **Many-to-One**: CodeSubmission → Module (optional reference to curriculum module)
- **Many-to-One**: CodeSubmission → Lesson (optional reference to specific lesson)
- **Many-to-One**: CodeSubmission → Exercise (optional reference to exercise)

### State Transitions
- `created` → `executing` → `success` → `stored` (only successful executions are persisted)
- `created` → `executing` → `timeout` → `discarded` (not persisted)
- `created` → `executing` → `error` → `discarded` (not persisted)
- `created` → `validating` → `blocked` → `discarded` (invalid code, not persisted)

### Indexes
- `idx_user_created_at` (user_id, created_at) - For querying user's submission history
- `idx_module_created_at` (module_id, created_at) - For module progress analytics
- `idx_exercise_status` (exercise_id, status) - For exercise completion statistics
- `idx_created_at` (created_at) - For chronological queries and cleanup jobs

## Entity: ImportWhitelist

**Description**: Configuration entity that defines the list of allowed Python standard library modules for student code imports.

### Fields
- `id` (UUID, Primary Key) - Unique identifier for the whitelist entry
- `module_name` (String) - Name of the allowed Python module (e.g., "math", "json")
- `category` (String) - Category of the module (e.g., "mathematics", "data_structures")
- `description` (Text) - Description of what the module does and why it's safe
- `is_active` (Boolean, Default: true) - Whether this module is currently allowed
- `created_at` (DateTime, Default: now) - When this whitelist entry was created
- `updated_at` (DateTime, Default: now) - When this whitelist entry was last updated

### Validation Rules
- `module_name` must be a valid Python standard library module name
- `category` must be one of: "core", "mathematics", "data_structures", "text_processing", "formats", "dates", "algorithms", "errors"
- `module_name` must be unique within active entries

### Indexes
- `idx_module_name_active` (module_name, is_active) - For fast lookup of allowed modules
