locals {
  # template_ids — authoritative VM-ID map for the three Packer-built
  # templates. Each key is the short-name passed to the dev_vm module's
  # `os` variable and to scripts/build_template.sh. The values are the
  # stable PVE VM-IDs reserved for this pipeline (clause #1 boundary
  # via the 9100–9102 range and the pkr- name prefix).
  template_ids = {
    ubuntu26 = 9100
    fedora   = 9101
    win11    = 9102
  }
}
