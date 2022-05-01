# nft-price-estimator

CS4225/5425 project

### Project structure

    .
    ├── model                   # ML models (not pretrained)
    ├── notebooks               # Actual notebooks containing the code used to scrape data/perform ML
    ├── resources               # Resource files
    ├── static                  # JS code used in flask
    ├── templates               # HTML for frontend
    ├── requirements.txt        # Python packages
    └── README.md

## Important notes (Do not skip)
1. `/nft_estimator_model.sav` is not the actual model we used because the actual fully trained model is very large
2. You will need to request for your own OpenSea API key from the OpenSea dev team, as these are not meant to be revealed in public and are controlled items.
3. `/sample` contains sample metadata and images scraped.
4. (FYI) `/sample/images/testImage.png` is not an existing NFT and `/sample/images/mad-hare-society-2-#2676.png` is an NFT existing on Crypto.com/nft, not listed on OpenSea marketplace. These are samples of our unseen dataset we used to test our model.
5. *Recommended:* The frontend can be run to observe how our ML model predicts the prices. More details regarding the data collection, processing can be found in our project report.

## Set up Python Virtual Environment
1. Create virtual environment: `yarn run venv`
2. Activate python virtual environment: `yarn run act` or `env/Scripts/activate`
3. Install dependencies: `yarn run init`

## To use scraper module
1. Install Python 
2. [Set up Python Virtual Environment](#set-up-python-virtual-environment)
3. `yarn run scrape`

**Alternative**: Use the python interpretor to run the scripts. Note that the binaries need to be installed first. This is subject to the availability of the Opensea API key as well, which we are not permitted to expose here.

### NFT object data 

Here's a quick sample of the schema used in metadata collection:

```
{
        "id": 8955,
        "name": "Azuki #8955",
        "image": "https://lh3.googleusercontent.com/5yg1ouzzuyrlunlPLwtQ1Spgi1X25PPLGjxKenQo7OCHCdgPNQaRdykn9vpkehA9PpfgYHfhCKWQMM4vBHDNYC8aneebPpdN-vARYw",
        "price": 2.99,
        "token": "ETH"
}
```

## Steps to Run Flask App Locally
1. Clone this repository
    ```sh
    git clone https://github.com/cs4225-nft-price-estimator/nft-price-estimator
    ```

2. (Optional) If you don't have Python, you can follow the guide to install Python 3.9.8 [here](https://www.python.org/downloads/release/python-398/). Do not use the latest Python 3.10 version as Tensorflow is not supported.

3. Create a python virtual environment 
    ```sh
    yarn run venv
    yarn run act
    yarn run init
    ```
    Windows (Powershell):
    ```sh
    yarn run venv
    env/Scripts/activate
    yarn run init
    ```
    
4. Lastly, you can run the application locally using Flask
    ```sh
    export FLASK_APP=app
    export FLASK_ENV=development
    flask run
    ```
    Windows:
    ```sh
    $env:FLASK_ENV = "development"
    flask run
    ```

5. (Optional) If you want to expose host and trust users on your network, you can make the server publicly available by adding --host=0.0.0.0 to the Flask run command.
    ```sh
    flask run --host=0.0.0.0
    ```
    Then you will be able to access the local server at [http://localhost:5000](http://localhost:5000).

6. Go to the hosted local server [http://127.0.0.1:5000](http://127.0.0.1:5000).