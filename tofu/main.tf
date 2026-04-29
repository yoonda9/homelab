# Invoke the parameterized vm module twice to clone one Ubuntu 26 guest
# and one CentOS Stream 10 guest from their respective cloud-init
# templates. The pair (vmid 300/301, clone 9001/9002) is the canonical
# test fleet for the Tofu/Ansible split — Tofu owns provisioning and
# ansible/configure-vms.yml owns post-boot configuration.

module "ubuntu26_test" {
  source = "./modules/vm"

  name          = "ubuntu26-test"
  vmid          = 300
  clone_from    = 9001
  memory        = 2048
  cores         = 2
  bridge        = "vmbr0"
  template_node = var.pve_node_name
  tags          = ["ubuntu", "tofu"]
}

module "centos10_test" {
  source = "./modules/vm"

  name          = "centos10-test"
  vmid          = 301
  clone_from    = 9002
  memory        = 2048
  cores         = 2
  bridge        = "vmbr0"
  template_node = var.pve_node_name
  tags          = ["centos", "tofu"]
}
