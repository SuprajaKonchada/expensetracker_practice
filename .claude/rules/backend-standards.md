# Python Backend Standards

## Python Coding

- Follow standard Python formatting and naming conventions.
- Follow existing project conventions unless they conflict with these rules.
- Use type hints for new Python code where practical.
- Prefer simple, readable, maintainable code.
- Avoid unnecessary duplication.
- Keep functions and methods focused on one responsibility.
- Use meaningful names for variables, functions, classes, modules, and files.
- Avoid excessively large files and functions.
- Avoid unnecessary global state.
- Reuse existing utilities where appropriate.
- Do not introduce a new framework or library without a clear reason.
- Keep dependencies explicitly declared and version controlled.
- Do not leave debugging statements in production code.
- Comments should explain why something is done when the reason is not obvious.
- Do not add comments that merely restate what the code does.

## Backend Architecture

- Keep API/controller functions small.
- Put business logic in service/business modules.
- Put database operations in a dedicated data-access/repository layer where applicable.
- Keep API, business logic, and database responsibilities separated.
- Reuse existing backend patterns where appropriate.

## API Standards

- Validate incoming API data before processing it.
- Return meaningful HTTP status codes.
- Return consistent error responses.
- Handle expected exceptions explicitly.
- Do not expose stack traces or internal implementation details through APIs.
- Do not expose database credentials or secrets through APIs.
- Keep API responses predictable and consistent.

## Configuration

- Use environment variables or configuration files for environment-specific settings.
- Do not hard-code secrets, credentials, tokens, or environment-specific values.
- Keep configuration separate from business logic.

## Database

- Keep SQLite operations in the data-access/repository layer.
- Use parameterized queries or the project's safe database-access mechanism.
- Do not construct SQL queries by directly concatenating untrusted user input.
- Handle expected database exceptions explicitly.
- Keep database transactions consistent and controlled.
- Do not introduce unnecessary database dependencies.

## Testing

- Add tests for new business logic.
- Add tests for new API behavior.
- Add tests for important database behavior.
- Update existing tests when backend behavior changes.