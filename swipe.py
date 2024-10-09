import requests
import json
import time
import subprocess
import datetime
import os
import yaml

PROMETHEUS_URL = ""

def query_prometheus(query):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {
        "query": query
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            return result['data']['result']
        else:
            print("Failed to fetch data:", result['error'])
    else:
        print("HTTP request failed with status code:", response.status_code)

if __name__ == "__main__":
    namespace = subprocess.run(['kubectl','get','ns','-o=jsonpath={.items[*].metadata.name}'], capture_output=True, text=True).stdout.split(' ')
    query = "kube_pod_status_phase{exported_namespace=~'"+ "|".join(namespace) +"',phase=~'Pending|Unknown|Failed'} > 0"
    
    while True:
        print(f"Monitoring pod status...{datetime.datetime.now()}")
        result = query_prometheus(query)
        if result:
            for item in result:
                pod = item['metric'].get('pod', 'unknown')
                exported_namespace = item['metric'].get('exported_namespace', 'unknown')
                phase = item['metric'].get('phase', 'unknown')
                print(f"pod: {pod} namespace: {exported_namespace} phase: {phase}")
                path = f'{os.path.abspath(__file__)[:-8]}/yaml_data/{pod}.yaml'
                if not os.path.isfile(path):
                    yaml_data = yaml.safe_load(subprocess.run(['kubectl','get','pod',pod, '-n', exported_namespace ,'-o' 'yaml'], capture_output=True, text=True).stdout)
                    del yaml_data['metadata']['creationTimestamp']
                    del yaml_data['metadata']['resourceVersion']
                    del yaml_data['metadata']['uid']
                    del yaml_data['status']
                    with open(path, 'w') as f:
                        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    print("YAML data already exists for this pod")
        else:
            print("No data returned")
        
        print()

        time.sleep(60)
