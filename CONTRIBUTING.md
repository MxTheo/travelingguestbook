
# Contributing to Gemene Grond

First off, thanks for taking the time to contribute!

All types of contributions are encouraged and valued. Please make sure to read the relevant section before making your contribution.

## Table of Contents

- [Contributing to Gemene Grond](#contributing-to-gemene-grond)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [I Have a Question](#i-have-a-question)
  - [I Want To Contribute](#i-want-to-contribute)
    - [Legal Notice](#legal-notice)
    - [Reporting Bugs](#reporting-bugs)
      - [Before Submitting a Bug Report](#before-submitting-a-bug-report)
      - [Submitting a Bug Report](#submitting-a-bug-report)
    - [Suggesting Enhancements](#suggesting-enhancements)
      - [Before Submitting an Enhancement](#before-submitting-an-enhancement)
      - [Submitting an Enhancement](#submitting-an-enhancement)
    - [Your First Code Contribution](#your-first-code-contribution)
      - [Development Setup](#development-setup)
    - [Initial Data](#initial-data)
  - [Data Models](#data-models)
    - [Street Activities](#street-activities)
    - [Experiences](#experiences)
    - [Tags](#tags)
    - [Personas](#personas)
  - [Styleguides](#styleguides)
    - [Python/Django Code](#pythondjango-code)
    - [Commit Messages](#commit-messages)
    - [Templates](#templates)
    - [Pull Request Process](#pull-request-process)
    - [PR Description Should Include:](#pr-description-should-include)
  - [Join The Project Team](#join-the-project-team)
  - [Questions?](#questions)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## I Have a Question

Before you ask a question, please:

1. Check the existing [Documentation](https://github.com/username/gemene-grond/wiki)
2. Search existing [Issues](https://github.com/username/gemene-grond/issues)

If you still need clarification:

- Open a new Issue
- Provide as much context as possible
- Include relevant versions (Python, Django, etc.)

## I Want To Contribute

### Legal Notice

When contributing, you must agree that you have authored 100% of the content, have the necessary rights, and that your contributions may be provided under the project license.

### Reporting Bugs

#### Before Submitting a Bug Report

- Ensure you're using the latest version
- Check if it's truly a bug, not an environment issue
- Search existing issues and online resources
- Collect relevant information:
  - Stack trace
  - OS and Python version
  - Steps to reproduce

#### Submitting a Bug Report

- Open an Issue
- Use a clear, descriptive title
- Explain expected vs actual behavior
- Provide reproduction steps
- Include relevant code/screenshots

### Suggesting Enhancements

#### Before Submitting an Enhancement

- Check if the feature already exists
- Search for similar suggestions
- Ensure it aligns with project philosophy

#### Submitting an Enhancement

- Use clear, descriptive title
- Provide detailed description
- Explain benefits for users
- Include examples or mockups

### Your First Code Contribution

#### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/gemene-grond.git
cd gemene-grond

# Environment setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py loaddata initial_tags
python manage.py loaddata initial_streetactivities
python manage.py loaddata initial_personas

# Run tests
python manage.py test

# Start server
python manage.py runserver
```

### Initial Data

The project includes fixture data:

- initial_tags.json - NVC-based tags for experiences
- initial_streetactivities.json - Example street activities
- initial_personas.json - Common passer-by personas

To create your own fixtures:
```python manage.py dumpdata streetactivities.StreetActivity --indent 2 > fixtures/initial_streetactivities.json```

## Data Models

### Street Activities

- Represent different ways to engage with strangers
- Methods: "invite" (with signs), "approach" (direct contact), or "both"
- Include clear questions and required supplies

### Experiences

- Reflections from practitioners (from_practitioner=True) or passers-by (False)
- Phases: pioneer (challenging), intermediate (intense), climax (peaceful)
- Use NVC tags to describe needs and feelings

### Tags

- Based on Nonviolent Communication principles
- Categories: needs, fulfilled feelings, unfulfilled feelings
- Hierarchical structure for better organization

### Personas

- Typologies of passers-by
- With related problems and reactions

## Styleguides

### Python/Django Code

- Follow PEP 8 and Django coding style
- Use descriptive variable names
- Document complex logic
- Write tests for new features

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Be descriptive and concise
- Reference issues when applicable

### Templates

- Use Bootstrap 5 classes
- Maintain accessibility standards
- Keep templates simple and clean

### Pull Request Process

- Fork the repository
- Create a feature branch: git checkout -b feature/description
- Make your changes
- Add tests, make sure that all python code has unittests
- Ensure all tests pass
- Submit a pull request

### PR Description Should Include:

- What and why changed
- Screenshots for UI changes
- Test results
- Related issue numbers

## Join The Project Team

Regular contributors may be invited to join the project team. We value:

- Consistent, quality contributions
- Understanding of project philosophy
- Helpful community engagement

## Questions?

- Open an Issue for bugs or questions
- Check the Wiki for user documentation
- Contact maintainers for private concerns

**Every contribution, no matter how small, helps deepen our collective understanding.**
