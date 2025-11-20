# Product Importer Web App

A production-ready product CSV importer with real-time progress tracking, webhooks, and product management.

## 🚀 Features

- **CSV Upload**: Import up to 500,000 products with batch processing
- **Real-time Progress**: Live progress bar with detailed metrics
- **Product Management**: Full CRUD operations with filtering and pagination
- **Webhooks**: Configurable webhooks for event notifications
- **Background Jobs**: Celery-based async processing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Fast**: Redis-based caching and progress tracking
- **Docker Ready**: Complete docker-compose setup for local development

## 🛠 Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: PostgreSQL
- **Background Jobs**: Celery + Redis
- **ORM**: SQLAlchemy
- **Frontend**: Vanilla JS + HTML + Tailwind CSS
- **Deployment**: Docker + Render/Upstash/Neon

## 📋 Prerequisites

- Docker & Docker Compose
- OR: Python 3.11+, PostgreSQL, Redis

## 🚀 Local Development with Docker

### 1. Clone and Setup

```bash
cd product_importer
docker-compose up -d
```

### 2. Access the Application

- **Web UI**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Environment Variables (Pre-configured in docker-compose)

```env
DATABASE_URL=postgresql://product_user:product_password@localhost:5432/product_importer
REDIS_URL=redis://localhost:6379/0
DEBUG=True
```

## 📚 Local Development without Docker

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```bash
# Create database
createdb product_importer

# Or use connection string
export DATABASE_URL="postgresql://username:password@localhost:5432/product_importer"
```

### 3. Setup Redis

```bash
# Start Redis server
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 4. Start the Application

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 3 (Optional) - Flower (Celery Monitoring):**
```bash
pip install flower
celery -A celery_app flower
```

Access at: http://localhost:5555

### 5. Access the Application

- Web UI: http://localhost:8000/static/index.html
- API Docs: http://localhost:8000/docs

## 📤 Using the Application

### Upload Products CSV

1. Go to **Upload** tab
2. Drag & drop or select a CSV file
3. CSV format:
   ```
   sku,name,description,price,quantity,active
   SKU001,Product Name,Description,99.99,100,true
   SKU002,Another Product,,49.99,50,
   ```
4. Click **Start Upload**
5. Watch progress in real-time

### Manage Products

1. Go to **Products** tab
2. Use filters to search (SKU, Name, Active status)
3. Create new products with form
4. Edit/Delete existing products
5. Bulk delete all products

### Configure Webhooks

1. Go to **Webhooks** tab
2. Create webhook with URL and event type
3. Test webhook to verify delivery
4. Check logs for webhook attempts

**Supported Event Types:**
- `import.completed`: Triggered after CSV import finishes
- `product.created`: Triggered when new product created
- `product.updated`: Triggered when product updated
- `test`: Manual test event

## 🐳 Docker Compose Services

```yaml
postgres    # PostgreSQL database (port 5432)
redis       # Redis cache/broker (port 6379)
api         # FastAPI server (port 8000)
celery      # Background worker
```

**View logs:**
```bash
docker-compose logs -f api      # API logs
docker-compose logs -f celery   # Celery logs
docker-compose logs -f postgres # Database logs
```

**Stop services:**
```bash
docker-compose down
```

**Remove all data:**
```bash
docker-compose down -v
```

## 📦 API Endpoints

### Upload
- `POST /api/upload/` - Upload CSV file
- `GET /api/upload/progress/{task_id}` - Get upload progress

### Products
- `GET /api/products/` - List products (paginated)
- `POST /api/products/` - Create product
- `GET /api/products/{id}` - Get product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `DELETE /api/products/` - Delete all products

### Webhooks
- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `GET /api/webhooks/{id}` - Get webhook
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook
- `POST /api/webhooks/{id}/test` - Test webhook
- `GET /api/webhooks/{id}/logs` - Get webhook logs

## 🌍 Deployment to Render

### 1. Create Render Account

Sign up at https://render.com

### 2. Create PostgreSQL Database

1. Go to Dashboard → New → PostgreSQL
2. Name: `product-importer-db`
3. Copy the **Internal Database URL**

### 3. Create Redis Instance

1. Go to https://console.upstash.com
2. Create new Redis database
3. Copy the **UPSTASH_REDIS_URL**

### 4. Deploy API Service

1. Create new Web Service
2. Connect your GitHub repo
3. Set environment variables:
   ```
   DATABASE_URL=<from Render>
   REDIS_URL=<from Upstash>
   CELERY_BROKER_URL=<from Upstash>
   CELERY_RESULT_BACKEND=<from Upstash>
   ```
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 5. Deploy Celery Worker

1. Create another Web Service (same repo)
2. Same environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `celery -A celery_app worker --loglevel=info`

### 6. Test Deployment

```bash
curl https://your-api.onrender.com/health
```

## 🔐 Security Notes

- Change default PostgreSQL credentials in production
- Use strong Redis passwords (Upstash)
- Enable HTTPS on Render (automatic)
- Set DEBUG=False in production
- Use environment variables for secrets

## 📊 Database Schema

### Products Table
- `id` (Integer, Primary Key)
- `sku` (String, Unique, Case-Insensitive)
- `name` (String)
- `description` (Text, Optional)
- `price` (Float, Optional)
- `quantity` (Integer)
- `active` (Boolean)
- `created_at`, `updated_at` (DateTime)

### Webhooks Table
- `id` (Integer, Primary Key)
- `url` (String)
- `event_type` (String)
- `enabled` (Boolean)
- `created_at`, `updated_at` (DateTime)

### Webhook Logs Table
- `id` (Integer, Primary Key)
- `webhook_id` (Integer, Foreign Key)
- `event_type` (String)
- `status_code` (Integer, Optional)
- `response_body` (Text, Optional)
- `error_message` (Text, Optional)
- `created_at` (DateTime)

## 🐛 Troubleshooting

### Connection Refused
- Ensure Docker containers are running: `docker-compose ps`
- Check port conflicts: `lsof -i :8000`

### Database Connection Error
- Verify DATABASE_URL environment variable
- Test connection: `psql $DATABASE_URL`

### Celery Tasks Not Running
- Check Redis connection: `redis-cli ping`
- View Celery logs: `docker-compose logs celery`
- Ensure worker is running and connected

### Upload Stuck
- Check file size (max 500MB)
- Verify CSV format
- Check API logs: `docker-compose logs api`

### Webhook Not Firing
- Ensure webhook is enabled
- Test endpoint manually: `curl -X POST https://your-endpoint.com`
- Check webhook logs in UI

## 📝 CSV Import Details

### Requirements
- File must be CSV format
- Required columns: `sku`, `name`
- Optional columns: `description`, `price`, `quantity`, `active`

### Processing
- Processes in batches of 10,000 rows
- SKU upsert (case-insensitive)
- Automatic data validation
- Error reporting per row

### Performance
- 10,000 rows: ~5-10 seconds
- 100,000 rows: ~1-2 minutes
- 500,000 rows: ~5-10 minutes

## 📄 License

MIT License

## 🤝 Support

For issues and questions, check logs:
```bash
docker-compose logs -f api
docker-compose logs -f celery
docker-compose logs -f postgres
```

---

**Ready to use!** Copy the entire `product_importer` folder to your project directory and run `docker-compose up`.
