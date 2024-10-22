"""Sensor platform for HTX API integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN, TARGET_PAYMENT_METHODS

CURRENCY_RUBLE = "RUB"

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HTX API sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for trade_type in ["buy", "sell"]:
        for payment_method in TARGET_PAYMENT_METHODS:
            sensors.append(HTXPriceSensor(
                coordinator,
                trade_type,
                payment_method,
            ))

    async_add_entities(sensors)

class HTXPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HTX API price sensor."""

    def __init__(
        self,
        coordinator,
        trade_type: str,
        payment_method: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.trade_type = trade_type
        self.payment_method = payment_method
        
        self._attr_name = f"HTX {trade_type.title()} {payment_method}"
        self._attr_unique_id = f"htx_api_{trade_type}_{payment_method.lower()}"
        self._attr_native_unit_of_measurement = CURRENCY_RUBLE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:currency-rub"
        self.entity_id = f"sensor.htx_{trade_type}_{payment_method.lower()}".replace(" ", "_")

    def _format_value(self, value):
        """Format numeric value to 2 decimal places."""
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return value

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data[self.trade_type].get(self.payment_method)
        if data is None:
            return None
        return self._format_value(data["price"])

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data[self.trade_type].get(self.payment_method)
        if data is None:
            return {
                "available": None,
                "min_limit": None,
                "max_limit": None,
            }
        
        return {
            "available": self._format_value(data["available"]),
            "min_limit": self._format_value(data["min_limit"]),
            "max_limit": self._format_value(data["max_limit"]),
        }
