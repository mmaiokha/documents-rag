from dataclasses import dataclass
import fitz

from core.storage import read_from_minio
import re


@dataclass
class Page:
    number: int
    text: str

@dataclass
class Chunk:
    content: str
    page_start: int
    page_end: int
    chunk_index: int

@dataclass
class Paragraph:
    page: int
    content: str


def clean_text(text: str) -> str:
    # remove zero-width symbols
    text = text.replace("\u200b", "")

    # replace non-bracking space
    text = text.replace("\xa0", " ")

    # Line break within a sentence - space
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # At most one empty separator between blocks
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def parse_pdf(bucket: str, key: str) -> list[Page]:
    pdf = read_from_minio(bucket=bucket, object_key=key)

    document = fitz.open(stream=pdf.getvalue(), filetype="pdf")

    pages = []

    for number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        if text:
            pages.append(
                Page(
                    number=number,
                    text=clean_text(text),
                )
            )

    document.close()

    return pages

def chunk_pages(pages: list[Page]) -> list[Chunk]:
    paragraphs: list[Paragraph] = []

    for page in pages:
        paragraphs.append(*split_paragraphs(page)) 


    return chunk_paragraphs(paragraphs=paragraphs)

def split_paragraphs(page: Page) -> list[Paragraph]:

    paragraphs = re.split(r"\n\s*\n", page.text)

    result = []

    for paragraph in paragraphs:
        paragraph = re.sub(r"\s*\n\s*", " ", paragraph)

        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()

        if paragraph:
            result.append(Paragraph(content=paragraph, page=page.number))

    return result

def chunk_paragraphs(
    paragraphs: list[Paragraph],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[Chunk]:

    chunks: list[Chunk] = []

    current_parts: list[str] = []
    current_size = 0
    current_page_start: int | None = None
    current_page_end: int | None = None

    for paragraph in paragraphs:
        content = paragraph.content

        # Huge paragraph
        if len(content) > chunk_size:

            # Save previous chunk
            if current_parts:
                chunks.append(
                    Chunk(
                        content="\n\n".join(current_parts),
                        page_start=current_page_start,
                        page_end=current_page_end,
                        chunk_index=len(chunks)
                    )
                )

                current_parts = []
                current_size = 0
                current_page_start = None
                current_page_end = None

            # Cut huge paragraph
            start = 0

            while start < len(content):
                end = start + chunk_size

                chunks.append(
                    Chunk(
                        content=content[start:end],
                        page_start=paragraph.page,
                        page_end=paragraph.page,
                        chunk_index=len(chunks)
                    )
                )

                if end >= len(content):
                    break

                start = end - overlap

            continue

        # Regular paragraph

        separator_size = 2 if current_parts else 0

        new_size = (
            current_size
            + separator_size
            + len(content)
        )

        # If small paragraph - save it to the current chunk and continue
        if new_size <= chunk_size:
            current_parts.append(content)
            current_size = new_size

            if current_page_start is None:
                current_page_start = paragraph.page

            current_page_end = paragraph.page

            continue

        # If prev + current paragraph size > chunk_size - save previous chunk and begin new one
        chunks.append(
            Chunk(
                content="\n\n".join(current_parts),
                page_start=current_page_start,
                page_end=current_page_end,
                chunk_index=len(chunks)
            )
        )

        # Begin new chunk
        current_parts = [content]
        current_size = len(content)
        current_page_start = paragraph.page
        current_page_end = paragraph.page

    # last chunk
    if current_parts:
        chunks.append(
            Chunk(
                content="\n\n".join(current_parts),
                page_start=current_page_start,
                page_end=current_page_end,
                chunk_index=len(chunks)
            )
        )

    return chunks