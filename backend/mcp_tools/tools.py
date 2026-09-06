from pathlib import Path


PROJECT_ROOT = Path(r"D:\DevPilot")


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


def is_allowed_file(file_path: Path):
    if not file_path.is_file():
        return False

    if any(part in IGNORED_DIRECTORIES for part in file_path.parts):
        return False

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    return True


def list_files():
    files = []

    for file_path in PROJECT_ROOT.rglob("*"):
        if not is_allowed_file(file_path):
            continue

        relative_path = file_path.relative_to(PROJECT_ROOT)

        files.append(str(relative_path))

    return files


def search_repository(query: str):
    results = []

    for file_path in PROJECT_ROOT.rglob("*"):
        if not is_allowed_file(file_path):
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if query.lower() in content.lower():
                relative_path = file_path.relative_to(PROJECT_ROOT)

                results.append({
                    "file": str(relative_path),
                    "match": query,
                })

        except Exception as e:
            print(f"Could not read {file_path}: {e}")

    return results


def read_file(file_path: str):
    target = PROJECT_ROOT / file_path

    if not is_allowed_file(target):
        return {
            "error": "File does not exist or is not an allowed source file."
        }

    try:
        content = target.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return {
            "file": file_path,
            "content": content,
        }

    except Exception as e:
        return {
            "error": f"Could not read file: {e}"
        }