# Security Standards

## Secrets and Configuration

- Never hard-code passwords, API keys, tokens, database credentials, or secrets.
- Use environment variables or the project's secure configuration mechanism.
- Do not commit secrets to source control.
- Do not expose backend secrets or database credentials to the React frontend.
- Do not include secrets in API responses.
- Do not log passwords, tokens, credentials, or sensitive user data.

## Input Validation

- Validate and sanitize user input.
- Do not trust frontend validation alone.
- Backend validation is mandatory for all data received through APIs.
- Validate data before performing database operations.
- Reject invalid or unexpected input with appropriate error responses.

## API Security

- Return appropriate HTTP status codes.
- Do not expose stack traces to users.
- Do not expose internal implementation details.
- Do not expose database errors directly to users.
- Handle expected exceptions safely.
- Use authentication and authorization checks where required.

## SQLite Security

- Use parameterized queries or the project's safe database-access mechanism.
- Never build SQL statements by concatenating untrusted user input.
- Restrict database access to the backend/data-access layer.
- Do not expose the SQLite database file through the frontend.
- Protect database files and credentials appropriately.

## MCP Security

- Follow the principle of least privilege.
- Give MCP servers only the permissions required for the task.
- Do not give MCP access to unrelated files or databases.
- Do not grant destructive permissions unless they are explicitly required.
- Review MCP configuration before using external tools.
- Do not use MCP to access unrelated project or user data.
- Verify the scope of MCP operations before executing them.

## Dependencies

- Do not introduce unnecessary dependencies.
- Review dependencies for known security issues when appropriate.
- Keep dependencies explicitly declared and version controlled.

## Security Review

- Security-sensitive changes should receive additional review before completion.
- Review authentication, authorization, validation, database access, secrets,
  and external integrations before considering security-sensitive work complete.