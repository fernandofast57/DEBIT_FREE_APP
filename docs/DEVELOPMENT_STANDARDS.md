
# Development Standards

## Code Style
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Maximum line length: 100 characters
- Use 4 spaces for indentation

## Naming Conventions
- Classes: PascalCase (e.g., GoldTransaction)
- Functions/Methods: snake_case (e.g., calculate_commission)
- Variables: snake_case (e.g., user_balance)
- Constants: UPPER_CASE (e.g., MAX_PURCHASE_AMOUNT)

## Documentation
- All public APIs must have docstrings
- Update GLOSSARY.md when adding new terms
- Keep API_DOCUMENTATION.md in sync with code changes

## Testing
- Minimum 80% test coverage
- Unit tests for all business logic
- Integration tests for API endpoints
- Run full test suite before commits

## Security
- Input validation for all endpoints
- Rate limiting for public APIs
- Secure password storage (bcrypt)
- Two-factor authentication for sensitive operations

## Version Control
- Descriptive commit messages
- One feature per branch
- Squash commits before merging
- Code review required for all changes
