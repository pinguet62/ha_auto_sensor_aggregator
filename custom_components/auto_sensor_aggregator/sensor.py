import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, Event, EventStateChangedData
from homeassistant.helpers import entity_registry as get_entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from typing import List

from .const import CONF_FILTER_KEY, CONF_FILTER_DEFAULT, CONF_LABEL_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info("Initialisation de AvgTemperatureSensorEntity")
    # TODO pressure & humidite
    async_add_entities([AvgTemperatureSensorEntity(hass, config_entry)], True)


class AvgTemperatureSensorEntity(SensorEntity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.__hass = hass
        self.__config_entry = config_entry

        self._attr_name = "Temperature AVG"  # TODO parameterizable
        self._attr_unique_id = "autosensoraggregator_temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_value: float | None = None

        self._attr_should_poll = False  # event based

    async def async_added_to_hass(self) -> None:
        entity_ids = self.__list_tracked_entity_ids()
        if entity_ids:
            unsub = async_track_state_change_event(self.__hass, entity_ids, self.__async_sensor_changed)
            self.async_on_remove(unsub)

    async def __async_sensor_changed(self, event: Event[EventStateChangedData]) -> None:
        self.__recalculate_average(self.__list_tracked_entity_ids())
        self.async_write_ha_state()

    def __list_tracked_entity_ids(self) -> List[SensorEntity]:
        entity_registry = get_entity_registry.async_get(self.__hass)
        list = []
        for state in self.__hass.states.async_all("sensor"):
            if state.entity_id == self.entity_id:
                continue  # ignore itself
            if state.attributes.get("device_class") != self._attr_device_class:
                continue

            entity_entry = entity_registry.async_get(state.entity_id)
            if entity_entry and entity_entry.labels:
                labels = entity_entry.labels
            else:
                labels = {}
            filter = self.__config_entry.options.get(CONF_FILTER_KEY, CONF_FILTER_DEFAULT)
            label = self.__config_entry.options.get(CONF_LABEL_KEY, None)
            if filter is CONF_FILTER_VALUE_ALL:
                accepted = True
            elif filter is CONF_FILTER_VALUE_INCLUDE:
                accepted = label in labels
            elif filter is CONF_FILTER_VALUE_EXCLUDE:
                accepted = label not in labels
            else:
                raise Error(f"Unknown filter {filter}")
            if not accepted:
                continue

            list.append(state.entity_id)

        return list

    def __recalculate_average(self, entity_ids: list[str]) -> None:
        values: list[float] = []

        for entity_id in entity_ids:
            state = self.__hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable"): continue
            try:
                value = float(state.state)
            except ValueError:
                continue
            values.append(value)

        if not values:
            self._attr_native_value = None
        else:
            precision = 2  # TODO precision depending max(precision(entity_ids))
            self._attr_native_value = round(sum(values) / len(values), precision)
