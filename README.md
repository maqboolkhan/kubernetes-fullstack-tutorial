# Simpei Todo Application 

This repository demonstrates how to deploy a full-stack Todo application with a Vue.js frontend, a FastAPI backend, and an SQLite database. The project is designed for learning purposes, with the goal of making Kubernetes deployment easy to understand. It includes examples of deployment using Kubernetes, both with and without Helm, as well as using Docker Compose.

I created this project because, while it is relatively easy to find resources for learning Kubernetes itself, I could not find a clear tutorial that shows how to deploy a full-stack application with custom docker images and persistent data. This repository aims to fill that gap and provide a practical example that learners can follow.

Before diving in, I assume you are already familiar with Docker and have basic overview of Kubernetes. This README is intensive but only explains much! This repository is not about explaining all the `kubectl` commands or how to debug, it is more about how to deploy your fullstack app using Kubernetes. In order to learn Kubernetes properly, checkout [Techworld with Nana](https://www.youtube.com/@TechWorldwithNana) or Linkedin Learning [courses](https://www.linkedin.com/learning/search?keywords=kubernetes).

 I used `Claude Sonnet 4.0` and [Kiro](https://kiro.dev) to generate both UI and API projects as I wanted to focus on Kubernetes part of this project. You can find README files in both projects, however they were generated with `Claude` too. Once both projects were generated, I did the Kubernetes part myself.

## Table of Contents

- [Architecture](#architecture)
- [Deployment Options](#deployment-options)
- [Prerequisites](#prerequisites)
  - [For Docker setup](#for-docker-setup)
  - [For Kubernetes (Kind)](#for-kubernetes-kind)
  - [For Helm Deployment](#for-helm-deployment)
  - [For Azure Deployment](#for-azure-deployment)
- [Deployment steps](#deployment-steps)
  - [Using Docker Compose](#using-docker-compose)
- [Kubernetes Configuration Overview](#kubernetes-configuration-overview)
  - [1. Kind Cluster Configuration (`cluster.yaml`)](#1-kind-cluster-configuration-clusteryaml)
  - [2. Backend Deployment & Service (`server.yaml`)](#2-backend-deployment--service-serveryaml)
  - [3. Frontend Deployment & Service (`ui.yaml`)](#3-frontend-deployment--service-uiyaml)
  - [4. Persistent Storage (`pvc.yaml`)](#4-persistent-storage-pvcyaml)
  - [5. Ingress Controller (`ingress.yaml`)](#5-ingress-controller-ingressyaml)
- [Kubernetes deployment with Kind (Local)](#kubernetes-deployment-with-kind-local)
- [Helm Chart deployment](#helm-chart-deployment)
- [AKS (Azure) deployment](#aks-azure-deployment)
- [AKS cleanup](#aks-cleanup)
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

Please first make sure you have the following tools installed on your machine.

### For Docker setup
- [Docker](https://docker.com)

### For Kubernetes (Kind)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Kind](https://kind.sigs.k8s.io)
- [Make](https://www.gnu.org/software/make/#download)

### For Helm Deployment
- [Helm](https://helm.sh)

### For Azure Deployment
- [azure-cli](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)

## Deployment steps

### Using Docker Compose

It is the quickest way to try this project. You only need to have `Docker` installed and make sure docker is running and simply run.

```bash
docker-compose up -d
```

Visit http://localhost:3000 to access the Simpei app. 

To stop the application, run

```bash
docker-compose down
```

## Kubernetes Configuration Overview

It is fun time now. Before getting our hands dirty, let's first understand all the Kubernetes yaml files. The `kubernetes/` directory contains essential YAML files for deploying the application. Each file serves a specific purpose in the overall architecture.

### 1. Kind Cluster Configuration (`cluster.yaml`)

Creates a local Kubernetes cluster in Docker using Kind hence you do not need this file for Azure deployment. Let's see this block more closely

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
    app: server-depl # Routes traffic to pods with label `app: server-depl` (see deployment in service.yaml) (If it won't match, it won't work)
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
  - **`"standard"`**: Uses the default storage class provided by Kind (or your Kubernetes cluster). In Kind, this typically maps to local storage on the Docker container. In cloud environments, this might be SSD, HDD, or other storage types depending on your cluster configuration. We will use "managed" storage class provided by Azure (see in later section).

- **`resources`**:
  - **`requests.storage: 1Gi`**: Requests 1 gigabyte of storage space. This is the minimum amount guaranteed to be available. The actual storage allocated might be larger depending on the storage class configuration.

I can totally recommend this amazing Youtube [video](https://www.youtube.com/watch?v=yYQXKiiJzS8). 

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

After having understanding of yaml files it is time to do some real work. Run the following command to create the Kind cluster:

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

## Kubernetes deployment with Kind (Local)

Run the following command:

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

First, make sure you have created the cluster and loaded images into it (see previous section). Now simply run:

```bash
helm install simpei ./chart
```

To uninstall the chart

```bash
helm uninstall simpei
```

## AKS (Azure) deployment

Before we start, know that deploying on AKS is not **free**. However, once you create your account you get 200$ credits for free for one month. These 200$ are more than enough to deploy and play around. Once you are done with your experiment, don't forget to delete all the resources (I will also write here how to do that).

Create your Azure account [here](https://portal.azure.com).

#### Login to your Azure CLI

```bash
az login # Enter 1 for subscription
```

Create Azure Resource group

```bash
az group create --name todo-app --location westus
```

You should get the following JSON back

```Json
{
  "id": "/subscriptions/<some-id>/resourceGroups/todo-app",
  "location": "westus",
  "managedBy": null,
  "name": "todo-app",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": null,
  "type": "Microsoft.Resources/resourceGroups"
}
```

Now let's create the AKS cluster (the following command will take a while)

```bash
az aks create --name todo-app-cluster --resource-group todo-app --generate-ssh-keys --node-vm-size Standard_B2s --node-count 2 --location westus
```

If everything works, then you should get a big JSON back!

Now let's login to the AKS cluster we just created!

```bash
az aks get-credentials --name todo-app-cluster --resource-group todo-app
```

The output should look like

```
Merged "todo-app-cluster" as current context in /Users/your_user/.kube/config
```

> Remember from now on when you run `kubectl` commands, you will be executing them on AKS not on your local Kind cluster

Now we have to install nginx as the ingress controller, you can find the installation command [here](https://kubernetes.github.io/ingress-nginx/deploy/#azure)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.13.1/deploy/static/provider/cloud/deploy.yaml
```

Now in order to use our docker images by AKS cluster, we first need to create a Azure's container registry (ACR) and then push our images into it!

Let's create ACR now
```bash
az acr create --resource-group todo-app -n <acr_name, this name is globally unique> --sku Basic
```
`-n` option is for your `ACR` name and it should be globally unique (so some name might already be taken)

Now we have to login to container registry we just created. In order to login, first we need to get credentials

```bash
az acr login -n <acr_name> --expose-token 
```

The above command should give you a JSON
```json
{
  "accessToken": "a huge string here",
  "loginServer": "<your acr name>.azurecr.io",
  "refreshToken": "a huge string here",
  "username": "some zeros"
}
```

Once we have the username and accessToken, then we are ready to login to ACR from our local Docker.

```bash
docker login <acr_name>.azurecr.io --username <username> --password <accessToken>
# output should be: Login Succeeded
```

Now as I am using `Mac` and we are going to deploy on Azure Linux images, so we need to build Docker images for Linux and then push

```bash
# Make sure you are at root project directory
docker buildx build --platform linux/amd64 -t <acr_name>.azurecr.io/simpei-ui:0.1.0 --push ./simpei-ui 
docker buildx build --platform linux/amd64 -t <acr_name>.azurecr.io/simpei-api:0.1.0 --push ./simpei
```

Now we can check if our images were pushed successfully or not with the following command

```bash
az acr repository list --name <acr_name>
# [
#   "simpei-api",
#   "simpei-ui"
# ]
```

Now as we have pushed our images to ACR, we need to connect ACR with Kubernetes so that Kubernetes can pull these images from ACR. For that we first need to create a `pull secret`

```bash
kubectl create secret docker-registry <name_of_pull_secret> --docker-password '<accessToken>' --docker-server=<acr_name> --docker-username=<username>
# Output: secret/<name_of_pull_secret> created
```

In the above command, `name_of_pull_secret` can be anything and `accessToken` & `username` should be the same as we used when logging to ACR with docker.
Now we need to attach this pull secret with the AKS cluster's namespace. We do that by editing the service account as every namespace has one. Run the following command

```bash
kubectl edit sa default 
```

Running the above command will open up a file in the vim editor. You need to add the following section at the end of that.

```yaml
imagePullSecrets:
- name: <name_of_pull_secret>
```

then finally save the file. We are almost ready to see our web alive :-)
Now we just need the external IP address of our nginx controller. Run

```bash
kubectl get svc -n ingress-nginx
# copy the external IP address of ingress-nginx-controller
```

Then edit the `chart/values-azure.yaml` file. Put your `ACR` name and `external IP address` there.
Now run 

```bash
helm upgrade --install <name_of_deployment> ./chart -f chart/values-azure.yaml
```
`<name_of_deployment>` can be any name (think of it as a tag). Wait for a few seconds, and finally visit http://external-ip.nip.io 🔥
You have done it.

Now to uninstall the deployment run:

```bash
helm uninstall <name_of_deployment>
```

## AKS cleanup

Very important step otherwise Azure will continue billing your app. First, let's delete the resource group you created:

```bash
az group delete --name <resource group name>
```

Now delete the context from your local machine,

```bash
kubectl config get-contexts # get the name of the AKS cluster
kubectl config delete-context --name <name of your cluster>
```

Now go to [portal.azure.com/subscription](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeV2), click on your subscription you created, and then `cancel` your subscription (make sure to turn off your subscription).

Fin, Tschüss

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
