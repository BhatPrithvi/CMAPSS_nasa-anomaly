module "docker_node" {
  source      = "./modules/docker_node/"
  name_prefix = "node"
  NodeCount   = 2
  app_image   = "nasa-anomaly:latest"
  app_ports   = [8001, 8002]
}