.PHONY: help
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: cluster
cluster: ## Create Kubernetes cluster with ingress
	@echo "🚀 Creating Kubernetes cluster..."
	@kind create cluster --name fullstack --config Kubernetes/cluster.yaml
	@echo "🚀 Deploying ingress nginx..."
	@kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml


.PHONY: delete-cluster
delete-cluster: ## Delete Kubernetes cluster
	@echo "🚀 Deleting Kubernetes cluster..."
	@kind delete cluster --name fullstack

.PHONY: build-images
build-images: ## Build Docker images for backend and frontend
	@echo "🚀 Building Simpei application for Kubernetes deployment..."
	@echo "📦 Building backend image..."
	@docker build -t simpei-api:latest ./simpei
	@echo "📦 Building frontend image for Kubernetes..."
	@docker build -t simpei-ui:latest --build-arg VUE_APP_API_URL=/api --build-arg NGINX_CONFIG=nginx-k8s.conf ./simpei-ui
	@echo "✅ Build complete!"

.PHONY: load-images
load-images: build-images ## Build and load images into Kubernetes cluster
	@echo "🚀 Loading Simpei application images into Kubernetes cluster..."
	@kind load docker-image simpei-ui:latest --name fullstack
	@kind load docker-image simpei-api:latest --name fullstack
	@echo "✅ Images loaded into Kubernetes cluster!"

.PHONY: deploy
deploy: ## Deploy application to Kubernetes cluster
	@echo "🚀 Deploying Simpei application to Kubernetes cluster..."
	@kubectl apply -f pvc.yaml
	@kubectl apply -f server.yaml
	@kubectl apply -f ui.yaml
	@kubectl apply -f ingress.yaml
	@echo "✅ Simpei application deployed to Kubernetes cluster!"
	@echo "🌎 Available at http://todo.local"

.PHONY: undeploy
undeploy: ## Remove application from Kubernetes cluster
	@echo "🚀 Undeploying Simpei application from Kubernetes cluster..."
	@kubectl delete -f server.yaml
	@kubectl delete -f ui.yaml
	@kubectl delete -f ingress.yaml
	@kubectl delete -f pvc.yaml
	@echo "✅ Simpei application undeployed from Kubernetes cluster!" 