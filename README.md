# Ross‑OS v0.1 — Semantic Reliability Middleware

Ross‑OS is a deterministic middleware layer engineered by The Ross Consultancy.
It stabilizes, normalizes, validates, and governs unstructured outputs from
multiple AI models (GPT, Claude, Gemini, etc.) into a single canonical payload.

Ross‑OS v0.1 includes:

1. The Normalization Engine
2. The Validation Engine (Structural, Semantic, Governance Firewalls)
3. The Action Registry (registry.json)
4. The Error Handling & Escalation Protocol
5. The Test Suite Manifest

Ross‑OS is not a model. It is semantic infrastructure.
ross-os-middleware/
├── .github/
│   └── workflows/
│       └── validation-ci.yml      # Automated pre-flight test pipeline
├── config/
│   └── registry.json              # Declarative Action Registry manifest
├── core/
│   ├── __init__.py
│   ├── normalizer.py              # Lexical sanitization & format compiling
│   └── validator.py               # Firewall logic & schema enforcement
├── schemas/
│   ├── payload.schema.json        # Canonical runtime payload validation schema
│   └── registry.schema.json       # Structural validation for registry.json
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test fixtures & static input mock definitions
│   └── test_firewalls.py          # Implementations of the 10 matrix boundary tests
├── main.py                        # System entry point / runtime gateway loop
├── README.md                      # Locked Architecture Specification document
└── requirements.txt               # Pin-point minimal engineering dependencies

ross-creative-consultancy/
│
├── ross-os/
│   ├── ross_os_middleware.py
│   ├── registry.json
│   ├── README.md
│   └── tests/
│       ├── test_01_claude_verbosity.json
│       ├── test_02_gpt_fragmentation.json
│       ├── test_03_gemini_markdown.json
│       ├── test_04_unicode_noise.json
│       ├── test_05_role_injection.json
│       ├── test_06_email_bypass.json
│       ├── test_07_unknown_action.json
│       ├── test_08_deprecated_action.json
│       ├── test_09_missing_parameter.json
│       └── test_10_multi_model_collision.json
│
└── (existing studio files)

