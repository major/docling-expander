"""Main script."""

import logging
from pathlib import Path

import httpx
import structlog
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from docling_core.types.doc.document import SectionHeaderItem
from rich import print
from transformers import AutoModel, AutoTokenizer

from expander.config import settings

logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

TOKENIZER = AutoTokenizer.from_pretrained(settings.embed_model)
EMBED_MODEL = AutoModel.from_pretrained(settings.embed_model)


def prepare_temp_storage() -> None:
    Path(settings.temporary_storage_path).mkdir(parents=True, exist_ok=True)


def get_example_document() -> Path:
    """Download the example document."""
    prepare_temp_storage()
    doc_file = Path(settings.temporary_storage_path) / "example_document.html"

    if not doc_file.exists():
        resp = httpx.get(settings.example_doc_url, timeout=30)
        resp.raise_for_status()
        doc_file.write_text(resp.text, encoding="utf-8")
        logger.info("Downloaded example document", url=settings.example_doc_url)

    return doc_file


def get_example_pdf_document() -> Path:
    """Download the example PDF document."""
    prepare_temp_storage()
    pdf_file = Path(settings.temporary_storage_path) / "example_document.pdf"

    if not pdf_file.exists():
        resp = httpx.get(settings.example_pdf_url, timeout=30)
        resp.raise_for_status()
        pdf_file.write_bytes(resp.content)
        logger.info("Downloaded example PDF document", url=settings.example_pdf_url)

    return pdf_file


def convert_to_docling_format(doc_path: Path) -> ConversionResult:
    """Convert the document to Docling format."""
    converter = DocumentConverter()
    result = converter.convert(doc_path)
    result.document.save_as_json(doc_path.with_suffix(".docling.json"))
    logger.info("Converted document to Docling format", path=doc_path)

    return result


def chunk_document(docling_doc: ConversionResult) -> list:
    """Chunk the document into manageable pieces."""
    chunker = HybridChunker(tokenizer=TOKENIZER)
    chunk_iter = chunker.chunk(dl_doc=docling_doc.document)

    return list(chunk_iter)


def main() -> None:
    """Main function to run the expander."""
    example_doc = get_example_document()
    docling_doc = convert_to_docling_format(example_doc)
    chunks = chunk_document(docling_doc)

    # Find an example list item where the chunk is incomplete. It doesn't contain the
    # full list and it also does not include the instructions above the list.
    chunk_to_expand = next(
        x
        for x in chunks
        if "On your host system, start an AI Inference Server" in x.text
    )
    # print(chunk_to_expand)

    # Find the parent of the list item, which should be the list group.
    parent_ref = chunk_to_expand.meta.doc_items[0].parent

    # Traverse up the hierarchy to find the section header item.
    while True:
        parent_item = parent_ref.resolve(doc=docling_doc.document)

        if not isinstance(parent_item, SectionHeaderItem):
            parent_ref = parent_item.parent
            continue
        else:
            break

    # Set up the serializer.
    serializer = MarkdownDocSerializer(doc=docling_doc.document)

    # Serialize all of the children.
    # Bug with code/pre blocks in list items: https://github.com/docling-project/docling/issues/2103
    parts = serializer.get_parts(item=parent_item)
    text = "\n-----\n".join([part.text for part in parts])
    print(text)


if __name__ == "__main__":
    main()
