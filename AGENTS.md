# Repository Guidelines

## Project Structure & Module Organization

This repository publishes the Naren Kubernetes Solutions documentation site with MkDocs Material. Authoritative articles live in `docs/` as individual Markdown files; use lowercase, descriptive, hyphenated names such as `basic-harbor-registry.md`. `docs/index.md` is the site landing page and article catalog. `mkdocs.yml` defines the theme, Markdown extensions, plugins, and site metadata. The root `README.md` provides a GitHub-facing overview, while `.github/workflows/ci.yaml` deploys the site. `docs/CNAME` preserves the custom domain in every deployment. Generated `site/` output must not be committed.

## Build, Test, and Development Commands

Follow `PUBLISHING.md` for the canonical environment setup and authoring workflow. Use `python -m mkdocs serve` for a live preview and `python -m mkdocs build --strict` for validation. Deployment is automatic after a successful push to `main`.

## Coding Style & Naming Conventions

Write concise Markdown with descriptive headings, short paragraphs, and fenced code blocks that specify a language (`yaml`, `sh`, or `python`). Keep command examples reproducible and explain placeholders. Use relative links for repository content and verify image paths from the rendered page. Follow the existing two-space YAML indentation in `mkdocs.yml`; do not use tabs. Name new articles in lowercase kebab-case and keep product names capitalized consistently (for example, Kubernetes, Argo CD, and GitLab).

## Testing Guidelines

There is no unit-test suite or coverage target. Treat a clean strict MkDocs build as the required validation. Preview changed pages locally and check headings, tables, admonitions, code highlighting, internal links, and mobile readability. Add every article to `mkdocs.yml`; update the homepage or README only when it should be featured.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `Add Harbor MCP entry to documentation index` and `Revise article dates`. Keep each commit focused and describe the content affected. Pull requests should summarize the documentation change, list validation performed, link relevant issues, and include screenshots for theme, layout, table, or image changes. Never commit credentials, tokens, private cluster addresses, or real certificate material; use clearly labeled placeholders instead.
