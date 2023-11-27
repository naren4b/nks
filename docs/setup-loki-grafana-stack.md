# Have a KIND cluster

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
  replicas: 1
test:
  enabled: false
gateway:
  enabled: false
monitoring:
  lokiCanary:
    enabled: false
  selfMonitoring:
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

#### ![Add Loki data source ](image.png)

Visit http://localhost:3000/connections/datasources/loki

#### ![Add basic dashboard](image-1.png)

Visit http://localhost:3000/dashboard/new?orgId=1
Add example: [loki-general-dashboard.json](../apps/loki/loki-general-dashboard.json)
