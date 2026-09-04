# Automated Tests

This directory contains automated tests used by the CI/CD pipeline.

---

# Purpose

The tests provide automated validation of project components before and
during production deployment.

Testing is intended to catch implementation and data-platform issues
before they reach the final production environment.

---

# Snowflake Production Tests

`test_snowflake_production.py`

The production test suite validates the Snowflake production environment
and expected production objects / data.

---

# CI/CD Integration

Tests are executed automatically through GitHub Actions.

```text
Git Push / Pull Request
        |
        v
GitHub Actions
        |
        v
Run Tests
        |
   +----+----+
   |         |
 PASS       FAIL
   |         |
   v         v
Continue    Stop
```

A failed test prevents the workflow from being considered successful.

---

# Test Philosophy

The tests complement, rather than replace the deployment validation.

```text
Automated Tests
      +
Snowflake Production Validation
      +
Power BI Verification
      =
End-to-End Validation
```
