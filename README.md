![banner](./unrelated_assests/img/MLOps_github_banner.png)
# DSBA-MLOps Repository
This repository was made for DSBA MLOps class.\
**Author**: Matteo COUCHOUD

## Structure
unrelated_assets (assets not related to assignments)\
coreAPI (code for the API project and docker image)\
images (build docker images)

## Quick commands

### Docker
- Build docker Scoring-API:\
`docker build -t socring-api`

- Save docker image as .tar file _(version to specify)_:\
`docker save scoring-api:<VERSION> -o scoring-api.tar`

- Load .tar image file:\
`docker load -i scoring-api.tar`




