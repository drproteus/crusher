FROM python:3.7
RUN apt update && apt upgrade -y && apt install -y mariadb-client
COPY . /var/run/crusher
WORKDIR /var/run/crusher
RUN python -m pip install -r /var/run/crusher/requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
