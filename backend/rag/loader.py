from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".css",
    ".html",
}


IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "__pycache__",
    "venv",
}


IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",
    ".json": "JSON",
    ".md": "Markdown",
    ".css": "CSS",
    ".html": "HTML",
}


def load_codebase(project_path: str):
    project = Path(project_path)
    documents = []

    for file_path in project.rglob("*"):
        if not file_path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in file_path.parts):
            continue

        if file_path.name in IGNORED_FILES:
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            documents.append({
                "path": str(file_path.relative_to(project)),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "language": LANGUAGE_MAP.get(
                    file_path.suffix.lower(),
                    "Unknown",
                ),
                "content": content,
            })

        except Exception as e:
            print(f"Could not read {file_path}: {e}")

    return documents