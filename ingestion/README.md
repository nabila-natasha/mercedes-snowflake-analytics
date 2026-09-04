# Ingestion

The ingestion layer contains dependencies and supporting components for
moving source data into Snowflake.

Python is used as the primary ingestion technology.

---

# Responsibilities

The ingestion layer is responsible for:
1. Source retrieval
2. Source file handling
3. Snowflake connectivity
4. Stage loading
5. RAW table loading

Transformation is deliberately separated from ingestion.

---

# Loading Pattern

For file-based data:

```text
Source File
    |
    v
Python
    |
    v
Snowflake Internal Stage
    |
    v
COPY INTO
    |
    v
RAW Table
```

For API-based data:

```text
Public API
    |
    v
Python
    |
    v
Snowflake
    |
    v
   RAW
```

---

# Dependencies

Python dependencies required for ingestion are maintained in:  
`requirements.txt`

---

# Security

Credentials are supplied through environment variables or GitHub Secrets.

They are not committed to the repository.
