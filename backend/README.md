# Santa's Mailroom Backend 🎅

FastAPI backend for the Santa's Mailroom application.

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Edit .env with your values

# Create database
createdb santa

# Run server
uvicorn app.main:app --reload

# Run worker (separate terminal)
python -m app.worker both
```

## Invite Codes

Generate invite codes for new parent accounts:

```bash
# Create a single invite code
python invite_cli.py create

# Create multiple codes
python invite_cli.py create --count 5

# List active invite codes
python invite_cli.py list

# Revoke a code
python invite_cli.py revoke SANTA-XK7M2P
```

## API Endpoints

### Auth
- `POST /api/auth/register` - Register with invite token
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Family & Children
- `GET/PUT /api/family` - Manage family settings
- `GET/POST /api/children` - List/add children
- `GET/PUT/DELETE /api/children/{id}` - Manage child

### Wishlist & Letters
- `GET /api/wishlist` - All wish items (filterable)
- `PUT /api/wishlist/{id}` - Update item status
- `GET /api/letters` - All letters
- `GET /api/letters/{id}` - Letter with details

### Good Deeds
- `GET/POST /api/deeds` - List/create deeds
- `POST /api/deeds/{id}/complete` - Complete deed (sends email!)

### Sent Emails
- `GET /api/sent-emails` - View all Santa's outgoing emails

### Notifications
- `GET /api/notifications` - Parent alerts

## Database Models

| Model | Purpose |
|-------|---------|
| `User` | Parent accounts |
| `Family` | Tenant with settings |
| `Child` | Registered children (hashed emails) |
| `Letter` | Incoming emails |
| `WishItem` | Extracted wishes with pricing |
| `SantaReply` | Generated replies |
| `GoodDeed` | Kindness tracking |
| `ModerationFlag` | Safety alerts |
| `SentEmail` | All outgoing emails |

## Services

| Service | Purpose |
|---------|---------|
| `email_service.py` | POP3 fetch, SMTP send |
| `gpt_service.py` | Extraction, moderation, reply generation |
| `product_search_service.py` | OpenAI web search for products |
| `notification_service.py` | Parent alerts |

## Worker Jobs

| Job Type | Description |
|----------|-------------|
| `fetch_emails` | Check inbox for new letters |
| `process_letter` | Extract wishes, moderate, generate reply |
| `send_reply` | Send Santa's letter reply |
| `send_deed_email` | Send deed suggestion email |
| `send_deed_congrats` | Send deed completion email |

## Email Safety

All AI-generated emails are verified before sending:

- Inappropriate language check
- Adult themes detection
- Tone verification

If safety check fails, email is blocked and logged.

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
