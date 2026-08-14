import asyncio
import json
import sys

from wredis_mcp.catalog import PatternsCatalog
from wredis_mcp.templates import TemplateGenerator


def demo_catalog_search():
    """Demonstrates the pattern catalog search capability."""
    catalog = PatternsCatalog()
    print("=== Search 'queue' ===")
    for p in catalog.search("queue"):
        print(f"  - {p['name']} ({p['manager']}): {p['description']}")

    print("\n=== Search 'cache' ===")
    for p in catalog.search("cache"):
        print(f"  - {p['name']} ({p['manager']}): {p['description']}")


def demo_scaffolding(target_dir: str):
    """Demonstrates the scaffolding generator."""
    for folder in TemplateGenerator.get_folders("standard"):
        print(f"  Creating folder: {folder}")
    blueprints = TemplateGenerator.get_files_blueprint("standard", "demo_service")
    for rel_path, _content in blueprints.items():
        print(f"  Generating file: {rel_path}")


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print("Running wredis-mcp examples (offline demo, no Redis required)...\n")
    demo_catalog_search()
    print("\n=== Scaffolding preview ===")
    demo_scaffolding(target)


if __name__ == "__main__":
    main()
