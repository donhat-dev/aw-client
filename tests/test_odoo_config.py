from dataclasses import dataclass

from aw_client.odoo_config import apply_global_odoo_config, mask_secret, normalize_odoo_config


@dataclass
class DummyOdooConfig:
    enabled: bool = False
    base_url: str = ""
    push_metadata_events: bool = False


class DummyClient:
    def __init__(self, setting):
        self.setting = setting

    def get_setting(self, key):
        return self.setting


def test_normalize_odoo_config_maps_public_url_to_base_url():
    assert normalize_odoo_config(
        {
            "enabled": True,
            "odoo_url": "https://odoo.example.com",
            "pin_code": "1234",
            "token": "secret",
            "public_user": {"name": "Ignored"},
        }
    ) == {
        "enabled": True,
        "base_url": "https://odoo.example.com",
        "pin_code": "1234",
        "token": "secret",
    }


def test_mask_secret_keeps_tail_only():
    assert mask_secret("abcdef") == "**cdef"


def test_apply_global_odoo_config_can_ignore_component_owned_fields():
    config = DummyOdooConfig()

    changed = apply_global_odoo_config(
        config,
        DummyClient(
            {
                "enabled": True,
                "odoo_url": "https://odoo.example.com",
                "push_metadata_events": True,
            }
        ),
        ignored_fields={"push_metadata_events"},
    )

    assert changed is True
    assert config.enabled is True
    assert config.base_url == "https://odoo.example.com"
    assert config.push_metadata_events is False
