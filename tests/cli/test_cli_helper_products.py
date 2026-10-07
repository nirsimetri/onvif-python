"""Tests for CLI helper products."""

from unittest.mock import Mock, patch

import pytest

from onvif.cli.helpers.products import (
    _fetch_product_page,
    _format_date_width,
    _get_content_widths,
    _get_terminal_width,
    _print_data_header,
    _print_data_pagination,
    _print_data_rows,
    _truncate_columns,
    search_products,
)

HEADERS = [
    "ID",
    "Test Date",
    "Model",
    "Firmware",
    "Profiles",
    "Category",
    "Type",
    "Company",
]


def make_row(
    id=1,  # pylint: disable=redefined-builtin
    date="2024-08-15 17:53:12",
    model="C210",
    firmware="1.0.0",
    profiles="M,T,S",
    category="IP Camera",
    type_="Camera",
    company="TP-Link",
):
    """Create a product row with optional field overrides."""
    return (
        id,
        date,
        model,
        firmware,
        profiles,
        category,
        type_,
        company,
    )


class TestFetchProductPage:
    """Tests for fetching a paginated product page from the database."""

    def test_with_results(self):
        """Test fetching a page when matching products exist."""
        cursor = Mock()

        cursor.fetchone.return_value = (45,)
        cursor.fetchall.return_value = [
            make_row(),
            make_row(id=2, model="C220"),
        ]

        total_count, total_pages, results = _fetch_product_page(
            cursor,
            "C210",
            page=1,
            per_page=20,
        )

        assert total_count == 45
        assert total_pages == 3
        assert len(results) == 2

        assert cursor.execute.call_count == 2

        count_params = cursor.execute.call_args_list[0].args[1]
        assert count_params == ("%C210%",) * 4

        data_params = cursor.execute.call_args_list[1].args[1]
        assert data_params == (
            "%C210%",
            "%C210%",
            "%C210%",
            "%C210%",
            20,
            0,
        )

    def test_second_page(self):
        """Test fetching a later page uses the correct database offset."""
        cursor = Mock()

        cursor.fetchone.return_value = (45,)
        cursor.fetchall.return_value = [make_row(id=21)]

        total_count, total_pages, results = _fetch_product_page(
            cursor,
            "camera",
            page=2,
            per_page=20,
        )

        assert total_count == 45
        assert total_pages == 3
        assert results == [make_row(id=21)]

        params = cursor.execute.call_args_list[1].args[1]

        assert params[-2:] == (20, 20)

    def test_no_results(self):
        """Test fetching a page when no matching products exist."""
        cursor = Mock()

        cursor.fetchone.return_value = (0,)

        total_count, total_pages, results = _fetch_product_page(
            cursor,
            "does-not-exist",
            page=1,
            per_page=20,
        )

        assert total_count == 0
        assert total_pages == 0
        assert results == []

        # The data query must not be executed.
        assert cursor.execute.call_count == 1

    @pytest.mark.parametrize(
        ("total_count", "per_page", "expected_pages"),
        [
            (1, 20, 1),
            (20, 20, 1),
            (21, 20, 2),
            (40, 20, 2),
            (41, 20, 3),
            (100, 25, 4),
        ],
    )
    def test_pagination(self, total_count, per_page, expected_pages):
        """Test calculation of total pages for different result counts."""
        cursor = Mock()
        cursor.fetchone.return_value = (total_count,)
        cursor.fetchall.return_value = []

        _, total_pages, _ = _fetch_product_page(
            cursor,
            "camera",
            page=1,
            per_page=per_page,
        )

        assert total_pages == expected_pages


class TestGetContentWidths:
    """Tests for calculating column widths from product data."""

    def test_empty_results(self):
        """Test that empty results produce zero content widths."""
        result = _get_content_widths([], HEADERS)

        assert result == [0] * len(HEADERS)

    def test_uses_longest_value(self):
        """Test that each column uses the width of its longest value."""
        results = [
            make_row(
                id=12345,
                date="2024-01-01T12:30:45.123456+08:00",
                model="SHORT",
                company="Short Company",
            ),
            make_row(
                id=1,
                date="2024-08-15T17:53:12.123456+08:00",
                model="A-MUCH-LONGER-CAMERA-MODEL",
                company="A Very Long Company Name",
            ),
        ]

        widths = _get_content_widths(results, HEADERS)

        assert widths[0] == len("12345")
        assert widths[1] == len("2024-08-15 17:53:12")
        assert widths[2] == len("A-MUCH-LONGER-CAMERA-MODEL")
        assert widths[7] == len("A Very Long Company Name")

    def test_ignores_falsy_values(self):
        """Test that falsy values do not contribute to column widths."""
        results = [
            (
                0,
                None,
                "",
                False,
                None,
                "",
                None,
                None,
            )
        ]

        widths = _get_content_widths(results, HEADERS)

        assert widths == [0] * len(HEADERS)


class TestTruncateColumns:
    """Tests for reducing column widths to fit the terminal."""

    def test_negative_remaining_width(self):
        """Test that widths remain unchanged when no space is available."""
        original = [10, 20, 30]

        result = _truncate_columns(
            original.copy(),
            [8, 8, 8],
            ["ID", "Date", "Model"],
            terminal_width=20,
            separator_space=6,
        )

        assert result == original

    def test_without_truncatable_columns(self):
        """Test that protected columns remain unchanged when space is sufficient."""
        original = [10, 20]

        result = _truncate_columns(
            original.copy(),
            [8, 8],
            ["ID", "Date"],
            terminal_width=100,
            separator_space=3,
        )

        assert result == original

    def test_proportional(self):
        """Test that truncatable columns are reduced proportionally."""
        widths = [10, 20, 30, 40]
        min_widths = [8, 8, 8, 8]
        headers = ["ID", "Date", "Model", "Company"]

        result = _truncate_columns(
            widths.copy(),
            min_widths,
            headers,
            terminal_width=80,
            separator_space=9,
        )

        # First two columns are protected.
        assert result[0] == 10
        assert result[1] == 20

        # Remaining columns are reduced.
        assert result[2] < 30
        assert result[3] < 40

        # Minimum widths are respected.
        assert result[2] >= 8
        assert result[3] >= 8

    def test_zero_current_width(self):
        """Test that zero-width columns are raised to their minimum width."""
        widths = [10, 20, 0, 0]

        result = _truncate_columns(
            widths.copy(),
            [8, 8, 8, 8],
            ["ID", "Date", "Model", "Company"],
            terminal_width=100,
            separator_space=9,
        )

        assert result[0] == 10
        assert result[1] == 20
        assert result[2] == 8
        assert result[3] == 8


class TestGetTerminalWidth:
    """Tests for calculating display widths based on terminal size."""

    def test_returns_content_width_when_it_fits(self):
        """Test that content widths are preserved when they fit."""
        results = [make_row(model="C210")]

        with patch(
            "onvif.cli.helpers.products.shutil.get_terminal_size",
        ) as mock_size:
            mock_size.return_value.columns = 200

            result = _get_terminal_width(results, HEADERS)

        assert len(result) == len(HEADERS)

        # Every column must be at least its header width / 8.
        for width, header in zip(result, HEADERS):
            assert width >= max(len(header), 8)

    @pytest.mark.parametrize(
        "exception",
        [
            AttributeError(),
            ValueError(),
            OSError(),
        ],
    )
    def test_falls_back_to_120(self, exception):
        """Test that terminal size errors use the fallback width."""
        results = [make_row(model="C210")]

        with patch(
            "onvif.cli.helpers.products.shutil.get_terminal_size",
            side_effect=exception,
        ):
            result = _get_terminal_width(results, HEADERS)

        assert len(result) == len(HEADERS)

    def test_truncates_wide_content(self):
        """Test that wide content is reduced to fit the terminal."""
        results = [
            make_row(
                model="A" * 100,
                company="B" * 100,
                firmware="C" * 100,
                profiles="D" * 100,
            )
        ]

        original_widths = _get_content_widths(results, HEADERS)

        with patch(
            "onvif.cli.helpers.products.shutil.get_terminal_size",
        ) as mock_size:
            mock_size.return_value.columns = 80

            result = _get_terminal_width(results, HEADERS)

        # Terminal width constraint should cause the calculated widths
        # to differ from the unconstrained content widths.
        assert result != original_widths

        # Columns have a minimum display width.
        assert all(width >= 8 for width in result)

        # Wide columns should be reduced rather than expanded.
        for index in (2, 3, 4, 7):
            assert result[index] < original_widths[index]


class TestFormatDateWidth:
    """Tests for formatting dates for table display."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2024-08-15", "2024-08-15"),
            (
                "2024-08-15T17:53:12",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15T17:53:12.123456",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15T17:53:12+08:00",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15T17:53:12Z",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15T17:53:12.123456+08:00",
                "2024-08-15 17:53:12",
            ),
        ],
    )
    def test_format_date(self, value, expected):
        """Test formatting supported date representations."""
        assert _format_date_width(value) == expected


class TestPrintDataHeader:
    """Tests for printing the product table header."""

    def test_prints_headers(self, capsys):
        """Test that all headers and the separator are printed."""
        col_widths = [8] * len(HEADERS)

        _print_data_header(HEADERS, col_widths)

        output = capsys.readouterr().out

        for header in HEADERS:
            assert header in output

        assert "-" in output


class TestPrintDataRows:
    """Tests for printing product rows in the terminal table."""

    def test_basic(self, capsys):
        """Test printing a standard product row."""
        results = [
            make_row(
                id=1,
                date="2024-08-15 17:53:12",
                model="C210",
            )
        ]

        col_widths = [8] * len(HEADERS)

        _print_data_rows(results, col_widths)

        output = capsys.readouterr().out

        assert "1" in output
        assert "2024-08-15 17:53:12" in output
        assert "C210" in output

    def test_handles_none(self, capsys):
        """Test printing a row containing None values."""
        row = (
            1,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        _print_data_rows([row], [8] * len(HEADERS))

        output = capsys.readouterr().out

        assert "1" in output
        assert output.count("|") == len(HEADERS) - 1

    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            (
                "2024-08-15T17:53:12.9154121+08:00",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15T17:53:12Z",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15 17:53:12",
                "2024-08-15 17:53:12",
            ),
            (
                "2024-08-15",
                "2024-08-15 00:00:00",
            ),
            (
                "not-a-date",
                "not-a-date",
            ),
        ],
    )
    def test_date_formats(self, capsys, date, expected):
        """Test formatting and fallback behavior for row dates."""
        row = make_row(date=date)

        _print_data_rows([row], [30] * len(HEADERS))

        output = capsys.readouterr().out

        assert expected in output

    def test_truncates_long_values(self, capsys):
        """Test that values exceeding their column width are truncated."""
        row = make_row(model="ABCDEFGHIJKLMNO")

        col_widths = [8] * len(HEADERS)

        _print_data_rows([row], col_widths)

        output = capsys.readouterr().out

        assert "ABCDE..." in output

    def test_does_not_truncate_short_values(self, capsys):
        """Test that values within their column width are not truncated."""
        row = make_row(model="C210")

        _print_data_rows([row], [20] * len(HEADERS))

        output = capsys.readouterr().out

        assert "C210" in output
        assert "..." not in output

    def test_invalid_date_falls_back_to_original(self, capsys):
        """Test that invalid dates are printed without modification."""
        row = make_row(date="2024/08/15 invalid")

        _print_data_rows([row], [30] * len(HEADERS))

        output = capsys.readouterr().out

        assert "2024/08/15 invalid" in output

    def test_multiple_rows(self, capsys):
        """Test printing multiple product rows."""
        rows = [
            make_row(id=1, model="C210"),
            make_row(id=2, model="C220"),
            make_row(id=3, model="C230"),
        ]

        _print_data_rows(rows, [20] * len(HEADERS))

        output = capsys.readouterr().out

        assert "C210" in output
        assert "C220" in output
        assert "C230" in output


class TestPrintDataPagination:
    """Tests for printing product table pagination controls."""

    def test_single_page(self, capsys):
        """Test pagination output when only one page exists."""
        _print_data_pagination(1, 1)

        output = capsys.readouterr().out

        assert "Page 1 of 1" in output
        assert "Navigation:" not in output

    def test_first_page(self, capsys):
        """Test pagination output for the first page."""
        _print_data_pagination(1, 3)

        output = capsys.readouterr().out

        assert "Page 1 of 3" in output
        assert "Next: --page 2" in output
        assert "Previous:" not in output

    def test_middle_page(self, capsys):
        """Test pagination output for a middle page."""
        _print_data_pagination(2, 3)

        output = capsys.readouterr().out

        assert "Page 2 of 3" in output
        assert "Previous: --page 1" in output
        assert "Next: --page 3" in output

    def test_last_page(self, capsys):
        """Test pagination output for the last page."""
        _print_data_pagination(3, 3)

        output = capsys.readouterr().out

        assert "Page 3 of 3" in output
        assert "Previous: --page 2" in output
        assert "Next:" not in output


class TestSearchProducts:
    """Tests for the main product search command."""

    def test_database_not_found(self):
        """Test that a missing product database exits with an error."""
        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=False,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            search_products("C210")

        assert exc_info.value.code == 1

    @pytest.mark.parametrize(
        ("page", "per_page"),
        [
            (0, 20),
            (-1, 20),
            (1, 0),
            (1, -1),
            (1, 101),
        ],
    )
    def test_invalid_pagination(self, page, per_page):
        """Test that invalid pagination arguments exit with an error."""
        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=True,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            search_products(
                "C210",
                page=page,
                per_page=per_page,
            )

        assert exc_info.value.code == 1

    def test_no_results(self, capsys):
        """Test search behavior when no matching products are found."""
        conn = Mock()
        cursor = Mock()

        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = (0,)

        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=True,
            ),
            patch(
                "onvif.cli.helpers.products.sqlite3.connect",
                return_value=conn,
            ),
            patch(
                "onvif.cli.helpers.products._fetch_product_page",
                return_value=(0, 0, []),
            ),
        ):
            assert search_products("unknown") is None

        output = capsys.readouterr().out

        assert "No products found" in output
        assert "unknown" in output
        conn.close.assert_not_called()

    def test_page_out_of_range(self, capsys):
        """Test search behavior when the requested page does not exist."""
        conn = Mock()

        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=True,
            ),
            patch(
                "onvif.cli.helpers.products.sqlite3.connect",
                return_value=conn,
            ),
            patch(
                "onvif.cli.helpers.products._fetch_product_page",
                return_value=(45, 3, []),
            ),
        ):
            assert (
                search_products(
                    "camera",
                    page=4,
                    per_page=20,
                )
                is None
            )

        output = capsys.readouterr().out

        assert "does not exist" in output
        assert "Total pages: 3" in output
        conn.close.assert_not_called()

    def test_database_error(self):
        """Test that database errors exit with an error status."""
        conn = Mock()

        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=True,
            ),
            patch(
                "onvif.cli.helpers.products.sqlite3.connect",
                return_value=conn,
            ),
            patch(
                "onvif.cli.helpers.products._fetch_product_page",
                side_effect=__import__("sqlite3").Error("database failure"),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            search_products("camera")

        assert exc_info.value.code == 1

    @pytest.mark.parametrize(
        "exception",
        [
            AttributeError("invalid result"),
            ValueError("invalid value"),
            OSError("filesystem failure"),
        ],
    )
    def test_other_errors(self, exception):
        """Test that unexpected errors exit with an error status."""
        conn = Mock()

        with (
            patch(
                "onvif.cli.helpers.products.os.path.exists",
                return_value=True,
            ),
            patch(
                "onvif.cli.helpers.products.sqlite3.connect",
                return_value=conn,
            ),
            patch(
                "onvif.cli.helpers.products._fetch_product_page",
                side_effect=exception,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            search_products("camera")

        assert exc_info.value.code == 1
