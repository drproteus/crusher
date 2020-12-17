build:
	docker-compose build web

collectstatic:
	mkdir -p static
	# docker-compose run -u "`id -u`:`id -g`" --rm web python manage.py collectstatic --no-input
	docker-compose run --no-deps --rm web python manage.py collectstatic --no-input

makemigrations:
	docker-compose run -u "`id -u`:`id -g`" --rm web python manage.py makemigrations

migrate:
	docker-compose run --rm web python manage.py migrate

up:
	docker-compose up -d

tail:
	docker-compose logs -f

tail-web:
	docker-compose logs -f web

stop:
	docker-compose stop

restart:
	docker-compose restart

rebuild:
	docker-compose build --no-cache web

clean:
	docker-compose down
	docker-compose rm

