# 🛡️ Gerçek Zamanlı E-Ticaret Anomali ve Fraud Tespit Platformu

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600?logo=rabbitmq&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

**E-ticaret platformunda gerçekleşen işlemleri toplayan, analiz eden, anomali tespit eden ve yapay zeka ajanlarına MCP üzerinden sunan web tabanlı platform.**

</div>

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Teknoloji Seçimleri](#-teknoloji-seçimleri)
- [Kurulum](#-kurulum)
- [Kullanım Rehberi](#-kullanım-rehberi)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [MCP Dokümantasyonu](#-mcp-dokümantasyonu)
- [Script Kullanımı](#-script-kullanımı)
- [Anomali Tespit Kuralları](#-anomali-tespit-kuralları)
- [Sorun Giderme](#-sorun-giderme)

---

## 🎯 Proje Hakkında

Bu platform, e-ticaret işlemlerini gerçek zamanlı olarak izler ve **3 farklı kural** kullanarak şüpheli aktiviteleri tespit eder:

- ⚡ **Hız Kontrolü**: Aynı kullanıcıdan kısa sürede çok fazla işlem
- 💰 **Tutar Kontrolü**: Kullanıcı ortalamasının çok üzerinde tutar
- 🌍 **Konum Kontrolü**: Fiziksel olarak imkansız seyahat (ör: 5 dk arayla İstanbul → Van)

**En az 2 kural ihlal edildiğinde** işlem şüpheli olarak işaretlenir.

---

## 🏗️ Sistem Mimarisi

```
┌─────────────┐         ┌──────────────┐         ┌───────────┐
│   Frontend   │◄──WS──►│  API Gateway  │◄──SQL──►│ PostgreSQL │
│  React/Vite  │        │   FastAPI     │         └───────────┘
└─────────────┘         └──────┬───────┘                │
                               │                         │
                        ┌──────▼───────┐                │
                        │   RabbitMQ    │                │
                        └──────┬───────┘                │
                               │                         │
                        ┌──────▼───────┐         ┌──────▼──────┐
                        │    Worker     │◄──────►│    Redis     │
                        │ Anomali Tespit│         │   Cache      │
                        └──────────────┘         └─────────────┘
                                                        │
                        ┌──────────────┐                │
                        │  MCP Server   │◄──────────────┘
                        │  AI Ajanları  │
                        └──────────────┘
```

### Servis Sorumlulukları

| Servis | Port | Sorumluluk |
|--------|------|-----------|
| **API Gateway** | 8000 | REST API, WebSocket, işlem kayıt, veri sorgulama |
| **Worker** | — | RabbitMQ consumer, anomali tespit motoru, Redis cache |
| **MCP Server** | 8001 | AI ajan entegrasyonu, `get_recent_frauds`, `check_user_status` |
| **Frontend** | 3000 | Dashboard, canlı akış, uyarı paneli, kullanıcı analizi |

---

## 🔧 Teknoloji Seçimleri

| Teknoloji | Gerekçe |
|-----------|---------|
| **FastAPI** | Async native, otomatik OpenAPI docs, Pydantic entegrasyonu |
| **RabbitMQ** | Bu ölçek için yeterli, esnek routing, dahili Management UI, kolay Docker kurulumu |
| **PostgreSQL** | ACID uyumlu, güçlü sorgulama, JSON desteği |
| **Redis** | Sub-ms latency, Sorted Set ile velocity tracking, kullanıcı state yönetimi |
| **React + Vite** | Hızlı dev server, HMR, TypeScript desteği |
| **Recharts** | React-native grafik kütüphanesi |
| **MCP SDK** | Anthropic'in resmi Model Context Protocol SDK'sı |

### Cache Yönetimi Kararları

Redis'te her anomali kuralı için özel veri yapısı kullanılır:

```
Sorted Set → user:{id}:transactions    (velocity: son işlem timestamp'leri)
List        → user:{id}:tx_amounts     (amount: son işlem tutarları)
Hash        → user:{id}:last_location  (location: son konum bilgisi)
```

Bu yapı sayesinde her kontrol O(1) veya O(log N) karmaşıklığında çalışır.

---

## 🚀 Kurulum

### Gereksinimler

- Docker & Docker Compose
- Git

### Tek Komutla Kurulum

```bash
# 1. Projeyi klonlayın
git clone <repo-url>
cd fraud-detection-platform

# 2. Ortam değişkenlerini ayarlayın
cp .env.example .env

# 3. Tüm sistemi başlatın
docker compose up -d --build

# 4. Durumu kontrol edin
docker compose ps
```

### Servis Adresleri

Sistem ayağa kalktıktan sonra aşağıdaki adreslerden servislere erişebilirsiniz:

- 🖥️ **Frontend Arayüzü**: [http://localhost:3000](http://localhost:3000)
- ⚙️ **API Gateway (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🐰 **RabbitMQ Yönetim Paneli**: [http://localhost:15672](http://localhost:15672) (Kullanıcı: `guest`, Şifre: `guest`)
- 🤖 **MCP Server (SSE Bağlantısı)**: `http://localhost:8001/sse` *(Not: Bu bir web arayüzü değildir, AI ajanlarının (Claude Desktop vb.) bağlanması için kullanılan uç noktadır)*

### Veritabanını Örnekle Doldurun

```bash
pip install httpx
python scripts/seed-data.py
```

---

## 📖 Kullanım Rehberi

### 1. Dashboard
Ana sayfa → Genel istatistikler, fraud oranı, risk dağılımı grafiği

### 2. Canlı Akış
`/live` → WebSocket ile gerçek zamanlı işlem akışı. Şüpheli işlemler kırmızı arka planla işaretlenir.

### 3. Fraud Uyarıları
`/alerts` → Tespit edilen tüm fraud'lar, risk seviyesi, ihlal edilen kurallar

### 4. Kullanıcı Analizi
`/users` → Kullanıcı seçerek detaylı risk profili, işlem geçmişi, fraud istatistikleri

---

## 📡 API Dokümantasyonu

### Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/v1/transactions` | Yeni işlem oluştur |
| `GET` | `/api/v1/transactions` | İşlem listesi (pagination + filter) |
| `GET` | `/api/v1/users/{user_id}/risk` | Kullanıcı risk durumu |
| `GET` | `/api/v1/users/{user_id}/history` | Kullanıcı işlem geçmişi |
| `GET` | `/api/v1/frauds` | Fraud listesi (tarih filtreli) |
| `GET` | `/api/v1/frauds/stats` | Fraud istatistikleri |
| `GET` | `/api/v1/health` | Sağlık kontrolü |
| `WS` | `/ws/live` | Canlı veri akışı |

### Örnek: İşlem Oluşturma

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_42",
    "amount": 1500.00,
    "currency": "TRY",
    "location": "Istanbul"
  }'
```

Tam API dokümantasyonu: http://localhost:8000/docs

---

## 🤖 MCP Dokümantasyonu

### Araçlar (Tools)

#### `get_recent_frauds`
Son fraud uyarılarını getirir.

```json
{
  "hours": 24,
  "limit": 20,
  "risk_level": "high"
}
```

#### `check_user_status`
Kullanıcının risk durumunu kontrol eder.

```json
{
  "user_id": "user_42"
}
```

### MCP Client Yapılandırması

Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fraud-detection": {
      "url": "http://localhost:8001/sse"
    }
  }
}
```

### MCP Test

**1. MCP Inspector ile Test (Tavsiye Edilen)**
Terminalde aşağıdaki komutu çalıştırarak resmi test aracını başlatın:
```bash
npx @modelcontextprotocol/inspector
```
Tarayıcıda açılan arayüzde (genellikle `http://localhost:5173`):
1. **Transport**: `SSE` seçin.
2. **URL**: `http://localhost:8001/sse` yazıp Connect deyin.
3. Sol menüdeki "Tools" sekmesinden araçları canlı olarak test edebilirsiniz.

**2. Python Script ile Test**
Ayrıca proje içindeki test script'ini de kullanabilirsiniz:
```bash
python scripts/mcp-test.py
```

---

## 📜 Script Kullanımı

### Manuel Veri Girişi

```bash
./scripts/manual-input.sh <user_id> <amount> <location>

# Örnek
./scripts/manual-input.sh user_42 1500.00 Istanbul
```

### Otomatik Test

```bash
./scripts/auto-test.sh [options]

# Opsiyonlar
--duration=<seconds>         # Çalışma süresi (varsayılan: 60)
--rate=<requests_per_second>  # Saniyede istek (varsayılan: 5)
--anomaly-chance=<percent>    # Anomali olasılığı % (varsayılan: 15)
--users=<count>               # Kullanıcı sayısı (varsayılan: 10)

# Örnek
./scripts/auto-test.sh --duration=30 --rate=10 --anomaly-chance=20
```

---

## 🔍 Anomali Tespit Kuralları

| Kural | Kriter | Redis Yapısı |
|-------|--------|-------------|
| **Velocity** | Son 60 saniyede > 5 işlem | Sorted Set (timestamp score) |
| **Amount** | Tutar > 3× ortalama (24 saat) | List (son tutarlar) |
| **Location** | İmkansız seyahat (mesafe/zaman) | Hash (son konum + timestamp) |

**Karar**: 2+ kural ihlali → **Fraud** olarak işaretle

### Risk Seviyeleri

| Seviye | İhlal Sayısı |
|--------|-------------|
| Low | 0 |
| Medium | 1 |
| High | 2 |
| Critical | 3 |

---

## 🔧 Sorun Giderme

### Servisler başlamıyor

```bash
# Logları kontrol edin
docker-compose logs -f api-gateway
docker-compose logs -f worker

# Tüm servisleri yeniden başlatın
docker-compose down && docker-compose up -d --build
```

### RabbitMQ bağlantı hatası

```bash
# RabbitMQ'nun hazır olmasını bekleyin
docker-compose logs rabbitmq | grep "started"

# Management UI: http://localhost:15672
```

### Database bağlantı hatası

```bash
# PostgreSQL durumunu kontrol edin
docker-compose exec postgres pg_isready

# Veritabanını sıfırlayın
docker-compose down -v && docker-compose up -d
```

### Frontend build hatası

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Proje Yapısı

```
fraud-detection-platform/
├── docker-compose.yml
├── .env.example
├── Makefile
├── services/
│   ├── api-gateway/          # REST API + WebSocket
│   ├── worker/               # Anomali tespit motoru
│   └── mcp-server/           # AI ajan entegrasyonu
├── shared/                   # Ortak kod (events, enums, geo)
├── frontend/                 # React + Vite + TypeScript
├── scripts/                  # Test ve veri script'leri
├── infra/                    # Veritabanı & queue yapılandırması
└── docs/                     # Teknik dokümantasyon
```

---

## 📄 Lisans

Bu proje açık kaynak bağımlılıklarla geliştirilmiştir.
