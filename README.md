# Config Secrets Scanner

A robust CLI tool for scanning directories to detect hardcoded secrets and sensitive information in your codebase.

## Features

- 🔍 **Recursive Directory Scanning**: Automatically scans all files in the current directory and subdirectories
- 🎯 **Multiple Secret Patterns**: Detects AWS keys, private keys, API tokens, database URLs, and more
- ⚠️ **Risk Level Classification**: Categorizes secrets as HIGH, MEDIUM, or LOW risk
- 🎨 **Rich Terminal UI**: Beautiful progress bars and color-coded tables using the `rich` library
- 🚫 **Smart Filtering**: Automatically ignores common directories (`.git`, `venv`, `node_modules`, etc.) and binary files
- 📊 **Detailed Reports**: Shows file path, line number, secret type, risk level, and masked snippet
- 🔒 **Security**: Masks sensitive information in output for safer viewing
- ⚡ **Performance**: Reads files line-by-line to handle large codebases efficiently

## Requirements

- Python 3.10 or higher
- `rich` library (installed automatically via install script)

## Installation

### Quick Install (Recommended)

Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

This script will:
- Check Python version (requires 3.10+)
- Install required dependencies (`rich`)
- Make the scanner executable

### Manual Installation

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Make the scanner executable (optional):
```bash
chmod +x scanner.py
```

## Usage

Scan the current directory:

```bash
python3 scanner.py
```

Or if you made it executable:

```bash
./scanner.py
```

The scanner will:
1. Recursively scan all files in the current directory
2. Display a progress bar showing scan status
3. Show a summary with risk level breakdown
4. Display a detailed table with all detected secrets

## Detected Secret Types

### HIGH RISK
- AWS Access Key IDs (e.g., `AKIA...`)
- AWS Secret Access Keys
- Private Keys (RSA, DSA, EC, OpenSSH)
- Database URLs with embedded passwords (PostgreSQL, MySQL, MongoDB)

### MEDIUM RISK
- Generic API tokens and access tokens
- GitHub Personal Access Tokens (`ghp_...`)
- Slack Webhook URLs
- Stripe Live Keys
- Slack Tokens

### LOW RISK
- Generic password variables (`password = "..."`)
- Secret variables (`secret = "..."`)
- API key variables (`apikey = "..."`)

## Ignored Paths

The scanner automatically ignores:

**Directories:**
- `.git`, `__pycache__`, `venv`, `env`
- `.idea`, `.vscode`, `node_modules`
- `.pytest_cache`, `.mypy_cache`

**File Extensions:**
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.ico`
- Binaries: `.pyc`, `.pyo`, `.exe`, `.dll`, `.so`, `.dylib`
- Archives: `.zip`, `.tar`, `.gz`
- Fonts: `.woff`, `.woff2`, `.ttf`, `.eot`
- Documents: `.pdf`

## Error Handling

The scanner gracefully handles:
- **Permission Errors**: Skips files without read permissions
- **Unicode Errors**: Uses `errors='ignore'` to handle binary files
- **Large Files**: Processes files line-by-line to minimize memory usage

## Example Output

```
Config Secrets Scanner

Scanning directory: /path/to/project

[cyan]Scanning files...[/cyan] ████████████████████ 100% 0:00:02

📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Secrets Found: 5

HIGH Risk:   3
MEDIUM Risk: 1
LOW Risk:    1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Secret Scan Results
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ File Path          ┃ Line┃ Secret Type        ┃ Risk     ┃ Snippet     ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ _test_secrets.env  │   5 │ AWS Access Key ID  │ HIGH     │ AKIA****    │
│ _test_secrets.env  │   6 │ AWS Secret...      │ HIGH     │ wJal****    │
│ _test_secrets.env  │  16 │ Database URL...    │ HIGH     │ postgres... │
│ _test_secrets.env  │  20 │ GitHub Personal... │ MEDIUM   │ ghp_****    │
│ _test_secrets.env  │  27 │ Password Variable  │ LOW      │ test****    │
└────────────────────┴─────┴────────────────────┴──────────┴─────────────┘

⚠️  Secrets detected! Please review and remove them immediately.
```

## Testing

A test file `_test_secrets.env` is included with fake secrets for demonstration purposes. Run the scanner to see it in action!

**Note:** This file contains fake secrets for testing only. Remove it before scanning your actual codebase.

## Limitations

- **Line-by-Line Scanning**: Multi-line secrets (like full private keys) may not be fully detected across line breaks
- **False Positives**: Some patterns may trigger false positives in test files or documentation
- **Pattern Coverage**: Additional secret types may need custom patterns for specific use cases

## Security Note

⚠️ **IMPORTANT**: This tool is for detecting secrets that should NOT be in your codebase. If you find real secrets:

1. **Immediately rotate/revoke** the compromised credentials
2. **Remove** the secrets from your codebase
3. **Use environment variables** or secure secret management solutions
4. **Review git history** to ensure secrets weren't committed previously

## License

This project is provided as-is for security scanning purposes.

## Contributing

Feel free to submit issues or pull requests to improve pattern detection or add new features.
