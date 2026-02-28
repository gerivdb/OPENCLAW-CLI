# 🦞 OPENCLAW-CLI - Command Line Interface

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OPENCLAW](https://img.shields.io/badge/OPENCLAW-CLI-green)](https://github.com/gerivdb/OPENCLAW)

Command-line interface for **OpenClaw** L1 semantic intent normalizer.

## 📦 Installation

### From Source

```bash
git clone https://github.com/gerivdb/OPENCLAW-CLI.git
cd OPENCLAW-CLI
pip install -e .
```

### Global Install

```bash
pip install git+https://github.com/gerivdb/OPENCLAW-CLI.git
```

## 🚀 Quick Start

### Normalize Intent

```bash
# Basic normalization
openclaw normalize "surveille le budget phi"

# With JSON output
openclaw normalize "crée un rollback guardian" --format json

# Batch file processing
openclaw normalize --file intents.txt --output results.jsonl
```

### Validate Canonical Spec

```bash
# Validate JSON-LD spec
openclaw validate spec.json

# Validate with IntentHash calculation
openclaw validate spec.json --hash
```

### Info & Stats

```bash
# Show normalizer info
openclaw info

# Show available patterns
openclaw info --patterns

# Check Kimi availability
openclaw info --kimi
```

## 📚 Commands

### `normalize`

Normalize raw intent to canonical JSON-LD specification.

```bash
openclaw normalize [OPTIONS] INTENT

Options:
  -f, --file PATH          Input file (one intent per line)
  -o, --output PATH        Output file (default: stdout)
  --format [text|json|jsonl]  Output format
  --kimi / --no-kimi       Enable/disable Kimi fallback
  --confidence FLOAT       Minimum confidence threshold
  --wal PATH               WAL database path for logging
```

**Examples**:

```bash
# Single intent
openclaw normalize "monitor phi budget" --format json

# Batch processing
openclaw normalize --file intents.txt --output normalized.jsonl

# With WAL logging
openclaw normalize "test" --wal ./openclaw_wal.db
```

### `validate`

Validate canonical specification compliance.

```bash
openclaw validate [OPTIONS] SPEC_FILE

Options:
  --hash                   Calculate IntentHash¹¹
  --level [L0|L1|L2|L3]   Validation level
  --strict                Strict validation (fail on warnings)
```

**Examples**:

```bash
# Basic validation
openclaw validate my_spec.json

# With IntentHash
openclaw validate my_spec.json --hash

# Strict L2 validation
openclaw validate my_spec.json --level L2 --strict
```

### `info`

Display OpenClaw normalizer information.

```bash
openclaw info [OPTIONS]

Options:
  --patterns      Show built-in normalization patterns
  --kimi          Check Kimi K2.5 local availability
  --metrics       Show normalizer metrics (if available)
  --version       Show version info
```

## 🔧 Integration with OPENCLAW Core

OPENCLAW-CLI uses [OPENCLAW](https://github.com/gerivdb/OPENCLAW) as a library:

```python
# CLI internally uses:
from openclaw import OpenClawNormalizer
from openclaw.integrations import KimiLocalClient

normalizer = OpenClawNormalizer(kimi_client=KimiLocalClient())
result = await normalizer.normalize(user_intent)
```

## 📊 Output Formats

### Text (default)

```
Raw Intent: surveille le budget phi
Method: pattern_match
Confidence: 0.91
Tools: C49
Canonical Spec:
{"citizen":"PhiBudgetGuardian","level":"L2",...}
```

### JSON

```json
{
  "raw_intent": "surveille le budget phi",
  "canonical_spec": "{...}",
  "tools_recommended": ["C49"],
  "confidence": 0.91,
  "normalization_method": "pattern_match",
  "timestamp": "2026-02-28T20:35:00+01:00"
}
```

### JSONL (batch)

```jsonl
{"raw_intent":"intent 1",...}
{"raw_intent":"intent 2",...}
{"raw_intent":"intent 3",...}
```

## 🧪 Configuration

Create `~/.openclaw/config.toml`:

```toml
[normalizer]
confidence_threshold = 0.65
enable_kimi = true

[kimi]
host = "127.0.0.1"
port = 8765
timeout_ms = 300

[wal]
default_path = "~/.openclaw/wal.db"
auto_log = true

[output]
default_format = "json"
color = true
```

## 🔗 Related Projects

- [OPENCLAW](https://github.com/gerivdb/OPENCLAW) - Core normalizer library
- [ECOYSTEM](https://github.com/gerivdb/ECOYSTEM) - ECOSYSTEM-1 core
- [ECOS-CLI](https://github.com/gerivdb/ECOS-CLI) - ECOS orchestrator

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

**φ-CPS Impact**: +0.0 (CLI tooling)  
**Intent Hash**: `0xH0_OPENCLAW_CLI_P0`  
**Created**: 2026-02-28
