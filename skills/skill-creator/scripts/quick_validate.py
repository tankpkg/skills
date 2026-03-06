#!/usr/bin/env python3
"""
Quick validation script for Tank skills.

Validates SKILL.md frontmatter, naming conventions, and structural requirements.
Run before packaging or deploying a skill.

Inspired by anthropics/skills validation approach.

Usage:
    python quick_validate.py <skill_directory>

Example:
    python quick_validate.py skills/my-skill
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, "No YAML frontmatter found (file must start with ---)"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format (missing closing ---)"

    frontmatter_text = match.group(1)

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return None, "Frontmatter must be a YAML dictionary"
            return frontmatter, ""
        except yaml.YAMLError as e:
            return None, f"Invalid YAML in frontmatter: {e}"

    # Fallback: basic parsing without PyYAML
    frontmatter = {}
    current_key = None
    current_value_lines = []

    for line in frontmatter_text.split("\n"):
        key_match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", line)
        if key_match and not line.startswith(" "):
            if current_key:
                frontmatter[current_key] = "\n".join(current_value_lines).strip()
            current_key = key_match.group(1)
            current_value_lines = [key_match.group(2)]
        elif current_key:
            current_value_lines.append(line)

    if current_key:
        frontmatter[current_key] = "\n".join(current_value_lines).strip()

    return frontmatter, ""


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """
    Validate a skill directory.

    Returns (is_valid, list_of_messages).
    Messages are either errors (prefixed with ✗) or warnings (prefixed with ⚠).
    """
    skill_path = Path(skill_path)
    messages = []
    errors = 0

    def error(msg: str):
        nonlocal errors
        errors += 1
        messages.append(f"  ✗ {msg}")

    def warn(msg: str):
        messages.append(f"  ⚠ {msg}")

    def ok(msg: str):
        messages.append(f"  ✓ {msg}")

    # --- Check directory exists ---
    if not skill_path.exists():
        return False, [f"  ✗ Skill directory not found: {skill_path}"]

    if not skill_path.is_dir():
        return False, [f"  ✗ Path is not a directory: {skill_path}"]

    # --- Check SKILL.md exists ---
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, [f"  ✗ SKILL.md not found in {skill_path}"]

    content = skill_md.read_text()
    ok("SKILL.md found")

    # --- Parse frontmatter ---
    frontmatter, parse_error = parse_frontmatter(content)
    if frontmatter is None:
        error(parse_error)
        return False, messages

    ok("Frontmatter parsed")

    # --- Check allowed keys ---
    ALLOWED_KEYS = {
        "name",
        "description",
        "license",
        "allowed-tools",
        "metadata",
        "compatibility",
    }
    unexpected = set(frontmatter.keys()) - ALLOWED_KEYS
    if unexpected:
        error(
            f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_KEYS))}"
        )

    # --- Validate name ---
    name = frontmatter.get("name")
    if not name:
        error("Missing 'name' in frontmatter")
    elif not isinstance(name, str):
        error(f"Name must be a string, got {type(name).__name__}")
    else:
        name = name.strip()

        if not re.match(r"^(@[a-z0-9-]+/)?[a-z0-9-]+$", name):
            error(f"Name '{name}' must be kebab-case, optionally scoped (@scope/name)")
        elif name.startswith("-") or name.endswith("-") or "--" in name:
            error(
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
            )

        if len(name) > 64:
            error(f"Name too long ({len(name)} chars, max 64)")
        else:
            ok(f"Name '{name}' valid")

    # --- Validate description ---
    description = frontmatter.get("description")
    if not description:
        error("Missing 'description' in frontmatter")
    elif not isinstance(description, str):
        error(f"Description must be a string, got {type(description).__name__}")
    else:
        description = description.strip()

        if "<" in description or ">" in description:
            error("Description cannot contain angle brackets (< or >)")

        if len(description) > 1024:
            error(f"Description too long ({len(description)} chars, max 1024)")
        elif len(description) < 50:
            warn(
                f"Description very short ({len(description)} chars). Add trigger phrases for better activation."
            )
        else:
            ok(f"Description length OK ({len(description)} chars)")

        # Check for trigger phrases
        trigger_keywords = ["trigger", "Trigger", "when", "use this", "Use this"]
        has_triggers = any(kw in description for kw in trigger_keywords)
        if not has_triggers:
            warn(
                "Description may lack trigger phrases. Include 'Trigger phrases:' for better skill activation."
            )

    # --- Validate compatibility (optional) ---
    compatibility = frontmatter.get("compatibility")
    if compatibility:
        if not isinstance(compatibility, str):
            error(f"Compatibility must be a string, got {type(compatibility).__name__}")
        elif len(compatibility) > 500:
            error(f"Compatibility too long ({len(compatibility)} chars, max 500)")

    # --- Check SKILL.md body length ---
    body_match = re.search(r"^---\n.*?\n---\n(.*)", content, re.DOTALL)
    if body_match:
        body = body_match.group(1)
        body_lines = body.strip().split("\n")
        line_count = len(body_lines)

        if line_count > 500:
            error(
                f"SKILL.md body is {line_count} lines (max 500 per spec, 200 recommended)"
            )
        elif line_count > 200:
            warn(f"SKILL.md body is {line_count} lines (recommended: under 200)")
        else:
            ok(f"SKILL.md body length OK ({line_count} lines)")

    # --- Check skills.json exists ---
    skills_json = skill_path / "skills.json"
    if skills_json.exists():
        ok("skills.json found")
    else:
        warn("No skills.json found (recommended for permissions)")

    # --- Check reference file lengths ---
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.glob("*.md")):
            ref_lines = len(ref_file.read_text().strip().split("\n"))
            if ref_lines > 450:
                warn(
                    f"Reference {ref_file.name} is {ref_lines} lines (recommended: 250-450)"
                )
            elif ref_lines < 100:
                warn(
                    f"Reference {ref_file.name} is {ref_lines} lines (may be too thin)"
                )
            else:
                ok(f"Reference {ref_file.name} length OK ({ref_lines} lines)")

    # --- Check for forbidden files ---
    forbidden = [
        "README.md",
        "INSTALLATION_GUIDE.md",
        "QUICK_REFERENCE.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
    ]
    for name in forbidden:
        if (skill_path / name).exists():
            warn(f"Found {name} — skills are for AI, not humans. Consider removing.")

    # --- Summary ---
    if errors == 0:
        messages.insert(0, "✓ Skill is valid!")
        return True, messages
    else:
        messages.insert(0, f"✗ Found {errors} error(s)")
        return False, messages


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_directory>")
        print("\nExample:")
        print("  python quick_validate.py skills/my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]
    print(f"Validating: {skill_path}\n")

    valid, messages = validate_skill(skill_path)
    for msg in messages:
        print(msg)

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
