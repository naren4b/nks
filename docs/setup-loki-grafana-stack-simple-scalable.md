# Install simple-scalable Loki Promtail Grafana stack in KIND cluster

![loki](https://github.com/naren4b/nks/assets/3488520/fa0674db-f45c-43da-98a1-2ca77c24d345)

In this blog post, we explore a quick and efficient way to set up a basic Loki-Promtail-Grafana stack in a KIND (Kubernetes in Docker) cluster. The tutorial provides a step-by-step guide, ensuring a seamless installation process. By leveraging these open-source tools, users can enhance their log monitoring and visualization capabilities within a Kubernetes environment. The simplicity of KIND makes it an ideal platform for testing and development, allowing users to easily deploy and manage the Loki logging system, Promtail agent, and Grafana dashboard for effective log analysis. Dive into the details and streamline your Kubernetes log management with this concise guide.

#### Have a KIND cluster

ref: [mykindk8scluster](https://naren4b.github.io/nks/mykindk8scluster.html) or [Demo Environment](https://killercoda.com/killer-shell-ckad/scenario/playground)

#### Install Loki

```
helm repo add grafana https://grafana.github.io/helm-charts

helm repo update

helm install --values values.yaml loki grafana/loki
helm upgrade --values values.yaml loki grafana/loki



```




Build and Load the image (ref: https://github.com/naren4b/monitoring-stack/tree/main/loki )

```bash
docker build -t loki-curator:1.1 .
kind create cluster
kind load docker-image loki-curator:1.1

```

Loki custom helm value file

```bash
cat<<EOF >$PWD/loki-demo-values.yaml
---
loki:
  schemaConfig:
    configs:
      - from: 2024-04-01
        store: tsdb
        object_store: s3
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
  ingester:
    chunk_encoding: snappy
  tracing:
    enabled: true
  querier:
    # Default is 4, if you have enough memory and CPU you can increase, reduce if OOMing
    max_concurrent: 4

#gateway:
#  ingress:
#    enabled: true
#    hosts:
#      - host: FIXME
#        paths:
#          - path: /
#            pathType: Prefix

deploymentMode: SimpleScalable

backend:
  replicas: 3
read:
  replicas: 3
write:
  replicas: 3

# Enable minio for storage
minio:
  enabled: true

# Zero out replica counts of other deployment modes
singleBinary:
  replicas: 0

ingester:
  replicas: 0
querier:
  replicas: 0
queryFrontend:
  replicas: 0
queryScheduler:
  replicas: 0
distributor:
  replicas: 0
compactor:
  replicas: 0
indexGateway:
  replicas: 0
bloomCompactor:
  replicas: 0
bloomGateway:
  replicas: 0
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
#helm uninstall loki
```

#### Install promtail

```bash
cat<<EOF >$PWD/promtail-demo-values.yaml
config:
  clients:
    - url: http://loki:3100/loki/api/v1/push
extraPorts:
   syslog:
     name: tcp-syslog
     annotations: {}
     labels: {}
     containerPort: 8514
     protocol: TCP
     service:
       type: ClusterIP
       clusterIP: null
       port: 1514
       externalIPs: []
       nodePort: null
       loadBalancerIP: null
       loadBalancerSourceRanges: []
       externalTrafficPolicy: null
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
