"""Sensor platform for HTX API integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_RUBLE

from .const import DOMAIN, TARGET_PAYMENT_METHODS
from . import HTXDataUpdateCoordinator

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

class HTXPriceSensor(SensorEntity, CoordinatorEntity):
    """Representation of a HTX API price sensor."""

    def __init__(
        self,
        coordinator: HTXDataUpdateCoordinator,
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

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data[self.trade_type].get(self.payment_method)
        if data is None:
            return None
        return data["price"]

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
            "available": data["available"],
            "min_limit": data["min_limit"],
            "max_limit": data["max_limit"],
        }
