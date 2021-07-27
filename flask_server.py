# # import main Flask class and request object
from flask import Flask, request
import json

import requests
import os
import base64

from discord_bot.update_sub_modules import modules as bq_modules
from discord_bot.machine_id import decrypt as machine_id_decrypt

'''
error codes

500 - OK
505 - unknown check_for
600 - data validation error
700 - client general exception
'''



current_directory = os.getcwd()
def local_fp(relative_fp:str):
    return os.path.join(current_directory, relative_fp)
local_fp_data = local_fp('discord_bot/data.json')
class stored_data:
    data = {}
    def load():
        with open(local_fp_data,'r') as f:
            stored_data.data = json.load(f)
    def dump():
        with open(local_fp_data,'w') as f:
            json.dump(stored_data.data, f, indent=4)
stored_data.load()



def handle_request(req_data:dict) -> str:
    """handles a request and returns stringified json"""

    stored_data.load()

    machine_id_encoded = req_data.get('machine_id', None)

    if machine_id_encoded is None:
        return json.dumps({
        "status": 600,
        "response": "No Machine ID was supplied"})
    
    # decrypt the machine id
    machine_id = machine_id_decrypt(machine_id_encoded)
    if machine_id is None:
        return json.dumps({
        "status": 600,
        "response": "Supplied Machine ID invalid"})
    
    check_for = req_data.get('check_for', 'unknown')

    if check_for == 'verified':
        verified = None
        matching_ids = [p for p in stored_data.data['verified_purchases'] if p['machine_id'] == machine_id]
        if len(matching_ids) > 0:
            verified = matching_ids[0]
            return json.dumps({
            "status": 500,
            "response": {
                "verified": True,
                "modules": verified['modules_owned']
            }})
        return json.dumps({
        "status": 500,
        "response": {
            "verified": False
        }})

    elif check_for == 'pending':
        pending = None
        matching_ids = [p for p in stored_data.data['pending_purchases'] if p['machine_id'] == machine_id]
        if len(matching_ids) > 0:
            pending = matching_ids[0]
            return json.dumps({
            "status": 500,
            "response": {
                "pending": True,
                "modules": pending['module_uids']
            }})
        return json.dumps({
        "status": 500,
        "response": {
            "pending": False
        }})
        
    else:
        return json.dumps({
        "status": 505,
        "response": "check_for is unknown"})



app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/validation/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        req_data = request.get_json()
        print(req_data)

        return handle_request(req_data)

    return "<p style=\"color: blue; font-size: 25px;\">this site only supports POST requests</p>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=7912)