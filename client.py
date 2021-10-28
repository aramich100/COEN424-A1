import string
import argparse
import requests
import random
import request_pb2
import response_pb2

base_url = "https://coen424-assignmnent1-heroku.herokuapp.com"

url_json = base_url+"/api/v1/json/batches"
url_protobuf = base_url+"/api/v1/protobuf/batches"


def str_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    elif value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# parser = argparse.ArgumentParser(description='Process some integers.')

# parser.add_argument('benchmark_type', type=str,
#                     help='Can only be \'DVD-testing\', \'DVD-training\',\
#                          \'NDBench-testing\', \'NDBench-training\'')
# parser.add_argument('workload_metric', type=str,
#                     help='Can only be \'CPUUtilization_Average\',\
#                          \'NetworkIn_Average\', \'NetworkOut_Average\',\
#                         \'MemoryUtilization_Average\', \'Final_Target\'')
# parser.add_argument('batch_unit', type=int,
#                     help='the number of samples contained in each batch,\
#                          such as 100')
# parser.add_argument('batch_id', type=int,
#                     help='such as the 1st or 2nd or... 5th Batch')
# parser.add_argument('batch_size', type=int,
#                     help='such as the how many batches to return,\
#                          5 means 5 batches to return')
# parser.add_argument("--protobuf", type=str_bool, nargs='?',
#                     const=True, default=False,
#                     help="will send and receive data with googles \
#                         protocol buffer")


# Generates a random string (as we need to make this unique)
def get_random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


# This function is used to call the server with json protocol
def request_with_json(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):

    # Build request body
    json_body = {
        "rfw_id": get_random_string(),
        "benchmark_type": benchmarkType,
        "workload_metric": workloadMetric,
        "batch_unit": int(batchUnit),
        "batch_id": int(batchID),
        "batch_size": int(batchSize)
    }

    # Send request to server
    response = requests.get(url_json, json=json_body)

    # Look at status
    if (response.status_code > 200):
        print("Something went wrong the response may be bad!")

    # Print result
    json_response = response.json()
    if json_response.get('rfw_id'):
        print('request ID: '+str(json_response.get('rfw_id')))
        print('last batch ID: '+str(json_response.get('last_batch_id')))
        print('samples: '+str(json_response.get('samples')))
    else:
        print(json_response)


# This function is used to call the server with protcol buffer
def request_with_protobuf(benchmarkType, workloadMetric, batchUnit, batchID, batchSize):
    # Create protocol buffer object
    request_RFW_protobuf = request_pb2.RFW()
    request_RFW_protobuf.rfw_id = get_random_string()

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


# new_args = parser.parse_args()

# if new_args.protobuf:
#     request_with_protobuf(new_args)
# else:
#     request_with_json(new_args)

objectType = input("Enter 'JSON' or 'ProtoBuff':   ")

benchmarkType = input(
    "Enter BenchMark Type  (DVD-testing, DVD-training, NDBench-testing, NDBench-training)  : ")
workloadMetric = input(
    "Enter Workload Metric (CPUUtilization_Average, NetworkIn_Average ,NetworkOut_Average, MemoryUtilization_Average, Final_Target :    ")
batchUnit = input("Enter Batch Unit (0,1,2...)    :")
batchID = input("Enter batch ID     (0,1,2...)    :")
batchSize = input("Enter batch size (0,1,2...)    :")

if objectType == 'JSON':
    request_with_json(benchmarkType, workloadMetric,
                      int(batchUnit), int(batchID), int(batchSize))

if objectType == 'ProtoBuff':
    request_with_protobuf(benchmarkType, workloadMetric,
                          int(batchUnit), int(batchID), int(batchSize))
