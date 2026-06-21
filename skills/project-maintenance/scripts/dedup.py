#!/usr/bin/env python3
"""
Semantic deduplication for Claude Code memory files.

Computes similarity between markdown files using keyword overlap (Jaccard similarity).
Outputs duplicate groups to stdout as JSON.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def extract_keywords(text: str, min_len: int = 3) -> set[str]:
    """Extract keywords from text using simple tokenization."""
    import re
    # Strip markdown, get alphanumeric tokens
    tokens = re.findall(r'\b\w+\b', text.lower())
    # Filter short words and common stopwords
    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
        'can', 'has', 'her', 'was', 'one', 'our', 'out', 'has',
        'this', 'that', 'with', 'from', 'they', 'will', 'would',
        'there', 'their', 'what', 'about', 'which', 'when', 'make',
        'just', 'over', 'such', 'into', 'than', 'them', 'could',
        'then', 'some', 'also', 'more', 'been', 'call', 'two',
        'how', 'its', 'may', 'see', 'now', 'way', 'get', 'use',
    }
    return {
        t for t in tokens
        if len(t) >= min_len and t not in stopwords
    }


def jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def read_file(path: Path) -> tuple[str, str]:
    """Read file content. Returns (content, error)."""
    try:
        return path.read_text(encoding='utf-8'), ''
    except (IOError, UnicodeDecodeError) as e:
        return '', str(e)


def find_duplicates(directory: str, threshold: float = 0.7) -> dict[str, Any]:
    """Find duplicate files in directory based on keyword similarity."""
    dir_path = Path(directory).expanduser()
    if not dir_path.is_dir():
        return {'error': f'Not a directory: {directory}', 'duplicates': []}

    # Collect all markdown files
    files = {}
    for md_file in dir_path.rglob('*.md'):
        content, err = read_file(md_file)
        if err:
            continue
        files[str(md_file)] = content

    if len(files) < 2:
        return {'duplicates': [], 'stats': {'total_files': len(files), 'duplicate_groups': 0}}

    # Compute keywords for each file
    keywords: dict[str, set[str]] = {}
    for path, content in files.items():
        keywords[path] = extract_keywords(content)

    # Find duplicate groups
    duplicates: list[dict] = []
    checked: set[tuple[str, str]] = set()

    for path1, kw1 in keywords.items():
        for path2, kw2 in keywords.items():
            if path1 >= path2:
                continue
            pair = (path1, path2)
            if pair in checked:
                continue
            checked.add(pair)

            similarity = jaccard_similarity(kw1, kw2)
            if similarity >= threshold:
                # Determine which to keep (newer file)
                mtime1 = os.path.getmtime(path1)
                mtime2 = os.path.getmtime(path2)
                keep = path2 if mtime2 > mtime1 else path1

                duplicates.append({
                    'files': [path1, path2],
                    'similarity': round(similarity, 2),
                    'recommendation': 'keep_newest',
                    'keep': keep,
                    'keep_mtime': max(mtime1, mtime2)
                })

    return {
        'duplicates': duplicates,
        'stats': {
            'total_files': len(files),
            'duplicate_groups': len(duplicates)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Find semantically duplicate markdown files'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=0.7,
        help='Similarity threshold 0-1 (default: 0.7)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )
    args = parser.parse_args()

    result = find_duplicates(args.directory, args.threshold)

    if args.format == 'text':
        if result.get('error'):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Total files: {result['stats']['total_files']}")
        print(f"Duplicate groups: {result['stats']['duplicate_groups']}")
        for group in result['duplicates']:
            print(f"\nSimilarity: {group['similarity']:.0%}")
            for f in group['files']:
                print(f"  - {f}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()