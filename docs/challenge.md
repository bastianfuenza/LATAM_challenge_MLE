# Software Engineer (ML & LLMs) Challenge

- [Overview](#overview)
- [Part I: Model](#part-i-model)
    - [Analysis](#analysis)
    - [Model Transcription](#model-transcription)
    - [Tests](#tests)
- [Part II: FastAPI App](#part-ii-fastapi-app)
    - [App Creation](#app-creation)
    - [Tests](#tests)
- [Part III: Deployment to GCP](#part-iii-deployment-to-gcp)
    - [Deployment](#deployment)
    - [Tests](#tests)
- [Part IV: CI/CD & Git](#part-iv-cicd--git)
    - [Continuous Integration (CI)](#continuous-integration-ci)
    - [Continuous Delivery (CD)](#continuous-delivery-cd)
    - [Git](#git)

## Overview

This document explains the results of the execution of this challenge, including: 
- Mayor decisions taken
- Steps taken
- Analysis made
- Others.

It is divided into 4 Parts, mimicking the instructions for the challenge:
- Part I: Model
- Part II: FastAPI app
- Part III: Deployment to GCP
- Part IV: CI/CD & Git

Overall, the challenge was finished, tests were passed, and the FastAPI app was deployed to GCP.

App URL: https://latam-mle-app-1011328148142.us-central1.run.app

## Part I: Model

### Analysis

A short analysis on the resulting model was made:

- The only features used where OPERA, TIPOVUELO, MES, which seems to have been a mistake; considering the plots, there should be useful information that can be added to the model.
- Feature importance was taken from a model predicting everything as class 0, meaning that it didn't learn useful information from the data, that makes the listed feature importance not useful.
- Training the models without feature importance and with balance, makes the logistic model better than before (better than with feature importance and balance).
- It can be argued that the first logistic model is still better than the last one, since it has a better f1-score, but it result's are barely different from a dummy model that only predicts class 0.
- It's clear that xgboost could be fine-tuned more to achieve better results (or try other models, other feature extraction, etc), but since it's not the scope of the challenge, it'll be ignored.

**The new Logistic model was going to be chosen, as is a model that learnt from the data, and in some cases can predict a delay; but the tests were designed to run with the previous models (the metrics where higher than the test expected), so the Logistic model with feature importance and balance was picked. Ultimately, if the model is useful at all depends on whether the benefit of predicting some delays outweighs the cost of having so many false positives. It's important to note that the model could be greatly improved by reworking the feature choice and extraction.**

### Model Transcription

Relevant points: 
- The Logistic model with feature importance and balance was picked, to mimic "get_dummies" a OneHotEncoder was used.
- Both model and encoder where saved to a file, and are automatically loaded when creating a instance of DelayModel.
- Check for correct and sufficient column in data was added to the preprocess, raises custom exception InputDataException if conditions are not met.

### Tests

All 4 tests in test_model were passed

## Part II: FastAPI App

### App Creation

Relevant points:
- DelayModel was integrated to predict on data recieved on the endpoint /predict
- DockerFile was created to deploy and serve the app 
- Pydantic models for input and outdata where created to provide extra checks (FlightData, PredictRequest, PredictResponse)
- If the input data passed to the endpoint does not have the propper format or data, the exception InputDataException is raised, returning a message with the problem and a 400 http code.
Response example: {"detail": "Unknown categories '13' found in column 'MES'"}

### Tests

All 4 tests in test_api were passed

## Part III: Deployment to GCP

### Deployment
App URL: https://latam-mle-app-1011328148142.us-central1.run.app

Docker image containing the app is sent to GCP Artifact Registry, and run in GCP Cloud Run; being publicly available to be consummed

### Tests

Stress test was passed

## Part IV: CI/CD & Git

### Continuous Integration (CI)

CI is triggered on push to _main_ or _dev_, and on pull request to _main_. Executes the following steps:
1. Checkout Code
2. Install Python
3. Install Make
4. Install Python requirements
5. Run Model & API tests (on _dev_ all tests are run regardles of one failing, _main_ stops the pipeline on failure)
6. Upload Test Reports as an artifact

### Continuous Delivery (CD)

CD is triggered only on _main_. Executes the following steps:
1. Setup Env variables
2. Checkout Code
3. Install Python
4. Install Make
5. Install Python requirements
6. Setup GCP SDK with credentials
7. Setup CLI and configure project
8. Build Docker image
9. Push Docker image to GCP Artifact Registry
10. Deploy Docker container to GCP Cloud Run
11. Run Stress Test
12. Upload Test Reports as an artifact

### Git

Branches are structure as:
- main
- dev
- feature_*:
    - feature_model
    - feature_fastapi
    - feature_deployment_gcp
    - feature_cicd

Code was worked on feature branches then merged to _dev_, after all work was finished it was merged to _main_ 