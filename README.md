# Obsidian Utilities

Advanced Obsidian vault content analysis and management utilities designed for Claude Code and CLI tools to safely manipulate, edit, and move files while preserving internal links.

## Overview

This collection provides powerful automation tools for Obsidian vaults, enabling:

- **Advanced vault content analysis** - Query and search through vault content using Obsidian's indexed search
- **Safe file manipulation** - Move and rename files while automatically updating all internal references
- **Link preservation** - Maintain wikilinks, markdown links, embeds, and complex references during file operations
- **CLI integration** - Designed specifically for use with Claude Code and other command-line tools

## Directory Structure

```
obsidian-utilities/
├── executable_scripts/           # All executable scripts (add this to PATH)
│   ├── mdget                    # Markdown content extraction and processing
│   ├── mv                       # Obsidian-aware file moving wrapper
│   ├── obsidian_mv             # Core markdown file renaming with reference updates
│   └── obsidian_query          # Query Obsidian vault via Local REST API
├── utilities_data/             # Data files and configurations
│   ├── mdget/                  # Markdown processing utilities
│   │   └── formatters.py       # Output formatting module
│   └── obsidian_mv/           # Obsidian utilities configuration
│       ├── obsidian_api.py    # API integration module
│       ├── settings.json      # Configuration settings
│       └── copy-to-vault-to-test/  # Test files
├── README/                     # Detailed documentation
│   ├── README_mv.md           # Enhanced mv utility docs
│   └── README_obsidian_mv.md  # Core obsidian_mv docs
└── supporting_docs/           # API documentation
    └── obsidian-local-api.md  # Obsidian Local REST API reference
```

## Prerequisites

### Required Setup

1. **Obsidian Local REST API Plugin**: Install and configure the [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) in Obsidian
2. **Environment Configuration**: Create a `.env` file in your utilities root directory with:
   ```
   LOCAL_OBSIDIAN_KEY="your_api_key_here"
   ```
3. **PATH Configuration**: Add the `executable_scripts` directory to your system PATH

### PATH Setup

Add the utilities to your PATH so they can be called from anywhere:

```bash
# Add to your ~/.zshrc (or ~/.bashrc)
export PATH="/path/to/obsidian-utilities/executable_scripts:$PATH"

# Reload your shell
source ~/.zshrc

# Clear command cache if needed
hash -r
```

**Important:** The utilities directory should be **prepended** to your PATH (before system directories) so the custom `mv` script takes precedence over the system `/bin/mv`.

## Available Utilities

### mdget - Markdown Content Extraction

Extract and process markdown content with flexible formatting options.

```bash
mdget document.md --property title,author    # Extract specific properties
mdget document.md --content                  # Extract main content
mdget document.md --format json              # Output as JSON
mdget --help                                 # Show all options
```

**Key Features:**
- Extract YAML frontmatter properties
- Process markdown content with custom formatting
- Multiple output formats (text, JSON, custom)
- Modular formatter system for extensibility

### mv & obsidian_mv - Obsidian-Aware File Moving

This system provides intelligent file moving/renaming for Obsidian vaults that automatically updates internal references when moving markdown files.

**Overview:**
- **`mv`**: Enhanced bash wrapper that intelligently routes to either `obsidian_mv` or system `mv`
- **`obsidian_mv`**: Python script that renames/moves markdown files and updates all references

#### How It Works

**The `mv` wrapper script analyzes each operation and decides which tool to use:**

**Uses `obsidian_mv` when BOTH conditions are met:**
1. **File is markdown** (ends with `.md`)
2. **File is in vault** (within `/path/to/your/obsidian/vault/` and not in hidden directories)

**Uses system `mv` for everything else:**
- Non-markdown files (`.txt`, `.pdf`, etc.)
- Files outside the vault
- Files in hidden directories (`.obsidian/`, `.git/`, etc.)

**When handling markdown files, `obsidian_mv`:**
1. **Finds all references** to the file being moved
2. **Updates wikilinks** like `[[old-name]]` → `[[new-name]]`
3. **Updates markdown links** like `[text](old-name.md)` → `[text](new-name.md)`
4. **Updates embeds** like `![[old-name]]` → `![[new-name]]`
5. **Handles complex links** with sections, aliases, and block references
6. **Renames the actual file** using Obsidian's Local REST API

#### Usage

Just use `mv` normally - the intelligence is automatic:

```bash
# Markdown files in vault → uses obsidian_mv with reference updates
mv "My Note.md" "Renamed Note.md"
mv test/document.md archive/document.md

# Non-markdown files → uses system mv
mv image.png renamed-image.png
mv data.csv backup/data.csv

# Files outside vault → uses system mv
mv /tmp/file.txt /tmp/renamed.txt

# Direct obsidian_mv usage for advanced options
obsidian_mv "old.md" "new.md" --dry-run        # Preview changes
obsidian_mv "old.md" "new.md" --json           # JSON output for automation
```

#### Configuration

Settings are stored in `utilities_data/obsidian_mv/settings.json`:

```json
{
  "vault_root": "/path/to/your/obsidian/vault/",
  "debug_mode": false
}
```

**Debug Mode:**
- `debug_mode: false` (default): Clean, minimal output
- `debug_mode: true`: Detailed debug information showing decision logic and reference updates

#### Safety Features

- **Hidden directory detection**: Skips Obsidian config (`.obsidian/`), git files (`.git/`), etc.
- **Reference validation**: Only updates actual references, not partial matches
- **API error handling**: Graceful fallback and error reporting
- **Dry run mode**: Preview changes before applying (`--dry-run` flag)

### obsidian_query - Vault Analysis

Query and analyze Obsidian vault content using the Local REST API's indexed search.

```bash
obsidian_query --stats                          # Show vault statistics
obsidian_query --property source=youtube       # Find notes with specific property
obsidian_query --tag programming               # Find notes with specific tag
obsidian_query --search "machine learning"     # Full-text search
obsidian_query --recent 10                     # Show 10 most recent notes
```

**Key Features:**
- Uses Obsidian's indexed search for fast results
- Multiple output formats (list, table, JSON)
- Searches frontmatter properties, tags, and content
- Statistical analysis of vault content

## Documentation

- **[obsidian-local-api.md](supporting_docs/obsidian-local-api.md)** - Obsidian Local REST API reference and setup guide

## Example Workflows

### Renaming a Note with References
```bash
# Rename a note and update all references automatically
mv "Meeting Notes 2024-01-15.md" "Weekly Team Meeting - Jan 15.md"
```

### Finding Content for Analysis
```bash
# Find all notes tagged with 'project' that mention 'deadline'
obsidian_query --tag project --search deadline --output table
```

### Safe File Reorganization
```bash
# Preview what would change when moving a file
obsidian_mv "research/ai-paper.md" "archive/research/ai-paper.md" --dry-run
```

## Integration with Claude Code

These utilities are specifically designed to work seamlessly with Claude Code and other CLI-based AI tools:

- **Safe automation**: All operations preserve Obsidian's internal link structure
- **Predictable behavior**: Consistent command-line interface following Unix conventions
- **Rich feedback**: JSON output modes for programmatic integration
- **Error handling**: Graceful failure modes with clear error messages

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Mike Wille