# Setting up Thanos for long term storage of prometheus metrics 

![thanos](https://github.com/naren4b/nks/assets/3488520/b0b78241-2e7c-4558-9c74-9a5a9b92b0ad)

# Generate 1 yr of test data 
```bash
mkdir -p /root/prom-eu1 && docker run -i quay.io/thanos/thanosbench:v0.2.0-rc.1 block plan -p continuous-365d-tiny --labels 'cluster="eu1"' --max-time=6h | docker run -v /root/prom-eu1:/prom-eu1 -i quay.io/thanos/thanosbench:v0.2.0-rc.1 block gen --output.dir prom-eu1
ls -lR /root/prom-eu1
```

# Setup Prometheus
```
cat<<EOF>prometheus0_eu1.yml
global:
  scrape_interval: 5s
  external_labels:
    cluster: eu1
    replica: 0
    tenant: team-eu # Not needed, but a good practice if you want to grow this to multi-tenant system some day.

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['127.0.0.1:9090']
  - job_name: 'sidecar'
    static_configs:
      - targets: ['127.0.0.1:19090']
  - job_name: 'minio'
    metrics_path: /minio/prometheus/metrics
    static_configs:
      - targets: ['127.0.0.1:9000']
  - job_name: 'querier'
    static_configs:
      - targets: ['127.0.0.1:9091']
  - job_name: 'store_gateway'
    static_configs:
      - targets: ['127.0.0.1:19091']
EOF

docker run -d --net=host --rm \
    -v $(pwd)/prometheus0_eu1.yml:/etc/prometheus/prometheus.yml \
    -v $(pwd)/prom-eu1:/prometheus \
    -u root \
    --name prometheus-0-eu1 \
    quay.io/prometheus/prometheus:v2.38.0 \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.retention.time=1000d \
    --storage.tsdb.path=/prometheus \
    --storage.tsdb.max-block-duration=2h \
    --storage.tsdb.min-block-duration=2h \
    --web.listen-address=:9090 \
    --web.external-url=https://63c2acb8-8951-4fc9-aae9-0ec136d51ca7-10-244-5-136-9090.papa.r.killercoda.com \
    --web.enable-lifecycle \
    --web.enable-admin-api
```
# Add a Side car which will expose the prometheus metrics at both http and grpc port 
```bash
docker run -d --net=host --rm \
    --name prometheus-0-eu1-sidecar \
    -u root \
    quay.io/thanos/thanos:v0.28.0 \
    sidecar \
    --http-address 0.0.0.0:19090 \
    --grpc-address 0.0.0.0:19190 \
    --prometheus.url http://172.17.0.1:9090
```
# Then host a querier which will pull data from Thanos-side car and expose it further 
```
docker run -d --net=host --rm \
    --name querier \
    quay.io/thanos/thanos:v0.28.0 \
    query \
    --http-address 0.0.0.0:9091 \
    --query.replica-label replica \
    --store 172.17.0.1:19190
```
# Run Grafana to see the metrics 
```
docker run -d --net=host --name grafana grafana/grafana
# Create data source http://localhost:9091 , type prometheus 
```
# Run local S3 minio
```bash

mkdir /root/minio && \
docker run -d --rm --name minio \
     -v /root/minio:/data \
     -p 9000:9000 -e "MINIO_ACCESS_KEY=minio" -e "MINIO_SECRET_KEY=melovethanos" \
     minio/minio:RELEASE.2019-01-31T00-31-19Z \
     server /data

mkdir /root/minio/thanos # the new bucket 
```
# Create the S3 configuration 
```bash
cat<<EOF > bucket_storage.yaml
type: S3
config:
  bucket: "thanos"
  endpoint: "172.17.0.1:9000"
  insecure: true
  signature_version2: true
  access_key: "minio"
  secret_key: "melovethanos"

EOF
```
# Configure the side car to push the 2hr chunk to S3-minio
```bash
docker stop prometheus-0-eu1-sidecar
docker run -d --net=host --rm \
    -v $(pwd)/bucket_storage.yaml:/etc/thanos/minio-bucket.yaml \
    -v $(pwd)/prom-eu1:/prometheus \
    --name prometheus-0-eu1-sidecar \
    -u root \
    quay.io/thanos/thanos:v0.28.0 \
    sidecar \
    --tsdb.path /prometheus \
    --objstore.config-file /etc/thanos/minio-bucket.yaml \
    --shipper.upload-compacted \
    --http-address 0.0.0.0:19090 \
    --grpc-address 0.0.0.0:19190 \
    --prometheus.url http://172.17.0.1:9090
```

# Run Store Gateway to pull from S3 and expose to querier
```bash
docker run -d --net=host --rm \
    -v /root/editor/bucket_storage.yaml:/etc/thanos/minio-bucket.yaml \
    --name store-gateway \
    quay.io/thanos/thanos:v0.28.0 \
    store \
    --objstore.config-file /etc/thanos/minio-bucket.yaml \
    --http-address 0.0.0.0:19091 \
    --grpc-address 0.0.0.0:19191
```
# ReConfigure the querier to pull from both side-car and Store and expose 
```bash 
docker stop querier && \
docker run -d --net=host --rm \
   --name querier \
   quay.io/thanos/thanos:v0.28.0 \
   query \
   --http-address 0.0.0.0:9091 \
   --query.replica-label replica \
   --store 172.17.0.1:19190 \
   --store 172.17.0.1:19191
 ```
 
# Run Compactor to reduce the metric size by deleting redundant or dupicate metrics  
```bash
docker run -d --net=host --rm \
 -v /root/bucket_storage.yaml:/etc/thanos/minio-bucket.yaml \
    --name thanos-compact \
    quay.io/thanos/thanos:v0.28.0 \
    compact \
    --wait --wait-interval 30s \
    --consistency-delay 0s \
    --objstore.config-file /etc/thanos/minio-bucket.yaml \
    --http-address 0.0.0.0:19095
```

- [Demo Environment](https://killercoda.com/killer-shell-cks/scenario/container-namespaces-docker)



