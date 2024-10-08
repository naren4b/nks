# Enhancing Kubernetes Monitoring & Automation with Robusta!

Find a comprehensive setup for Kubernetes monitoring, notifications, troubleshooting, and automation using Robusta. This powerful tool integrates seamlessly with Prometheus, enabling real-time monitoring and instant alerts via Slack and Robusta UI.

#### Key Highlights:

- Deployed a Kubernetes cluster and Prometheus stack.
- Integrated Slack for instant alert notifications in the #devops channel.
- Set up Robusta for advanced monitoring and automated issue resolution.
- Monitoring has never been easier or more effective. Excited to see how this enhances our DevOps processes! 💻🔧

![robusta-monitoring](https://github.com/user-attachments/assets/1c7bd4dc-fa2f-47a7-a80f-8f766030e25b)

#### Prerequisites:

1. Workspace must have `Docker, Helm, Kubectl` installed
2. Kubernetes Cluster
3. A Prometheus installation
4. [Set up a Sink](https://docs.robusta.dev/master/configuration/sinks/index.html)
   - Create a sink account. I have chosen the slack [My Slack](https://narenorg.slack.com) and created a channel `#devops`. [more on #Slack-Sink](https://docs.robusta.dev/master/configuration/sinks/slack.html)
   - Create a Free Registration at Robust and create an app in it My Account: [My Robusta-UI](https://platform.robusta.dev/naren4biz/settings#account) . [more on #robusta-ui](https://docs.robusta.dev/master/configuration/sinks/RobustaUI.html)

#### Installation:

#### Let's Create a KIND Kubernetes Cluster

```
 kind create cluster --name=robusta-demo
```

#### Setup of Prometheus stack

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update

cat<<EOF >robusta-demo-values.yaml
prometheus: # collect rules from all namespaces and ignore label filters
    ruleNamespaceSelector: {}
    ruleSelector: {}
    ruleSelectorNilUsesHelmValues: false
defaultRules: # those rules are now managed by Robusta
    rules:
      alertmanager: false
      etcd: false
      configReloaders: false
      general: false
      kubeApiserverSlos: false
      kubeControllerManager: false
      kubeProxy: false
      kubernetesApps: false
      kubernetesResources: false
      kubernetesStorage: false
      kubernetesSystem: false
      kubeSchedulerAlerting: false
      kubeStateMetrics: false
      network: false
      nodeExporterAlerting: false
      prometheus: false
      prometheusOperator: false
EOF

helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -f robusta-demo-values.yaml --namespace monitoring --create-namespace

```

[more](https://naren4b.github.io/nks/docs/prometheus_pushgateway.html#installing-prometheus--prometheus-operator)

#### Setup the Sink

```
Generate the Slack Channel
Name: devops
Email address: XXX.YYYY@gmail.com
Account: naren4biz
```

```bash hl_lines="2 3"
curl -fsSL -o robusta https://docs.robusta.dev/master/_static/robusta
chmod +x robusta
./robusta gen-config --no-enable-prometheus-stack --cluster-name=robusta-demo --slack-channel=devops
```

![image](https://github.com/user-attachments/assets/1181a823-69ca-4332-b6f7-2812e93f28b1)

# Install robusta forwarder & Runner

```
helm repo add robusta https://robusta-charts.storage.googleapis.com && helm repo update
helm upgrade --install robusta robusta/robusta -f ./generated_values.yaml --set clusterName=robusta-demo --set isSmallCluster=true --set enabledManagedConfiguration=true
```

# Let's Deploy a crashpod

```
kubectl apply -f https://gist.githubusercontent.com/robusta-lab/283609047306dc1f05cf59806ade30b6/raw
```

### Check the Channel

My Slack: [My Slack](https://narenorg.slack.com/archives/CP2PBCJ9J/p1723299440028189)
![image](https://github.com/user-attachments/assets/a88d5fa7-21b5-4d33-a615-9033af64fe68)

### Check the Robusta UI

My Account: [Robusta-UI](https://platform.robusta.dev/naren4biz/apps?isGrouped=false&statusSort=%22asc%22&page=1)
![robusta-monitoring-failedpod](https://github.com/user-attachments/assets/e0671ed3-ec76-4712-be50-241b848c81c1)
