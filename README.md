![banner](documentation/unrelated_assests/img/MLOps_github_banner.png)
# Monsieur Valeur Foncière - DSBA-MLOps Repository
This repository was made for DSBA MLOps class.\
**Author**: Matteo COUCHOUD

## Description

Estimating the market value of a property in France is complex time-consuming, and often requires access to expensive professional services. _Monsieur Valeur Foncière_ gives individuals and real estate professionals an instant and data-driven estimate of a property's value based on key descriptive attributes.

## Reasoning

Whether you are buying, selling, or simply assessing your assets, knowing the fair market value of a property is an important data to have. In France, this data is publicly available through the DVF dataset (Demandes de Valeurs Foncières) published by the DGFIP and the Ministry of Economy, Finance and Industry. It covers the entirety of French territory (except Alsace and Moselle) and records the declared property values submitted to tax authorities in a year.

However, this dataset is quite technical, extensive and as such less accessible for non-specialist.

The goal of the _Monsieur Valeur Foncière_ tool is to bridge the gap between non technical users and possible property value insights. By training a prediction model on the DVF dataset, it
makes this public data usable/actionable to anyone without prior technical knowledge.

It addresses the three identified pain points:
- **Cost**: getting a professional valuation can be quite expensive. The tool provides an instant estimate at no cost.
- **Speed**: a professional valuation takes days. The tool returns an estimate in mere seconds.
- **Accessibility**: the DVF data exists but is unusable in its raw form for most people. The tool makes it exploitable in a simple way.

Two main audiences:
- **Individuals**: anyone looking to buy, sell, or simply understand the value of a property without the need to commit to a professional service
- **Real estate professionals**: agents or analysts who need to quickly check or estimate multiple property values from a portfolio


Account registration screen:
![register](documentation/screenshots/auth/register_scren.png)

Login screen:
![register](documentation/screenshots/auth/login_screen.png)

Dashboard with a prediction made:
![register](documentation/screenshots/auth/pred_dash_screen.png)

Estimations history:
![register](documentation/screenshots/auth/history_screen.png)

Area for batch estimation (importing a CSV file):
![register](documentation/screenshots/auth/batch_screen.png)


## Key functionnalities ?
Here are key functionnalities of the tool:

1. **Everything in one account**: the tool provides account creation and login so your estimates belong to you only.
2. **Single property value estimate**: you can fill in a short form describing the property (`surface area`, `number of rooms`, `department`, `property type`, `number of lots`, `land surface area`) and get an instant estimated value along with a price range which indicates the uncertainty of the estimate.
3. **Batch estimation**: you can upload a CSV file containing multiple properties and get estimates for all of them at once.
4. **History**: all your past estimates are saved to your account and can be consulted at any time.

_Data for Alsace and Moselle are not available. As such, estimates of those two regions are not available._





## Read further - Documentation
The following pages gove more details on inner works of the product and reasoning behind technical choices:
- [Detailed functionnalities](documentation/product.md)
- [Architecture](documentation/architecture.md)
- [Machine Learning for Property Scoring](documentation/scoring.md)
- [Authentication and security](documentation/security.md)

## How to build the app

Before running anything in the app, you must train the prediction model.
1. Training data can be found at this link: [https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees). Download the `.csv` file (_csv/2025/full.csv.gz_).

From the root of the project, put the `.csv` file in the `inputs` folder.

Now, with a terminal at **the root of the project**:

2. Run the training command: `python src/training/cli.py --data inputs/full.csv`
3. Build the whole application: `docker-compose up --build` (or `docker-compose down && docker-compose up --build` if the app is already running).
4. Connect to the app at `localhost:3000/auth.html`

The app can be stopped through the Docker Desktop interface (`dsba-mlops` container), or by running `docker-compose down` from the root of the project.

## Current limitations

Functionnalities:
- **Price range**: the  range showing the uncertainty of an estimate is an approximation, not a statistically rigorous confidence interval. It should be interpreted as a rough indication of variability, not a guaranteed price bracket.
- **Geographic coverage**: the model is trained on French DVF data and is only relevant for properties located in France. Also, Alsace and Moselle are currently not available in the dataset and will not have estimate in the tool.

Developpement:
- **CORS configuration**: the current setup contains code that works on a local environment (such as CORS policy) but has not been validated for production. A security review would be required before any public deployment. For more information on CORS, see the [Authentication and Security](documentation/security.md) page.
- **Docker images & model file**: for a production context, Docker images should be stored on a dedicated registry like DockerHub and the model file on an object storage service. Both are included in this repository for convenience during development.

## Future implementation ideas
While the tool successfuly implements the key features metionned earlier, it can still be made better. Here are some ideas:

- [Estimates]: Implement a true confidence interval system. A statistically rigorous one would require a more complex approach like quantile regression.




