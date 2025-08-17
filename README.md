# Simpei Todo Application

A full-stack todo application with Vue.js frontend, FastAPI backend and SQLite as database, designed for learning and easy understanding of deployment using **Kubernetes** with or without **Helm** and also using Docker Compose.

Before you start learning Kuberenetes, I assume you are familiar with Docker. This README is intensive but only explain much! In order to learn Kubernetes properly, checkout [Techworld with Nana](https://www.youtube.com/@TechWorldwithNana) or Linkedin Learning [courses](https://www.linkedin.com/learning/search?keywords=kubernetes&promptType=LEARNER_TYPED).

 I used `Claude Sonnet 4.0` and [Kiro](https://kiro.dev) to generate both UI and API projects as I wanted to focus on Kubernetes part of this project. Once, both projects were generated I did Kubernetes part myself. You can find README files in both projects, however they were generated with `Claude` too!

## Table of Contents

- [Architecture](#architecture)
- [Deployment Options](#deployment-options)
- [Prerequisites](#prerequisites)
  - [For Docker setup](#for-docker-setup)
  - [For Kubernetes (Kind)](#for-kubernetes-kind)
  - [For Helm Deployment](#for-helm-deployment)
- [Deployment steps](#deployment-steps)
  - [Using Docker Compose](#using-docker-compose)
- [Kubernetes Configuration Overview](#kubernetes-configuration-overview)
  - [1. Kind Cluster Configuration (`cluster.yaml`)](#1-kind-cluster-configuration-clusteryaml)
  - [2. Backend Deployment & Service (`server.yaml`)](#2-backend-deployment--service-serveryaml)
  - [3. Frontend Deployment & Service (`ui.yaml`)](#3-frontend-deployment--service-uiyaml)
  - [4. Persistent Storage (`pvc.yaml`)](#4-persistent-storage-pvcyaml)
  - [5. Ingress Controller (`ingress.yaml`)](#5-ingress-controller-ingressyaml)
- [Kubernetes delopyment with Kind (Local)](#kubernetes-delopyment-with-kind-local)
- [Helm Chart deployment](#helm-chart-deployment)
- [Local Development Setup](#local-development-setup)
  - [Frontend Development (`simpei-ui/`)](#frontend-development-simpei-ui)
  - [Backend Development (`simpei/src/simpei/`)](#backend-development-simpeisrcsimpei)

## Architecture

- **Frontend**: Vue.js application (`simpei-ui/`)
- **Backend**: FastAPI application (`simpei/src/simpei/`)
- **Database**: SQLite (persistent volume in Kubernetes)

## Deployment Options

1. **Local Development**: Docker Compose
2. **Local Kubernetes**: Kind + Make commands
3. **Production Kubernetes**: Helm chart with custom values

## Prerequisites

Please first make sure you have following tools installed in your machine.

### For Docker setup
- [Docker](https://docker.com)

### For Kubernetes (Kind)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Kind](https://kind.sigs.k8s.io)
- [Make](https://www.gnu.org/software/make/#download)

### For Helm Deployment
- [Helm](https://helm.sh)

## Deployment steps

### Using Docker Compose

It is quickest way to try this project. You only need to have `Docker` installed and make sure docker is running and simply run.

```bash
docker-compose up -d
```

Visit http://localhost:3000 to visit to the Simpei app. 

To stop the application, run

```bash
docker-compose down
```

## Kubernetes Configuration Overview

It is fun time now. Before getting our hands dirty, lets first understand all the Kubernetes yaml files. The `kubernetes/` directory contains essential YAML files for deploying the application. Each file serves a specific purpose in the overall architecture.

### 1. Kind Cluster Configuration (`cluster.yaml`)

Creates a local Kubernetes cluster in Docker using Kind. Let see this block more closely

```yaml
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
```

This YAML block defines the control-plane node and maps HTTP (80) and HTTPS (443) traffic from your local machine into the cluster, so you can access services (via ingress) just like you would in a real Kubernetes environment.

- **`- role: control-plane`**  
  This defines a node in the Kind cluster.  
  - `role: control-plane` means this node will act as the **Kubernetes master node**, running the API server, scheduler, controller-manager, etc.  

- **`extraPortMappings`**  
  This section tells Kind to map ports from the Docker container (where the control-plane node runs) to your host machine. Without this, ports exposed inside the Kubernetes node are not directly accessible from your local machine.

  Inside it:
  - **`containerPort: 80`** → The port **inside the Kind node container**.  
  - **`hostPort: 80`** → The port on your **local machine** that will forward traffic to the containerPort.  
  - **`protocol: TCP`** → Protocol used (usually `TCP`, but could be `UDP` if specified).  

  Same for the second mapping.

### Why is this needed?

By default, services in a Kind cluster are only reachable **inside the cluster** or through `kubectl port-forward`.  
With `extraPortMappings`, you expose ports from the control-plane node to your host, which is useful for:

- Running an **Ingress Controller** (like NGINX).  
  - Ingress controllers typically listen on ports 80 (HTTP) and 443 (HTTPS).  
  - Mapping these to the host lets you access services via `localhost` without extra `port-forwarding`.  


### 2. Backend Deployment & Service (`server.yaml`)

This file contains both a **Service** and a **Kubernetes Deployment** for the FastAPI backend. The Deployment manages the application pods, while the Service provides network access to them.

**Service Configuration:**

_Excerpt of service from the service.yaml file_

```yaml
spec:
  ports:
  - port: 8000 # Service listens on port 8000
    targetPort: 8000 # Forwards traffic to container port 8000
  selector:
    app: server-depl # Routes traffic to pods with label `app: server-depl` (see deployment in service.yaml) (If it wont match, it won't work)
  type: ClusterIP # ClusterIP service implies that this service is only accessible within cluster
```

**Deployment Configuration:**

_Excerpt of deployment from the service.yaml file_

```yaml
spec:
  replicas: 1 # Runs exactly one instance of the backend pod
  ...
  template:
    spec:
      securityContext: # Runs container as non-root user (UID/GID 1000) for security
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - image: simpei-api:latest # Container of fast api service
        imagePullPolicy: IfNotPresent #  Uses local image if available
        name: simpei-api
        ports:
        - containerPort: 8000 # Container port 8000 exposed
        volumeMounts: # Mounts persistent volume storage at `/app/data` for SQLite database
        - name: data-volume
          mountPath: app/data
      volumes: # References the PVC (`server-depl-pvc`) for persistent data storage
      - name: data-volume
        persistentVolumeClaim:
          claimName: server-depl-pvc
```

### 3. Frontend Deployment & Service (`ui.yaml`)

This file contains both a **Kubernetes Deployment** and a **Service** for the Vue.js frontend. The Deployment manages the UI pods, while the Service provides network access to them.

**Service Configuration:**

Nothing new to explain here.

**Deployment Configuration:**

_Excerpt of deployment from the ui.yaml file_

```yaml
    env:
    - name: BACKEND_HOST
      value: "server-serv.default.svc.cluster.local"
    - name: BACKEND_PORT
      value: "8000"
```

- **`env`**: Environment variables that configure backend connection
  - **`BACKEND_HOST`**: Uses Kubernetes DNS to find the backend service
  - **`BACKEND_PORT`**: Backend service port (8000)


### 4. Persistent Storage (`pvc.yaml`)

Creates a Persistent Volume Claim (PVC) that provides 1GB persistent storage for the SQLite database. This ensures data survives pod restarts and redeployments.

**Complete PVC Configuration:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: server-depl-pvc
  labels:
    app: server-depl
  annotations:
    helm.sh/resource-policy: keep
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: "standard"
  resources:
    requests:
      storage: 1Gi
```

**Configuration Breakdown:**

- **`annotations`**:
  - **`helm.sh/resource-policy: keep`**: Prevents Helm from deleting this PVC during upgrades or uninstalls, preserving your database data. Without this, your todos would be lost every time you redeploy!

- **`accessModes`**:
  - **`ReadWriteOnce`**: The volume can be mounted as read-write by a single node only. This is perfect for SQLite since it doesn't support concurrent writes from multiple processes.

- **`storageClassName`**:
  - **`"standard"`**: Uses the default storage class provided by Kind (or your Kubernetes cluster). In Kind, this typically maps to local storage on the Docker container. In cloud environments, this might be SSD, HDD, or other storage types depending on your cluster configuration.

- **`resources`**:
  - **`requests.storage: 1Gi`**: Requests 1 gigabyte of storage space. This is the minimum amount guaranteed to be available. The actual storage allocated might be larger depending on the storage class configuration.

### 5. Ingress Controller (`ingress.yaml`)

The Ingress resource acts as a **reverse proxy** and **load balancer** that routes external HTTP/HTTPS traffic to internal services within the Kubernetes cluster. Think of it as the "front door" to your application.

**Complete Ingress Configuration:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: todo.local
    http:
      paths:
      - backend:
          service:
            name: ui-serv
            port:
              number: 3000
        path: /
        pathType: Prefix
status:
  loadBalancer:
    ingress:
    - hostname: localhost
```

**Configuration Breakdown:**

- **`ingressClassName: nginx`**: Specifies that this Ingress should be handled by the NGINX Ingress Controller.

- **`rules`**: Defines routing rules based on hostnames and paths
  - **`host: todo.local`**: Only requests with the `Host: todo.local` header will match this rule. This is why we need to add `127.0.0.1 todo.local` to `/etc/hosts` (We will do it later) - it makes your browser send requests to `localhost` but with the correct host header.

- **`paths`**: Defines URL path-based routing within the host
  - **`path: /`**: Matches all paths starting with `/` (essentially all requests to this host)
  - **`pathType: Prefix`**: Means any path starting with `/` will match (e.g., `/`, `/todos`, `/api`, etc.)
  - **`backend`**: Specifies where to forward matching requests
    - **`service.name: ui-serv`**: Routes to the frontend service
    - **`service.port.number: 3000`**: Uses port 3000 of the ui-serv service

- **`status`**: Shows the current state of the Ingress resource (this section is typically populated by Kubernetes after deployment)
  - **`loadBalancer.ingress`**: Lists the external endpoints where the Ingress is accessible
  - **`hostname: localhost`**: Indicates that the Ingress is accessible via `localhost` (in Kind's case, this reflects the local development setup)


---

Time to do some real work, Run following command to create the Kind cluster:

```bash
# Create Kubernetes local cluster
make cluster
```
wait for a minute or two (sometimes cluster is not ready immediately)
```bash 
# Load images into cluster
make load-images
```

We need to do one more change. 

```bash
echo "127.0.0.1   todo.local" | sudo tee -a /etc/hosts
```

Now we can deploy our application using `Kubernetes`.

## Kubernetes delopyment with Kind (Local)

Run following command:

```bash
make deploy
```

Access the application at http://todo.local

> Note: Data will not persist when you run using `Kubectl`  commands. To persist data, you need to use `Helm` deployment.

Run 

```bash
make undeploy
```

To remove the application deployment.

## Helm Chart deployment

First, make sure you have created cluster and loaded images into it (see previous section). Now simply run:

```bash
helm install simpei ./chart
```

To uninstall chart

```bash
helm uninstall simpei
```


## Local Development Setup

### Frontend Development (`simpei-ui/`)

**Prerequisites:**
- Node.js (v14+)
- npm or yarn

```bash
cd simpei-ui
npm install
npm run serve
```



**Development server:** http://localhost:8080

### Backend Development (`simpei/src/simpei/`)

**Prerequisites:**
- Python 3.8+
- uv (Python package manager)

```bash
cd simpei
uv sync
uv run uvicorn src.simpei.main:app --reload
```

**API server:** http://localhost:8000

**API docs:** http://localhost:8000/docs
