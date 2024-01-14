helm repo add vm https://victoriametrics.github.io/helm-charts/
helm repo update
helm show values vm/victoria-metrics-cluster > values.yaml
helm install vmcluster vm/victoria-metrics-cluster -f values.yaml 























# Certificate Configuration

```bash
CA_NAME="NKS Certificate Authority"
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=${CA_NAME}" -days 10000 -out ca.crt

```

```bash
mkdir vms
cd vms


CERT_NAME="victoria-metrics-server"
NODE_IP=127.0.0.1
DOMAIN=nks.in


cat<< EOF >victoria-metrics-server-csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = IN
ST = Karnataka
L = Bangalore
O = victoria-metrics
OU = nks
CN = $CERT_NAME

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.$NODE_IP.nip.io
DNS.2 = $DOMAIN
DNS.3 = *.$DOMAIN
IP.1 = $NODE_IP


[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment,digitalSignature,nonRepudiation
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF


openssl genrsa -out victoria-metrics-server-tls.key 2048
openssl req -new -key victoria-metrics-server-tls.key -out victoria-metrics-server-tls.csr -config victoria-metrics-server-csr.conf
openssl x509 -req -in victoria-metrics-server-tls.csr -CA ../ca.crt -CAkey ../ca.key -CAcreateserial -out victoria-metrics-server-tls.crt -days 10000     -extensions v3_ext -extfile victoria-metrics-server-csr.conf -sha256

cd ..
cp ca.crt vms

```

# Victoria Metric Agent(Client) Configuration

```bash
mkdir vma
cd vma
CERT_NAME="vmagent-client"
NODE_IP=127.0.0.1
DOMAIN=nks.in


cat<< EOF >vmagent-client-csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = IN
ST = Karnataka
L = Bangalore
O = victoria-metrics
OU = nks
CN = $CERT_NAME

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.$NODE_IP.nip.io
DNS.2 = $DOMAIN
DNS.3 = *.$DOMAIN
IP.1 = $NODE_IP


[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment,digitalSignature,nonRepudiation
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF


openssl genrsa -out vmagent-client-tls.key 2048
openssl req -new -key vmagent-client-tls.key -out vmagent-client-tls.csr -config vmagent-client-csr.conf
openssl x509 -req -in vmagent-client-tls.csr -CA ../ca.crt -CAkey ../ca.key -CAcreateserial -out vmagent-client-tls.crt -days 10000     -extensions v3_ext -extfile vmagent-client-csr.conf -sha256
cd ..
cp ca.crt vma

```

### Install vmagent | run-vmagent.sh

VM Agent which will scrape selected time series from local Prometheus server, where `service="naren"`

```bash
#! /bin/bash
name=$1
default_value="demo"
name=${name:-$default_value}
vmagent_name=${name}-vmagent
mkdir -p ${PWD}/$vmagent_name

remoteWrite_url="http://localhost:8428/api/v1/write"


docker build -t victoriametrics/vmagent:$vmagent_name ${PWD}/$vmagent_name/
rm -rf ${PWD}/$vmagent_name/Dockerfile

cat <<EOF > ${PWD}/$vmagent_name/relabel.yml
- target_label: "node"
  replacement: "local"
EOF

cat <<EOF >${PWD}/$vmagent_name/prometheus.yml
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s

    honor_labels: true
    metrics_path: '/federate'

    params:
      'match[]':
        - '{service="naren"}'
        - '{__name__=~"up|vm_.*"}'
    static_configs:
      - targets:
          - localhost:9090
EOF

docker volume create vmagentdata
docker rm ${vmagent_name} -f

docker run -d --restart unless-stopped --network host \
  --name=${vmagent_name} \
  -v ${PWD}/$vmagent_name:/etc/prometheus/ \
  -v ${PWD}/vma:/opt/ \
  -v vmagentdata:/vmagentdata \
  victoriametrics/vmagent -remoteWrite.url=$remoteWrite_url -remoteWrite.urlRelabelConfig=/etc/prometheus/relabel.yml -remoteWrite.forceVMProto -promscrape.config=/etc/prometheus/prometheus.yml -remoteWrite.tlsCAFile=/opt/ca.crt -remoteWrite.tlsCertFile=/opt/vmagent-client-tls.crt -remoteWrite.tlsKeyFile=/opt/vmagent-client-tls.key -remoteWrite.tlsInsecureSkipVerify=false

docker ps -l

```

# Victoria Metric Server Configuration

```bash
name=$1
default_value="demo"
name=${name:-$default_value}
docker volume create victoria-metrics-data
# victoria-metrics
victoria_metrics_name=${name}-victoria-metrics
victoria_metrics_host_port=8428
docker rm ${victoria_metrics_name} -f
docker run -d --restart unless-stopped --network host \
    --name=${victoria_metrics_name} \
    -v victoria-metrics-data:/victoria-metrics-data \
    -v ${PWD}/vms:/opt/ \
    victoriametrics/victoria-metrics -tls=true -tlsKeyFile=/opt/victoria-metrics-server-tls.key -tlsCertFile=/opt/victoria-metrics-server-tls.crt

docker ps -l

```

cat <<EOF >${PWD}/$vmagent_name/Dockerfile
FROM victoriametrics/vmagent
ENTRYPOINT ["/vmagent-prod"]
CMD ["-remoteWrite.url=$remoteWrite_url" ,"-remoteWrite.urlRelabelConfig=/etc/prometheus/relabel.yml", "-remoteWrite.forceVMProto","-promscrape.config=/etc/prometheus/prometheus.yml","-remoteWrite.tlsCAFile=/opt/ca.crt","-remoteWrite.tlsCertFile=/opt/vmagent-client-tls.crt","-remoteWrite.tlsKeyFile=/opt/vmagent-client-tls.key","-remoteWrite.tlsInsecureSkipVerify=false"]
EOF

-tls
Whether to enable TLS for incoming HTTP requests at -httpListenAddr (aka https). -tlsCertFile and -tlsKeyFile must be set if -tls is set
-tlsCertFile string
Path to file with TLS certificate if -tls is set. Prefer ECDSA certs instead of RSA certs as RSA certs are slower. The provided certificate file is automatically re-read every second, so it can be dynamically updated
-tlsCipherSuites array
Optional list of TLS cipher suites for incoming requests over HTTPS if -tls is set. See the list of supported cipher suites at https://pkg.go.dev/crypto/tls#pkg-constants
Supports an array of values separated by comma or specified via multiple flags.
-tlsKeyFile string

```yaml
  -remoteWrite.flushInterval duration
     Interval for flushing the data to remote storage. This option takes effect only when less than 10K data points per second are pushed to -remoteWrite.url (default 1s)

  -remoteWrite.maxBlockSize size
     The maximum block size to send to remote storage. Bigger blocks may improve performance at the cost of the increased memory usage. See also -remoteWrite.maxRowsPerBlock
     Supports the following optional suffixes for size values: KB, MB, GB, TB, KiB, MiB, GiB, TiB (default 8388608)

  -remoteWrite.queues int
     The number of concurrent queues to each -remoteWrite.url. Set more queues if default number of queues isn't enough for sending high volume of collected data to remote storage. Default      value is 2 * numberOfAvailableCPUs (default 32)

  -remoteWrite.rateLimit array
     Optional rate limit in bytes per second for data sent to the corresponding -remoteWrite.url. By default, the rate limit is disabled. It can be useful for limiting load on remote      storage when big amounts of buffered data is sent after temporary unavailability of the remote storage (default 0)
     Supports array of values separated by comma or specified via multiple flags.

  -remoteWrite.sendTimeout array
     Timeout for sending a single block of data to the corresponding -remoteWrite.url (default 1m0s)
     Supports array of values separated by comma or specified via multiple flags.

  -remoteWrite.tlsCAFile array
     Optional path to TLS CA file to use for verifying connections to the corresponding -remoteWrite.url. By default, system CA is used
     Supports an array of values separated by comma or specified via multiple flags.
  -remoteWrite.tlsCertFile array
     Optional path to client-side TLS certificate file to use when connecting to the corresponding -remoteWrite.url
     Supports an array of values separated by comma or specified via multiple flags.
  -remoteWrite.tlsInsecureSkipVerify array
     Whether to skip tls verification when connecting to the corresponding -remoteWrite.url
     Supports array of values separated by comma or specified via multiple flags.
  -remoteWrite.tlsKeyFile array
     Optional path to client-side TLS certificate key to use when connecting to the corresponding -remoteWrite.url
     Supports an array of values separated by comma or specified via multiple flags.
  -remoteWrite.vmProtoCompressLevel int
     The compression level for VictoriaMetrics remote write protocol. Higher values reduce network traffic at the cost of higher CPU usage. Negative values reduce CPU usage at the cost of increased network traffic. See https://docs.victoriametrics.com/vmagent.html#victoriametrics-remote-write-protocol
```
