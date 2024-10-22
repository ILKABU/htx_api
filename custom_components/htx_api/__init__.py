"""HTX API integration for Home Assistant."""
# ... (предыдущие импорты остаются теми же)

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

    def _format_number(self, number: float) -> float:
        """Format number to 2 decimal places."""
        return round(float(number), 2)

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
                    "price": self._format_number(item["price"]),
                    "available": self._format_number(item["tradeCount"]),
                    "min_limit": self._format_number(item["minTradeLimit"]),
                    "max_limit": self._format_number(item["maxTradeLimit"]),
                    "raw_data": item,
                    "last_update": datetime.now().isoformat()
                }
            else:
                result[method] = None
                
        return result

    async def async_shutdown(self):
        """Close HTTP session."""
        await self.http_session.close()
