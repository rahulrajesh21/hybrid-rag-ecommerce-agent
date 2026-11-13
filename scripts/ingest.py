from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


def load_files() -> list[Document]:
    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"

    if not knowledge_dir.exists():
        return []

    docs: list[Document] = []
    for file_path in sorted(knowledge_dir.rglob("*.md")):
        if file_path.is_file():
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if content.strip():
                docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path.relative_to(knowledge_dir)),
                            "filename": file_path.name,
                        },
                    )
                )

    return docs


def ingestion() -> list[Document]:
    header_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    raw_docs = load_files()

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=header_to_split_on,
        strip_headers=False,
    )

    header_splits: list[Document] = []

    for doc in raw_docs:
        splits = markdown_splitter.split_text(doc.page_content)

        for split in splits:
            split.metadata.update(doc.metadata)

        header_splits.extend(splits)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    final_chunks = text_splitter.split_documents(header_splits)

    file_chunk_counts: dict[str, int] = {}
    for chunk in final_chunks:
        source = chunk.metadata["source"]
        idx = file_chunk_counts.get(source, 0)
        chunk.metadata["id"] = f"{source}::chunk_{idx}"
        file_chunk_counts[source] = idx + 1

    return final_chunks