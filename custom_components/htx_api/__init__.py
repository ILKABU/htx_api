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
            
    # Фильтруем данные по минимальному лимиту и исключенным пользователям
    filtered_data = [
        item for item in all_data 
        if float(item["minTradeLimit"]) >= 10000 
        and item.get("userName") not in EXCLUDED_USERS
    ]
    
    _LOGGER.debug(
        "Filtered data: total=%d, after_limit_filter=%d, after_user_filter=%d",
        len(all_data),
        len([item for item in all_data if float(item["minTradeLimit"]) >= 10000]),
        len(filtered_data)
    )
    
    return filtered_data
