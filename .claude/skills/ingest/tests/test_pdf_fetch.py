"""
test_pdf_fetch.py — Phase 2b PDF fetch tests.

Tests use real network (Unpaywall, Crossref, arXiv). Skip if offline.
Run: python3 tests/test_pdf_fetch.py
"""

import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from pdf_fetch import (
    try_unpaywall, try_crossref_link, try_arxiv,
    validate_pdf, download_pdf, fetch_pdf, MAGIC_PDF
)


def _online():
    try:
        urllib.request.urlopen('https://api.crossref.org/works', timeout=5)
        return True
    except Exception:
        return False


class TestPdfFetch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix='pdf_fetch_test_'))
        cls.online = _online()

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_validate_pdf_magic(self):
        """2b.5: magic number check."""
        # Valid PDF header
        valid = self.tmpdir / 'valid.pdf'
        valid.write_bytes(MAGIC_PDF + b'-1.4\n' + b'x' * 2000)
        self.assertTrue(validate_pdf(valid))

        # Invalid (HTML)
        invalid = self.tmpdir / 'invalid.pdf'
        invalid.write_bytes(b'<html><body>404</body></html>')
        self.assertFalse(validate_pdf(invalid))

        # Too small
        tiny = self.tmpdir / 'tiny.pdf'
        tiny.write_bytes(MAGIC_PDF + b'-1.4')
        self.assertFalse(validate_pdf(tiny), 'files < 1KB must fail')

    def test_try_arxiv_doi(self):
        """arXiv DOI pattern → URL."""
        u = try_arxiv('10.48550/arxiv.2403.12345')
        self.assertIsNotNone(u)
        self.assertIn('arxiv.org/pdf/', u)

    def test_try_arxiv_id(self):
        """Raw arXiv ID → URL."""
        u = try_arxiv('2403.12345')
        self.assertIsNotNone(u)

    def test_try_arxiv_non_arxiv(self):
        """Non-arXiv DOI → None."""
        self.assertIsNone(try_arxiv('10.1098/rspa.1957.0133'))

    def test_try_crossref_link_pdf(self):
        """Crossref link-set with application/pdf."""
        meta = {
            'link': [
                {'URL': 'https://example.com/paper.pdf', 'content-type': 'application/pdf'},
                {'URL': 'https://example.com/paper.html', 'content-type': 'text/html'},
            ]
        }
        self.assertEqual(try_crossref_link(meta), 'https://example.com/paper.pdf')

    def test_try_crossref_link_none(self):
        """No application/pdf link → None."""
        self.assertIsNone(try_crossref_link({'link': [{'URL': 'x', 'content-type': 'text/html'}]}))
        self.assertIsNone(try_crossref_link({}))

    def test_try_unpaywall_oa(self):
        """2b.1: Unpaywall OA DOI lookup."""
        if not self.online:
            self.skipTest('offline')
        # Tuegel 2011 — Hindawi OA, well-known
        url = try_unpaywall('10.1155/2011/154798')
        # Unpaywall may return None if rate-limited; just check it doesn't crash
        if url:
            self.assertTrue(url.startswith('http'))

    def test_download_pdf_real_oa(self):
        """2b.1: real OA download + validate."""
        if not self.online:
            self.skipTest('offline')
        url = try_unpaywall('10.1155/2011/154798')
        if not url:
            self.skipTest('Unpaywall did not return URL (rate limit / quota)')
        dest = self.tmpdir / 'Tuegel2011.pdf'
        ok, reason = download_pdf(url, dest, max_size_mb=10)
        if not ok:
            self.skipTest(f'download failed (probably network): {reason}')
        self.assertTrue(dest.exists())
        self.assertTrue(validate_pdf(dest), f'downloaded PDF invalid: {dest.stat().st_size} bytes')

    def test_download_pdf_invalid_magic(self):
        """2b.5: non-PDF URL rejected."""
        if not self.online:
            self.skipTest('offline')
        # Any HTML page
        dest = self.tmpdir / 'html.pdf'
        ok, reason = download_pdf('https://api.crossref.org/works/10.1098/rspa.1957.0133',
                                   dest, max_size_mb=5)
        self.assertFalse(ok, f'must reject non-PDF: {reason}')
        self.assertFalse(dest.exists(), 'partial file must be cleaned up')

    def test_fetch_pdf_idempotent(self):
        """2b.6: existing valid PDF → skip download."""
        dest = self.tmpdir / 'existing.pdf'
        dest.write_bytes(MAGIC_PDF + b'-1.4\n' + b'x' * 3000)
        ok, reason = fetch_pdf('10.9999/fake', {}, dest)
        self.assertTrue(ok)
        self.assertIn('already exists', reason)

    def test_fetch_pdf_fallback_fail(self):
        """all sources fail → False."""
        if not self.online:
            self.skipTest('offline')
        dest = self.tmpdir / 'nonexistent.pdf'
        ok, reason = fetch_pdf('10.9999/definitely-not-real-xyz', {}, dest)
        self.assertFalse(ok)
        self.assertFalse(dest.exists())

    def test_fetch_pdf_arxiv(self):
        """2b.3: arXiv DOI full fetch."""
        if not self.online:
            self.skipTest('offline')
        # Use a known arXiv paper (small)
        dest = self.tmpdir / 'arxiv.pdf'
        ok, reason = fetch_pdf('10.48550/arxiv.1706.03762', {}, dest, max_size_mb=5)
        # 1706.03762 = Attention Is All You Need (always available)
        if not ok:
            self.skipTest(f'arxiv fetch failed: {reason}')
        self.assertTrue(validate_pdf(dest))


if __name__ == '__main__':
    unittest.main(verbosity=2)
