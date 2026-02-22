"""Tests pour MQTT Entity Bridge."""
import asyncio
from unittest.mock import Mock, patch, AsyncMock

import pytest

from custom_components.mqtt_entity_bridge import (
    DOMAIN,
    async_setup,
    async_setup_entry,
)


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    mock_hass = Mock()
    mock_hass.data = {}
    mock_hass.states = Mock()
    mock_hass.states.get = Mock(return_value=None)
    mock_hass.states.async_all = Mock(return_value=[])
    mock_hass.services = Mock()
    mock_hass.services.async_register = AsyncMock()
    mock_hass.create_task = Mock()
    return mock_hass


@pytest.fixture
def config_entry():
    """Mock ConfigEntry."""
    entry = Mock()
    entry.data = {
        "host": "192.168.1.100",
        "port": 1883,
        "username": "test_user",
        "password": "test_pass",
        "topic_prefix": "homeassistant",
    }
    return entry


@pytest.mark.asyncio
async def test_async_setup_with_config(hass):
    """Test async_setup with config."""
    config = {DOMAIN: {}}
    result = await async_setup(hass, config)
    assert result is True


@pytest.mark.asyncio
async def test_async_setup_without_config(hass):
    """Test async_setup without config."""
    config = {}
    result = await async_setup(hass, config)
    assert result is True


@pytest.mark.asyncio
@patch("custom_components.mqtt_entity_bridge.MQTTEntityBridge")
async def test_async_setup_entry(mock_mqtt_class, hass, config_entry):
    """Test async_setup_entry."""
    mock_client = AsyncMock()
    mock_mqtt_class.return_value = mock_client

    result = await async_setup_entry(hass, config_entry)

    assert result is True
    assert DOMAIN in hass.data
    assert hass.services.async_register.call_count >= 3  # 3 services registered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
