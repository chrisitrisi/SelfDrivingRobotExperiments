"""Liest gemeinsame Projektregeln und ein Arbeitspaket mit der GitHub CLI."""

import argparse
import json
import subprocess
import sys

REPO = "chrisitrisi/SelfDrivingRobotExperiments"


def gh(*args):
    result = subprocess.run(
        ["gh", *args], capture_output=True, encoding="utf-8", check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "GitHub-Abfrage fehlgeschlagen")
    return result.stdout


def project_file(path):
    return gh("api", "-H", "Accept: application/vnd.github.raw+json",
              f"repos/{REPO}/contents/{path}?ref=master")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", type=int, help="GitHub-Issue-Nummer")
    args = parser.parse_args()
    if args.issue < 1:
        parser.error("Die Issue-Nummer muss positiv sein.")

    try:
        rules = project_file("AGENTS.md")
        interfaces = project_file("docs/schnittstellen.md")
        endpoint = f"repos/{REPO}/issues/{args.issue}"
        issue = json.loads(gh("api", endpoint))
        if "pull_request" in issue:
            raise RuntimeError("Diese Nummer gehört zu einem Pull Request.")
        pages = json.loads(gh("api", "--paginate", "--slurp",
                              f"{endpoint}/comments?per_page=100"))
    except FileNotFoundError:
        parser.exit(1, "GitHub CLI (gh) fehlt. Installiere sie und nutze gh auth login.\n")
    except (RuntimeError, ValueError) as error:
        parser.exit(1, f"Projektstart fehlgeschlagen: {error}\n")

    print(rules.strip(), interfaces.strip(), sep="\n\n")
    print(f"\n# Issue {args.issue} – {issue['title']}\n{issue['html_url']}\n")
    print(issue["body"] or "(keine Beschreibung)")
    for page in pages:
        for comment in page:
            author = (comment.get("user") or {}).get("login", "unbekannt")
            print(f"\n## {author} · {comment['created_at']}\n{comment['body']}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    main()
