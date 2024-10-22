"""HTX API integration for Home Assistant."""
from datetime import timedelta
import logging
import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
    PAYMENT_METHODS,
    TARGET_PAYMENT_METHODS,
    BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HTX API from a config entry."""
    coordinator = HTXDataUpdateCoordinator(
        hass,
        update_interval=timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()))
    )
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Error setting up HTX API integration: %s", err)
        return False
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok

class HTXDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching HTX API data."""

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: timedelta = DEFAULT_SCAN_INTERVAL,
    ):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.http_session = aiohttp.ClientSession()

    async def _async_update_data(self):
        """Fetch data from HTX API."""
        try:
            buy_data = await self._fetch_htx_data("buy")
            sell_data = await self._fetch_htx_data("sell")
            
            return {
                "buy": self._process_data(buy_data, False),
                "sell": self._process_data(sell_data, True)
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with HTX API: {err}")

    async def _fetch_htx_data(self, trade_type: str) -> list:
        """Fetch data from HTX API."""
        all_data = []
        page = 1
        
        while page <= 10:  # Limit to 10 pages
            params = {
                "coinId": "2",
                "currency": "11",
                "tradeType": trade_type,
                "currPage": str(page),
                "payMethod": "0",
                "acceptOrder": "0",
                "blockType": "general",
                "online": "1",
                "range": "0",
                "onlyTradable": "false",
                "isFollowed": "false"
            }
            
            try:
                async with self.http_session.get(BASE_URL, params=params) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"API returned {response.status}")
                    
                    data = await response.json()
                    if not data.get("data"):
                        break
                        
                    all_data.extend(data["data"])
                    page += 1
            except Exception as err:
                _LOGGER.error("Error fetching data from HTX API: %s", err)
                break
                
        return [item for item in all_data if float(item["minTradeLimit"]) >= 10000]

    def _process_data(self, data: list, is_sell: bool) -> dict:
        """Process and sort HTX data."""
        result = {}
        
        # Sort by price
        data.sort(key=lambda x: float(x["price"]), 
                 reverse=not is_sell)
        
        for method in TARGET_PAYMENT_METHODS:
            relevant_items = [
                item for item in data
                if any(method.lower() in self._get_payment_method_names(pm, pms).lower()
                      for pm, pms in [(item.get("payMethod"), item.get("payMethods"))])
            ]
            
            if relevant_items:
                item = relevant_items[0]  # Get best offer
                result[method] = {
                    "price": float(item["price"]),
                    "available": float(item["tradeCount"]),
                    "min_limit": float(item["minTradeLimit"]),
                    "max_limit": float(item["maxTradeLimit"]),
                    "raw_data": item
                }
            else:
                result[method] = None
                
        return result

    def _get_payment_method_names(self, pay_method, pay_methods):
        """Get payment method names from codes."""
        if pay_methods and isinstance(pay_methods, list):
            return ", ".join(PAYMENT_METHODS.get(str(m["payMethodId"]), m["name"]) 
                           for m in pay_methods)
        elif pay_method:
            return ", ".join(PAYMENT_METHODS.get(id_str, id_str) 
                           for id_str in pay_method.split(","))
        return "Неизвестный метод"

    async def async_shutdown(self):
        """Close HTTP session."""
        await self.http_session.close()
