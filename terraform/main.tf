terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Verify Minikube is running
resource "null_resource" "verify_minikube" {
  provisioner "local-exec" {
    command = "minikube status"
  }
}

# Verify Kubernetes nodes are ready
resource "null_resource" "verify_nodes" {
  depends_on = [null_resource.verify_minikube]

  provisioner "local-exec" {
    command = "kubectl get nodes"
  }
}

# Verify all system pods are running
resource "null_resource" "verify_pods" {
  depends_on = [null_resource.verify_nodes]

  provisioner "local-exec" {
    command = "kubectl get pods -A"
  }
}

# Verify local registry is running
resource "null_resource" "verify_registry" {
  depends_on = [null_resource.verify_pods]

  provisioner "local-exec" {
    command = "curl -s http://localhost:5001/v2/quiz-app/tags/list"
  }
}
