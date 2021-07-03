# Testing Framework for Niffler Modules

## Setup

Install the requirements from `<repo-home>/requirements-dev.txt`

```
pip install -r requirements-dev.txt
```

Add the test data in `<repo-home>/tests/data/<module-name>/input` for respective tests.

### PNG Extraction Test Data Setup

Test data in `<repo-home>/tests/data/png-extraction/input`.

For unit tests, add a valid dcm file, with name `test-img.dcm`.

### Meta Extraction Test Data Setup

Test data in `<repo-home>/tests/data/meta-extraction/input`.

For unit tests, add a valid dcm file, with name `test-img.dcm`.

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
