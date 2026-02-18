import sys
import re
import zlib
import base64


def extract_text_from_pdf(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()

    # Find all stream...endstream sections (very naive parser, but enough for this assignment)
    streams = []
    start = 0
    while True:
        stream_idx = data.find(b"stream", start)
        if stream_idx == -1:
            break
        endstream_idx = data.find(b"endstream", stream_idx)
        if endstream_idx == -1:
            break
        # Skip the "stream" keyword and following newline
        stream_content = data[stream_idx + len(b"stream") : endstream_idx].strip(b"\r\n")
        streams.append(stream_content)
        start = endstream_idx + len(b"endstream")

    texts = []
    for raw in streams:
        decoded = raw
        # Apply ASCII85 and Flate if possible; ignore failures
        try:
            decoded = base64.a85decode(decoded, adobe=True)
        except Exception:
            pass
        try:
            decoded = zlib.decompress(decoded)
        except Exception:
            pass

        try:
            s = decoded.decode("latin-1", errors="ignore")
        except Exception:
            continue

        # Extract text within parentheses used by Tj/TJ operators
        for match in re.findall(r"\(([^)]*)\)\s*(?:Tj|TJ)", s):
            texts.append(match)

    return "\n".join(texts)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python extract_pdf_text.py <pdf_path>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    text = extract_text_from_pdf(path)
    print(text)


if __name__ == "__main__":
    main()

