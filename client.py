#protobuff imports made from our server app.py
import request_pb2
import response_pb2

import string
import requests
import random

#heroku server URL made by running the server on heroku deployment
baseURL = "https://coen424-assignmnent1-heroku.herokuapp.com"

#JSON URL to access the json extension of the server
JSONURL = baseURL+"/api/v1/json/batches"

#protobuf URL to access the protobuff extension of the server
ProtoURL = baseURL+"/api/v1/protobuf/batches"

#generates a random ascii string to identify the unique samples
def genRandom():
    l = string.ascii_lowercase
    return ''.join(random.choice(l) for j in range(10))

#requesting json from the server
def reqJSON(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):
    #creating a json object with our variables
    jsonObject= {"rfwID": genRandom(), "benchmarkType": benchmarkType,
                 "workloadMetric": workloadMetric, "batchUnit": int(batchUnit),
                 "batchID": int(batchID), "batchSize": int(batchSize)}

    #making a response to the server
    response = requests.get(JSONURL, json=jsonObject)

    if (response.status_code > 200):
        print("ERROR CODE: ", response.status_code)

    #displaying the json response 
    jsonResp = response.json()
    if jsonResp.get('rfwID'):
        print('Request ID: '+str(jsonResp.get('rfwID')))
        print('Last batch ID: '+str(jsonResp.get('lastBatchID')))
        print('Samples: '+str(jsonResp.get('Samples')))
    else:
        print(jsonResp)

#requesting protobuff (XML) from the server
def reqProtobuf(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):
    #protobuf object
    requProtoRFW = request_pb2.RFW()
    requProtoRFW.rfw_id = genRandom()
    requProtoRFW.benchmark_type = benchmarkType
    requProtoRFW.workload_metric = workloadMetric
    requProtoRFW.batch_unit = batchUnit
    requProtoRFW.batch_id = batchID
    requProtoRFW.batch_size = batchSize

    #requesting to the server
    response = requests.get(ProtoURL, data=requProtoRFW.SerializeToString(), headers = {'Content-Type': 'application/octet-stream'})

    #validating the response
    if (response.status_code > 200):
        print("ERROR: There may have been a problem with the response.")
        print(response.content)
    else:
        #this is a good response
        respProtoRFD = response_pb2.RFD()
        respProtoRFD.ParseFromString(response.content)
        print(respProtoRFD)

#user input for client to run application
#user can access the json or protobuf
objectType = input("Enter 'JSON' or 'ProtoBuf': ")
#user can choose which csv file to enter
benchmarkType = input("Enter BenchMark Type  (DVD-testing, DVD-training, NDBench-testing, NDBench-training): ")
#user chooses the column of the csv file 
workloadMetric = input("Enter Workload Metric (CPUUtilization_Average, NetworkIn_Average ,NetworkOut_Average, MemoryUtilization_Average, Final_Target: ")
#user enters the batch unit
batchUnit = input("Enter Batch Unit (0,1,2...): ")
#user enters the batch id
batchID = input("Enter batch ID (0,1,2...): ")
#user enters the batch size
batchSize = input("Enter batch size (0,1,2...): ")

#if the user chose JSON, then request json
if objectType == 'JSON':
    reqJSON(benchmarkType, workloadMetric,
            int(batchUnit), int(batchID), int(batchSize))

#if user chose protobuf, then request protobuf
if objectType == 'ProtoBuf':
    reqProtobuf(benchmarkType, workloadMetric,
                int(batchUnit), int(batchID), int(batchSize))
