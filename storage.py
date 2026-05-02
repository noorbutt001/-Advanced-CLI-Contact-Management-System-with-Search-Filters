"""
storage.py
----------
Data Layer: Handles ALL file I/O operations.
This layer knows nothing about UI or business logic — it only reads/writes data.
"""

import json
import csv
import os
from config import DATA_FILE


def load_contacts() -> list:
    """Load contacts from the JSON file. Returns empty list if file missing/corrupt."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ [storage] Failed to load contacts: {e}")
        return []


def save_contacts(contacts: list) -> bool:
    """Persist contacts to the JSON file. Returns True on success."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4)
        return True
    except IOError as e:
        print(f"⚠️ [storage] Failed to save contacts: {e}")
        return False


def export_to_csv(contacts: list, filename: str) -> bool:
    """Export contact list to a CSV file."""
    if not contacts:
        return False
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(contacts[0].keys()))
            writer.writeheader()
            writer.writerows(contacts)
        return True
    except IOError as e:
        print(f"⚠️ [storage] Export failed: {e}")
        return False


def import_from_csv(filename: str) -> list:
    """Import contacts from a CSV file. Returns list of dicts."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except IOError as e:
        raise IOError(f"Import failed: {e}")