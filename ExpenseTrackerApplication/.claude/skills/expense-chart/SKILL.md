---
name: expense-chart
description: Add a category-wise expense distribution pie chart to the Expense Tracker using the existing .NET backend, React frontend, and SQLite database. Use this skill when implementing or updating expense visualization by category.
---

# Expense Distribution Pie Chart

Add a new Expense Distribution Pie Chart feature to the Expense Tracker.

## Requirements

- Display a pie chart showing the distribution of expenses by category.
- Calculate the total expense amount for each category using the existing expense data.
- Each pie chart slice should represent one expense category.
- The slice value must be based on the total amount spent in that category, not the number of expenses.
- Display the category name and corresponding expense amount clearly.
- Use the existing backend, React frontend, and SQLite database. Follow the backend framework, architecture, service layer, data-access patterns, and conventions already used by the project.- Use SQLite for persistent data storage.
- Follow all project instructions and standards defined in:
  - `architecture.md`
  - `backend-standards.md`
  - `frontend-standards.md`
  - `security-standards.md`
  - `testing-standards.md`
- Reuse existing APIs, services, components, and patterns where appropriate.
- Do not introduce unrelated functionality.
- Do not duplicate business logic unnecessarily between the backend and frontend.

## Implementation

1. Explore the existing Expense Tracker.
2. Identify how expenses and categories are currently stored and retrieved.
3. Identify the appropriate backend service, repository/data-access, model/schema, and API layers used by the project. Follow the existing framework and project patterns rather than introducing a new architecture.
4. Determine whether an existing API can be reused or whether a new API is required.
5. Identify where the pie chart should be displayed in the existing React UI.
6. Create an implementation plan.
7. Implement the feature.
8. Follow all applicable project standards.

## Verification

After implementation:

1. Run the application.
2. Verify that the pie chart loads correctly.
3. Verify that category totals are calculated correctly.
4. Verify that adding an expense updates the chart correctly.
5. Verify that editing an expense updates the chart correctly.
6. Verify that deleting an expense updates the chart correctly.
7. Verify that categories with no expenses are handled appropriately.
8. Add or update appropriate backend and frontend tests.
9. Run the tests and fix any failures.
10. Review the implementation against the project standards.

## Final Report

Report:

- Files created
- Files modified
- API changes
- Components created or modified
- Tests added or updated
- Verification results
- Any remaining issues