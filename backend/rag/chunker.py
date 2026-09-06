def chunk_documents(documents, chunk_size=1200, overlap=200):
    chunks = []

    for document in documents:
        content = document["content"]

        if not content.strip():
            continue

        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk_content = content[start:end]

            start_line = content[:start].count("\n") + 1
            end_line = content[:end].count("\n") + 1

            chunks.append({
                "content": chunk_content,
                "path": document["path"],
                "filename": document["filename"],
                "extension": document["extension"],
                "language": document["language"],
                "start_line": start_line,
                "end_line": end_line,
            })

            start += chunk_size - overlap

    return chunks