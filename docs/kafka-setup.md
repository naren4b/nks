# Deploying Basic Kafka cluster with the help of Strimzi operators (1/n)
![my-kafka-basic](https://github.com/naren4b/nks/assets/3488520/fa8a559d-b85e-4ce4-947e-133ccd1c7dda)

# Apache ZooKeeper
Apache ZooKeeper is a core dependency for Kafka as it provides a cluster coordination service, storing and tracking the status of brokers and consumers. ZooKeeper is also used for controller election.

# Kafka Connect
Kafka Connect is an integration toolkit for streaming data between Kafka brokers and other systems using Connector plugins. Kafka Connect provides a framework for integrating Kafka with an external data source or target, such as a database, for import or export of data using connectors. Connectors are plugins that provide the connection configuration needed.
  1. A source connector pushes external data into Kafka.
  2. A sink connector extracts data out of Kafka
  3. External data is translated and transformed into the appropriate format.
# Kafka MirrorMaker
Kafka MirrorMaker replicates data between two Kafka clusters, within or across data centers.
MirrorMaker takes messages from a source Kafka cluster and writes them to a target Kafka cluster.

# Kafka Bridge
Kafka Bridge provides an API for integrating HTTP-based clients with a Kafka cluster.

# Kafka Exporter
Kafka Exporter extracts data for analysis as Prometheus metrics, primarily data relating to offsets, consumer groups, consumer lag and topics. Consumer lag is the delay between the last message written to a partition and the message currently being picked up from that partition by a consumer


# prerequisite
- Killercoda play ground : https://killercoda.com/killer-shell-ckad/scenario/playground
or 
- Kind cluster : https://kind.sigs.k8s.io/docs/user/quick-start/#creating-a-cluster

```bash
# Validate docker installation
docker ps
docker version

# Validate kind
kind version

# Validate kubectl
kubectl version
```
# Install kafka 

# create namespace
```bash
kubectl create namespace kafka
```
# kafka Operaor ClusterRoles, ClusterRoleBindings CRD
```bash
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl get pod -n kafka -w
kubectl logs deployment/strimzi-cluster-operator -n kafka -f
```
# Install Single node kafka cluster 
```bash
kubectl apply -f https://strimzi.io/examples/latest/kafka/kafka-persistent-single.yaml -n kafka 
kubectl get pod -n kafka 
kubectl get pod -n kafka -w
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka 
```

# Send Messages 
```bash
kubectl -n kafka run kafka-producer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic my-topic
```
# Receive Messages
```
kubectl -n kafka run kafka-consumer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic my-topic --from-beginning
```

# Clean up 
```bash
kubectl -n kafka delete $(kubectl get strimzi -o name -n kafka)
kubectl -n kafka delete -f 'https://strimzi.io/install/latest?namespace=kafka'
```
ref: 
- https://strimzi.io/docs/operators/latest/overview
- https://strimzi.io/quickstarts/
