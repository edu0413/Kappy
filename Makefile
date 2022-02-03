start-database:
	cd dockerfiles && docker-compose up --build -d db_auth

stop-database:
	cd dockerfiles && docker-compose stop db_auth

start-backend:
	cd dockerfiles && docker-compose up --build backend

stop-backend:
	cd dockerfiles && docker-compose stop backend

run: start-backend
