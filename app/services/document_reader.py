from pathlib import Path

from pypdf import PdfReader


class DocumentReader:
    SUPPORTED_TEXT_TYPES = {".txt", ".md"}

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            reader = PdfReader(str(path))
            parts: list[str] = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            return "\n".join(parts).strip()

        if suffix in cls.SUPPORTED_TEXT_TYPES:
            return path.read_text(encoding="utf-8").strip()

        raise ValueError("Only PDF, TXT, and MD files are supported for indexing.")
