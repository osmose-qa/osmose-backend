# Docker

osmose-backend can be run in a Docker container. This avoids setting
up and configuring Python, Java and PostgreSQL on your system.

Note : A PostgreSQL docker is automatically installed and run by
docker compose and doesn't need be installed manually.
The osmose-frontend docker may also be run but is not mandatory.


## Setup for production

Build the Docker images
```sh
docker compose build
```

For production setup, you may fill the `SENTRY_DSN` in the `.env` to enable error reporting.

The `./work` directory on your host must be writable by anyone, as the
`osmose` user in the container will have some random UID (probably 1000).
```sh
chmod a+w ./work
```

Taking Monaco (a quick and small one) as an example, once the docker
image is built, you can run Osmose analyzers using:
```sh
docker compose run --rm backend ./osmose_run.py --country=monaco
docker compose down # Destroy the loaded data base
```

This will run interactively and you will see the output scrolling on your
screen. The container will be deleted at the end of the process. All
downloaded and output data will be saved in the `./work` directory.


## Develop on Osmose using docker

Run every thing from the `docker` directory.

Add the `osmose-frontend` project, it will allow you to show the result on a web map.
```sh
git clone https://github.com/osmose-qa/osmose-frontend.git
```

Copy `.env.template` as `.env` and uncomment the `COMPOSE_FILE` line.

Build the Docker images
```sh
docker compose build
```

### Run

Start e.g. with Monaco, a quick and small one. Import the OSM data.
```sh
docker compose run --rm backend ./osmose_run.py --country=monaco --skip-analyser --skip-upload --no-clean
```

Then you can run all Osmose analysers using:
```sh
docker compose run --rm backend ./osmose_run.py --skip-init --no-clean --country=monaco
```

List configured "countries" and analysers with:
```sh
docker compose run --rm backend ./osmose_run.py --list-country
docker compose run --rm backend ./osmose_run.py --list-analyser
```

To test a specific analyser:
```sh
docker compose run --rm backend ./osmose_run.py --skip-init --no-clean --country=monaco --analyser=osmosis_highway_floating_islands
```

To run one plugin only use:
```sh
docker compose run --rm backend ./osmose_run.py --skip-init --no-clean --country=monaco --analyser=sax --plugin=Name_Multiple
```

The files containing the results will be in `./work/results`.

### Show the results on the map

```sh
docker compose up api web
```

The result will be available on the frontend at: http://127.0.0.1:8080/en/issues/open?item=xxxx&useDevItem=all


### Access to the Database

After data load the Database will contain the OSM data. You
can enter to explore and test SQL directly. Open a psql shell on database
from within the Backend container with:
```sh
docker compose run --rm backend psql -h postgis
```
Password: `-osmose-`.

Then on Postgres shell:
```sh
osmose=> set search_path to monaco,public;
```

You can Reset the Database and the docker containers with:
```sh
docker compose down -v
```


### Alternative: Develop with Jupyter

Load OSM data, as before.

Then run the jupyter-notebook web server:
```sh
docker compose run -p 8888:8888 --rm backend jupyter-notebook
```
Note the `8888:8888`, which exposes port `8888` to localhost.

Follow the displayed link on http://localhost:8888/... Use this [password](https://github.com/osmose-qa/osmose-backend/blob/master/docker/work/.jupyter/jupyter_notebook_config.py#L13).


Start by reading the index documentation, and copy template to test your
own analyzer code.


## Run the tests

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details. But, for short:
```sh
docker compose run --rm backend pytest plugins/TagFix_Housenumber.py
docker compose run --rm backend ./tools/pytest.sh lint
docker compose run --rm backend ./tools/pytest.sh mypy
docker compose run --rm backend ./tools/pytest.sh sax # Run all plugins tests
docker compose run --rm backend ./tools/pytest.sh merge # Not required, run all test on merge from analysers directory
docker compose run --rm backend ./tools/pytest.sh other # Not required, run all other analysers and non analyser tests
```
