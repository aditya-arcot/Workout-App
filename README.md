### Local Development

Copy `.env.example` to `.env` & populate variables

```bash
cp config/env/.env.example config/env/.env
```

Install dependencies:

```bash
envsubst
npm
uv
watchexec
```

Start containers:

```bash
./scripts/dev.sh
```

### Database

All writes should go through SQLAlchemy

Alembic updates & bulk SQLAlchemy updates must explicitly set `updated_at`
