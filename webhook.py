### Library Includes and Boilerplate ###
from flask import Flask, request, jsonify
from urllib.request import urlopen, Request
from pprint import pprint
import json
import os

app = Flask(__name__)
@app.route('/', methods=['POST']) ###Listen on / for POST requests
def webhook():
    allowed = True #Default to allowed
    result = ""
    request_info = request.json #read the JSON into a Python dict
    #pprint(request_info)
    
    try:
        annotations=request_info['request']['object']['metadata']['annotations']
    except:
        print('Bad request: ' + request_info)
        return
    
    if 'nginx.router.openshift.io/port' in annotations.keys():
        port = annotations['nginx.router.openshift.io/port']
        if 'nginx.router.openshift.io/protocol' in annotations.keys():
            protocol = annotations['nginx.router.openshift.io/protocol']
            port = port + protocol
            
            with open('/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
                token = f.read()
            
            try:
                master = os.environ['APIURL']
            except:
                print('Set API endpoint URL environment "APIURL"')
                return
                
            limit = os.environ.get('LIMIT', 500)
            path = '/apis/route.openshift.io/v1/routes?limit=' + limit
            req = Request(master + path, headers={'Authorization': 'Bearer ' + token})
            resp = urlopen(req, cafile='/run/secrets/kubernetes.io/serviceaccount/ca.crt')
            data = json.load(resp)
            
            ports = []
            try:
                items = data['items']
            except:
                print('Bad response: ' + data)
            for item in items:
                try:
                    a=item['metadata']['annotations']
                    ports.append(a['nginx.router.openshift.io/port'] + a['nginx.router.openshift.io/protocol'])
                except:
                    pass
        
            if port in ports:
                allowed = False
                result = 'Port ' + port + ' is already used'
        else:
            allowed = False
            result = 'No "nginx.router.openshift.io/protocol" annotations in metadata'

    # Now construct the response JSON
    admission_response = {
        "uid": request_info['request']['uid'],
        "allowed": allowed,
        "result": result
    }
    admissionReview = {
         "response": admission_response
    }
    return jsonify(admissionReview) #And send it back!

app.run(host='0.0.0.0', debug=True, ssl_context=('/cert/tls.crt', '/cert/tls.key'))
