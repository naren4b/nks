# Repository Guidelines

This repository publishes **Naren Cloud Architecture Lab**, a static MkDocs Material site of hands-on cloud and platform engineering guides by Narendranath Panda.

- Live site: https://blog.npanda.online/
- GitHub: https://github.com/naren4b/nks
- Human publishing workflow: `PUBLISHING.md`

This is documentation, not an application. There is no app server, database, or unit-test suite.

## Project Structure

| Path | Purpose |
| --- | --- |
| `docs/` | Authoritative Markdown articles. One file per article. |
| `docs/index.md` | Homepage: career/portfolio narrative, not a full catalog. |
| `docs/images/` | Repository-owned images. Reference with relative paths such as `./images/name.jpg`. |
| `docs/linux/` | Published Linux and Talos runbooks. Keep them in `nav:` under Linux & Talos. |
| `docs/CNAME` | Custom domain `blog.npanda.online`. Do not move, rename, or delete. |
| `mkdocs.yml` | Site metadata, theme, plugins, and **the published article catalog**. |
| `requirements.txt` | Pinned `mkdocs-material==9.6.14`. |
| `.github/workflows/ci.yaml` | Python 3.12 strict build on PRs; `mkdocs gh-deploy --force` on push to `main`. |
| `site/` | Generated output. Gitignored. Never commit. |

Root scratch files such as `chat.txt` and `provenece.json` are not site content. Do not link them from the docs.

## Commands

Python 3.12 matches CI. Create the venv once, then:

```sh
python -m pip install -r requirements.txt
python -m mkdocs serve                 # live preview, typically http://127.0.0.1:8000
python -m mkdocs build --strict        # required validation (same as CI)
git diff --check
```

After a merge to `main`, GitHub Actions deploys automatically. Confirm the article and navigation on the live site. Do not run `mkdocs gh-deploy` locally unless explicitly asked.

## Adding or Changing Articles

Follow `PUBLISHING.md`. Required steps:

1. Create `docs/<article-slug>.md` using lowercase kebab-case.
2. Add the article **once** under the matching `nav:` category in `mkdocs.yml`.
3. Add it to `docs/index.md` only if it is a featured guide.
4. Add it to `README.md` only if it is among the repository’s strongest work.
5. Run `python -m mkdocs build --strict` before considering the work done.

Do not create a parallel catalog. Navigation in `mkdocs.yml` is the source of truth.

Current `nav:` categories: Home, Career Progression, Linux & Talos, AWS Solutions Architecture, SRE & Observability, Kubernetes & Cloud Native, Platform Engineering & GitOps, Security & Registries, Data & Messaging, AI & Automation, About.

New AWS articles should map decisions to Well-Architected pillars (see `docs/aws-architecture.md`).

## Markdown Conventions

- Start with one `#` title and a short outcome-focused introduction.
- Use the section template in `PUBLISHING.md` for **new** articles. Do not rewrite older lab-note articles into that template unless asked.
- Fenced code blocks must declare a language (`yaml`, `sh`, `bash`, `python`).
- Keep command examples reproducible. Explain placeholders.
- Use relative links between articles (`career-journey.md`, not `/career-journey/`).
- Images need descriptive alt text. Prefer files under `docs/images/` with relative paths. Existing GitHub CDN image URLs may stay; do not convert them unless asked.
- Two-space indentation in YAML. No tabs.
- Articles do not use YAML frontmatter.
- Material admonitions (`!!! note`, `!!! warning`) are enabled but unused; use them only when they add signal.
- Capitalize product names consistently: Kubernetes, Argo CD, GitLab, Harbor, Terraform, OpenTofu, Terragrunt, Amazon EKS.

Voice: first person on `about.md`, `career-journey.md`, and `index.md`. Elsewhere, write as practical implementation guides. Do not add LinkedIn-style hashtags or emoji-heavy titles on new work.

## Validation

Treat a clean strict MkDocs build as the required check. `--strict` fails on missing files and broken internal links, so every `nav:` entry and in-article relative link must resolve.

Also check headings, tables, code highlighting, image paths from the rendered page, and that the article appears in the correct nav section.

## Git and Pull Requests

This project lives on GitHub (`naren4b/nks`), not GitLab.

- Branch from latest `main` as `docs/<article-topic>`.
- Commit with a short imperative subject describing the content affected, for example `Add Harbor MCP entry to documentation index`.
- Keep commits focused. Do not mix article work with unrelated CI or branding changes.
- Pull requests should summarize the change, audience, and validation (`mkdocs build --strict`). Include screenshots when theme, layout, tables, or images change.

## Security

Never commit credentials, tokens, private cluster addresses, customer names, real certificates, or kubeconfigs. Use obvious placeholders such as `<AWS_ACCOUNT_ID>` and `registry.example.com`. Do not copy values from local clusters into articles.

Ignore Windows `*:Zone.Identifier` files (already in `.gitignore`). Do not add them.
