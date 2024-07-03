# Interacting with Strimzi Kafka cluster through Kafka Bridge(2/n)
![image](https://github.com/naren4b/nks/assets/3488520/fa8a559d-b85e-4ce4-947e-133ccd1c7dda)
![image](https://github.com/naren4b/nks/assets/3488520/00bde3f5-d946-41fb-abf8-8f9d8f91fdfd)


Continuing from : (Deploying Basic Kafka cluster with the help of Strimzi operators (1/n))[https://naren4b.github.io/nks/docs/kafka-setup.html ]

### Deploy a Kafka Topic (topic name: my-topic)
```bash
kubectl apply -n kafka -f https://raw.githubusercontent.com/strimzi/strimzi-kafka-operator/main/examples/topic/kafka-topic.yaml
```

### Deploy a Kafka Bridge
```bash
kubectl apply -n kafka -f https://raw.githubusercontent.com/strimzi/strimzi-kafka-operator/main/examples/bridge/kafka-bridge.yaml
```
### Deploy an Ingress 
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kafka-ingress-bridge
  namespace: kafka
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - host: kafka-bridge.local.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-bridge-bridge-service
                port:
                  number: 8080
```
### Deploy a consumer 
Notes: Run inside the cluster for the 'my-topic' Check the send messages are received 
```bash
kubectl -n kafka run kafka-consumer -n kafka -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 \
                                                     --rm=true --restart=Never -- bin/kafka-console-consumer.sh \
                                                     --bootstrap-server my-cluster-kafka-bootstrap:9092 \
                                                     --topic my-topic --from-beginning

```
# Verifying the setup
Notes: Check the ingress(kafka-bridge.local.com) is accessiable 
let's post messages to our topic : 'my-topic'

```bash
 curl -X POST   http://kafka-bridge.local.com/topics/my-topic   -H 'content-type: application/vnd.kafka.json.v2+json'   -d '{
    "records": [
        {
            "key": "naren4b-key",
            "value": "hello from naren4b 0001"
        }
    ]
}'
```

![image](https://github.com/naren4b/nks/assets/3488520/b6b2fe5c-2886-4ae6-b849-c14d7ae0ec19)
![image](https://github.com/naren4b/nks/assets/3488520/0ac979cc-8640-4fe1-9649-1fa708c7e923)

ref: https://strimzi.io/docs/bridge/latest/#proc-producing-messages-from-bridge-topics-partitions-bridge

