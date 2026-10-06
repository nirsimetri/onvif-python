"""ONVIF Interactive Shell context."""

from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from onvif.client import ONVIFClient


@dataclass
class ShellContext:  # pylint: disable=too-many-instance-attributes
    """Store shared state for the interactive shell."""

    UNSET = object()

    client: ONVIFClient
    args: Namespace

    current_service: object | None = None
    current_service_name: str | None = None
    stored_data: dict[str, Any] = field(
        default_factory=dict
    )  # For storing command results
    stored_metadata: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )  # For storing metadata about stored data (service, method

    last_result: Any = field(default=UNSET, repr=False)
    last_method: str | None = None
    last_service_name: str | None = None
    last_operation_timestamp: datetime | None = None

    base_commands: list[str] = field(
        default_factory=lambda: [
            "capabilities",
            "caps",
            "services",
            "help",
            "exit",
            "store",
            "rm",
            "show",
            "cls",
            "clear",
            "info",
            "debug",
            "ls",
            "cd",
            "shortcuts",
            "desc",
            "type",
        ]
    )

    device_info_text: str | None = None
