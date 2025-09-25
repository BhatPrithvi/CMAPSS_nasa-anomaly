variable "name_prefix" {}
variable "NodeCount" { default = 1 }
variable "app_image" { default = "nasa-anomaly:latest" }
variable "app_ports" { type = list(number) }

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_container" "node"{
    count = var.NodeCount
    name  = "${var.name_prefix}-${count.index+1}"
    image = var.app_image


ports{
    internal = 8000
    external = var.app_ports[count.index]
}

volumes{
    host_path = "/output/nasa-anomaly/logs-${count.index+1}"
    container_path = "/app/logs"
}
}