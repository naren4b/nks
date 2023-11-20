# Setting up Monitoring Stack in a Node (docker container)
![misc-Monitoring-Stack](https://github.com/naren4b/nks/assets/3488520/01d43a95-6e67-4da4-8ba5-ce84a3a7aa34)


### AlertManager Setup | run-alertmanager.sh

```bash
#! /bin/bash

name=$1
default_value="demo"
name=${name:-$default_value}
mkdir -p alertmanager
cat <<EOF >${PWD}/alertmanager/alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'web.hook'
receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

alertmanager_name=${name}-alertmanager
alertmanager_host_port=9093
mkdir -p ${alertmanager_name}

docker rm ${alertmanager_name} -f
docker run -d --restart unless-stopped --network host \
    -v ${PWD}/alertmanager:/etc/alertmanager \
    --name=${alertmanager_name} \
    prom/alertmanager

docker ps -l

```

###  Grafana setup

```bash
#! /bin/bash

name=$1
default_value="demo"
name=${name:-$default_value}

#scanner-grafana
grafana_name=${name}-grafana
grafana_host_port=3000
docker rm ${grafana_name} -f
docker run -d --restart unless-stopped --network host \
    --name=${grafana_name} \
    -v ${PWD}/${grafana_name}/plugins:/var/grafana/plugins \
    -v ${PWD}/${grafana_name}/provisioning:/etc/grafana/provisioning \
    grafana/grafana

docker ps -l


```

###  node-exporter setup | run-node-exporter.sh

```bash
#! /bin/bash

cat <<EOF >/etc/cron.d/directory_size
*/5 * * * * root du -sb /var/log /var/cache/apt /var/lib/prometheus | sed -ne 's/^\([0-9]\+\)\t\(.*\)$/node_directory_size_bytes{directory="\2"} \1/p' > /var/lib/node_exporter/textfile_collector/directory_size.prom.$$ && mv /var/lib/node_exporter/textfile_collector/directory_size.prom.$$ /var/lib/node_exporter/textfile_collector/directory_size.prom
EOF
name=$1
default_value="demo"
name=${name:-$default_value}
node_exporter_name=${name}-node-exporter
node_exporter_host_port=9100
text_collector_dir=/var/lib/node-exporter/textfile_collector
docker rm ${node_exporter_name} -f
mkdir -p ${text_collector_dir}

docker run -d --restart unless-stopped --network host \
    -v ${text_collector_dir}:${text_collector_dir} \
    --name=${node_exporter_name} \
    prom/node-exporter --collector.textfile.directory=${text_collector_dir}

docker ps -l

```

###  Prometheus setup | run-prometheus.sh

```bash
#! /bin/bash
name=$1
default_value="demo"
name=${name:-$default_value}

mkdir -p prometheus
cat <<EOF >${PWD}/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
scrape_configs:
  - job_name: prometheus
    metrics_path: /metrics
    scheme: http
    static_configs:
      - targets:
          - localhost:9090
  - job_name: node-exporter
    metrics_path: /metrics
    scheme: http
    static_configs:
      - targets:
          - localhost:9100
EOF

prometheus_name=${name}-prometheus
prometheus_host_port=9090
docker volume create prometheus-data
mkdir -p ${prometheus_name}
docker rm ${prometheus_name} -f
docker run -d --restart unless-stopped --network host \
    --name=${prometheus_name} \
    -v ${PWD}/prometheus/:/etc/prometheus/ \
    -v prometheus-data:/prometheus \
    prom/prometheus
docker ps -l

```

###  Install the moitoring stack | install.sh

```bash
#! /bin/bash

name=$1
default_value="demo"
name=${name:-$default_value}

source run-alertmanager.sh $name
source run-prometheus.sh $name
source run-node-exporter.sh $name
source run-grafana.sh $name

docker ps | grep -E "STATUS|$name"


```

###  Uninstall the moitoring stack | uninstall.sh

```
#! /bin/bash
name=$1
default_value="demo"
name=${name:-$default_value}

docker ps | grep $name | awk '{print $1}' | xargs docker rm -f

```

![image](https://github.com/naren4b/nks/assets/3488520/fe1004f0-b547-4108-a2b2-c17e5462b9f2)
