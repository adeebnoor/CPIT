from __future__ import annotations

import ipaddress
import socket
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_EXTRACTED_CHARS = 220_000
WEB_HEADING_PREFIX = "SOURCE HEADING: "


def _validate_public_url(url: str) -> str:
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid public http(s) URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")
    if parsed.port not in {None, 80, 443}:
        raise ValueError("Only standard web ports 80 and 443 are allowed.")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local/private URLs are not allowed.")
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("The source hostname could not be resolved.") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("Private, loopback, link-local, and reserved addresses are not allowed.")
    return url


def _download(url: str) -> tuple[bytes, str, str]:
    safe_url = _validate_public_url(url)
    req = Request(
        safe_url,
        headers={
            "User-Agent": "ISCARB-Lecture-Studio/1.1 (+source-grounded educational compiler)",
            "Accept": "text/html,application/pdf,text/plain;q=0.9,*/*;q=0.5",
        },
    )
    with urlopen(req, timeout=20) as resp:
        final_url = _validate_public_url(resp.geturl())
        ctype = (resp.headers.get_content_type() or "application/octet-stream").lower()
        length = resp.headers.get("Content-Length")
        if length and int(length) > MAX_SOURCE_BYTES:
            raise ValueError("The linked source is too large. Please upload the file instead.")
        data = resp.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError("The linked source is too large. Please upload the file instead.")
        return data, ctype, final_url


def _clean(text: str) -> str:
    return " ".join(unescape(text or "").split()).strip()


def _extract_slideshare(soup: BeautifulSoup, source_url: str) -> str | None:
    slide_alts: list[str] = []
    seen: set[str] = set()
    for img in soup.find_all("img"):
        alt = _clean(img.get("alt", ""))
        src = str(img.get("src") or img.get("data-src") or img.get("data-lazy-src") or "")
        if len(alt) < 35 or "slidesharecdn" not in src:
            continue
        if alt in seen:
            continue
        seen.add(alt)
        slide_alts.append(alt)
    if not slide_alts:
        return None
    title_tag = soup.find("h1")
    title = _clean(title_tag.get_text(" ", strip=True)) if title_tag else "SlideShare lecture"
    lines = [f"SOURCE URL: {source_url}", f"SOURCE TITLE: {title}", "SOURCE TYPE: SlideShare slide-text extraction", ""]
    for idx, alt in enumerate(slide_alts, start=1):
        lines.append(f"SLIDE {idx}: {alt}")
    return "\n\n".join(lines)


def _extract_html(data: bytes, source_url: str) -> str:
    """Extract a public web lecture while preserving its visible structure.

    Modern pages use h1-h6/p/li; older university lecture notes often use HTML
    definition lists (dt/dd), table cells, or blockquotes instead. Treating only
    p/li as content silently dropped named strategy lists from otherwise readable
    sources. This extractor keeps those author-visible blocks, deduplicates them,
    and never follows images or public-web visual fallbacks.
    """
    soup = BeautifulSoup(data, "html.parser")
    host = (urlparse(source_url).hostname or "").lower()
    if "slideshare.net" in host:
        specialized = _extract_slideshare(soup, source_url)
        if specialized:
            return specialized[:MAX_EXTRACTED_CHARS]

    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()
    title = _clean(soup.title.get_text(" ", strip=True)) if soup.title else "Web source"
    chunks: list[str] = [f"SOURCE URL: {source_url}", f"SOURCE TITLE: {title}", "SOURCE TYPE: public web page", ""]
    seen: set[str] = set()
    heading_tags = {"h1", "h2", "h3", "h4", "h5", "h6"}
    content_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd", "td", "th", "blockquote", "pre"]
    for tag in soup.find_all(content_tags):
        text = _clean(tag.get_text(" ", strip=True))
        if len(text) < 3 or text in seen:
            continue
        seen.add(text)
        chunks.append(f"{WEB_HEADING_PREFIX}{text}" if tag.name in heading_tags else text)
        if sum(len(x) for x in chunks) >= MAX_EXTRACTED_CHARS:
            break
    return "\n\n".join(chunks)[:MAX_EXTRACTED_CHARS]


def materialize_url_source(url: str, target_dir: Path) -> Path:
    data, ctype, final_url = _download(url)
    target_dir.mkdir(parents=True, exist_ok=True)
    if ctype == "application/pdf" or data.startswith(b"%PDF"):
        path = target_dir / "linked_source.pdf"
        path.write_bytes(data)
        return path
    if ctype.startswith("text/plain"):
        path = target_dir / "linked_source.txt"
        path.write_text(data.decode("utf-8", errors="replace")[:MAX_EXTRACTED_CHARS], encoding="utf-8")
        return path
    if ctype in {"text/html", "application/xhtml+xml"} or b"<html" in data[:5000].lower():
        text = _extract_html(data, final_url)
        if len(text.strip()) < 200:
            raise ValueError("Not enough readable lecture content could be extracted from this URL. Upload the PDF/PPTX instead.")
        path = target_dir / "linked_source.txt"
        path.write_text(text, encoding="utf-8")
        return path
    raise ValueError("This URL does not expose a supported readable source. Upload PDF/PPTX/DOCX instead.")
