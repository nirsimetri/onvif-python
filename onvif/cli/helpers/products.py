"""ONVIF products search helpers."""

import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

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
        print(f"{colorize('Error:', 'red')} Products database not found at {db_path}")
        sys.exit(1)

    # Validate pagination parameters
    if page < 1:
        print(f"{colorize('Error:', 'red')} Page number must be 1 or greater")
        sys.exit(1)

    if per_page < 1 or per_page > 100:
        print(f"{colorize('Error:', 'red')} Per-page must be between 1 and 100")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # First, get total count for pagination info
        count_query = """
        SELECT COUNT(*)
        FROM onvif_products
        WHERE LOWER(model) LIKE LOWER(?)
           OR LOWER(post_title) LIKE LOWER(?)
           OR LOWER(company_name) LIKE LOWER(?)
           OR LOWER(product_category) LIKE LOWER(?)
        """

        search_pattern = f"%{search_term}%"
        cursor.execute(
            count_query,
            (search_pattern, search_pattern, search_pattern, search_pattern),
        )
        total_count = cursor.fetchone()[0]

        if total_count == 0:
            print(
                f"{colorize('No products found matching:', 'yellow')} {colorize(search_term, 'white')}"
            )
            return

        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        if page > total_pages:
            print(
                f"{colorize('Error:', 'red')} Page {page} does not exist. Total pages: {total_pages}"
            )
            return

        offset = (page - 1) * per_page

        # Search query with pagination
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
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                per_page,
                offset,
            ),
        )
        results = cursor.fetchall()

        # Display results in table format
        start_result = offset + 1
        end_result = min(offset + per_page, total_count)
        print(
            f"\n{colorize(f'Found {total_count} product(s) matching:', 'green')} {colorize(search_term, 'white')}"
        )
        print(
            f"{colorize(f'Showing {start_result}-{end_result} of {total_count} results', 'cyan')}"
        )
        print()

        # Table headers
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

        # Get terminal width for adaptive formatting
        try:
            terminal_width = shutil.get_terminal_size().columns
        except (AttributeError, ValueError, OSError):
            terminal_width = 120  # fallback width

        # Calculate minimum column widths
        min_col_widths = [max(len(str(header)), 8) for header in headers]

        # Calculate actual content widths (without truncation first)
        actual_widths = [0] * len(headers)
        for row in results:
            for i, value in enumerate(row):
                if value:
                    if i == 1:  # Date column - calculate formatted date width
                        str_value = str(value)
                        if "T" in str_value:
                            date_part = str_value.split("T", maxsplit=1)[0]
                            time_part = str_value.split("T")[1].split(".")[0]
                            if "+" in time_part:
                                time_part = time_part.split("+")[0]
                            elif "Z" in time_part:
                                time_part = time_part.replace("Z", "")
                            formatted_date = f"{date_part} {time_part}"
                            actual_widths[i] = max(
                                actual_widths[i], len(formatted_date)
                            )
                        else:
                            actual_widths[i] = max(actual_widths[i], len(str_value))
                    else:
                        actual_widths[i] = max(actual_widths[i], len(str(value)))

        # Combine minimum widths with actual content widths
        col_widths = [
            max(min_col_widths[i], actual_widths[i]) for i in range(len(headers))
        ]

        # Calculate space needed for separators (3 chars per separator: " | ")
        separator_space = (len(headers) - 1) * 3
        total_content_width = sum(col_widths)
        total_needed_width = total_content_width + separator_space

        # If table is too wide for terminal, apply smart truncation
        if total_needed_width > terminal_width:
            available_width = terminal_width - separator_space

            # Priority columns that should not be truncated (ID, Date)
            protected_cols = {0, 1}  # ID and Date columns
            protected_width = sum(col_widths[i] for i in protected_cols)

            # Width available for other columns
            remaining_width = available_width - protected_width

            # Columns that can be truncated
            truncatable_cols = [
                i for i in range(len(headers)) if i not in protected_cols
            ]

            if remaining_width > 0 and truncatable_cols:
                # Calculate proportional allocation for truncatable columns
                current_truncatable_width = sum(col_widths[i] for i in truncatable_cols)

                for i in truncatable_cols:
                    if current_truncatable_width > 0:
                        # Proportional allocation
                        proportion = col_widths[i] / current_truncatable_width
                        new_width = int(remaining_width * proportion)

                        # Ensure minimum width
                        col_widths[i] = max(new_width, min_col_widths[i])
                    else:
                        col_widths[i] = min_col_widths[i]

        # Print header
        header_line = " | ".join(
            header.ljust(col_widths[i]) for i, header in enumerate(headers)
        )
        print(colorize(header_line, "yellow"))
        print(colorize("-" * len(header_line), "white"))

        # Print data rows
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

        # Display pagination information
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

        conn.close()

    except sqlite3.Error as e:
        print(f"{colorize('Database error:', 'red')} {e}")
        sys.exit(1)
    except (AttributeError, ValueError, OSError) as e:
        print(f"{colorize('Error:', 'red')} {e}")
        sys.exit(1)
