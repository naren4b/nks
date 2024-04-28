# Deploy a batch monitoring stack with Prometheus PushGateway in Kubernetes cluster

![k8s-prom-pushgateway](https://github.com/naren4b/nks/assets/3488520/ee960052-abca-4860-838b-285ce88d0c33)

The Prometheus PushGateway serves as an invaluable tool for managing batch metrics, enabling the integration of Internet of Things (IoT) sensor data into Prometheus. This guide illustrates the process of configuring a PushGateway instance and recording metrics from a basic BASH script.

It presents a straightforward approach for system administrators to visualize data external to Kubernetes.

### The setup comprises several core applications and jobs responsible for fetching the data:

1. **Grafana:** serves as a robust visualization tool utilized to showcase our metrics. It functions as the 'frontend' of our system.
2. **Prometheus:** operates as a highly scalable time-series database, serving as the 'backend' of our setup. It is typically configured to regularly scrape metrics data from applications.
3. **PushGateway:** acts as a 'sink' or 'buffer' for metric data that has a short lifespan, making it unsuitable for Prometheus scraping. This is where our cron jobs will log data, as the containers do not persist long enough for Prometheus to capture them.
### Cluster Setup 
Let's use a Killercoda K8s cluster : [killercoda.com](https://killercoda.com/killer-shell-cks/scenario/container-namespaces-docker)
### Installing Grafana 
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
cat<<EOF> /tmp/grafana-values.yaml 
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus-operated:9090
      access: proxy
      isDefault: true
EOF
helm upgrade --install grafana grafana/grafana --namespace monitoring --create-namespace -f /tmp/grafana-values.yaml 
kubectl port-forward svc/grafana -n monitoring 3000:80 --address 0.0.0.0 &
// Get the admin password
kubectl get secrets -n monitoring grafana -o jsonpath={".data.admin-password"} |  base64 -d 
```

### Installing Prometheus & Prometheus Operator 
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 
helm repo update
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace \
    --set=alertmanager.enabled=false,kubeProxy.enabled=false,kubeStateMetrics.enabled=false,nodeExporter.enabled=false,grafana.enabled=false,kubelet.enabled=false,kubeApiServer.enabled=false,kubeEtcd.enabled=false,kubeScheduler.enabled=false,coreDns.enabled=false,kubeControllerManager.enabled=false
kubectl port-forward svc/prometheus-operated -n monitoring 9090 --address 0.0.0.0 &
```
### Installing PushGateway 
```
cat<<EOF > /tmp/push-gateway-values.yaml 
    metrics:
      enabled: true
    serviceMonitor:
      enabled: true
      namespace: monitoring
      additionalLabels:
        app.kubernetes.io/instance: prometheus-pushgateway
        app.kubernetes.io/name: prometheus-pushgateway
EOF

helm upgrade --install prometheus-pushgateway prometheus-community/prometheus-pushgateway --namespace monitoring --create-namespace -f /tmp/push-gateway-values.yaml 
kubectl label servicemonitors.monitoring.coreos.com prometheus-pushgateway release=prometheus -n monitoring
kubectl port-forward svc/prometheus-pushgateway -n monitoring 9091 --address 0.0.0.0 &
```
### Check Everything working fine
```bash
kubectl get pod -n monitoring --no-headers -w
```
![image](https://github.com/naren4b/nks/assets/3488520/96b76ffe-4e5f-4af4-9ac8-669a42fbe95b)
![image](https://github.com/naren4b/nks/assets/3488520/c52fbb0d-906d-47e8-89e4-7f48bfeda4da)
![image](https://github.com/naren4b/nks/assets/3488520/84976316-2a55-4ef4-804f-9267e882af2e)


### Generate few metrics through curl command into pushgateway api endpoint
```bash
// Simple single metrics
echo "http_request_duration_seconds 5" | curl --silent --data-binary @- "http://localhost:9091/metrics/job/demo"
```
![image](https://github.com/naren4b/nks/assets/3488520/cfb83aa3-ee44-4993-8aea-8160c399ee0a)
![image](https://github.com/naren4b/nks/assets/3488520/945fba14-4650-42ea-b76f-469b842897f3)
![image](https://github.com/naren4b/nks/assets/3488520/ed811052-7317-43eb-a5f6-bd857df54bef)

### Automation Script for generating random metrics
```bash 
cat<<EOF >genmetrics.sh
type=("apple" "banana" "orange" "grape")
array_length=${#type[@]}
random_index=$((RANDOM % array_length))
job=${type[$random_index]}
value=$((RANDOM % 10 + 1))
echo "http_request_duration_seconds{client=\"x\",req=\"$(date +%s)\",job=\"$job\"} $value"
echo "http_request_duration_seconds{client=\"x\",req=\"$(date +%s)\"} $value" | curl --silent --data-binary @- "http://localhost:9091/metrics/job/$job"
EOF
```
![image](https://github.com/naren4b/nks/assets/3488520/1376b94b-9aa3-4f02-beb9-8f57c16f91a8)
![image](https://github.com/naren4b/nks/assets/3488520/9f31d1e2-3254-4beb-b3f8-6c388e92dedb)


Ref: 
- https://www.civo.com/learn/deploy-a-batch-monitoring-stack-with-prometheus-pushgateway






   
