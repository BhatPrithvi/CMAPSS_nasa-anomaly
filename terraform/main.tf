terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

##############################
# ML Containers
##############################

resource "docker_container" "node1_ml" {
  name  = "node-1-ml"
  image = "nasa-anomaly:latest"
  ports {
    internal = 8000
    external = 8001
  }
}

resource "docker_container" "node2_ml" {
  name  = "node-2-ml"
  image = "nasa-anomaly:latest"
  ports {
    internal = 8000
    external = 8002
  }
}

##############################
# SSH Sidecar Containers
##############################

resource "docker_container" "node1_ssh" {
  name  = "node-1-ssh"
  image = "nasa-anomaly-ssh:latest"
  ports {
    internal = 22
    external = 2220
  }
}

resource "docker_container" "node2_ssh" {
  name  = "node-2-ssh"
  image = "nasa-anomaly-ssh:latest"
  ports {
    internal = 22
    external = 2221
  }
}
