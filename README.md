<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/DaKeiser/vaccine-efficacy-prediction/master/assets/chaos-td.png" alt="Chaos" width="200">
  <br>
  Vaccine Efficacy Tracker
  <br>
</h1>

<h3 align="center">An AI solution to track the Covid Vaccine Efficacy for <a href="https://www.ey.com/en_in/techathon" target="_blank">EY Techathon</a></h3>

## Installation
```
$ git clone git@github.com:DaKeiser/chaos.git
```

## Setup
To run this project, follow these steps

```
$ cd ey-hackathon
$ pipenv install
```

- Copy and Paste the `config.json.example` file and rename it as `config.json`
- You then need to create an account on [mapbox](http://mapbox.com/) and paste your public access token in the field `mapbox-token`

To run the model to generate the CSVs, run
```
$ pipenv run python3 model.py
```
Running it once a day will suffice.

To run the application, run
```
$ pipenv run python3 app.py
```

To run using docker

```sh
$ docker-compose build
$ docker-compose up
```

## UI

The app is still in development phase. Currently, the user can find the number of future cases in a particular state or a district.

<img src="https://raw.githubusercontent.com/DaKeiser/vaccine-efficacy-prediction/master/assets/ui.png" width="800">

## Contributors
- [Arpitha Malavalli](https://github.com/ArpithaMalavalli)
- [Nikitha Adivi](https://github.com/NikiAdivi)
- [Sai Rithwik M](https://github.com/DaKeiser)
- [Saiakash Konidena](https://github.com/sal2701)
- [Sama Sai Karthik](https://github.com/Kartik-Sama)

