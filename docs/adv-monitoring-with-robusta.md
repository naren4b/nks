# Kubernetes Notifications, Troubleshooting, And Automation With Robusta
![robusta-monitoring](https://github.com/user-attachments/assets/1c7bd4dc-fa2f-47a7-a80f-8f766030e25b)

# Prerequisites:
  1. Workspace must have Docker, Helm, Kubectl  
  2. Kubernetes Cluster 
  3. A Prometheus installation
  4. [Set up a Sink](https://docs.robusta.dev/master/configuration/sinks/index.html)
     - [#slack](https://docs.robusta.dev/master/configuration/sinks/slack.html) : https://app.slack.com/client/T07FJ4APNMA/C07F13BA7DM
     - [#msteam](https://docs.robusta.dev/master/configuration/sinks/ms-teams.html)
     - [#robusta-ui](https://docs.robusta.dev/master/configuration/sinks/RobustaUI.html)
     
# Installation:
#### Kubernetes Cluster
```
 kind create cluster --name=demo
```
# Settup of Prometheus stack
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update 
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace     

```
[more](https://naren4b.github.io/nks/docs/prometheus_pushgateway.html#installing-prometheus--prometheus-operator)

# Setup the Sink Generate the 
``` 
curl -fsSL -o robusta https://docs.robusta.dev/master/_static/robusta
chmod +x robusta
./robusta gen-config --no-enable-prometheus-stack
```
![image](https://github.com/user-attachments/assets/e67d5c00-8749-4c03-a849-e5b0fe84161a)


# Install robusta forwarder & Runner  
```
helm repo add robusta https://robusta-charts.storage.googleapis.com && helm repo update
helm upgrade --install robusta robusta/robusta -f ./generated_values.yaml --set clusterName=demo --set isSmallCluster=true
```
# Let's Test it 
```
kubectl apply -f https://gist.githubusercontent.com/robusta-lab/283609047306dc1f05cf59806ade30b6/raw
```
### Check the Channel 
![image](https://github.com/user-attachments/assets/06ceb6eb-a22e-4346-a61f-96e921e03d70)
### Check the Robusta UI
![image](https://github.com/user-attachments/assets/ab559e7d-c7bc-44ee-a9a2-0ba8bfd75e15)

  
