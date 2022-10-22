# EnergyAustraliaApiTest


The problem
-----------
Your team is tasked with listing out music festival data in a particular manner.
The data is provided to you via an API by another team; they assure you all the data is available and have provided you with the Swagger documentation needed to get started.


# Requirements 
- Python3
- pipenv or pip
- allure (https://docs.qameta.io/allure-report/#_installing_a_commandline)

# Set up
If you have pipenv installed you have to run <code> pipenv install </code> or if you  use pip run <code>pip install -r requirements.txt</code>

# Run The test
python EnergyAustraliaApiTest.py --alluredir reports

# Generate the report
allure serve reports


# Conclusion
I found the response is not respected the schema given for MusicalFestival, and Band
