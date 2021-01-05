# ey-hackathon

EY Hackathon Covid Efficacy Tracker

## Installation
```
$ git clone git@github.com:DaKeiser/ey-hackathon.git
```

## Setup
To run this project, follow these steps

```
$ cd ey-hackathon
$ pipenv install
```

- Copy and Paste the `config.json.example` file and rename it as `config.json`
- You then need to create an account on [mapbox](http://mapbox.com/) and paste your public access token in the field `mapbox-token`

```
$ pipenv run python3 app.py
```

To run using docker

```sh
$ docker-compose build
$ docker-compose up
```

