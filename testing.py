# Autoscaler python file

# This program leverages direct HTTP request instead of prometheus python library client_python
# If there is any needs to change the approach, visit "https://github.com/prometheus/client_python"
import requests

from kubernetes import client, config
from kubernetes.stream import stream

# For Pretty Print result of k8s API
import json



def scale_deployment(namespace: str, deployment_name: str, replicas: int):
    body = {"spec": {"replicas": replicas}}
    response = apps_v1.patch_namespaced_deployment_scale(
        name=deployment_name,
        namespace=namespace,
        body=body
    )
    print(f"Scaled {deployment_name} to {replicas} replicas")
    return response
def get_replica_num(cpu_performance: int, cpu_utilization: float):
    # Need to implement
    pass
def shallow_traverse(input: list):
    for element in input:
        if isinstance(element, dict):
            print(f"Dict keys: {element.keys()}")
        elif isinstance(element, str):
            print(f"String: {element}")
        else:
            print(f"Other: {element}, type: {type(element)}")
def fetch_metrics_prometheus(prometheus_url, query):
    # Note that response is Response object of requests library requests.Response
    response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": query})
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success":
            return data["data"]["result"]
        else:
            print(f"Failed to fetch metrics: {data}")
    else:
        print(f"HTTP ERROR: {response.status_code}")
    return [] # Return empty list when something gone wrong



# Loading K8s cluster config
config.load_kube_config()
apps_v1 = client.AppsV1Api()
v1 = client.CoreV1Api()


# This URL is only available for Korea University network
# Leveraging http protocol to communicate with Prometheus server
URL_APPEND = "/api/v1/query"
master_node_prometheus_ip = "http://163.152.20.79:30090"
aigpu1_prometheus_ip = "http://163.152.20.215:30090"
master_node_prometheus_url = master_node_prometheus_ip + URL_APPEND
aigpu1_prometheus_url = aigpu1_prometheus_ip + URL_APPEND


nodes_list = v1.list_node()
for node in nodes_list:
    print(f"Node name: {node.metadata.name}")


all_deployment = apps_v1.list_deployment_for_all_namespaces(watch=False, pretty='pretty')
all_namespace = v1.list_namespace(watch= False)
all_pod = v1.list_pod_for_all_namespaces(watch=False)

target_deployment = apps_v1.list_namespaced_deployment(namespace='target')

# If you want to see entire structure of target_deployment, use follwing line
#print(json.dumps(client.ApiClient().sanitize_for_serialization(target_deployment), indent=4))

for deployment in target_deployment.items:
    print(f"Deployment name: {deployment.metadata.name}")
    print(f"Deployment namespace: {deployment.metadata.namespace}")
    print(f"Current Replica #: {deployment.spec.replicas}")
    print(f"Selector: {deployment.spec.selector.match_labels}")


TARGET_NAMESPACE = 'target'
TARGET_DEPLOYMENT = 'autoscaling-deployment'
REQUEST_PERIOD = 30 #second
THRESHOLD = 75.0    #percentage
NODE_CPU_UTIL_QUERY = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100 )'
POD_CPU_UTIL_QUERY = 'kube_deployment_status_condition'




replica_num = 10
print(f"----------------------------------------------------------------------")
print(f"Target deployment: {TARGET_DEPLOYMENT} in namespace: {TARGET_NAMESPACE}")
print(f"Scaling to {replica_num}...")
try:
    scale_deployment(namespace= TARGET_NAMESPACE, deployment_name=TARGET_DEPLOYMENT, replicas=replica_num)
    print(f"Scaling Successed.")
except:
    print(f"Something gone wrong at scale_deployment...")
print(f"----------------------------------------------------------------------")


response_master = requests.get(f"{master_node_prometheus_url}/api/v1/query", params={"query": NODE_CPU_UTIL_QUERY})
data_master = response_master.json()

print(f"Listing Node & CPU usage")
if data_master["status"] == "success":
    for result in data_master["data"]["result"]:
        print(f"Instance: {result['metric']['instance']}, CPU Usage: {result['value'][1]}%")
else:
    print("Failed to fetch metrics: ", data_master)