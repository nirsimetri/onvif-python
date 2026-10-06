"""Service commands implementation."""

from __future__ import annotations

import cmd
import textwrap
import traceback
from datetime import datetime
from typing import Callable

from requests.exceptions import RequestException
from zeep.exceptions import Fault, TransportError

from onvif.cli.helpers import (
    get_method_documentation,
    get_operation_type_info,
)
from onvif.cli.utils import (
    colorize,
    get_service_methods,
    parse_json_params,
)
from onvif.utils.exceptions import ONVIFOperationException

from .context import ShellContext


class ServiceCommands(cmd.Cmd):
    """Provide ONVIF service commands."""

    context: ShellContext
    _substitute_stored_references: Callable[[str], str]
    _handle_connection_error: Callable[..., None]
    _split_multi_commands: Callable[[str], list]

    def execute_service_method(self, method_name: str, params_str: str) -> None:
        """Execute a method on the current service."""
        if not self.context.current_service:
            print(f"{colorize('Error:', 'red')} Not in service mode")
            return

        try:
            method = getattr(self.context.current_service, method_name)
        except AttributeError:
            print(
                f"{colorize('Error:', 'red')} Unknown method "
                f"'{method_name}' for service '{self.context.current_service_name}'"
            )
            available_methods = get_service_methods(self.context.current_service)
            print(
                f"{colorize('Available methods:', 'yellow')} {', '.join(available_methods[:5])}"
            )
            if len(available_methods) > 5:
                print(
                    f"Type {colorize('ls', 'cyan')} or press "
                    f"{colorize('<TAB>', 'yellow')} to see all available methods"
                )
            return

        try:
            # Substitute stored data references before parsing
            if params_str and "$" in params_str:
                params_str = self._substitute_stored_references(params_str)

            params = parse_json_params(params_str) if params_str else {}
            result = method(**params)

            self.context.last_result = result
            self.context.last_method = method_name  # Store method name for metadata
            self.context.last_service_name = (
                self.context.current_service_name
            )  # Store service name
            self.context.last_operation_timestamp = datetime.now()
            print(str(result))

        except (ONVIFOperationException, ValueError, TypeError) as e:
            # Check if it's a connection error (must be wrapped in ONVIFOperationException)
            if isinstance(e, ONVIFOperationException) and isinstance(
                e.original_exception, (RequestException, TransportError)
            ):
                self._handle_connection_error()
            else:
                # For all other errors (SOAP faults, TypeErrors, etc.),
                # just print and continue.
                print(f"{colorize('Error:', 'red')} {e}")
                if self.context.args.debug:
                    # In debug mode, show traceback for unexpected errors, but not for
                    # common user errors like SOAP faults or missing arguments (TypeError).
                    is_soap_fault = isinstance(
                        e, ONVIFOperationException
                    ) and isinstance(e.original_exception, Fault)
                    if not is_soap_fault and not isinstance(e, TypeError):
                        traceback.print_exc()

    def do_desc(self, line) -> None:
        """Describes a method from its WSDL documentation.

        Usage: desc <method_name>
        """
        method_name = line.strip()

        if not self.context.current_service:
            print(
                f"{colorize('Error:', 'red')} You must be in a service mode to use 'desc'."
            )
            print(f"Enter a service first (e.g., {colorize('devicemgmt', 'yellow')})")
            return

        if not method_name:
            print("Usage: desc <method_name>")
            return

        if not hasattr(self.context.current_service, method_name):
            print(
                f"{colorize('Error:', 'red')} Method '{method_name}' "
                f"not found in service '{self.context.current_service_name}'."
            )
            print(f"Use {colorize('ls', 'yellow')} to see available methods.")
            return

        doc_info = get_method_documentation(self.context.current_service, method_name)

        if doc_info:
            print(
                f"\n{colorize('Description for', 'yellow')} "
                f"{self.context.current_service_name}.{method_name}():"
            )
            doc_parts = doc_info["doc"].split("\n")
            for part in doc_parts:
                wrapped_doc = textwrap.fill(
                    part, width=100, initial_indent="  ", subsequent_indent="  "
                )
                print(colorize(wrapped_doc, "white"))

            if doc_info["required"]:
                print(f"\n{colorize('Required Arguments:', 'green')}")
                for arg in doc_info["required"]:
                    print(f"  - {arg}")

            if doc_info["optional"]:
                print(f"\n{colorize('Optional Arguments:', 'cyan')}")
                for arg in doc_info["optional"]:
                    print(f"  - {arg}")
            print()  # Add a newline for better spacing
        else:
            print(
                f"No documentation or parameter info found for method '{method_name}'."
            )

    # pylint: disable=too-many-branches,too-many-statements
    def do_type(self, line) -> None:
        """Show input and output types for a method.

        Usage: type <method_name>
        """
        method_name = line.strip()

        if not self.context.current_service:
            print(
                f"{colorize('Error:', 'red')} You must be in a service mode to use 'type'."
            )
            print(f"Enter a service first (e.g., {colorize('devicemgmt', 'yellow')})")
            return

        if not method_name:
            print("Usage: type <method_name>")
            return

        if not hasattr(self.context.current_service, method_name):
            print(
                f"{colorize('Error:', 'red')} Method '{method_name}' "
                f"not found in service '{self.context.current_service_name}'."
            )
            print(f"Use {colorize('ls', 'yellow')} to see available methods.")
            return

        type_info = get_operation_type_info(self.context.current_service, method_name)

        if type_info:
            # Helper function to display parameters recursively with tree-style indentation
            # pylint: disable=too-many-locals,too-many-branches
            def display_params(params, prefix_lines=None, is_root_level=False):
                """Display parameters with tree-style formatting.

                Args:
                    params: List of parameter dictionaries
                    prefix_lines: List of strings representing the tree prefix for each line
                    is_root_level: If True, don't show tree characters at this level
                """
                if prefix_lines is None:
                    prefix_lines = []

                for idx, param in enumerate(params):
                    is_last = idx == len(params) - 1

                    # Determine tree characters (only if not root level)
                    if is_root_level:
                        tree_branch = ""
                        tree_continue = ""
                    else:
                        if is_last:
                            tree_branch = "└── "
                            tree_continue = "    "
                        else:
                            tree_branch = "├── "
                            tree_continue = "│   "

                    # Determine prefix symbol: + for attributes, - for elements
                    prefix_symbol = "+" if param.get("is_attribute", False) else "-"

                    # Format occurrences based on type
                    occurs = ""
                    if param.get("is_attribute", False):
                        # For attributes: only show "required" if use="required"
                        # Default for attributes is optional (no label needed)
                        if param["minOccurs"] == "1":  # This means use="required"
                            occurs = f" - {colorize('required', 'yellow')}"
                        # If minOccurs == "0", it's optional (default), so no label
                    else:
                        # For elements: show unbounded, optional, or required
                        if param["maxOccurs"] == "unbounded":
                            occurs = f" - {colorize('unbounded', 'magenta')}"
                        elif param["minOccurs"] == "0":
                            occurs = f" - {colorize('optional', 'green')}"
                        else:
                            occurs = f" - {colorize('required', 'yellow')}"

                    # Format type
                    type_str = f"[{param['type']}]" if param["type"] else ""

                    # Build the current line prefix from all previous levels
                    current_prefix = "".join(prefix_lines)

                    # Add spacing for root level items
                    if is_root_level:
                        current_prefix = "  "

                    # Display parameter name with tree structure, prefix, occurrence, and type
                    # Only add semicolon separator if there's an occurrence label
                    separator = ";" if occurs else ""
                    param_line = (
                        f"{current_prefix}{tree_branch}{prefix_symbol}{colorize(param['name'], 'white')}"
                        f"{occurs}{separator} {colorize(type_str, 'cyan')}"
                    )
                    print(param_line)

                    # Display documentation if available
                    if param.get("documentation"):
                        doc_lines = param["documentation"].split("\n")
                        for doc_line in doc_lines:
                            if doc_line.strip():
                                # Add tree continuation for documentation
                                if is_root_level:
                                    doc_prefix = "  "
                                else:
                                    doc_prefix = current_prefix + tree_continue
                                wrapped_doc = textwrap.fill(
                                    doc_line.strip(),
                                    width=96,  # Slightly less to account for tree chars
                                    initial_indent=doc_prefix + "  ",
                                    subsequent_indent=doc_prefix + "  ",
                                )
                                print(colorize(wrapped_doc, "reset"))

                    # Display children recursively with updated prefix
                    if param.get("children"):
                        if is_root_level:
                            # Start tree structure from children
                            new_prefix_lines = ["  "]
                        else:
                            new_prefix_lines = prefix_lines + [tree_continue]
                        display_params(
                            param["children"], new_prefix_lines, is_root_level=False
                        )

            input_msg = type_info["input"]
            # Display Input
            if input_msg is not None:
                print(f"\n{colorize('Input:', 'cyan')}")
                msg_name = f"[{input_msg['name']}]"
                print(f"{colorize(msg_name, 'yellow')}")

                if input_msg["parameters"]:
                    display_params(input_msg["parameters"], is_root_level=True)
                else:
                    print(f"  {colorize('(no parameters)', 'reset')}")
            else:
                print(
                    f"\n{colorize('Input:', 'cyan')} {colorize('(not defined)', 'reset')}"
                )

            output_msg = type_info["output"]
            # Display Output
            if output_msg is not None:
                print(f"\n{colorize('Output:', 'cyan')}")
                msg_name = f"[{output_msg['name']}]"
                print(f"{colorize(msg_name, 'yellow')}")

                if output_msg["parameters"]:
                    display_params(output_msg["parameters"], is_root_level=True)
                else:
                    print(f"  {colorize('(no parameters)', 'reset')}")
            else:
                print(
                    f"\n{colorize('Output:', 'cyan')} {colorize('(not defined)', 'reset')}"
                )

            print()  # Add newline for spacing
        else:
            print(
                f"{colorize('Error:', 'red')} "
                f"Could not retrieve type information for '{method_name}'."
            )

    def complete_desc(self, text, _line, _begidx, _endidx) -> list:
        """Autocomplete method names for desc command."""
        if not self.context.current_service:
            return []
        methods = get_service_methods(self.context.current_service)
        return [m for m in methods if m.lower().startswith(text.lower())]

    def complete_type(self, text, _line, _begidx, _endidx) -> list:
        """Autocomplete method names for type command."""
        if not self.context.current_service:
            return []
        methods = get_service_methods(self.context.current_service)
        return [m for m in methods if m.lower().startswith(text.lower())]
