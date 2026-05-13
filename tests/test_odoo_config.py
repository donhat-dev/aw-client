from aw_client.odoo_config import mask_secret, normalize_odoo_config


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
