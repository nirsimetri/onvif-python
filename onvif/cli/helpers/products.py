"""ONVIF products search helpers."""

import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from onvif.cli.utils import colorize


def search_products(search_term: str, page: int = 1, per_page: int = 20) -> None:
    """Search ONVIF products database and display results in table format with
    pagination.

    Args:
        search_term (str): Search term to match against model, post_title, and company_name fields
        page (int): Page number (1-based)
    """
    # Get the database path relative to the script location
    db_path = Path(__file__).resolve().parent.parent.parent / "db" / "products.db"

    if not os.path.exists(db_path):
        print(
            f"{colorize('Error:', 'red')} " f"Products database not found at {db_path}"
        )
        sys.exit(1)

    # Validate pagination parameters
    if page < 1:
        print(f"{colorize('Error:', 'red')} Page number must be 1 or greater")
        sys.exit(1)

    if per_page < 1 or per_page > 100:
        print(f"{colorize('Error:', 'red')} " "Per-page must be between 1 and 100")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_count, total_pages, results = _fetch_product_page(
            cursor,
            search_term,
            page,
            per_page,
        )

        if total_count == 0:
            print(
                f"{colorize('No products found matching:', 'yellow')} "
                f"{colorize(search_term, 'white')}"
            )
            return

        if page > total_pages:
            print(
                f"{colorize('Error:', 'red')} "
                f"Page {page} does not exist. Total pages: {total_pages}"
            )
            return

        offset = (page - 1) * per_page
        headers = [
            "ID",
            "Test Date",
            "Model",
            "Firmware",
            "Profiles",
            "Category",
            "Type",
            "Company",
        ]
        col_widths = _get_terminal_width(results, headers)

        print(
            f"\n{colorize(f'Found {total_count} product(s) matching:', 'green')} "
            f"{colorize(search_term, 'white')}"
        )
        print(
            f"Showing {colorize(f'{offset + 1}-{min(offset + per_page, total_count)}', 'cyan')} "
            f"of {colorize(f"{total_count} results", 'cyan')}"
        )
        print()

        _print_data_header(headers, col_widths)
        _print_data_rows(results, col_widths)
        _print_data_pagination(page, total_pages)

        conn.close()

    except sqlite3.Error as e:
        print(f"{colorize('Database error:', 'red')} {e}")
        sys.exit(1)
    except (AttributeError, ValueError, OSError) as e:
        print(f"{colorize('Error:', 'red')} {e}")
        sys.exit(1)


def _fetch_product_page(
    cursor: sqlite3.Cursor,
    search_term: str,
    page: int,
    per_page: int,
) -> tuple[int, int, list[Any]]:
    """Fetch one page of products."""
    search_pattern = f"%{search_term}%"

    count_query = """
        SELECT COUNT(*)
        FROM onvif_products
        WHERE LOWER(model) LIKE LOWER(?)
           OR LOWER(post_title) LIKE LOWER(?)
           OR LOWER(company_name) LIKE LOWER(?)
           OR LOWER(product_category) LIKE LOWER(?)
    """

    cursor.execute(count_query, (search_pattern,) * 4)
    total_count = cursor.fetchone()[0]

    total_pages = (total_count + per_page - 1) // per_page

    if total_count == 0:
        return 0, total_pages, []

    offset = (page - 1) * per_page

    query = """
        SELECT ID, test_date, post_title, product_firmware_version,
               product_profiles, product_category, type,
               company_name
        FROM onvif_products
        WHERE LOWER(model) LIKE LOWER(?)
           OR LOWER(post_title) LIKE LOWER(?)
           OR LOWER(company_name) LIKE LOWER(?)
           OR LOWER(product_category) LIKE LOWER(?)
        ORDER BY test_date DESC
        LIMIT ? OFFSET ?
    """

    cursor.execute(
        query,
        (search_pattern,) * 4 + (per_page, offset),
    )

    return total_count, total_pages, cursor.fetchall()


def _get_content_widths(
    results: list[Any],
    headers: list[str],
) -> list[int]:
    """Calculate actual content width for each column."""
    widths = [0] * len(headers)

    for row in results:
        for index, value in enumerate(row):
            if not value:
                continue

            value = str(value)
            if index == 1:
                value = _format_date_width(value)

            widths[index] = max(widths[index], len(value))

    return widths


def _truncate_columns(
    col_widths: list[int],
    min_widths: list[int],
    headers: list[str],
    terminal_width: int,
    separator_space: int,
) -> list[int]:
    """Truncate columns proportionally to fit the terminal."""
    available_width = terminal_width - separator_space
    protected_width = sum(col_widths[i] for i in (0, 1))
    remaining_width = available_width - protected_width

    truncatable = [i for i in range(len(headers)) if i not in (0, 1)]

    if remaining_width <= 0 or not truncatable:
        return col_widths

    current_width = sum(col_widths[i] for i in truncatable)

    for index in truncatable:
        if current_width > 0:
            proportion = col_widths[index] / current_width
            new_width = int(remaining_width * proportion)
            col_widths[index] = max(new_width, min_widths[index])
        else:
            col_widths[index] = min_widths[index]

    return col_widths


def _get_terminal_width(
    results: list[Any],
    headers: list[str],
) -> list[int]:
    """Get terminal width for adaptive formatting."""
    try:
        terminal_width = shutil.get_terminal_size().columns
    except (AttributeError, ValueError, OSError):
        terminal_width = 120

    min_widths = [max(len(header), 8) for header in headers]
    content_widths = _get_content_widths(results, headers)
    col_widths = [max(min_widths[i], content_widths[i]) for i in range(len(headers))]

    separator_space = (len(headers) - 1) * 3
    total_width = sum(col_widths) + separator_space

    if total_width <= terminal_width:
        return col_widths

    return _truncate_columns(
        col_widths,
        min_widths,
        headers,
        terminal_width,
        separator_space,
    )


def _format_date_width(value: str) -> str:
    """Return the date value in display format."""
    if "T" not in value:
        return value

    date_part, time_part = value.split("T", maxsplit=1)
    time_part = time_part.split(".", maxsplit=1)[0]
    time_part = time_part.split("+", maxsplit=1)[0]
    time_part = time_part.replace("Z", "")

    return f"{date_part} {time_part}"


def _print_data_header(headers: list[str], col_widths: list[int]) -> None:
    """Print table header"""
    header_line = " | ".join(
        header.ljust(col_widths[i]) for i, header in enumerate(headers)
    )
    print(colorize(header_line, "yellow"))
    print(colorize("-" * len(header_line), "white"))


# pylint: disable=too-many-branches,too-many-nested-blocks
def _print_data_rows(results: list[Any], col_widths: list[int]) -> None:
    """Print data table rows"""
    for row in results:
        formatted_row = []
        for i, value in enumerate(row):
            if value is None:
                formatted_value = ""
            else:
                str_value = str(value)

                # Special formatting for date column (index 1)
                if i == 1 and value:  # Date column
                    try:
                        # Handle ISO format with timezone
                        if "T" in str_value:
                            # Parse ISO format: 2024-08-15T17:53:12.9154121+08:00
                            # Extract just the date and time part before timezone
                            date_part = str_value.split("T", maxsplit=1)[0]
                            time_part = str_value.split("T")[1].split(".")[
                                0
                            ]  # Remove microseconds
                            if "+" in time_part:
                                time_part = time_part.split("+")[0]
                            elif "Z" in time_part:
                                time_part = time_part.replace("Z", "")
                            formatted_value = f"{date_part} {time_part}"
                        elif (
                            len(str_value) == 19 and " " in str_value
                        ):  # Already in correct format
                            formatted_value = str_value
                        elif len(str_value) == 10:  # Just date, add time
                            formatted_value = f"{str_value} 00:00:00"
                        else:
                            # Try to parse common formats
                            try:
                                parsed_date = datetime.strptime(
                                    str_value, "%Y-%m-%d %H:%M:%S"
                                ).astimezone()
                                formatted_value = parsed_date.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            except ValueError:
                                try:
                                    parsed_date = datetime.strptime(
                                        str_value, "%Y-%m-%d"
                                    ).astimezone()
                                    formatted_value = parsed_date.strftime(
                                        "%Y-%m-%d 00:00:00"
                                    )
                                except ValueError:
                                    formatted_value = (
                                        str_value  # Keep original if parsing fails
                                    )
                    except (KeyError, ValueError, IndexError):
                        formatted_value = str_value  # Keep original if any error
                else:
                    # Apply truncation based on calculated column width
                    max_width = col_widths[i]
                    if len(str_value) > max_width:
                        formatted_value = str_value[: max_width - 3] + "..."
                    else:
                        formatted_value = str_value

            formatted_row.append(formatted_value.ljust(col_widths[i]))

        print(" | ".join(formatted_row))


def _print_data_pagination(page: int, total_pages: int) -> None:
    """Print pagination information"""
    print()
    newline = "\n" if total_pages == 1 else ""
    print(f"{colorize(f'Page {page} of {total_pages}', 'cyan')} {newline}")

    # Show navigation hints
    nav_hints = []
    if page > 1:
        nav_hints.append(f"Previous: --page {page - 1}")
    if page < total_pages:
        nav_hints.append(f"Next: --page {page + 1}")

    if nav_hints:
        print(f"{colorize('Navigation:', 'white')} {' | '.join(nav_hints)}\n")
