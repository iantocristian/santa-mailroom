# Santa's Mailroom 🎅

A magical Christmas application where children email Santa and parents manage everything through a festive dashboard.

## Features

- 📧 **Email Santa** - Children send wish lists to a dedicated email address
- 🎁 **Wishlist Management** - Parents see extracted items with prices
- ✨ **Good Deeds Tracker** - Santa suggests kind acts, parents mark completion
- 🛡️ **Content Safety** - Automatic moderation flags concerning content
- 📖 **Scrapbook View** - Year-by-year timeline of letters and wishes
- 📤 **Sent Emails** - View all Santa's outgoing emails
- ❄️ **Festive UI** - Animated snowfall and Christmas theme

## Project Structure

```
santa/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── routers/      # API routes
│   │   ├── services/     # Business logic (email, GPT, search)
│   │   ├── models.py     # SQLAlchemy models
│   │   └── worker.py     # Background job worker
│   └── requirements.txt
│
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # UI components (Sidebar, Snowfall)
│   │   ├── pages/        # Route pages
│   │   ├── store/        # Zustand stores
│   │   └── styles/       # Christmas theme CSS
│   └── package.json
│
└── docker-compose.yaml   # Container orchestration
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### 1. Database Setup

```sql
CREATE DATABASE santa;
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your settings

uvicorn app.main:app --reload
```

Backend: http://localhost:8000

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

### 4. Email Worker

```bash
cd backend
source .venv/bin/activate
python -m app.worker both
```

## Configuration

All configuration via `.env` file:

### Required

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key |

### Email (POP3 - Receiving)

| Variable | Description |
|----------|-------------|
| `POP3_SERVER` | POP3 server (e.g., `pop.gmail.com`) |
| `POP3_PORT` | Port (default: 995) |
| `POP3_USERNAME` | Email account |
| `POP3_PASSWORD` | App password |

### Email (SMTP - Sending)

| Variable | Description |
|----------|-------------|
| `SMTP_SERVER` | SMTP server (e.g., `smtp.gmail.com`) |
| `SMTP_PORT` | Port (465 for SSL, 587 for TLS) |
| `SMTP_USERNAME` | Email account |
| `SMTP_PASSWORD` | App password |
| `SANTA_EMAIL_ADDRESS` | Santa's "from" address |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Child's Email  │────▶│  POP3 Fetcher   │────▶│   Job Queue     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────▼────────┐
                        │              Email Worker               │
                        │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
                        │  │ Extract │  │Moderate │  │ Search  │  │
                        │  │  Items  │  │ Content │  │Products │  │
                        │  └─────────┘  └─────────┘  └─────────┘  │
                        └────────────────────────────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌───────▼─────────┐
│  Santa's Reply  │◀────│  SMTP Sender    │◀────│  Reply Worker   │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Parent Dashboard                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Children │  │ Wishlist │  │  Deeds   │  │ Scrapbook/Emails │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Auth
- `POST /api/auth/register` - Register (requires invite token)
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Family & Children
- `GET/PUT /api/family` - Family settings
- `GET/POST/PUT/DELETE /api/children` - Child management

### Content
- `GET/PUT /api/wishlist` - Wish items
- `GET /api/letters` - Letters and replies
- `GET/POST /api/deeds` - Good deeds
- `POST /api/deeds/{id}/complete` - Complete deed (sends email!)
- `GET /api/sent-emails` - View all Santa emails

## Documentation

- [USER-GUIDE.md](./USER-GUIDE.md) - End user guide
- [backend/README.md](./backend/README.md) - Backend details
- [frontend/README.md](./frontend/README.md) - Frontend details

## License

MIT
