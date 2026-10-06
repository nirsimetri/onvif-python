"""ONVIF Interactive Shell utilities."""

from __future__ import annotations

import os
import shutil
import socket
import ssl
import sys
import threading
import traceback

from onvif.cli.utils import (
    colorize,
    get_device_available_services,
    get_service_methods,
)

from .context import ShellContext


class ShellUtilities:
    """Provide interactive shell utilities."""

    context: ShellContext
    prompt: str
    stop_health_check: threading.Event
    health_check_thread: threading.Thread

    def _initialize_health_check(self) -> None:
        """Initialize the background health check."""
        self.stop_health_check = threading.Event()
        self.health_check_thread = threading.Thread(
            target=self._periodic_health_check, daemon=True
        )

    def update_prompt(self) -> None:
        """Update command prompt based on current context."""
        if self.context.current_service_name:
            self.prompt = (
                f"{self.context.args.username}@{self.context.args.host}"
                f":{self.context.args.port}"
                f"/{self.context.current_service_name} > "
            )
        else:
            self.prompt = (
                f"{self.context.args.username}@{self.context.args.host}"
                f":{self.context.args.port} > "
            )

    # pylint: disable=too-many-locals
    def _display_grid(self, items: list):
        """Display items in grid format matching TAB completion (vertical layout)"""
        if not items:
            return

        # Get device services for coloring (only in root mode)
        services = (
            get_device_available_services(self.context.client)
            if not self.context.current_service
            else []
        )

        # Calculate terminal width
        try:
            term_width = shutil.get_terminal_size().columns
        except (KeyError, ValueError, RuntimeError):
            term_width = 80

        # Find the longest item length
        longest_length = max(len(item) for item in items)

        # Column width calculation: use same algorithm as cmd.Cmd.columnize()
        # Python's columnize uses: maxlen + 2 if maxlen > 0 else 2
        col_width = longest_length + 2 if longest_length > 0 else 2

        # Calculate number of columns that fit
        num_cols = max(1, term_width // col_width)

        # Calculate number of rows needed
        num_rows = (len(items) + num_cols - 1) // num_cols

        # Display items in VERTICAL layout (column by column, like TAB completion)
        for row_idx in range(num_rows):
            row_items = []
            for col_idx in range(num_cols):
                # Calculate index in vertical order
                item_idx = col_idx * num_rows + row_idx

                if item_idx < len(items):
                    item = items[item_idx]

                    # Apply coloring
                    if item in services:
                        colored_item = colorize(item, "cyan")
                    else:
                        colored_item = item

                    # Calculate padding: align to column width
                    # Use ljust-style padding for consistency with cmd.Cmd
                    padding = col_width - len(item)
                    formatted_item = colored_item + " " * padding
                    row_items.append(formatted_item)

            if row_items:
                # Join and rstrip to remove trailing spaces
                line = "".join(row_items).rstrip()
                print(line)

    def columnize(self, list, _displaywidth=80):  # pylint: disable=redefined-builtin
        """Override columnize to use grid format for TAB completion."""
        if not list:
            return

        # Use our grid display for TAB completion with coloring enabled
        self._display_grid(list)

    def print_topics(self, header, cmds, _cmdlen, _maxcol):
        """Override print_topics to use grid format for TAB completion."""
        if not cmds:
            return

        # Print without header if it's empty or whitespace
        if header.strip():
            print(f"{header}\n")

        # Use our grid display for TAB completion with coloring enabled
        self._display_grid(cmds)

    def get_suggestions(self, partial_cmd: str) -> list[str]:
        """Get command suggestions based on partial input."""
        suggestions = []

        if self.context.current_service:
            # In service mode - suggest methods
            methods = get_service_methods(self.context.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            for method in methods:
                if method.lower().startswith(partial_cmd.lower()):
                    suggestions.append(method)
        else:
            # In root mode - suggest device-specific services and commands
            services = get_device_available_services(
                self.context.client
            )  # Use device-specific services
            commands = self.context.base_commands

            for service in services:
                if service.lower().startswith(partial_cmd.lower()):
                    suggestions.append(colorize(service, "cyan"))

            for cmd_base in commands:
                if cmd_base.lower().startswith(partial_cmd.lower()):
                    suggestions.append(cmd_base)

        return suggestions[:5]  # Limit to 5 suggestions

    def completenames(self, text: str, *_ignored):
        """Override completenames for tab completion from command names."""
        if self.context.current_service:
            # Complete method names in service mode
            methods = get_service_methods(self.context.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            completions = [
                method for method in methods if method.lower().startswith(text.lower())
            ]
        else:
            # Complete device-specific service names and basic commands in root mode
            services = get_device_available_services(
                self.context.client
            )  # Use device-specific services
            commands = self.context.base_commands
            all_completions = services + commands
            completions = [
                cmd for cmd in all_completions if cmd.lower().startswith(text.lower())
            ]

        return completions

    def _periodic_health_check(self) -> None:
        """Periodically checks device connection using TCP or TLS depending on mode."""
        # Get health check interval from args, default to 10 seconds
        health_check_interval = getattr(self.context.args, "health_check_interval", 10)

        # Wait before first check to allow intro to finish
        self.stop_health_check.wait(health_check_interval)

        while not self.stop_health_check.is_set():
            sock: socket.socket | None = None
            try:
                # For HTTPS, use ssl.create_connection for proper TLS handling
                if getattr(self.context.args, "https", False):
                    context = ssl.create_default_context()
                    context.minimum_version = ssl.TLSVersion.TLSv1_2
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    # Use ssl.create_connection instead of wrapping existing socket
                    sock = context.wrap_socket(
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                        server_hostname=self.context.args.host,
                    )
                    sock.settimeout(5.0)
                    sock.connect((self.context.args.host, self.context.args.port))
                else:
                    # For HTTP, simple TCP connection check
                    sock = socket.create_connection(
                        (self.context.args.host, self.context.args.port), timeout=5.0
                    )

                # Connection successful
            except (
                socket.timeout,
                ConnectionRefusedError,
                socket.gaierror,
                ssl.SSLError,
                ssl.SSLEOFError,
                OSError,
            ) as e:
                # Connection failed, trigger exit
                print(
                    f"\n{colorize('Connection to device lost.', 'red')}",
                    file=sys.stderr,
                )
                print(
                    f"{colorize('Error:', 'red')} Health check failed: {e}",
                    file=sys.stderr,
                )
                print(
                    colorize("Exiting ONVIF interactive shell...", "yellow"),
                    file=sys.stderr,
                )
                # Forcibly exit the entire process. This is necessary to interrupt
                # the blocking input() call in the main thread.
                os._exit(1)
            finally:
                # Ensure the socket is always closed
                if sock:
                    sock.close()

            # Wait before next check or stop signal
            self.stop_health_check.wait(health_check_interval)

    def _handle_connection_error(self) -> None:
        """Handle connection errors by notifying the user and exiting."""
        print(f"\n{colorize('Connection to device lost.', 'red')}", file=sys.stderr)
        # print(f"{colorize('Error:', 'red')} {e}", file=sys.stderr)
        if self.context.args.debug:
            traceback.print_exc()
        print(colorize("Exiting ONVIF interactive shell...", "yellow"), file=sys.stderr)
        print(colorize("Goodbye!", "cyan"), file=sys.stderr)
        sys.exit(1)

    def _split_multi_commands(self, s: str) -> list:
        """Split a command string by top-level '&&' separators while ignoring
        occurrences inside quotes or bracketed structures.

        Returns a list of command strings (trimmed).
        """
        parts = []
        buf = []
        i = 0
        length = len(s)
        depth = 0
        in_single = False
        in_double = False
        while i < length:
            ch = s[i]
            # Toggle quote states
            if ch == "'" and not in_double:
                in_single = not in_single
                buf.append(ch)
                i += 1
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                buf.append(ch)
                i += 1
                continue

            # Track bracket depth to avoid splitting inside {...} or [...]
            if not in_single and not in_double:
                if ch in "{[(":
                    depth += 1
                elif ch in "}])":
                    depth = max(0, depth - 1)

            # Detect top-level &&
            # pylint: disable=too-many-boolean-expressions
            if (
                not in_single
                and not in_double
                and depth == 0
                and ch == "&"
                and i + 1 < length
                and s[i + 1] == "&"
            ):
                # finish current buffer
                token = "".join(buf).strip()
                parts.append(token)
                buf = []
                i += 2
                # skip optional spaces after &&
                while i < length and s[i].isspace():
                    i += 1
                continue

            buf.append(ch)
            i += 1

        if buf:
            token = "".join(buf).strip()
            if token:
                parts.append(token)

        return parts
