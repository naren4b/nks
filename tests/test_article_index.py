import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location('article_index', Path(__file__).parents[1] / 'hooks/article_index.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

class ArticleIndexTests(unittest.TestCase):
    def test_order_categories_and_membership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, body in {'old': '# Old\n\nPublished: 2026-09-30\n\nOlder summary.', 'new': '# New\n\nPublished: 2026-10-03\n\nNew summary.', 'guide': '# Guide\n\nUndated.', 'hidden': '# Hidden\n\nPublished: 2026-10-04'}.items():
                (root / (name + '.md')).write_text(body)
            config = {'docs_dir': directory, 'nav': [{'AI & Automation': [{'Old': 'old.md'}, {'New': 'new.md'}, {'Guide': 'guide.md'}, {'Duplicate': 'new.md'}]}]}
            entries = hook.collect(config)
            self.assertEqual([a['path'] for a in entries], ['new.md', 'old.md', 'guide.md'])
            self.assertEqual(entries[0]['category'], 'AI & Automation')
            self.assertEqual(entries[0]['summary'], 'New summary.')
            self.assertIsNone(entries[-1]['date'])
            page = SimpleNamespace(file=SimpleNamespace(src_uri='articles.md'))
            result = hook.on_page_markdown('<!-- articles-chronological -->', page=page, config=config, files=None)
            self.assertLess(result.index('[New]'), result.index('[Old]'))
            self.assertIn('## More Guides', result)
            self.assertNotIn('Hidden', result)

    def test_invalid_date_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'bad.md').write_text('# Bad\n\nPublished: 2026-02-30')
            with self.assertRaises(ValueError):
                hook.collect({'docs_dir': directory, 'nav': [{'Bad': 'bad.md'}]})

    def test_home_shows_latest_five(self):
        with tempfile.TemporaryDirectory() as directory:
            nav = []
            for day in range(1, 8):
                path = f'post-{day}.md'
                (Path(directory) / path).write_text(f'# Post {day}\n\nPublished: 2026-10-{day:02}\n\nSummary.')
                nav.append({f'Post {day}': path})
            page = SimpleNamespace(file=SimpleNamespace(src_uri='index.md'))
            result = hook.on_page_markdown('<!-- recent-articles -->', page=page, config={'docs_dir': directory, 'nav': nav}, files=None)
            self.assertEqual(result.count('### '), 5)
            self.assertLess(result.index('[Post 7]'), result.index('[Post 6]'))
            self.assertNotIn('[Post 2]', result)

if __name__ == '__main__':
    unittest.main()
