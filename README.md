# PhoneBuzz

PhoneBuzz is a webapplication that uses the Twilio API to call a user, receive a numerical input from the user, and then recite the FizzBuzz sequence up to that input unto the user. To use this application one can call into the application, use the application to create an outgoing call, or replay a previous outgoing call in the call history. This application was built in response to the LendUp coding challenge.

## Try It Out

You can try out the app [here](https://phonebuzz-francis.herokuapp.com/). The "Call From PhoneBuzz option does not work because I used a free Twilio account to make the website."

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You will need the Flask and Twilio libraries/frameworks within python3. Look at the requirements.txt file for more information. Either of these can be easily installed through "pip install twilio/flask"


## Running the application on your own

To get the app up and running on your own machine, with your own Twilio account you will need to go to the app.py file, and input your Twilio credentials into the first few lines of code after the import statements:
```
TWILIO_ACCOUNT_SID = ______________
TWILIO_AUTH_TOKEN = _______________
TWILIO_CALLER_ID = ________________
```
Then you will need to change this line in app.py to the url which you will be hosting your website off of. 
```
host_url = _________________
```
## Thank You!
For any questions email me at (francis1788@gmail.com)