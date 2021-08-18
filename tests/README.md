# Testing Framework for Niffler Modules

## Overview

This framework includes Unit and Integration Testing of various Niffler Modules. It utilizes `pytest` and GitHub Actions to execute Automated Testing Workflows.

Tests for the following Niffler modules have been added

- Unit Tests
  - Cold Extraction
  - Dicom Anonymization
  - Metadata Extraction
  - PNG Extraction
- Integration Tests
  - Dicom Anonymization
  - PNG Extraction

## Setup

Install the requirements from `<repo-home>/requirements-dev.txt`

```
pip install -r requirements-dev.txt
```

### Test Data

Unzip tests/data.zip in test directory.

```bash
unzip ./tests/data.zip -d ./tests/
```

## Running Tests

Initialize the required data, and run tests from `<repo-home>`.

```bash
pytest ./tests
```

For coverage report, run

```bash
pytest ./tests --cov=./modules --cov-report=html
```

and open the `<repo-home>/htmlcov/index.html`
