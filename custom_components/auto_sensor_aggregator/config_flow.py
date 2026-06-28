from homeassistant.config_entries import ConfigFlow

DOMAIN = "auto_sensor_aggregator"


class SampleConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Auto sensor aggregator", data={})
