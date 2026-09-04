from __future__ import annotations

import ipaddress
import json
import mimetypes
import socket
from html import unescape
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_EXTRACTED_CHARS = 220_000
MAX_SOURCE_IMAGE_BYTES = 5 * 1024 * 1024
MAX_SOURCE_IMAGES = 16
MIN_SOURCE_IMAGE_WIDTH = 220
MIN_SOURCE_IMAGE_HEIGHT = 120
WEB_HEADING_PREFIX = "SOURCE HEADING: "
WEB_IMAGE_MANIFEST = "source_web_images.json"


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
    sources. Author-visible figures are materialized separately by
    ``_materialize_html_images`` so the text profile remains clean while the
    Presenter can still reuse genuine P1 figures.
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


def _candidate_img_src(img) -> str:
    for key in ("src", "data-src", "data-lazy-src", "data-original"):
        raw = str(img.get(key) or "").strip()
        if raw:
            return raw
    srcset = str(img.get("srcset") or "").strip()
    if srcset:
        return srcset.split(",")[0].strip().split(" ")[0]
    return ""


def _image_records(soup: BeautifulSoup, source_url: str) -> list[dict]:
    """Find only figures explicitly embedded by the P1 page.

    No search engine, stock-photo site, Wikipedia fallback, or keyword lookup is
    used. For safety and provenance, remote image fetches are restricted to the
    same hostname as the supplied P1 page.
    """
    page_host = (urlparse(source_url).hostname or "").lower().rstrip(".")
    content_names = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd", "td", "th", "blockquote", "pre"}
    heading_names = {"h1", "h2", "h3", "h4", "h5", "h6"}
    section = 3  # SOURCE URL / TITLE / TYPE are P1 sections 1..3 in the profile.
    seen_text: set[str] = set()
    seen_url: set[str] = set()
    recent: list[str] = []
    heading = ""
    out: list[dict] = []

    for tag in soup.find_all(list(content_names | {"img"})):
        if tag.name != "img":
            text = _clean(tag.get_text(" ", strip=True))
            if len(text) < 3 or text in seen_text:
                continue
            seen_text.add(text)
            section += 1
            recent.append(text)
            recent = recent[-3:]
            if tag.name in heading_names:
                heading = text
            continue

        raw = _candidate_img_src(tag)
        if not raw or raw.startswith("data:"):
            continue
        image_url = urljoin(source_url, raw)
        parsed = urlparse(image_url)
        if parsed.scheme not in {"http", "https"} or (parsed.hostname or "").lower().rstrip(".") != page_host:
            continue
        if image_url in seen_url:
            continue
        seen_url.add(image_url)
        alt = _clean(tag.get("alt", ""))
        stem = _clean(Path(parsed.path).stem.replace("_", " ").replace("-", " "))
        context_parts = [x for x in [heading, *recent, alt, stem] if x]
        context = " · ".join(dict.fromkeys(context_parts))[:1600]
        out.append({
            "section": max(4, section),
            "image_url": image_url,
            "alt_text": alt or stem or f"Primary source figure near section {section}",
            "context": context,
        })
        if len(out) >= MAX_SOURCE_IMAGES:
            break
    return out


def _download_source_image(image_url: str, target: Path) -> tuple[int, int, str] | None:
    try:
        safe = _validate_public_url(image_url)
        req = Request(safe, headers={"User-Agent": "ISCARB-Source-Figure/1.0", "Accept": "image/*"})
        with urlopen(req, timeout=15) as resp:
            final = _validate_public_url(resp.geturl())
            ctype = (resp.headers.get_content_type() or "").lower()
            if not ctype.startswith("image/"):
                return None
            data = resp.read(MAX_SOURCE_IMAGE_BYTES + 1)
            if len(data) < 1000 or len(data) > MAX_SOURCE_IMAGE_BYTES:
                return None
        from PIL import Image
        with Image.open(BytesIO(data)) as im:
            width, height = im.size
            if width < MIN_SOURCE_IMAGE_WIDTH or height < MIN_SOURCE_IMAGE_HEIGHT:
                return None
            fmt = (im.format or "PNG").upper()
            if fmt in {"PNG", "JPEG", "WEBP"}:
                ext = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}[fmt]
                actual = target.with_suffix(ext)
                actual.write_bytes(data)
            else:
                actual = target.with_suffix(".png")
                im.convert("RGB").save(actual, format="PNG")
        return width, height, str(actual)
    except Exception:
        return None


def _materialize_html_images(data: bytes, source_url: str, target_dir: Path) -> None:
    """Persist genuine P1 page figures beside the linked-source text.

    This is deliberately *not* a public-image fallback. The only accepted image
    URLs are img elements authored into the supplied primary page itself, on the
    same hostname. Failure is non-fatal and falls back to native ISCARB diagrams.
    """
    try:
        soup = BeautifulSoup(data, "html.parser")
        title = _clean(soup.title.get_text(" ", strip=True)) if soup.title else "Web source"
        records = _image_records(soup, source_url)
        if not records:
            return
        image_dir = target_dir / "source_web_images"
        image_dir.mkdir(parents=True, exist_ok=True)
        assets: list[dict] = []
        for index, record in enumerate(records, 1):
            result = _download_source_image(record["image_url"], image_dir / f"source-{index:02d}")
            if not result:
                continue
            width, height, local_path = result
            assets.append({**record, "local_path": local_path, "width": width, "height": height})
        if not assets:
            return
        (target_dir / WEB_IMAGE_MANIFEST).write_text(json.dumps({
            "source_url": source_url,
            "source_title": title,
            "source_kind": "source-web",
            "assets": assets,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Visual extraction must never block source compilation.
        return


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
        _materialize_html_images(data, final_url, target_dir)
        return path
    raise ValueError("This URL does not expose a supported readable source. Upload PDF/PPTX/DOCX instead.")
