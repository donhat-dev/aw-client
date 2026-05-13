from __future__ import annotations

import json
from typing import Any, Dict, Optional

ODOO_CONFIG_SETTING = "odoo_config"

_ODOO_CONFIG_FIELDS = {
    "enabled",
    "base_url",
    "pin_code",
    "token",
    "api_secret",
    "sign_requests",
    "employee_id",
    "device_id",
    "device_name",
    "timeout_secs",
    "push_screenshots",
    "push_metadata_events",
}

_SECRET_FIELDS = {"pin_code", "token", "api_secret"}


def normalize_odoo_config(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        return {}

    normalized: Dict[str, Any] = {}
    for key, value in raw.items():
        if key == "odoo_url":
            normalized["base_url"] = value
        elif key in _ODOO_CONFIG_FIELDS:
            normalized[key] = value

    return normalized


def load_global_odoo_config(client: Any, logger: Any = None) -> Optional[Dict[str, Any]]:
    try:
        raw = client.get_setting(ODOO_CONFIG_SETTING)
    except Exception as exc:
        if logger:
            logger.debug("Unable to load /api/0/settings/%s: %s", ODOO_CONFIG_SETTING, exc)
        return None

    config = normalize_odoo_config(raw)
    if not config:
        return None
    return config


def apply_global_odoo_config(odoo_config: Any, client: Any, logger: Any = None, source: str = "") -> bool:
    global_config = load_global_odoo_config(client, logger=logger)
    if not global_config:
        return False

    changed = False
    fingerprint = json.dumps(global_config, sort_keys=True, default=str)
    previous_fingerprint = getattr(odoo_config, "_aw_global_odoo_fingerprint", None)
    for key, value in global_config.items():
        if not hasattr(odoo_config, key):
            continue
        if getattr(odoo_config, key) != value:
            setattr(odoo_config, key, value)
            changed = True

    if previous_fingerprint != fingerprint:
        setattr(odoo_config, "_aw_global_odoo_fingerprint", fingerprint)

    if logger and (changed or previous_fingerprint != fingerprint):
        logger.info(
            "Loaded global Odoo config from /api/0/settings/%s%s: %s",
            ODOO_CONFIG_SETTING,
            f" for {source}" if source else "",
            summarize_odoo_config(odoo_config),
        )
    return changed


def odoo_config_fingerprint(odoo_config: Any) -> str:
    payload = {
        key: getattr(odoo_config, key)
        for key in sorted(_ODOO_CONFIG_FIELDS)
        if hasattr(odoo_config, key)
    }
    return json.dumps(payload, sort_keys=True, default=str)


def summarize_odoo_config(odoo_config: Any) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for key in sorted(_ODOO_CONFIG_FIELDS):
        if not hasattr(odoo_config, key):
            continue
        value = getattr(odoo_config, key)
        summary[key] = mask_secret(value) if key in _SECRET_FIELDS else value
    return summary


def mask_secret(value: Any, visible: int = 4) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    if visible <= 0:
        return "*" * len(text)
    if len(text) <= visible:
        return "*" * len(text)
    return "*" * (len(text) - visible) + text[-visible:]
