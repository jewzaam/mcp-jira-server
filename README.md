# JIRA Extractor

A command-line tool for extracting JIRA issues and related issues with configurable export options and relationship traversal.

## Setup

### Prerequisites
- Python 3.8 or higher
- Access to a JIRA instance with valid credentials

### Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Authentication Setup

#### Option 1: Using secret-tool (Recommended for Linux)

Store your JIRA token securely using the system keyring:

```bash
# Store token in keyring
JIRA_USER=$USER
secret-tool store --label="JIRA API Token" service jira-pat-for-$JIRA_USER

# Retrieve and use token (using public RFE issue, no auth required)
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877
# Or with authentication:
JIRA_USER=$USER && JIRA_TOKEN=$(secret-tool lookup service jira-pat-for-$JIRA_USER) && python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username "$JIRA_USER" --token "$JIRA_TOKEN"
```

#### Option 2: Environment Variables

Create a configuration file (recommended) or export variables directly:

```bash
# Create config file (automatically ignored by git)
cat > .env <<EOF
export JIRA_URL="https://issues.redhat.com"
export JIRA_USER="your-username"
export JIRA_TOKEN="your-api-token"
EOF

# Source config and run
source .env
python jira_extractor.py -u "$JIRA_URL" -i RFE-7877 --username "$JIRA_USER" --token "$JIRA_TOKEN"
```

#### Option 3: Configuration Script

Create a shell script with your settings:

```bash
# Create config file
cat > jira-config.sh <<EOF
#!/bin/bash
# JIRA Configuration - DO NOT COMMIT TO VERSION CONTROL
export JIRA_URL="https://issues.redhat.com"
export JIRA_USER="your-username"
export JIRA_TOKEN="your-api-token"
EOF

chmod +x jira-config.sh

# Use configuration
source ./jira-config.sh
python jira_extractor.py -u "$JIRA_URL" -i RFE-7877 --username "$JIRA_USER" --token "$JIRA_TOKEN"
```

### Basic Usage Examples

Extract a single issue to stdout:
```bash
# Public issue (no authentication required)
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877

# Or with authentication for private issues
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken
```

Using with stored credentials:
```bash
# With secret-tool
JIRA_USER=$USER && JIRA_TOKEN=$(secret-tool lookup service jira-pat-for-$JIRA_USER) && python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username "$JIRA_USER" --token "$JIRA_TOKEN"

# With config file
source ./jira-config.sh
python jira_extractor.py -u "$JIRA_URL" -i RFE-7877 --username "$JIRA_USER" --token "$JIRA_TOKEN"
```

### Output Options

Output to stdout (default):
```bash
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken -o -
```

Output to directory:
```bash
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken -o ./output
```

### Advanced Options

Include expanded fields:
```bash
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken --expand "changelog,comments,subtasks"
```

Enable debug logging:
```bash
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken --debug
```

Overwrite existing files:
```bash
python jira_extractor.py -u https://issues.redhat.com -i RFE-7877 --username $USER --token mytoken -o ./output --overwrite
```

### Testing with Makefile

The project includes a Makefile with useful targets for testing connectivity:

```bash
# Test connection with stored credentials
source ./jira-config.sh
JIRA_URL="$JIRA_URL" JIRA_USER="$JIRA_USER" JIRA_TOKEN="$JIRA_TOKEN" make test-connection

# Or with secret-tool  
export JIRA_URL="https://issues.redhat.com" && export JIRA_USER=$USER && export JIRA_TOKEN=$(secret-tool lookup service jira-pat-for-$JIRA_USER) && make test-connection
```

### Security Notes

- **Never commit credentials to version control**
- Use `secret-tool` on Linux systems for secure token storage
- Configuration files (`.env`, `jira-config.sh`) are automatically ignored by git
- API tokens are preferred over passwords for automation
- Limit token permissions to read-only when possible
- Store tokens in system keyring or encrypted configuration files
- Use `chmod 600` to restrict configuration file permissions

### Command Line Options

```
Options:
  -u, --url TEXT        JIRA instance URL  [required]
  --username TEXT       JIRA username  [required]
  --password TEXT       JIRA password (will prompt if not provided)
  --token TEXT          API token (use instead of password)
  -i, --issue TEXT      JIRA issue key (e.g., PROJ-123)  [required]
  -o, --output TEXT     Output directory or "-" for stdout (default: stdout)
  --expand TEXT         Comma-separated fields to expand (e.g., changelog,comments)
  --debug               Enable debug logging
  --overwrite           Overwrite existing files
  --help                Show this message and exit.
```

## Authentication

### API Token Setup

#### 1. Generate JIRA API Token
For better security, use API tokens instead of passwords:

1. Log into your JIRA instance (https://issues.redhat.com)
2. Go to Account Settings → Security → API Tokens
3. Create a new API token
4. Copy the token for use with the tool

#### 2. Store Token Securely

**Using secret-tool (Linux):**
```bash
# Install secret-tool (if not already installed)
sudo dnf install libsecret-tools    # Fedora/RHEL
sudo apt install libsecret-tools     # Ubuntu/Debian

# Store your token
secret-tool store --label="JIRA API Token" service jira username your-username
# You'll be prompted to enter your token
```

**Using configuration file:**
```bash
# Create secure config file
cat > jira-config.sh <<EOF
#!/bin/bash
export JIRA_URL="https://issues.redhat.com"
export JIRA_USER="your-username"
export JIRA_TOKEN="your-api-token-here"
EOF

chmod 600 jira-config.sh  # Restrict permissions
```

### Basic Authentication (Not Recommended)
If API tokens are not available, you can use username/password authentication. The password will be prompted securely if not provided on the command line.

## Output Format

All output is in JSON format, matching the native JIRA REST API response structure. When outputting to a directory, each issue is saved as `{ISSUE-KEY}.json`.

## Error Handling

The tool provides clear error messages for common scenarios:
- Authentication failures
- Network connectivity issues
- Issue not found or access denied
- File system errors (permissions, disk space)

## License

This program is licensed under GPL-3.0-or-later. See the LICENSE file for details.

## Attribution

Generated by: Cursor (Claude)
Copyright (C) 2025 Naveen Z. Malik 