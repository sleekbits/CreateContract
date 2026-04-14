from __future__ import annotations

import shutil
from pathlib import Path

from docx2pdf import convert
from docxtpl import DocxTemplate


class TemplateEngine:
    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_contract(self, template_path: str, data: dict[str, str], save_dir: str, base_filename: str) -> tuple[str, str]:
        target_dir = Path(save_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        docx_file = target_dir / f"{base_filename}.docx"
        pdf_file = target_dir / f"{base_filename}.pdf"

        docx_file = self._avoid_overwrite(docx_file)
        pdf_file = docx_file.with_suffix(".pdf")

        tpl = DocxTemplate(template_path)
        tpl.render(data)
        tpl.save(docx_file)

        self._convert_to_pdf(docx_file, pdf_file)
        return str(docx_file), str(pdf_file)

    def _avoid_overwrite(self, filepath: Path) -> Path:
        if not filepath.exists():
            return filepath
        idx = 1
        while True:
            candidate = filepath.with_name(f"{filepath.stem}_{idx}{filepath.suffix}")
            if not candidate.exists():
                return candidate
            idx += 1

    def _convert_to_pdf(self, docx_file: Path, pdf_file: Path) -> None:
        try:
            convert(str(docx_file), str(pdf_file))
            return
        except Exception:
            pass

        try:
            import win32com.client  # type: ignore

            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(str(docx_file.resolve()))
            doc.SaveAs(str(pdf_file.resolve()), FileFormat=17)
            doc.Close(False)
            word.Quit()
        except Exception as ex:
            raise RuntimeError(
                f"DOCX generated but PDF conversion failed. Ensure Microsoft Word is installed. Details: {ex}"
            )

    @staticmethod
    def install_template(source_file: str, template_name: str) -> str:
        target_dir = Path("assets/templates")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{template_name}.docx"
        shutil.copy2(source_file, target)
        return str(target)
