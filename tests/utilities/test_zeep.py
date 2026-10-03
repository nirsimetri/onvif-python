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
        """Initialize the object with Zeep-style values."""
        self.__values__ = values


class PlainObject:  # pylint: disable=too-few-public-methods
    """Simple object that only exposes normal object attributes."""

    def __init__(self):
        """Initialize public and private attributes."""
        self.name = "camera"
        self.enabled = True
        self._private = "ignored"


class NestedObject:  # pylint: disable=too-few-public-methods
    """Simple object used for nested object conversion tests."""

    def __init__(self, value):
        """Initialize the nested object."""
        self.value = value


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
            (" true ", True),
            ("false", False),
            (" FALSE ", False),
            ("123", 123),
            (" 42 ", 42),
            ("0", 0),
            ("123.45", 123.45),
            ("-12.5", -12.5),
            ("hello", "hello"),
            ("", ""),
            ("  ", ""),
            ("-10", -10.0),
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
            "Item": {
                "id": 123,
                "enabled": True,
            },
        }

    def test_parses_nested_children(self):
        """Test recursively parsing nested children."""
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
        """Test parsing an element containing attributes and children."""
        element = etree.fromstring(
            '<Root><Device id="1"><Name>camera</Name></Device></Root>'
        )

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Device": {
                "id": 1,
                "Name": "camera",
            },
        }

    def test_parses_namespaced_elements(self):
        """Test using local names for namespaced elements."""
        element = etree.fromstring("""
            <Root xmlns="urn:test">
                <Device>
                    <Name>camera</Name>
                </Device>
            </Root>
            """)

        assert ZeepPatcher._parse_element_recursive(element) == {
            "Device": {
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

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Value"] == "parsed"
        assert result["__original_elements__"] == [root]
        parsed_value.parse_xmlelement.assert_called_once()

    def test_passes_name_and_context_to_schema_parser(self):
        """Test forwarding name and context to schema parsing."""
        root = etree.fromstring("<Root><Value>camera</Value></Root>")

        parsed_value = Mock()
        parsed_value.parse_xmlelement.return_value = "parsed"

        schema = Mock()
        schema.get_element.return_value = parsed_value

        parser = Mock(max_occurs=1)
        context = Mock()

        ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
            name="Root",
            context=context,
        )

        parsed_value.parse_xmlelement.assert_called_once_with(
            root[0],
            schema=schema,
            allow_none=True,
            context=context,
        )

    def test_parses_root_attributes_with_children(self):
        """Test preserving root attributes when children are present."""
        root = etree.fromstring(
            '<Root id="10" enabled="true"><Value>camera</Value></Root>'
        )

        parsed_value = Mock()
        parsed_value.parse_xmlelement.return_value = "parsed"

        schema = Mock()
        schema.get_element.return_value = parsed_value

        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["id"] == 10
        assert result["Root"]["enabled"] is True
        assert result["Root"]["Value"] == "parsed"

    def test_parses_child_attributes_and_nested_children(self):
        """Test manually parsing a child with attributes and nested children."""
        root = etree.fromstring("""
            <Root>
                <Device id="10">
                    <Name>camera</Name>
                    <Port>80</Port>
                </Device>
            </Root>
            """)

        schema = Mock()
        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Device"] == {
            "id": 10,
            "Name": "camera",
            "Port": 80,
        }

    def test_falls_back_to_manual_parsing_when_schema_fails(self):
        """Test manual parsing when schema lookup fails."""
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

    def test_falls_back_to_text_when_schema_fails(self):
        """Test fallback parsing of a child containing only text."""
        root = etree.fromstring("<Root><Value>123</Value></Root>")

        schema = Mock()
        schema.get_element.side_effect = ValueError("unknown element")

        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Value"] == 123

    def test_falls_back_when_schema_parser_raises(self):
        """Test fallback parsing when the schema parser itself fails."""
        root = etree.fromstring("<Root><Value>camera</Value></Root>")

        parsed_value = Mock()
        parsed_value.parse_xmlelement.side_effect = RuntimeError("parse failed")

        schema = Mock()
        schema.get_element.return_value = parsed_value

        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema,
        )

        assert result["Root"]["Value"] == "camera"

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

    def test_parses_attribute_only_element(self):
        """Test parsing an element containing only attributes."""
        root = etree.fromstring('<Root id="123" enabled="true"/>')
        parser = Mock(max_occurs=1)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([root]),
            schema=None,
        )

        assert result["Root"] == {
            "id": 123,
            "enabled": True,
        }

    def test_parses_multiple_elements(self):
        """Test parsing multiple XML elements from the queue."""
        first = etree.fromstring("<First>one</First>")
        second = etree.fromstring("<Second>2</Second>")

        parser = Mock(max_occurs=2)

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque([first, second]),
            schema=None,
        )

        assert result["First"] == "one"
        assert result["Second"] == 2
        assert result["__original_elements__"] == [first, second]

    def test_stops_at_max_occurs(self):
        """Test that parsing stops at max_occurs."""
        first = etree.fromstring("<First>one</First>")
        second = etree.fromstring("<Second>two</Second>")

        parser = Mock(max_occurs=1)
        elements = deque([first, second])

        result = ZeepPatcher._patched_parse_xmlelements(
            parser,
            elements,
            schema=None,
        )

        assert result["First"] == "one"
        assert "Second" not in result
        assert list(elements) == [second]

    def test_returns_empty_result_without_elements(self):
        """Test that an empty element queue produces an empty result."""
        parser = Mock(max_occurs=1)

        assert not ZeepPatcher._patched_parse_xmlelements(
            parser,
            deque(),
            schema=None,
        )


# pylint: disable=protected-access,attribute-defined-outside-init
class TestZeepObjectToDict:
    """Tests for converting Zeep objects into dictionaries."""

    def test_handles_none_and_primitive_values(self):
        """Test that None and primitive values are returned unchanged."""
        assert ZeepPatcher._zeep_object_to_dict(None) is None
        assert ZeepPatcher._zeep_object_to_dict("value") == "value"
        assert ZeepPatcher._zeep_object_to_dict(10) == 10
        assert ZeepPatcher._zeep_object_to_dict(1.5) == 1.5
        assert ZeepPatcher._zeep_object_to_dict(True) is True

    def test_converts_lists_and_dicts(self):
        """Test recursive conversion of lists and dictionaries."""
        value = {
            "items": [
                1,
                {"name": "camera"},
                ["nested", 2],
            ],
        }

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

    def test_converts_nested_zeep_values(self):
        """Test recursive conversion of nested Zeep objects."""
        obj = ZeepObject(
            {
                "Name": "camera",
                "Device": ZeepObject(
                    {
                        "XAddr": "http://camera",
                    }
                ),
            }
        )

        assert ZeepPatcher._zeep_object_to_dict(obj) == {
            "Name": "camera",
            "Device": {
                "XAddr": "http://camera",
            },
        }

    def test_converts_zeep_values_containing_lists(self):
        """Test recursive conversion of lists containing Zeep objects."""
        obj = ZeepObject(
            {
                "Devices": [
                    ZeepObject({"Name": "camera-1"}),
                    ZeepObject({"Name": "camera-2"}),
                ],
            }
        )

        assert ZeepPatcher._zeep_object_to_dict(obj) == {
            "Devices": [
                {"Name": "camera-1"},
                {"Name": "camera-2"},
            ],
        }

    def test_converts_object_dict(self):
        """Test conversion of objects exposing a regular __dict__."""
        assert ZeepPatcher._zeep_object_to_dict(PlainObject()) == {
            "name": "camera",
            "enabled": True,
        }

    def test_converts_nested_object_dict(self):
        """Test recursive conversion of regular nested objects."""
        obj = PlainObject()
        obj.device = NestedObject("camera")

        assert ZeepPatcher._zeep_object_to_dict(obj) == {
            "name": "camera",
            "enabled": True,
            "device": {
                "value": "camera",
            },
        }

    def test_returns_objects_without_supported_attributes(self):
        """Test returning objects that expose neither values nor dict state."""

        class SlotObject:  # pylint: disable=too-few-public-methods
            """Object without a __dict__."""

            __slots__ = ("value",)

            def __init__(self):
                """Initialize the slot value."""
                self.value = "camera"

        obj = SlotObject()

        assert ZeepPatcher._zeep_object_to_dict(obj) is obj


# pylint: disable=invalid-name
class TestFlattenXsdAnyFields:
    """Tests for flattening xsd:any fields."""

    def test_returns_primitive_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert ZeepPatcher.flatten_xsd_any_fields("value") == "value"
        assert ZeepPatcher.flatten_xsd_any_fields(10) == 10
        assert ZeepPatcher.flatten_xsd_any_fields(1.5) == 1.5
        assert ZeepPatcher.flatten_xsd_any_fields(True) is True
        assert ZeepPatcher.flatten_xsd_any_fields(None) is None

    def test_returns_dict_unchanged(self):
        """Test that dictionaries are ignored by object processing."""
        value = {"Device": {"XAddr": "http://camera"}}

        assert ZeepPatcher.flatten_xsd_any_fields(value) is value

    def test_returns_object_without_dict_unchanged(self):
        """Test that objects without __dict__ are returned unchanged."""

        class SlotObject:  # pylint: disable=too-few-public-methods
            """Object without a __dict__."""

            __slots__ = ()

        obj = SlotObject()

        assert ZeepPatcher.flatten_xsd_any_fields(obj) is obj

    def test_processes_list_items(self):
        """Test that objects in a list are processed."""
        obj = ZeepObject(
            {
                "_value_1": {
                    "Device": {
                        "XAddr": "http://camera",
                    },
                    "__original_elements__": [],
                }
            }
        )

        result = ZeepPatcher.flatten_xsd_any_fields([obj])

        assert result == [obj]
        assert obj.__values__["Device"] == {
            "XAddr": "http://camera",
        }
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

    def test_does_not_flatten_existing_non_none_field(self):
        """Test preserving an existing populated schema field."""
        obj = ZeepObject(
            {
                "Capabilities": {
                    "Existing": True,
                },
                "_value_1": {
                    "Capabilities": {
                        "XAddr": "http://camera",
                    },
                    "__original_elements__": [],
                },
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.__values__["Capabilities"] == {
            "Existing": True,
        }

    def test_does_not_use_wrapper_when_inner_content_is_not_dict(self):
        """Test handling a single-tag wrapper with primitive content."""
        obj = ZeepObject(
            {
                "Capabilities": None,
                "_value_1": {
                    "Capabilities": "raw",
                    "__original_elements__": [],
                },
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.__values__["Capabilities"] == "raw"
        assert obj.__values__["_value_1"] == []

    def test_flattens_multiple_tags(self):
        """Test flattening multiple xsd:any tags."""
        obj = ZeepObject(
            {
                "_value_1": {
                    "Device": {
                        "XAddr": "http://device",
                    },
                    "Media": {
                        "XAddr": "http://media",
                    },
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

    def test_processes_multiple_value_fields(self):
        """Test processing multiple _value_N fields."""
        obj = ZeepObject(
            {
                "Device": None,
                "Media": None,
                "_value_1": {
                    "Device": {
                        "XAddr": "http://device",
                    },
                    "__original_elements__": [],
                },
                "_value_2": {
                    "Media": {
                        "XAddr": "http://media",
                    },
                    "__original_elements__": [],
                },
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
        assert obj.__values__["_value_2"] == []

    def test_restores_none_original_elements(self):
        """Test replacing parsed data with None when originals are absent."""
        obj = ZeepObject(
            {
                "_value_1": {
                    "Device": {
                        "XAddr": "http://device",
                    },
                    "__original_elements__": None,
                }
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.__values__["Device"] == {
            "XAddr": "http://device",
        }
        assert obj.__values__["_value_1"] is None

    def test_ignores_non_dict_value_fields(self):
        """Test ignoring _value_N fields that are not parsed dictionaries."""
        obj = ZeepObject(
            {
                "_value_1": "raw",
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.__values__["_value_1"] == "raw"

    def test_flattens_plain_object_attributes(self):
        """Test flattening xsd:any data stored on a regular object."""
        obj = PlainObject()
        obj.Capabilities = None
        obj._value_1 = {
            "Capabilities": {
                "XAddr": "http://camera",
            },
            "__original_elements__": [],
        }

        result = ZeepPatcher.flatten_xsd_any_fields(obj)

        assert result is obj
        assert obj.Capabilities == {
            "XAddr": "http://camera",
        }
        assert not obj._value_1

    def test_copies_wrapper_children_to_plain_object(self):
        """Test copying wrapper children into existing plain-object fields."""
        obj = PlainObject()
        obj.Capabilities = None
        obj.XAddr = None
        obj._value_1 = {
            "Capabilities": {
                "XAddr": "http://camera",
            },
            "__original_elements__": [],
        }

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.Capabilities == {
            "XAddr": "http://camera",
        }
        assert obj.XAddr == "http://camera"

    def test_flattens_multiple_tags_on_plain_object(self):
        """Test flattening multiple tags on a regular object."""
        obj = PlainObject()
        obj._value_1 = {
            "Device": {
                "XAddr": "http://device",
            },
            "Media": {
                "XAddr": "http://media",
            },
            "__original_elements__": [],
        }

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj.Device == {
            "XAddr": "http://device",
        }
        assert obj.Media == {
            "XAddr": "http://media",
        }
        assert not obj._value_1

    def test_restores_plain_object_value_to_original_elements(self):
        """Test restoring original XML elements on plain objects."""
        original = etree.fromstring("<Device/>")

        obj = PlainObject()
        obj._value_1 = {
            "Device": {
                "XAddr": "http://device",
            },
            "__original_elements__": [original],
        }

        ZeepPatcher.flatten_xsd_any_fields(obj)

        assert obj._value_1 == [original]

    def test_processes_nested_objects(self):
        """Test recursively flattening nested objects."""
        child = ZeepObject(
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

        parent = ZeepObject(
            {
                "Child": child,
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(parent)

        assert child.__values__["Capabilities"] == {
            "XAddr": "http://camera",
        }

    def test_processes_nested_lists(self):
        """Test recursively flattening objects contained in lists."""
        first = ZeepObject(
            {
                "Device": None,
                "_value_1": {
                    "Device": {
                        "XAddr": "http://device-1",
                    },
                    "__original_elements__": [],
                },
            }
        )
        second = ZeepObject(
            {
                "Device": None,
                "_value_1": {
                    "Device": {
                        "XAddr": "http://device-2",
                    },
                    "__original_elements__": [],
                },
            }
        )

        parent = ZeepObject(
            {
                "Devices": [first, second],
            }
        )

        ZeepPatcher.flatten_xsd_any_fields(parent)

        assert first.__values__["Device"] == {
            "XAddr": "http://device-1",
        }
        assert second.__values__["Device"] == {
            "XAddr": "http://device-2",
        }

    def test_handles_cyclic_references(self):
        """Test preventing infinite recursion through visited objects."""
        first = ZeepObject(
            {
                "Child": None,
            }
        )
        second = ZeepObject(
            {
                "Parent": first,
            }
        )
        first.__values__["Child"] = second

        assert ZeepPatcher.flatten_xsd_any_fields(first) is first


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
        assert XsdAny.parse_xmlelements is ZeepPatcher._patched_parse_xmlelements

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
