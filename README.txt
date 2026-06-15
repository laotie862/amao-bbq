# Amao BBQ Order System

## 二维码
| 场景 | 顾客扫码 | 厨房扫码 |
|------|---------|---------|
| 🏠 局域网 (同 WiFi) | qr-lan/customer-lan.png | qr-lan/kitchen-lan.png |
| 🌐 公网 (4G/5G 随时) | qr-public/customer-public.png | qr-public/kitchen-public.png |

## 文件
- `amao-bbq-swipe.html` — 顾客点单页
- `kitchen.html` — 厨房看板
- `server.py` — 本地服务器 (可选，公网不需要)

## 部署
- 公网: https://laotie862.github.io/amao-bbq/
- 数据库: Supabase (kpdzliicwddunewzhwqm)
- 局域网和公网共享同一个数据库，订单互通
