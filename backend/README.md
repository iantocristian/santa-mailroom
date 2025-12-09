# Santa Wishlist Backend

Christmas wishlist API - children email Santa, parents manage everything.

## Setup

```bash
# Create venv
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

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

Generate invite codes for new parent accounts (format: `SANTA-XK7M2P`):

```bash
# Create a single invite code
python invite_cli.py create

# Create multiple codes
python invite_cli.py create --count 5

# Create with a note and expiry
python invite_cli.py create --note "For John's family" --expires 30

# List active invite codes
python invite_cli.py list

# List all codes (including used)
python invite_cli.py list --all

# Revoke a code
python invite_cli.py revoke SANTA-XK7M2P
```

**Docker usage:**
```bash
# Generate 5 invite codes
docker compose exec backend python invite_cli.py create -c 5

# List all codes
docker compose exec backend python invite_cli.py list --all
```

## API Endpoints

**Auth**
- `POST /api/auth/register` - Register with invite token
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

**Family & Children**
- `GET/POST/PUT /api/family` - Manage family settings
- `GET/POST /api/children` - List/add children
- `GET/PUT/DELETE /api/children/{id}` - Manage child

**Wishlist & Letters**
- `GET /api/wishlist` - All wish items (filterable)
- `PUT /api/wishlist/{id}` - Update item (reality filter)
- `GET /api/letters` - All letters
- `GET /api/letters/timeline` - Scrapbook view

**Good Deeds & Moderation**
- `GET/POST /api/deeds` - Manage good deeds
- `GET /api/moderation` - Content flags
- `GET /api/notifications` - Parent alerts

## Email Safety Layer

All AI-generated emails are verified by a secondary LLM before being sent to children. This provides defense-in-depth against inappropriate content.

**Configuration:**
```bash
# In .env
GPT_SAFETY_MODEL=gpt-4o-mini        # Model for safety checks
EMAIL_SAFETY_CHECK_ENABLED=true     # Set to false to disable
```

**What it checks:**
- Inappropriate language
- Adult themes (violence, drugs, etc.)
- Harmful content
- Manipulation tactics
- Privacy concerns
- Tone issues

If safety check fails, the email is **blocked** and logged.

## Testing

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests (115 security tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_auth_security.py -v
```

**Test coverage includes:**
- Authentication security (tokens, login)
- Authorization (IDOR prevention)
- Input validation (SQL injection, XSS)

