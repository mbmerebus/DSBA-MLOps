![banner](./unrelated_assests/img/MLOps_github_banner.png)
# DSBA-MLOps Repository
This repository was made for DSBA MLOps class.\
**Author**: Matteo COUCHOUD

## Functionalities

DSBA-MLOps is a French property valuation application built as a microservices architecture.

The app supports the following functionalities:
- User login/logout and account creation, access to a user's own dashboard.
- Property value prediction for a single property or for a batch (import CSV file). Confidence intervals for prediction.
- User specific scoring history.
- Model training using csv data, most recent model automatically chosen.

>_The prediction model is a `HistGradientBoostingRegressor` trained on French real estate transaction data (DVF). It can be retrained using the training CLI._


## Structure
The project follows a multi-service architecture:
```
DSBA-MLOps
├── inputs --input data folder
│   └── (data csv file here)
├── redis --redis configuration
├── src --source code for all API/services
│   ├── training --training CLI and code for the prediction model
│   ├── scoring --property scoring service using trained model
│   ├── auth --user authentication service
│   ├── history --scoring history, specific to the user
│   ├── gateway --request routing service and single entry point
│   └── webui --frontend service (nginx)
└── docker-compose.yml
```

## How to build the app

Before running anything in the app, you must train the prediction model.
1. Training data can be found at this link: [https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees). Download the `.csv` file (_csv/2025/full.csv.gz_).

From the root of the project, put the `.csv` file in the `inputs` folder.

Now, with a terminal at **the root of the project**:

2. Run the training command: `python src/training/cli.py --data inputs/full.csv`
3. Build the whole application: `docker-compose up --build` (or `docker-compose down && docker-compose up --build` if the app is already running).
4. Connect to the app at `localhost:3000/auth.html`

The app can be stopped through the Docker Desktop interface (`dsba-mlops` container), or by running `docker-compose down` from the root of the project.

## Tested
This code has been tested and works on the following operating systems:
- Linux (Ubuntu, Fedora)
- MacOS 26 (Tahoe)

_The code hasn't been tested on Windows yet, but should work._





