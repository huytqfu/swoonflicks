"""Test _src/new_film.py trên synopsis mẫu (Dragons Bow). Chạy: python3 _src/tests/new_film_test.py"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import new_film as nf

SPEC = {
    "slug": "sample-dragon-academy",
    "title": "Dragons Bow To The Trash",
    "network": "NetShort",
    "genre": ["Fantasy"],
    "synopsis": "Born without a Dragon Mark, Elias is mocked as a powerless nobody at the Royal Dragon Rider Academy. "
                "No one knows he once routed a Level 72 Demon King, commands dragons without a bond, and has awakened "
                "Alexstrasza, the ancient King of Dragons. As corrupt nobles rig the trials against him, the academy is "
                "about to learn who the real monster is.",
    "sources": {"episodes": "https://example.com/full-episodes/sample-1", "app": None},
}


class NewFilm(unittest.TestCase):
    def setUp(self):
        self.ct, self.seo, self.home = nf.make(dict(SPEC))

    def errs(self, ct=None, seo=None):
        return nf.lint(SPEC["title"], SPEC["synopsis"], ct or self.ct, seo or self.seo, SPEC["network"])

    def test_schema(self):
        self.assertEqual(set(self.seo), {"title", "description", "keywords", "sources", "checked"})
        self.assertEqual(set(self.seo["sources"]), {"episodes", "app"})
        self.assertEqual(self.ct["faq"][0]["q"], "Where can I watch Dragons Bow To The Trash?")
        self.assertNotIn("intro", self.ct)  # không viết hộ intro
        self.assertLessEqual(len(self.seo["title"]), 60)
        self.assertLessEqual(len(self.seo["description"]), 155)
        self.assertTrue(self.seo["description"].startswith("Born without a Dragon Mark"))

    def test_generated_is_clean(self):
        self.assertEqual(self.errs(), [])

    def test_bans(self):
        bad = {**self.ct, "intro": "Watch it free on NetShort, all 48 episodes, as Elias draws his sword."}
        e = " | ".join(self.errs(ct=bad))
        for x in ("'free'", "'NetShort'", "'48 episodes'", "'sword'", "số 48"):
            self.assertIn(x, e)

    def test_fabricated_name(self):
        bad = {**self.ct, "why": ["A rivalry with Prince Gavin Mercer drives every trial."]}
        e = " | ".join(self.errs(ct=bad))
        self.assertIn("'Gavin'", e)
        self.assertIn("'Mercer'", e)

    def test_names_from_synopsis_ok(self):
        ok = {**self.ct, "why": ["Elias faces the nobles of the Royal Dragon Rider Academy with Alexstrasza on his side."]}
        self.assertEqual([x for x in self.errs(ct=ok) if x.startswith("why")], [])

    def test_lengths_and_homepage_source(self):
        seo = {**self.seo, "title": "x" * 61, "description": "y" * 156, "sources": {"episodes": "https://netshort.com/", "app": None}}
        e = " | ".join(self.errs(seo=seo))
        self.assertIn("seo.title dài 61", e)
        self.assertIn("seo.description dài 156", e)
        self.assertIn("không phải trang chủ", e)

    def test_merge_keeps_handwritten(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.seo.json"
            p.write_text(json.dumps({"title": "Hand Title", "sources": {"episodes": None, "app": None}}), encoding="utf-8")
            out, added = nf.merge_missing(p, self.seo)
            self.assertEqual(out["title"], "Hand Title")
            self.assertIn("keywords", added)
            self.assertEqual(out["sources"]["episodes"], SPEC["sources"]["episodes"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
