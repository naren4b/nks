![vls-gpt (1)](https://github.com/user-attachments/assets/e4bd4f45-c4fa-4fb7-9d0f-99c866c813bc)

# Install VictoriaLogs
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

# Install Promtail
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
# Check the logs in VMUI
Access the ui : https://localhost:9428/select/vmui
![image](https://github.com/user-attachments/assets/25674ad3-786a-4d2c-bc9a-28341b2d718e)

# Install Grafana 
```
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


