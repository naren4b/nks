Horizontal Pod Autoscaler: a HorizontalPodAutoscaler automatically updates a workload resource (such as a Deployment or StatefulSet), with the aim of automatically scaling the workload to match demand.

Cluster Autoscaler - a component that automatically adjusts the size of a Kubernetes Cluster so that all pods have a place to run and there are no unneeded nodes. Supports several public cloud providers. Version 1.0 (GA) was released with kubernetes 1.8.

Vertical Pod Autoscaler - a set of components that automatically adjust the amount of CPU and memory requested by pods running in the Kubernetes Cluster. Current state - beta.

reference: https://github.com/kubernetes/autoscaler/tree/master
