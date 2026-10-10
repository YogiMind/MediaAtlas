# Development

## Run

```bash
python main.py scan path/to/folder          # dry run
python main.py scan path/to/folder --apply  # write changes
uvicorn backend.api.app:app --reload        # API at http://127.0.0.1:8000
pytest -v                                   # tests
```

## Conventions

- All SQL lives in `core/db.py`; none in `api` or the CLI.
- `core` never prints; it returns data.
- Docstrings: one-line summary, then `Args` and `Returns`. Explain *why* in comments, not *what*.
- Tests use `tmp_path` (temporary folders and databases), never the real library.
- Connections come from `connect()`, so foreign keys are always enforced.
- After changing `schema.sql`, delete the dev database (`CREATE TABLE IF NOT EXISTS` won't alter existing tables) until migrations exist.

## API

The reference is generated: run the server and open **http://127.0.0.1:8000/docs**.
It is always correct, so it isn't duplicated here.

Conventions:

- Resources live under `/api/`: `/api/assets`, `/api/tags`, `/api/scan`
- Tags are written `namespace:value`; filtering repeats `?tag=a:b&tag=c:d` and means ALL
- Scanning is a dry run unless `"apply": true`
- Files are fetched by asset id, never by path

(Earlier design notes used `/api/files` and `/api/folders`; the implemented names are `/api/assets`, and a folders endpoint doesn't exist yet.)

## REST in practice

Notes on which REST principles matter for this project:

- **Client-server:** the frontend and backend are separate; the API is the only contract.
- **Stateless:** every request carries what the server needs; nothing about a "session" lives in the server. Metadata therefore lives in the database, never in server memory.
- **Uniform interface:** resources have stable URLs (`/api/assets/{id}`) and are manipulated through JSON representations.
- **Cacheable / layered:** relevant only if the app is ever put behind a proxy.
- **HATEOAS** (the server tells the client which links to follow) is not pursued; the frontend knows the endpoints.
