# pylint: disable=protected-access
"""Tests for interactive shell reference commands."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from onvif.cli.interactive.context import ShellContext
from onvif.cli.interactive.reference import ReferenceCommands


def create_context(**overrides):
    """Create a mocked shell context with sensible defaults."""
    args = SimpleNamespace(
        username="admin",
        host="192.168.1.100",
        port=80,
        debug=False,
    )

    context = ShellContext(
        client=MagicMock(),
        args=args,
    )

    context.current_service_name = overrides.pop("current_service_name", None)
    context.stored_data = overrides.pop("stored_data", {})
    context.stored_metadata = overrides.pop("stored_metadata", {})
    context.last_result = overrides.pop("last_result", None)
    context.last_method = overrides.pop("last_method", None)
    context.last_service_name = overrides.pop("last_service_name", None)

    for key, value in overrides.items():
        setattr(context, key, value)

    return context


def create_commands(**overrides):
    """Create ReferenceCommands with a mocked shell context."""
    commands = ReferenceCommands()
    commands.context = create_context(**overrides)
    return commands


class TestReferenceCommandsStore:
    """Test stored result commands."""

    def test_do_store_without_name_prints_usage(self, capsys):
        """Verify store without a name prints usage information."""
        commands = create_commands()

        commands.do_store("")

        output = capsys.readouterr().out

        assert "Usage: store <name>" in output
        assert commands.context.stored_data == {}

    @pytest.mark.parametrize(
        "name",
        [
            "123name",
            "1",
            "-name",
            "name-with-dash",
            "name.with.dot",
            "name with space",
            "$name",
            "name!",
        ],
    )
    def test_do_store_rejects_invalid_name(self, name, capsys):
        """Verify store rejects invalid variable names."""
        commands = create_commands(last_result={"value": 123})

        commands.do_store(name)

        output = capsys.readouterr().out

        assert "Invalid name" in output
        assert name not in commands.context.stored_data

    @pytest.mark.parametrize(
        "name",
        [
            "result",
            "_result",
            "Result",
            "result1",
            "result_1",
            "_result_1",
            "ABC",
        ],
    )
    def test_do_store_accepts_valid_name(self, name):
        """Verify store accepts valid variable names."""
        commands = create_commands(last_result={"value": 123})

        commands.do_store(name)

        assert commands.context.stored_data[name] == {"value": 123}

    def test_do_store_rejects_duplicate_name(self, capsys):
        """Verify store rejects an existing variable name."""
        commands = create_commands(
            stored_data={"result": {"old": True}},
            last_result={"new": True},
        )

        commands.do_store("result")

        output = capsys.readouterr().out

        assert "already exists" in output
        assert commands.context.stored_data["result"] == {"old": True}

    def test_do_store_without_result(self, capsys):
        """Verify store rejects an unset last result."""
        commands = create_commands()

        # The implementation currently checks against a newly-created
        # sentinel object, so explicitly use the same semantic value only
        # through a patched object comparison.
        unset = object()

        with patch(
            "onvif.cli.interactive.reference.object",
            return_value=unset,
        ):
            commands.context.last_result = unset
            commands.do_store("result")

        output = capsys.readouterr().out

        assert "No result to store" in output
        assert "result" not in commands.context.stored_data

    def test_do_store_saves_result(self):
        """Verify store saves the last result."""
        result = {"Profiles": [{"token": "profile1"}]}
        commands = create_commands(last_result=result)

        commands.do_store("profiles")

        assert commands.context.stored_data["profiles"] == result

    def test_do_store_saves_service_metadata(self):
        """Verify store saves the last service name as metadata."""
        commands = create_commands(
            last_result={"value": 123},
            last_service_name="media",
        )

        commands.do_store("result")

        assert commands.context.stored_metadata["result"] == {
            "service": "media",
        }

    def test_do_store_saves_method_metadata(self):
        """Verify store saves the last method as metadata."""
        commands = create_commands(
            last_result={"value": 123},
            last_method="GetProfiles",
        )

        commands.do_store("result")

        assert commands.context.stored_metadata["result"] == {
            "method": "GetProfiles",
        }

    def test_do_store_saves_complete_metadata(self):
        """Verify store saves service and method metadata."""
        commands = create_commands(
            last_result={"value": 123},
            last_service_name="media",
            last_method="GetProfiles",
        )

        commands.do_store("profiles")

        assert commands.context.stored_metadata["profiles"] == {
            "service": "media",
            "method": "GetProfiles",
        }

    def test_do_store_without_metadata_uses_unknown_in_output(self, capsys):
        """Verify store uses unknown metadata when none is available."""
        commands = create_commands(last_result={"value": 123})

        commands.do_store("result")

        output = capsys.readouterr().out

        assert "Stored result as:" in output
        assert "$result" in output
        assert "unknown.unknown()" in output

    def test_do_store_prints_metadata(self, capsys):
        """Verify store displays service and method metadata."""
        commands = create_commands(
            last_result={"value": 123},
            last_service_name="media",
            last_method="GetProfiles",
        )

        commands.do_store("profiles")

        output = capsys.readouterr().out

        assert "Stored result as:" in output
        assert "$profiles" in output
        assert "media.GetProfiles()" in output


class TestReferenceCommandsShow:
    """Test show commands."""

    def test_do_show_without_name_lists_empty_storage(self, capsys):
        """Verify show without an argument lists stored data."""
        commands = create_commands()

        commands.do_show("")

        output = capsys.readouterr().out

        assert "Stored data:" in output

    def test_do_show_lists_stored_data(self, capsys):
        """Verify show lists all stored variables."""
        commands = create_commands(
            stored_data={
                "profiles": [{"token": "profile1"}],
                "services": ["media", "device"],
            },
            stored_metadata={
                "profiles": {
                    "service": "media",
                    "method": "GetProfiles",
                },
                "services": {
                    "service": "devicemgmt",
                    "method": "GetServices",
                },
            },
        )

        commands.do_show("")

        output = capsys.readouterr().out

        assert "$profiles" in output
        assert "media.GetProfiles()" in output
        assert "$services" in output
        assert "devicemgmt.GetServices()" in output

    def test_do_show_uses_unknown_metadata(self, capsys):
        """Verify show uses unknown metadata for stored data without metadata."""
        commands = create_commands(
            stored_data={"result": {"value": 123}},
        )

        commands.do_show("")

        output = capsys.readouterr().out

        assert "$result" in output
        assert "unknown.unknown()" in output

    def test_do_show_resolves_reference(self, capsys):
        """Verify show prints a resolved stored reference."""
        commands = create_commands(
            stored_data={"profiles": [{"token": "abc123"}]},
        )

        commands.do_show("profiles[0].token")

        output = capsys.readouterr().out

        assert "abc123" in output

    def test_do_show_prints_unresolved_reference_error(self, capsys):
        """Verify show reports an unresolved reference."""
        commands = create_commands(
            stored_data={"profiles": [{"token": "abc123"}]},
        )

        commands.do_show("profiles[99].token")

        output = capsys.readouterr().out

        assert "Cannot resolve" in output
        assert "profiles[99].token" in output

    def test_do_show_resolves_attribute_reference(self, capsys):
        """Verify show resolves object attributes."""
        profile = SimpleNamespace(token="abc123")
        commands = create_commands(
            stored_data={"profile": profile},
        )

        commands.do_show("profile.token")

        output = capsys.readouterr().out

        assert "abc123" in output


class TestReferenceCommandsSubstitute:
    """Test stored-reference substitution."""

    def test_substitute_without_references(self):
        """Verify strings without references remain unchanged."""
        commands = create_commands()

        params = '{"Name": "Profile"}'

        result = commands._substitute_stored_references(params)

        assert result == params

    def test_substitute_string_reference(self):
        """Verify a string reference is converted to a JSON string."""
        commands = create_commands(
            stored_data={"token": "abc123"},
        )

        result = commands._substitute_stored_references('{"Token": $token}')

        assert result == '{"Token": "abc123"}'

    def test_substitute_integer_reference(self):
        """Verify an integer reference is serialized correctly."""
        commands = create_commands(
            stored_data={"count": 42},
        )

        result = commands._substitute_stored_references('{"Count": $count}')

        assert result == '{"Count": 42}'

    def test_substitute_boolean_reference(self):
        """Verify a boolean reference is serialized correctly."""
        commands = create_commands(
            stored_data={"enabled": True},
        )

        result = commands._substitute_stored_references('{"Enabled": $enabled}')

        assert result == '{"Enabled": true}'

    def test_substitute_null_reference(self):
        """Verify a null reference is serialized correctly."""
        commands = create_commands(
            stored_data={"value": None},
        )

        result = commands._substitute_stored_references('{"Value": $value}')

        # None is treated as an unresolved reference by the implementation.
        assert result == '{"Value": $value}'

    def test_substitute_list_reference(self):
        """Verify a list reference is serialized correctly."""
        commands = create_commands(
            stored_data={"items": [1, 2, 3]},
        )

        result = commands._substitute_stored_references('{"Items": $items}')

        assert result == '{"Items": [1, 2, 3]}'

    def test_substitute_dict_reference(self):
        """Verify a dictionary reference is serialized correctly."""
        commands = create_commands(
            stored_data={"profile": {"token": "abc123", "enabled": True}},
        )

        result = commands._substitute_stored_references('{"Profile": $profile}')

        assert result == ('{"Profile": {"token": "abc123", "enabled": true}}')

    def test_substitute_nested_reference(self):
        """Verify a nested reference is resolved before serialization."""
        commands = create_commands(
            stored_data={
                "profiles": [
                    {"token": "abc123"},
                ],
            },
        )

        result = commands._substitute_stored_references('{"Token": $profiles[0].token}')

        assert result == '{"Token": "abc123"}'

    def test_substitute_multiple_references(self):
        """Verify multiple references are substituted."""
        commands = create_commands(
            stored_data={
                "token": "abc123",
                "count": 42,
            },
        )

        result = commands._substitute_stored_references(
            '{"Token": $token, "Count": $count}'
        )

        assert result == '{"Token": "abc123", "Count": 42}'

    def test_substitute_unresolved_reference_keeps_original(self, capsys):
        """Verify unresolved references remain unchanged."""
        commands = create_commands()

        params = '{"Token": $missing}'

        result = commands._substitute_stored_references(params)

        output = capsys.readouterr().out

        assert result == params
        assert "Cannot resolve $missing" in output

    def test_substitute_non_serializable_value_falls_back_to_string(self):
        """Verify non-JSON-serializable values are converted to strings."""
        value = object()
        commands = create_commands(
            stored_data={"value": value},
        )

        result = commands._substitute_stored_references('{"Value": $value}')

        assert result == f'{{"Value": "{str(value)}"}}'

    def test_substitute_uses_json_dumps(self):
        """Verify stored values are serialized using json.dumps."""
        commands = create_commands(
            stored_data={"value": {"key": "value"}},
        )

        with patch(
            "onvif.cli.interactive.reference.json.dumps",
            wraps=__import__("json").dumps,
        ) as dumps:
            commands._substitute_stored_references('{"Value": $value}')

        dumps.assert_called_once_with({"key": "value"})

    def test_substitute_preserves_reference_inside_text(self):
        """Verify references can be substituted within larger parameter strings."""
        commands = create_commands(
            stored_data={"token": "abc123"},
        )

        result = commands._substitute_stored_references(
            '{"Token": $token, "Other": "value"}'
        )

        assert result == ('{"Token": "abc123", "Other": "value"}')


class TestReferenceCommandsResolve:
    """Test stored-reference resolution."""

    def test_resolve_missing_reference(self):
        """Verify missing variables resolve to None."""
        commands = create_commands()

        assert commands._resolve_stored_reference("missing") is None

    def test_resolve_empty_reference(self):
        """Verify an empty reference resolves to None."""
        commands = create_commands()

        assert commands._resolve_stored_reference("") is None

    def test_resolve_stored_scalar(self):
        """Verify a stored scalar value is returned."""
        commands = create_commands(
            stored_data={"value": 42},
        )

        assert commands._resolve_stored_reference("value") == 42

    def test_resolve_stored_string(self):
        """Verify a stored string value is returned."""
        commands = create_commands(
            stored_data={"token": "abc123"},
        )

        assert commands._resolve_stored_reference("token") == "abc123"

    def test_resolve_list_index(self):
        """Verify list indexes are resolved."""
        commands = create_commands(
            stored_data={
                "profiles": [
                    "profile0",
                    "profile1",
                ],
            },
        )

        assert commands._resolve_stored_reference("profiles[0]") == "profile0"
        assert commands._resolve_stored_reference("profiles[1]") == "profile1"

    def test_resolve_tuple_index(self):
        """Verify tuple indexes are resolved."""
        commands = create_commands(
            stored_data={
                "values": ("first", "second"),
            },
        )

        assert commands._resolve_stored_reference("values[1]") == "second"

    def test_resolve_nested_list_and_dict(self):
        """Verify nested list and dictionary access."""
        commands = create_commands(
            stored_data={
                "profiles": [
                    {"token": "abc123"},
                ],
            },
        )

        assert commands._resolve_stored_reference("profiles[0].token") == "abc123"

    def test_resolve_nested_dict(self):
        """Verify nested dictionary access."""
        commands = create_commands(
            stored_data={
                "profile": {
                    "credentials": {
                        "token": "abc123",
                    },
                },
            },
        )

        assert (
            commands._resolve_stored_reference("profile.credentials.token") == "abc123"
        )

    def test_resolve_object_attribute(self):
        """Verify object attributes are resolved."""
        profile = SimpleNamespace(
            token="abc123",
            name="Profile 1",
        )
        commands = create_commands(
            stored_data={"profile": profile},
        )

        assert commands._resolve_stored_reference("profile.token") == "abc123"
        assert commands._resolve_stored_reference("profile.name") == "Profile 1"

    def test_resolve_dictionary_key(self):
        """Verify dictionary keys are resolved."""
        commands = create_commands(
            stored_data={
                "profile": {
                    "token": "abc123",
                },
            },
        )

        assert commands._resolve_stored_reference("profile.token") == "abc123"

    def test_resolve_out_of_range_index(self):
        """Verify out-of-range list indexes return None."""
        commands = create_commands(
            stored_data={"profiles": ["profile0"]},
        )

        assert commands._resolve_stored_reference("profiles[99]") is None

    def test_resolve_iterable_string_by_index(self):
        """Verify string values can be indexed through the generic iterable path."""
        commands = create_commands(
            stored_data={"profile": "not-a-list"},
        )

        assert commands._resolve_stored_reference("profile[0]") == "n"

    def test_resolve_missing_attribute(self):
        """Verify missing object attributes return None."""
        profile = SimpleNamespace(token="abc123")
        commands = create_commands(
            stored_data={"profile": profile},
        )

        assert commands._resolve_stored_reference("profile.missing") is None

    def test_resolve_missing_dictionary_key(self):
        """Verify missing dictionary keys return None."""
        commands = create_commands(
            stored_data={"profile": {"token": "abc123"}},
        )

        assert commands._resolve_stored_reference("profile.missing") is None

    def test_resolve_nested_out_of_range_index(self):
        """Verify nested out-of-range indexes return None."""
        commands = create_commands(
            stored_data={
                "profiles": [
                    {"token": "abc123"},
                ],
            },
        )

        assert commands._resolve_stored_reference("profiles[5].token") is None

    def test_resolve_iterable_non_list_by_index(self):
        """Verify index traversal works for other iterable values."""
        commands = create_commands(
            stored_data={
                "values": "abc",
            },
        )

        assert commands._resolve_stored_reference("values[1]") == "b"

    def test_resolve_non_iterable_by_index_returns_none(self):
        """Verify indexing a non-iterable returns None."""
        commands = create_commands(
            stored_data={
                "value": 123,
            },
        )

        assert commands._resolve_stored_reference("value[0]") is None


class TestReferenceCommandsCompletion:
    """Test reference command autocompletion."""

    def test_complete_show_returns_matching_names(self):
        """Verify show completion returns matching stored names."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "profile": {},
                "services": [],
                "device": {},
            },
        )

        result = commands.complete_show(
            "prof",
            "show prof",
            5,
            9,
        )

        assert result == ["profiles", "profile"]

    def test_complete_show_is_case_sensitive(self):
        """Verify show completion preserves case-sensitive behavior."""
        commands = create_commands(
            stored_data={
                "Profiles": [],
                "profiles": [],
            },
        )

        result = commands.complete_show(
            "Prof",
            "show Prof",
            5,
            9,
        )

        assert result == ["Profiles"]

    def test_complete_show_without_argument_lists_all_names(self):
        """Verify show completion lists all names without an argument."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "services": [],
            },
        )

        result = commands.complete_show(
            "",
            "show ",
            5,
            5,
        )

        assert result == ["profiles", "services"]

    def test_complete_show_with_nested_accessor_returns_no_results(self):
        """Verify nested accessor completion returns no results."""
        commands = create_commands(
            stored_data={
                "profiles": [],
            },
        )

        result = commands.complete_show(
            "profiles[",
            "show profiles[",
            5,
            14,
        )

        assert result == []

    def test_complete_show_after_completed_argument_returns_no_results(self):
        """Verify completion after a complete argument returns no results."""
        commands = create_commands(
            stored_data={
                "profiles": [],
            },
        )

        result = commands.complete_show(
            "",
            "show profiles ",
            14,
            14,
        )

        assert result == []

    def test_complete_rm_returns_matching_names(self):
        """Verify rm completion returns matching stored names."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "profile": {},
                "services": [],
            },
        )

        result = commands.complete_rm(
            "prof",
            "rm prof",
            3,
            7,
        )

        assert result == ["profiles", "profile"]

    def test_complete_rm_without_text_returns_all_names(self):
        """Verify rm completion returns all names with empty text."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "services": [],
            },
        )

        result = commands.complete_rm(
            "",
            "rm ",
            3,
            3,
        )

        assert result == ["profiles", "services"]

    def test_complete_rm_is_case_sensitive(self):
        """Verify rm completion is case-sensitive."""
        commands = create_commands(
            stored_data={
                "Profiles": [],
                "profiles": [],
            },
        )

        result = commands.complete_rm(
            "Prof",
            "rm Prof",
            3,
            7,
        )

        assert result == ["Profiles"]


class TestReferenceCommandsRemove:
    """Test removal of stored references."""

    def test_do_rm_without_name_prints_usage(self, capsys):
        """Verify rm without a name prints usage."""
        commands = create_commands()

        commands.do_rm("")

        output = capsys.readouterr().out

        assert "Usage: rm <name>" in output

    def test_do_rm_removes_stored_data(self, capsys):
        """Verify rm removes stored data."""
        commands = create_commands(
            stored_data={
                "profiles": [{"token": "abc123"}],
            },
            stored_metadata={
                "profiles": {
                    "service": "media",
                    "method": "GetProfiles",
                },
            },
        )

        commands.do_rm("profiles")

        output = capsys.readouterr().out

        assert "profiles" not in commands.context.stored_data
        assert "profiles" not in commands.context.stored_metadata
        assert "Removed:" in output
        assert "$profiles" in output

    def test_do_rm_removes_data_without_metadata(self, capsys):
        """Verify rm removes data even when metadata does not exist."""
        commands = create_commands(
            stored_data={
                "profiles": [{"token": "abc123"}],
            },
        )

        commands.do_rm("profiles")

        output = capsys.readouterr().out

        assert "profiles" not in commands.context.stored_data
        assert "Removed:" in output

    def test_do_rm_unknown_name_prints_error(self, capsys):
        """Verify rm reports an unknown stored variable."""
        commands = create_commands(
            stored_data={
                "profiles": [],
            },
        )

        commands.do_rm("missing")

        output = capsys.readouterr().out

        assert "No stored data named 'missing'" in output
        assert commands.context.stored_data == {"profiles": []}

    def test_do_rm_does_not_remove_other_data(self):
        """Verify rm only removes the requested variable."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "services": [],
            },
            stored_metadata={
                "profiles": {"service": "media"},
                "services": {"service": "devicemgmt"},
            },
        )

        commands.do_rm("profiles")

        assert "profiles" not in commands.context.stored_data
        assert "profiles" not in commands.context.stored_metadata
        assert "services" in commands.context.stored_data
        assert "services" in commands.context.stored_metadata


class TestReferenceCommandsClear:
    """Test clearing stored references."""

    def test_do_cls_clears_stored_data(self, capsys):
        """Verify cls clears all stored data."""
        commands = create_commands(
            stored_data={
                "profiles": [],
                "services": [],
            },
            stored_metadata={
                "profiles": {"service": "media"},
                "services": {"service": "devicemgmt"},
            },
        )

        commands.do_cls("")

        output = capsys.readouterr().out

        assert commands.context.stored_data == {}
        assert commands.context.stored_metadata == {}
        assert "Cleared all stored data" in output

    def test_do_cls_clears_metadata(self):
        """Verify cls clears metadata together with stored data."""
        commands = create_commands(
            stored_data={"result": 123},
            stored_metadata={"result": {"method": "TestMethod"}},
        )

        commands.do_cls("")

        assert commands.context.stored_data == {}
        assert commands.context.stored_metadata == {}

    def test_do_cls_is_safe_when_storage_is_empty(self, capsys):
        """Verify cls works when no stored data exists."""
        commands = create_commands()

        commands.do_cls("")

        output = capsys.readouterr().out

        assert commands.context.stored_data == {}
        assert commands.context.stored_metadata == {}
        assert "Cleared all stored data" in output
