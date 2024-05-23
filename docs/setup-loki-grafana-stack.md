# Install Single Binary Loki Promtail Grafana stack in KIND cluster

![loki](https://github.com/naren4b/nks/assets/3488520/fa0674db-f45c-43da-98a1-2ca77c24d345)

In this blog post, we explore a quick and efficient way to set up a basic Loki-Promtail-Grafana stack in a KIND (Kubernetes in Docker) cluster. The tutorial provides a step-by-step guide, ensuring a seamless installation process. By leveraging these open-source tools, users can enhance their log monitoring and visualization capabilities within a Kubernetes environment. The simplicity of KIND makes it an ideal platform for testing and development, allowing users to easily deploy and manage the Loki logging system, Promtail agent, and Grafana dashboard for effective log analysis. Dive into the details and streamline your Kubernetes log management with this concise guide.

#### Have a KIND cluster

ref: [mykindk8scluster](https://naren4b.github.io/nks/mykindk8scluster.html) or [Demo Environment](https://killercoda.com/killer-shell-ckad/scenario/playground)

#### Install Loki
Loki custom helm value file
```bash
cat<<EOF >$PWD/loki-demo-values.yaml
---
loki:
  commonConfig:
    replication_factor: 1
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
    max_concurrent: 2


deploymentMode: SingleBinary
singleBinary:
  replicas: 1
  persistence:
    size: 1Gi # Chageit
chunksCache:
  writebackSizeLimit: 10MB



test:
  enabled: false
lokiCanary:
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

# Enable minio for storage
minio:
  enabled: true

# Zero out replica counts of other deployment modes
backend:
  replicas: 0
read:
  replicas: 0
write:
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
chunksCache:
  enabled: false
resultsCache:
  enabled: false

EOF
```


### Install helm-chart

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

REPO_NAME=grafana
REPO_PATH=loki
CHART_VERSION=6.5.2
CHART_APP_VERSION=loki
helm upgrade --install loki ${REPO_NAME}/${REPO_PATH}  --version ${CHART_VERSION} -f $PWD/loki-values.yaml -n monitoring
#helm uninstall loki  -n monitoring
```

#### Install promtail

```bash
cat<<EOF >$PWD/promtail-demo-values.yaml
config:
  clients:
    - url: http://loki:3100/loki/api/v1/push
      tenant_id: 1
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
REPO_NAME=grafana
REPO_PATH=grafana
CHART_VERSION=7.3.11
CHART_APP_VERSION=loki
helm upgrade --install grafana ${REPO_NAME}/${REPO_PATH}  --version ${CHART_VERSION} -n monitoring
kubectl  -n monitoring port-forward svc/grafana 3000:3000 --address 0.0.0.0

```

#### [Add Loki data source ]

![image](https://github.com/naren4b/nks/assets/3488520/d1c20e4e-586d-4365-bbfb-c050fb7d9c5d)
```
URL: http://loki:3100
#ADD Http Header 
X-Scope-OrgID: 1
```
Visit http://localhost:3000/connections/datasources/loki

#### [Add basic dashboard](https://github.com/naren4b/nks/blob/main/apps/loki/loki-general-dashboard.json)

![image-1](https://github.com/naren4b/nks/assets/3488520/818cff38-598f-4e3b-b8da-4f1ecc254b63)

Visit http://localhost:3000/dashboard/new?orgId=1

Add example: [loki-general-dashboard.json](../apps/loki/loki-general-dashboard.json)
