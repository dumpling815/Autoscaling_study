# Autoscaler python file
import requests
from kubernetes import client, config
from kubernetes.stream import stream

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


# This URL is only available for Korea University network
# Leveraging http protocol to communicate with Prometheus server
master_node_prometheus_url = "http://163.152.20.79:30090"
aigpu1_prometheus_url = "http://163.152.20.215:30090"

# Loading K8s cluster config
config.load_kube_config()
apps_v1 = client.AppsV1Api()
v1 = client.CoreV1Api()
print("Listing pods with their IPs")
print("---------------------------")
all_deployment = apps_v1.list_deployment_for_all_namespaces(watch=False, pretty='pretty')
all_namespace = v1.list_namespace(watch= False)
all_pod = v1.list_pod_for_all_namespaces(watch=False)

deployment_dict = all_deployment.to_dict()
namespace_dict = all_namespace.to_dict()
pod_dict = all_pod.to_dict()
#print((all_deployment.to_dict()['items']))

print(len(deployment_dict))
print(len(namespace_dict))
print(len(pod_dict))



TARGET_NAMESPACE = 'target'
TARGET_DEPLOYMENT = 'autoscaling-deployment'
replica_num = 6
print(f"Target deployment: {TARGET_DEPLOYMENT} in namespace: {TARGET_NAMESPACE}")
print(f"Scaling to {replica_num}...")
try:
    scale_deployment(namespace= TARGET_NAMESPACE, deployment_name=TARGET_DEPLOYMENT, replicas=replica_num)
except:
    print(f"Something gone wrong at scale_deployment...")

QUERY = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100 )'

response_master = requests.get(f"{master_node_prometheus_url}/api/v1/query", params={"query": QUERY})
data_master = response_master.json()

if data_master["status"] == "success":
    for result in data_master["data"]["result"]:
        print(f"Instance: {result['metric']['instance']}, CPU Usage: {result['value'][1]}%")
else:
    print("Failed to fetch metrics: ", data_master)