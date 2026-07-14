# Publishing a New Article

Use this workflow to add an article, preview it locally, and publish it to [blog.npanda.online](https://blog.npanda.online/).

## 1. Prepare the Repository

Create a focused branch from the latest `main`:

```sh
git switch main
git pull --ff-only
git switch -c docs/article-topic
```

Create the Python environment once. Python 3.12 matches CI:

```sh
python -m venv .venv
```

Activate it on PowerShell and install the pinned dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 2. Create the Article

Add `docs/<article-slug>.md`. Use lowercase kebab-case, for example `docs/eks-private-cluster.md`. Store repository-owned images under `docs/assets/<article-slug>/` and reference them with relative paths.

Start from this structure and remove sections that do not apply:

````markdown
# Clear, Outcome-Focused Article Title

A short introduction explaining the problem, audience, and result.

## What You Will Build

Describe the outcome and include an architecture diagram when useful.

## Prerequisites

- Required tools and tested versions
- Access, permissions, and infrastructure assumptions

## Implementation

Explain each step and why it is needed.

```yaml
# Use realistic, sanitized examples.
```

## Validation

Show commands and expected results.

## Security and Production Considerations

Call out credentials, permissions, resilience, cost, and scaling concerns.

## Troubleshooting

Document likely symptoms, causes, and fixes.

## Cleanup

Explain how to remove billable or temporary resources.

## Key Takeaways

Summarize the main decisions and lessons.
````

Never publish real tokens, account IDs, private endpoints, certificates, customer names, or other sensitive data. Use obvious placeholders such as `<AWS_ACCOUNT_ID>`.

## 3. Add It to Navigation

Edit `nav:` in `mkdocs.yml` and add the file under one appropriate category:

```yaml
- Kubernetes & EKS:
    - Private EKS Cluster: eks-private-cluster.md
```

Every article belongs in navigation. Add it to `docs/index.md` only if it is a featured guide. Add it to `README.md` only if it represents the repository’s strongest work; this avoids maintaining duplicate article catalogs.

## 4. Preview and Validate

Run the local server while writing:

```sh
python -m mkdocs serve
```

Before committing, run the same validation as CI:

```sh
python -m mkdocs build --strict
git diff --check
```

Check desktop and mobile layouts, headings, navigation, internal links, image alt text, code-block languages, spelling, and command output.

## 5. Publish

Commit with a short imperative subject and push the branch:

```sh
git add docs/<article-slug>.md mkdocs.yml
git commit -m "Add private EKS cluster guide"
git push -u origin docs/article-topic
```

Open a pull request describing the article, its audience, and the validation performed. Include screenshots when layout or diagrams changed. After the pull request is merged, GitHub Actions runs a strict build and deploys `main` to GitHub Pages. Confirm the article and navigation at the live site.

## Publication Checklist

- [ ] Filename is lowercase kebab-case.
- [ ] Title and introduction clearly state the outcome.
- [ ] Commands and versions were tested.
- [ ] Examples contain no sensitive information.
- [ ] Images have alt text and use stable paths.
- [ ] The article appears once in `mkdocs.yml` navigation.
- [ ] `python -m mkdocs build --strict` succeeds.
- [ ] The pull request explains scope and validation.
