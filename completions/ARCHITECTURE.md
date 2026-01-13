# Shell Completion Architecture

This document explains how the shell completion system works for BigQuery utilities.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Terminal                            │
│  $ bq-profile my-proj<TAB>                                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Shell (bash/zsh)                             │
│  Triggers completion function based on command                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Completion Function (_bq_complete)                  │
│  1. Parse current word and context                              │
│  2. Determine what to complete (command, option, value)          │
│  3. Call appropriate completion helper                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐   ┌──────────────────────┐
│  Option Helper   │   │  Table ID Helper     │
│  - Format values │   │  - Check cache       │
│  - File paths    │   │  - Return matches    │
│  - Project IDs   │   │  - Refresh if stale  │
└──────────────────┘   └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  Cache System        │
                       │  ~/.cache/bq-*       │
                       │  TTL: 1 hour         │
                       └──────────┬───────────┘
                                  │
                       ┌──────────┴───────────┐
                       ▼                      ▼
              ┌────────────────┐    ┌────────────────┐
              │  bq command    │    │  jq processor  │
              │  List datasets │    │  Parse JSON    │
              │  List tables   │    │  Format IDs    │
              └────────────────┘    └────────────────┘
```

## Component Details

### 1. Shell RC Files (~/.bashrc or ~/.zshrc)

**Purpose**: Load completion functions at shell startup

**Bash**:
```bash
if [ -f "$HOME/.bash_completion.d/bq-utils" ]; then
    . "$HOME/.bash_completion.d/bq-utils"
fi
```

**Zsh**:
```bash
fpath=(~/.zsh/completion $fpath)
autoload -Uz compinit
compinit
```

### 2. Completion Scripts

#### bash_completion
- **Location**: `~/.bash_completion.d/bq-utils`
- **Size**: ~250 lines
- **Key Functions**:
  - `_bq_complete()`: Main completion entry point
  - `_complete_bq_table_id()`: Table ID completion
  - `_complete_format()`: Format option completion
  - `_get_bq_tables()`: Fetch tables from cache

#### zsh_completion
- **Location**: `~/.zsh/completion/_bq-utils`
- **Size**: ~450 lines
- **Key Functions**:
  - `_bq_utils()`: Main completion entry point
  - `_bq_tables()`: Table ID completion with descriptions
  - `_format_options()`: Format completion with descriptions
  - `_bq_refresh_cache()`: Background cache refresh

### 3. Cache System

#### Cache File
- **Location**: `~/.cache/bq-completion-cache`
- **Format**: Plain text, one table ID per line
- **TTL**: 3600 seconds (1 hour)
- **Size**: Varies (typically 1-10 KB for hundreds of tables)

#### Cache Refresh Process

```
Check cache age
    │
    ├─ Fresh? (< 1 hour old)
    │   └─> Use cached data
    │
    └─ Stale? (>= 1 hour old)
        └─> Trigger background refresh
            │
            ├─> Get project ID (env or gcloud)
            ├─> List datasets (bq ls)
            ├─> For each dataset:
            │   └─> List tables (bq ls)
            ├─> Format as project.dataset.table
            └─> Write to cache file
```

### 4. Completion Flow

#### Simple Option Completion

```
User types: bq-profile --<TAB>

Flow:
1. Shell calls _bq_complete with context
2. Detects "--" prefix (option)
3. Looks up options for "bq-profile"
4. Returns: --format= --sample-size= --detect-anomalies ...
5. Shell displays options
```

#### Format Value Completion

```
User types: bq-profile table --format=<TAB>

Flow:
1. Shell calls _bq_complete
2. Detects "--format=" with value needed
3. Looks up format options for "bq-profile"
4. Returns: text json markdown html
5. Shell displays format options
```

#### Table ID Completion (Fast Path - Cache Hit)

```
User types: bq-profile my-proj<TAB>

Flow:
1. Shell calls _bq_complete
2. Detects table ID context (non-option argument)
3. Calls _complete_bq_table_id
4. Checks cache file age
5. Cache is fresh (< 1 hour)
6. Reads cache file
7. Filters lines matching "my-proj"
8. Returns matching table IDs
9. Shell displays matches
```

#### Table ID Completion (Slow Path - Cache Miss)

```
User types: bq-profile my-proj<TAB>

Flow:
1. Shell calls _bq_complete
2. Cache doesn't exist or is stale
3. Returns empty results (for now)
4. Spawns background job to refresh cache:
   ├─> bq ls --project_id=PROJECT --format=json
   ├─> jq extracts dataset IDs
   ├─> For each dataset:
   │   ├─> bq ls --dataset_id=DATASET --format=json
   │   └─> jq formats as project.dataset.table
   └─> Writes to cache file
5. Next TAB press will use fresh cache
```

### 5. Command Registration

#### Bash

```bash
# For each utility, register the completion function
complete -F _bq_complete bq-profile
complete -F _bq_complete bq-explain
complete -F _bq_complete bq-lineage
# ... etc
```

#### Zsh

```zsh
# Single completion function handles all commands
#compdef bq-profile bq-explain bq-explore ...

# Function checks $service to determine which utility
_bq_utils() {
    local service="${words[1]:t}"
    case "$service" in
        bq-profile) ... ;;
        bq-explain) ... ;;
        # ... etc
    esac
}
```

## Performance Characteristics

### Completion Speed

| Operation | Cold (No Cache) | Warm (Cache Hit) | Notes |
|-----------|----------------|------------------|-------|
| Command completion | < 10ms | < 10ms | Fast, in-memory |
| Option completion | < 10ms | < 10ms | Fast, in-memory |
| Format completion | < 10ms | < 10ms | Fast, in-memory |
| Table ID (cached) | 10-50ms | 10-50ms | File I/O + filtering |
| Table ID (refresh) | 1-30s | N/A | API calls in background |

### Cache Refresh Performance

Depends on:
- Number of datasets in project
- Number of tables per dataset
- Network latency to BigQuery API
- BigQuery API rate limits

Typical times:
- Small project (1-5 datasets, 10-50 tables): 1-5 seconds
- Medium project (5-20 datasets, 50-500 tables): 5-15 seconds
- Large project (20+ datasets, 500+ tables): 15-60 seconds

### Memory Usage

- Minimal: Completion scripts are sourced, not constantly running
- Cache file: Typically < 100 KB even for large projects
- Background refresh: Temporary spike during cache population

## Data Flow Diagram

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Shell Completion    │
│  Engine (readline)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐     ┌─────────────────┐
│  Completion Script   │────▶│  Utility Meta   │
│  (bash/zsh)          │     │  (options, etc) │
└──────┬───────────────┘     └─────────────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  Cache File  │      │   API Calls  │
│  (fast)      │      │   (slow)     │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
            ┌──────────┐
            │ Results  │
            │ Filtered │
            └────┬─────┘
                 │
                 ▼
            ┌──────────┐
            │  Shell   │
            │ Display  │
            └──────────┘
```

## Error Handling

### Missing Prerequisites

```
bq command not found
    └─> Completion works for options
        └─> Table ID completion returns empty
            └─> No error shown to user

jq command not found
    └─> Cache refresh fails silently
        └─> Completion works for everything except table IDs

No GCP project configured
    └─> Cache refresh skipped
        └─> Completion works except table IDs
```

### Cache Corruption

```
Cache file corrupted/invalid
    └─> Read fails
        └─> Treats as cache miss
            └─> Triggers refresh
```

### API Errors

```
BigQuery API error (permissions, quota, etc.)
    └─> Background job fails
        └─> Cache not updated
            └─> Falls back to old cache or empty
```

## Extension Points

### Adding New Utility

1. Add to `_UTIL_OPTIONS` array (bash) or `_bq_utils` case (zsh)
2. Define available options
3. Define format options (if applicable)
4. Add to `complete` registration (bash) or `#compdef` (zsh)

### Adding New Option Type

1. Add to option string for utility
2. Add completion logic in option parsing section
3. Create helper function if needed (e.g., for custom values)

### Custom Cache Strategy

Modify:
- `_BQ_CACHE_FILE`: Change cache location
- `_BQ_CACHE_TTL`: Change refresh interval
- `_get_bq_tables()`: Change cache population logic

## Security Considerations

### Cache Safety
- Cache file is in user's home directory
- Standard file permissions (644)
- Contains only public table identifiers
- No credentials stored

### Command Injection
- All user input is properly quoted
- No eval of user input
- API calls are through `bq` command (not direct network access)

### Information Disclosure
- Cache reveals table structure of accessible projects
- Only shows tables user already has access to
- No data values, only metadata

## Debugging

### Enable Debug Mode

**Bash**:
```bash
set -x  # Enable command tracing
bq-profile --<TAB>
set +x  # Disable
```

**Zsh**:
```zsh
setopt xtrace  # Enable tracing
bq-profile --<TAB>
unsetopt xtrace  # Disable
```

### Check What's Loaded

**Bash**:
```bash
# Check if function exists
type _bq_complete

# Check if completion is registered
complete -p bq-profile

# Check variables
declare -p _UTIL_OPTIONS
```

**Zsh**:
```zsh
# Check if function exists
which _bq_utils

# Check fpath
echo $fpath

# Check completion cache
rm -f ~/.zcompdump && compinit
```

### Manual Cache Testing

```bash
# View cache
cat ~/.cache/bq-completion-cache

# Check cache age
stat -f %m ~/.cache/bq-completion-cache  # macOS
stat -c %Y ~/.cache/bq-completion-cache  # Linux

# Force refresh
rm ~/.cache/bq-completion-cache
bq-profile <TAB>

# Populate manually
project=$(gcloud config get-value project)
bq ls --project_id="$project" --format=json | \
  jq -r '.[].id' | \
  while read ds; do
    bq ls --project_id="$project" --dataset_id="$ds" --format=json | \
      jq -r --arg p "$project" --arg d "$ds" \
        '.[] | "\($p).\($d).\(.id)"'
  done > ~/.cache/bq-completion-cache
```

## Future Enhancements

### Potential Improvements

1. **Fuzzy Matching**: Match table IDs with typos or partial matches
2. **Contextual Help**: Show inline documentation for options
3. **Smart Defaults**: Remember frequently used tables/options
4. **Multi-level Cache**: Cache datasets separately from tables
5. **Async Refresh**: Use inotify/fswatch for smarter cache updates
6. **Compression**: Compress large cache files
7. **Partial Results**: Show cached results while refreshing
8. **Custom Completers**: Plugin system for custom completion logic

### Integration Opportunities

- **IDE Integration**: Export completion metadata for IDE autocomplete
- **Documentation**: Auto-generate docs from completion definitions
- **Testing**: Validate utilities match completion definitions
- **Metrics**: Track completion usage patterns
