# Car Stock Management System - Complete Documentation

## Overview

The Car Stock Management System is a modern, cloud-based inventory management solution designed specifically for automotive parts retailers and distributors. It provides real-time inventory tracking, multi-user access control, and seamless integration with Telegram for notifications and backup.

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Client Layer                          │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │  Web Browser   │  │  Mobile Device │                 │
│  │   (Vue.js)     │  │   (Responsive) │                 │
│  └────────┬───────┘  └────────┬───────┘                 │
└───────────┼──────────────────┼──────────────────────────┘
            │                  │
            └──────────┬───────┘
                       │ HTTPS
┌──────────────────────▼───────────────────────────────────┐
│                  Application Layer                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │           FastAPI Backend (Python)                │   │
│  │  • RESTful API                                    │   │
│  │  • Authentication & Authorization                 │   │
│  │  • Business Logic                                 │   │
│  │  • File Upload Handling                           │   │
│  └──────────┬───────────────────────────┬────────────┘   │
└─────────────┼───────────────────────────┼────────────────┘
              │                           │
    ┌─────────▼─────────┐       ┌────────▼────────┐
    │                   │       │                  │
┌───▼────────────────┐  │  ┌────▼──────────────┐  │
│  Convex Database   │  │  │  External APIs    │  │
│  • Products        │  │  │  • Telegram Bot   │  │
│  • Users           │  │  │  • ImgBB CDN      │  │
│  • Backups         │  │  └───────────────────┘  │
└────────────────────┘  │                         │
                        └─────────────────────────┘
```

### Data Flow

1. **User Authentication**
   - User submits credentials
   - Backend validates against Convex database
   - JWT token generated and returned
   - Token used for subsequent requests

2. **Product Management**
   - User uploads product with image
   - Image sent to ImgBB, URL returned
   - Product data saved to Convex
   - Notification sent to Telegram channel
   - Real-time update to all connected clients

3. **Inventory Updates**
   - Stock level changes trigger updates
   - Convex database updated
   - Telegram message edited
   - Dashboard statistics recalculated

## Core Features

### 1. Product Management

#### Product Schema
```typescript
{
  product_number: string,      // Unique identifier
  product_name: string,         // Product name
  car_name: string,             // Compatible car model
  model_number: string,         // Car model year/variant
  type: string,                 // Product category
  quantity: number,             // Current stock
  original_quantity: number,    // Initial stock
  price_iqd: number,           // Retail price (IQD)
  wholesale_price_iqd: number, // Wholesale price (IQD)
  status: string,              // "متوفر" or "نفذ"
  image: string,               // ImgBB URL
  message_id: number,          // Telegram message ID
  last_update: string          // ISO timestamp
}
```

#### Operations
- **Create**: Add new products with images
- **Read**: Search, filter, and sort products
- **Update**: Modify product details and stock
- **Delete**: Remove products (soft delete option)

### 2. User Management

#### User Roles & Permissions

| Permission | Admin | Employee | Viewer |
|------------|-------|----------|--------|
| View Products | ✅ | ✅ | ✅ |
| View Statistics | ✅ | ✅ | ✅ |
| Add Products | ✅ | ✅ | ❌ |
| Edit Products | ✅ | ✅ | ❌ |
| Delete Products | ✅ | ❌ | ❌ |
| Export Data | ✅ | ✅ | ❌ |
| Import Data | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ |
| Backups | ✅ | ❌ | ❌ |

#### Session Management
- Token-based authentication
- 7-day session expiry
- Automatic session cleanup
- Concurrent session support

### 3. Search & Filtering

#### Search Capabilities
- Full-text search across:
  - Product names
  - Car names
  - Product numbers
  - Model numbers
  - Product types

#### Filter Options
- **By Car**: Filter by car manufacturer/model
- **By Type**: Filter by product category
- **By Status**: Available, Out of Stock
- **By Price Range**: Min/Max price filters
- **By Date**: Last updated date range

#### Sorting Options
- Price (ascending/descending)
- Quantity (ascending/descending)
- Name (alphabetical)
- Last Update (newest/oldest)

### 4. Statistics Dashboard

#### Overview Metrics
- Total Products Count
- Available Products
- Out of Stock Items
- Total Inventory Value (IQD)
- Total Items in Stock
- Average Product Price

#### Analytics
- **By Product Type**: Count, quantity, and value per category
- **By Car Model**: Distribution of products per car
- **Top Selling**: Most sold products (based on quantity change)
- **Low Stock Alerts**: Products below threshold

### 5. Telegram Integration

#### Features
- Automatic product posting
- Real-time updates
- Message editing for stock changes
- Product deletion synchronization
- Formatted messages with HTML

#### Message Format
```
🔧 [Product Name]
━━━━━━━━━━━━━━━━
🚗 Car: [Car Name]
🔢 Model: [Model Number]
🏷️ Number: [Product Number]
📂 Type: [Type]
📦 Quantity: [Quantity]
📊 Status: [Status]
━━━━━━━━━━━━━━━━
💰 Price: [Price] IQD
📦 Wholesale: [Wholesale Price] IQD
━━━━━━━━━━━━━━━━
📅 [Timestamp]
🖼️ [Image Link]
```

### 6. Image Management

#### ImgBB Integration
- Cloud-based image storage
- CDN delivery for fast loading
- Automatic image optimization
- Permanent image URLs
- No storage limits

#### Image Handling
- Upload validation (size, format)
- Base64 encoding
- Automatic URL generation
- Fallback for missing images

### 7. Backup System

#### Backup Types
- **Manual Backups**: On-demand by admin
- **Daily Backups**: Automatic at midnight
- **Weekly Backups**: Every Sunday
- **Pre-Update Backups**: Before bulk operations

#### Backup Contents
- Complete product database
- User information (encrypted passwords)
- System settings
- Metadata (timestamp, product count)

#### Restore Capabilities
- Full system restore
- Selective product restore
- Backup comparison
- Rollback functionality

## API Reference

### Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

### Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer {your_token_here}
```

### Endpoints

#### Authentication Endpoints

##### POST /api/auth/login
Login to the system

**Request Body:**
```
username=admin&password=admin123
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "username": "admin",
    "name": "المدير",
    "role": "admin",
    "role_name": "مدير",
    "permissions": ["view", "add", "edit", "delete", "export", "import", "backup"]
  }
}
```

##### POST /api/auth/logout
Logout from the system

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "تم تسجيل الخروج بنجاح"
}
```

##### GET /api/auth/me
Get current user information

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "username": "admin",
  "name": "المدير",
  "role": "admin",
  "role_name": "مدير",
  "permissions": ["view", "add", "edit", "delete", "export", "import", "backup"]
}
```

##### GET /api/auth/roles
Get available roles and permissions

**Response:**
```json
{
  "admin": {
    "name": "مدير",
    "permissions": ["view", "add", "edit", "delete", "export", "import", "backup"]
  },
  "employee": {
    "name": "موظف",
    "permissions": ["view", "add", "edit", "export"]
  },
  "viewer": {
    "name": "عارض",
    "permissions": ["view"]
  }
}
```

#### Product Endpoints

##### GET /api/products
Get all products with optional filtering

**Query Parameters:**
- `search` (string): Search term
- `car_name` (string): Filter by car name
- `product_type` (string): Filter by product type
- `status` (string): "available" or "out_of_stock"
- `min_price` (number): Minimum price
- `max_price` (number): Maximum price
- `sort_by` (string): "price", "quantity", "name", "last_update"
- `order` (string): "asc" or "desc"

**Example:**
```
GET /api/products?search=brake&car_name=toyota&status=available&sort_by=price&order=asc
```

**Response:**
```json
[
  {
    "product_number": "12345",
    "product_name": "Brake Pad Set",
    "car_name": "Toyota Camry",
    "model_number": "2020-2023",
    "type": "Brake System",
    "quantity": 10,
    "original_quantity": 15,
    "price_iqd": 50000,
    "wholesale_price_iqd": 45000,
    "status": "متوفر",
    "image": "https://i.ibb.co/abc123/image.jpg",
    "message_id": 12345,
    "last_update": "2024-01-15T10:30:00Z"
  }
]
```

##### POST /api/products
Create a new product

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Form Data:**
- `product_number` (required): Unique product identifier
- `product_name` (required): Product name
- `car_name` (required): Compatible car model
- `model_number` (optional): Car model year/variant
- `product_type` (required): Product category
- `quantity` (required): Initial stock quantity
- `price_iqd` (required): Retail price
- `wholesale_price_iqd` (required): Wholesale price
- `image` (optional): Product image file

**Response:**
```json
{
  "product_number": "12345",
  "product_name": "Brake Pad Set",
  "car_name": "Toyota Camry",
  "model_number": "2020-2023",
  "type": "Brake System",
  "quantity": 10,
  "original_quantity": 10,
  "price_iqd": 50000,
  "wholesale_price_iqd": 45000,
  "status": "متوفر",
  "image": "https://i.ibb.co/abc123/image.jpg",
  "message_id": 12345,
  "last_update": "2024-01-15T10:30:00Z"
}
```

##### PATCH /api/products/{product_number}
Update an existing product

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Form Data (all optional):**
- `product_name`: Updated product name
- `car_name`: Updated car model
- `model_number`: Updated model number
- `product_type`: Updated product type
- `quantity`: Updated stock quantity
- `price_iqd`: Updated retail price
- `wholesale_price_iqd`: Updated wholesale price
- `image`: New product image

**Response:**
```json
{
  "product_number": "12345",
  "product_name": "Brake Pad Set - Premium",
  "quantity": 8,
  "price_iqd": 52000,
  "last_update": "2024-01-15T11:00:00Z"
}
```

##### PATCH /api/products/{product_number}/status
Update product status (quick actions)

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `action`: "sold_one", "sold_all", or "out_of_stock"

**Example:**
```
PATCH /api/products/12345/status?action=sold_one
```

**Response:**
```json
{
  "product_number": "12345",
  "quantity": 9,
  "status": "متوفر",
  "last_update": "2024-01-15T11:15:00Z"
}
```

##### DELETE /api/products/{product_number}
Delete a product

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "status": "deleted",
  "product_number": "12345"
}
```

#### Statistics Endpoints

##### GET /api/stats
Get comprehensive dashboard statistics

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "overview": {
    "total_products": 150,
    "available_products": 120,
    "out_of_stock": 30,
    "total_value": 75000000,
    "total_items": 1500,
    "average_price": 50000
  },
  "by_type": {
    "Brake System": {
      "count": 25,
      "quantity": 250,
      "value": 12500000
    },
    "Engine Parts": {
      "count": 30,
      "quantity": 300,
      "value": 15000000
    }
  },
  "by_car": {
    "Toyota Camry": {
      "count": 45,
      "quantity": 450
    },
    "Honda Accord": {
      "count": 35,
      "quantity": 350
    }
  },
  "top_selling": [
    {
      "product_number": "12345",
      "product_name": "Brake Pad Set",
      "sold": 5,
      "remaining": 10
    }
  ],
  "low_stock": [
    {
      "product_number": "67890",
      "product_name": "Oil Filter",
      "quantity": 2
    }
  ]
}
```

#### User Management Endpoints (Admin Only)

##### GET /api/users
List all users

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "username": "admin",
    "name": "المدير",
    "role": "admin",
    "role_name": "مدير",
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "username": "employee1",
    "name": "John Doe",
    "role": "employee",
    "role_name": "موظف",
    "created_at": "2024-01-10T10:00:00Z"
  }
]
```

##### POST /api/users
Create a new user

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `username` (required): Unique username
- `password` (required): User password
- `name` (required): Full name
- `role` (required): "admin", "employee", or "viewer"

**Response:**
```json
{
  "message": "تم إنشاء المستخدم بنجاح",
  "user": {
    "username": "employee1",
    "name": "John Doe",
    "role": "employee",
    "role_name": "موظف"
  }
}
```

##### DELETE /api/users/{username}
Delete a user

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "message": "تم حذف المستخدم بنجاح"
}
```

#### System Endpoints

##### GET /api/health
Check system health and connectivity

**Response:**
```json
{
  "status": "online",
  "version": "5.0.0",
  "telegram": true
}
```

##### GET /api/settings
Get system settings (Admin only)

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "telegram_bot_token": "1234567890...",
  "telegram_chat_id": "-1001234567890",
  "imgbb_api_key": "abc123...",
  "version": "5.0.0",
  "convex_url": "https://your-project.convex.cloud"
}
```

##### POST /api/settings
Update system settings (Admin only)

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/x-www-form-urlencoded
```

**Form Data (all optional):**
- `bot_token`: New Telegram bot token
- `chat_id`: New Telegram chat ID
- `imgbb_key`: New ImgBB API key

**Response:**
```json
{
  "message": "تم تحديث الإعدادات بنجاح"
}
```

## Installation Guide

### Prerequisites

1. **Node.js** (v16+)
   ```bash
   node --version  # Should be v16 or higher
   ```

2. **Python** (v3.8+)
   ```bash
   python --version  # Should be 3.8 or higher
   ```

3. **npm** or **yarn**
   ```bash
   npm --version
   ```

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/car-stock-system.git
cd car-stock-system
```

#### 2. Install Root Dependencies
```bash
npm install
```

#### 3. Install Frontend Dependencies
```bash
cd web-frontend
npm install
cd ..
```

#### 4. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### 5. Setup Convex

```bash
# Login to Convex
npx convex login

# Initialize project
npx convex dev
```

This will:
- Create a new Convex project
- Deploy the database schema
- Generate your CONVEX_URL

#### 6. Configure Environment Variables

Create `.env` in project root:

```env
# Convex
VITE_CONVEX_URL=https://your-project.convex.cloud
CONVEX_URL=https://your-project.convex.cloud

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ImgBB
IMGBB_API_KEY=your_imgbb_key
```

#### 7. Start Development Server

```bash
npm run dev
```

Access the application at `http://localhost:5173`

## Deployment Guide

### Deploy to Render

#### 1. Prepare Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: car-stock-system
   - **Environment**: Python
   - **Build Command**: `npm run build:prod`
   - **Start Command**: `npm start`
   - **Instance Type**: Free or Starter

#### 3. Add Environment Variables

In Render dashboard, add:
```
VITE_CONVEX_URL=https://your-project.convex.cloud
CONVEX_URL=https://your-project.convex.cloud
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
IMGBB_API_KEY=your_imgbb_key
```

#### 4. Deploy Convex to Production

```bash
npx convex deploy --prod
```

Update your `.env` with the production URL.

#### 5. Deploy

Click "Create Web Service" and wait for deployment to complete.

### Deploy to Other Platforms

#### Heroku
```bash
heroku create car-stock-system
heroku config:set VITE_CONVEX_URL=your_url
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
```

#### DigitalOcean App Platform
1. Connect repository
2. Set build command: `npm run build:prod`
3. Set run command: `npm start`
4. Add environment variables
5. Deploy

#### AWS EC2
```bash
# SSH into instance
ssh -i key.pem ubuntu@your-ip

# Clone repository
git clone https://github.com/yourusername/car-stock-system.git
cd car-stock-system

# Install dependencies
npm install
cd web-frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# Setup environment
nano .env  # Add your variables

# Build
npm run build

# Start with PM2
pm2 start "npm start" --name car-stock
```

## Troubleshooting

### Common Issues

#### 1. Convex Connection Error
```
Error: Failed to connect to Convex
```

**Solution:**
- Verify `CONVEX_URL` in `.env`
- Run `npx convex dev` to ensure deployment
- Check internet connection

#### 2. Telegram Bot Not Responding
```
Error: Telegram API Error: 401 Unauthorized
```

**Solution:**
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Ensure bot is added to channel/group
- Check `TELEGRAM_CHAT_ID` format (should start with `-100`)

#### 3. Image Upload Fails
```
Error: ImgBB API Key غير مُعد
```

**Solution:**
- Verify `IMGBB_API_KEY` in `.env`
- Check API key is valid at [ImgBB](https://api.imgbb.com/)
- Ensure image size is under 32MB

#### 4. Port Already in Use
```
Error: Port 8000 is already in use
```

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 5. Build Fails
```
Error: Cannot find module 'vite'
```

**Solution:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Frontend
cd web-frontend
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode

Enable debug logging:

```env
# .env
DEBUG=true
LOG_LEVEL=debug
```

## Best Practices

### Security

1. **Change Default Credentials**
   - First login with admin/admin123
   - Immediately change password in settings

2. **Use Environment Variables**
   - Never commit `.env` to version control
   - Use different keys for dev/prod
   - Rotate API keys regularly

3. **Enable HTTPS**
   - Use SSL certificates in production
   - Redirect HTTP to HTTPS
   - Enable HSTS headers

4. **Rate Limiting**
   - Implement rate limiting for API endpoints
   - Protect against brute force attacks
   - Monitor suspicious activity

### Performance

1. **Image Optimization**
   - Compress images before upload
   - Use WebP format when possible
   - Implement lazy loading

2. **Database Indexing**
   - Indexes already configured in schema
   - Monitor query performance
   - Use pagination for large datasets

3. **Caching**
   - Cache frequently accessed data
   - Use Redis for session storage
   - Implement CDN for static assets

4. **CDN Usage**
   - ImgBB provides CDN automatically
   - Consider Cloudflare for static assets
   - Enable browser caching

### Maintenance

1. **Regular Backups**
   - Enable automated daily backups
   - Store backups in multiple locations
   - Test restore procedures regularly

2. **Monitor Logs**
   - Setup log rotation
   - Monitor error rates
   - Set up alerts for critical issues

3. **Update Dependencies**
   - Check for updates weekly
   - Test updates in staging first
   - Keep security patches current

4. **Health Checks**
   - Monitor API availability
   - Check external service status
   - Set up uptime monitoring

## FAQ

### General Questions

**Q: Can I use this system for other types of inventory?**
A: Yes! The system is flexible and can be adapted for any inventory management needs. Just modify the product schema and labels.

**Q: Is there a mobile app?**
A: The web interface is fully responsive and works on mobile devices. A native app is planned for future releases.

**Q: Can I export data to Excel?**
A: Yes, use the export functionality in the dashboard to download data as CSV/Excel.

**Q: How many products can the system handle?**
A: Convex can handle millions of records. Performance depends on your plan and query optimization.

### Technical Questions

**Q: Can I self-host without Convex?**
A: Yes, but you'll need to replace Convex with another database (PostgreSQL, MongoDB, etc.) and modify the backend accordingly.

**Q: Does it support multiple languages?**
A: Currently, the UI is in Arabic with English API documentation. Multi-language support is planned.

**Q: Can I integrate with my existing POS system?**
A: Yes, use the RESTful API to integrate with any system that supports HTTP requests.

**Q: Is there a webhook system?**
A: Not currently, but you can poll the API or use Telegram notifications for real-time updates.

## Changelog

### Version 5.0.0 (Current)
- ✨ Hybrid cloud storage (Convex + Telegram + ImgBB)
- ✨ Role-based access control
- ✨ Advanced search and filtering
- ✨ Statistics dashboard
- ✨ Automated backups
- 🐛 Fixed image upload issues
- 🐛 Improved error handling
- ⚡ Performance optimizations

### Version 4.0.0
- ✨ Convex database integration
- ✨ Real-time synchronization
- 🐛 Fixed Telegram message editing

### Version 3.0.0
- ✨ User authentication system
- ✨ Multi-user support
- ✨ Permission management

### Version 2.0.0
- ✨ ImgBB image hosting
- ✨ Telegram integration
- 🐛 Various bug fixes

### Version 1.0.0
- 🎉 Initial release
- ✨ Basic CRUD operations
- ✨ Local file storage

## Roadmap

### Short Term (Q1 2026)
- [ ] Multi-language support (English, Arabic, Kurdish)
- [ ] Barcode scanning
- [ ] Print labels and invoices
- [ ] Advanced reporting
- [ ] Email notifications

### Medium Term (Q2-Q3 2026)
- [ ] Mobile native apps (iOS/Android)
- [ ] Supplier management
- [ ] Purchase orders
- [ ] Sales tracking
- [ ] Customer management

### Long Term (Q4 2026+)
- [ ] AI-powered demand forecasting
- [ ] Integration marketplace
- [ ] Multi-warehouse support
- [ ] Advanced analytics
- [ ] API marketplace

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Code Style

- **Python**: Follow PEP 8
- **JavaScript/TypeScript**: Follow Airbnb style guide
- **Vue**: Follow Vue.js style guide
- **Commits**: Use conventional commits

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: This comprehensive guide

---

**Last Updated**: January 15, 2026  
**Version**: 5.0.0  
**Maintained by**: Car Stock System Team
