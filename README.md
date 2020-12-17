```
  ____ ____  _   _ ____  _   _ _____ ____
 / ___|  _ \| | | / ___|| | | | ____|  _ \
| |   | |_) | | | \___ \| |_| |  _| | |_) |
| |___|  _ <| |_| |___) |  _  | |___|  _ <
 \____|_| \_\\___/|____/|_| |_|_____|_| \_\
```

For naval medical operations, provides:

* Inventory
  * Staff
  * Supplies
  * etc.
* Invoicing
* Job tracking
* Reporting & metrics

### Setup
* `make build` to build main Django webserver image
* adjust .env and docker-compose.yml to taste, then: `make up` to spin up all containers in the background
* `make collectstatic` to export static files so they can be served
* `make migrate` to run all pending migrations on DB
* after making model adjustments, run `make makemigrations` to generate the new migrations, then run `make migrate` to apply
* by default, a GraphiQL interface is available @ http://localhost:8080/graphql

---
![dr. crusher](https://live.staticflickr.com/4856/45142715954_8f50020329.jpg)
