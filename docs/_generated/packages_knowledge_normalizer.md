# app.packages.knowledge.normalizer

Knowledge Normalizer - Extracts text from source documents
Uses GROBID for PDFs, Unstructured for docs, outputs to sources_clean/

## Members
- Path(*args, **kwargs)
- PdfReader(stream: Union[str, IO, pathlib._local.Path], strict: bool = False, password: Union[NoneType, str, bytes] = None) -> None
- extract_text_from_pdf(pdf_path: pathlib._local.Path) -> str
- extract_text_from_txt(txt_path: pathlib._local.Path) -> str
- main()
- normalize_all()
- normalize_file(raw_path: pathlib._local.Path) -> Optional[pathlib._local.Path]
