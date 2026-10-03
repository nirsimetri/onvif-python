"""Tests for ZeepPatcher."""

from collections import deque
from unittest.mock import Mock

import pytest
from lxml import etree
from zeep.xsd.elements.any import Any as XsdAny

from onvif.utils.zeep import ZeepPatcher


class ZeepObject:  # pylint: disable=too-few-public-methods
    """Simple object that mimics a Zeep object."""

    def __init__(self, values):
        self.__values__ = values


@pytest.fixture(autouse=True)
def reset_zeep_patch():
    """Ensure the global Zeep patch is removed before and after each test."""
    ZeepPatcher.remove_patch()
    yield
    ZeepPatcher.remove_patch()


# pylint: disable=protected-access
class TestParseTextValue:
    """Tests for ZeepPatcher text value conversion."""

    def test_returns_none_for_none(self):
        """Test that None remains None."""
        assert ZeepPatcher._parse_text_value(None) is None

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("true", True),
            ("TRUE", True),
            (" false ", False),
            ("123", 123),
            (" 42 ", 42),
            ("123.45", 123.45),
            ("hello", "hello"),
        ],
    )
    def test_converts_text_value(self, value, expected):
        """Test conversion of supported text value types."""
        assert ZeepPatcher._parse_text_value(value) == expected


# pylint: disable=protected-access
class TestParseElementRecursive:
    """Tests for recursive XML element parsing."""

    def test_parses_text_children(self):
        """Test parsing elements containing text values."""
        element = etree.fromstring(
            "<Root><Name>camera</Name><Enabled>true</Enabled><Count>2</Count></Root>"
        )

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Name": "camera",
            "Enabled": True,
            "Count": 2,
        }

    def test_parses_attributes(self):
        """Test parsing child attributes into dictionaries."""
        element = etree.fromstring('<Root><Item id="123" enabled="true"/></Root>')

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Item": {"id": 123, "enabled": True},
        }

    def test_parses_nested_children(self):
        """Test recursively parsing nested child elements."""
        element = etree.fromstring(
            "<Root><Device><Name>camera</Name><Port>80</Port></Device></Root>"
        )

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Device": {
                "Name": "camera",
                "Port": 80,
            },
        }

    def test_merges_attributes_and_children(self):
        """Test parsing an element containing both attributes and children."""
        element = etree.fromstring(
            '<Root><Device id="1"><Name>camera</Name></Device></Root>'
        )

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Device": {
                "id": 1,
                "Name": "camera",
            },
        }

    def test_returns_none_for_empty_element(self):
        """Test that an element without children produces None."""
        element = etree.fromstring("<Root/>")

        assert ZeepPatcher._parse_element_recursive(element) is None


# pylint: disable=protected-access
class TestPatchedParseXmlElements:
    """Tests for the patched Zeep xsd:any XML parser."""

    def test_parses_xml_with_schema(self):
        """Test parsing child elements through the provided schema."""
        root = etree.fromstring("<Root><Value>camera</Value></Root>")

        parsed_value = Mock()
        parsed_value.parse_xmlelement.return_value = "parsed"

        schema = Mock()
        schema.get_element.return_value = parsed_value

        parser = Mock(max_occurs=1)
        elements = deque([root])

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            elements,
            schema,
        )

        assert result["Root"]["Value"] == "parsed"
        assert result["__original_elements__"] == [root]
        parsed_value.parse_xmlelement.assert_called_once()

    def test_parses_attributes_without_schema_lookup(self):
        """Test parsing child attributes without schema parsing."""
        root = etree.fromstring('<Root><Device id="123" enabled="true"/></Root>')
        schema = Mock()
        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Device"] == {
            "id": 123,
            "enabled": True,
        }

    def test_falls_back_to_manual_parsing_when_schema_fails(self):
        """Test manual parsing when schema lookup or parsing fails."""
        root = etree.fromstring("<Root><Device><Name>camera</Name></Device></Root>")
        schema = Mock()
        schema.get_element.side_effect = ValueError("unknown element")
        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Device"] == {
            "Name": "camera",
        }

    def test_parses_text_only_element(self):
        """Test parsing an element containing only text."""
        root = etree.fromstring("<Root>hello</Root>")
        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema=None,
        )

        assert result["Root"] == "hello"
        assert result["__original_elements__"] == [root]

    def test_returns_empty_result_without_elements(self):
        """Test that an empty element queue produces an empty result."""
        parser = Mock(max_occurs=1)

        assert not ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque(),
            schema=None,
        )


# pylint: disable=protected-access
class TestZeepObjectToDict:
    """Tests for converting Zeep objects into dictionaries."""

    def test_handles_none_and_primitive_values(self):
        """Test that None and primitive values are returned unchanged."""
        assert ZeepPatcher._zeep_object_to_dict(None) is None
        assert ZeepPatcher._zeep_object_to_dict("value") == "value"
        assert ZeepPatcher._zeep_object_to_dict(10) == 10
        assert ZeepPatcher._zeep_object_to_dict(True) is True

    def test_converts_lists_and_dicts(self):
        """Test recursive conversion of lists and dictionaries."""
        value = {"items": [1, {"name": "camera"}]}

        assert ZeepPatcher._zeep_object_to_dict(value) == value

    def test_converts_zeep_values(self):
        """Test conversion of objects exposing Zeep __values__."""
        obj = ZeepObject(
            {
                "Name": "camera",
                "_value_1": "ignored",
            }
        )

        assert ZeepPatcher._zeep_object_to_dict(obj) == {
            "Name": "camera",
        }

    def test_converts_object_dict(self):
        """Test conversion of objects exposing a regular __dict__."""

        class Object:  # pylint: disable=too-few-public-methods
            """Simple object with public and private attributes."""

            def __init__(self):
                self.name = "camera"
                self._private = "ignored"

        assert ZeepPatcher._zeep_object_to_dict(Object()) == {
            "name": "camera",
        }


class TestFlattenXsdAnyFields:
    """Tests for flattening xsd:any fields."""

    def test_returns_primitive_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert ZeepPatcher.flatten_xsd_any_fields("value") == "value"
        assert ZeepPatcher.flatten_xsd_any_fields(None) is None

    def test_processes_list_items(self):
        """Test that objects in a list are processed."""
        obj = ZeepObject(
            {
                "_value_1": {
                    "Device": {"XAddr": "http://camera"},
                    "__original_elements__": [],
                }
            }
        )

        result = ZeepPatcher.flatten_xsd_any_fields([obj])

        assert result == [obj]
        assert obj.__values__["Device"] == {"XAddr": "http://camera"}
        assert obj.__values__["_value_1"] == []

    def test_flattens_single_tag_wrapper(self):
        """Test flattening a single xsd:any wrapper."""
        obj = ZeepObject(
            {
                "Capabilities": None,
                "_value_1": {
                    "Capabilities": {
                        "XAddr": "http://camera",
                    },
                    "__original_elements__": [],
                },
            }
        )

        result = ZeepPatcher.flatten_xsd_any_fields(obj)

        assert result is obj
        assert obj.__values__["Capabilities"] == {
            "XAddr": "http://camera",
        }
        assert obj.__values__["_value_1"] == []

    def test_flattens_multiple_tags(self):
        """Test flattening multiple xsd:any tags."""
        obj = ZeepObject(
            {
                "_value_1": {
                    "Device": {"XAddr": "http://device"},
                    "Media": {"XAddr": "http://media"},
                    "__original_elements__": [],
                }
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.__values__["Device"] == {
            "XAddr": "http://device",
        }
        assert obj.__values__["Media"] == {
            "XAddr": "http://media",
        }
        assert obj.__values__["_value_1"] == []


class TestZeepPatchLifecycle:
    """Tests for applying, removing, and checking the Zeep patch."""

    def setup_method(self):
        """Ensure the Zeep patch is inactive before each test."""
        ZeepPatcher.remove_patch()

    def teardown_method(self):
        """Ensure the Zeep patch is inactive after each test."""
        ZeepPatcher.remove_patch()

    def test_patch_is_not_active_by_default(self):
        """Test that the patch starts in an inactive state."""
        assert ZeepPatcher.is_patched() is False

    def test_apply_patch(self):
        """Test that applying the patch changes the patch state."""
        original = XsdAny.parse_xmlelements

        ZeepPatcher.apply_patch()

        assert ZeepPatcher.is_patched() is True
        assert XsdAny.parse_xmlelements is ZeepPatcher._patched_parse_xmlelements
        assert ZeepPatcher._original_parse_xmlelements is original

    def test_apply_patch_is_idempotent(self):
        """Test that applying the patch multiple times is safe."""
        ZeepPatcher.apply_patch()
        original = ZeepPatcher._original_parse_xmlelements

        ZeepPatcher.apply_patch()

        assert ZeepPatcher._original_parse_xmlelements is original

    def test_remove_patch(self):
        """Test that removing the patch restores the original state."""
        original = XsdAny.parse_xmlelements

        ZeepPatcher.apply_patch()
        ZeepPatcher.remove_patch()

        assert ZeepPatcher.is_patched() is False
        assert XsdAny.parse_xmlelements is original

    def test_remove_patch_when_not_applied(self):
        """Test that removing an inactive patch is safe."""
        ZeepPatcher.remove_patch()

        assert ZeepPatcher.is_patched() is False
