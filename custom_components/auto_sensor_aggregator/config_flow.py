import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector, SelectSelectorConfig, SelectSelectorMode, SelectOptionDict,
    TextSelector, TextSelectorConfig, TextSelectorType)
from typing import Any

from .const import (
    CONF_FILTER_KEY, CONF_FILTER_DEFAULT, CONF_FILTER_VALUE_ALL, CONF_FILTER_VALUE_INCLUDE, CONF_FILTER_VALUE_EXCLUDE,
    CONF_LABEL_KEY)

DOMAIN = "auto_sensor_aggregator"


class AvgTemperatureConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:  # submit
            return self.async_create_entry(title="Auto sensor aggregator", data=user_input)
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AvgTemperatureOptionsFlowHandler()


class AvgTemperatureOptionsFlowHandler(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        current_filter = self.config_entry.options.get(CONF_FILTER_KEY, CONF_FILTER_DEFAULT)
        current_label = self.config_entry.options.get(CONF_LABEL_KEY, "")

        if user_input is not None:  # submit
            selected_mode = user_input.get(CONF_FILTER_KEY)
            select_label = user_input.get(CONF_LABEL_KEY, "").strip()
            if selected_mode in (CONF_FILTER_VALUE_INCLUDE, CONF_FILTER_VALUE_EXCLUDE) and not select_label:
                errors[CONF_LABEL_KEY] = "Please define the label"

            if not errors:
                return self.async_create_entry(title="Auto sensor aggregator", data=user_input)

            current_filter = selected_mode
            current_label = select_label

        schema_dict: dict[Any, Any] = {
            vol.Required(CONF_FILTER_KEY, default=current_filter): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=CONF_FILTER_VALUE_ALL,
                                         label="All sensors"),
                        SelectOptionDict(value=CONF_FILTER_VALUE_INCLUDE,
                                         label="Only sensors annotated with following label"),
                        SelectOptionDict(value=CONF_FILTER_VALUE_EXCLUDE,
                                         label="Except sensors annotated with following label")],
                    mode=SelectSelectorMode.DROPDOWN)),
        }
        if current_filter in (CONF_FILTER_VALUE_INCLUDE, CONF_FILTER_VALUE_EXCLUDE):
            schema_dict[vol.Required(CONF_LABEL_KEY, default=current_label)] = TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True))

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict), errors=errors)
