up:
	docker-compose --env-file .env.prod up -d --build
createsuperuser:
	docker-compose --env-file .env.prod exec flask flask -A src.app:app users createsuperuser
migrate:
	docker-compose --env-file .env.prod exec --workdir /opt/app/src flask alembic upgrade head