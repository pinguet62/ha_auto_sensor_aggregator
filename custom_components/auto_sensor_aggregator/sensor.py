import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info("Initialisation de sensor")
    async_add_entities([SampleSensor()], True)


class SampleSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "Sample Sensor"
        self._attr_unique_id = "auto_sensor_aggregator_sensor_id_001"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_native_value = "42"

    async def async_update(self):
        pass
