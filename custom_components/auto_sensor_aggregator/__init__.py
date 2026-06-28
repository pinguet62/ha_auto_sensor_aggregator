import logging

from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "auto_sensor_aggregator"


async def async_setup(hass, config):
    _LOGGER.info("Initialisation de auto_sensor_aggregator")
    hass.async_create_task(
        discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )
    return True
