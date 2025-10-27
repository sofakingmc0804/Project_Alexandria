"""Utilities for generating lightweight documentation and stub files."""

from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ModuleDoc:
    """Collected documentation for a module."""

    name: str
    docstring: str | None
    members: list[str]


def _resolve_modules(package_roots: Sequence[str]) -> list[str]:
    modules: list[str] = []
    root_path = Path("app")
    for package in package_roots:
        package_path = root_path / Path(package.replace(".", "/"))
        if not package_path.exists():
            continue
        for py_file in package_path.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            if "__pycache__" in py_file.parts:
                continue
            module_name = "app." + py_file.relative_to(root_path).with_suffix("").as_posix().replace("/", ".")
            modules.append(module_name)
    return sorted(set(modules))


def collect_module_docs(package_roots: Sequence[str]) -> list[ModuleDoc]:
    """Collect documentation details for all modules under the given package roots."""

    docs: list[ModuleDoc] = []
    for module_name in _resolve_modules(package_roots):
        try:
            module = importlib.import_module(module_name)
        except Exception:  # pragma: no cover - skip modules with import issues
            continue
        docstring = inspect.getdoc(module)
        members: list[str] = []
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            if inspect.isfunction(obj) or inspect.isclass(obj):
                signature = ""
                try:
                    signature = str(inspect.signature(obj))
                except (TypeError, ValueError):
                    signature = "()"
                members.append(f"- {name}{signature}")
        docs.append(ModuleDoc(name=module_name, docstring=docstring, members=sorted(members)))
    return docs


def generate_markdown_docs(output_dir: Path, package_roots: Sequence[str]) -> list[Path]:
    """Generate Markdown documentation for modules under the provided roots."""

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for module_doc in collect_module_docs(package_roots):
        relative_name = module_doc.name.replace("app.", "")
        doc_path = output_dir / f"{relative_name.replace('.', '_')}.md"
        lines: list[str] = [f"# {module_doc.name}"]
        lines.append("")
        if module_doc.docstring:
            lines.append(module_doc.docstring)
            lines.append("")
        if module_doc.members:
            lines.append("## Members")
            lines.extend(module_doc.members)
            lines.append("")
        doc_path.write_text("\n".join(lines), encoding="utf-8")
        generated.append(doc_path)
    return generated


def generate_stub_files(output_dir: Path, package_roots: Sequence[str]) -> list[Path]:
    """Generate minimal .pyi stub files for modules under the provided roots."""

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    root_path = Path("app")
    for module_name in _resolve_modules(package_roots):
        try:
            importlib.import_module(module_name)
        except Exception:  # pragma: no cover - skip modules with import errors
            continue
        stub_rel = module_name.replace("app.", "").replace(".", "/") + ".pyi"
        stub_path = output_dir / stub_rel
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        header = (
            "\"\"\"Auto-generated stub for "
            + module_name
            + "\"\"\"\nfrom typing import Any as _Any\n\n__all__: list[str]\n"
        )
        stub_path.write_text(header, encoding="utf-8")
        generated.append(stub_path)
    return generated


__all__ = [
    "ModuleDoc",
    "collect_module_docs",
    "generate_markdown_docs",
    "generate_stub_files",
]
