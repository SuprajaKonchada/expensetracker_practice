# Testing Standards

## General

- Every new feature must include appropriate tests.
- Existing tests must continue to pass after changes.
- Do not remove or weaken tests simply to make the test suite pass.
- Tests must verify meaningful behavior rather than merely increasing coverage numbers.
- Follow the testing tools and conventions already established by the project.

## Python Backend

- Test business logic independently.
- Test important API endpoints.
- Test validation and error cases.
- Test expected exception handling.
- Test important database behavior.
- Test API responses and HTTP status codes.
- Test important service/business logic independently from API controllers where practical.

## React Frontend

- Test important user interactions.
- Test form validation.
- Test loading states.
- Test empty states.
- Test success states.
- Test error states.
- Test important API integration behavior.
- Test important component behavior.
- Use the testing tools already established by the React project.

## SQLite

- Test important database operations.
- Test data creation and retrieval.
- Test updates and deletes where applicable.
- Test important constraints and validation.
- Test database-related error handling.
- Use isolated test data and avoid relying on production data.

## Test Pyramid

- Prefer many small, fast tests.
- Use fewer integration tests for interactions between components or layers.
- Use a smaller number of end-to-end tests for critical user workflows.

## Feature Testing Workflow

For every new feature:

1. Understand the feature requirement.
2. Identify affected frontend behavior.
3. Identify affected backend behavior.
4. Identify affected database behavior.
5. Define appropriate test cases.
6. Implement the feature.
7. Add or update tests.
8. Run relevant tests.
9. Fix failures caused by the implementation.
10. Verify the complete user workflow.

## Before Completion

- Run relevant backend tests.
- Run relevant frontend tests.
- Run relevant integration tests.
- Run end-to-end tests for critical workflows where applicable.
- Verify database behavior where applicable.
- Fix implementation-related failures.
- Report what was tested.
- Do not claim a feature is complete without verification.