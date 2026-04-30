# Invoke the parameterized linux_vm module twice to clone one Ubuntu 26
# guest and one CentOS Stream 10 guest from their respective cloud-init
# templates. The pair (vmid 300/301, clone 9001/9002) is the canonical
# test fleet for the Tofu/Ansible split — Tofu owns provisioning and
# ansible/configure-vms.yml owns post-boot configuration.
#
# These ubuntu26-test / centos10-test entries are temporary scaffolding;
# Step 1b pivots `tofu/main.tf` to the two-map for_each shape with
# ubuntu26-dev / centos10-dev as the canonical dev fleet, and the
# default_* and ssh_authorized_keys inputs become root-level variables.

module "ubuntu26_test" {
  source = "./modules/linux_vm"

  name                = "ubuntu26-test"
  vmid                = 300
  clone_from          = 9001
  memory              = 2048
  cores               = 2
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  tags                = ["ubuntu", "tofu"]
  disk_gb             = 32
  default_user        = "user"
  default_password    = "changeme"
  ssh_authorized_keys = []
}

module "centos10_test" {
  source = "./modules/linux_vm"

  name                = "centos10-test"
  vmid                = 301
  clone_from          = 9002
  memory              = 2048
  cores               = 2
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  tags                = ["centos", "tofu"]
  disk_gb             = 32
  default_user        = "user"
  default_password    = "changeme"
  ssh_authorized_keys = []
}
