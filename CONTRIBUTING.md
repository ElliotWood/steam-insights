# Contributing to Steam Insights

Thank you for considering contributing to Steam Insights! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of SQLAlchemy, FastAPI, and Streamlit
- (Optional) PostgreSQL for database development

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/steam-insights.git
   cd steam-insights
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies including development tools:
   ```bash
   pip install -r requirements.txt
   pip install black flake8 mypy pytest pytest-cov
   ```

5. Set up your environment:
   ```bash
   cp .env.example .env
   # Add your Steam API key to .env
   ```

6. Initialize the database:
   ```bash
   python setup.py
   ```

## Development Workflow

### Creating a New Feature

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines below

3. Write or update tests for your changes

4. Run tests to ensure they pass:
   ```bash
   pytest tests/ -v
   ```

5. Format your code:
   ```bash
   black src/ tests/
   ```

6. Check code quality:
   ```bash
   flake8 src/ tests/
   ```

7. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

8. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

9. Create a Pull Request on GitHub

### Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Error messages or logs
- Screenshots (if applicable)

Use the GitHub issue tracker and label your issue as "bug".

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Check existing issues to avoid duplicates
- Clearly describe the enhancement
- Explain why it would be useful
- Provide examples if possible

Use the GitHub issue tracker and label your issue as "enhancement".

## Code Style Guidelines

### Python Code Style

- Follow PEP 8 style guide
- Use Black formatter with default settings
- Maximum line length: 88 characters (Black default)
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes

Example:
```python
def import_game(self, app_id: int) -> Optional[Game]:
    """
    Import or update a game from Steam.
    
    Args:
        app_id: Steam application ID
        
    Returns:
        Game object if successful, None otherwise
    """
    # Implementation here
```

### Code Organization

- One class per file when possible
- Group related functionality in modules
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Database Models

- Use descriptive table and column names
- Define appropriate indexes
- Document relationships
- Use proper data types

### API Development

- Follow RESTful conventions
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Return proper status codes
- Document endpoints with Pydantic models
- Handle errors gracefully

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Mock external API calls
- Test edge cases and error conditions

Example:
```python
def test_import_game_success(test_db):
    """Test successful game import."""
    importer = GameDataImporter(test_db)
    game = importer.import_game(730)
    
    assert game is not None
    assert game.steam_appid == 730
    assert game.name == "Counter-Strike 2"
```

## Project Structure

When adding new features, follow the existing structure:

```
src/
├── api/           # API endpoints and clients
├── database/      # Database connections
├── models/        # Data models
├── etl/          # Data import and processing
├── scrapers/     # Web scrapers
├── dashboard/    # UI components
└── utils/        # Utility functions
```

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Mock external dependencies
- Use pytest fixtures for common setup

### Integration Tests

- Test complete workflows
- Use test database
- Verify data persistence

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_models.py

# Specific test function
pytest tests/test_models.py::test_create_game
```

## Documentation

### Code Documentation

- Write docstrings for all public functions and classes
- Use Google or NumPy docstring style
- Include type hints
- Document exceptions that can be raised

### README Updates

When adding significant features:
- Update the main README.md
- Add usage examples
- Update feature list
- Add any new configuration requirements

### API Documentation

- FastAPI automatically generates docs from Pydantic models
- Ensure models have descriptions
- Add response examples when helpful

## Pull Request Process

1. **Before Submitting:**
   - Ensure tests pass
   - Format code with Black
   - Check with flake8
   - Update documentation
   - Add or update tests

2. **PR Description:**
   - Describe what changes you made
   - Explain why the changes are needed
   - Link related issues
   - Include screenshots for UI changes

3. **Review Process:**
   - Maintainers will review your PR
   - Address any requested changes
   - Keep PR focused on a single feature/fix

4. **After Approval:**
   - PR will be merged by maintainers
   - Delete your feature branch

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- Additional Steam API integrations
- Performance optimizations
- Enhanced error handling
- More comprehensive tests
- Documentation improvements

### Features
- Scheduled data updates
- Advanced analytics and predictions
- Additional visualizations
- Data export functionality
- User authentication and preferences

### Data Sources
- Integration with other gaming APIs
- Additional web scrapers
- Kaggle dataset importers
- Regional data support

### Quality
- Code coverage improvements
- Type hint coverage
- Logging improvements
- Error messages

## Questions?

If you have questions about contributing:

- Check existing documentation
- Search closed issues for similar questions
- Open a new issue with the "question" label
- Join discussions in pull requests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Accept criticism gracefully
- Prioritize the community's best interests

### Enforcement

Unacceptable behavior can be reported to project maintainers. All complaints will be reviewed and investigated.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub's contributor graph

Thank you for contributing to Steam Insights! 🎮
