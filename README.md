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
$ pipenv shell
$ cd src
$ python3 app.py
```

To run using docker

```
$ docker build -t ey .
$ docker run --rm -it -p 8050:8050 ey
```

