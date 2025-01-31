import functools
import re
from pathlib import Path

def validate_class_names():
    def decorator(cls):
        glossary_path = Path('docs/GLOSSARY.md')
        if not glossary_path.exists():
            raise FileNotFoundError("GLOSSARY.md not found")

        with open(glossary_path, 'r', encoding='utf-8') as f:
            glossary_content = f.read().lower()

        if cls.__name__.lower() not in glossary_content:
            raise ValueError(f"Class {cls.__name__} is not defined in GLOSSARY.md")

        return cls
    return decorator