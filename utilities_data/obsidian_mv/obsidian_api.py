#!/usr/bin/env python3
"""
Shared API module for Obsidian Local REST API operations.
Provides a unified interface for all Obsidian vault operations.
"""

import requests
import json
import re
from pathlib import Path
from urllib.parse import quote
from typing import List, Dict, Tuple, Optional

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ObsidianAPI:
    """
    Unified API client for Obsidian Local REST API operations.
    Handles authentication, HTTP requests, and common vault operations.
    """

    def __init__(self, api_base_url: str = "https://127.0.0.1:27124", api_key_file: str = ".env"):
        """
        Initialize the API client.

        Args:
            api_base_url: Base URL for the Obsidian REST API
            api_key_file: Path to file containing API key
        """
        self.api_base_url = api_base_url
        self.api_key_file = api_key_file
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        """Load API key from environment file."""
        try:
            # Navigate from utilities_data/obsidian_mv/ back to vault root
            # Path: utilities_data/obsidian_mv/ -> utilities_data/ -> utilities/ -> system/ -> life/ -> vault/
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / self.api_key_file
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('OBSIDIAN_API_KEY'):
                        return line.split('=')[1].strip().strip('"')
            raise ValueError("OBSIDIAN_API_KEY not found in .env file")
        except FileNotFoundError:
            raise FileNotFoundError(f"{self.api_key_file} file not found")

    def get_file_content(self, filepath: str) -> Optional[str]:
        """
        Get the content of a file via REST API.

        Args:
            filepath: Path to the file relative to vault root

        Returns:
            File content as string, or None if file not found or error
        """
        encoded_path = quote(filepath, safe='/')

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/vnd.olrapi.note+json'
        }

        try:
            response = requests.get(
                f"{self.api_base_url}/vault/{encoded_path}",
                headers=headers,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('content', '')
            else:
                return None

        except requests.exceptions.RequestException:
            return None

    def update_file_content(self, filepath: str, content: str) -> bool:
        """
        Update the content of a file via REST API using PUT.

        Args:
            filepath: Path to the file relative to vault root
            content: New content for the file

        Returns:
            True if successful, False otherwise
        """
        encoded_path = quote(filepath, safe='/')

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'text/markdown'
        }

        try:
            response = requests.put(
                f"{self.api_base_url}/vault/{encoded_path}",
                headers=headers,
                data=content.encode('utf-8'),
                verify=False,
                timeout=10
            )

            return response.status_code in [200, 204]

        except requests.exceptions.RequestException:
            return False

    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file via REST API.

        Args:
            filepath: Path to the file relative to vault root

        Returns:
            True if successful, False otherwise
        """
        encoded_path = quote(filepath, safe='/')

        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        try:
            response = requests.delete(
                f"{self.api_base_url}/vault/{encoded_path}",
                headers=headers,
                verify=False,
                timeout=10
            )

            return response.status_code in [200, 204]

        except requests.exceptions.RequestException:
            return False

    def find_references(self, filename: str) -> List[Dict[str, str]]:
        """
        Find all files that reference the given filename using Dataview queries.

        Args:
            filename: Name of the file to search references for

        Returns:
            List of dictionaries with 'filename' keys for files that reference the target
        """
        # Remove .md extension if present for the search
        search_name = filename.replace('.md', '') if filename.endswith('.md') else filename

        # Prepare the Dataview query
        query = f"TABLE file.path, file.inlinks FROM [[{search_name}]]"

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/vnd.olrapi.dataview.dql+txt'
        }

        try:
            response = requests.post(
                f"{self.api_base_url}/search/",
                headers=headers,
                data=query,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except requests.exceptions.RequestException:
            return []

    def extract_link_references(self, content: str, target_note: str) -> List[str]:
        """
        Extract all [[...]] and ![[...]] references that point to the target note from content.
        Handles all Obsidian link patterns including embeds, headings, and blocks.

        Args:
            content: File content to search
            target_note: Name of the note being referenced

        Returns:
            List of complete link strings that reference the target note
        """
        # Remove .md extension from target if present
        target_base = target_note.replace('.md', '') if target_note.endswith('.md') else target_note

        # Find all [[...]] and ![[...]] links in the content
        # Pattern captures: (optional !, complete match, inner content)
        link_pattern = r'(!?\[\[([^\]]+)\]\])'
        matches = []

        for match in re.finditer(link_pattern, content):
            full_match = match.group(1)  # The complete ![[...]] or [[...]]
            link_inner = match.group(2)  # The text inside [[...]]

            # Skip search helpers (they don't reference specific notes)
            if link_inner.startswith('## ') or link_inner.startswith('^^ '):
                continue

            # Skip internal anchors (references within the same file)
            if link_inner.startswith('#'):
                continue

            # Split link text and alias if present (e.g., [[link|alias]])
            link_parts = link_inner.split('|')
            link_target = link_parts[0].strip()

            # Separate note name from anchor/heading/block references
            # Handle patterns like: "Note name#Heading", "Note name#^block-id"
            if '#' in link_target:
                note_part = link_target.split('#')[0].strip()
            else:
                note_part = link_target

            # Check if this link references our target
            # It could be:
            # - Exact match: [[popular note]] or [[popular note#Heading]]
            # - With path: [[test/popular note]] or [[test/popular note#Heading]]
            # - With leading slash: [[/test/popular note]]
            # - With .md extension: [[popular note.md]]

            # Normalize both for comparison
            link_base = note_part.replace('.md', '') if note_part.endswith('.md') else note_part
            link_base = link_base.lstrip('/')  # Remove leading slash

            # Check if this references our target
            if (link_base == target_base or
                link_base.endswith('/' + target_base) or
                target_base.endswith('/' + link_base)):
                matches.append(full_match)

        return matches

    def extract_link_references_from_file(self, filepath: str, target_note: str) -> List[str]:
        """
        Extract link references from a specific file.

        Args:
            filepath: Path to the file to analyze
            target_note: Name of the note being referenced

        Returns:
            List of complete [[...]] link strings that reference the target note
        """
        content = self.get_file_content(filepath)
        if content is None:
            return []

        return self.extract_link_references(content, target_note)

    def rename_file(self, old_path: str, new_path: str) -> bool:
        """
        Rename/move a file by copying content and deleting original.

        Args:
            old_path: Current file path
            new_path: New file path

        Returns:
            True if successful, False otherwise
        """
        # Get the content of the old file
        content = self.get_file_content(old_path)
        if content is None:
            return False

        # Create the new file with the content
        if not self.update_file_content(new_path, content):
            return False

        # Delete the old file
        if not self.delete_file(old_path):
            # If we can't delete the old file, try to clean up by deleting the new one
            self.delete_file(new_path)
            return False

        return True

    def generate_link_replacement(self, link_text: str, old_name: str, new_name: str) -> str:
        """
        Generate replacement text for a link, preserving aliases, anchors, and embed prefixes.
        Handles all Obsidian link patterns including embeds, headings, and blocks.

        Args:
            link_text: The original link text (including [[ ]] and optional !)
            old_name: Old note name
            new_name: New note name

        Returns:
            Updated link text with new name
        """
        # Remove .md extensions for comparison
        old_base = old_name.replace('.md', '') if old_name.endswith('.md') else old_name
        new_base = new_name.replace('.md', '') if new_name.endswith('.md') else new_name

        # Get just the filename part without path for comparison
        old_filename = old_base.split('/')[-1]
        new_filename = new_base.split('/')[-1]

        # Check if this is an embed link (starts with !)
        is_embed = link_text.startswith('!')
        embed_prefix = '!' if is_embed else ''

        # Remove the embed prefix and [[ ]] from the link text
        if is_embed:
            link_inner = link_text[3:-2]  # Remove ![[...]]
        else:
            link_inner = link_text[2:-2]  # Remove [[...]]

        # Split on pipe to handle aliases
        parts = link_inner.split('|')
        link_target = parts[0].strip()
        alias = parts[1].strip() if len(parts) > 1 else None

        # Separate note name from anchor/heading/block references
        anchor = ''
        if '#' in link_target:
            note_and_anchor = link_target.split('#', 1)  # Split only on first #
            note_target = note_and_anchor[0].strip()
            anchor = '#' + note_and_anchor[1]  # Preserve the # and everything after
        else:
            note_target = link_target

        # Handle different path formats for the note part only
        new_target = note_target

        # Direct match with full path
        if note_target == old_base or note_target == old_name:
            new_target = new_base
        # With .md extension
        elif note_target == f"{old_base}.md":
            new_target = f"{new_base}.md"
        # Just the filename (most common case)
        elif note_target == old_filename:
            new_target = new_filename
        elif note_target == f"{old_filename}.md":
            new_target = f"{new_filename}.md"
        # Absolute path
        elif note_target.startswith('/'):
            if note_target == f"/{old_base}" or note_target == f"/{old_name}":
                new_target = f"/{new_base}"
            elif note_target == f"/{old_base}.md":
                new_target = f"/{new_base}.md"
        # Relative path - replace the last component
        elif '/' in note_target:
            path_parts = note_target.split('/')
            last_part = path_parts[-1]
            if last_part == old_filename or last_part == f"{old_filename}.md":
                path_parts[-1] = new_filename if last_part == old_filename else f"{new_filename}.md"
                new_target = '/'.join(path_parts)

        # Reconstruct the full link with embed prefix, new target, anchor, and alias
        full_target = new_target + anchor

        if alias:
            return f"{embed_prefix}[[{full_target}|{alias}]]"
        else:
            return f"{embed_prefix}[[{full_target}]]"