#!/usr/bin/env python3
"""
This script generates Sphinx documentation pages for device READMEs.

It scans the src/ac_training_lab directory recursively for README.md files,
but excludes any directories with "dummy_pkg" in their name, and creates
corresponding stub files in the docs/devices directory that include these
README files via the MyST Markdown include directive.
"""

import os
from pathlib import Path

# Base directories
SRC_DIR = Path("src/ac_training_lab")
DOCS_DEVICES_DIR = Path("docs/devices")

# GitHub repository URL for source links
GITHUB_REPO = "https://github.com/AccelerationConsortium/ac-training-lab"
GITHUB_BRANCH = "main"  # or master, depending on your repository

# Ensure the devices directory exists
DOCS_DEVICES_DIR.mkdir(exist_ok=True)

# Create an index for the devices
device_index_content = """# Devices

This section contains documentation for all devices in the AC Training Lab.
Each page is generated from the README.md file in the corresponding device's
source directory.

```{toctree}
:maxdepth: 1

"""

# Track the device documents we generate
generated_docs = []

# Find all README.md files in the src directory recursively, but exclude
# directories with dummy_pkg in their name
for root, dirs, files in os.walk(SRC_DIR):
    # Skip directories that have "dummy_pkg" in their name or start with _ or .
    dirs[:] = [d for d in dirs if "dummy_pkg" not in d and not d.startswith(("_", "."))]

    root_path = Path(root)

    # Check if there's a README.md file in this directory
    if "README.md" in files:
        # Get the relative path from src/ac_training_lab
        rel_path = root_path.relative_to(SRC_DIR)

        # Generate a sensible device name
        device_name = str(rel_path).replace(os.path.sep, "-")
        if device_name == ".":  # Root directory
            device_name = "ac-training-lab"

        # Generate stub filename (convert to snake case for file naming)
        stub_filename = f"{device_name}.md"

        # Create relative path to the README from docs/devices
        rel_readme_path = os.path.join(
            "..", "..", str(SRC_DIR), str(rel_path), "README.md"
        )
        rel_readme_path = rel_readme_path.replace(
            "\\", "/"
        )  # Ensure forward slashes for Sphinx

        # Create GitHub link to the source code
        github_path = (
            f"{GITHUB_REPO}/tree/{GITHUB_BRANCH}/src/ac_training_lab/{rel_path}"
        )
        if str(rel_path) == ".":
            github_path = f"{GITHUB_REPO}/tree/{GITHUB_BRANCH}/src/ac_training_lab"

        # Create GitHub edit link to the source README
        github_edit_path = f"{GITHUB_REPO}/edit/{GITHUB_BRANCH}/src/ac_training_lab"
        if str(rel_path) != ".":
            github_edit_path += f"/{rel_path}"
        github_edit_path += "/README.md"

        # Create stub content with source code link and edit page metadata
        stub_content = f"""---
edit_page: {github_edit_path}
---

```{{admonition}} Source Code
:class: note

<a href="{github_path}" target="_blank">View source code for this device on GitHub</a> | <a href="{github_edit_path}" target="_blank">Suggest edit</a>
```

```{{include}} {rel_readme_path}
```
"""

        # Write the stub file
        stub_path = DOCS_DEVICES_DIR / stub_filename
        with open(stub_path, "w", encoding="utf-8") as f:
            f.write(stub_content)

        # Add to generated docs list
        generated_docs.append((device_name, stub_filename))
        print(f"Generated device documentation stub for {device_name}")

# Sort the generated docs by device name for the index
generated_docs.sort()

# Complete the device index file
for device_name, stub_filename in generated_docs:
    # Remove .md extension for toctree
    stub_name = os.path.splitext(stub_filename)[0]
    device_index_content += f"{stub_name}\n"

device_index_content += "```\n"

# Write the device index file
with open(DOCS_DEVICES_DIR / "index.md", "w", encoding="utf-8") as f:
    f.write(device_index_content)

print(f"Generated device index with {len(generated_docs)} devices")
print("Device documentation generation complete.")
