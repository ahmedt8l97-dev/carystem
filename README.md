# Car Stock Management System

A comprehensive hybrid cloud-based inventory management system for automotive parts and accessories, featuring real-time synchronization with Telegram and cloud storage.

## 🚀 Features

- **Hybrid Cloud Storage**: Combines Convex database with Telegram for data redundancy and ImgBB for image hosting
- **Real-time Inventory Tracking**: Monitor stock levels, prices, and product details in real-time
- **Multi-user Authentication**: Role-based access control (Admin, Employee, Viewer)
- **Advanced Search & Filtering**: Search by product name, car model, type, price range, and availability
- **Telegram Integration**: Automatic product updates posted to Telegram channel
- **Image Management**: Cloud-based image storage via ImgBB
- **Statistics Dashboard**: Comprehensive analytics including sales trends, inventory value, and low stock alerts
- **Backup System**: Automated and manual backup capabilities
- **RESTful API**: Full-featured API for integration with other systems

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

The system uses a hybrid architecture:

```
┌─────────────────┐
│   Vue Frontend  │
│   (Web Client)  │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
┌────────▼────────┐  ┌──────▼──────┐
│  FastAPI Backend│  │   Convex    │
│   (Python)      │  │  (Database) │
└────────┬────────┘  └─────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Telegram│ │ ImgBB │
│  Bot   │ │(Images)│
└────────┘ └───────┘
```

## 🛠️ Tech Stack

### Frontend
- **Vue 3**: Progressive JavaScript framework
- **Vite**: Next-generation frontend tooling
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Lucide Icons**: Modern icon library

### Backend
- **FastAPI**: Modern Python web framework
- **Convex**: Real-time database with TypeScript SDK
- **Python 3.8+**: Core backend language
- **Uvicorn**: ASGI server

### External Services
- **Telegram Bot API**: Message broadcasting and data backup
- **ImgBB API**: Image hosting and CDN

## 📦 Prerequisites

Before installation, ensure you have:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **Telegram Bot Token** ([Create one via BotFather](https://t.me/botfather))
- **ImgBB API Key** ([Get one here](https://api.imgbb.com/))
- **Convex Account** ([Sign up at convex.dev](https://convex.dev))

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/car-stock-system.git
cd car-stock-system
```

### 2. Install Dependencies

#### Root Dependencies
```bash
npm install
```

#### Frontend Dependencies
```bash
cd web-frontend
npm install
cd ..
```

#### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Convex Configuration
VITE_CONVEX_URL=https://your-project.convex.cloud
CONVEX_URL=https://your-project.convex.cloud

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# ImgBB Configuration
IMGBB_API_KEY=your_imgbb_api_key_here
```

### 4. Initialize Convex Database

```bash
npx convex dev
```

This will:
- Create your Convex project
- Deploy the database schema
- Generate TypeScript types

## ⚙️ Configuration

### Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Create a channel or group
4. Add your bot as an administrator
5. Get the chat ID using [@userinfobot](https://t.me/userinfobot)

### ImgBB Setup

1. Sign up at [ImgBB](https://imgbb.com/)
2. Navigate to [API page](https://api.imgbb.com/)
3. Generate an API key
4. Add it to your `.env` file

### User Roles

The system supports three user roles:

| Role | Permissions |
|------|-------------|
| **Admin** | Full access: view, add, edit, delete, export, import, backup, user management |
| **Employee** | Limited access: view, add, edit, export |
| **Viewer** | Read-only: view products and statistics |

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change these credentials immediately after first login!**

## 🎯 Usage

### Development Mode

Run all services concurrently:

```bash
npm run dev
```

This starts:
- Frontend dev server (Vite) on `http://localhost:5173`
- Backend API (FastAPI) on `http://localhost:8000`
- Convex dev environment

### Individual Services

```bash
# Frontend only
npm run dev:frontend

# Backend only
npm run dev:python

# Convex only
npm run dev:backend
```

### Production Build

```bash
npm run build
```

## 📚 API Documentation

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

Response:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "username": "admin",
    "name": "المدير",
    "role": "admin",
    "permissions": ["view", "add", "edit", "delete", "export", "import", "backup"]
  }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

### Products

#### List Products
```http
GET /api/products?search=brake&car_name=toyota&status=available
Authorization: Bearer {token}
```

Query Parameters:
- `search`: Search term (product name, car name, product number)
- `car_name`: Filter by car name
- `product_type`: Filter by product type
- `status`: `available` or `out_of_stock`
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `sort_by`: `price`, `quantity`, `name`, or `last_update`
- `order`: `asc` or `desc`

#### Add Product
```http
POST /api/products
Authorization: Bearer {token}
Content-Type: multipart/form-data

product_number=12345
product_name=Brake Pad
car_name=Toyota Camry
model_number=2020-2023
product_type=Brake System
quantity=10
price_iqd=50000
wholesale_price_iqd=45000
image=@file.jpg
```

#### Update Product
```http
PATCH /api/products/{product_number}
Authorization: Bearer {token}
Content-Type: multipart/form-data

quantity=8
price_iqd=52000
```

#### Delete Product
```http
DELETE /api/products/{product_number}
Authorization: Bearer {token}
```

### Statistics

#### Get Dashboard Statistics
```http
GET /api/stats
Authorization: Bearer {token}
```

Response includes:
- Overview (total products, value, items)
- Products by type
- Products by car
- Top selling products
- Low stock alerts

### User Management (Admin Only)

#### List Users
```http
GET /api/users
Authorization: Bearer {token}
```

#### Create User
```http
POST /api/users
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded

username=employee1&password=pass123&name=John Doe&role=employee
```

#### Delete User
```http
DELETE /api/users/{username}
Authorization: Bearer {token}
```

## 🚢 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Create a new Web Service on [Render](https://render.com)
3. Connect your repository
4. Configure:
   - **Build Command**: `npm run build:prod`
   - **Start Command**: `npm start`
5. Add environment variables in Render dashboard
6. Deploy!

### Deploy Convex

```bash
npx convex deploy --prod
```

### Environment Variables for Production

Ensure all environment variables are set in your hosting platform:
- `VITE_CONVEX_URL`
- `CONVEX_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `IMGBB_API_KEY`
- `PORT` (automatically set by most platforms)

## 🔒 Security Best Practices

1. **Change Default Credentials**: Immediately change the default admin password
2. **Use HTTPS**: Always use HTTPS in production
3. **Secure API Keys**: Never commit API keys to version control
4. **Regular Backups**: Enable automatic backups
5. **Update Dependencies**: Keep all dependencies up to date
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Input Validation**: All inputs are validated server-side

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please:
- Open an issue on GitHub
- Check the [documentation](docs/README.md)
- Contact the development team

## 🙏 Acknowledgments

- FastAPI for the excellent Python framework
- Convex for real-time database capabilities
- Telegram for reliable message delivery
- ImgBB for image hosting services
- Vue.js community for frontend tools

---

**Made with ❤️ for automotive parts management**
