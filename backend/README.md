# BVBChat Backend

Stock Market Chat Assistant API built with FastAPI and PostgreSQL.

## Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE bvbchat;
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/bvbchat
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/bvbchat` |
| `SECRET_KEY` | JWT signing secret | `dev-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## CLI tool (backend/invite_cli.py):

# Generate keypair
```
python invite_cli.py generate-keys -o invite
````

# Create invite token
````
python invite_cli.py create-token -k invite.key -n "John Doe"
````

# Run generate-keys and add the public key to .env
```
INVITE_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
```

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}` - Get conversation with messages
- `DELETE /api/conversations/{id}` - Delete conversation
- `POST /api/conversations/{id}/messages` - Send message

