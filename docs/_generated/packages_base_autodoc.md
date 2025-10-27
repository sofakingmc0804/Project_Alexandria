# app.packages.base.autodoc

Utilities for generating lightweight documentation and stub files.

## Members
- ModuleDoc(name: 'str', docstring: 'str | None', members: 'list[str]') -> None
- Path(*args, **kwargs)
- collect_module_docs(package_roots: 'Sequence[str]') -> 'list[ModuleDoc]'
- dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
- generate_markdown_docs(output_dir: 'Path', package_roots: 'Sequence[str]') -> 'list[Path]'
- generate_stub_files(output_dir: 'Path', package_roots: 'Sequence[str]') -> 'list[Path]'
