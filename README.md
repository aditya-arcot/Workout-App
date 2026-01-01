### Local Development

Copy `.env.example` to `.env` & populate variables

```bash
cp .env.example .env
```

Install dependencies:

```bash
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
