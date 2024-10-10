import requests
import time
import subprocess
import datetime
import os
import yaml

PROMETHEUS_URL = ""
TARGET_CLUSTER_CONTEXT = ""

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


def get_failed_pods(target_cluster_context):
    print(f"Monitoring pod status...{datetime.datetime.now()}")
    subprocess.run(['kubectl','config','use-context',target_cluster_context])
    namespace = subprocess.run(['kubectl','get','ns','-o=jsonpath={.items[*].metadata.name}'], capture_output=True, text=True).stdout.split(' ')
    query = "kube_pod_status_phase{exported_namespace=~'"+ "|".join(namespace) +"',phase=~'Pending|Unknown|Failed'} > 0"
    result = query_prometheus(query)
    if result:
        for item in result:
            pod = item['metric'].get('pod', 'unknown')
            exported_namespace = item['metric'].get('exported_namespace', 'unknown')
            phase = item['metric'].get('phase', 'unknown')
            print(f"pod: {pod} namespace: {exported_namespace} phase: {phase}")
            path = f'{os.path.abspath(__file__)[:-8]}/yaml_data/{pod}.yaml'
            if not os.path.isfile(path):
                #try:
                yaml_data = yaml.safe_load(subprocess.run(['kubectl','get','pod',pod, '-n', exported_namespace ,'-o' 'yaml'], capture_output=True, text=True).stdout)
                
                minimal_data = {
                "apiVersion": yaml_data.get("apiVersion", "v1"),
                "kind": yaml_data.get("kind", "Pod"),
                "metadata": {
                    "name": yaml_data["metadata"].get("name", "minimal-pod"),
                    "labels": yaml_data["metadata"].get("labels", {}),
                },
                "spec": {
                    "containers": yaml_data["spec"].get("containers", []),
                    "restartPolicy": yaml_data["spec"].get("restartPolicy", "Always")
                }
                }
                with open(path, 'w') as f:
                    yaml.dump(minimal_data, f, default_flow_style=False, allow_unicode=True)
                #except:
                #    print("missing pod data. Maybe prometheus monitoring failed.")
            else:
                print("YAML data already exists for this pod")
    else:
        print("No data returned")

def check_pod():
    print("Running check_pod")
    print("this script will check the status of pods every minute.")
    # kubectl use-context swipe
    # yamlファイルを選ぶ
    # yamlファイルをkubectl applyで適用する
    # 一定時間待つ
    # 作成したPodがrunningになるか確認する
    # 　runnningになっていたらアラートを管理者にそうでなければユーザに
    #Podを削除して環境をリセット


if __name__ == "__main__":
    
    while True:
        get_failed_pods(TARGET_CLUSTER_CONTEXT)
        print()
        check_pod()
        time.sleep(60)
