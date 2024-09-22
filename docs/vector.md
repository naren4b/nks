# Take Control of Your Observability Data with  [vector.dev](https://vector.dev/docs/)
![vector drawio](https://github.com/user-attachments/assets/81c8400f-b8fe-4a75-bc1a-6eec86076db6)
[_A lightweight, ultra-fast tool for building observability pipelines_](https://vector.dev/docs/)

Vector is a high-performance, end-to-end (agent & aggregator) observability data pipeline that puts you in control of your observability data.
Collect, transform, and route all your logs and metrics to any vendors you want today and any other vendors you may want tomorrow. 
Vector enables dramatic cost reduction, novel data enrichment, and data security where you need it, not where it is most convenient for your vendors. 
Additionally, it is open source and up to 10x faster than every alternative in the space.

More details: [vector.dev](https://vector.dev/docs/)
![overview-vector drawio](https://github.com/user-attachments/assets/8ef88bcd-5555-4993-a386-23c29a75fb74)

# Example Installation 
![example-vector drawio](https://github.com/user-attachments/assets/8bd06145-77bb-4328-833c-80f8af6200ca)


# Server Setup
**Aggregator `vector.yaml` Configuration File**
```yaml
mkdir -p aggregator
cat <<-EOF > $PWD/aggregator/vector.yaml
data_dir: /vector-data-dir
api:
  enabled: true
  address: 0.0.0.0:8686
sources:
  vector:
     address: 0.0.0.0:6000
     type: vector
     version: "2"
  my_internal_logs:
    type: internal_logs
  my_internal_metrics:
    type: internal_metrics
transforms:
  parse_logs:
    type: "remap"
    inputs: [vector,my_internal_logs,my_internal_metrics]
    source: |
      . = parse_syslog!(string!(.message)) 
sinks:
  stdout:
    type: console
    inputs: [parse_logs]
    encoding:
        codec: json
EOF
```

**Configuration Ref:**
**- api:**
  -   https://vector.dev/docs/reference/api/
**- source:**
  -   https://vector.dev/docs/reference/configuration/sources/vector
  -   https://vector.dev/docs/reference/configuration/sources/internal_metrics/
  -   https://vector.dev/docs/reference/configuration/sources/internal_logs/
    
**- transforms:**
  -   https://vector.dev/docs/reference/configuration/transforms/remap/
    
**- sink:**
  -   https://vector.dev/docs/reference/configuration/sinks/console/

**Depoly the Server (vector aggregator)** 
```bash 
# docker rm -f vector-aggregator 
docker run -d --rm --name vector-aggregator -v $(pwd)/aggregator:/etc/vector/  -p 8686:8686 -p 6000:6000 docker.io/timberio/vector:0.41.1-alpine
```

# Client(s) Setup 
**Vector Agent `vector.yaml` Configuration File**
```yaml
mkdir -p agent
cat <<-EOF > $PWD/agent/vector.yaml
data_dir: /vector-data-dir
api:
  enabled: false
  address: 0.0.0.0:8686
sources:
  dummy_logs:
    type: "demo_logs"
    format: "syslog"
    interval: 1
  my_internal_logs:
    type: internal_logs
  my_internal_metrics:
    type: internal_metrics
transforms:
  parse_logs:
    type: "remap"
    inputs: ["dummy_logs"]
    source: |
      . = parse_syslog!(string!(.message))
sinks:
  vector_sink:
    type: vector
    inputs:
      - dummy_logs
    address: 172.17.0.1:6000  #Change me
  stdout:
    type: console
    inputs: [parse_logs,my_internal_logs,my_internal_metrics]
    encoding:
        codec: json
EOF
```
**Configuration Ref:**

- **source**:
  -   https://vector.dev/docs/reference/configuration/sources/demo_logs/
  -   https://vector.dev/docs/reference/configuration/sources/internal_metrics/
  -   https://vector.dev/docs/reference/configuration/sources/internal_logs/
    
- **transforms**:
  -   https://vector.dev/docs/reference/configuration/transforms/remap/
 
- **sink**:
  -   https://vector.dev/docs/reference/configuration/sinks/vector/

**Depoly the Client (vector agent)** 
```bash
#docker rm -f vector-agent 
docker run -d --name vector-agent -v $(pwd)/agent:/etc/vector/ --rm docker.io/timberio/vector:0.41.1-alpine
```
Now, your Vector Aggregator and Vector Agent are set up and running. They can efficiently collect, transform, and route logs and metrics, offering complete control over your observability data pipeline.
```scss
This `README.md` file provides clear instructions on setting up both the server and client components of the Vector pipeline, including configuration references and deployment commands.
```
