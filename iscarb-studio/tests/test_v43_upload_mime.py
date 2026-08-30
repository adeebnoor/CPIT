from __future__ import annotations

import unittest
from pathlib import Path

from app.gemini_service import GeminiService
from app.main import ALLOWED_EXTS


class UploadMimeTypeTests(unittest.TestCase):
    """Uploading a PowerPoint chapter stopped the compile with
    "Unknown mime type: Could not determine the mimetype for your file".
    The SDK infers the type from the filename and raises when it cannot, and
    .pptx is not in the production image's mimetypes registry."""

    def test_every_accepted_format_has_a_named_mime_type(self):
        for ext in sorted(ALLOWED_EXTS):
            with self.subTest(ext=ext):
                mime = GeminiService._mime_for(Path("lecture" + ext))
                self.assertNotEqual(mime, "application/octet-stream",
                                    f"{ext} would be uploaded without a usable type")
                self.assertIn("/", mime)

    def test_powerpoint_resolves_to_the_openxml_type(self):
        self.assertEqual(
            GeminiService._mime_for(Path("Ch13.pptx")),
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    def test_resolution_does_not_depend_on_the_local_registry(self):
        """The registry differs between the dev machine and the production image,
        which is why this only failed in production."""
        import mimetypes
        original = mimetypes.guess_type
        mimetypes.guess_type = lambda *_a, **_k: (None, None)
        try:
            self.assertEqual(
                GeminiService._mime_for(Path("Ch13.pptx")),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        finally:
            mimetypes.guess_type = original

    def test_an_unknown_suffix_still_uploads_rather_than_raising(self):
        self.assertEqual(GeminiService._mime_for(Path("notes.unknownext")), "application/octet-stream")

    def test_upload_passes_the_type_instead_of_relying_on_inference(self):
        import inspect
        source = inspect.getsource(GeminiService._upload)
        self.assertIn("mime_type", source, "upload still lets the SDK guess the type")


if __name__ == "__main__":
    unittest.main()
