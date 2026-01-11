#!/usr/bin/env python3
"""
Config Secrets Scanner

A CLI tool to recursively scan directories for hardcoded secrets.
Uses regex patterns to detect AWS keys, private keys, API tokens, and more.
"""

import re
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SecretMatch:
    """Represents a detected secret match."""
    file_path: Path
    line_number: int
    secret_type: str
    risk_level: RiskLevel
    snippet: str
    line_content: str


# Patterns configuration: (pattern, secret_type, risk_level)
PATTERNS: List[Tuple[re.Pattern, str, RiskLevel]] = [
    # HIGH RISK Patterns
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS Access Key ID', RiskLevel.HIGH),
    (re.compile(r'aws_secret_access_key\s*[=:]\s*["\']?([A-Za-z0-9/+=]{40})["\']?', re.IGNORECASE), 'AWS Secret Access Key', RiskLevel.HIGH),
    (re.compile(r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE KEY-----', re.MULTILINE), 'Private Key', RiskLevel.HIGH),
    (re.compile(r'(postgres|mysql|mongodb)://[^:\s]+:[^@\s]+@[^\s]+', re.IGNORECASE), 'Database URL with Password', RiskLevel.HIGH),
    
    # MEDIUM RISK Patterns
    (re.compile(r'(api[_-]?key|access[_-]?token|bearer)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?', re.IGNORECASE), 'API Token', RiskLevel.MEDIUM),
    (re.compile(r'ghp_[A-Za-z0-9]{36}'), 'GitHub Personal Access Token', RiskLevel.MEDIUM),
    (re.compile(r'https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]+'), 'Slack Webhook URL', RiskLevel.MEDIUM),
    (re.compile(r'sk_live_[A-Za-z0-9]{24,}'), 'Stripe Live Key', RiskLevel.MEDIUM),
    (re.compile(r'xox[baprs]-[0-9a-zA-Z-]{10,}'), 'Slack Token', RiskLevel.MEDIUM),
    
    # LOW RISK Patterns
    (re.compile(r'password\s*[=:]\s*["\']([^"\']+)["\']', re.IGNORECASE), 'Password Variable', RiskLevel.LOW),
    (re.compile(r'secret\s*[=:]\s*["\']([^"\']+)["\']', re.IGNORECASE), 'Secret Variable', RiskLevel.LOW),
    (re.compile(r'apikey\s*[=:]\s*["\']([^"\']+)["\']', re.IGNORECASE), 'API Key Variable', RiskLevel.LOW),
]


# Directories to ignore
IGNORED_DIRS = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'node_modules', '.pytest_cache', '.mypy_cache'}

# File extensions to ignore (binary files)
IGNORED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.pyc', '.pyo', '.pdf', 
                     '.zip', '.tar', '.gz', '.exe', '.dll', '.so', '.dylib', '.woff', '.woff2', '.ttf', '.eot'}

console = Console()


def should_ignore_path(path: Path) -> bool:
    """Check if a path should be ignored."""
    # Check if any parent directory is in ignored list
    for part in path.parts:
        if part in IGNORED_DIRS:
            return True
    
    # Check file extension
    if path.is_file() and path.suffix.lower() in IGNORED_EXTENSIONS:
        return True
    
    return False


def mask_secret(snippet: str, secret_type: str) -> str:
    """Mask sensitive parts of the secret for display."""
    if len(snippet) <= 8:
        return '*' * len(snippet)
    
    # For AWS keys, show first 4 and mask the rest
    if 'AWS' in secret_type and snippet.startswith('AKIA'):
        return snippet[:4] + '*' * min(8, len(snippet) - 4)
    
    # For tokens, show first 4-6 chars and mask
    if len(snippet) > 20:
        return snippet[:4] + '*' * 8 + snippet[-4:]
    else:
        return snippet[:4] + '*' * (len(snippet) - 4)


def scan_file(file_path: Path) -> List[SecretMatch]:
    """
    Scan a single file for secrets line by line.
    Returns a list of SecretMatch objects.
    """
    matches = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                for pattern, secret_type, risk_level in PATTERNS:
                    pattern_matches = pattern.finditer(line)
                    for match in pattern_matches:
                        snippet = match.group(0)
                        # Try to extract captured group if available (prefer captured group over full match)
                        if match.groups() and match.group(1):
                            snippet = match.group(1)
                        
                        matches.append(SecretMatch(
                            file_path=file_path,
                            line_number=line_num,
                            secret_type=secret_type,
                            risk_level=risk_level,
                            snippet=snippet,
                            line_content=line.rstrip()
                        ))
    except (PermissionError, UnicodeDecodeError) as e:
        console.print(f"[yellow]Warning:[/yellow] Skipped {file_path}: {type(e).__name__}")
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Unexpected error scanning {file_path}: {type(e).__name__}")
    
    return matches


def scan_directory(root_dir: Path) -> List[SecretMatch]:
    """
    Recursively scan a directory for secrets.
    Returns a list of all SecretMatch objects found.
    """
    all_matches = []
    
    # Get all files to scan (for progress tracking)
    files_to_scan = []
    for path in root_dir.rglob('*'):
        if path.is_file() and not should_ignore_path(path):
            files_to_scan.append(path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Scanning files...", total=len(files_to_scan))
        
        for file_path in files_to_scan:
            matches = scan_file(file_path)
            all_matches.extend(matches)
            progress.update(task, advance=1)
    
    return all_matches


def create_results_table(matches: List[SecretMatch], root_dir: Path) -> Table:
    """Create a rich Table with scan results."""
    table = Table(title="🔍 Secret Scan Results", show_header=True, header_style="bold magenta")
    table.add_column("File Path", style="cyan", no_wrap=False)
    table.add_column("Line", justify="right", style="blue")
    table.add_column("Secret Type", style="green")
    table.add_column("Risk Level", justify="center")
    table.add_column("Snippet", style="dim")
    
    # Sort matches by risk level (HIGH first) and then by file path
    risk_order = {RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 2}
    sorted_matches = sorted(matches, key=lambda m: (risk_order[m.risk_level], str(m.file_path), m.line_number))
    
    for match in sorted_matches:
        # Get relative path
        try:
            rel_path = match.file_path.relative_to(root_dir)
        except ValueError:
            rel_path = match.file_path
        
        # Color code risk level
        risk_color = {
            RiskLevel.HIGH: "[bold red]",
            RiskLevel.MEDIUM: "[bold yellow]",
            RiskLevel.LOW: "[bold blue]"
        }[match.risk_level]
        
        masked_snippet = mask_secret(match.snippet, match.secret_type)
        
        table.add_row(
            str(rel_path),
            str(match.line_number),
            match.secret_type,
            f"{risk_color}{match.risk_level.value}[/]",
            masked_snippet
        )
    
    return table


def print_summary(matches: List[SecretMatch]):
    """Print a summary of the scan results."""
    high_count = sum(1 for m in matches if m.risk_level == RiskLevel.HIGH)
    medium_count = sum(1 for m in matches if m.risk_level == RiskLevel.MEDIUM)
    low_count = sum(1 for m in matches if m.risk_level == RiskLevel.LOW)
    
    summary_text = f"""
[bold]Total Secrets Found:[/bold] {len(matches)}

[bold red]HIGH Risk:[/bold red]   {high_count}
[bold yellow]MEDIUM Risk:[/bold yellow] {medium_count}
[bold blue]LOW Risk:[/bold blue]    {low_count}
"""
    
    console.print(Panel(summary_text, title="📊 Summary", border_style="blue"))


def main():
    """Main entry point for the CLI tool."""
    console.print("[bold green]Config Secrets Scanner[/bold green]\n")
    
    # Get current working directory
    root_dir = Path.cwd()
    console.print(f"[dim]Scanning directory:[/dim] {root_dir}\n")
    
    # Scan directory
    matches = scan_directory(root_dir)
    
    # Display results
    console.print("\n")
    
    if matches:
        print_summary(matches)
        console.print("\n")
        table = create_results_table(matches, root_dir)
        console.print(table)
        console.print("\n[bold red]⚠️  Secrets detected! Please review and remove them immediately.[/bold red]\n")
    else:
        console.print("[bold green]✓ No secrets detected![/bold green]\n")


if __name__ == "__main__":
    main()
