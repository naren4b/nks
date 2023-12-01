# Install basic Loki Promtail Grafana stack in KIND cluster 
![misc-loki-grafana](https://github.com/naren4b/nks/assets/3488520/fcb23a61-c6b7-4d5c-adda-0c5d744f355d)


#### Have a KIND cluster

ref: [mykindk8scluster](https://naren4b.github.io/nks/mykindk8scluster.html) or [Demo Environment](https://killercoda.com/killer-shell-ckad/scenario/playground)

#### Install Loki

```bash
cat<<EOF >$PWD/loki-demo-values.yaml
loki:
  commonConfig:
    replication_factor: 1
  storage:
    type: "filesystem"
  auth_enabled: false
singleBinary:
  persistence:
    size: 1Gi
    #storageClass: standard
  replicas: 1
  extraContainers:
    - name: curator
      image: "loki-curator:1.9" # https://github.com/grafana/loki/issues/2314#issuecomment-1028637269 
      imagePullPolicy: IfNotPresent
      env:
        - name: SPACEMONITORING_FOLDER
          value: "/data/loki/chunks"
        - name: SPACEMONITORING_DELETINGITERATION
          value: "5"
        - name: SPACEMONITORING_MAXUSEDPERCENTE
          value: "80"
        - name: CLEANUP_INTERVAL
          value: "60"
      resources:
        limits:
          memory: 1Gi
        requests:
          memory: 10Mi
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
        - name: storage
          mountPath: "/data"
          subPath:

test:
  enabled: false
gateway:
  enabled: false
monitoring:
  lokiCanary:
    enabled: false
  selfMonitoring:
    enabled: false
    grafanaAgent:
      installOperator: false

EOF
```

### Install helm-chart

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

REPO_NAME=grafana
REPO_PATH=loki
CHART_VERSION=5.38.0
CHART_APP_VERSION=loki
helm install loki ${REPO_NAME}/${REPO_PATH}  --version ${CHART_VERSION} -f $PWD/loki-demo-values.yaml
helm uninstall loki
```

#### Install promtail

```bash
cat<<EOF >$PWD/promtail-demo-values.yaml
config:
  clients:
    - url: http://loki:3100/loki/api/v1/push
EOF
```

```bash

REPO_NAME=grafana
REPO_PATH=promtail
CHART_VERSION=6.15.3
CHART_APP_VERSION=promtail
helm install promtail ${REPO_NAME}/${REPO_PATH}  --version ${CHART_VERSION} -f $PWD/promtail-demo-values.yaml

```

##### Install Grafana

```bash
kubectl run grafana --image=grafana/grafana --port=3000
kubectl expose pod grafana --port=3000 --name=grafana
kubectl port-forward svc/grafana 3000:3000 --address 0.0.0.0

```

#### [Add Loki data source ]
![image](https://github.com/naren4b/nks/assets/3488520/d1c20e4e-586d-4365-bbfb-c050fb7d9c5d)
_url: http://loki:3100_
Visit http://localhost:3000/connections/datasources/loki

#### [Add basic dashboard](https://github.com/naren4b/nks/blob/main/apps/loki/loki-general-dashboard.json)
![image-1](https://github.com/naren4b/nks/assets/3488520/818cff38-598f-4e3b-b8da-4f1ecc254b63)

Visit http://localhost:3000/dashboard/new?orgId=1

Add example: [loki-general-dashboard.json](../apps/loki/loki-general-dashboard.json)
