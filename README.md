# HTX API Integration for Home Assistant

This integration allows you to monitor HTX P2P market prices directly in Home Assistant.

## Features

- Real-time monitoring of HTX P2P USDT/RUB prices
- Support for multiple payment methods (Sberbank, Tinkoff, Raiffeisen, SBP)
- Both buy and sell orders monitoring
- Automatic updates every minute

## Installation

### HACS Installation
1. Open HACS in your Home Assistant instance
2. Click on "Custom repositories"
3. Add this repository URL with category "Integration"
4. Click "Install"
5. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/htx_api` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings -> Devices & Services
2. Click "Add Integration"
3. Search for "HTX API"
4. Click to install

## Available Sensors

The integration creates the following sensors:
- HTX Buy [Payment Method] Price
- HTX Sell [Payment Method] Price

Each sensor includes attributes for:
- Available amount
- Minimum limit
- Maximum limit

## Usage Example

You can use these sensors in automations, scripts, or display them in your dashboard:

```yaml
type: entities
title: HTX P2P USDT/RUB
entities:
  - entity: sensor.htx_sell_sberbank
  - entity: sensor.htx_sell_tinkoff
  - entity: sensor.htx_buy_sberbank
  - entity: sensor.htx_buy_tinkoff
```

## Support

If you have any issues or feature requests, please open an issue on GitHub.
