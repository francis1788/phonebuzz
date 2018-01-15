import os
import twilio.twiml
from twilio import *
from twilio.rest import Client
from flask import Flask, request
from flask import render_template
from flask import g
import time
import sqlite3
import json
from multiprocessing import Process
from twilio.twiml.voice_response import VoiceResponse, Say

app = Flask(__name__)



TWILIO_CALLER_ID = "+18312469407"
TWILIO_ACCOUNT_SID = 'AC8fde0d1a6081058d9779798929b3623a'
TWILIO_AUTH_TOKEN = '4de220ce7dfd39fe43ced795fbd15df4'
url = "https://phonebuzz-francis.herokuapp.com/"


def fizz_bizz(number):
	lst = ["FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i) for i in range(1,number+1)]
	return " ".join(lst)

def setup_database():
    global connect
    global cursor
    DB = "database.db"
    connect = sqlite3.connect(DB, check_same_thread=False)
    cursor = connect.cursor()
    table_exists = cursor.execute("SELECT name FROM sqlite_master WHERE name ='calls' and type='table'").fetchone()
    
    if not table_exists:
        connect.execute('CREATE TABLE calls (id INTEGER PRIMARY KEY, datetime DATETIME, delay INT, phonenum INT, num INT)')
    cursor.close()

setup_database()

@app.route('/', methods=['GET', 'POST']) #allow both GET and POST requests
def main():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        global phone
        global delay
        phone = request.form.get('phone')
        delay = request.form['delay']
        phone = phone.replace(" ","").replace("(","").replace(")","").replace("-","")
        if not delay:
            delay = 0
        try:
            assert(len(phone) == 10)
            phone = int(phone)
        except:
            return '''<h1>Sorry {} is not a verified or valid phone number.</h1>
                    <h2> Please input a valid number </h2>
                  <a href={}>Return</a>'''.format(phone,url)  
        try:
            insert_into_sql(phone, delay)
            cursor = connect.cursor()
            id = cursor.execute("SELECT MAX(id) FROM calls")
            id = id.fetchone()
            id = id[0]
            cursor.close()
            p = Process(target=caller, args=(phone, delay, id))
            p.start()
            
        except:
            print('Error')
        message = "Thank you for using PhoneBuzz! Your call to "+str(phone)+" has been initiated."
        title = "Call Initiated"
        return render_template('timer.html',call=title,delay=int(delay), message=message)   
        
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM calls')
    return render_template('index.html', calls=cursor.fetchall())

def insert_into_sql(phone, delay):
    cursor = connect.cursor()
    insert = "INSERT INTO calls (id, datetime, delay, phonenum) VALUES "
    insert = insert + "(NULL, CURRENT_TIMESTAMP," + str(delay) + "," + str(phone) +" )"
    cursor.execute(insert)
    connect.commit()
    cursor.close()

def caller(phone, delay, id):
    phone = str(phone)
    if delay:
       time.sleep(int(delay))
    client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
    call = client.calls.create(to='+1'+phone,
                               from_=TWILIO_CALLER_ID,
                               url=url+"response?id="+str(id))
    print(call)


@app.route("/response", methods=['GET', 'POST'])
def response():
    resp = VoiceResponse()

    signature = request.headers.get('X-Twilio-Signature', '')
    print(signature)
    if not signature:
        resp.say("This is not Twilio")
        return str(resp)

    id = request.args.get("id")
    if id:
        with resp.gather(finishOnKey="#", action="/handle-number?id="+str(id), method="POST") as g:
            message = "Welcome to PhoneBuzz! Please enter any number, followed by the pound sign, to play!"
            g.say(message, voice="woman")
    else:
        with resp.gather(finishOnKey="#", action="/handle-number", method="POST") as g:
            message = "Welcome to PhoneBuzz! Please enter any number, followed by the pound sign, to play!"
            g.say(message, voice="woman")

    return str(resp)

def replay_call(num, delay, phone):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    new_url = url + "replay-number?num=" + str(num)
    print(phone)
    time.sleep(delay)
    call = client.calls.create(to='+1'+str(phone),
                               from_=TWILIO_CALLER_ID,
                               url=new_url)
@app.route("/replay/<id>", methods=['GET', 'POST'])
def replay(id):
    cursor = connect.cursor()
    phone = cursor.execute("SELECT phonenum FROM calls WHERE id=" + str(id))
    phone = phone.fetchall()[0][0]
    delay = cursor.execute("SELECT delay FROM calls WHERE id=" + str(id))
    delay = delay.fetchall()[0][0]
    num = cursor.execute("SELECT num FROM calls WHERE id=" + str(id))
    num = num.fetchall()[0][0]
    if not num:
        cursor = connect.cursor()
        cursor.execute("DELETE FROM calls WHERE num is NULL")
        cursor.close()
        return '''
            <title>Recall Could Not Be Initiated</title>
              <h1>There was no number stored for this replay. </h1>
              <h2>This is probably because a user did not input a number or hung up. This field will now be deleted from the home page.</h2>
              <a href={}>Return</a>'''.format(url)
    cursor = connect.cursor()
    insert = "INSERT INTO calls (id, datetime, delay, phonenum, num) VALUES "
    insert = insert + "(NULL, CURRENT_TIMESTAMP," + str(delay) + "," + str(phone) + "," + str(num) + ")"
    cursor.execute(insert)
    connect.commit()
    cursor.close()

    p = Process(target=replay_call, args=(num, delay, phone))
    p.start()
    
    message = "Thank you for using PhoneBuzz! Your recall to "+str(phone)+", with delay "+ str(delay) + " seconds has been initiated."
    title = "Recall Initiated"
    return render_template('timer.html', delay=int(delay),message=message,call=title)

@app.route("/replay-number", methods=['GET', 'POST'])
def replay_number():
    number = request.args.get("num")
    number = int(number)
    
    resp = VoiceResponse()
    message = "Welcome to PhoneBuzz Replay! The number is " + str(number) + "..."

    message += fizz_bizz(number)
    
    message += "...Thank you for using PhoneBuzz!"   
    
    resp.say(message, voice="woman")
    return str(resp)

@app.route("/handle-number", methods=['GET', 'POST'])
def handle_number():
        
    number_string = request.values.get('Digits', None)
    number = int(number_string)
    try:
        ident = request.args.get('id')
    except:
        cursor = connect.cursor()
        ident = cursor.execute("SELECT MAX(id) FROM calls")
        ident = ident.fetchone()
        ident = ident[0]
        cursor.close()
    try:
        cursor = connect.cursor()
        stmt = "UPDATE calls SET num=" + str(number) + " WHERE id=" + str(ident)
        print(stmt)
        cursor.execute(stmt)
        connect.commit()
    except:
        print("incoming call")

    resp = VoiceResponse()
    message = "..."
    
    lst = fizz_bizz(number)
    
    message += lst
    message += "...Thank you for using PhoneBuzz!"
    resp.say(message, voice="woman")
    cursor = connect.cursor()
    cursor.execute("DELETE FROM calls WHERE num is NULL")
    cursor.close()
    return str(resp)


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), use_reloader=False)
