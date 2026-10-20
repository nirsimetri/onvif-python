"""Tests for ONVIF WSDL utilities."""

import os

import pytest

from onvif.utils.wsdl import ONVIFWSDL


class TestSetCustomWsdlDir:
    """Test global custom WSDL directory configuration."""

    def test_sets_custom_directory(self, tmp_path):
        """Test setting the global custom WSDL directory."""
        ONVIFWSDL.set_custom_wsdl_dir(os.fspath(tmp_path))

        assert ONVIFWSDL.get_custom_wsdl_dir() == os.fspath(tmp_path)

        ONVIFWSDL.clear_custom_wsdl_dir()

    def test_clears_custom_directory(self, tmp_path):
        """Test clearing the global custom WSDL directory."""
        ONVIFWSDL.set_custom_wsdl_dir(os.fspath(tmp_path))

        ONVIFWSDL.clear_custom_wsdl_dir()

        assert ONVIFWSDL.get_custom_wsdl_dir() is None


# pylint: disable=protected-access
class TestGetBaseDir:
    """Test WSDL base directory resolution."""

    def test_uses_per_call_directory(self, tmp_path, monkeypatch):
        """Test that a per-call directory takes priority."""
        global_dir = tmp_path / "global"
        per_call_dir = tmp_path / "per-call"

        monkeypatch.setattr(
            ONVIFWSDL,
            "_custom_wsdl_dir",
            os.fspath(global_dir),
        )

        result = ONVIFWSDL._get_base_dir(os.fspath(per_call_dir))

        assert result == os.fspath(per_call_dir)

    def test_uses_global_directory(self, tmp_path, monkeypatch):
        """Test that the global custom directory is used."""
        custom_dir = tmp_path / "custom"

        monkeypatch.setattr(
            ONVIFWSDL,
            "_custom_wsdl_dir",
            os.fspath(custom_dir),
        )

        assert ONVIFWSDL._get_base_dir() == os.fspath(custom_dir)

    def test_uses_builtin_directory(self, monkeypatch):
        """Test that the built-in WSDL directory is used by default."""
        monkeypatch.setattr(ONVIFWSDL, "_custom_wsdl_dir", None)
        monkeypatch.setattr(ONVIFWSDL, "BASE_DIR", "/builtin/wsdl")

        assert ONVIFWSDL._get_base_dir() == "/builtin/wsdl"


# pylint: disable=protected-access
class TestGetWsdlMap:
    """Test WSDL map generation."""

    def test_builds_builtin_map(self, monkeypatch):
        """Test building the WSDL map from the built-in directory."""
        monkeypatch.setattr(ONVIFWSDL, "_custom_wsdl_dir", None)
        monkeypatch.setattr(ONVIFWSDL, "BASE_DIR", "/builtin/wsdl")

        wsdl_map = ONVIFWSDL._get_wsdl_map()

        assert wsdl_map
        assert "devicemgmt" in wsdl_map
        assert "media" in wsdl_map
        assert "ptz" in wsdl_map

    def test_builds_custom_flat_map(self, tmp_path, monkeypatch):
        """Test building the WSDL map from a custom flat directory."""
        monkeypatch.setattr(ONVIFWSDL, "_custom_wsdl_dir", None)

        wsdl_map = ONVIFWSDL._get_wsdl_map(os.fspath(tmp_path))

        assert wsdl_map
        assert wsdl_map["devicemgmt"]["ver10"]["path"] == os.path.join(
            os.fspath(tmp_path),
            "devicemgmt.wsdl",
        )
        assert wsdl_map["media"]["ver10"]["path"] == os.path.join(
            os.fspath(tmp_path),
            "media.wsdl",
        )
        assert wsdl_map["ptz"]["ver20"]["path"] == os.path.join(
            os.fspath(tmp_path),
            "ptz.wsdl",
        )

    def test_uses_global_custom_directory(self, tmp_path, monkeypatch):
        """Test that the global custom directory is used for the WSDL map."""
        monkeypatch.setattr(
            ONVIFWSDL,
            "_custom_wsdl_dir",
            os.fspath(tmp_path),
        )

        wsdl_map = ONVIFWSDL._get_wsdl_map()

        assert wsdl_map["media"]["ver10"]["path"] == os.path.join(
            os.fspath(tmp_path),
            "media.wsdl",
        )

    def test_contains_expected_services(self, monkeypatch):
        """Test that the WSDL map contains the supported services."""
        monkeypatch.setattr(ONVIFWSDL, "_custom_wsdl_dir", None)

        wsdl_map = ONVIFWSDL._get_wsdl_map()

        expected_services = {
            "devicemgmt",
            "events",
            "pullpoint",
            "notification",
            "subscription",
            "pausable_subscription",
            "accesscontrol",
            "accessrules",
            "actionengine",
            "advancedsecurity",
            "jwt",
            "keystore",
            "tlsserver",
            "dot1x",
            "authorizationserver",
            "mediasigning",
            "analytics",
            "ruleengine",
            "analyticsdevice",
            "appmgmt",
            "authenticationbehavior",
            "credential",
            "deviceio",
            "display",
            "doorcontrol",
            "imaging",
            "media",
            "media2",
            "provisioning",
            "ptz",
            "receiver",
            "recording",
            "replay",
            "schedule",
            "search",
            "thermal",
            "uplink",
        }

        assert expected_services <= wsdl_map.keys()

    def test_definitions_have_required_fields(self, monkeypatch):
        """Test that every WSDL definition has the required fields."""
        monkeypatch.setattr(ONVIFWSDL, "_custom_wsdl_dir", None)

        wsdl_map = ONVIFWSDL._get_wsdl_map()

        for versions in wsdl_map.values():
            for definition in versions.values():
                assert {"path", "binding", "namespace"} <= definition.keys()


# pylint: disable=protected-access
class TestEnsureWsdlMapInitialized:
    """Test lazy WSDL map initialization."""

    def test_preserves_existing_map(self, monkeypatch):
        """Test that an existing WSDL map is not replaced."""
        wsdl_map = {
            "custom": {
                "ver10": {
                    "path": "/custom.wsdl",
                    "binding": "CustomBinding",
                    "namespace": "urn:custom",
                }
            }
        }

        monkeypatch.setattr(ONVIFWSDL, "WSDL_MAP", wsdl_map)

        ONVIFWSDL._ensure_wsdl_map_initialized()

        assert ONVIFWSDL.WSDL_MAP is wsdl_map


class TestGetWsdlMapAccessor:
    """Test the public WSDL map accessor."""

    def test_returns_existing_map(self, monkeypatch):
        """Test returning an already initialized WSDL map."""
        wsdl_map = {
            "media": {
                "ver10": {
                    "path": "/media.wsdl",
                    "binding": "MediaBinding",
                    "namespace": "urn:media",
                }
            }
        }

        monkeypatch.setattr(ONVIFWSDL, "WSDL_MAP", wsdl_map)

        assert ONVIFWSDL.get_wsdl_map() is wsdl_map

    def test_initializes_missing_map(self, monkeypatch):
        """Test that get_wsdl_map initializes a missing map."""
        monkeypatch.setattr(ONVIFWSDL, "WSDL_MAP", None)

        result = ONVIFWSDL.get_wsdl_map()

        assert result is ONVIFWSDL.WSDL_MAP
        assert result

    def test_raises_when_map_is_not_initialized(self, monkeypatch):
        """Test that get_wsdl_map raises when initialization fails."""
        monkeypatch.setattr(ONVIFWSDL, "WSDL_MAP", None)
        monkeypatch.setattr(
            ONVIFWSDL,
            "_ensure_wsdl_map_initialized",
            lambda: None,
        )

        with pytest.raises(
            RuntimeError,
            match="WSDL map was not initialized",
        ):
            ONVIFWSDL.get_wsdl_map()


class TestGetDefinition:
    """Test WSDL definition lookup."""

    def test_returns_builtin_definition(self):
        """Test retrieving an existing built-in WSDL definition."""
        definition = ONVIFWSDL.get_definition("media")

        assert definition
        assert definition["binding"] == "MediaBinding"
        assert definition["namespace"] == ("http://www.onvif.org/ver10/media/wsdl")
        assert os.path.exists(definition["path"])

    def test_returns_versioned_definition(self):
        """Test retrieving a definition for a specific version."""
        definition = ONVIFWSDL.get_definition("media2", "ver20")

        assert definition
        assert definition["binding"] == "Media2Binding"
        assert definition["namespace"] == ("http://www.onvif.org/ver20/media/wsdl")
        assert os.path.exists(definition["path"])

    def test_returns_custom_definition(self, tmp_path):
        """Test retrieving a definition from a custom WSDL directory."""
        wsdl_file = tmp_path / "media.wsdl"
        wsdl_file.write_text("<definitions />", encoding="utf-8")

        definition = ONVIFWSDL.get_definition(
            "media",
            custom_wsdl_dir=os.fspath(tmp_path),
        )

        assert definition["path"] == os.fspath(wsdl_file)
        assert definition["binding"] == "MediaBinding"

    def test_per_call_directory_overrides_global_directory(self, tmp_path):
        """Test that a per-call directory takes priority."""
        global_dir = tmp_path / "global"
        per_call_dir = tmp_path / "per-call"

        global_dir.mkdir()
        per_call_dir.mkdir()

        global_file = global_dir / "media.wsdl"
        per_call_file = per_call_dir / "media.wsdl"

        global_file.write_text("<global />", encoding="utf-8")
        per_call_file.write_text("<per-call />", encoding="utf-8")

        ONVIFWSDL.set_custom_wsdl_dir(os.fspath(global_dir))

        try:
            definition = ONVIFWSDL.get_definition(
                "media",
                custom_wsdl_dir=os.fspath(per_call_dir),
            )
        finally:
            ONVIFWSDL.clear_custom_wsdl_dir()

        assert definition["path"] == os.fspath(per_call_file)

    def test_raises_for_unknown_service(self, monkeypatch):
        """Test that an unknown service raises ValueError."""
        monkeypatch.setattr(
            ONVIFWSDL,
            "WSDL_MAP",
            {
                "media": {
                    "ver10": {
                        "path": "/media.wsdl",
                        "binding": "MediaBinding",
                        "namespace": "urn:media",
                    }
                }
            },
        )

        with pytest.raises(
            ValueError,
            match="Unknown service: unknown",
        ):
            ONVIFWSDL.get_definition("unknown")

    def test_raises_for_unknown_version(self, monkeypatch):
        """Test that an unavailable version raises ValueError."""
        monkeypatch.setattr(
            ONVIFWSDL,
            "WSDL_MAP",
            {
                "media": {
                    "ver10": {
                        "path": "/media.wsdl",
                        "binding": "MediaBinding",
                        "namespace": "urn:media",
                    }
                }
            },
        )

        with pytest.raises(
            ValueError,
            match="Version ver20 not available for media",
        ):
            ONVIFWSDL.get_definition("media", "ver20")

    def test_raises_for_missing_wsdl_file(self, monkeypatch):
        """Test that a missing WSDL file raises FileNotFoundError."""
        monkeypatch.setattr(
            ONVIFWSDL,
            "WSDL_MAP",
            {
                "media": {
                    "ver10": {
                        "path": "/does/not/exist/media.wsdl",
                        "binding": "MediaBinding",
                        "namespace": "urn:media",
                    }
                }
            },
        )

        with pytest.raises(
            FileNotFoundError,
            match="WSDL file not found",
        ):
            ONVIFWSDL.get_definition("media")

    def test_raises_when_map_initialization_fails(self, monkeypatch):
        """Test that get_definition raises when map initialization fails."""
        monkeypatch.setattr(ONVIFWSDL, "WSDL_MAP", None)
        monkeypatch.setattr(
            ONVIFWSDL,
            "_ensure_wsdl_map_initialized",
            lambda: None,
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to initialize WSDL map",
        ):
            ONVIFWSDL.get_definition("media")

    def test_raises_when_custom_map_initialization_fails(self, monkeypatch):
        """Test that get_definition raises when a custom map is unavailable."""
        monkeypatch.setattr(
            ONVIFWSDL,
            "_get_wsdl_map",
            lambda _custom_dir: None,
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to initialize WSDL map",
        ):
            ONVIFWSDL.get_definition(
                "media",
                custom_wsdl_dir="/custom",
            )
