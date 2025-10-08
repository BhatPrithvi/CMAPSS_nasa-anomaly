output "node_map" {
  description = "Mapping of ML nodes with their Flask and SSH ports"
  value = {
    node-1 = {
      flask_port = 8001
      ssh_port   = 2220
    }
    node-2 = {
      flask_port = 8002
      ssh_port   = 2221
    }
  }
}


