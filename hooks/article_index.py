"""Build article discovery from navigation and explicit publication dates."""
import datetime
from pathlib import Path
import re

EXCLUDED = {"index.md", "articles.md", "about.md", "career-journey.md"}


def nav_entries(items, category="Guides"):
    for item in items:
        if isinstance(item, str):
            yield None, item, category
        elif isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, list):
                    yield from nav_entries(value, label if category == "Guides" else category)
                elif isinstance(value, str):
                    yield label, value, category


def collect(config):
    root = Path(config["docs_dir"]).resolve()
    seen, articles = set(), []
    for label, relative, category in nav_entries(config["nav"]):
        if relative in seen or relative in EXCLUDED or not relative.endswith(".md"):
            continue
        seen.add(relative)
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        heading = re.search(r"^# (.+)$", source, re.M)
        title = heading.group(1) if heading else label or path.stem
        header = "\n".join(source.splitlines()[:15])
        dates = re.findall(r"^Published: (\d{4}-\d{2}-\d{2})(?:\s*·.*)?\s*$", header, re.M)
        if len(dates) > 1:
            raise ValueError(f"Multiple publication dates in {relative}")
        date = datetime.date.fromisoformat(dates[0]) if dates else None
        summary = ""
        for paragraph in source.split("\n\n"):
            paragraph = paragraph.strip()
            if paragraph and not paragraph.startswith(("#", "Published:", "<", "!", "|", chr(96) * 3, "- ", "[")):
                summary = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", paragraph)
                summary = " ".join(summary.split())
                if len(summary) > 200:
                    summary = summary[:200].rsplit(" ", 1)[0] + "…"
                break
        articles.append(dict(path=relative, title=title, category=category, date=date, summary=summary))
    return sorted(articles, key=lambda a: (-(a["date"].toordinal() if a["date"] else 0), a["title"].casefold()))


def title_link(article):
    title = article["title"].replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    return f'[{title}]({article["path"]})'


def dated_list(articles):
    return "\n\n".join(
        f'### {title_link(a)}\n\n**{a["date"]:%d %b %Y}** · {a["category"]}\n\n{a["summary"]}'
        for a in articles
    ) or "New articles will appear here when published."


def on_page_markdown(markdown, *, page, config, files):
    if page.file.src_uri not in {"index.md", "articles.md"}:
        return markdown
    articles = collect(config)
    dated = [a for a in articles if a["date"]]
    if page.file.src_uri == "index.md":
        return markdown.replace("<!-- recent-articles -->", dated_list(dated[:5]))
    older = [a for a in articles if not a["date"]]
    guides = "\n".join(f'- {title_link(a)} — {a["category"]}' for a in older)
    listing = dated_list(dated)
    if guides:
        listing += "\n\n## More Guides\n\nThese guides have no recorded publication date. Browse them by title or use the topic navigation.\n\n" + guides
    return markdown.replace("<!-- articles-chronological -->", listing)
