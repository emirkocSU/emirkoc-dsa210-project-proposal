# 🤝 Contributing to Premium Car Alert Bot

Thank you for your interest in contributing to the Premium Car Alert Bot! This document provides guidelines and information for contributors.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Process](#contributing-process)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to abide by these guidelines:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect different viewpoints and experiences

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/yourusername/premium-car-alert-bot.git
cd premium-car-alert-bot
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/originalowner/premium-car-alert-bot.git
```

## 🛠️ Development Setup

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.production .env
# Edit .env with your configuration
```

### Mobile App Setup

```bash
# Navigate to mobile app
cd expo-app

# Install dependencies
npm install

# Start development server
npx expo start
```

### Database Setup

```bash
# Initialize database
python -c "
import asyncio
from tgbot.database import DatabaseManager

async def init_db():
    db = DatabaseManager()
    await db.initialize()
    print('✅ Database initialized')

asyncio.run(init_db())
"
```

## 🔄 Contributing Process

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the coding standards below
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add: YOLOv8 model optimization for faster inference"
```

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/videos if applicable
- Checklist completion

## 📝 Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Use type hints
def process_car_image(image_url: str) -> Dict[str, Any]:
    """Process car image and return damage analysis."""
    pass

# Use async/await for I/O operations
async def fetch_car_data(listing_url: str) -> Optional[CarData]:
    """Fetch car data from listing URL."""
    pass

# Use descriptive variable names
damage_detection_result = await analyze_image(image_url)
user_subscription_status = await check_subscription(user_id)
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8 .
```

### JavaScript/TypeScript (Mobile App)

```typescript
// Use TypeScript for type safety
interface User {
  id: string;
  email: string;
  subscriptionActive: boolean;
}

// Use async/await
const fetchUserData = async (userId: string): Promise<User> => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

// Use descriptive component names
const CarDamageAnalysisScreen: React.FC = () => {
  return <View>...</View>;
};
```

### Naming Conventions

- **Files**: `snake_case` for Python, `camelCase` for TypeScript
- **Classes**: `PascalCase`
- **Functions**: `snake_case` for Python, `camelCase` for TypeScript
- **Variables**: `snake_case` for Python, `camelCase` for TypeScript
- **Constants**: `UPPER_SNAKE_CASE`

## 🧪 Testing Guidelines

### Python Tests

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=tgbot --cov-report=html

# Run specific test
python -m pytest tests/test_yolo.py::test_damage_detection
```

### Test Structure

```python
# tests/test_yolo.py
import pytest
from unittest.mock import AsyncMock, patch
from tgbot.utils.yolo import YOLOCarDamageDetector

@pytest.mark.asyncio
async def test_damage_detection():
    """Test YOLOv8 damage detection functionality."""
    detector = YOLOCarDamageDetector()
    
    # Mock external dependencies
    with patch('tgbot.utils.yolo.download_image') as mock_download:
        mock_download.return_value = b'fake_image_data'
        
        result = await detector.analyze_damage(['http://example.com/car.jpg'])
        
        assert result is not None
        assert 'damages' in result
        assert 'confidence' in result
```

### Mobile App Tests

```bash
# Run mobile app tests
cd expo-app
npm test

# Run with coverage
npm run test:coverage
```

## 📚 Documentation

### Code Documentation

```python
def analyze_car_damage(image_urls: List[str], confidence_threshold: float = 0.4) -> Dict[str, Any]:
    """
    Analyze car images for damage using YOLOv8.
    
    Args:
        image_urls: List of car image URLs to analyze
        confidence_threshold: Minimum confidence for damage detection (0.0-1.0)
    
    Returns:
        Dict containing:
            - damages: List of detected damages with positions and confidence
            - overall_score: Overall damage score (0-100)
            - processing_time: Time taken for analysis in seconds
    
    Raises:
        ValueError: If image_urls is empty or invalid
        NetworkError: If images cannot be downloaded
    """
    pass
```

### API Documentation

Update `API_DOCUMENTATION.md` when adding new endpoints:

```markdown
## POST /api/analyze-damage

Analyze car images for damage detection.

**Request:**
```json
{
  "image_urls": ["https://example.com/car1.jpg"],
  "confidence_threshold": 0.4
}
```

**Response:**
```json
{
  "damages": [...],
  "overall_score": 25,
  "processing_time": 12.5
}
```
```

## 🐛 Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11.1]
- Bot version: [e.g. 1.2.0]

**Screenshots**
If applicable, add screenshots
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered
```

## 🔍 Code Review Process

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No merge conflicts
- [ ] PR description is clear

### Review Criteria

- **Functionality**: Does the code work as intended?
- **Quality**: Is the code clean and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Testing**: Is the code adequately tested?

## 🏷️ Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(yolo): add YOLOv8 model caching for faster inference

fix(bot): resolve memory leak in image processing

docs(api): update damage detection endpoint documentation

test(scanner): add integration tests for car listing scanner
```

## 🎯 Areas for Contribution

### High Priority
- YOLOv8 model optimization
- Performance improvements
- Bug fixes and stability
- Test coverage improvements

### Medium Priority
- New car listing sources
- Mobile app features
- UI/UX improvements
- Documentation enhancements

### Low Priority
- Code refactoring
- Developer tooling
- CI/CD improvements

## 🤔 Questions?

- 💬 Join our [Telegram discussion group](https://t.me/PremiumCarAlertDev)
- 📧 Email: dev@premiumcaralert.com
- 🐛 Open an issue for bugs
- 💡 Open a discussion for feature ideas

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Hall of fame page
- Contributor spotlight (monthly)

Thank you for contributing to Premium Car Alert Bot! 🚗🤖✨