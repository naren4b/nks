![vls-gpt](https://github.com/user-attachments/assets/81916d6a-e1d8-4c2d-aa75-9d321b7fcba5)

# Install VictoriaLogs
```bash
helm repo add vm https://victoriametrics.github.io/helm-charts/
helm repo update

helm search repo vm/victoria-logs-single -l
helm show values vm/victoria-logs-single > victoria-logs-single-values.yaml

helm upgrade --install vls vm/victoria-logs-single -f vls-values.yaml

nohup kubectl port-forward vls-victoria-logs-single-server-0 9428 --address 0.0.0.0 &
```
# Install Promtail
```
cat<<EOF >gpt-values.yaml
config:
  clients:
    - url: "http://localhost:9428/insert/loki/api/v1/push"
EOF

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm search repo grafana/promtail  -l
helm show values grafana/promtail > promtail-values.yaml
helm upgrade --install gpt grafana/promtail -f gpt-values.yaml
```


Install Grafana 

