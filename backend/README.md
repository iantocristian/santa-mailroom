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

## Invite CLI

Generate invite tokens for new parent accounts:

```bash
# Generate keypair
python invite_cli.py generate-keys -o invite

# Add public key to .env
# INVITE_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Create invite token
python invite_cli.py create-token -k invite.key -n "Parent Name"
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
