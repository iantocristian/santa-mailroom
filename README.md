# Santa Wishlist Application 🎅

A magical Christmas wish list application where children email Santa and parents manage everything through a festive dashboard.

## Features

- 📧 **Email Santa**: Children send wish lists to a dedicated email address
- 🎁 **Wishlist Management**: Parents see extracted items with prices and links
- ✨ **Good Deeds Tracker**: Santa suggests kind acts, parents mark completion
- 🛡️ **Content Safety**: Automatic moderation flags concerning content
- 📖 **Scrapbook View**: Year-by-year timeline of letters and wishes
- 🔔 **Notifications**: Alerts for new letters, budget limits, and flags

## Project Structure

```
santa/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── routers/      # API routes
│   │   ├── services/     # Business logic (email, GPT, etc.)
│   │   ├── models.py     # SQLAlchemy models
│   │   └── tasks.py      # Celery async tasks
│   ├── alembic/          # Database migrations
│   └── requirements.txt
│
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Route pages
│   │   ├── store/        # Zustand stores
│   │   └── styles/       # CSS styles
│   └── package.json
│
└── docker-compose.yaml   # Container orchestration
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis (for Celery task queue)

### 1. Setup PostgreSQL Database

```sql
CREATE DATABASE santa;
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy example env and configure
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start the server
python -m uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Configuration

All configuration is via environment variables (`.env` file):

### Required Settings

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key for GPT features |

### Email Settings

| Variable | Description |
|----------|-------------|
| `POP3_SERVER` | POP3 server for receiving emails |
| `POP3_PORT` | POP3 port (default: 995) |
| `POP3_USERNAME` | Email inbox username |
| `POP3_PASSWORD` | Email inbox password |
| `SMTP_SERVER` | SMTP server for sending replies |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USERNAME` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `SANTA_EMAIL_ADDRESS` | The "from" address for Santa's replies |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `GPT_MODEL` | `gpt-4o` | Model for generating replies |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis URL for task queue |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new parent account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |

### Family & Children
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/family` | Get family settings |
| PUT | `/api/family` | Update family settings |
| GET | `/api/children` | List children |
| POST | `/api/children` | Register a child |
| PUT | `/api/children/{id}` | Update child |
| DELETE | `/api/children/{id}` | Remove child |

### Wishlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wishlist` | List wish items (filterable) |
| GET | `/api/wishlist/summary` | Budget/category summary |
| PUT | `/api/wishlist/{id}` | Approve/deny item |

### Letters & Timeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/letters` | List letters |
| GET | `/api/letters/{id}` | Get letter with items and reply |
| GET | `/api/letters/timeline` | Scrapbook view data |
| POST | `/api/letters/{id}/export` | Export as PDF |

### Good Deeds
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deeds` | List good deeds |
| POST | `/api/deeds` | Suggest new deed |
| PUT | `/api/deeds/{id}/complete` | Mark as completed |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Child's Email  │────▶│  POP3 Fetcher   │────▶│   Task Queue    │
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
│  │ Children │  │ Wishlist │  │  Deeds   │  │ Timeline/Letters │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## License

MIT
