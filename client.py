# Protobuff Imports
import request_pb2
import response_pb2

import string
import requests
import random


# Heroku Server Base URL
base_url = "https://coen424-assignmnent1-heroku.herokuapp.com"

# JSON URL Extension
url_json = base_url+"/api/v1/json/batches"

# Protobuf URL Extension
url_protobuf = base_url+"/api/v1/protobuf/batches"


# Generates a random string (as we need to make this unique)
def genRandom():
    l = string.ascii_lowercase
    return ''.join(random.choice(l) for i in range(10))


# This function is used to call the server with json protocol
def reqJSON(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):

    json_obj = {
        "rfw_id": genRandom(),
        "benchmark_type": benchmarkType,
        "workload_metric": workloadMetric,
        "batch_unit": int(batchUnit),
        "batch_id": int(batchID),
        "batch_size": int(batchSize)}

    # Send request to server
    response = requests.get(url_json, json=json_obj)

    if (response.status_code > 200):
        print(" -- ERROR CODE -- :  ", response.status_code)

    # Print result
    json_resp = response.json()
    if json_resp.get('rfw_id'):
        print(' Request ID: '+str(json_resp.get('rfw_id')))
        print(' Last batch ID: '+str(json_resp.get('last_batch_id')))
        print(' Samples: '+str(json_resp.get('samples')))
    else:
        print(json_resp)


# This function is used to call the server with protcol buffer
def reqProtobuf(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):
    # Create protocol buffer object
    request_RFW_protobuf = request_pb2.RFW()
    request_RFW_protobuf.rfw_id = genRandom()
    request_RFW_protobuf.benchmark_type = benchmarkType
    request_RFW_protobuf.workload_metric = workloadMetric
    request_RFW_protobuf.batch_unit = batchUnit
    request_RFW_protobuf.batch_id = batchID
    request_RFW_protobuf.batch_size = batchSize

    # Make the request to the server
    response = requests.get(url_protobuf,
                            data=request_RFW_protobuf.SerializeToString(),
                            headers={'Content-Type': 'application/octet-stream'})

    # Make sure the response is successful
    if (response.status_code > 200):
        print("Something went wrong the response may be bad!")
        print(response.content)
    else:
        # Process successful response
        response_protobuf_RFD = response_pb2.RFD()
        response_protobuf_RFD.ParseFromString(response.content)
        print(response_protobuf_RFD)


# USER INPUT
objectType = input("Enter 'JSON' or 'ProtoBuff':   ")

benchmarkType = input(
    "Enter BenchMark Type  (DVD-testing, DVD-training, NDBench-testing, NDBench-training)  : ")
workloadMetric = input(
    "Enter Workload Metric (CPUUtilization_Average, NetworkIn_Average ,NetworkOut_Average, MemoryUtilization_Average, Final_Target :    ")
batchUnit = input("Enter Batch Unit (0,1,2...)    :  ")
batchID = input("Enter batch ID     (0,1,2...)    :  ")
batchSize = input("Enter batch size (0,1,2...)    :  ")

if objectType == 'JSON':
    reqJSON(benchmarkType, workloadMetric,
            int(batchUnit), int(batchID), int(batchSize))

if objectType == 'ProtoBuff':
    reqProtobuf(benchmarkType, workloadMetric,
                int(batchUnit), int(batchID), int(batchSize))
