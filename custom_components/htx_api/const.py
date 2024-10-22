"""Constants for HTX API integration."""
from datetime import timedelta

DOMAIN = "htx_api"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=20)  # Изменено с 1 секунды на 20 секунд
CONF_SCAN_INTERVAL = "scan_interval"

PAYMENT_METHODS = {
    "28": "Тинькофф",
    "29": "Сбербанк",
    "36": "Райффайзенбанк",
    "69": "СБП",
    "70": "Переводы в определенный банк",
    "75": "СБП",
    "45": "ОТП Банк",
    "351": "Газпромбанк"
}

TARGET_PAYMENT_METHODS = ["Сбербанк", "Тинькофф", "Райффайзенбанк", "СБП"]
BASE_URL = "https://otc-api.trygofast.com/v1/data/trade-market"
