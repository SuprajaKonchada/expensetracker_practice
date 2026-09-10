# React Frontend Standards

## React

- Use React for all new frontend functionality.
- Follow the existing React project structure and conventions.
- Build reusable components where appropriate.
- Keep components focused on a clear responsibility.
- Avoid excessively large components.
- Prefer composition and reusable components over duplicated UI code.
- Use meaningful names for components, hooks, variables, and files.
- Follow consistent component and file naming conventions.
- Reuse existing components and utilities where appropriate.
- Do not introduce a new frontend library without a clear reason.

## State Management

- Keep state as close as possible to the component that owns it.
- Avoid unnecessary global state.
- Do not duplicate the same source of truth across multiple components.
- Handle loading, success, empty, and error states explicitly.

## API Integration

- Communicate with the backend through the application's API layer.
- Do not access SQLite directly from React.
- Reuse existing API utilities where available.
- Handle API loading and error states.
- Do not expose backend secrets, database credentials, or private configuration in frontend code.

## Forms and Validation

- Validate user input before sending requests where appropriate.
- Provide clear validation feedback.
- Do not rely on frontend validation as the only validation.
- Backend validation remains mandatory.

## UI

- Preserve existing user workflows unless a requirement explicitly changes them.
- Maintain consistent layouts, spacing, typography, and interaction patterns.
- Reuse existing UI components where appropriate.
- Provide clear success and error feedback.
- Ensure interactive elements have appropriate accessible labels.
- Avoid unnecessary UI duplication.

## Code Quality

- Keep JSX readable.
- Avoid deeply nested JSX where it reduces readability.
- Extract reusable UI into components.
- Keep business logic out of presentation components where practical.
- Avoid unnecessary effects and re-renders.
- Remove debugging statements before completion.

## Testing

- Test important user interactions.
- Test form validation.
- Test loading, empty, success, and error states.
- Test important API integration behavior.
- Use the testing tools already established by the React project.