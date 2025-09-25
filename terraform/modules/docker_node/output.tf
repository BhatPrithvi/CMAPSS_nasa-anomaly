output "nodes"{
    value = {
        for i,c in docker_container.node :
        c.name => {
            app_port = c.ports[0].external
        }

    }
}