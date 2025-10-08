#!/bin/bash
# terraform -chdir=terraform → run Terraform commands inside the terraform/ directory, where configs live.
# output -json node_map → fetches the value of the Terraform output variable node_map in JSON form.
terraform -chdir=terraform output -json node_map > /tmp/tfout.json

# Creates a new file ansible/inventories/dev.ini.
# The first line is [ml_nodes], which defines an Ansible host group called ml_nodes.
# > overwrites the file if it already exists
echo "[ml_nodes]" > Ansible/inventories/dev.ini

# Uses jq (a JSON processor) to transform the JSON into INI-style host entries.
# to_entries[] → turns JSON object into an array of {key, value} pairs.
jq -r 'to_entries[] | "\(.key) ansible_host=127.0.0.1 ansible_port=\(.value.ssh_port) ansible_user=ansible ansible_password=ansible ansible_connection=ssh"' /tmp/tfout.json >> Ansible/inventories/dev.ini


echo "Inventory generated at Ansible/inventories/dev.ini"