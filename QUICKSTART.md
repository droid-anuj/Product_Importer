# 🚀 QUICK START GUIDE

## ⚡ 30-Second Setup with Docker

```bash
cd product_importer
docker-compose up -d
```

That's it! Your application is running.

### 📍 Access Points

- **Web UI**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

---

## 🎯 First Steps

### 1. Upload a Sample CSV

Create a file `products.csv`:

```csv
sku,name,description,price,quantity,active
PROD001,Blue Shirt,Comfortable cotton shirt,29.99,100,true
PROD002,Red Hat,Classic baseball cap,19.99,50,true
PROD003,Black Shoes,Running shoes,89.99,30,true
PROD004,White Socks,Pack of 5,9.99,200,true
PROD005,Green Jacket,Waterproof jacket,149.99,25,true
```

### 2. Upload via UI

1. Go to http://localhost:8000/static/index.html
2. Click **Upload** tab
3. Drag and drop `products.csv` (or click to select)
4. Click **Start Upload**
5. Watch real-time progress!

### 3. View Products

1. Click **Products** tab
2. See your imported products in a sortable table
3. Filter by SKU, name, or status
4. Create/Edit/Delete products directly

### 4. Setup Webhooks (Optional)

1. Click **Webhooks** tab
2. Click **Create Webhook**
3. Enter: `https://webhook.site/your-unique-url` (free service)
4. Event Type: `import.completed`
5. Click **Test** to verify

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api       # API server
docker-compose logs -f celery    # Background worker
docker-compose logs -f postgres  # Database

# Check service status
docker-compose ps

# Stop services
docker-compose down

# Remove all data and volumes
docker-compose down -v

# Rebuild images
docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### "Connection refused" on first run

Services take time to start. Wait 30 seconds, then:

```bash
docker-compose ps
```

All should show "Up" status.

### Upload stuck at 0%

Check API logs:
```bash
docker-compose logs api
```

### Celery tasks not processing

Check worker logs:
```bash
docker-compose logs celery
```

### Database connection error

Verify PostgreSQL is healthy:
```bash
docker-compose ps postgres
```

Should show "healthy" status.

---

## 📦 CSV Format Guide

### Required Columns
- `sku` - Unique product identifier
- `name` - Product name

### Optional Columns
- `description` - Product description
- `price` - Product price (numeric)
- `quantity` - Stock quantity (numeric)
- `active` - true/false (defaults to true)

### Example
```csv
sku,name,description,price,quantity,active
SKU001,Product A,Great product,99.99,100,true
SKU002,Product B,,49.99,50,
SKU003,Product C,Description here,199.99,10,false
```

---

## 🌐 API Endpoints

All endpoints start with `/api`

### Upload
```bash
POST /upload/              # Upload CSV
GET /upload/progress/{id}  # Get progress
```

### Products
```bash
GET /products/             # List (paginated)
POST /products/            # Create
PUT /products/{id}         # Update
DELETE /products/{id}      # Delete
DELETE /products/          # Delete all
```

### Webhooks
```bash
GET /webhooks/             # List
POST /webhooks/            # Create
PUT /webhooks/{id}         # Update
DELETE /webhooks/{id}      # Delete
POST /webhooks/{id}/test   # Test webhook
GET /webhooks/{id}/logs    # View logs
```

---

## 💡 Tips & Tricks

### Generate Large Test CSV

```bash
python3 << 'EOF'
import csv
with open('large_test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sku', 'name', 'description', 'price', 'quantity', 'active'])
    for i in range(1, 10001):
        writer.writerow([f'SKU{i:06d}', f'Product {i}', f'Desc {i}', 9.99 + i*0.01, 100+i, 'true'])
EOF
```

### Monitor with Flower (Celery Dashboard)

```bash
pip install flower
celery -A celery_app flower
# Open http://localhost:5555
```

### Reset Everything

```bash
# Delete all data and restart clean
docker-compose down -v
docker-compose up -d
```

### Check Database Directly

```bash
docker-compose exec postgres psql -U product_user -d product_importer -c "SELECT COUNT(*) FROM products;"
```

---

## 🚀 Production Deployment

Ready to deploy? See `README.md` for:
- Render deployment steps
- Upstash Redis setup
- Neon PostgreSQL setup
- Environment configuration

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Logs | `docker-compose logs -f api` |
| Status | `docker-compose ps` |
| Reset | `docker-compose down -v && docker-compose up -d` |
| Shell | `docker-compose exec api bash` |
| DB Shell | `docker-compose exec postgres psql -U product_user -d product_importer` |

---

## ✨ Features at a Glance

✅ Upload CSV with 500K+ products  
✅ Real-time progress tracking  
✅ Full product CRUD  
✅ Advanced filtering  
✅ Webhook support  
✅ REST API documentation  
✅ Responsive UI  
✅ Production-ready  

---

**Ready?** Start with: `docker-compose up -d`
