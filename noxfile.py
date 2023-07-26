from pathlib import Path

import nox

LINT_FILES = ("hacking/pr_labeler/label.py", "noxfile.py")
nox.options.sessions = ("lint",)


def install(session: nox.Session, *args, req: str, **kwargs):
    session.install(
        *args,
        "-r",
        f"requirements/{req}.in",
        "-c",
        f"requirements/{req}.txt",
        *args,
        **kwargs,
    )


@nox.session
def ruff(session: nox.Session):
    install(session, req="ruff")
    session.run("ruff", *LINT_FILES, *session.posargs)


@nox.session
def formatters(session: nox.Session):
    install(session, req="formatters")
    session.run("isort", *session.posargs, *LINT_FILES)
    session.run("black", *session.posargs, *LINT_FILES)


@nox.session
def formatters_check(session: nox.Session):
    install(session, req="formatters")
    session.run("isort", *session.posargs, "--check", *LINT_FILES)
    session.run("black", *session.posargs, "--check", *LINT_FILES)


@nox.session
def typing(session: nox.Session):
    install(session, req="typing")
    session.run("mypy", *session.posargs, *LINT_FILES)


@nox.session
def lint(session: nox.Session):
    session.notify("ruff")
    session.notify("formatters")


@nox.session(name="pip-compile", python=["3.9"])
@nox.parametrize(
    ["req"],
    [path.name.replace(".in", "") for path in Path("requirements").glob("*in")],
)
def pip_compile(session: nox.Session, req: str):
    session.install("pip-tools")
    # fmt: off
    session.run(
        "pip-compile",
        "--resolver", "backtracking",
        "--upgrade",
        "--allow-unsafe",
        "--quiet",
        "--strip-extras",
        "-o", f"requirements/{req}.txt",
        f"requirements/{req}.in",
    )
    # fmt: on
