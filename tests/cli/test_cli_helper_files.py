"""Tests for CLI helper files."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from onvif.cli.helpers.files import (
    _serialize_for_json,
    save_output_to_file,
)


class TestSerializeForJson:
    """Tests for serializing values into JSON-compatible objects."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            ("hello", "hello"),
            (123, 123),
            (12.5, 12.5),
            (True, True),
            (False, False),
        ],
    )
    def test_primitive(self, value, expected):
        """Test serialization of primitive values."""
        assert _serialize_for_json(value) == expected

    def test_datetime(self):
        """Test serialization of datetime values."""
        value = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

        assert _serialize_for_json(value) == "2026-01-02T03:04:05+00:00"

    def test_list(self):
        """Test serialization of list values."""
        value = [
            "hello",
            123,
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            {"nested": True},
        ]

        assert _serialize_for_json(value) == [
            "hello",
            123,
            "2026-01-01T00:00:00+00:00",
            {"nested": True},
        ]

    def test_tuple(self):
        """Test serialization of tuple values."""
        value = ("hello", 123, True)

        assert _serialize_for_json(value) == [
            "hello",
            123,
            True,
        ]

    def test_dict(self):
        """Test serialization of dictionary values."""
        value = {
            "name": "camera",
            "enabled": True,
            "count": 10,
            "nested": {
                "value": 42,
            },
        }

        assert _serialize_for_json(value) == value

    def test_regular_object(self):
        """Test serialization of a regular object."""

        class Camera:
            """Simple camera object for serialization testing."""

            def __init__(self):
                self.name = "Camera 1"
                self.enabled = True
                self._private = "hidden"

        camera = Camera()

        assert _serialize_for_json(camera) == {
            "name": "Camera 1",
            "enabled": True,
        }

    def test_regular_object_nested(self):
        """Test serialization of a regular object with nested values."""

        class Camera:
            """Simple camera object with nested settings."""

            def __init__(self):
                self.name = "Camera 1"
                self.settings = {
                    "fps": 30,
                    "enabled": True,
                }

        camera = Camera()

        assert _serialize_for_json(camera) == {
            "name": "Camera 1",
            "settings": {
                "fps": 30,
                "enabled": True,
            },
        }

    def test_regular_object_uses_dir_when_dict_empty(self):
        """Test serialization using public attributes when __dict__ is empty."""

        class Camera:
            """Camera object exposing a property instead of instance attributes."""

            @property
            def name(self):
                """Return the camera name."""
                return "Camera 1"

        camera = Camera()

        assert _serialize_for_json(camera) == {
            "name": "Camera 1",
        }

    def test_regular_object_skips_callable_attributes(self):
        """Test that callable attributes are excluded from serialization."""

        class Camera:
            """Camera object containing a callable attribute."""

            def __init__(self):
                self.name = "Camera 1"

            def method(self):
                """Return a value that should not be serialized."""
                return "ignored"

        camera = Camera()

        assert _serialize_for_json(camera) == {
            "name": "Camera 1",
        }

    def test_zeep_object(self):
        """Test serialization of a Zeep-like object."""

        class ZeepObject:
            """Simple object that mimics a Zeep object."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Name", object()),
                        ("Enabled", object()),
                    ]
                },
            )()

            Name = "Camera 1"
            Enabled = True

        result = _serialize_for_json(ZeepObject())

        assert result == {
            "Name": "Camera 1",
            "Enabled": True,
        }

    def test_zeep_object_nested(self):
        """Test serialization of a nested Zeep-like object."""

        class Profile:
            """Simple profile object that mimics a Zeep object."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Name", object()),
                        ("Token", object()),
                    ]
                },
            )()

            Name = "Main"
            Token = "profile_1"

        profile = Profile()

        class Camera:
            """Simple camera object containing a nested profile."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Profile", object()),
                    ]
                },
            )()

            Profile = profile

        assert _serialize_for_json(Camera()) == {
            "Profile": {
                "Name": "Main",
                "Token": "profile_1",
            }
        }

    def test_zeep_object_skips_missing_element(self):
        """Test that missing Zeep elements are skipped."""

        class ZeepObject:
            """Simple Zeep-like object with a missing element."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Existing", object()),
                        ("Missing", object()),
                    ]
                },
            )()

            Existing = "value"

        result = _serialize_for_json(ZeepObject())

        assert result == {
            "Existing": "value",
        }

    def test_zeep_object_skips_none_element(self):
        """Test that Zeep elements with None values are skipped."""

        class ZeepObject:
            """Simple Zeep-like object containing a None element."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Value", object()),
                    ]
                },
            )()

            Value = None

        assert _serialize_for_json(ZeepObject()) == {}

    def test_zeep_object_includes_regular_attributes(self):
        """Test that regular attributes are included with Zeep elements."""

        class ZeepObject:
            """Simple Zeep-like object with an additional attribute."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Name", object()),
                    ]
                },
            )()

            Name = "Camera 1"
            Extra = "extra"

        assert _serialize_for_json(ZeepObject()) == {
            "Name": "Camera 1",
            "Extra": "extra",
        }

    def test_zeep_object_does_not_duplicate_xsd_element(self):
        """Test that XSD elements are not duplicated as regular attributes."""

        class ZeepObject:
            """Simple Zeep-like object with an XSD element."""

            _xsd_type = type(
                "XSDType",
                (),
                {
                    "elements": [
                        ("Name", object()),
                    ]
                },
            )()

            Name = "Camera 1"

        assert _serialize_for_json(ZeepObject()) == {
            "Name": "Camera 1",
        }

    def test_value_1(self):
        """Test serialization of an object containing _value_1."""

        class ZeepValue:
            """Simple object containing a Zeep _value_1 attribute."""

            __slots__ = ("_value_1",)

            def __init__(self):
                self._value_1 = {
                    "Name": "Camera 1",
                    "Enabled": True,
                }

        assert _serialize_for_json(ZeepValue()) == {
            "Name": "Camera 1",
            "Enabled": True,
        }

    def test_value_1_nested(self):
        """Test serialization of nested values stored in _value_1."""

        class ZeepValue:
            """Simple object containing nested Zeep values."""

            __slots__ = ("_value_1",)

            def __init__(self):
                self._value_1 = [
                    {"Name": "Camera 1"},
                    {"Name": "Camera 2"},
                ]

        assert _serialize_for_json(ZeepValue()) == [
            {"Name": "Camera 1"},
            {"Name": "Camera 2"},
        ]

    def test_fallback_to_vars(self):
        """Test fallback serialization for objects without serializable attributes."""

        class CustomObject:
            """Simple object that falls back to string conversion."""

            __slots__ = ()

            def __str__(self):
                """Return the fallback string representation."""
                return "custom-value"

        obj = CustomObject()

        assert _serialize_for_json(obj) == "custom-value"


class TestSaveOutputToFileJson:
    """Tests for saving CLI output as JSON."""

    def test_json(self, tmp_path):
        """Test saving output as a JSON file."""
        output_path = tmp_path / "result.json"

        client = Mock()
        client.xml_plugin = None

        result = {
            "name": "Camera 1",
            "enabled": True,
        }

        save_output_to_file(
            result,
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert '"result": {' in content
        assert '"name": "Camera 1"' in content
        assert '"enabled": true' in content
        assert '"timestamp":' in content
        assert '"raw_result":' in content

    def test_json_debug(self):
        """Test saving JSON output with SOAP debug information."""
        client = Mock()

        client.xml_plugin = Mock()
        client.xml_plugin.last_sent_xml = "<request/>"
        client.xml_plugin.last_received_xml = "<response/>"
        client.xml_plugin.last_operation = "GetDeviceInformation"

        result = {"value": 123}

        with patch(
            "onvif.cli.helpers.files.open",
            create=True,
        ) as mock_open:
            save_output_to_file(
                result,
                "result.json",
                True,
                client,
            )

        handle = mock_open.return_value.__enter__.return_value
        written = handle.write.call_args_list

        assert written

    def test_json_debug_without_plugin(self):
        """Test JSON debug output when no XML plugin is available."""
        client = Mock()
        client.xml_plugin = None

        result = {"value": 123}

        with patch("onvif.cli.helpers.files.json.dump") as mock_dump:
            save_output_to_file(
                result,
                "result.json",
                True,
                client,
            )

        output_data = mock_dump.call_args.args[0]

        assert "debug" not in output_data


class TestSaveOutputToFileXml:
    """Tests for saving CLI output as XML."""

    def test_xml_with_raw_response(self, tmp_path):
        """Test saving XML output containing a raw SOAP response."""
        output_path = tmp_path / "result.xml"

        client = Mock()
        client.xml_plugin = Mock()
        client.xml_plugin.last_received_xml = "<soap:Envelope/>"
        client.xml_plugin.last_operation = "GetProfiles"

        with patch("onvif.cli.helpers.files.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026,
                1,
                2,
                3,
                4,
                5,
                tzinfo=timezone.utc,
            )

            save_output_to_file(
                {"value": 123},
                str(output_path),
                False,
                client,
            )

        content = output_path.read_text(encoding="utf-8")

        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert "<!-- ONVIF SOAP Response -->" in content
        assert "<!-- Operation: GetProfiles -->" in content
        assert "<soap:Envelope/>" in content

    def test_xml_without_raw_response(self, tmp_path):
        """Test saving XML output when no raw SOAP response is available."""
        output_path = tmp_path / "result.xml"

        client = Mock()
        client.xml_plugin = None

        result = {"value": 123}

        save_output_to_file(
            result,
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert "<onvif_result>" in content
        assert str(result) in content
        assert "Raw SOAP XML not available" in content

    def test_xml_with_plugin_but_empty_response(self, tmp_path):
        """Test XML output when the plugin exists but has no response."""
        output_path = tmp_path / "result.xml"

        client = Mock()
        client.xml_plugin = Mock()
        client.xml_plugin.last_received_xml = ""
        client.xml_plugin.last_operation = "GetProfiles"

        save_output_to_file(
            "parsed result",
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert "<onvif_result>" in content
        assert "parsed result" in content

    def test_xml_unknown_operation(self, tmp_path):
        """Test XML output when the SOAP operation is unknown."""
        output_path = tmp_path / "result.xml"

        client = Mock()
        client.xml_plugin = Mock()
        client.xml_plugin.last_received_xml = "<response/>"
        client.xml_plugin.last_operation = None

        save_output_to_file(
            "result",
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert "<!-- Operation: Unknown -->" in content


class TestSaveOutputToFileText:
    """Tests for saving CLI output as plain text."""

    def test_text(self, tmp_path):
        """Test saving output as a plain text file."""
        output_path = tmp_path / "result.txt"

        client = Mock()
        client.xml_plugin = None

        save_output_to_file(
            "hello world",
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert content.startswith("ONVIF Command Output\n")
        assert "Timestamp:" in content
        assert "=" * 50 in content
        assert "hello world" in content

    def test_text_debug(self, tmp_path):
        """Test saving text output with SOAP debug information."""
        output_path = tmp_path / "result.txt"

        client = Mock()
        client.xml_plugin = Mock()
        client.xml_plugin.last_operation = "GetProfiles"
        client.xml_plugin.last_sent_xml = "<request/>"
        client.xml_plugin.last_received_xml = "<response/>"

        save_output_to_file(
            "result",
            str(output_path),
            True,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert "DEBUG INFORMATION" in content
        assert "Operation: GetProfiles" in content
        assert "SOAP Request:" in content
        assert "<request/>" in content
        assert "SOAP Response:" in content
        assert "<response/>" in content

    def test_text_debug_only_operation(self, tmp_path):
        """Test text debug output containing only the operation."""
        output_path = tmp_path / "result.txt"

        client = Mock()
        client.xml_plugin = Mock()
        client.xml_plugin.last_operation = "GetProfiles"
        client.xml_plugin.last_sent_xml = ""
        client.xml_plugin.last_received_xml = ""

        save_output_to_file(
            "result",
            str(output_path),
            True,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert "Operation: GetProfiles" in content
        assert "SOAP Request:" not in content
        assert "SOAP Response:" not in content


class TestSaveOutputToFileExtensionHandling:
    """Tests for output file extension handling."""

    @pytest.mark.parametrize(
        "filename",
        [
            "result",
            "result.txt",
            "result.log",
            "result.output",
            "RESULT.TXT",
        ],
    )
    def test_defaults_to_text(self, tmp_path, filename):
        """Test that unsupported extensions default to text output."""
        output_path = tmp_path / filename

        client = Mock()
        client.xml_plugin = None

        save_output_to_file(
            "result",
            str(output_path),
            False,
            client,
        )

        content = output_path.read_text(encoding="utf-8")

        assert content.startswith("ONVIF Command Output\n")
        assert "result" in content


class TestSaveOutputToFileErrorHandling:
    """Tests for errors raised while saving CLI output."""

    @pytest.mark.parametrize(
        "exception",
        [
            OSError("write failed"),
            ValueError("invalid value"),
            AttributeError("missing attribute"),
        ],
    )
    def test_handles_save_error(self, exception, capsys):
        """Test that save errors are reported without raising."""
        client = Mock()
        client.xml_plugin = None

        with patch(
            "onvif.cli.helpers.files.open",
            side_effect=exception,
            create=True,
        ):
            save_output_to_file(
                {"value": 123},
                "result.json",
                False,
                client,
            )

        captured = capsys.readouterr()

        assert "Error saving output:" in captured.err
        assert str(exception) in captured.err
        assert "{'value': 123}" in captured.out

    def test_error_uses_colorize(self, capsys):
        """Test that save errors are passed through colorize."""
        client = Mock()
        client.xml_plugin = None

        with (
            patch(
                "onvif.cli.helpers.files.open",
                side_effect=OSError("write failed"),
                create=True,
            ),
            patch(
                "onvif.cli.helpers.files.colorize",
                return_value="COLORED ERROR",
            ) as mock_colorize,
        ):
            save_output_to_file(
                "result",
                "result.txt",
                False,
                client,
            )

        mock_colorize.assert_called_once_with(
            "Error saving output:",
            "red",
        )

        captured = capsys.readouterr()

        assert "COLORED ERROR" in captured.err
        assert "result" in captured.out
