# nft-price-estimator

CS4225/5425 project

## To use scraper module
1. Install Python
2. `yarn install`
3. `yarn run init`
4. `yarn run scrape`
Note: you can use npm if you wish

NFT object data { price: float, id: str, name: str, image: str }

## Steps to Run Flask App Locally
1. Clone this repository
    ```sh
    git clone https://github.com/cs4225-nft-price-estimator/nft-price-estimator
    ```
2. (Optional) If you don't have Python, you can follow the guide to install Python 3.9.8 [here](https://www.python.org/downloads/release/python-398/). Do not use the latest Python 3.10 version as Tensorflow is not supported.

3. Install the required dependencies
    ```sh
    pip install -r requirements.txt
    ```
    or
    ```sh
    pip3 install -r requirements.txt
    ```
    
4. Lastly, you can run the application using Flask
    ```sh
    export FLASK_APP=app
    export FLASK_ENV=development
    flask run
    ```

5. (Optional) If you want to expose host and trust users on your network, you can make the server publicly available by adding --host=0.0.0.0 to the Flask run command.
    ```sh
    flask run --host=0.0.0.0
    ```
    Then you will be able to access the local server at [http://localhost:5000](http://localhost:5000).

6. Go to the hosted local server [http://127.0.0.1:5000](http://127.0.0.1:5000).