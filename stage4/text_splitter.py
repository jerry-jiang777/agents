from rag_config import CHUNK_OVERLAP, CHUNK_SIZE


def split_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    chunks = []
    for document in documents:
        chunks.extend(split_document(document, chunk_size, chunk_overlap))
    return chunks


def split_document(document, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    lines = document["lines"]
    source = document["source"]
    chunks = []
    current_lines = []
    current_length = 0
    start_line = 1
    heading_path = []

    for line_number, line in enumerate(lines, start=1):
        heading = parse_markdown_heading(line)
        if heading:
            level, title = heading
            heading_path = heading_path[: level - 1]
            heading_path.append(title)

        line_length = len(line) + 1
        if current_lines and current_length + line_length > chunk_size:
            chunks.append(
                build_chunk(source, current_lines, start_line, line_number - 1, heading_path)
            )
            overlap_lines = take_overlap_lines(current_lines, chunk_overlap)
            current_lines = overlap_lines[:]
            current_length = sum(len(item) + 1 for item in current_lines)
            start_line = max(1, line_number - len(current_lines))

        current_lines.append(line)
        current_length += line_length

    if current_lines:
        chunks.append(build_chunk(source, current_lines, start_line, len(lines), heading_path))

    for index, chunk in enumerate(chunks):
        chunk["chunk_id"] = index
    return chunks


def parse_markdown_heading(line):
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    hashes = len(stripped) - len(stripped.lstrip("#"))
    if hashes > 6:
        return None
    title = stripped[hashes:].strip()
    if not title:
        return None
    return hashes, title


def take_overlap_lines(lines, chunk_overlap):
    if chunk_overlap <= 0:
        return []
    overlap = []
    total_length = 0
    for line in reversed(lines):
        line_length = len(line) + 1
        if overlap and total_length + line_length > chunk_overlap:
            break
        overlap.insert(0, line)
        total_length += line_length
    return overlap


def build_chunk(source, lines, start_line, end_line, heading_path):
    text = "\n".join(lines).strip()
    return {
        "source": source,
        "start_line": start_line,
        "end_line": end_line,
        "heading_path": " > ".join(heading_path),
        "text": text,
    }
