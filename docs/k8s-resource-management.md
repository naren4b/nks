# Kubernetes Resource Management 
 ![image](https://github.com/naren4b/nks/assets/3488520/569a3368-f664-49d3-a5d1-02c72086a5e7)

## Resource Management for Pods and Containers

### Request:
  When you specify the resource request for containers in a Pod, the kube-scheduler uses this information to decide which node to place the Pod on
### Limit:
  When you specify a resource limit for a container, the kubelet enforces those limits so that the running container is not allowed to use more of that resource than the limit you set.
  
<img src="https://github.com/naren4b/nks/assets/3488520/32523112-a55c-4abe-b280-afa2c7eb579f" alt="drawing" width="300"/>

### Notes:
If the node where a Pod is running has enough resources available, it is possible(and allowed) for a container to use more resource than it has request for. However, a container is not allowed to use more than its resource limit.

### CPU: 
- Limits and requests for CPU resources are measured in cpu units. In Kubernetes, 1 CPU unit is equivalent to 1 physical CPU core, or 1 virtual core, depending on whether the node is a physical host or a virtual machine running inside a physical machine.
- If CPU limit reached, then it will be **throttled** 
- Defined at container level 
### Memory: 
- Limits and requests for memory are measured in bytes. You can express memory as a plain integer or as a fixed-point number using one of these quantity suffixes: E, P, T, G, M, k. You can also use the power-of-two equivalents: Ei, Pi, Ti, Gi, Mi, Ki. For example, the following represent roughly the same value. 
- If memory limit reached, then it will be **OOMKilled & restarted** 
- Defined at container level 

## Kubernetes checks the request(unallocated<ask) while scheduling
![image](https://github.com/naren4b/nks/assets/3488520/569a3368-f664-49d3-a5d1-02c72086a5e7)

## Over committed state 
Limit for a pod can be set to any value(6Gi+6Gi) , but should not sum of total increase to node resource(8Gi)
If actual consumption increases( 3+6=9Gi) which is more than node limit (8Gi) One of the pod /container will be killed 
This is an Over committed state 

![image](https://github.com/naren4b/nks/assets/3488520/56db6246-084a-4026-af49-a17de3df2670)

## Quality of Service(QoS)

### Guaranteed : 
When both request and limit are defined and are equal 
Pods that are Guaranteed have the strictest resource limits and are least likely to face eviction. They are guaranteed not to be killed until they exceed their limits or there are no lower-priority Pods that can be preempted from the Node. They may not acquire resources beyond their specified limits. These Pods can also make use of exclusive CPUs using the static CPU management policy.

### Burstable  : 
When both request and limit are defined and are NOT equal 
Pods that are Burstable have some lower-bound resource guarantees based on the request, but do not require a specific limit. If a limit is not specified, it defaults to a limit equivalent to the capacity of the Node, which allows the Pods to flexibly increase their resources if resources are available. In the event of Pod eviction due to Node resource pressure, these Pods are evicted only after all BestEffort Pods are evicted. Because a Burstable Pod can include a Container that has no resource limits or requests, a Pod that is Burstable can try to use any amount of node resources

### BestEffort: 
When both request and limit are NOT  defined 
Pods in the BestEffort QoS class can use node resources that aren't specifically assigned to Pods in other QoS classes
The kubelet prefers to evict BestEffort Pods if the node comes under resource pressure

## Limit Range
A LimitRange is a policy to constrain the resource allocations (limits and requests) that you can specify for each applicable object kind (such as Pod or PersistentVolumeClaim) in a namespace.

A LimitRange provides constraints that can:
Enforce minimum and maximum compute resources usage per Pod or Container in a namespace.
Enforce minimum and maximum storage request per PersistentVolumeClaim in a namespace.
Enforce a ratio between request and limit for a resource in a namespace.
Set default request/limit for compute resources in a namespace and automatically inject them to Containers at runtime.

A LimitRange is enforced in a particular namespace when there is a LimitRange object in that namespace.

## ResourceQuota
When several users or teams share a cluster with a fixed number of nodes, there is a concern that one team could use more than its fair share of resources.
Resource quotas are a tool for administrators to address this concern.
A resource quota, defined by a ResourceQuota object, provides constraints that limit aggregate resource consumption per namespace. It can limit the quantity of objects that can be created in a namespace by type, as well as the total amount of compute resources that may be consumed by resources in that namespace.

**Resource quotas work like this:**

Different teams work in different namespaces. This can be enforced with RBAC.
The administrator creates one ResourceQuota for each namespace.
Users create resources (pods, services, etc.) in the namespace, and the quota system tracks usage to ensure it does not exceed hard resource limits defined in a ResourceQuota.
If creating or updating a resource violates a quota constraint, the request will fail with HTTP status code 403 FORBIDDEN with a message explaining the constraint that would have been violated.
If quota is enabled in a namespace for compute resources like cpu and memory, users must specify requests or limits for those values; otherwise, the quota system may reject pod creation. 

***💥Hint: Use the LimitRanger admission controller to force defaults for pods that make no compute resource requirements.***


_references:_
 - https://kubernetes.io/docs/concepts/policy/resource-quotas/
 - https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/
 - https://kubernetes.io/docs/concepts/policy/limit-range/
 - https://www.youtube.com/watch?v=MbgFIQoVh6w
