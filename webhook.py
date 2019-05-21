### Library Includes and Boilerplate ###
from flask import Flask, request, jsonify
from pprint import pprint
import json
app = Flask(__name__)
@app.route('/', methods=['POST']) ###Listen on / for POST requests
def webhook():
    allowed = True #Default to allowed
    request_info = request.json #read the JSON into a Python dict
    print(request_info)
#    for container_spec in request_info["request"]["object"]["spec"]["containers"]: #For each container defined in the request
#        if 'env' in container_spec: #if there are environment variables set....
#            print("Environment Variables Cannot Be Passed to Containers")
#            allowed = False #NOPE!

    # Now construct the response JSON
    admission_response = {
        "allowed": allowed
    }
    admissionReview = {
         "response": admission_response
    }
    return jsonify(admissionReview) #And send it back!

app.run(host='0.0.0.0', debug=True, ssl_context=('/cert/tls.crt', '/cert/tls.key'))
