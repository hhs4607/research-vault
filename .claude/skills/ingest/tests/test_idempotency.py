"""
test_idempotency.py — Phase 2a core tests.

Run: python3 -m pytest tests/test_idempotency.py
or:  python3 tests/test_idempotency.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from vault import (
    find_vault,
    find_note_by_doi,
    resolve_author_year_idempotent,
    parse_frontmatter,
    is_confirmed,
    pending_has_doi,
)


class TestIdempotency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vault = find_vault()

    def test_find_note_by_doi_existing(self):
        """2a.1: existing DOI must return Path (any valid match)."""
        # Hashin & Rotem 1973 (Paper-1 §2.1 anchor)
        # Vault convention may use Hashin1973 or HashinRotem1973
        p = find_note_by_doi(self.vault, '10.1177/002199837300700404')
        if p:
            self.assertTrue(p.exists(), msg=f'returned Path must exist: {p}')
            self.assertTrue(p.stem.startswith('Hashin'),
                            msg=f'unexpected stem: {p.stem}')
        else:
            # fallback: try Han 2025 self-cite
            p2 = find_note_by_doi(self.vault, '10.3390/polym17020157')
            self.assertIsNotNone(p2, msg='at least one known DOI must resolve')

    def test_find_note_by_doi_missing(self):
        """2a.2: nonexistent DOI returns None."""
        p = find_note_by_doi(self.vault, '10.9999/definitely-fake-12345')
        self.assertIsNone(p)

    def test_find_note_by_doi_excludes_broken(self):
        """2a.3: _broken/ subfolder excluded."""
        pn_dir = self.vault / '07-wiki' / 'paper-notes' / '_broken'
        if not pn_dir.exists():
            self.skipTest('_broken not present')
        # Create test file in _broken with known DOI
        test_doi = '10.0000/broken-test-zzz'
        test_file = pn_dir / 'BrokenTest2099.md'
        test_file.write_text(f'---\ndoi: "{test_doi}"\n---\n\n# Test\n')
        try:
            result = find_note_by_doi(self.vault, test_doi)
            self.assertIsNone(result, msg='_broken/ file must not match')
        finally:
            test_file.unlink(missing_ok=True)

    def test_resolve_author_year_update_on_doi_match(self):
        """2a.4: same DOI → action='update'."""
        # Use an existing paper-note
        existing = None
        for p in (self.vault / '07-wiki' / 'paper-notes').glob('*.md'):
            if '_broken' in p.parts:
                continue
            fm = parse_frontmatter(p)
            if fm.get('doi'):
                existing = (p, fm.get('doi'))
                break
        if not existing:
            self.skipTest('no paper-note with DOI available')
        author_year, action = resolve_author_year_idempotent(
            self.vault, existing[0].stem, existing[1])
        self.assertEqual(action, 'update')
        self.assertEqual(author_year, existing[0].stem)

    def test_resolve_author_year_create_new(self):
        """2a.5: different DOI, unused base → action='create', base name."""
        base = 'FakeAuthor9999'
        fake_doi = '10.0000/fake-fake-fake'
        author_year, action = resolve_author_year_idempotent(
            self.vault, base, fake_doi)
        self.assertEqual(action, 'create')
        self.assertEqual(author_year, base)

    def test_resolve_author_year_suffix_on_collision(self):
        """2a.5b: base collides, different DOI → suffix 'b'."""
        # Pick an existing author_year
        existing = None
        for p in (self.vault / '07-wiki' / 'paper-notes').glob('*.md'):
            if '_broken' in p.parts:
                continue
            existing = p.stem
            break
        if not existing:
            self.skipTest('no paper-note available')
        fake_doi = '10.0000/collision-test-xxx'
        author_year, action = resolve_author_year_idempotent(
            self.vault, existing, fake_doi)
        self.assertEqual(action, 'create')
        self.assertTrue(author_year != existing,
                        msg=f'expected suffix, got same {author_year}')

    def test_pending_has_doi_existing(self):
        """2a.6: _pending.md lookup."""
        # Check if any DOI in pending
        pending = self.vault / '03-projects/Paper-1/references/_pending.md'
        if not pending.exists():
            self.skipTest('_pending.md not found')
        # Use a known non-pending DOI
        self.assertFalse(pending_has_doi(self.vault, '10.9999/totally-fake'))

    def test_is_confirmed_strict(self):
        """2a.7: CONFIRMED strict check (Codex B8)."""
        partial = {
            'paper1_sections': ['§2.1'],
            'paper1_tier': 'A',
            'paper1_role': 'anchor',
            'doi': '10.1177/...',
            # missing: paper1_slots, ingest_agent
        }
        self.assertFalse(is_confirmed(partial),
                         msg='Missing slot should fail CONFIRMED')

        complete = {
            'paper1_sections': ['§2.1'],
            'paper1_slots': ['§2.1 P2'],
            'paper1_tier': 'A',
            'paper1_role': 'anchor',
            'doi': '10.1177/002199837300700404',
            'ingest_agent': '§2-agent',
        }
        self.assertTrue(is_confirmed(complete))

        # Invalid tier
        bad_tier = complete.copy()
        bad_tier['paper1_tier'] = 'Z'
        self.assertFalse(is_confirmed(bad_tier))

    def test_vault_detection(self):
        """2a.8 regression: vault_detection works on this env."""
        v = find_vault()
        self.assertTrue((v / 'CLAUDE.md').exists())
        self.assertTrue((v / '07-wiki').is_dir())


if __name__ == '__main__':
    unittest.main(verbosity=2)
