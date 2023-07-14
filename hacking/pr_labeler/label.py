from __future__ import annotations

from pathlib import Path

import github
import github.PullRequest
import typer
from codeowners import OwnerTuple, CodeOwners

OWNER = "gotmax23-2"
REPO = "ansible-documentation"
LABELS: dict[OwnerTuple, list[str]] = {
    ("TEAM", "@ansible/steering-committee"): ["sc_approval"],
}
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CODEOWNERS = (ROOT / ".github/CODEOWNERS").read_text("utf-8")


def handle_codeowner_labels(pr: github.PullRequest.PullRequest) -> None:
    labels = LABELS.copy()
    owners = CodeOwners(CODEOWNERS)
    files = pr.get_files()
    for file in files:
        for owner in owners.of(file.filename):
            print("file", file.filename)
            if labels_to_add := labels.pop(owner, None):
                print("Adding labels to", f"{pr.id}:", *map(repr, labels_to_add))
                # pr.add_to_labels(*labels_to_add)
        if not labels:
            return


APP = typer.Typer()


@APP.command()
def main(pr_number: int):
    gclient = github.Github()
    repo = gclient.get_repo(f"{OWNER}/{REPO}")
    pr = repo.get_pull(pr_number)
    if pr.state != "open":
        print("Refusing to process closed ticket")
        return
    handle_codeowner_labels(pr)


if __name__ == "__main__":
    APP()
