start:
	docker compose up

stop:
	docker compose down

restart:
	make stop
	make start