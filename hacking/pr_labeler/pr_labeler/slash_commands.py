# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Commands that can be run on tickets
"""

from __future__ import annotations

import dataclasses
import enum
import functools
from collections.abc import Callable, Collection, Sequence
from typing import TYPE_CHECKING, TypeVar

from .cli_context import IssueOrPrCtx

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeAlias


Callback: TypeAlias = "Callable[[SlashCommandCtx], None]"
ISSUE_COMMANDS: dict[str, Callback] = {}
PR_COMMANDS: dict[str, Callback] = {}


def _no_args(name: str, text: Sequence[str]):
    if not text:
        raise CommandError(
            name, f"extra arguments: {text!r} are not allowed with {name} command"
        )


class CommandError(Exception):
    __slots__ = ("command_name", "error")

    def __init__(self, command_name: str, error: str) -> None:
        self.command_name = command_name
        self.error = error
        super().__init__(f"{self.command_name}: {self.error}")


@dataclasses.dataclass
class SlashCommandCtx:
    command_name: str
    command_args: Sequence[str]
    labeler_ctx: IssueOrPrCtx


def register_callback(
    issue: bool,
    pull: bool,
    allow_args: bool = False,
    name: str | Collection[str] | None = None,
) -> Callable[[Callback], Callback]:
    def wrapper(func: Callback) -> Callback:
        if name is None:
            final_names = [func.__name__]
        elif isinstance(name, str):
            final_names = [name]
        else:
            final_names = list(name)

        @functools.wraps(func)
        def inner(ctx: SlashCommandCtx) -> None:
            if not allow_args and ctx.command_args:
                _no_args(final_name, ctx.command_args)
            return func(ctx)

        for final_name in final_names:
            if issue:
                ISSUE_COMMANDS[final_name] = inner
            if pull:
                PR_COMMANDS[final_name] = inner
        return inner

    return wrapper
