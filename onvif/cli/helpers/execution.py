"""ONVIF command execution helpers."""

import warnings
from typing import Any

from onvif.cli.utils import colorize, parse_json_params
from onvif.client import ONVIFClient


def execute_command(
    client: ONVIFClient,
    service_name: str,
    method_name: str,
    params_str: str | None = None,
) -> Any:
    """Execute a single ONVIF command.

    Args:
        client (ONVIFClient): ONVIFClient instance
        service_name (str): Selected service for command execution
        method_name (str): Method to execute by service
        params_str (str | None): Provided params for method execution

    Returns:
        The operation response printed in terminal
    """
    # Get service instance
    try:
        service = getattr(client, service_name.lower())()
    except AttributeError as e:
        raise ValueError(f"{colorize('Unknown service:', 'red')} {service_name}") from e

    # Get method
    try:
        method = getattr(service, method_name)
    except AttributeError as e:
        raise ValueError(
            f"{colorize('Unknown method', 'red')} '{method_name}' for service '{service_name}'"
        ) from e

    # Parse parameters
    params = parse_json_params(params_str) if params_str else {}

    # Execute method
    return method(**params)


def setup_warning_format():
    """Setup custom warning format to show clean, concise warnings."""

    def custom_warning_format(
        message, category, filename, lineno, line=None
    ):  # pylint: disable=unused-argument
        # Show only the warning message without file path and line number
        return f"{category.__name__}: {message}\n"

    warnings.formatwarning = custom_warning_format
