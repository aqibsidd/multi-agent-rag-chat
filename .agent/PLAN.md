# PLAN

Task: TASK-003

## Risk tier

LOW — local dev infra file, no production deployment involved.

## Specialist concerns

none.

## Objective

`docker-compose.yml` at repo root running Qdrant locally with persistent
storage.

## Steps

1. Write `docker-compose.yml`: Qdrant service (`qdrant/qdrant` image),
   port 6333 (REST) and 6334 (gRPC) mapped, named volume for
   `/qdrant/storage`.
2. Validate the compose file parses (`docker compose config`) if the CLI
   works even without the daemon running; otherwise just validate YAML
   syntax, since actually starting it is TASK-005's job (AWAITING_HUMAN).

## Acceptance criteria

- [ ] `docker-compose.yml` exists, valid YAML
- [ ] Qdrant service maps port 6333, uses a named volume for persistence

## Files expected to change

- `docker-compose.yml` (new, repo root)
