![vls-gpt (1)](https://github.com/user-attachments/assets/e4bd4f45-c4fa-4fb7-9d0f-99c866c813bc)

# 🚀 Exploring VictoriaLogs: A Fast and Resource-Efficient Log Management Solution
VictoriaLogs is an open-source, user-friendly database for logs from VictoriaMetrics, designed to be efficient, scalable, and easy to operate.

#### VictoriaLogs provides the following features:
- It is recource-efficient and fast.
- It uses up to 30x less RAM and up to 15x less disk space than other solutions such as Elasticsearch and Grafana Loki. See benchmarks and this article for details.
- VictoriaLogs’ capacity and performance scales linearly with the available resources (CPU, RAM, disk IO, disk space).
- It runs smoothly on Raspberry PI and on servers with hundreds of CPU cores and terabytes of RAM.
- It can accept logs from popular log collectors.
- It is much easier to set up and operate compared to Elasticsearch and Grafana Loki, since it is basically zero-config.
- It provides easy yet powerful query language with full-text search capabilities across all the log fields. See LogsQL docs.
- It provides built-in web UI for logs’ exploration.
- It provides Grafana plugin for building arbitrary dashboards in Grafana.
- It provides interactive command-line tool for querying VictoriaLogs.
- It can be seamlessly combined with good old Unix tools for log analysis such as grep, less, sort, jq, etc. See these docs for details.
- It support log fields with high cardinality (e.g. high number of unique values) such as trace_id, user_id and ip.
- It is optimized for logs with hundreds of fields (aka wide events).
- It supports multitenancy.
- It supports out-of-order logs’ ingestion aka backfilling.
- It supports live tailing for newly ingested logs.
- It supports selecting surrounding logs in front and after the selected logs.
- It supports alerting

🔧 My Setup Steps:

1️⃣ Installed VictoriaLogs using Helm charts.

2️⃣ Exposed the Web UI for quick log exploration.

3️⃣ Deployed Promtail for log forwarding.

4️⃣ Integrated Grafana to visualize logs with dashboards.

#  Installed VictoriaLogs using Helm charts.
```bash
helm repo add vm https://victoriametrics.github.io/helm-charts/
helm repo update
helm search repo vm/victoria-logs-single -l
helm show values vm/victoria-logs-single > victoria-logs-single-values.yaml
```
Install victoria-logs-single
```bash
touch  vls-values.yaml
helm upgrade --install vls vm/victoria-logs-single -f vls-values.yaml
#Verify
kubectl get pod -l app.kubernetes.io/instance=vls,app.kubernetes.io/name=victoria-logs-single

```
Check the UI 
```
nohup kubectl port-forward vls-victoria-logs-single-server-0 9428 --address 0.0.0.0 &
```
![image](https://github.com/user-attachments/assets/9a97d544-cf56-472f-bc7c-3d8c571557c6)

# Deployed Promtail for log forwarding.
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm search repo grafana/promtail  -l
helm show values grafana/promtail > promtail-values.yaml
```
Prepare the value file 
```bash
cat<<EOF >gpt-values.yaml
config:
  clients:
    - url: "http://vls-victoria-logs-single-server.default.svc.cluster.local:9428/insert/loki/api/v1/push"
EOF
helm upgrade --install gpt grafana/promtail -f gpt-values.yaml

#Verify 
kubectl get pod -l app.kubernetes.io/instance=gpt,app.kubernetes.io/name=promtail
nohup kubectl --namespace default port-forward daemonset/gpt-promtail 3101 --address 0.0.0.0 &
curl http://127.0.0.1:3101/metrics
```
#  Exposed the Web UI for quick log exploration aka VMUI
Access the ui : https://localhost:9428/select/vmui
![image](https://github.com/user-attachments/assets/25674ad3-786a-4d2c-bc9a-28341b2d718e)

# Integrated Grafana to visualize logs with dashboards.
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm search repo grafana/grafana  -l
helm show values grafana/grafana > grafana-values.yaml

cat<<EOF >gg-values.yaml
env:
  GF_INSTALL_PLUGINS: "victoriametrics-logs-datasource"
EOF
# serve_from_sub_path=true

helm upgrade --install gg grafana/grafana -f gg-values.yaml

kubectl get secret --namespace default gg-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=gg" -o jsonpath="{.items[0].metadata.name}")
nohup kubectl --namespace default port-forward svc/gg-grafana 3000:80 --address 0.0.0.0 &
```
![image](https://github.com/user-attachments/assets/eb81c501-dc6d-469c-9d3f-349d1ac7a718)


