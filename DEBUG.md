# DEBUG Error

Running  `./scripts/build_template.sh fedora` fails with the following output.

It seems like the cloud-init isn't actually getting picked up properly and so the user and SSH are not being set up as expected.

```shell
==> step 1: env-var pre-flight
==> step 2: fedora — ensure tpl-cloud-fedora44 source template (idempotent)
==> step 1: idempotent guard — qm status 9001 on root@pve.home.arpa
==>        template VM 9001 (tpl-cloud-fedora44) already exists; skipping bootstrap
==> step 4: packer init
==> step 5: packer build -only=proxmox-clone.fedora (force=true overwrite)
[1;32mproxmox-clone.fedora: output will be in this color.[0m

[1;32m==> proxmox-clone.fedora: Creating CD disk...[0m
[1;32m==> proxmox-clone.fedora: xorriso 1.5.6 : RockRidge filesystem manipulator, libburnia project.[0m
[1;32m==> proxmox-clone.fedora: Drive current: -outdev 'stdio:/tmp/packer3206625237.iso'[0m
[1;32m==> proxmox-clone.fedora: Media current: stdio file, overwriteable[0m
[1;32m==> proxmox-clone.fedora: Media status : is blank[0m
[1;32m==> proxmox-clone.fedora: Media summary: 0 sessions, 0 data blocks, 0 data, 73.6g free[0m
[1;32m==> proxmox-clone.fedora: xorriso : WARNING : -volid text does not comply to ISO 9660 / ECMA 119 rules[0m
[1;32m==> proxmox-clone.fedora: Added to ISO image: directory '/'='/tmp/packer_to_cdrom2276719554'[0m
[1;32m==> proxmox-clone.fedora: xorriso : UPDATE :       2 files added in 1 seconds[0m
[1;32m==> proxmox-clone.fedora: xorriso : UPDATE :       2 files added in 1 seconds[0m
[1;32m==> proxmox-clone.fedora: ISO image produced: 185 sectors[0m
[1;32m==> proxmox-clone.fedora: Written to medium : 185 sectors at LBA 0[0m
[1;32m==> proxmox-clone.fedora: Writing to 'stdio:/tmp/packer3206625237.iso' completed successfully.[0m
[1;32m==> proxmox-clone.fedora: Done copying paths from CD_dirs[0m
[1;32m==> proxmox-clone.fedora: Uploaded ISO to local:iso/packer3206625237.iso[0m
[1;32m==> proxmox-clone.fedora: Force set, checking for existing artifact on PVE cluster[0m
[1;32m==> proxmox-clone.fedora: No existing artifact found[0m
[1;32m==> proxmox-clone.fedora: Creating VM[0m
[1;32m==> proxmox-clone.fedora: Starting VM[0m
[1;32m==> proxmox-clone.fedora: Waiting for SSH to become available...[0m
[1;32m==> proxmox-clone.fedora: Connected to SSH![0m
[1;32m==> proxmox-clone.fedora: Provisioning with shell script: /tmp/packer-shell1776929545[0m
[1;32m==> proxmox-clone.fedora: uid=1000(user) gid=1000(user) groups=1000(user)[0m
[1;32m==> proxmox-clone.fedora: /usr/bin/python3[0m
[1;32m==> proxmox-clone.fedora: enabled[0m
[1;32m==> proxmox-clone.fedora: Provisioning with shell script: /tmp/packer-shell243340035[0m
[1;31m==> proxmox-clone.fedora: Updating and loading repositories:[0m
[1;31m==> proxmox-clone.fedora: Repositories loaded.[0m
[1;31m==> proxmox-clone.fedora: Package "cloud-init-25.3-3.fc44.noarch" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "cloud-utils-growpart-0.33-13.fc44.noarch" is already installed.[0m
[1;31m==> proxmox-clone.fedora:[0m
[1;32m==> proxmox-clone.fedora: Nothing to do.[0m
[1;31m==> proxmox-clone.fedora: Updating and loading repositories:[0m
[1;31m==> proxmox-clone.fedora: Repositories loaded.[0m
[1;31m==> proxmox-clone.fedora: Group "container-management" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "podman-5:5.8.1-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Group "core" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "sudo-1.9.17-7.p2.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "curl-8.18.0-4.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "dnf5-5.4.1.0-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "bash-5.3.9-3.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "coreutils-9.10-3.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "e2fsprogs-1.47.3-4.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "less-691-2.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "openssh-clients-10.2p1-7.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "openssh-server-10.2p1-7.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "setup-2.15.0-28.fc44.noarch" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "shadow-utils-2:4.19.0-6.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "util-linux-2.41.3-12.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "audit-4.1.4-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "filesystem-3.18-52.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "glibc-2.43-2.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "hostname-3.25-4.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "iproute-6.17.0-2.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "iputils-20250605-2.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "kbd-2.9.0-3.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "man-db-2.13.1-3.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "ncurses-6.6-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "parted-3.6-14.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "policycoreutils-3.10-1.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora: Package                                        Arch   Version                               Repository                            Size[0m
[1;32m==> proxmox-clone.fedora: Upgrading:[0m
[1;32m==> proxmox-clone.fedora:  elfutils-debuginfod-client                    x86_64 0:0.195-1.fc44                        updates                           83.8 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "procps-ng-4.0.6-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "rootfiles-9.0-6.fc44.noarch" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "rpm-6.0.1-2.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:    replacing elfutils-debuginfod-client        x86_64 0:0.194-5.fc44                        4e4a4f70cfdd4047b39087e8606c2591  83.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  elfutils-libelf                               x86_64 0:0.195-1.fc44                        updates                            1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:    replacing elfutils-libelf                   x86_64 0:0.194-5.fc44                        4e4a4f70cfdd4047b39087e8606c2591   1.1 MiB[0m
[1;31m==> proxmox-clone.fedora: Package "selinux-policy-targeted-43.3-1.fc44.noarch" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  elfutils-libs                                 x86_64 0:0.195-1.fc44                        updates                          715.3 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "sssd-common-2.12.0-4.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "sssd-kcm-2.12.0-4.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "systemd-259.5-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "vim-minimal-2:9.2.240-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "NetworkManager-1:1.56.0-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "dnf5-plugins-5.4.1.0-1.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:    replacing elfutils-libs                     x86_64 0:0.194-5.fc44                        4e4a4f70cfdd4047b39087e8606c2591 715.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  harfbuzz                                      x86_64 0:14.1.0-2.fc44                       updates                            2.8 MiB[0m
[1;32m==> proxmox-clone.fedora:    replacing harfbuzz                          x86_64 0:12.3.2-1.fc44                       4e4a4f70cfdd4047b39087e8606c2591   2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  libldb                                        x86_64 2:4.24.1-1.fc44                       updates                          465.6 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "prefixdevname-0.2.0-8.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:    replacing libldb                            x86_64 2:4.24.0-6.fc44                       4e4a4f70cfdd4047b39087e8606c2591 465.6 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "systemd-resolved-259.5-1.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  ngtcp2                                        x86_64 0:1.22.1-1.fc44                       updates                          338.2 KiB[0m
[1;32m==> proxmox-clone.fedora:    replacing ngtcp2                            x86_64 0:1.21.0-1.fc44                       4e4a4f70cfdd4047b39087e8606c2591 330.2 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "zram-generator-defaults-1.2.1-5.fc44.noarch" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  ngtcp2-crypto-ossl                            x86_64 0:1.22.1-1.fc44                       updates                           51.6 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "systemd-oomd-defaults-259.5-1.fc44.noarch" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "qemu-guest-agent-2:10.2.2-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "tar-2:1.35-8.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:    replacing ngtcp2-crypto-ossl                x86_64 0:1.21.0-1.fc44                       4e4a4f70cfdd4047b39087e8606c2591  51.6 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "sudo-1.9.17-7.p2.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  pinentry                                      x86_64 0:1.3.2-3.fc44                        updates                          266.8 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "dnf5-5.4.1.0-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "systemd-udev-259.5-1.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:    replacing pinentry                          x86_64 0:1.3.2-2.fc44                        4e4a4f70cfdd4047b39087e8606c2591 266.8 KiB[0m
[1;32m==> proxmox-clone.fedora: Installing group/module packages:[0m
[1;32m==> proxmox-clone.fedora:  ModemManager                                  x86_64 0:1.24.2-3.fc44                       fedora                             4.7 MiB[0m
[1;31m==> proxmox-clone.fedora: Package "chrony-4.8-5.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-adsl                           x86_64 1:1.56.0-1.fc44                       fedora                            39.8 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "systemd-oomd-defaults-259.5-1.fc44.noarch" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-bluetooth                      x86_64 1:1.56.0-1.fc44                       fedora                           101.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-config-connectivity-fedora     noarch 1:1.56.0-1.fc44                       fedora                           310.0   B[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-openconnect-gnome              x86_64 0:1.2.10-11.fc44                      fedora                           154.8 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "unzip-6.0-69.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-openvpn-gnome                  x86_64 1:1.12.5-4.fc44                       fedora                           354.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-ppp                            x86_64 1:1.56.0-1.fc44                       fedora                            63.4 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "bash-completion-1:2.17-2.fc44.noarch" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-ssh-gnome                      x86_64 0:1.4.4-1.fc44                        updates                          172.9 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "btrfs-progs-6.19.1-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "cpio-2.15-9.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-vpnc-gnome                     x86_64 1:1.4.0-6.fc44                        fedora                           145.3 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "dnf5-plugins-5.4.1.0-1.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "rsync-3.4.1-6.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-wifi                           x86_64 1:1.56.0-1.fc44                       fedora                           329.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-wwan                           x86_64 1:1.56.0-1.fc44                       fedora                           140.8 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "which-2.23-4.fc44.x86_64" is already installed.[0m
[1;32m==> proxmox-clone.fedora:  PackageKit-command-not-found                  x86_64 0:1.3.4-3.fc44                        fedora                            34.9 KiB[0m
[1;31m==> proxmox-clone.fedora: Package "file-5.46-9.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "gnupg2-2.4.9-5.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora: Package "psmisc-23.7-7.fc44.x86_64" is already installed.[0m
[1;31m==> proxmox-clone.fedora:[0m
[1;32m==> proxmox-clone.fedora:  PackageKit-gstreamer-plugin                   x86_64 0:1.3.4-3.fc44                        fedora                            23.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  PackageKit-gtk3-module                        x86_64 0:1.3.4-3.fc44                        fedora                            19.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-cli                                      x86_64 0:2.17.8-3.fc44                       fedora                             0.0   B[0m
[1;31m==> proxmox-clone.fedora: Total size of inbound packages is 2 GiB. Need to download 2 GiB.[0m
[1;31m==> proxmox-clone.fedora: After this operation, 5 GiB extra will be used (install 5 GiB, remove 6 MiB).[0m
[1;32m==> proxmox-clone.fedora:  acl                                           x86_64 0:2.3.2-6.fc44                        fedora                           219.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  adobe-source-code-pro-fonts                   noarch 0:2.042.1.062.1.026-9.fc44            fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  alsa-sof-firmware                             noarch 0:2025.12.2-1.fc44                    fedora                            10.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  alsa-ucm                                      noarch 0:1.2.15.3-3.fc44                     fedora                           626.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  alsa-utils                                    x86_64 0:1.2.15.2-3.fc44                     fedora                             2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  amd-gpu-firmware                              noarch 0:20260410-1.fc44                     updates                           26.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  amd-ucode-firmware                            noarch 0:20260410-1.fc44                     updates                          608.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  at-spi2-atk                                   x86_64 0:2.60.3-1.fc44                       updates                          284.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  atheros-firmware                              noarch 0:20260410-1.fc44                     updates                           39.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  attr                                          x86_64 0:2.5.2-8.fc44                        fedora                           172.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  b43-fwcutter                                  x86_64 0:019-41.fc44                         fedora                            55.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  b43-openfwwf                                  noarch 0:5.2-48.fc44                         fedora                            30.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  baobab                                        x86_64 0:50.0-1.fc44                         fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  bash-color-prompt                             noarch 0:0.7.1-3.fc44                        fedora                            32.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  bc                                            x86_64 0:1.08.2-4.fc44                       fedora                           236.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  bind-utils                                    x86_64 32:9.18.48-1.fc44                     updates                          659.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  bluez-cups                                    x86_64 0:5.86-4.fc44                         fedora                            47.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  brcmfmac-firmware                             noarch 0:20260410-1.fc44                     updates                            9.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  brltty                                        x86_64 0:6.8-8.fc44                          fedora                             8.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  bzip2                                         x86_64 0:1.0.8-23.fc44                       fedora                            95.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  cifs-utils                                    x86_64 0:7.5-1.fc44                          fedora                           274.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  cirrus-audio-firmware                         noarch 0:20260410-1.fc44                     updates                            2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  colord                                        x86_64 0:1.4.8-4.fc44                        fedora                             2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  compsize                                      x86_64 0:1.5^git20250123.d79eacf-15.fc44     fedora                            22.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  cryptsetup                                    x86_64 0:2.8.4-1.fc44                        fedora                           770.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  cups                                          x86_64 1:2.4.18-1.fc44                       updates                            8.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  cups-browsed                                  x86_64 1:2.1.1-7.fc44                        fedora                           400.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  cups-filters                                  x86_64 1:2.0.1-14.fc44                       fedora                           974.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  cups-pk-helper                                x86_64 0:0.2.7-12.fc44                       fedora                           375.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  cyrus-sasl-plain                              x86_64 0:2.1.28-35.fc44                      fedora                            47.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  decibels                                      noarch 0:49.6.1-1.fc44                       updates                          537.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  default-editor                                noarch 0:8.7.1-2.fc44                        updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-cjk-mono                        noarch 0:4.3-1.fc44                          fedora                           424.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-cjk-sans                        noarch 0:4.3-1.fc44                          fedora                             2.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-cjk-serif                       noarch 0:4.3-1.fc44                          fedora                           417.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-core-emoji                      noarch 0:4.3-1.fc44                          fedora                           338.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-core-math                       noarch 0:4.3-1.fc44                          fedora                           334.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-core-mono                       noarch 0:4.3-1.fc44                          fedora                           371.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-core-sans                       noarch 0:4.3-1.fc44                          fedora                            11.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-core-serif                      noarch 0:4.3-1.fc44                          fedora                           364.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-other-mono                      noarch 0:4.3-1.fc44                          fedora                           378.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-other-sans                      noarch 0:4.3-1.fc44                          fedora                           380.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-other-serif                     noarch 0:4.3-1.fc44                          fedora                           371.0   B[0m
[1;32m==> proxmox-clone.fedora:  deltarpm                                      x86_64 0:3.6.5-8.fc44                        fedora                           222.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  desktop-backgrounds-gnome                     noarch 0:44.0.0-2.fc44                       fedora                           361.0   B[0m
[1;32m==> proxmox-clone.fedora:  dnsmasq                                       x86_64 0:2.92-4.fc44                         fedora                           821.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  dos2unix                                      x86_64 0:7.5.3-3.fc44                        fedora                           819.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  dosfstools                                    x86_64 0:4.2-18.fc44                         fedora                           236.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  dracut-config-rescue                          x86_64 0:108-6.fc44                          fedora                             4.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  ethtool                                       x86_64 2:7.0-1.fc44                          updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  exfatprogs                                    x86_64 0:1.3.2-1.fc44                        fedora                           267.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-bookmarks                              noarch 0:28-36.fc44                          fedora                            93.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-chromium-config                        noarch 0:3.0-9.fc44                          fedora                            17.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-flathub-remote                         noarch 0:1-12.fc44                           fedora                             5.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-release-workstation                    noarch 0:44-17                               fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  fedora-workstation-backgrounds                noarch 0:1.6-9.fc44                          fedora                             5.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-workstation-repositories               x86_64 0:38-9.fc44                           fedora                             3.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  firefox                                       x86_64 0:150.0-1.fc44                        fedora                           270.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  firewalld                                     noarch 0:2.4.0-2.fc44                        fedora                             2.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  fpaste                                        noarch 0:0.5.0.0-4.fc44                      fedora                            75.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  fprintd-pam                                   x86_64 0:1.94.5-5.fc44                       fedora                            30.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  gamemode                                      x86_64 0:1.8.2-4.fc44                        fedora                           294.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  ghostscript                                   x86_64 0:10.06.0-2.fc44                      fedora                            30.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  git                                           x86_64 0:2.54.0-1.fc44                       updates                           57.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  glib-networking                               x86_64 0:2.80.1-4.fc44                       fedora                           750.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  glibc-all-langpacks                           x86_64 0:2.43-2.fc44                         fedora                           227.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  glycin-thumbnailer                            x86_64 0:2.1.1-1.fc44                        fedora                           448.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-backgrounds                             noarch 0:50.0-1.fc44                         fedora                            37.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-bluetooth                               x86_64 1:47.2-1.fc44                         updates                           95.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-boxes                                   x86_64 0:50.0-1.fc44                         fedora                             6.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-browser-connector                       x86_64 0:42.1-14.fc44                        fedora                           125.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-calculator                              x86_64 0:50.0-1.fc44                         fedora                             8.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-calendar                                x86_64 0:50.0-1.fc44                         fedora                             2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-characters                              x86_64 0:50.0-1.fc44                         fedora                             2.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-classic-session                         noarch 0:50.1-1.fc44                         updates                            8.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-clocks                                  x86_64 0:50.0-1.fc44                         fedora                             3.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-color-manager                           x86_64 0:3.36.2-3.fc44                       fedora                             3.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-connections                             x86_64 0:50.0-1.fc44                         fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-contacts                                x86_64 0:50.0-1.fc44                         fedora                             2.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-control-center                          x86_64 0:50.1-1.fc44                         updates                           23.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-disk-utility                            x86_64 0:46.1-4.fc44                         fedora                             6.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-epub-thumbnailer                        x86_64 0:1.8-4.fc44                          fedora                            61.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-font-viewer                             x86_64 0:50.0-1.fc44                         fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-initial-setup                           x86_64 0:50.0-3.fc44                         fedora                             1.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-logs                                    x86_64 0:50.0-1.fc44                         fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-maps                                    x86_64 0:50.1-1.fc44                         updates                            5.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-remote-desktop                          x86_64 0:50.1-1.fc44                         updates                            2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-session-wayland-session                 x86_64 0:50.0-1.fc44                         fedora                             7.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-settings-daemon                         x86_64 0:50.1-1.fc44                         updates                            6.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell                                   x86_64 0:50.1-2.fc44                         updates                           14.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-background-logo         noarch 0:50~beta-2.fc44                      fedora                            58.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-software                                x86_64 0:50.0-2.fc44                         fedora                            12.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-system-monitor                          x86_64 0:50.0-1.fc44                         fedora                             5.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-text-editor                             x86_64 0:50.0-1.fc44                         fedora                             2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-user-docs                               noarch 0:50.0-1.fc44                         fedora                            60.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-user-share                              x86_64 0:48.2-1.fc44                         fedora                           751.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-weather                                 noarch 0:50.0-1.fc44                         fedora                           834.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  gst-thumbnailers                              x86_64 0:1.0.0-1.fc44                        fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugin-dav1d                       x86_64 0:0.15.0-1.fc44                       fedora                           551.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugin-libav                       x86_64 0:1.28.2-1.fc44                       updates                          330.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugin-openh264                    x86_64 0:1.28.2-1.fc44                       updates                           68.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-bad-free                   x86_64 0:1.28.2-1.fc44                       updates                           10.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-good                       x86_64 0:1.28.2-1.fc44                       updates                            7.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-ugly-free                  x86_64 0:1.28.2-1.fc44                       updates                          565.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gutenprint-cups                               x86_64 0:5.3.5-7.fc44                        fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-afc                                      x86_64 0:1.60.0-1.fc44                       fedora                           153.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-afp                                      x86_64 0:1.60.0-1.fc44                       fedora                           191.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-archive                                  x86_64 0:1.60.0-1.fc44                       fedora                            39.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-fuse                                     x86_64 0:1.60.0-1.fc44                       fedora                            49.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-goa                                      x86_64 0:1.60.0-1.fc44                       fedora                           162.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-gphoto2                                  x86_64 0:1.60.0-1.fc44                       fedora                           161.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-mtp                                      x86_64 0:1.60.0-1.fc44                       fedora                           169.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-smb                                      x86_64 0:1.60.0-1.fc44                       fedora                           100.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  hplip                                         x86_64 0:3.25.8-2.fc44                       fedora                            29.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  hyperv-daemons                                x86_64 0:6.10-3.fc44                         fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  ibus-anthy                                    x86_64 0:1.5.18-1.fc44                       fedora                             8.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-chewing                                  x86_64 0:2.1.7-2.fc44                        fedora                           232.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-gtk3                                     x86_64 0:1.5.34-1.fc44                       updates                           48.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-gtk4                                     x86_64 0:1.5.34-1.fc44                       updates                           47.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-hangul                                   x86_64 0:1.5.5-12.fc44                       fedora                           200.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-libpinyin                                x86_64 0:1.16.5-3.fc44                       fedora                             2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-m17n                                     x86_64 0:1.4.38-1.fc44                       fedora                           270.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-typing-booster                           noarch 0:2.30.7-1.fc44                       updates                            9.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  intel-audio-firmware                          noarch 0:20260410-1.fc44                     updates                            3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  intel-gpu-firmware                            noarch 0:20260410-1.fc44                     updates                            8.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  intel-lpmd                                    x86_64 0:0.0.9-3.fc44                        fedora                           175.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  intel-vsc-firmware                            noarch 0:20260410-1.fc44                     updates                            7.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  iptables-nft                                  x86_64 0:1.8.11-13.fc44                      fedora                           461.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  iptstate                                      x86_64 0:2.2.7-11.fc44                       fedora                           103.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  iwlegacy-firmware                             noarch 0:20260410-1.fc44                     updates                          123.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  iwlwifi-dvm-firmware                          noarch 0:20260410-1.fc44                     updates                            1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  iwlwifi-mvm-firmware                          noarch 0:20260410-1.fc44                     updates                           62.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  libertas-firmware                             noarch 0:20260410-1.fc44                     updates                            1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libglvnd-gles                                 x86_64 1:1.7.0-9.fc44                        fedora                            97.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-calc                              x86_64 1:26.2.2.2-2.fc44                     updates                           27.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-emailmerge                        x86_64 1:26.2.2.2-2.fc44                     updates                           30.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsane-hpaio                                 x86_64 0:3.25.8-2.fc44                       fedora                           185.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libva-intel-media-driver                      x86_64 0:25.4.6-2.fc44                       fedora                            10.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  linux-firmware                                noarch 0:20260410-1.fc44                     updates                           50.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  localsearch                                   x86_64 0:3.11.1-1.fc44                       updates                            3.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  logrotate                                     x86_64 0:3.22.0-5.fc44                       fedora                           152.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  loupe                                         x86_64 0:50.0-1.fc44                         fedora                             7.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  lrzsz                                         x86_64 0:0.12.20-76.fc44                     fedora                           184.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  lsof                                          x86_64 0:4.98.0-9.fc44                       fedora                           578.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  mailcap                                       noarch 0:2.1.54-10.fc44                      fedora                            86.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  man-pages                                     noarch 0:6.13-3.fc44                         fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  mcelog                                        x86_64 3:175-14.fc44                         fedora                           158.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  mdadm                                         x86_64 0:4.3-11.fc44                         fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  mediawriter                                   x86_64 0:5.3.1-1.fc44                        updates                            3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-dri-drivers                              x86_64 0:26.0.5-3.fc44                       updates                           51.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-vulkan-drivers                           x86_64 0:26.0.5-3.fc44                       updates                          159.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  microcode_ctl                                 x86_64 2:2.1-74.fc44                         fedora                            16.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  mpage                                         x86_64 0:2.5.7-24.fc44                       fedora                           133.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  mt7xxx-firmware                               noarch 0:20260410-1.fc44                     updates                           21.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  mtr                                           x86_64 2:0.95-14.fc44                        fedora                           188.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  nautilus                                      x86_64 0:50.1-1.fc44                         updates                           13.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  net-tools                                     x86_64 0:2.0-0.77.20160912git.fc44           fedora                           843.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  nfs-utils                                     x86_64 1:2.8.7-1.fc44                        updates                          608.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  nmap-ncat                                     x86_64 4:7.92-8.fc44                         fedora                           481.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  nss-mdns                                      x86_64 0:0.15.1-28.fc44                      fedora                           156.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  ntfs-3g                                       x86_64 2:2022.10.3-12.fc44                   fedora                           319.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  ntfsprogs                                     x86_64 2:2022.10.3-12.fc44                   fedora                           995.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  nvidia-gpu-firmware                           noarch 0:20260410-1.fc44                     updates                          101.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  nxpwireless-firmware                          noarch 0:20260410-1.fc44                     updates                          905.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  open-vm-tools-desktop                         x86_64 0:13.0.10-2.fc44                      fedora                           453.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  opensc                                        x86_64 0:0.27.1-2.fc44                       updates                            1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  orca                                          noarch 0:50.1.2-1.fc44                       updates                           22.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  pam_afs_session                               x86_64 0:2.6-25.fc44                         fedora                            94.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  papers                                        x86_64 0:49.6-1.fc44                         updates                           14.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  papers-nautilus                               x86_64 0:49.6-1.fc44                         updates                           19.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  paps                                          x86_64 0:0.8.0-15.fc44                       fedora                           249.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  passwdqc                                      x86_64 0:2.0.3-9.fc44                        fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  pciutils                                      x86_64 0:3.14.0-3.fc44                       fedora                           287.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  pinentry-gnome3                               x86_64 0:1.3.2-3.fc44                        updates                           88.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  pinfo                                         x86_64 0:0.6.13-10.fc44                      fedora                           224.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-alsa                                 x86_64 0:1.6.4-1.fc44                        updates                          157.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-config-raop                          x86_64 0:1.6.4-1.fc44                        updates                           35.0   B[0m
[1;32m==> proxmox-clone.fedora:  pipewire-pulseaudio                           x86_64 0:1.6.4-1.fc44                        updates                          464.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-utils                                x86_64 0:1.6.4-1.fc44                        updates                            1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  plocate                                       x86_64 0:1.1.24-1.fc44                       fedora                           562.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth                                      x86_64 0:24.004.60-24.fc44                   fedora                           334.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-system-theme                         x86_64 0:24.004.60-24.fc44                   fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  policycoreutils-python-utils                  noarch 0:3.10-1.fc44                         fedora                            94.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  polkit                                        x86_64 0:127-2.fc44.2                        fedora                           493.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  psacct                                        x86_64 0:6.6.4-26.fc44                       fedora                           198.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  ptyxis                                        x86_64 0:50.1-1.fc44                         fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  qcom-wwan-firmware                            noarch 0:20260410-1.fc44                     updates                          749.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtwayland-adwaita-decoration              x86_64 0:6.10.3-1.fc44                       updates                          131.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  quota                                         x86_64 1:4.11-2.fc44                         fedora                           700.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  realmd                                        x86_64 0:0.17.1-19.fc44                      fedora                           837.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  realtek-firmware                              noarch 0:20260410-1.fc44                     updates                            6.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  rygel                                         x86_64 0:45.1-1.fc44                         fedora                             4.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  samba-client                                  x86_64 2:4.24.1-1.fc44                       updates                            2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  sane-backends-drivers-scanners                x86_64 0:1.4.0-6.fc44                        fedora                            12.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  showtime                                      noarch 0:50.0-1.fc44                         fedora                           721.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  simple-scan                                   x86_64 0:49.1-2.fc44                         fedora                             3.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  snapshot                                      x86_64 0:50.0-1.fc44                         fedora                             4.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  sos                                           noarch 0:4.11.1-1.fc44                       updates                            4.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  speech-dispatcher                             x86_64 0:0.12.1-6.fc44                       fedora                            28.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  spice-vdagent                                 x86_64 0:0.23.0-2.fc44                       fedora                           215.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  spice-webdavd                                 x86_64 0:3.0-13.fc44                         fedora                            54.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  sushi                                         x86_64 0:50~rc.1-1.fc44                      fedora                           430.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  symlinks                                      x86_64 0:1.7-14.fc44                         fedora                            21.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  system-config-printer-udev                    x86_64 0:1.5.18-17.fc44                      fedora                            49.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  tcpdump                                       x86_64 14:4.99.6-3.fc44                      fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  thermald                                      x86_64 0:2.5.9-3.fc44                        fedora                           588.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  time                                          x86_64 0:1.9-28.fc44                         fedora                            82.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  tinysparql                                    x86_64 0:3.11.1-1.fc44                       updates                            2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  tiwilink-firmware                             noarch 0:20260410-1.fc44                     updates                            4.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  toolbox                                       x86_64 0:0.3-4.fc44                          fedora                            12.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  traceroute                                    x86_64 3:2.1.6-4.fc44                        fedora                           103.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  tree                                          x86_64 0:2.2.1-4.fc44                        fedora                           120.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  unoconv                                       noarch 0:0.9.0-18.fc44                       fedora                           249.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  uresourced                                    x86_64 0:0.5.4-5.fc44                        fedora                           113.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  usb_modeswitch                                x86_64 0:2.6.2-5.fc44                        fedora                           217.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  usbutils                                      x86_64 0:019-2.fc44                          fedora                           327.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  virtualbox-guest-additions                    x86_64 0:7.2.6-1.fc44                        fedora                             3.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  vte-profile                                   x86_64 0:0.84.0-1.fc44                       fedora                            51.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  wget2-wget                                    x86_64 0:2.2.1-2.fc44                        fedora                            42.0   B[0m
[1;32m==> proxmox-clone.fedora:  whois                                         x86_64 0:5.6.6-1.fc44                        fedora                           177.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  wireplumber                                   x86_64 0:0.5.14-1.fc44                       updates                          427.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  words                                         noarch 0:3.0-63.fc44                         fedora                             4.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  wpa_supplicant                                x86_64 1:2.11-9.fc44                         fedora                             6.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-desktop-portal                            x86_64 0:1.21.1-1.fc44                       fedora                             1.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-desktop-portal-gnome                      x86_64 0:50.0-1.fc44                         fedora                           986.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-desktop-portal-gtk                        x86_64 0:1.15.3-3.fc44                       fedora                           469.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-user-dirs-gtk                             x86_64 0:0.16-2.fc44                         fedora                           222.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  yelp                                          x86_64 2:49.0-2.fc44                         fedora                             2.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  zip                                           x86_64 0:3.0-45.fc44                         fedora                           698.0 KiB[0m
[1;32m==> proxmox-clone.fedora: Installing dependencies:[0m
[1;32m==> proxmox-clone.fedora:  Box2D                                         x86_64 0:2.4.2-7.fc44                        fedora                           251.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  ImageMagick                                   x86_64 1:7.1.2.13-2.fc44                     fedora                            88.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  ImageMagick-libs                              x86_64 1:7.1.2.13-2.fc44                     fedora                             8.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  LibRaw                                        x86_64 0:0.22.1-1.fc44                       fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  ModemManager-glib                             x86_64 0:1.24.2-3.fc44                       fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-openconnect                    x86_64 0:1.2.10-11.fc44                      fedora                             3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-openvpn                        x86_64 1:1.12.5-4.fc44                       fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-ssh                            x86_64 0:1.4.4-1.fc44                        updates                          230.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-ssh-selinux                    x86_64 0:1.4.4-1.fc44                        updates                           18.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  NetworkManager-vpnc                           x86_64 1:1.4.0-6.fc44                        fedora                           545.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  PackageKit                                    x86_64 0:1.3.4-3.fc44                        fedora                             3.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  PackageKit-glib                               x86_64 0:1.3.4-3.fc44                        fedora                           532.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  SDL2_image                                    x86_64 0:2.8.8-4.fc44                        fedora                           217.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  SDL3                                          x86_64 0:3.4.4-1.fc44                        updates                            3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  abattis-cantarell-fonts                       noarch 0:0.301-17.fc44                       fedora                           525.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  abattis-cantarell-vf-fonts                    noarch 0:0.301-17.fc44                       fedora                           192.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt                                          x86_64 0:2.17.8-3.fc44                       fedora                             2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-addon-ccpp                               x86_64 0:2.17.8-3.fc44                       fedora                           282.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-addon-kerneloops                         x86_64 0:2.17.8-3.fc44                       fedora                            90.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-addon-pstoreoops                         x86_64 0:2.17.8-3.fc44                       fedora                            14.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-addon-vmcore                             x86_64 0:2.17.8-3.fc44                       fedora                            37.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-addon-xorg                               x86_64 0:2.17.8-3.fc44                       fedora                            61.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-dbus                                     x86_64 0:2.17.8-3.fc44                       fedora                           160.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-libs                                     x86_64 0:2.17.8-3.fc44                       fedora                            68.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-plugin-bodhi                             x86_64 0:2.17.8-3.fc44                       fedora                            39.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  abrt-tui                                      noarch 0:2.17.8-3.fc44                       fedora                            79.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  abseil-cpp                                    x86_64 0:20260107.1-1.fc44                   fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  accountsservice                               x86_64 0:23.13.9-16.fc44                     fedora                           375.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  accountsservice-libs                          x86_64 0:23.13.9-16.fc44                     fedora                           212.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  adobe-mappings-cmap                           noarch 0:20231115-5.fc44                     fedora                            15.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  adobe-mappings-cmap-deprecated                noarch 0:20231115-5.fc44                     fedora                           582.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  adobe-mappings-pdf                            noarch 0:20190401-12.fc44                    fedora                             4.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  adwaita-cursor-theme                          noarch 0:50.0-1.fc44                         fedora                            11.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  adwaita-icon-theme                            noarch 0:50.0-1.fc44                         fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  adwaita-icon-theme-legacy                     noarch 0:46.2-7.fc44                         fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  alsa-lib                                      x86_64 0:1.2.15.3-3.fc44                     fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  anthy-unicode                                 x86_64 0:1.0.0.20260213-1.fc44               fedora                            25.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  antiword                                      x86_64 0:0.37-44.fc44                        fedora                           642.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  appstream                                     x86_64 0:1.1.0-3.fc44                        fedora                             4.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  appstream-data                                noarch 0:44-4.fc44                           fedora                            14.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  apr                                           x86_64 0:1.7.6-5.fc44                        fedora                           303.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  apr-util                                      x86_64 0:1.6.3-27.fc44                       fedora                           220.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  apr-util-lmdb                                 x86_64 0:1.6.3-27.fc44                       fedora                            11.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  aribb24                                       x86_64 0:1.0.3^20160216git5e9be27-5.fc44     fedora                            83.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  at-spi2-core                                  x86_64 0:2.60.3-1.fc44                       updates                            1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  atk                                           x86_64 0:2.60.3-1.fc44                       updates                          252.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  atkmm                                         x86_64 0:2.28.4-7.fc44                       fedora                           372.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  augeas-libs                                   x86_64 0:1.14.2-0.11.20260408gitada6219.fc44 updates                            1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  autocorr-en                                   noarch 1:26.2.2.2-2.fc44                     updates                          284.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  avahi                                         x86_64 0:0.9~rc2-8.fc44                      fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  avahi-glib                                    x86_64 0:0.9~rc2-8.fc44                      fedora                            19.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  avahi-gobject                                 x86_64 0:0.9~rc2-8.fc44                      fedora                            48.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  avahi-libs                                    x86_64 0:0.9~rc2-8.fc44                      fedora                           179.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  bind-libs                                     x86_64 32:9.18.48-1.fc44                     updates                            3.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  binutils                                      x86_64 0:2.46-1.fc44                         fedora                            27.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  bluez                                         x86_64 0:5.86-4.fc44                         fedora                             3.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  bluez-libs                                    x86_64 0:5.86-4.fc44                         fedora                           202.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  bluez-obexd                                   x86_64 0:5.86-4.fc44                         fedora                           358.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-atomic                                  x86_64 0:1.90.0-7.fc44                       fedora                            20.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-charconv                                x86_64 0:1.90.0-7.fc44                       fedora                           161.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-chrono                                  x86_64 0:1.90.0-7.fc44                       fedora                            41.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-container                               x86_64 0:1.90.0-7.fc44                       fedora                            69.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-date-time                               x86_64 0:1.90.0-7.fc44                       fedora                            12.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-iostreams                               x86_64 0:1.90.0-7.fc44                       fedora                            90.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-locale                                  x86_64 0:1.90.0-7.fc44                       fedora                           695.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-random                                  x86_64 0:1.90.0-7.fc44                       fedora                            29.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-regex                                   x86_64 0:1.90.0-7.fc44                       fedora                           298.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  boost-thread                                  x86_64 0:1.90.0-7.fc44                       fedora                           127.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  brlapi                                        x86_64 0:0.8.7-8.fc44                        fedora                           602.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  bubblewrap                                    x86_64 0:0.11.0-4.fc44                       fedora                           134.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  cairo                                         x86_64 0:1.18.4-6.fc44                       fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  cairo-gobject                                 x86_64 0:1.18.4-6.fc44                       fedora                            31.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  cairomm                                       x86_64 0:1.14.5-15.fc44                      fedora                           203.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  cairomm1.16                                   x86_64 0:1.18.0-16.fc44                      fedora                           224.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  capstone                                      x86_64 0:5.0.6-4.fc44                        fedora                            14.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  cdparanoia-libs                               x86_64 0:10.2-50.fc44                        fedora                           113.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  cjson                                         x86_64 0:1.7.18-5.fc44                       fedora                            63.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  cldr-emoji-annotation                         noarch 1:48.2-1.fc44                         fedora                           122.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  cldr-emoji-annotation-dtd                     noarch 1:48.2-1.fc44                         fedora                           203.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  clucene-contribs-lib                          x86_64 0:2.3.3.4-55.20130812.e8e3d20git.fc44 fedora                           324.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  clucene-core                                  x86_64 0:2.3.3.4-55.20130812.e8e3d20git.fc44 fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  cmake-filesystem                              x86_64 0:4.3.0-1.fc44                        fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  codec2                                        x86_64 0:1.2.0-9.fc44                        fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  color-filesystem                              noarch 0:1-38.fc44                           fedora                           151.0   B[0m
[1;32m==> proxmox-clone.fedora:  colord-gtk4                                   x86_64 0:0.3.1-6.fc44                        fedora                            31.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  colord-libs                                   x86_64 0:1.4.8-4.fc44                        fedora                           830.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  ctags                                         x86_64 0:6.2.1-3.fc44                        fedora                             2.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  cups-client                                   x86_64 1:2.4.18-1.fc44                       updates                          177.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  cups-filesystem                               noarch 1:2.4.18-1.fc44                       updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  cups-ipptool                                  x86_64 1:2.4.18-1.fc44                       updates                            4.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  cups-libs                                     x86_64 1:2.4.18-1.fc44                       updates                          634.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  daxctl-libs                                   x86_64 0:84-1.fc44                           fedora                            86.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  dbus-tools                                    x86_64 1:1.16.2-1.fc44                       fedora                            98.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  dconf                                         x86_64 0:0.49.0-5.fc44                       fedora                           306.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-am                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ar                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-as                              noarch 0:4.3-1.fc44                          fedora                           348.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ast                             noarch 0:4.3-1.fc44                          fedora                           349.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-be                              noarch 0:4.3-1.fc44                          fedora                           352.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-bg                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-bn                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-bo                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-br                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-chr                             noarch 0:4.3-1.fc44                          fedora                           349.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-dv                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-dz                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-el                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-eo                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-eu                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-fa                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-got                             noarch 0:4.3-1.fc44                          fedora                           345.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-gu                              noarch 0:4.3-1.fc44                          fedora                           348.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-he                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-hi                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-hy                              noarch 0:4.3-1.fc44                          fedora                           348.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ia                              noarch 0:4.3-1.fc44                          fedora                           354.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ii                              noarch 0:4.3-1.fc44                          fedora                           352.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-iu                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ka                              noarch 0:4.3-1.fc44                          fedora                           348.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-kab                             noarch 0:4.3-1.fc44                          fedora                           345.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-km                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-kn                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ku                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-lo                              noarch 0:4.3-1.fc44                          fedora                           338.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-mai                             noarch 0:4.3-1.fc44                          fedora                           349.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ml                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-mni                             noarch 0:4.3-1.fc44                          fedora                           349.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-mr                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-my                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-nb                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ne                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-nn                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-nqo                             noarch 0:4.3-1.fc44                          fedora                           341.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-nr                              noarch 0:4.3-1.fc44                          fedora                           364.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-nso                             noarch 0:4.3-1.fc44                          fedora                           361.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-or                              noarch 0:4.3-1.fc44                          fedora                           340.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-pa                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ru                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-sat                             noarch 0:4.3-1.fc44                          fedora                           347.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-si                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ss                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-syr                             noarch 0:4.3-1.fc44                          fedora                           345.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ta                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-te                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-th                              noarch 0:4.3-1.fc44                          fedora                           340.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-tn                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ts                              noarch 0:4.3-1.fc44                          fedora                           344.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-uk                              noarch 0:4.3-1.fc44                          fedora                           350.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ur                              noarch 0:4.3-1.fc44                          fedora                           340.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-ve                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-vi                              noarch 0:4.3-1.fc44                          fedora                           352.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-xh                              noarch 0:4.3-1.fc44                          fedora                           342.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-yi                              noarch 0:4.3-1.fc44                          fedora                           346.0   B[0m
[1;32m==> proxmox-clone.fedora:  default-fonts-zu                              noarch 0:4.3-1.fc44                          fedora                           340.0   B[0m
[1;32m==> proxmox-clone.fedora:  desktop-file-utils                            x86_64 0:0.28-5.fc44                         fedora                           218.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  device-mapper-multipath-libs                  x86_64 0:0.13.1-1.fc44                       fedora                           902.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  distribution-gpg-keys                         noarch 0:1.119-1.fc44                        updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  djvulibre-libs                                x86_64 0:3.5.28-16.fc44                      fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  dmidecode                                     x86_64 1:3.6-9.fc44                          fedora                           230.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  dnf5daemon-server                             x86_64 0:5.4.1.0-1.fc44                      fedora                           764.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  dnf5daemon-server-polkit                      noarch 0:5.4.1.0-1.fc44                      fedora                           326.0   B[0m
[1;32m==> proxmox-clone.fedora:  dotconf                                       x86_64 0:1.4.1-7.fc44                        fedora                            58.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  double-conversion                             x86_64 0:3.4.0-3.fc44                        fedora                           101.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  duktape                                       x86_64 0:2.7.0-11.fc44                       fedora                           623.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  editorconfig-libs                             x86_64 0:0.12.10-1.fc44                      fedora                            38.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  edk2-ovmf                                     noarch 0:20260213-6.fc44                     updates                           45.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  elfutils                                      x86_64 0:0.195-1.fc44                        updates                            3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  emacs-filesystem                              x86_64 1:30.2-2.fc44                         fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  enchant2                                      x86_64 0:2.8.15-1.fc44                       fedora                           218.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  epiphany-runtime                              x86_64 1:50.3-1.fc44                         updates                            6.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  espeak-ng                                     x86_64 0:1.52.0-3.fc44                       fedora                            24.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  evince-libs                                   x86_64 0:48.1-2.fc44                         fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  evolution-data-server                         x86_64 0:3.60.1-1.fc44                       updates                            8.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  evolution-data-server-langpacks               noarch 0:3.60.1-1.fc44                       updates                            9.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  evolution-ews-langpacks                       noarch 0:3.60.1-1.fc44                       updates                            1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  exempi                                        x86_64 0:2.6.4-9.fc44                        fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  exiv2-libs                                    x86_64 0:0.28.6-3.fc44                       fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  f44-backgrounds-base                          noarch 0:44.0.0-1.fc44                       fedora                             9.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  f44-backgrounds-gnome                         noarch 0:44.0.0-1.fc44                       fedora                           706.0   B[0m
[1;32m==> proxmox-clone.fedora:  faad2-libs                                    x86_64 1:2.11.2-6.fc44                       fedora                           618.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  fdk-aac-free                                  x86_64 0:2.0.3-2.fc44                        fedora                           628.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-logos                                  noarch 0:42.0.1-3.fc44                       fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-logos-httpd                            noarch 0:42.0.1-3.fc44                       fedora                            12.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-third-party                            noarch 0:0.10-16.fc44                        fedora                            78.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  fftw-libs-double                              x86_64 0:3.3.10-17.fc44                      fedora                             3.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  fftw-libs-single                              x86_64 0:3.3.10-17.fc44                      fedora                             3.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  firewalld-filesystem                          noarch 0:2.4.0-2.fc44                        fedora                           239.0   B[0m
[1;32m==> proxmox-clone.fedora:  flac-libs                                     x86_64 0:1.5.0-8.fc44                        fedora                           627.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  flashrom                                      x86_64 0:1.6.0-3.fc44                        fedora                             7.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  flatpak                                       x86_64 0:1.17.6-1.fc44                       fedora                             8.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  flatpak-libs                                  x86_64 0:1.17.6-1.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  flatpak-selinux                               noarch 0:1.17.6-1.fc44                       fedora                            13.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  flatpak-session-helper                        x86_64 0:1.17.6-1.fc44                       fedora                            99.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  flite                                         x86_64 0:2.2-13.fc44                         fedora                            21.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  folks                                         x86_64 1:0.15.12-1.fc44                      fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  fontconfig                                    x86_64 0:2.17.0-4.fc44                       fedora                           776.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  fonts-filesystem                              noarch 1:5.0.0-2.fc44                        fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  fprintd                                       x86_64 0:1.94.5-5.fc44                       fedora                           829.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  freeglut                                      x86_64 0:3.8.0-2.fc44                        fedora                           485.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  freerdp-libs                                  x86_64 2:3.24.2-1.fc44                       fedora                             3.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  fribidi                                       x86_64 0:1.0.16-4.fc44                       fedora                           190.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  fstrm                                         x86_64 0:0.6.1-14.fc44                       fedora                            50.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  fwupd                                         x86_64 0:2.1.1-1.fc44                        fedora                            10.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  game-music-emu                                x86_64 0:0.6.4-3.fc44                        fedora                           360.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  gcr                                           x86_64 0:4.4.0.1-7.fc44                      fedora                           133.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gcr-libs                                      x86_64 0:4.4.0.1-7.fc44                      fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gcr3                                          x86_64 0:3.41.1-12.fc44                      fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  gcr3-base                                     x86_64 0:3.41.1-12.fc44                      fedora                           810.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gd                                            x86_64 0:2.3.3-21.fc44                       fedora                           411.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gdb-headless                                  x86_64 0:17.1-4.fc44                         fedora                            16.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gdk-pixbuf2                                   x86_64 0:2.44.4-2.fc44                       fedora                             2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gdm                                           x86_64 1:50.0-1.fc44                         fedora                             5.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  genisoimage                                   x86_64 0:1.1.11-63.fc44                      fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  geoclue2                                      x86_64 0:2.8.0-2.fc44                        fedora                           405.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  geoclue2-libs                                 x86_64 0:2.8.0-2.fc44                        fedora                           167.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  geocode-glib                                  x86_64 0:3.26.4-15.fc44                      fedora                           226.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gettext                                       x86_64 0:0.26-4.fc44                         fedora                            12.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  ghostscript-tools-fontutils                   noarch 0:10.06.0-2.fc44                      fedora                             2.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  ghostscript-tools-printing                    noarch 0:10.06.0-2.fc44                      fedora                             3.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  giflib                                        x86_64 0:6.1.3-1.fc44                        updates                          122.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  git-core                                      x86_64 0:2.54.0-1.fc44                       updates                           25.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  git-core-doc                                  noarch 0:2.54.0-1.fc44                       updates                           18.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  gjs                                           x86_64 0:1.88.0-1.fc44                       fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  glibmm2.4                                     x86_64 0:2.66.8-3.fc44                       fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  glibmm2.68                                    x86_64 0:2.88.0-1.fc44                       fedora                             3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  glusterfs                                     x86_64 0:11.2-5.fc44                         fedora                             2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  glusterfs-cli                                 x86_64 0:11.2-5.fc44                         fedora                           472.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  glusterfs-client-xlators                      x86_64 0:11.2-5.fc44                         fedora                             3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  glusterfs-fuse                                x86_64 0:11.2-5.fc44                         fedora                           528.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  glx-utils                                     x86_64 0:9.0.0-11.fc44                       fedora                           418.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  glycin-gtk4-libs                              x86_64 0:2.1.1-1.fc44                        fedora                           287.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  glycin-libs                                   x86_64 0:2.1.1-1.fc44                        fedora                             4.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  glycin-loaders                                x86_64 0:2.1.1-1.fc44                        fedora                            14.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-app-list                                noarch 0:3.0-4.fc44                          fedora                            74.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-autoar                                  x86_64 0:0.4.5-4.fc44                        fedora                           150.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-bluetooth-libs                          x86_64 1:47.2-1.fc44                         updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-control-center-filesystem               noarch 0:50.1-1.fc44                         updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  gnome-desktop3                                x86_64 0:44.5-1.fc44                         fedora                             3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-desktop4                                x86_64 0:44.5-1.fc44                         fedora                           471.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-keyring                                 x86_64 0:50.0-1.fc44                         fedora                             3.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-keyring-pam                             x86_64 0:50.0-1.fc44                         fedora                            31.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-menus                                   x86_64 0:3.38.1-2.fc44                       fedora                           638.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-online-accounts                         x86_64 0:3.58.1-1.fc44                       updates                            1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-online-accounts-libs                    x86_64 0:3.58.1-1.fc44                       updates                          762.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-session                                 x86_64 0:50.0-1.fc44                         fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-common                            noarch 0:50.1-2.fc44                         updates                           16.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-apps-menu               noarch 0:50.1-1.fc44                         updates                           22.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-common                  noarch 0:50.1-1.fc44                         updates                          621.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-launch-new-instance     noarch 0:50.1-1.fc44                         updates                            1.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-places-menu             noarch 0:50.1-1.fc44                         updates                           20.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-shell-extension-window-list             noarch 0:50.1-1.fc44                         updates                           85.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnutls-dane                                   x86_64 0:3.8.12-1.fc44                       fedora                            60.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnutls-utils                                  x86_64 0:3.8.12-1.fc44                       fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gobject-introspection                         x86_64 0:1.86.0-3.fc44                       fedora                           397.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-carlito-fonts                          noarch 0:1.103-0.28.20130920.fc44            fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-crosextra-caladea-fonts                noarch 1:1.002-0.22.20130214.fc44            fedora                           251.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-droid-sans-fonts                       noarch 0:20200215-24.fc44                    fedora                             6.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-color-emoji-fonts                 noarch 0:20250623-4.fc44                     fedora                             4.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-fonts-common                      noarch 0:20251201-2.fc44                     fedora                            17.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-naskh-arabic-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           250.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-arabic-vf-fonts              noarch 0:20251201-2.fc44                     fedora                           235.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-armenian-vf-fonts            noarch 0:20251201-2.fc44                     fedora                            33.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-bengali-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           164.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-canadian-aboriginal-vf-fonts noarch 0:20251201-2.fc44                     fedora                           156.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-cherokee-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           133.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-cjk-vf-fonts                 noarch 1:2.004-11.fc44                       fedora                            31.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-devanagari-vf-fonts          noarch 0:20251201-2.fc44                     fedora                           279.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-ethiopic-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           508.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-georgian-vf-fonts            noarch 0:20251201-2.fc44                     fedora                            57.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-gothic-fonts                 noarch 0:20251201-2.fc44                     fedora                            13.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-gujarati-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           197.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-gurmukhi-vf-fonts            noarch 0:20251201-2.fc44                     fedora                            48.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-hebrew-vf-fonts              noarch 0:20251201-2.fc44                     fedora                            27.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-kannada-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           181.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-khmer-vf-fonts               noarch 0:20251201-2.fc44                     fedora                           118.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-lao-vf-fonts                 noarch 0:20251201-2.fc44                     fedora                            34.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-math-fonts                   noarch 0:20251201-2.fc44                     fedora                           969.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-meetei-mayek-vf-fonts        noarch 0:20251201-2.fc44                     fedora                            29.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-mono-cjk-vf-fonts            noarch 1:2.004-11.fc44                       fedora                            30.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-mono-vf-fonts                noarch 0:20251201-2.fc44                     fedora                           561.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-nko-fonts                    noarch 0:20251201-2.fc44                     fedora                            40.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-ol-chiki-vf-fonts            noarch 0:20251201-2.fc44                     fedora                            26.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-oriya-vf-fonts               noarch 0:20251201-2.fc44                     fedora                           199.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-sinhala-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           166.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-symbols-2-fonts              noarch 0:20251201-2.fc44                     fedora                           657.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-symbols-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           236.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-syriac-vf-fonts              noarch 0:20251201-2.fc44                     fedora                            85.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-tamil-vf-fonts               noarch 0:20251201-2.fc44                     fedora                            78.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-telugu-vf-fonts              noarch 0:20251201-2.fc44                     fedora                           229.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-thaana-vf-fonts              noarch 0:20251201-2.fc44                     fedora                            29.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-thai-vf-fonts                noarch 0:20251201-2.fc44                     fedora                            33.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-vf-fonts                     noarch 0:20251201-2.fc44                     fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-sans-yi-fonts                     noarch 0:20251201-2.fc44                     fedora                           180.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-armenian-vf-fonts           noarch 0:20251201-2.fc44                     fedora                            33.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-bengali-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           356.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-cjk-vf-fonts                noarch 1:2.003-4.fc44                        fedora                            54.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-devanagari-vf-fonts         noarch 0:20251201-2.fc44                     fedora                           293.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-ethiopic-vf-fonts           noarch 0:20251201-2.fc44                     fedora                           421.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-georgian-vf-fonts           noarch 0:20251201-2.fc44                     fedora                            75.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-gujarati-vf-fonts           noarch 0:20251201-2.fc44                     fedora                           170.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-gurmukhi-vf-fonts           noarch 0:20251201-2.fc44                     fedora                            54.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-hebrew-vf-fonts             noarch 0:20251201-2.fc44                     fedora                            32.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-kannada-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           232.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-khmer-vf-fonts              noarch 0:20251201-2.fc44                     fedora                           168.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-lao-vf-fonts                noarch 0:20251201-2.fc44                     fedora                            44.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-oriya-vf-fonts              noarch 0:20251201-2.fc44                     fedora                           189.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-sinhala-vf-fonts            noarch 0:20251201-2.fc44                     fedora                           341.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-tamil-vf-fonts              noarch 0:20251201-2.fc44                     fedora                           176.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-telugu-vf-fonts             noarch 0:20251201-2.fc44                     fedora                           329.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-thai-vf-fonts               noarch 0:20251201-2.fc44                     fedora                            42.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-serif-vf-fonts                    noarch 0:20251201-2.fc44                     fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  gperftools-libs                               x86_64 0:2.18.1-1.fc44                       fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gpgmepp                                       x86_64 0:2.0.1-3.fc44                        fedora                           441.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  graphene                                      x86_64 0:1.10.8-4.fc44                       fedora                           158.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  graphviz-libs                                 x86_64 0:14.1.4-2.fc44                       updates                            1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gsettings-desktop-schemas                     x86_64 0:50.1-1.fc44                         updates                            6.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gsm                                           x86_64 0:1.0.24-2.fc44                       fedora                            65.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gsound                                        x86_64 0:1.0.3-12.fc44                       fedora                            81.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  gspell                                        x86_64 0:1.14.3-1.fc44                       fedora                           352.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gssdp                                         x86_64 0:1.6.4-6.fc44                        fedora                           150.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  gssproxy                                      x86_64 0:0.9.2-10.fc44                       fedora                           268.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  gst-editing-services                          x86_64 0:1.28.2-1.fc44                       updates                            1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1                                    x86_64 0:1.28.2-1.fc44                       updates                            5.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugin-gtk4                        x86_64 0:0.15.0-1.fc44                       fedora                           817.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-bad-free-libs              x86_64 0:1.28.2-1.fc44                       updates                            3.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-base                       x86_64 0:1.28.2-1.fc44                       updates                            7.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-good-gtk                   x86_64 0:1.28.2-1.fc44                       updates                           64.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  gtk-update-icon-cache                         x86_64 0:3.24.52-1.fc44                      fedora                            62.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  gtk-vnc2                                      x86_64 0:1.5.0-4.fc44                        fedora                           227.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gtk3                                          x86_64 0:3.24.52-1.fc44                      fedora                            22.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gtk4                                          x86_64 0:4.22.4-1.fc44                       updates                           28.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gtkmm3.0                                      x86_64 0:3.24.10-3.fc44                      fedora                             5.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  gtkmm4.0                                      x86_64 0:4.22.0-1.fc44                       fedora                             5.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gtksourceview4                                x86_64 0:4.8.4-11.fc44                       fedora                             4.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  gtksourceview5                                x86_64 0:5.20.0-1.fc44                       fedora                             4.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  gupnp                                         x86_64 0:1.6.9-3.fc44                        fedora                           311.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gupnp-av                                      x86_64 0:0.14.4-4.fc44                       fedora                           361.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gupnp-dlna                                    x86_64 0:0.12.0-12.fc44                      fedora                           351.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  gupnp-igd                                     x86_64 0:1.6.0-8.fc44                        fedora                            66.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gutenprint                                    x86_64 0:5.3.5-7.fc44                        fedora                            29.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gutenprint-libs                               x86_64 0:5.3.5-7.fc44                        fedora                           350.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs                                          x86_64 0:1.60.0-1.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gvfs-client                                   x86_64 0:1.60.0-1.fc44                       fedora                             4.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  gvnc                                          x86_64 0:1.5.0-4.fc44                        fedora                           242.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  gvncpulse                                     x86_64 0:1.5.0-4.fc44                        fedora                            45.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  gweather-locations                            x86_64 0:2026.2-1.fc44                       fedora                            20.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  gweather-locations-common                     noarch 0:2026.2-1.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  harfbuzz-icu                                  x86_64 0:14.1.0-2.fc44                       updates                           15.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  hdparm                                        x86_64 0:9.65-10.fc44                        fedora                           184.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  hicolor-icon-theme                            noarch 0:0.18-3.fc44                         fedora                            72.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  hidapi                                        x86_64 0:0.15.0-3.fc44                       fedora                           110.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  highway                                       x86_64 0:1.3.0-2.fc44                        fedora                             5.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  hplip-common                                  x86_64 0:3.25.8-2.fc44                       fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  hplip-libs                                    x86_64 0:3.25.8-2.fc44                       fedora                           444.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  httpd                                         x86_64 0:2.4.66-4.fc44                       fedora                            56.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  httpd-core                                    x86_64 0:2.4.66-4.fc44                       fedora                             4.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  httpd-filesystem                              noarch 0:2.4.66-4.fc44                       fedora                           464.0   B[0m
[1;32m==> proxmox-clone.fedora:  httpd-tools                                   x86_64 0:2.4.66-4.fc44                       fedora                           197.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell                                      x86_64 0:1.7.2-11.fc44                       fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-en-AU                                noarch 0:0.20260225-2.fc44                   updates                          502.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-en-CA                                noarch 0:0.20260225-2.fc44                   updates                          499.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-en-GB                                noarch 0:0.20260225-2.fc44                   updates                          543.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-en-US                                noarch 0:0.20260225-2.fc44                   updates                          506.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-filesystem                           x86_64 0:1.7.2-11.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  hwdata                                        noarch 0:0.406-1.fc44                        updates                            9.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  hyperv-daemons-license                        noarch 0:6.10-3.fc44                         fedora                            18.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  hypervfcopyd                                  x86_64 0:6.10-3.fc44                         fedora                            20.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  hypervkvpd                                    x86_64 0:6.10-3.fc44                         fedora                            36.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  hypervvssd                                    x86_64 0:6.10-3.fc44                         fedora                            19.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  hyphen                                        x86_64 0:2.8.8-28.fc44                       fedora                            51.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  hyphen-en                                     noarch 0:2.8.8-28.fc44                       fedora                           103.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus                                          x86_64 0:1.5.34-1.fc44                       updates                          149.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-anthy-python                             noarch 0:1.5.18-1.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-libs                                     x86_64 0:1.5.34-1.fc44                       updates                          855.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  igvm-libs                                     x86_64 0:0.4.0-9.fc44                        fedora                           475.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  iio-sensor-proxy                              x86_64 0:3.8-2.fc44                          fedora                           156.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  ilbc                                          x86_64 0:3.0.4-19.fc44                       fedora                            91.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  imath                                         x86_64 0:3.1.12-6.fc44                       fedora                           379.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  inih-cpp                                      x86_64 0:62-2.fc44                           fedora                            40.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  intel-gmmlib                                  x86_64 0:22.10.0-1.fc44                      fedora                           892.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  iproute-tc                                    x86_64 0:6.17.0-2.fc44                       fedora                           927.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  ipset-libs                                    x86_64 0:7.24-3.fc44                         fedora                           212.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  ipxe-roms-qemu                                noarch 0:20240119-5.gitde8a0821.fc44         fedora                             2.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  iscsi-initiator-utils                         x86_64 0:6.2.1.11-0.git4b3e853.fc44.3        fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  iscsi-initiator-utils-iscsiuio                x86_64 0:6.2.1.11-0.git4b3e853.fc44.3        fedora                           167.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  isns-utils-libs                               x86_64 0:0.103-4.fc44                        fedora                           507.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  iso-codes                                     noarch 0:4.20.1-3.fc44                       fedora                            22.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  iw                                            x86_64 0:6.17-2.fc44                         fedora                           293.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  iwlwifi-mld-firmware                          noarch 0:20260410-1.fc44                     updates                           17.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  java-25-openjdk-crypto-adapter                x86_64 1:25.0.3.0.9-1.fc44                   updates                          506.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  java-25-openjdk-headless                      x86_64 1:25.0.3.0.9-1.fc44                   updates                          236.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  javapackages-filesystem                       noarch 0:6.4.1-10.fc44                       fedora                             2.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  javascriptcoregtk4.1                          x86_64 0:2.52.3-1.fc44                       updates                           32.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  javascriptcoregtk6.0                          x86_64 0:2.52.3-1.fc44                       updates                           32.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  jbig2dec-libs                                 x86_64 0:0.20-8.fc44                         fedora                           168.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  jbigkit-libs                                  x86_64 0:2.1-33.fc44                         fedora                           117.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  jomolhari-fonts                               noarch 0:0.003-45.fc44                       fedora                             2.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  json-glib                                     x86_64 0:1.10.8-5.fc44                       fedora                           596.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  jxrlib                                        x86_64 0:1.1-33.fc44                         fedora                           763.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  kasumi-common                                 noarch 0:2.5-50.fc44                         fedora                             8.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  kasumi-unicode                                x86_64 0:2.5-50.fc44                         fedora                           170.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  kde-filesystem                                x86_64 0:5-7.fc44                            fedora                           774.0   B[0m
[1;32m==> proxmox-clone.fedora:  kernel-tools-libs                             x86_64 0:6.19.14-300.fc44                    updates                           30.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  kexec-tools                                   x86_64 0:2.0.32-3.fc44                       fedora                           237.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  keyutils                                      x86_64 0:1.6.3-7.fc44                        fedora                           150.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  kf6-filesystem                                x86_64 0:6.25.0-1.fc44                       fedora                             1.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  kf6-karchive                                  x86_64 0:6.25.0-1.fc44                       fedora                           822.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  kf6-kimageformats                             x86_64 0:6.25.0-2.fc44                       fedora                             3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  kyotocabinet-libs                             x86_64 0:1.2.80-9.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  lame-libs                                     x86_64 0:3.100-21.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  langpacks-core-en                             noarch 0:4.3-1.fc44                          fedora                           398.0   B[0m
[1;32m==> proxmox-clone.fedora:  langpacks-fonts-en                            noarch 0:4.3-1.fc44                          fedora                           341.0   B[0m
[1;32m==> proxmox-clone.fedora:  langtable                                     noarch 0:0.0.70-1.fc44                       fedora                           242.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  lcms2                                         x86_64 0:2.16-7.fc44                         fedora                           445.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  leptonica                                     x86_64 0:1.87.0-3.fc44                       fedora                             3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libICE                                        x86_64 0:1.1.2-4.fc44                        fedora                           198.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libSM                                         x86_64 0:1.2.5-4.fc44                        fedora                           100.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libX11                                        x86_64 0:1.8.13-1.fc44                       fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libX11-common                                 noarch 0:1.8.13-1.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libX11-xcb                                    x86_64 0:1.8.13-1.fc44                       fedora                            10.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXau                                        x86_64 0:1.0.12-4.fc44                       fedora                            72.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXcomposite                                 x86_64 0:0.4.6-7.fc44                        fedora                            40.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXcursor                                    x86_64 0:1.2.3-4.fc44                        fedora                            53.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXdamage                                    x86_64 0:1.1.6-7.fc44                        fedora                            39.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXdmcp                                      x86_64 0:1.1.5-5.fc44                        fedora                            82.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXext                                       x86_64 0:1.3.6-5.fc44                        fedora                            89.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXfixes                                     x86_64 0:6.0.1-7.fc44                        fedora                            34.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXfont2                                     x86_64 0:2.0.7-4.fc44                        fedora                           338.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXft                                        x86_64 0:2.3.8-10.fc44                       fedora                           168.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXi                                         x86_64 0:1.8.2-4.fc44                        fedora                            80.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXinerama                                   x86_64 0:1.1.5-10.fc44                       fedora                            14.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXmu                                        x86_64 0:1.2.1-5.fc44                        fedora                           191.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXpm                                        x86_64 0:3.5.17-7.fc44                       fedora                           148.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXrandr                                     x86_64 0:1.5.4-7.fc44                        fedora                            55.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXrender                                    x86_64 0:0.9.12-4.fc44                       fedora                            49.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXres                                       x86_64 0:1.2.2-7.fc44                        fedora                            20.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXt                                         x86_64 0:1.3.1-4.fc44                        fedora                           437.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXtst                                       x86_64 0:1.2.5-4.fc44                        fedora                            33.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXv                                         x86_64 0:1.0.13-4.fc44                       fedora                            25.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libXxf86vm                                    x86_64 0:1.1.6-4.fc44                        fedora                            25.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  liba52                                        x86_64 0:0.7.4-53.fc44                       fedora                            86.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libabw                                        x86_64 0:0.1.3-19.fc44                       fedora                           277.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libadwaita                                    x86_64 0:1.9.0-1.fc44                        fedora                             3.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libao                                         x86_64 0:1.2.0-31.fc44                       fedora                           127.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libaom                                        x86_64 0:3.13.3-1.fc44                       updates                            5.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libargon2                                     x86_64 0:20190702-10.fc44                    fedora                            48.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libaribcaption                                x86_64 0:1.1.1-4.fc44                        fedora                           260.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libass                                        x86_64 0:0.17.4-2.fc44                       fedora                           290.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libasyncns                                    x86_64 0:0.8-32.fc44                         fedora                            55.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libatasmart                                   x86_64 0:0.19-32.fc44                        fedora                           114.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libatomic                                     x86_64 0:16.0.1-0.10.fc44                    fedora                            45.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libavc1394                                    x86_64 0:0.5.4-27.fc44                       fedora                           134.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libavcodec-free                               x86_64 0:8.0.1-6.fc44                        fedora                            10.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  libavdevice-free                              x86_64 0:8.0.1-6.fc44                        fedora                           190.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libavfilter-free                              x86_64 0:8.0.1-6.fc44                        fedora                             4.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libavformat-free                              x86_64 0:8.0.1-6.fc44                        fedora                             2.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libavif                                       x86_64 0:1.3.0-4.fc44                        fedora                           265.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libavutil-free                                x86_64 0:8.0.1-6.fc44                        fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libb2                                         x86_64 0:0.98.1-15.fc44                      fedora                            41.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libbabeltrace                                 x86_64 0:1.5.11-17.fc44                      fedora                           522.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblkio                                      x86_64 0:1.5.0-5.fc44                        fedora                           764.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev                                   x86_64 0:3.5.0-1.fc44                        updates                          389.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-crypto                            x86_64 0:3.5.0-1.fc44                        updates                           67.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-fs                                x86_64 0:3.5.0-1.fc44                        updates                          108.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-loop                              x86_64 0:3.5.0-1.fc44                        updates                           19.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-mdraid                            x86_64 0:3.5.0-1.fc44                        updates                           31.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-nvme                              x86_64 0:3.5.0-1.fc44                        updates                           47.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-part                              x86_64 0:3.5.0-1.fc44                        updates                           43.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-smart                             x86_64 0:3.5.0-1.fc44                        updates                           43.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-swap                              x86_64 0:3.5.0-1.fc44                        updates                           19.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libblockdev-utils                             x86_64 0:3.5.0-1.fc44                        updates                           43.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libbluray                                     x86_64 0:1.4.0-3.fc44                        fedora                           318.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libbs2b                                       x86_64 0:3.1.0-37.fc44                       fedora                            63.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libbytesize                                   x86_64 0:2.12-2.fc44                         fedora                            87.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcaca                                       x86_64 0:0.99-0.82.beta20.fc44               fedora                           869.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcacard                                     x86_64 3:2.8.2-1.fc44                        fedora                           123.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcamera                                     x86_64 0:0.7.0-1.fc44                        fedora                             2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  libcanberra                                   x86_64 0:0.30-39.fc44                        fedora                           265.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcanberra-gtk3                              x86_64 0:0.30-39.fc44                        fedora                            70.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcdio                                       x86_64 0:2.3.0-1.fc44                        fedora                           592.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcdio-paranoia                              x86_64 0:10.2+2.0.2-6.fc44                   fedora                           178.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcdr                                        x86_64 0:0.1.8-5.fc44                        fedora                           890.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libchewing                                    x86_64 0:0.11.0-2.fc44                       fedora                             7.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  libchromaprint                                x86_64 0:1.6.0-4.fc44                        fedora                            69.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcloudproviders                             x86_64 0:0.4.0-1.fc44                        fedora                           124.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcmis                                       x86_64 0:0.6.2-11.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libcue                                        x86_64 0:2.3.0-14.fc44                       fedora                            85.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcupsfilters                                x86_64 1:2.1.1-7.fc44                        fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libdaemon                                     x86_64 0:0.14-33.fc44                        fedora                            64.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdatrie                                     x86_64 0:0.2.14-2.fc44                       fedora                            61.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdav1d                                      x86_64 0:1.5.3-1.fc44                        fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  libdc1394                                     x86_64 0:2.2.7-9.fc44                        fedora                           354.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdecor                                      x86_64 0:0.2.5-2.fc44                        fedora                           168.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdeflate                                    x86_64 0:1.25-3.fc44                         fedora                           119.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdisplay-info                               x86_64 0:0.3.0-1.fc44                        fedora                           226.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdnf5-plugin-appstream                      x86_64 0:5.4.1.0-1.fc44                      fedora                            32.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdovi                                       x86_64 0:3.3.2-2.fc44                        fedora                           593.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdrm                                        x86_64 0:2.4.133-1.fc44                      updates                          405.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdvdnav                                     x86_64 0:7.0.0-1.fc44                        fedora                           124.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libdvdread                                    x86_64 0:7.0.1-1.fc44                        fedora                           182.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libe-book                                     x86_64 0:0.1.3-41.fc44                       fedora                           461.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libebur128                                    x86_64 0:1.2.6-15.fc44                       fedora                            39.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libei                                         x86_64 0:1.5.0-2.fc44                        fedora                           115.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libeis                                        x86_64 0:1.5.0-2.fc44                        fedora                           115.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libeot                                        x86_64 0:0.01-35.fc44                        fedora                            77.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libepoxy                                      x86_64 0:1.5.10-12.fc44                      fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libepubgen                                    x86_64 0:0.1.1-22.fc44                       fedora                           383.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  liberation-mono-fonts                         noarch 1:2.1.5-15.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  liberation-sans-fonts                         noarch 1:2.1.5-15.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  liberation-serif-fonts                        noarch 1:2.1.5-15.fc44                       fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  libetonyek                                    x86_64 0:0.1.13-2.fc44                       fedora                             2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libev                                         x86_64 0:4.33-15.fc44                        fedora                           105.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libevdev                                      x86_64 0:1.13.6-2.fc44                       fedora                            89.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libexif                                       x86_64 0:0.6.26-1.fc44                       fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  libexttextcat                                 x86_64 0:3.4.6-13.fc44                       fedora                           453.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libfdt                                        x86_64 0:1.7.2-9.fc44                        fedora                            61.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libfontenc                                    x86_64 0:1.1.8-5.fc44                        fedora                            66.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libfprint                                     x86_64 0:1.94.10-1.fc44                      fedora                           852.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libfreehand                                   x86_64 0:0.1.2-27.fc44                       fedora                           461.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libftdi                                       x86_64 0:1.5-22.fc44                         fedora                            93.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libfyaml                                      x86_64 0:0.8-9.fc44                          fedora                           490.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgee                                        x86_64 0:0.20.8-3.fc44                       fedora                           952.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgexiv2                                     x86_64 0:0.16.0-2.fc44                       fedora                           267.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgfapi0                                     x86_64 0:11.2-5.fc44                         fedora                           230.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgfrpc0                                     x86_64 0:11.2-5.fc44                         fedora                           224.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgfxdr0                                     x86_64 0:11.2-5.fc44                         fedora                            50.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libglusterfs0                                 x86_64 0:11.2-5.fc44                         fedora                           922.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libglvnd                                      x86_64 1:1.7.0-9.fc44                        fedora                           526.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libglvnd-egl                                  x86_64 1:1.7.0-9.fc44                        fedora                            68.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libglvnd-glx                                  x86_64 1:1.7.0-9.fc44                        fedora                           601.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libglvnd-opengl                               x86_64 1:1.7.0-9.fc44                        fedora                           144.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgphoto2                                    x86_64 0:2.5.33-2.fc44                       fedora                             6.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libgs                                         x86_64 0:10.06.0-2.fc44                      fedora                            24.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libgsf                                        x86_64 0:1.14.56-1.fc44                      fedora                           988.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgtop2                                      x86_64 0:2.41.3-5.fc44                       fedora                           497.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgudev                                      x86_64 0:238-9.fc44                          fedora                            91.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgusb                                       x86_64 0:0.4.9-5.fc44                        fedora                           157.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libgweather                                   x86_64 0:4.6.0-1.fc44                        fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libgxps                                       x86_64 0:0.3.2-12.fc44                       fedora                           192.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libhandy                                      x86_64 0:1.8.3-10.fc44                       fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libhangul                                     x86_64 0:0.2.0-3.fc44                        fedora                             6.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libheif                                       x86_64 0:1.21.2-1.fc44                       fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libibverbs                                    x86_64 0:61.0-2.fc44                         fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libical                                       x86_64 0:3.0.20-7.fc44                       fedora                           966.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libical-glib                                  x86_64 0:3.0.20-7.fc44                       fedora                           570.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libicu                                        x86_64 0:77.1-2.fc44                         fedora                            36.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libiec61883                                   x86_64 0:1.2.0-39.fc44                       fedora                            85.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libieee1284                                   x86_64 0:0.2.11-48.fc44                      fedora                            85.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libijs                                        x86_64 0:0.35-26.fc44                        fedora                            61.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libimagequant                                 x86_64 0:4.1.0-2.fc44                        fedora                           707.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libimobiledevice                              x86_64 0:1.3.0^20240916gited9703d-7.fc44     fedora                           316.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libimobiledevice-glue                         x86_64 0:1.3.1-4.fc44                        fedora                           122.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libinput                                      x86_64 0:1.31.1-1.fc44                       updates                          695.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libipt                                        x86_64 0:2.1.2-4.fc44                        fedora                           125.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libiscsi                                      x86_64 0:1.20.3-4.fc44                       fedora                           251.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libjaylink                                    x86_64 0:0.3.0-10.fc44                       fedora                            89.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libjcat                                       x86_64 0:0.2.6-1.fc44                        updates                          213.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libjpeg-turbo                                 x86_64 0:3.1.3-1.fc44                        fedora                           818.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libjxl                                        x86_64 1:0.11.1-8.fc44                       fedora                             4.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  liblangtag                                    x86_64 0:0.6.7-7.fc44                        fedora                           209.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblangtag-data                               noarch 0:0.6.7-7.fc44                        fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  liblc3                                        x86_64 0:1.1.3-7.fc44                        fedora                           174.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libldac                                       x86_64 0:2.0.2.3-19.fc44                     fedora                            78.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblerc                                       x86_64 0:4.0.0-10.fc44                       fedora                           647.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblouis                                      x86_64 0:3.33.0-7.fc44                       fedora                           484.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblouis-tables                               noarch 0:3.33.0-7.fc44                       fedora                            12.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  liblouisutdml                                 x86_64 0:2.12.0-8.fc44                       fedora                           422.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblouisutdml-utils                           x86_64 0:2.12.0-8.fc44                       fedora                            54.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  liblqr-1                                      x86_64 0:0.4.2-29.fc44                       fedora                           101.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmanette                                    x86_64 0:0.2.13-2.fc44                       fedora                           367.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmaxminddb                                  x86_64 0:1.13.3-1.fc44                       fedora                            88.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmbim                                       x86_64 0:1.32.0-3.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libmbim-utils                                 x86_64 0:1.32.0-3.fc44                       fedora                           312.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmediaart                                   x86_64 0:1.9.7-4.fc44                        fedora                            83.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmodplug                                    x86_64 1:0.8.9.0-29.fc44                     fedora                           367.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmpc                                        x86_64 0:1.4.1-1.fc44                        updates                          168.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmpeg2                                      x86_64 0:0.5.1-33.fc44                       fedora                           182.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmspack                                     x86_64 0:0.10.1-0.16.alpha.fc44              fedora                           155.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmspub                                      x86_64 0:0.1.4-39.fc44                       fedora                           448.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmtp                                        x86_64 0:1.1.22-3.fc44                       fedora                           515.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libmwaw                                       x86_64 0:0.3.22-8.fc44                       fedora                             7.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libmysofa                                     x86_64 0:1.3.3-4.fc44                        fedora                            78.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnbd                                        x86_64 0:1.25.4-1.fc44                       fedora                           491.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnfs                                        x86_64 0:6.0.2-7.fc44                        fedora                           554.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnfsidmap                                   x86_64 1:2.8.7-1.fc44                        updates                          170.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnice                                       x86_64 0:0.1.23-2.fc44                       fedora                           509.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnma                                        x86_64 0:1.10.6-11.fc44                      fedora                           358.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnma-common                                 noarch 0:1.10.6-11.fc44                      fedora                           770.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnma-gtk4                                   x86_64 0:1.10.6-11.fc44                      fedora                           334.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnotify                                     x86_64 0:0.8.8-1.fc44                        fedora                           126.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libnumbertext                                 x86_64 0:1.0.11-10.fc44                      fedora                           775.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libodfgen                                     x86_64 0:0.1.8-16.fc44                       fedora                           765.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  liboeffis                                     x86_64 0:1.5.0-2.fc44                        fedora                            32.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libogg                                        x86_64 2:1.3.6-2.fc44                        fedora                            45.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libopenjph                                    x86_64 0:0.25.3-3.fc44                       fedora                           482.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libopenmpt                                    x86_64 0:0.8.6-1.fc44                        fedora                             1.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  liborcus                                      x86_64 0:0.21.0-5.fc44                       fedora                             1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libosinfo                                     x86_64 0:1.12.0-5.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libpagemaker                                  x86_64 0:0.0.4-28.fc44                       fedora                           158.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpaper                                      x86_64 1:2.1.1-10.fc44                       fedora                            48.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpasswdqc                                   x86_64 0:2.0.3-9.fc44                        fedora                            99.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpcap                                       x86_64 14:1.10.6-2.fc44                      fedora                           432.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpciaccess                                  x86_64 0:0.16-17.fc44                        fedora                            48.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpfm                                        x86_64 0:4.13.0-19.fc44                      fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  libphodav                                     x86_64 0:3.0-13.fc44                         fedora                           144.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libphonenumber                                x86_64 0:8.13.55-9.fc44                      fedora                             6.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  libpinyin                                     x86_64 0:2.11.91-2.fc44                      fedora                           937.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpinyin-data                                x86_64 0:2.11.91-2.fc44                      fedora                            36.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libplacebo                                    x86_64 0:7.360.1-3.fc44                      fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libplist                                      x86_64 0:2.6.0-6.fc44                        fedora                           232.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpmem                                       x86_64 0:2.1.0-5.fc44                        fedora                           421.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpmemobj                                    x86_64 0:2.1.0-5.fc44                        fedora                           386.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libportal                                     x86_64 0:0.9.1-4.fc44                        fedora                           228.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libportal-gtk3                                x86_64 0:0.9.1-4.fc44                        fedora                            27.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libportal-gtk4                                x86_64 0:0.9.1-4.fc44                        fedora                            27.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libppd                                        x86_64 1:2.1.1-3.fc44                        fedora                           736.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libproxy                                      x86_64 0:0.5.12-2.fc44                       fedora                           102.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libpskc                                       x86_64 0:2.6.14-1.fc44                       fedora                            86.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libqmi                                        x86_64 0:1.36.0-3.fc44                       fedora                             5.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libqmi-utils                                  x86_64 0:1.36.0-3.fc44                       fedora                           868.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libqrtr-glib                                  x86_64 0:1.2.2-9.fc44                        fedora                            77.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libquadmath                                   x86_64 0:16.0.1-0.10.fc44                    fedora                           325.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libqxp                                        x86_64 0:0.0.2-33.fc44                       fedora                           336.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  librabbitmq                                   x86_64 0:0.15.0-4.fc44                       fedora                            89.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  librados2                                     x86_64 2:20.2.1-1.fc44                       updates                           16.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libraqm                                       x86_64 0:0.10.1-4.fc44                       fedora                            32.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libraw1394                                    x86_64 0:2.1.2-25.fc44                       fedora                           158.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  librbd1                                       x86_64 2:20.2.1-1.fc44                       updates                           12.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  librdmacm                                     x86_64 0:61.0-2.fc44                         fedora                           153.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-core                              x86_64 1:26.2.2.2-2.fc44                     updates                          288.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-data                              x86_64 1:26.2.2.2-2.fc44                     updates                            3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-filters                           x86_64 1:26.2.2.2-2.fc44                     updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-graphicfilter                     x86_64 1:26.2.2.2-2.fc44                     updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-gtk4                              x86_64 1:26.2.2.2-2.fc44                     updates                            1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-impress                           x86_64 1:26.2.2.2-2.fc44                     updates                          791.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-langpack-en                       x86_64 1:26.2.2.2-2.fc44                     updates                          169.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-ogltrans                          x86_64 1:26.2.2.2-2.fc44                     updates                          304.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-opensymbol-fonts                  noarch 1:26.2.2.2-2.fc44                     updates                          435.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-pdfimport                         x86_64 1:26.2.2.2-2.fc44                     updates                          589.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-pyuno                             x86_64 1:26.2.2.2-2.fc44                     updates                            2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-ure                               x86_64 1:26.2.2.2-2.fc44                     updates                            6.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-ure-common                        noarch 1:26.2.2.2-2.fc44                     updates                            2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-writer                            x86_64 1:26.2.2.2-2.fc44                     updates                           12.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-xsltfilter                        x86_64 1:26.2.2.2-2.fc44                     updates                            4.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreport                                     x86_64 0:2.17.15-10.fc44                     fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-cli                                 x86_64 0:2.17.15-10.fc44                     fedora                            36.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-fedora                              x86_64 0:2.17.15-10.fc44                     fedora                            53.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-filesystem                          noarch 0:2.17.15-10.fc44                     fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  libreport-plugin-bugzilla                     x86_64 0:2.17.15-10.fc44                     fedora                           128.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-plugin-kerneloops                   x86_64 0:2.17.15-10.fc44                     fedora                            43.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-plugin-logger                       x86_64 0:2.17.15-10.fc44                     fedora                            47.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-plugin-systemd-journal              x86_64 0:2.17.15-10.fc44                     fedora                            21.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-plugin-ureport                      x86_64 0:2.17.15-10.fc44                     fedora                            76.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreport-web                                 x86_64 0:2.17.15-10.fc44                     fedora                            52.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  librevenge                                    x86_64 0:0.0.5-13.fc44                       fedora                           772.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  librist                                       x86_64 0:0.2.11-1.fc44                       fedora                           182.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  librsvg2                                      x86_64 0:2.62.0-1.fc44                       fedora                             5.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libsamplerate                                 x86_64 0:0.2.2-12.fc44                       fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libsane-airscan                               x86_64 0:0.99.36-2.fc44                      fedora                           291.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsbc                                        x86_64 0:2.1-2.fc44                          fedora                            93.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libshaderc                                    x86_64 0:2026.1-1.fc44                       fedora                             4.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libshout                                      x86_64 0:2.4.6-10.fc44                       fedora                           178.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libshumate                                    x86_64 0:1.6.1-1.fc44                        updates                          589.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsigc++20                                   x86_64 0:2.12.1-7.fc44                       fedora                            90.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsigc++30                                   x86_64 0:3.8.0-1.fc44                        updates                           95.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libslirp                                      x86_64 0:4.9.1-3.fc44                        fedora                           160.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsmbclient                                  x86_64 2:4.24.1-1.fc44                       updates                          171.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsndfile                                    x86_64 0:1.2.2-11.fc44                       fedora                           553.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsodium                                     x86_64 0:1.0.22-1.fc44                       updates                          481.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsoup3                                      x86_64 0:3.6.6-6.fc44                        fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libspectre                                    x86_64 0:0.2.12-11.fc44                      fedora                            89.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libspelling                                   x86_64 0:0.4.10-1.fc44                       fedora                           244.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libsrtp                                       x86_64 0:2.8.0-1.fc44                        fedora                           129.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libssh2                                       x86_64 0:1.11.1-5.fc44                       fedora                           338.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libstaroffice                                 x86_64 0:0.0.7-17.fc44                       fedora                             2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libstemmer                                    x86_64 0:3.0.1-11.fc44                       fedora                           641.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libswresample-free                            x86_64 0:8.0.1-6.fc44                        fedora                           155.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libswscale-free                               x86_64 0:8.0.1-6.fc44                        fedora                           766.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libthai                                       x86_64 0:0.1.30-2.fc44                       fedora                           800.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libtheora                                     x86_64 1:1.1.1-41.fc44                       fedora                           480.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libtiff                                       x86_64 0:4.7.1-2.fc44                        fedora                           640.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libtinysparql                                 x86_64 0:3.11.1-1.fc44                       updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libtommath                                    x86_64 0:1.3.1~rc1-7.fc44                    fedora                           130.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libtpms                                       x86_64 0:0.10.2-3.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libtraceevent                                 x86_64 0:1.8.4-5.fc44                        fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libudfread                                    x86_64 0:1.2.0-3.fc44                        fedora                            62.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libudisks2                                    x86_64 0:2.11.1-2.fc44                       updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  libultrahdr                                   x86_64 0:1.4.0^20251202git8cbc983-1.fc44     fedora                           384.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libunibreak                                   x86_64 0:6.1-5.fc44                          fedora                           139.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libunwind                                     x86_64 0:1.8.3-1.fc44                        fedora                           194.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libusal                                       x86_64 0:1.1.11-63.fc44                      fedora                           452.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libusbmuxd                                    x86_64 0:2.1.0-5.fc44                        fedora                            75.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libuser                                       x86_64 0:0.64-17.fc44                        fedora                             1.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  libuv                                         x86_64 1:1.51.0-3.fc44                       fedora                           582.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libv4l                                        x86_64 0:1.32.0-3.fc44                       fedora                           364.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libva                                         x86_64 0:2.23.0-3.fc44                       fedora                           345.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvdpau                                      x86_64 0:1.5-11.fc44                         fedora                            20.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libverto-libev                                x86_64 0:0.3.2-12.fc44                       fedora                            15.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-client                                x86_64 0:12.0.0-3.fc44                       fedora                           996.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-common                         x86_64 0:12.0.0-3.fc44                       fedora                           457.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-config-network                 x86_64 0:12.0.0-3.fc44                       fedora                           470.0   B[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-interface               x86_64 0:12.0.0-3.fc44                       fedora                           758.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-network                 x86_64 0:12.0.0-3.fc44                       fedora                           888.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-nodedev                 x86_64 0:12.0.0-3.fc44                       fedora                           823.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-nwfilter                x86_64 0:12.0.0-3.fc44                       fedora                           848.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-qemu                    x86_64 0:12.0.0-3.fc44                       fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-secret                  x86_64 0:12.0.0-3.fc44                       fedora                           750.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage                 x86_64 0:12.0.0-3.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-core            x86_64 0:12.0.0-3.fc44                       fedora                           903.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-disk            x86_64 0:12.0.0-3.fc44                       fedora                            27.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-gluster         x86_64 0:12.0.0-3.fc44                       fedora                            35.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-iscsi           x86_64 0:12.0.0-3.fc44                       fedora                            19.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-iscsi-direct    x86_64 0:12.0.0-3.fc44                       fedora                            27.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-logical         x86_64 0:12.0.0-3.fc44                       fedora                            27.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-mpath           x86_64 0:12.0.0-3.fc44                       fedora                            15.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-rbd             x86_64 0:12.0.0-3.fc44                       fedora                            39.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-driver-storage-scsi            x86_64 0:12.0.0-3.fc44                       fedora                            19.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-kvm                            x86_64 0:12.0.0-3.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-lock                           x86_64 0:12.0.0-3.fc44                       fedora                            99.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-log                            x86_64 0:12.0.0-3.fc44                       fedora                           110.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-plugin-lockd                   x86_64 0:12.0.0-3.fc44                       fedora                            27.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon-proxy                          x86_64 0:12.0.0-3.fc44                       fedora                           733.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-gconfig                               x86_64 0:5.0.0-8.fc44                        fedora                           382.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-glib                                  x86_64 0:5.0.0-8.fc44                        fedora                           132.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-gobject                               x86_64 0:5.0.0-8.fc44                        fedora                           222.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-libs                                  x86_64 0:12.0.0-3.fc44                       fedora                            30.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-ssh-proxy                             x86_64 0:12.0.0-3.fc44                       fedora                            19.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvisio                                      x86_64 0:0.1.10-1.fc44                       fedora                           708.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvisual                                     x86_64 1:0.4.2-4.fc44                        fedora                           464.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvmaf                                       x86_64 0:3.0.0-5.fc44                        fedora                           846.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvncserver                                  x86_64 0:0.9.15-6.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libvorbis                                     x86_64 1:1.3.7-14.fc44                       fedora                           837.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvpl                                        x86_64 1:2.16.0-2.fc44                       fedora                           438.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libvpx                                        x86_64 0:1.15.0-5.fc44                       fedora                             3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  libwacom                                      x86_64 0:2.18.0-1.fc44                       fedora                           109.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwacom-data                                 noarch 0:2.18.0-1.fc44                       fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  libwayland-client                             x86_64 0:1.24.0-3.fc44                       fedora                            61.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwayland-cursor                             x86_64 0:1.24.0-3.fc44                       fedora                            37.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwayland-egl                                x86_64 0:1.24.0-3.fc44                       fedora                            12.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwayland-server                             x86_64 0:1.24.0-3.fc44                       fedora                            86.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwbclient                                   x86_64 2:4.24.1-1.fc44                       updates                           71.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwebp                                       x86_64 0:1.6.0-3.fc44                        fedora                           968.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwinpr                                      x86_64 2:3.24.2-1.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libwmf-lite                                   x86_64 0:0.2.13-9.fc44                       fedora                           159.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwpd                                        x86_64 0:0.10.3-24.fc44                      fedora                           730.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwpg                                        x86_64 0:0.3.4-7.fc44                        fedora                           177.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwps                                        x86_64 0:0.4.14-7.fc44                       fedora                             2.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  libwsman1                                     x86_64 0:2.8.1-14.fc44                       fedora                           360.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxcb                                        x86_64 0:1.17.0-7.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libxcvt                                       x86_64 0:0.1.2-11.fc44                       fedora                            14.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxdp                                        x86_64 0:1.6.3-1.fc44                        fedora                           167.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxkbcommon-x11                              x86_64 0:1.13.1-2.fc44                       fedora                            35.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxkbfile                                    x86_64 0:1.1.3-5.fc44                        fedora                           201.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxmlb                                       x86_64 0:0.3.26-1.fc44                       updates                          284.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxshmfence                                  x86_64 0:1.3.2-8.fc44                        fedora                            12.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  libxslt                                       x86_64 0:1.1.43-6.fc44                       fedora                           471.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libyuv                                        x86_64 0:0-0.61.20260213git6067afd.fc44      fedora                           683.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libzip                                        x86_64 0:1.11.4-3.fc44                       fedora                           143.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libzmf                                        x86_64 0:0.0.2-42.fc44                       fedora                           188.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  lilv-libs                                     x86_64 0:0.26.4-1.fc44                       fedora                           125.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  linux-atm-libs                                x86_64 0:2.5.1-46.fc44                       fedora                            72.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  linux-firmware-whence                         noarch 0:20260410-1.fc44                     updates                          415.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  lksctp-tools                                  x86_64 0:1.0.21-3.fc44                       fedora                           250.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  llvm-filesystem                               x86_64 0:22.1.4-1.fc44                       updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  llvm-libs                                     x86_64 0:22.1.4-1.fc44                       updates                          140.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  lm_sensors-libs                               x86_64 0:3.6.0-24.fc44                       fedora                            85.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  lockdev                                       x86_64 0:1.0.4-0.54.20111007git.fc44         fedora                            70.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  lpcnetfreedv                                  x86_64 0:0.5-10.fc44                         fedora                            14.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  lpsolve                                       x86_64 0:5.5.2.14-2.fc44                     fedora                           759.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  lttng-ust                                     x86_64 0:2.14.0-5.fc44                       fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  lzop                                          x86_64 0:1.04-18.fc44                        fedora                            98.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  m17n-db                                       noarch 0:1.8.10-3.fc44                       fedora                             2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  m17n-lib                                      x86_64 0:1.8.6-3.fc44                        fedora                           463.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  madan-fonts                                   noarch 0:2.000-43.fc44                       fedora                           246.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  malcontent                                    x86_64 0:0.14.0-1.fc44                       fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  malcontent-libs                               x86_64 0:0.14.0-1.fc44                       fedora                           172.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  malcontent-ui-libs                            x86_64 0:0.14.0-1.fc44                       fedora                           103.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  mariadb-connector-c                           x86_64 0:3.4.8-3.fc44                        fedora                           523.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  mariadb-connector-c-config                    noarch 0:3.4.8-3.fc44                        fedora                           497.0   B[0m
[1;32m==> proxmox-clone.fedora:  md4c                                          x86_64 0:0.5.1-5.fc44                        fedora                           199.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  mdevctl                                       x86_64 0:1.4.0-3.fc44                        fedora                             2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-filesystem                               x86_64 0:26.0.5-3.fc44                       updates                            3.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-libEGL                                   x86_64 0:26.0.5-3.fc44                       updates                          394.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-libGL                                    x86_64 0:26.0.5-3.fc44                       updates                          370.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-libGLU                                   x86_64 0:9.0.3-8.fc44                        fedora                           369.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  mesa-libgbm                                   x86_64 0:26.0.5-3.fc44                       updates                           19.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  mobile-broadband-provider-info                noarch 0:20240407-5.fc44                     fedora                           504.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  mod_dnssd                                     x86_64 0:0.6-36.fc44                         fedora                            57.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  mozilla-filesystem                            x86_64 0:1.9-38.fc44                         fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  mozilla-openh264                              x86_64 0:2.6.0-3.fc44                        fedora-cisco-openh264              1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  mozjs140                                      x86_64 0:140.6.0-4.fc44                      fedora                            20.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  mpg123-libs                                   x86_64 0:1.32.10-3.fc44                      fedora                           825.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  msgraph                                       x86_64 0:0.3.4-5.fc44                        fedora                           149.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  mtdev                                         x86_64 0:1.1.6-12.fc44                       fedora                            29.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  mutter                                        x86_64 0:50.1-1.fc44                         updates                            9.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  mutter-common                                 noarch 0:50.1-1.fc44                         updates                           35.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  mythes                                        x86_64 0:1.2.5-10.fc44                       fedora                            23.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  mythes-en                                     noarch 0:3.0-43.fc44                         fedora                            20.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  nautilus-extensions                           x86_64 0:50.1-1.fc44                         updates                           82.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-basic-filters                          x86_64 0:1.47.7-1.fc44                       updates                          936.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-basic-plugins                          x86_64 0:1.47.7-1.fc44                       updates                          483.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-selinux                                noarch 0:1.47.7-1.fc44                       updates                           16.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-server                                 x86_64 0:1.47.7-1.fc44                       updates                          244.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  ndctl-libs                                    x86_64 0:84-1.fc44                           fedora                           225.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  net-snmp-libs                                 x86_64 1:5.9.5.2-4.fc44                      fedora                             3.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  nfs-client-utils                              x86_64 1:2.8.7-1.fc44                        updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  nfs-common-utils                              x86_64 1:2.8.7-1.fc44                        updates                          383.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  nfsv3-client-utils                            x86_64 1:2.8.7-1.fc44                        updates                          147.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  nfsv4-client-utils                            x86_64 1:2.8.7-1.fc44                        updates                           42.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  ngtcp2-crypto-gnutls                          x86_64 0:1.22.1-1.fc44                       updates                           43.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  nspr                                          x86_64 0:4.38.2-9.fc44                       fedora                           327.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  nss                                           x86_64 0:3.122.1-1.fc44                      fedora                             2.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  nss-softokn                                   x86_64 0:3.122.1-1.fc44                      fedora                             2.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  nss-softokn-freebl                            x86_64 0:3.122.1-1.fc44                      fedora                           998.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  nss-sysinit                                   x86_64 0:3.122.1-1.fc44                      fedora                            17.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  nss-util                                      x86_64 0:3.122.1-1.fc44                      fedora                           212.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  ntfs-3g-libs                                  x86_64 2:2022.10.3-12.fc44                   fedora                           384.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  numad                                         x86_64 0:0.5-50.20251104git.fc44             fedora                            59.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  oniguruma                                     x86_64 0:6.9.10-4.fc44                       fedora                           770.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  open-vm-tools                                 x86_64 0:13.0.10-2.fc44                      fedora                             3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  openal-soft                                   x86_64 0:1.24.2-6.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  openapv-libs                                  x86_64 0:0.2.1.2-1.fc44                      fedora                           125.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  openconnect                                   x86_64 0:9.12-10.fc44                        fedora                             3.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  opencore-amr                                  x86_64 0:0.1.6-10.fc44                       fedora                           352.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  openexr-libs                                  x86_64 0:3.2.4-7.fc44                        fedora                             6.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  openh264                                      x86_64 0:2.6.0-3.fc44                        fedora-cisco-openh264              1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  openjpeg                                      x86_64 0:2.5.4-3.fc44                        fedora                           464.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  openpace                                      x86_64 0:1.1.3-5.fc44                        fedora                           315.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  openpgm                                       x86_64 0:5.3.128-6.fc44                      fedora                           320.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  opensc-libs                                   x86_64 0:0.27.1-2.fc44                       updates                            2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  openvpn                                       x86_64 0:2.7.3-1.fc44                        updates                            1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  opus                                          x86_64 0:1.6-2.fc44                          fedora                           467.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  orc                                           x86_64 0:0.4.41-3.fc44                       fedora                           721.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  osinfo-db                                     noarch 0:20251212-1.fc44                     fedora                             4.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  osinfo-db-tools                               x86_64 0:1.12.0-5.fc44                       fedora                           190.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  ostree-libs                                   x86_64 0:2026.1-1.fc44                       updates                            1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  paktype-naskh-basic-fonts                     noarch 0:7.0-4.20231228.fc44                 fedora                             3.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  pam_passwdqc                                  x86_64 0:2.0.3-9.fc44                        fedora                            20.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  pango                                         x86_64 0:1.57.1-1.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  pangomm                                       x86_64 0:2.46.4-5.fc44                       fedora                           250.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  pangomm2.48                                   x86_64 0:2.56.1-3.fc44                       fedora                           312.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  papers-libs                                   x86_64 0:49.6-1.fc44                         updates                          936.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  papers-previewer                              x86_64 0:49.6-1.fc44                         updates                           51.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  papers-thumbnailer                            x86_64 0:49.6-1.fc44                         updates                            1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  passim-libs                                   x86_64 0:0.1.11-1.fc44                       updates                           70.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  passwdqc-utils                                x86_64 0:2.0.3-9.fc44                        fedora                            73.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcaudiolib                                    x86_64 0:1.1-19.fc44                         fedora                            60.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  pciutils-libs                                 x86_64 0:3.14.0-3.fc44                       fedora                            99.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcre2-utf16                                   x86_64 0:10.47-1.fc44.1                      fedora                           655.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcre2-utf32                                   x86_64 0:10.47-1.fc44.1                      fedora                           623.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcsc-lite                                     x86_64 0:2.4.1-2.fc44                        fedora                           214.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcsc-lite-ccid                                x86_64 0:1.7.1-2.fc44                        fedora                           362.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  pcsc-lite-libs                                x86_64 0:2.4.1-2.fc44                        fedora                            63.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-AutoLoader                               noarch 0:5.74-524.fc44                       updates                           20.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-B                                        x86_64 0:1.89-524.fc44                       updates                          501.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Carp                                     noarch 0:1.54-521.fc44                       fedora                            46.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Class-Struct                             noarch 0:0.68-524.fc44                       updates                           25.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Data-Dumper                              x86_64 0:2.191-522.fc44                      fedora                           115.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Digest                                   noarch 0:1.20-521.fc44                       fedora                            35.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Digest-MD5                               x86_64 0:2.59-521.fc44                       fedora                            59.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-DynaLoader                               x86_64 0:1.57-524.fc44                       updates                           32.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Encode                                   x86_64 4:3.21-521.fc44                       fedora                             4.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Errno                                    x86_64 0:1.38-524.fc44                       updates                            8.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Error                                    noarch 1:0.17030-3.fc44                      fedora                            76.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Exporter                                 noarch 0:5.79-521.fc44                       fedora                            54.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Fcntl                                    x86_64 0:1.20-524.fc44                       updates                           48.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-File-Basename                            noarch 0:2.86-524.fc44                       updates                           14.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-File-Path                                noarch 0:2.18-522.fc44                       fedora                            63.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-File-Temp                                noarch 1:0.231.200-2.fc44                    fedora                           163.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-File-stat                                noarch 0:1.14-524.fc44                       updates                           12.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-FileHandle                               noarch 0:2.05-524.fc44                       updates                            9.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Getopt-Long                              noarch 1:2.58-521.fc44                       fedora                           144.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Getopt-Std                               noarch 0:1.14-524.fc44                       updates                           11.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Git                                      noarch 0:2.54.0-1.fc44                       updates                           64.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-HTTP-Tiny                                noarch 0:0.092-2.fc44                        fedora                           157.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-IO                                       x86_64 0:1.55-524.fc44                       updates                          147.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-IO-Socket-IP                             noarch 0:0.43-522.fc44                       fedora                           100.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-IO-Socket-SSL                            noarch 0:2.098-2.fc44                        fedora                           723.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-IPC-Open3                                noarch 0:1.24-524.fc44                       updates                           27.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-MIME-Base32                              noarch 0:1.303-25.fc44                       fedora                            30.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-MIME-Base64                              x86_64 0:3.16-521.fc44                       fedora                            41.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Net-SSLeay                               x86_64 0:1.94-12.fc44                        fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  perl-POSIX                                    x86_64 0:2.23-524.fc44                       updates                          229.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-PathTools                                x86_64 0:3.94-521.fc44                       fedora                           179.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Pod-Escapes                              noarch 1:1.07-521.fc44                       fedora                            24.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Pod-Perldoc                              noarch 0:3.28.01-522.fc44                    fedora                           163.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Pod-Simple                               noarch 1:3.47-4.fc44                         fedora                           565.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Pod-Usage                                noarch 4:2.05-521.fc44                       fedora                            86.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Scalar-List-Utils                        x86_64 5:1.70-2.fc44                         fedora                           144.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-SelectSaver                              noarch 0:1.02-524.fc44                       updates                            2.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Socket                                   x86_64 4:2.040-3.fc44                        fedora                           120.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Storable                                 x86_64 1:3.37-522.fc44                       fedora                           235.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Symbol                                   noarch 0:1.09-524.fc44                       updates                            6.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Term-ANSIColor                           noarch 0:5.01-522.fc44                       fedora                            97.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Term-Cap                                 noarch 0:1.18-521.fc44                       fedora                            29.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-TermReadKey                              x86_64 0:2.38-27.fc44                        fedora                            63.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Text-ParseWords                          noarch 0:3.31-521.fc44                       fedora                            13.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Text-Tabs+Wrap                           noarch 0:2024.001-521.fc44                   fedora                            22.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Time-HiRes                               x86_64 4:1.9778-521.fc44                     fedora                           115.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-Time-Local                               noarch 2:1.350-521.fc44                      fedora                            69.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-URI                                      noarch 0:5.34-3.fc44                         fedora                           268.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-base                                     noarch 0:2.27-524.fc44                       updates                           12.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-constant                                 noarch 0:1.33-522.fc44                       fedora                            26.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-if                                       noarch 0:0.61.000-524.fc44                   updates                            5.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-interpreter                              x86_64 4:5.42.2-524.fc44                     updates                          118.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-lib                                      x86_64 0:0.65-524.fc44                       updates                            8.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-libnet                                   noarch 0:3.15-522.fc44                       fedora                           289.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-libs                                     x86_64 4:5.42.2-524.fc44                     updates                           11.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  perl-locale                                   noarch 0:1.13-524.fc44                       updates                            6.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-mro                                      x86_64 0:1.29-524.fc44                       updates                           41.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-overload                                 noarch 0:1.40-524.fc44                       updates                           71.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-overloading                              noarch 0:0.02-524.fc44                       updates                            4.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-parent                                   noarch 1:0.244-521.fc44                      fedora                            10.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-podlators                                noarch 1:6.0.2-521.fc44                      fedora                           317.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-vars                                     noarch 0:1.05-524.fc44                       updates                            3.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire                                      x86_64 0:1.6.4-1.fc44                        updates                          451.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-gstreamer                            x86_64 0:1.6.4-1.fc44                        updates                          185.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-jack-audio-connection-kit            x86_64 0:1.6.4-1.fc44                        updates                           30.0   B[0m
[1;32m==> proxmox-clone.fedora:  pipewire-jack-audio-connection-kit-libs       x86_64 0:1.6.4-1.fc44                        updates                          520.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-libs                                 x86_64 0:1.6.4-1.fc44                        updates                            9.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  pixman                                        x86_64 0:0.46.2-3.fc44                       fedora                           718.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  pkcs11-helper                                 x86_64 0:1.30.0-5.fc44                       fedora                           164.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-core-libs                            x86_64 0:24.004.60-24.fc44                   fedora                           366.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-graphics-libs                        x86_64 0:24.004.60-24.fc44                   fedora                           171.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-plugin-label                         x86_64 0:24.004.60-24.fc44                   fedora                            51.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-plugin-two-step                      x86_64 0:24.004.60-24.fc44                   fedora                            75.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-scripts                              x86_64 0:24.004.60-24.fc44                   fedora                            30.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  plymouth-theme-spinner                        x86_64 0:24.004.60-24.fc44                   fedora                           194.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  polkit-libs                                   x86_64 0:127-2.fc44.2                        fedora                           220.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  poppler                                       x86_64 0:26.01.0-3.fc44                      fedora                             4.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  poppler-cpp                                   x86_64 0:26.01.0-3.fc44                      fedora                           129.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  poppler-data                                  noarch 0:0.4.11-11.fc44                      fedora                            12.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  poppler-glib                                  x86_64 0:26.01.0-3.fc44                      fedora                           658.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  poppler-utils                                 x86_64 0:26.01.0-3.fc44                      fedora                           813.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  portaudio                                     x86_64 0:19.7.0-3.fc44                       fedora                           257.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  ppp                                           x86_64 0:2.5.1-7.fc44                        fedora                           944.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  protobuf                                      x86_64 0:3.19.6-20.fc44                      fedora                             3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  pulseaudio-libs                               x86_64 0:17.0-9.fc44                         fedora                             3.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  pulseaudio-libs-glib2                         x86_64 0:17.0-9.fc44                         fedora                            19.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  pulseaudio-utils                              x86_64 0:17.0-9.fc44                         fedora                           262.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-abrt                                  x86_64 0:2.17.8-3.fc44                       fedora                            71.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-abrt-addon                            noarch 0:2.17.8-3.fc44                       fedora                            18.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-anyio                                 noarch 0:4.12.1-3.fc44                       fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-argcomplete                           noarch 0:3.6.3-4.fc44                        fedora                           325.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-augeas                                x86_64 0:1.2.0-7.fc44                        fedora                           184.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-botocore                              noarch 0:1.42.84-1.fc44                      updates                          109.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-brlapi                                x86_64 0:0.8.7-8.fc44                        fedora                           272.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-cairo                                 x86_64 0:1.28.0-5.fc44                       fedora                           508.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-certifi                               noarch 0:2026.01.04-1.fc44                   fedora                             7.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-cffi                                  x86_64 0:2.0.0-3.fc44                        fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-click                                 noarch 1:8.3.3-1.fc44                        updates                            1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-cups                                  x86_64 0:2.0.4-8.fc44                        fedora                           248.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-dasbus                                noarch 0:1.7-14.fc44                         fedora                           403.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-dateutil                              noarch 1:2.9.0.post0-7.fc44                  fedora                           878.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-enchant                               noarch 0:3.3.0-2.fc44                        fedora                           428.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-firewall                              noarch 0:2.4.0-2.fc44                        fedora                             2.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-gobject                               x86_64 0:3.56.2-1.fc44                       fedora                            27.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-gobject-base                          x86_64 0:3.56.2-1.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-h11                                   noarch 0:0.16.0-6.fc44                       fedora                           279.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-httpcore                              noarch 0:1.0.9-6.fc44                        fedora                           853.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-ibus                                  x86_64 0:1.5.34-1.fc44                       updates                           26.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-inotify                               noarch 0:0.9.6-43.fc44                       fedora                           297.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-jmespath                              noarch 0:1.0.1-14.fc44                       fedora                           150.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-libreport                             x86_64 0:2.17.15-10.fc44                     fedora                           514.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-linux-procfs                          noarch 0:0.7.4-2.fc44                        fedora                            91.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-louis                                 noarch 0:3.33.0-7.fc44                       fedora                            43.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-nftables                              noarch 1:1.1.6-2.fc44                        fedora                            43.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-olefile                               noarch 0:0.47-13.fc44                        fedora                           346.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-packaging                             noarch 0:25.0-8.fc44                         fedora                           607.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pam                                   noarch 0:2.0.2-18.fc44                       fedora                            53.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pexpect                               noarch 0:4.9.0-15.fc44                       fedora                           624.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pillow                                x86_64 0:12.2.0-1.fc44                       updates                            4.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-ptyprocess                            noarch 0:0.7.0-15.fc44                       fedora                            80.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pyatspi                               noarch 0:2.58.2-1.fc44                       fedora                           414.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pycparser                             noarch 0:2.22-8.fc44                         fedora                             2.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pyudev                                noarch 0:0.24.4-3.fc44                       fedora                           343.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pyxdg                                 noarch 0:0.28-1.fc44                         fedora                           469.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-rapidfuzz                             x86_64 0:3.14.3-2.fc44                       fedora                            11.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-s3transfer                            noarch 0:0.16.0-2.fc44                       fedora                           653.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-satyr                                 x86_64 0:0.43-10.fc44                        fedora                           117.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-speechd                               x86_64 0:0.12.1-6.fc44                       fedora                           322.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-systemd                               x86_64 0:235-18.fc44                         fedora                           346.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  qatlib                                        x86_64 0:25.08.0-4.fc44                      fedora                           675.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  qatzip-libs                                   x86_64 0:1.3.1-3.fc44                        fedora                           144.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-alsa                               x86_64 2:10.2.2-1.fc44                       fedora                            28.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-dbus                               x86_64 2:10.2.2-1.fc44                       fedora                           284.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-jack                               x86_64 2:10.2.2-1.fc44                       fedora                            19.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-oss                                x86_64 2:10.2.2-1.fc44                       fedora                            19.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-pa                                 x86_64 2:10.2.2-1.fc44                       fedora                            27.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-pipewire                           x86_64 2:10.2.2-1.fc44                       fedora                            44.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-sdl                                x86_64 2:10.2.2-1.fc44                       fedora                            19.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-audio-spice                              x86_64 2:10.2.2-1.fc44                       fedora                            15.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-blkio                              x86_64 2:10.2.2-1.fc44                       fedora                            36.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-curl                               x86_64 2:10.2.2-1.fc44                       fedora                            32.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-dmg                                x86_64 2:10.2.2-1.fc44                       fedora                            11.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-gluster                            x86_64 2:10.2.2-1.fc44                       fedora                            35.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-iscsi                              x86_64 2:10.2.2-1.fc44                       fedora                            50.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-nfs                                x86_64 2:10.2.2-1.fc44                       fedora                            28.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-rbd                                x86_64 2:10.2.2-1.fc44                       fedora                            40.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-block-ssh                                x86_64 2:10.2.2-1.fc44                       fedora                            42.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-char-baum                                x86_64 2:10.2.2-1.fc44                       fedora                            19.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-char-spice                               x86_64 2:10.2.2-1.fc44                       fedora                            20.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-common                                   x86_64 2:10.2.2-1.fc44                       fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-qxl                       x86_64 2:10.2.2-1.fc44                       fedora                            87.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-vhost-user-gpu            x86_64 2:10.2.2-1.fc44                       fedora                           786.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu                x86_64 2:10.2.2-1.fc44                       fedora                            69.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-ccw            x86_64 2:10.2.2-1.fc44                       fedora                            11.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-gl             x86_64 2:10.2.2-1.fc44                       fedora                            46.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-pci            x86_64 2:10.2.2-1.fc44                       fedora                            15.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-pci-gl         x86_64 2:10.2.2-1.fc44                       fedora                            10.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-pci-rutabaga   x86_64 2:10.2.2-1.fc44                       fedora                            10.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-gpu-rutabaga       x86_64 2:10.2.2-1.fc44                       fedora                            37.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-vga                x86_64 2:10.2.2-1.fc44                       fedora                            19.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-vga-gl             x86_64 2:10.2.2-1.fc44                       fedora                            11.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-display-virtio-vga-rutabaga       x86_64 2:10.2.2-1.fc44                       fedora                            11.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-uefi-vars                         x86_64 2:10.2.2-1.fc44                       fedora                            61.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-usb-host                          x86_64 2:10.2.2-1.fc44                       fedora                            47.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-usb-redirect                      x86_64 2:10.2.2-1.fc44                       fedora                            68.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-device-usb-smartcard                     x86_64 2:10.2.2-1.fc44                       fedora                            31.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-img                                      x86_64 2:10.2.2-1.fc44                       fedora                            24.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-kvm                                      x86_64 2:10.2.2-1.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  qemu-pr-helper                                x86_64 2:10.2.2-1.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-system-x86                               x86_64 2:10.2.2-1.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  qemu-system-x86-core                          x86_64 2:10.2.2-1.fc44                       fedora                            60.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-curses                                x86_64 2:10.2.2-1.fc44                       fedora                            39.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-egl-headless                          x86_64 2:10.2.2-1.fc44                       fedora                            15.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-gtk                                   x86_64 2:10.2.2-1.fc44                       fedora                            86.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-opengl                                x86_64 2:10.2.2-1.fc44                       fedora                            36.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-sdl                                   x86_64 2:10.2.2-1.fc44                       fedora                            44.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-spice-app                             x86_64 2:10.2.2-1.fc44                       fedora                            15.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-ui-spice-core                            x86_64 2:10.2.2-1.fc44                       fedora                            67.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  qpdf-libs                                     x86_64 0:12.3.2-1.fc44                       fedora                             3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-filesystem                                x86_64 0:6.10.3-1.fc44                       updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtbase                                    x86_64 0:6.10.3-1.fc44                       updates                           13.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtbase-common                             noarch 0:6.10.3-1.fc44                       updates                           76.0   B[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtbase-gui                                x86_64 0:6.10.3-1.fc44                       updates                           27.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtdeclarative                             x86_64 0:6.10.3-1.fc44                       updates                           55.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtsvg                                     x86_64 0:6.10.3-1.fc44                       updates                          910.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  qt6-qtwayland                                 x86_64 0:6.10.3-1.fc44                       updates                            3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  quota-nls                                     noarch 1:4.11-2.fc44                         fedora                           300.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  raptor2                                       x86_64 0:2.0.15-50.fc44                      fedora                           571.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  rasqal                                        x86_64 0:0.9.33-32.fc44                      fedora                           886.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  rav1e-libs                                    x86_64 0:0.8.1-3.fc44                        fedora                             3.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  rdma-core-common                              noarch 0:61.0-2.fc44                         fedora                            21.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  redhat-menus                                  noarch 0:12.0.2-39.fc44                      fedora                           672.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  redland                                       x86_64 0:1.0.17-41.fc44                      fedora                           513.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  rest                                          x86_64 0:0.10.2-5.fc44                       fedora                           202.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  rit-meera-new-fonts                           noarch 0:1.6.2-5.fc44                        fedora                           198.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  rit-rachana-fonts                             noarch 0:1.5.2-5.fc44                        fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  rpcbind                                       x86_64 0:1.2.8-1.fc44                        fedora                           111.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  rpm-plugin-dbus-announce                      x86_64 0:6.0.1-2.fc44                        fedora                            16.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  rtkit                                         x86_64 0:0.11-70.fc44                        fedora                           137.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  rubberband-libs                               x86_64 0:4.0.0-5.fc44                        fedora                           471.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  rutabaga-gfx-ffi                              x86_64 0:0.1.3-5.fc44                        fedora                           618.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  samba-client-libs                             x86_64 2:4.24.1-1.fc44                       updates                           11.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  samba-common                                  noarch 2:4.24.1-1.fc44                       updates                          204.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  samba-core-libs                               x86_64 2:4.24.1-1.fc44                       updates                            1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  samba-ndr-libs                                x86_64 2:4.24.1-1.fc44                       updates                            4.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  sane-airscan                                  x86_64 0:0.99.36-2.fc44                      fedora                           174.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  sane-backends                                 x86_64 0:1.4.0-6.fc44                        fedora                             3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  sane-backends-libs                            x86_64 0:1.4.0-6.fc44                        fedora                            96.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  satyr                                         x86_64 0:0.43-10.fc44                        fedora                           347.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  scrub                                         x86_64 0:2.6.1-12.fc44                       fedora                           126.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  sdl2-compat                                   x86_64 0:2.32.64-1.fc44                      fedora                           408.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  seabios-bin                                   noarch 0:1.17.0-10.fc44                      fedora                           960.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  seavgabios-bin                                noarch 0:1.17.0-10.fc44                      fedora                           366.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  serd                                          x86_64 0:0.32.8-1.fc44                       fedora                           140.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  setxkbmap                                     x86_64 0:1.3.4-7.fc44                        fedora                            31.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  shared-mime-info                              x86_64 0:2.4-3.fc44                          fedora                             5.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  sil-padauk-fonts                              noarch 0:3.003-21.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  simdutf                                       x86_64 0:7.2.1-3.fc44                        fedora                           611.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  slang                                         x86_64 0:2.3.3-9.fc44                        fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  snappy                                        x86_64 0:1.2.2-4.fc44                        fedora                            79.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  sord                                          x86_64 0:0.16.22-1.fc44                      fedora                            85.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  sound-theme-freedesktop                       noarch 0:0.8-31.fc44                         fedora                           460.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  soundtouch                                    x86_64 0:2.4.0-3.fc44                        fedora                           225.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  source-highlight                              x86_64 0:3.1.9-27.fc44                       fedora                             3.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  soxr                                          x86_64 0:0.1.3-21.fc44                       fedora                           191.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  spandsp                                       x86_64 0:0.0.6-22.fc44                       fedora                           856.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  speech-dispatcher-espeak-ng                   x86_64 0:0.12.1-6.fc44                       fedora                            59.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  speech-dispatcher-libs                        x86_64 0:0.12.1-6.fc44                       fedora                            92.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  speex                                         x86_64 0:1.2.0-21.fc44                       fedora                           128.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  spice-glib                                    x86_64 0:0.42-8.fc44                         fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  spice-gtk3                                    x86_64 0:0.42-8.fc44                         fedora                           285.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  spice-server                                  x86_64 0:0.16.0-2.fc43                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  spirv-tools-libs                              x86_64 0:2026.1-1.fc44                       fedora                             6.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  sratom                                        x86_64 0:0.6.22-1.fc44                       fedora                            48.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  srt-libs                                      x86_64 0:1.5.5-1.fc44                        updates                            1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  sshpass                                       x86_64 0:1.09-12.fc44                        fedora                            42.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  sssd-nfs-idmap                                x86_64 0:2.12.0-4.fc44                       fedora                            46.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  startup-notification                          x86_64 0:0.12-33.fc44                        fedora                            94.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  stix-fonts                                    noarch 0:2.13b171-10.fc44                    fedora                             3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  stoken-libs                                   x86_64 0:0.93-2.fc44                         fedora                            90.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  svt-av1-libs                                  x86_64 0:3.1.2-2.fc44                        fedora                             5.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  switcheroo-control                            x86_64 0:3.0-5.fc44                          fedora                           141.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  swtpm                                         x86_64 0:0.10.1-3.fc44                       fedora                            53.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  swtpm-libs                                    x86_64 0:0.10.1-3.fc44                       fedora                           132.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  swtpm-selinux                                 noarch 0:0.10.1-3.fc44                       fedora                           253.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  swtpm-tools                                   x86_64 0:0.10.1-3.fc44                       fedora                           257.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  system-config-printer-libs                    noarch 0:1.5.18-17.fc44                      fedora                             6.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  systemd-container                             x86_64 0:259.5-1.fc44                        fedora                             2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  taglib                                        x86_64 0:2.2.1-1.fc44                        fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  tcl                                           x86_64 1:9.0.2-1.fc44                        fedora                             4.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  tecla                                         x86_64 0:50.0-1.fc44                         fedora                           153.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  tesseract-common                              noarch 0:5.5.2-1.fc44                        fedora                            14.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  tesseract-langpack-eng                        noarch 0:4.1.0-12.fc44                       fedora                             3.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  tesseract-libs                                x86_64 0:5.5.2-1.fc44                        fedora                             3.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  tesseract-tessdata-doc                        noarch 0:4.1.0-12.fc44                       fedora                            15.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  texlive-lib                                   x86_64 12:20260301-109.fc44                  updates                            1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  thrift                                        x86_64 0:0.20.0-9.fc44                       fedora                             5.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  totem-pl-parser                               x86_64 0:3.26.7-1.fc44                       updates                          315.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  tslib                                         x86_64 0:1.24-2.fc44                         fedora                           402.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  tuned                                         noarch 0:2.27.0-1.fc44                       fedora                             1.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  twolame-libs                                  x86_64 0:0.4.0-9.fc44                        fedora                           161.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  tzdata-java                                   noarch 0:2026a-1.fc44                        fedora                           100.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  uchardet                                      x86_64 0:0.0.8-10.fc44                       fedora                           275.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  udisks2                                       x86_64 0:2.11.1-2.fc44                       updates                            3.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  unicode-ucd                                   noarch 0:17.0.0-2.fc44                       fedora                            39.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  upower                                        x86_64 0:1.91.2-1.fc44                       updates                          306.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  upower-libs                                   x86_64 0:1.91.2-1.fc44                       updates                          178.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  uriparser                                     x86_64 0:1.0.0-2.fc44                        fedora                           182.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-bookman-fonts                      noarch 0:20200910-27.fc44                    fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-c059-fonts                         noarch 0:20200910-27.fc44                    fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-d050000l-fonts                     noarch 0:20200910-27.fc44                    fedora                            84.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-fonts                              noarch 0:20200910-27.fc44                    fedora                             5.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-fonts-common                       noarch 0:20200910-27.fc44                    fedora                            37.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-gothic-fonts                       noarch 0:20200910-27.fc44                    fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-nimbus-mono-ps-fonts               noarch 0:20200910-27.fc44                    fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-nimbus-roman-fonts                 noarch 0:20200910-27.fc44                    fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-nimbus-sans-fonts                  noarch 0:20200910-27.fc44                    fedora                             2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-p052-fonts                         noarch 0:20200910-27.fc44                    fedora                             1.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-standard-symbols-ps-fonts          noarch 0:20200910-27.fc44                    fedora                            64.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  urw-base35-z003-fonts                         noarch 0:20200910-27.fc44                    fedora                           390.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  usb_modeswitch-data                           noarch 0:20191128-15.fc44                    fedora                           130.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  usbmuxd                                       x86_64 0:1.1.1^20240915git0b1b233-7.fc44     fedora                           149.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  usbredir                                      x86_64 0:0.15.0-3.fc44                       fedora                           109.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  usermode                                      x86_64 0:1.114-16.fc44                       fedora                           830.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  vazirmatn-vf-fonts                            noarch 0:33.003-16.fc44                      fedora                           286.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  vid.stab                                      x86_64 0:1.1.1-8.fc44                        fedora                            96.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  virglrenderer                                 x86_64 0:1.3.0-1.fc44                        fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  virt-what                                     x86_64 0:1.27-5.fc44                         fedora                            67.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  virtiofsd                                     x86_64 0:1.13.3-1.fc44                       fedora                             2.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  vo-amrwbenc                                   x86_64 0:0.1.3-24.fc44                       fedora                           157.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  volume_key-libs                               x86_64 0:0.3.12-29.fc44                      fedora                           694.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  vpnc                                          x86_64 0:0.5.3^20241114.git11e15a1-4.fc44    fedora                           230.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  vpnc-script                                   noarch 0:20230907-7.git5b9e7e4c.fc44         fedora                            38.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  vte291                                        x86_64 0:0.84.0-1.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  vte291-gtk4                                   x86_64 0:0.84.0-1.fc44                       fedora                             1.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  vulkan-loader                                 x86_64 0:1.4.341.0-1.fc44                    fedora                           577.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  wavpack                                       x86_64 0:5.9.0-2.fc44                        fedora                           586.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  webkit2gtk4.1                                 x86_64 0:2.52.3-1.fc44                       updates                           90.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  webkitgtk6.0                                  x86_64 0:2.52.3-1.fc44                       updates                           91.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  webrtc-audio-processing                       x86_64 0:2.1-5.fc44                          fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  wget2                                         x86_64 0:2.2.1-2.fc44                        fedora                             1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  wget2-libs                                    x86_64 0:2.2.1-2.fc44                        fedora                           369.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  wireless-regdb                                noarch 0:2026.03.18-1.fc44                   updates                           12.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  wireplumber-libs                              x86_64 0:0.5.14-1.fc44                       updates                            1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  wsdd                                          noarch 0:0.8-6.fc44                          fedora                            96.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util                                      x86_64 0:0.4.1-9.fc44                        fedora                            26.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util-cursor                               x86_64 0:0.1.6-2.fc44                        fedora                            23.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util-image                                x86_64 0:0.4.1-9.fc44                        fedora                            22.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util-keysyms                              x86_64 0:0.4.1-9.fc44                        fedora                            16.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util-renderutil                           x86_64 0:0.3.10-9.fc44                       fedora                            24.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  xcb-util-wm                                   x86_64 0:0.4.2-9.fc44                        fedora                            81.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-dbus-proxy                                x86_64 0:0.1.7-1.fc44                        updates                           90.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-user-dirs                                 x86_64 0:0.18-11.fc43                        fedora                           166.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdg-utils                                     noarch 0:1.2.1-5.fc44                        fedora                           346.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  xen-libs                                      x86_64 0:4.21.1-2.fc44                       updates                            1.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  xen-licenses                                  x86_64 0:4.21.1-2.fc44                       updates                          290.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  xevd-libs                                     x86_64 0:0.5.0-6.fc44                        fedora                           379.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  xeve-libs                                     x86_64 0:0.5.1-6.fc44                        fedora                           904.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  xhost                                         x86_64 0:1.0.9-11.fc44                       fedora                            25.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  xkbcomp                                       x86_64 0:1.5.0-2.fc44                        fedora                           225.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  xml-common                                    noarch 0:0.6.3-68.fc44                       fedora                            78.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmlrpc-c                                      x86_64 0:1.60.04-5.fc44                      fedora                           506.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmlrpc-c-client                               x86_64 0:1.60.04-5.fc44                      fedora                            51.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmlsec1                                       x86_64 1:1.2.41-4.fc44                       fedora                           570.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmlsec1-nss                                   x86_64 1:1.2.41-4.fc44                       fedora                           204.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmlsec1-openssl                               x86_64 1:1.2.41-4.fc44                       fedora                           285.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  xmodmap                                       x86_64 0:1.0.11-10.fc44                      fedora                            47.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  xorg-x11-server-Xwayland                      x86_64 0:24.1.11-1.fc44                      updates                            2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  xorg-x11-xauth                                x86_64 1:1.1.5-1.fc44                        fedora                            52.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  xorg-x11-xinit                                x86_64 0:1.4.3-4.fc44                        fedora                           142.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  xprop                                         x86_64 0:1.2.8-5.fc44                        fedora                            54.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  xrdb                                          x86_64 0:1.2.2-7.fc44                        fedora                            42.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  xvidcore                                      x86_64 0:1.3.7-19.fc44                       fedora                           878.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  yelp-libs                                     x86_64 2:49.0-2.fc44                         fedora                           298.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  yelp-xsl                                      noarch 0:49.0-2.fc44                         fedora                             1.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  zeromq                                        x86_64 0:4.3.5-22.fc43                       fedora                           894.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  zimg                                          x86_64 0:3.0.6-3.fc44                        fedora                           610.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  zix                                           x86_64 0:0.8.0-2.fc44                        fedora                            58.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  zlib-ng                                       x86_64 0:2.3.3-3.fc44                        fedora                           186.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  zvbi                                          x86_64 0:0.2.44-3.fc44                       fedora                             1.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  zxcvbn-c                                      x86_64 0:2.6-2.fc44                          fedora                             3.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  zxing-cpp                                     x86_64 0:2.2.1-6.fc44                        fedora                             1.3 MiB[0m
[1;32m==> proxmox-clone.fedora: Installing weak dependencies:[0m
[1;32m==> proxmox-clone.fedora:  adwaita-mono-fonts                            noarch 0:50.0-1.fc44                         fedora                             5.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  adwaita-sans-fonts                            noarch 0:50.0-1.fc44                         fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  apr-util-openssl                              x86_64 0:1.6.3-27.fc44                       fedora                            19.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  avahi-tools                                   x86_64 0:0.9~rc2-8.fc44                      fedora                            97.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  bolt                                          x86_64 0:0.9.11-1.fc44                       updates                          499.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  braille-printer-app                           x86_64 1:2.0~b0^386eea385f-11.fc44           fedora                           190.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  cifs-utils-info                               x86_64 0:7.5-1.fc44                          fedora                            38.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  cpp                                           x86_64 0:16.0.1-0.10.fc44                    fedora                            42.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  cups-filters-driverless                       x86_64 1:2.0.1-14.fc44                       fedora                            44.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  edk2-shell-x64                                noarch 0:20260213-6.fc44                     updates                            1.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  evince-djvu                                   x86_64 0:48.1-2.fc44                         fedora                            62.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  evolution-ews-core                            x86_64 0:3.60.1-1.fc44                       updates                            2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  exiv2                                         x86_64 0:0.28.6-3.fc44                       fedora                            12.2 MiB[0m
[1;32m==> proxmox-clone.fedora:  f2fs-tools                                    x86_64 0:1.16.0-10.fc44                      fedora                           578.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  fedora-chromium-config-gnome                  noarch 0:3.0-9.fc44                          fedora                            17.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  ffmpeg-free                                   x86_64 0:8.0.1-6.fc44                        fedora                             2.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  firefox-langpacks                             x86_64 0:150.0-1.fc44                        fedora                            42.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  fwupd-efi                                     x86_64 0:1.8-1.fc44                          fedora                           170.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  fwupd-plugin-flashrom                         x86_64 0:2.1.1-1.fc44                        fedora                            39.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  fwupd-plugin-modem-manager                    x86_64 0:2.1.1-1.fc44                        fedora                           125.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  fwupd-plugin-uefi-capsule-data                x86_64 0:2.1.1-1.fc44                        fedora                             7.0 MiB[0m
[1;32m==> proxmox-clone.fedora:  gdouros-symbola-fonts                         noarch 0:10.24-19.fc44                       fedora                             3.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-software-fedora-langpacks               x86_64 0:50.0-2.fc44                         fedora                            47.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  gnome-tour                                    x86_64 0:50.0-1.fc44                         updates                            2.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  google-noto-emoji-fonts                       noarch 0:20250623-4.fc44                     fedora                           884.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  gstreamer1-plugins-good-qt6                   x86_64 0:1.28.2-1.fc44                       updates                          232.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  hunspell-en                                   noarch 0:0.20260225-2.fc44                   updates                            7.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  ibus-setup                                    noarch 0:1.5.34-1.fc44                       updates                          331.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  intel-mediasdk                                x86_64 0:23.2.2-11.fc44                      updates                           24.5 MiB[0m
[1;32m==> proxmox-clone.fedora:  intel-vpl-gpu-rt                              x86_64 0:26.1.0-1.fc44                       fedora                            11.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  ipp-usb                                       x86_64 0:0.9.31-2.fc44                       fedora                             6.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  ipset                                         x86_64 0:7.24-3.fc44                         fedora                            72.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  jq                                            x86_64 0:1.8.1-3.fc44                        updates                          465.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  julietaula-montserrat-fonts                   noarch 1:9.000-4.fc44                        fedora                             5.6 MiB[0m
[1;32m==> proxmox-clone.fedora:  kernel-tools                                  x86_64 0:6.19.14-300.fc44                    updates                          927.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  langpacks-en                                  noarch 0:4.3-1.fc44                          fedora                           400.0   B[0m
[1;32m==> proxmox-clone.fedora:  libcamera-ipa                                 x86_64 0:0.7.0-1.fc44                        fedora                           725.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  libcap-ng-python3                             x86_64 0:0.9.2-1.fc44                        fedora                            90.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-gtk3                              x86_64 1:26.2.2.2-2.fc44                     updates                            1.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  libreoffice-help-en                           x86_64 1:26.2.2.2-2.fc44                     updates                           29.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  libvirt-daemon                                x86_64 0:12.0.0-3.fc44                       fedora                           735.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  libwnck3                                      x86_64 0:43.3-2.fc44                         fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  malcontent-control                            x86_64 0:0.14.0-1.fc44                       fedora                           267.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  mod_http2                                     x86_64 0:2.0.37-2.fc44                       fedora                           435.2 KiB[0m
[1;32m==> proxmox-clone.fedora:  mod_lua                                       x86_64 0:2.4.66-4.fc44                       fedora                           137.6 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit                                        x86_64 0:1.47.7-1.fc44                       updates                            0.0   B[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-curl-plugin                            x86_64 0:1.47.7-1.fc44                       updates                           62.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  nbdkit-ssh-plugin                             x86_64 0:1.47.7-1.fc44                       updates                           42.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  nilfs-utils                                   x86_64 0:2.2.11-8.fc44                       fedora                           467.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  nm-connection-editor                          x86_64 0:1.36.0-7.fc44                       fedora                             4.8 MiB[0m
[1;32m==> proxmox-clone.fedora:  ntfs-3g-system-compression                    x86_64 0:1.1-2.fc44                          fedora                            47.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  open-sans-fonts                               noarch 0:1.10-25.fc44                        fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  p11-kit-server                                x86_64 0:0.26.2-1.fc44                       fedora                            32.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  passim                                        x86_64 0:0.1.11-1.fc44                       updates                          232.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  perl-NDBM_File                                x86_64 0:1.18-524.fc44                       updates                           28.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  pipewire-plugin-libcamera                     x86_64 0:1.6.4-1.fc44                        updates                          146.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  polkit-pkla-compat                            x86_64 0:0.1-32.fc44                         fedora                            89.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-boto3                                 noarch 0:1.42.84-1.fc44                      updates                            2.4 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-file-magic                            noarch 0:5.46-9.fc44                         fedora                            28.5 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-httpx                                 noarch 0:0.28.1-11.fc44                      fedora                           992.1 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-langtable                             noarch 0:0.0.70-1.fc44                       fedora                             1.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-perf                                  x86_64 0:6.19.14-300.fc44                    updates                            9.7 MiB[0m
[1;32m==> proxmox-clone.fedora:  python3-pyaudio                               x86_64 0:0.2.13-11.fc44                      fedora                           127.4 KiB[0m
[1;32m==> proxmox-clone.fedora:  python3-regex                                 x86_64 0:2026.2.28-1.fc44                    fedora                             2.1 MiB[0m
[1;32m==> proxmox-clone.fedora:  qatlib-service                                x86_64 0:25.08.0-4.fc44                      fedora                            68.7 KiB[0m
[1;32m==> proxmox-clone.fedora:  qemu-kvm-core                                 x86_64 2:10.2.2-1.fc44                       fedora                             0.0   B[0m
[1;32m==> proxmox-clone.fedora:  qt6-qttranslations                            noarch 0:6.10.3-1.fc44                       updates                           15.3 MiB[0m
[1;32m==> proxmox-clone.fedora:  sane-backends-drivers-cameras                 x86_64 0:1.4.0-6.fc44                        fedora                           501.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  skopeo                                        x86_64 1:1.22.2-1.fc44                       updates                           24.9 MiB[0m
[1;32m==> proxmox-clone.fedora:  speech-dispatcher-utils                       x86_64 0:0.12.1-6.fc44                       fedora                            50.9 KiB[0m
[1;32m==> proxmox-clone.fedora:  tuned-ppd                                     noarch 0:2.27.0-1.fc44                       fedora                             7.0 KiB[0m
[1;32m==> proxmox-clone.fedora:  udftools                                      x86_64 0:2.3-13.fc44                         fedora                           431.3 KiB[0m
[1;32m==> proxmox-clone.fedora:  wl-clipboard                                  x86_64 0:2.2.1^git20251124.e808203-2.fc44    fedora                           148.8 KiB[0m
[1;32m==> proxmox-clone.fedora:  xdriinfo                                      x86_64 0:1.0.7-6.fc44                        fedora                            29.7 KiB[0m
[1;32m==> proxmox-clone.fedora: Installing groups dependencies:[0m
[1;32m==> proxmox-clone.fedora:  Fedora Workstation product core[0m
[1;32m==> proxmox-clone.fedora:  Printing Support[0m
[1;32m==> proxmox-clone.fedora:  Common NetworkManager Submodules[0m
[1;32m==> proxmox-clone.fedora:  Multimedia[0m
[1;32m==> proxmox-clone.fedora:  LibreOffice[0m
[1;32m==> proxmox-clone.fedora:  Hardware Support[0m
[1;32m==> proxmox-clone.fedora:  Guest Desktop Agents[0m
[1;32m==> proxmox-clone.fedora:  GNOME[0m
[1;32m==> proxmox-clone.fedora:  Fonts[0m
[1;32m==> proxmox-clone.fedora:  Firefox Web Browser[0m
[1;32m==> proxmox-clone.fedora:  Desktop accessibility[0m
[1;32m==> proxmox-clone.fedora:  base-graphical[0m
[1;32m==> proxmox-clone.fedora: Installing environmental groups:[0m
[1;32m==> proxmox-clone.fedora:  Fedora Workstation[0m
[1;32m==> proxmox-clone.fedora:[0m
[1;32m==> proxmox-clone.fedora: Transaction Summary:[0m
[1;32m==> proxmox-clone.fedora:  Installing:      1513 packages[0m
[1;32m==> proxmox-clone.fedora:  Upgrading:          8 packages[0m
[1;32m==> proxmox-clone.fedora:  Replacing:          8 packages[0m
[1;32m==> proxmox-clone.fedora:[0m
[1;31m==> proxmox-clone.fedora: [   1/1521] dracut-config-rescue-0:108- 100% |  23.8 KiB/s |  11.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [   2/1521] plymouth-system-theme-0:24. 100% |  18.9 KiB/s |   9.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [   3/1521] plymouth-0:24.004.60-24.fc4 100% | 333.4 KiB/s | 127.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [   4/1521] firewalld-0:2.4.0-2.fc44.no 100% | 392.6 KiB/s | 532.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [   5/1521] brltty-0:6.8-8.fc44.x86_64  100% | 796.6 KiB/s |   1.8 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [   6/1521] fedora-bookmarks-0:28-36.fc 100% | 313.3 KiB/s |  66.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [   7/1521] default-fonts-cjk-mono-0:4. 100% |  72.0 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [   8/1521] default-fonts-cjk-sans-0:4. 100% |  89.0 KiB/s |  11.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [   9/1521] default-fonts-cjk-serif-0:4 100% |  71.4 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  10/1521] default-fonts-core-emoji-0: 100% |  72.3 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  11/1521] default-fonts-core-math-0:4 100% |  71.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  12/1521] default-fonts-core-mono-0:4 100% |  73.2 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  13/1521] default-fonts-core-sans-0:4 100% | 228.3 KiB/s |  29.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  14/1521] default-fonts-core-serif-0: 100% |  70.8 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  15/1521] default-fonts-other-mono-0: 100% |  71.5 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  16/1521] default-fonts-other-sans-0: 100% |  85.6 KiB/s |  10.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  17/1521] default-fonts-other-serif-0 100% |  76.9 KiB/s |   9.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  18/1521] polkit-0:127-2.fc44.2.x86_6 100% | 578.5 KiB/s | 171.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  19/1521] gnome-initial-setup-0:50.0- 100% | 572.2 KiB/s | 560.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  20/1521] gnome-session-wayland-sessi 100% |  95.7 KiB/s |  13.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  21/1521] speech-dispatcher-0:0.12.1- 100% | 787.7 KiB/s |   4.6 MiB |  00m06s[0m
[1;31m==> proxmox-clone.fedora: [  22/1521] ptyxis-0:50.1-1.fc44.x86_64 100% | 694.8 KiB/s | 511.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  23/1521] yelp-2:49.0-2.fc44.x86_64   100% | 801.5 KiB/s | 857.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  24/1521] NetworkManager-wwan-1:1.56. 100% | 296.2 KiB/s |  58.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  25/1521] fprintd-pam-0:1.94.5-5.fc44 100% | 190.0 KiB/s |  22.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  26/1521] gnome-text-editor-0:50.0-1. 100% | 732.7 KiB/s | 781.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  27/1521] NetworkManager-openconnect- 100% | 421.1 KiB/s |  46.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  28/1521] NetworkManager-ppp-1:1.56.0 100% | 288.1 KiB/s |  33.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  29/1521] NetworkManager-openvpn-gnom 100% | 384.4 KiB/s |  72.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  30/1521] NetworkManager-vpnc-gnome-1 100% | 365.2 KiB/s |  40.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  31/1521] gvfs-smb-0:1.60.0-1.fc44.x8 100% | 247.1 KiB/s |  41.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  32/1521] xdg-user-dirs-gtk-0:0.16-2. 100% | 462.0 KiB/s |  90.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  33/1521] NetworkManager-adsl-1:1.56. 100% | 207.6 KiB/s |  25.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  34/1521] gvfs-archive-0:1.60.0-1.fc4 100% | 169.4 KiB/s |  23.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  35/1521] PackageKit-command-not-foun 100% | 213.6 KiB/s |  24.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  36/1521] gvfs-mtp-0:1.60.0-1.fc44.x8 100% | 253.6 KiB/s |  62.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  37/1521] gnome-disk-utility-0:46.1-4 100% | 818.6 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  38/1521] xdg-desktop-portal-gtk-0:1. 100% | 523.4 KiB/s | 143.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  39/1521] simple-scan-0:49.1-2.fc44.x 100% | 840.5 KiB/s |   1.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [  40/1521] gvfs-gphoto2-0:1.60.0-1.fc4 100% | 276.5 KiB/s |  61.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  41/1521] showtime-0:50.0-1.fc44.noar 100% | 562.1 KiB/s | 201.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  42/1521] gnome-system-monitor-0:50.0 100% | 723.9 KiB/s |   1.1 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [  43/1521] glycin-thumbnailer-0:2.1.1- 100% | 610.5 KiB/s | 228.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  44/1521] adobe-source-code-pro-fonts 100% | 807.9 KiB/s | 806.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  45/1521] gnome-calendar-0:50.0-1.fc4 100% | 787.8 KiB/s | 679.1 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  46/1521] gnome-color-manager-0:3.36. 100% | 805.3 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  47/1521] gnome-clocks-0:50.0-1.fc44. 100% | 841.8 KiB/s |   2.0 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [  48/1521] gnome-epub-thumbnailer-0:1. 100% | 217.4 KiB/s |  28.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  49/1521] gnome-contacts-0:50.0-1.fc4 100% | 710.2 KiB/s | 554.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  50/1521] gvfs-afc-0:1.60.0-1.fc44.x8 100% | 228.8 KiB/s |  57.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  51/1521] gvfs-afp-0:1.60.0-1.fc44.x8 100% | 339.9 KiB/s |  69.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  52/1521] gnome-logs-0:50.0-1.fc44.x8 100% | 790.1 KiB/s | 723.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  53/1521] baobab-0:50.0-1.fc44.x86_64 100% | 776.4 KiB/s | 514.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  54/1521] gnome-boxes-0:50.0-1.fc44.x 100% |   1.2 MiB/s |   1.2 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  55/1521] gnome-browser-connector-0:4 100% | 561.0 KiB/s |  65.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  56/1521] gnome-characters-0:50.0-1.f 100% |   3.3 MiB/s | 460.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  57/1521] gnome-connections-0:50.0-1. 100% |   2.1 MiB/s | 321.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  58/1521] gnome-font-viewer-0:50.0-1. 100% |   1.8 MiB/s | 269.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  59/1521] gnome-user-docs-0:50.0-1.fc 100% |   6.5 MiB/s |  16.8 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [  60/1521] gnome-user-share-0:48.2-1.f 100% |   2.1 MiB/s | 330.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  61/1521] gnome-weather-0:50.0-1.fc44 100% |   1.1 MiB/s | 213.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  62/1521] gst-thumbnailers-0:1.0.0-1. 100% |   3.5 MiB/s | 432.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  63/1521] gvfs-goa-0:1.60.0-1.fc44.x8 100% | 511.3 KiB/s |  59.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  64/1521] loupe-0:50.0-1.fc44.x86_64  100% |   3.3 MiB/s |   2.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  65/1521] snapshot-0:50.0-1.fc44.x86_ 100% |   3.4 MiB/s |   1.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  66/1521] sushi-0:50~rc.1-1.fc44.x86_ 100% |   1.1 MiB/s | 138.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  67/1521] vte-profile-0:0.84.0-1.fc44 100% | 249.1 KiB/s |  28.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  68/1521] xdg-desktop-portal-gnome-0: 100% |   2.4 MiB/s | 277.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  69/1521] hyperv-daemons-0:6.10-3.fc4 100% |  66.5 KiB/s |   7.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  70/1521] open-vm-tools-desktop-0:13. 100% |   1.4 MiB/s | 164.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  71/1521] spice-vdagent-0:0.23.0-2.fc 100% | 776.2 KiB/s |  90.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  72/1521] spice-webdavd-0:3.0-13.fc44 100% | 256.4 KiB/s |  28.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  73/1521] virtualbox-guest-additions- 100% |   2.6 MiB/s | 746.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  74/1521] alsa-sof-firmware-0:2025.12 100% |   4.9 MiB/s |  10.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [  75/1521] b43-fwcutter-0:019-41.fc44. 100% | 262.6 KiB/s |  29.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  76/1521] b43-openfwwf-0:5.2-48.fc44. 100% | 192.1 KiB/s |  22.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  77/1521] intel-lpmd-0:0.0.9-3.fc44.x 100% | 515.6 KiB/s |  84.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  78/1521] usb_modeswitch-0:2.6.2-5.fc 100% | 619.7 KiB/s |  73.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  79/1521] alsa-utils-0:1.2.15.2-3.fc4 100% |   4.3 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  80/1521] alsa-ucm-0:1.2.15.3-3.fc44. 100% |   2.6 MiB/s | 321.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  81/1521] NetworkManager-bluetooth-1: 100% | 446.5 KiB/s |  52.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  82/1521] NetworkManager-wifi-1:1.56. 100% |   1.1 MiB/s | 136.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  83/1521] dnsmasq-0:2.92-4.fc44.x86_6 100% |   3.4 MiB/s | 385.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  84/1521] iptables-nft-0:1.8.11-13.fc 100% |   1.5 MiB/s | 186.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  85/1521] wpa_supplicant-1:2.11-9.fc4 100% |   3.5 MiB/s |   1.8 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  86/1521] cups-filters-1:2.0.1-14.fc4 100% |   1.7 MiB/s | 215.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  87/1521] cups-pk-helper-0:0.2.7-12.f 100% | 793.2 KiB/s |  93.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  88/1521] bluez-cups-0:5.86-4.fc44.x8 100% | 257.6 KiB/s |  30.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  89/1521] colord-0:1.4.8-4.fc44.x86_6 100% |   2.1 MiB/s | 595.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  90/1521] cups-browsed-1:2.1.1-7.fc44 100% |   1.2 MiB/s | 142.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  91/1521] gutenprint-cups-0:5.3.5-7.f 100% |   2.1 MiB/s | 605.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  92/1521] hplip-0:3.25.8-2.fc44.x86_6 100% |   5.3 MiB/s |  20.8 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [  93/1521] mpage-0:2.5.7-24.fc44.x86_6 100% | 506.4 KiB/s |  59.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  94/1521] paps-0:0.8.0-15.fc44.x86_64 100% | 968.5 KiB/s | 115.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  95/1521] system-config-printer-udev- 100% | 239.1 KiB/s |  28.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  96/1521] microcode_ctl-2:2.1-74.fc44 100% |   4.4 MiB/s |  13.1 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [  97/1521] realmd-0:0.17.1-19.fc44.x86 100% |   2.0 MiB/s | 253.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [  98/1521] toolbox-0:0.3-4.fc44.x86_64 100% |   5.3 MiB/s |   3.6 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [  99/1521] bash-color-prompt-0:0.7.1-3 100% | 179.9 KiB/s |  20.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 100/1521] bzip2-0:1.0.8-23.fc44.x86_6 100% | 449.2 KiB/s |  52.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 101/1521] cifs-utils-0:7.5-1.fc44.x86 100% | 952.8 KiB/s | 115.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 102/1521] cryptsetup-0:2.8.4-1.fc44.x 100% |   2.9 MiB/s | 353.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 103/1521] fedora-flathub-remote-0:1-1 100% | 105.8 KiB/s |  12.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 104/1521] fedora-workstation-reposito 100% |  85.1 KiB/s |   9.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 105/1521] ntfs-3g-2:2022.10.3-12.fc44 100% |   1.1 MiB/s | 133.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 106/1521] ntfsprogs-2:2022.10.3-12.fc 100% |   2.2 MiB/s | 383.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 107/1521] wget2-wget-0:2.2.1-2.fc44.x 100% |  81.9 KiB/s |   9.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 108/1521] NetworkManager-config-conne 100% |  94.4 KiB/s |  10.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 109/1521] dosfstools-0:4.2-18.fc44.x8 100% | 890.0 KiB/s | 105.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 110/1521] exfatprogs-0:1.3.2-1.fc44.x 100% | 892.4 KiB/s | 106.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 111/1521] fpaste-0:0.5.0.0-4.fc44.noa 100% | 290.5 KiB/s |  33.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 112/1521] ibus-chewing-0:2.1.7-2.fc44 100% | 738.2 KiB/s |  88.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 113/1521] ibus-hangul-0:1.5.5-12.fc44 100% | 641.1 KiB/s |  75.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 114/1521] ibus-libpinyin-0:1.16.5-3.f 100% |   4.5 MiB/s | 902.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 115/1521] ibus-m17n-0:1.4.38-1.fc44.x 100% |   1.1 MiB/s | 130.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 116/1521] mdadm-0:4.3-11.fc44.x86_64  100% |   3.7 MiB/s | 459.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 117/1521] mtr-2:0.95-14.fc44.x86_64   100% | 758.6 KiB/s |  88.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 118/1521] nmap-ncat-4:7.92-8.fc44.x86 100% |   1.9 MiB/s | 231.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 119/1521] tcpdump-14:4.99.6-3.fc44.x8 100% |   1.0 MiB/s | 518.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 120/1521] whois-0:5.6.6-1.fc44.x86_64 100% | 566.3 KiB/s |  66.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 121/1521] abrt-cli-0:2.17.8-3.fc44.x8 100% |  82.3 KiB/s |   9.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 122/1521] acl-0:2.3.2-6.fc44.x86_64   100% | 168.3 KiB/s |  74.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 123/1521] attr-0:2.5.2-8.fc44.x86_64  100% | 324.2 KiB/s |  61.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 124/1521] bc-0:1.08.2-4.fc44.x86_64   100% | 470.3 KiB/s | 125.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 125/1521] compsize-0:1.5^git20250123. 100% | 175.9 KiB/s |  19.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 126/1521] deltarpm-0:3.6.5-8.fc44.x86 100% | 493.8 KiB/s |  93.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 127/1521] dos2unix-0:7.5.3-3.fc44.x86 100% | 686.2 KiB/s | 297.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 128/1521] iptstate-0:2.2.7-11.fc44.x8 100% | 274.9 KiB/s |  52.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 129/1521] logrotate-0:3.22.0-5.fc44.x 100% | 403.5 KiB/s |  77.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 130/1521] lrzsz-0:0.12.20-76.fc44.x86 100% | 459.0 KiB/s |  88.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 131/1521] lsof-0:4.98.0-9.fc44.x86_64 100% | 644.5 KiB/s | 227.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 132/1521] mailcap-0:2.1.54-10.fc44.no 100% | 298.6 KiB/s |  34.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 133/1521] man-pages-0:6.13-3.fc44.noa 100% | 862.5 KiB/s |   3.7 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [ 134/1521] mcelog-3:175-14.fc44.x86_64 100% | 378.6 KiB/s |  74.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 135/1521] net-tools-0:2.0-0.77.201609 100% | 743.6 KiB/s | 263.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 136/1521] passwdqc-0:2.0.3-9.fc44.x86 100% |  70.5 KiB/s |   8.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 137/1521] pinfo-0:0.6.13-10.fc44.x86_ 100% | 525.2 KiB/s | 103.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 138/1521] plocate-0:1.1.24-1.fc44.x86 100% | 661.8 KiB/s | 182.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 139/1521] psacct-0:6.6.4-26.fc44.x86_ 100% | 437.6 KiB/s |  87.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 140/1521] quota-1:4.11-2.fc44.x86_64  100% | 558.0 KiB/s | 197.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 141/1521] symlinks-0:1.7-14.fc44.x86_ 100% | 150.9 KiB/s |  17.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 142/1521] thermald-0:2.5.9-3.fc44.x86 100% |   1.2 MiB/s | 248.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 143/1521] time-0:1.9-28.fc44.x86_64   100% | 389.6 KiB/s |  46.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 144/1521] traceroute-3:2.1.6-4.fc44.x 100% | 511.0 KiB/s |  60.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 145/1521] tree-0:2.2.1-4.fc44.x86_64  100% | 540.1 KiB/s |  62.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 146/1521] usbutils-0:019-2.fc44.x86_6 100% | 968.1 KiB/s | 115.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 147/1521] words-0:3.0-63.fc44.noarch  100% |   4.4 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 148/1521] zip-0:3.0-45.fc44.x86_64    100% |   2.3 MiB/s | 264.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 149/1521] desktop-backgrounds-gnome-0 100% |  80.6 KiB/s |   8.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 150/1521] fedora-chromium-config-0:3. 100% | 133.3 KiB/s |  14.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 151/1521] fedora-release-workstation- 100% | 112.3 KiB/s |  12.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 152/1521] fedora-workstation-backgrou 100% |   5.9 MiB/s |   5.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 153/1521] gnome-shell-extension-backg 100% | 182.8 KiB/s |  21.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 154/1521] policycoreutils-python-util 100% | 413.9 KiB/s |  50.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 155/1521] unoconv-0:0.9.0-18.fc44.noa 100% | 480.5 KiB/s |  56.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 156/1521] uresourced-0:0.5.4-5.fc44.x 100% | 578.3 KiB/s |  68.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 157/1521] plymouth-theme-spinner-0:24 100% |   1.6 MiB/s | 188.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 158/1521] firewalld-filesystem-0:2.4. 100% |  87.0 KiB/s |  10.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 159/1521] python3-firewall-0:2.4.0-2. 100% |   4.0 MiB/s | 516.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 160/1521] plymouth-core-libs-0:24.004 100% |   1.0 MiB/s | 125.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 161/1521] plymouth-scripts-0:24.004.6 100% | 150.8 KiB/s |  18.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 162/1521] alsa-lib-0:1.2.15.3-3.fc44. 100% |   1.5 MiB/s | 562.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 163/1521] dotconf-0:1.4.1-7.fc44.x86_ 100% | 269.0 KiB/s |  31.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 164/1521] libao-0:1.2.0-31.fc44.x86_6 100% | 448.3 KiB/s |  53.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 165/1521] libsndfile-0:1.2.2-11.fc44. 100% |   1.8 MiB/s | 224.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 166/1521] pulseaudio-libs-0:17.0-9.fc 100% |   2.5 MiB/s | 705.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 167/1521] speech-dispatcher-espeak-ng 100% | 292.3 KiB/s |  33.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 168/1521] speech-dispatcher-libs-0:0. 100% | 386.5 KiB/s |  42.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 169/1521] bluez-libs-0:5.86-4.fc44.x8 100% | 741.9 KiB/s |  84.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 170/1521] brlapi-0:0.8.7-8.fc44.x86_6 100% |   1.6 MiB/s | 192.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 171/1521] libicu-0:77.1-2.fc44.x86_64 100% |   4.6 MiB/s |  10.8 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 172/1521] pcre2-utf32-0:10.47-1.fc44. 100% |   2.1 MiB/s | 242.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 173/1521] polkit-libs-0:127-2.fc44.2. 100% | 632.9 KiB/s |  72.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 174/1521] cairo-0:1.18.4-6.fc44.x86_6 100% |   3.8 MiB/s | 756.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 175/1521] cairo-gobject-0:1.18.4-6.fc 100% | 151.8 KiB/s |  17.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 176/1521] fdk-aac-free-0:2.0.3-2.fc44 100% |   3.0 MiB/s | 350.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 177/1521] fontconfig-0:2.17.0-4.fc44. 100% |   2.4 MiB/s | 278.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 178/1521] gdk-pixbuf2-0:2.44.4-2.fc44 100% |   4.2 MiB/s | 489.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 179/1521] gtk3-0:3.24.52-1.fc44.x86_6 100% |   6.1 MiB/s |   6.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 180/1521] libX11-0:1.8.13-1.fc44.x86_ 100% |   2.4 MiB/s | 676.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 181/1521] libX11-xcb-0:1.8.13-1.fc44. 100% |  94.1 KiB/s |  11.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 182/1521] libXcomposite-0:0.4.6-7.fc4 100% | 217.8 KiB/s |  24.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 183/1521] libXdamage-0:1.1.6-7.fc44.x 100% | 213.5 KiB/s |  23.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 184/1521] libXext-0:1.3.6-5.fc44.x86_ 100% | 357.2 KiB/s |  40.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 185/1521] libXfixes-0:6.0.1-7.fc44.x8 100% | 173.9 KiB/s |  19.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 186/1521] libXrandr-0:1.5.4-7.fc44.x8 100% | 252.8 KiB/s |  27.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 187/1521] libjpeg-turbo-0:3.1.3-1.fc4 100% |   2.1 MiB/s | 243.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 188/1521] gnome-backgrounds-0:50.0-1. 100% | 882.2 KiB/s |  37.2 MiB |  00m43s[0m
[1;31m==> proxmox-clone.fedora: [ 189/1521] libvpx-0:1.15.0-5.fc44.x86_ 100% |   3.3 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 190/1521] libxcb-0:1.17.0-7.fc44.x86_ 100% |   2.1 MiB/s | 238.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 191/1521] mozilla-filesystem-0:1.9-38 100% |  78.0 KiB/s |   8.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 192/1521] nspr-0:4.38.2-9.fc44.x86_64 100% |   1.3 MiB/s | 143.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 193/1521] nss-0:3.122.1-1.fc44.x86_64 100% |   2.7 MiB/s | 757.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 194/1521] nss-util-0:3.122.1-1.fc44.x 100% | 800.3 KiB/s |  90.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 195/1521] libwebp-0:1.6.0-3.fc44.x86_ 100% | 362.5 KiB/s | 329.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 196/1521] pango-0:1.57.1-1.fc44.x86_6 100% |   1.9 MiB/s | 366.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 197/1521] pixman-0:0.46.2-3.fc44.x86_ 100% | 690.1 KiB/s | 297.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 198/1521] google-noto-sans-mono-cjk-v 100% |   5.5 MiB/s |  14.4 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 199/1521] google-noto-serif-cjk-vf-fo 100% |   5.3 MiB/s |  19.9 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [ 200/1521] google-noto-color-emoji-fon 100% |   4.5 MiB/s |   2.3 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 201/1521] google-noto-sans-math-fonts 100% |   3.3 MiB/s | 414.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 202/1521] google-noto-sans-symbols-2- 100% |   2.3 MiB/s | 283.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 203/1521] google-noto-sans-symbols-vf 100% |   1.0 MiB/s | 125.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 204/1521] stix-fonts-0:2.13b171-10.fc 100% |   4.1 MiB/s |   1.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 205/1521] google-noto-sans-mono-vf-fo 100% |   2.3 MiB/s | 277.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 206/1521] abattis-cantarell-vf-fonts- 100% |   1.0 MiB/s | 120.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 207/1521] google-noto-sans-vf-fonts-0 100% |   2.4 MiB/s | 614.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 208/1521] google-noto-serif-vf-fonts- 100% |   3.3 MiB/s | 666.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 209/1521] default-fonts-am-0:4.3-1.fc 100% |  76.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 210/1521] default-fonts-ar-0:4.3-1.fc 100% |  83.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 211/1521] default-fonts-as-0:4.3-1.fc 100% |  79.1 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 212/1521] default-fonts-ast-0:4.3-1.f 100% |  78.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 213/1521] default-fonts-be-0:4.3-1.fc 100% |  77.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 214/1521] default-fonts-bg-0:4.3-1.fc 100% |  77.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 215/1521] default-fonts-bn-0:4.3-1.fc 100% |  78.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 216/1521] default-fonts-bo-0:4.3-1.fc 100% |  76.9 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 217/1521] default-fonts-br-0:4.3-1.fc 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 218/1521] default-fonts-chr-0:4.3-1.f 100% |  76.5 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 219/1521] default-fonts-dv-0:4.3-1.fc 100% |  78.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 220/1521] default-fonts-dz-0:4.3-1.fc 100% |  79.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 221/1521] default-fonts-el-0:4.3-1.fc 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 222/1521] default-fonts-eo-0:4.3-1.fc 100% |  76.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 223/1521] default-fonts-eu-0:4.3-1.fc 100% |  83.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 224/1521] default-fonts-fa-0:4.3-1.fc 100% |  76.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 225/1521] default-fonts-got-0:4.3-1.f 100% |  77.8 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 226/1521] default-fonts-gu-0:4.3-1.fc 100% |  32.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 227/1521] default-fonts-he-0:4.3-1.fc 100% |  77.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 228/1521] default-fonts-hi-0:4.3-1.fc 100% |  82.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 229/1521] default-fonts-hy-0:4.3-1.fc 100% |  76.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 230/1521] default-fonts-ia-0:4.3-1.fc 100% |  76.7 KiB/s |   9.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 231/1521] default-fonts-ii-0:4.3-1.fc 100% |  79.1 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 232/1521] default-fonts-iu-0:4.3-1.fc 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 233/1521] default-fonts-ka-0:4.3-1.fc 100% |  77.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 234/1521] default-fonts-kab-0:4.3-1.f 100% |  76.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 235/1521] default-fonts-km-0:4.3-1.fc 100% |  77.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 236/1521] default-fonts-kn-0:4.3-1.fc 100% |  77.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 237/1521] default-fonts-ku-0:4.3-1.fc 100% |  76.6 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 238/1521] default-fonts-lo-0:4.3-1.fc 100% |  78.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 239/1521] default-fonts-mai-0:4.3-1.f 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 240/1521] default-fonts-ml-0:4.3-1.fc 100% |  78.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 241/1521] default-fonts-mni-0:4.3-1.f 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 242/1521] default-fonts-mr-0:4.3-1.fc 100% |  77.1 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 243/1521] default-fonts-my-0:4.3-1.fc 100% |  76.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 244/1521] default-fonts-nb-0:4.3-1.fc 100% |  76.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 245/1521] default-fonts-ne-0:4.3-1.fc 100% |  75.5 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 246/1521] default-fonts-nn-0:4.3-1.fc 100% |  76.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 247/1521] default-fonts-nqo-0:4.3-1.f 100% |  76.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 248/1521] default-fonts-nr-0:4.3-1.fc 100% |  78.1 KiB/s |   9.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 249/1521] default-fonts-nso-0:4.3-1.f 100% |  76.8 KiB/s |   9.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 250/1521] default-fonts-or-0:4.3-1.fc 100% |  76.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 251/1521] default-fonts-pa-0:4.3-1.fc 100% |  77.7 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 252/1521] default-fonts-ru-0:4.3-1.fc 100% |  76.6 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 253/1521] default-fonts-sat-0:4.3-1.f 100% |  79.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 254/1521] default-fonts-si-0:4.3-1.fc 100% |  79.1 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 255/1521] default-fonts-ss-0:4.3-1.fc 100% |  80.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 256/1521] default-fonts-syr-0:4.3-1.f 100% |  77.1 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 257/1521] default-fonts-ta-0:4.3-1.fc 100% |  76.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 258/1521] default-fonts-te-0:4.3-1.fc 100% |  76.4 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 259/1521] default-fonts-th-0:4.3-1.fc 100% |  76.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 260/1521] default-fonts-tn-0:4.3-1.fc 100% |  76.6 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 261/1521] default-fonts-ts-0:4.3-1.fc 100% |  79.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 262/1521] default-fonts-uk-0:4.3-1.fc 100% |  78.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 263/1521] default-fonts-ur-0:4.3-1.fc 100% |  77.6 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 264/1521] default-fonts-ve-0:4.3-1.fc 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 265/1521] default-fonts-vi-0:4.3-1.fc 100% |  79.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 266/1521] default-fonts-xh-0:4.3-1.fc 100% |  79.3 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 267/1521] default-fonts-yi-0:4.3-1.fc 100% |  77.0 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 268/1521] default-fonts-zu-0:4.3-1.fc 100% |  77.2 KiB/s |   9.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 269/1521] google-noto-naskh-arabic-vf 100% | 456.5 KiB/s | 127.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 270/1521] google-noto-serif-armenian- 100% | 264.4 KiB/s |  31.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 271/1521] google-noto-serif-bengali-v 100% | 585.0 KiB/s | 161.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 272/1521] google-noto-sans-cjk-vf-fon 100% | 876.8 KiB/s |  13.7 MiB |  00m16s[0m
[1;31m==> proxmox-clone.fedora: [ 273/1521] google-noto-serif-devanagar 100% | 448.1 KiB/s | 120.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 274/1521] google-noto-serif-georgian- 100% | 463.6 KiB/s |  54.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 275/1521] google-noto-serif-ethiopic- 100% | 533.2 KiB/s | 144.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 276/1521] google-noto-serif-gurmukhi- 100% | 346.8 KiB/s |  40.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 277/1521] google-noto-serif-gujarati- 100% | 445.9 KiB/s |  86.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 278/1521] google-noto-serif-hebrew-vf 100% | 263.3 KiB/s |  28.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 279/1521] google-noto-serif-kannada-v 100% | 371.0 KiB/s |  89.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 280/1521] google-noto-serif-khmer-vf- 100% | 339.0 KiB/s |  64.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 281/1521] google-noto-serif-lao-vf-fo 100% | 301.9 KiB/s |  34.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 282/1521] google-noto-serif-oriya-vf- 100% | 483.0 KiB/s |  94.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 283/1521] google-noto-serif-sinhala-v 100% | 452.7 KiB/s |  85.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 284/1521] google-noto-serif-tamil-vf- 100% | 451.1 KiB/s |  88.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 285/1521] google-noto-serif-telugu-vf 100% | 501.2 KiB/s |  94.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 286/1521] google-noto-serif-thai-vf-f 100% | 306.1 KiB/s |  33.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 287/1521] duktape-0:2.7.0-11.fc44.x86 100% | 621.0 KiB/s | 172.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 288/1521] accountsservice-libs-0:23.1 100% | 360.2 KiB/s |  68.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 289/1521] rit-rachana-fonts-0:1.5.2-5 100% | 801.3 KiB/s | 984.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 290/1521] geoclue2-libs-0:2.8.0-2.fc4 100% | 286.5 KiB/s |  56.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 291/1521] geocode-glib-0:3.26.4-15.fc 100% | 358.4 KiB/s |  71.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 292/1521] gdm-1:50.0-1.fc44.x86_64    100% | 826.7 KiB/s | 945.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 293/1521] gnome-desktop4-0:44.5-1.fc4 100% | 555.3 KiB/s | 153.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 294/1521] libgweather-0:4.6.0-1.fc44. 100% | 637.6 KiB/s | 352.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 295/1521] libnma-gtk4-0:1.10.6-11.fc4 100% | 590.5 KiB/s | 110.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 296/1521] libadwaita-0:1.9.0-1.fc44.x 100% | 778.5 KiB/s | 762.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 297/1521] hicolor-icon-theme-0:0.18-3 100% | 336.8 KiB/s |  66.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 298/1521] json-glib-0:1.10.8-5.fc44.x 100% | 633.6 KiB/s | 175.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 299/1521] gnome-session-0:50.0-1.fc44 100% | 761.8 KiB/s | 384.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 300/1521] libportal-gtk4-0:0.9.1-4.fc 100% | 131.7 KiB/s |  17.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 301/1521] libportal-0:0.9.1-4.fc44.x8 100% | 438.3 KiB/s |  83.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 302/1521] yelp-libs-2:49.0-2.fc44.x86 100% | 549.6 KiB/s | 109.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 303/1521] vte291-gtk4-0:0.84.0-1.fc44 100% | 710.4 KiB/s | 422.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 304/1521] yelp-xsl-0:49.0-2.fc44.noar 100% | 631.6 KiB/s | 227.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 305/1521] editorconfig-libs-0:0.12.10 100% | 253.4 KiB/s |  28.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 306/1521] enchant2-0:2.8.15-1.fc44.x8 100% | 446.6 KiB/s |  85.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 307/1521] libspelling-0:0.4.10-1.fc44 100% | 531.3 KiB/s | 112.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 308/1521] ModemManager-glib-0:1.24.2- 100% | 656.1 KiB/s | 337.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 309/1521] fprintd-0:1.94.5-5.fc44.x86 100% | 665.1 KiB/s | 182.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 310/1521] gtksourceview5-0:5.20.0-1.f 100% | 804.4 KiB/s | 987.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 311/1521] gcr3-0:3.41.1-12.fc44.x86_6 100% | 790.8 KiB/s | 470.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 312/1521] NetworkManager-openconnect- 100% | 784.6 KiB/s | 580.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 313/1521] graphene-0:1.10.8-4.fc44.x8 100% | 242.7 KiB/s |  60.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 314/1521] gcr3-base-0:3.41.1-12.fc44. 100% | 648.4 KiB/s | 280.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 315/1521] libnma-0:1.10.6-11.fc44.x86 100% | 591.9 KiB/s | 110.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 316/1521] libsoup3-0:3.6.6-6.fc44.x86 100% | 690.6 KiB/s | 407.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 317/1521] vulkan-loader-0:1.4.341.0-1 100% | 618.8 KiB/s | 165.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 318/1521] openconnect-0:9.12-10.fc44. 100% | 792.2 KiB/s | 908.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 319/1521] NetworkManager-openvpn-1:1. 100% | 722.7 KiB/s | 311.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 320/1521] NetworkManager-vpnc-1:1.4.0 100% | 577.7 KiB/s | 159.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 321/1521] shared-mime-info-0:2.4-3.fc 100% | 797.7 KiB/s | 402.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 322/1521] gvfs-0:1.60.0-1.fc44.x86_64 100% | 658.5 KiB/s | 365.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 323/1521] gnome-keyring-0:50.0-1.fc44 100% | 806.3 KiB/s | 866.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 324/1521] xdg-user-dirs-0:0.18-11.fc4 100% | 436.2 KiB/s |  82.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 325/1521] libcanberra-gtk3-0:0.30-39. 100% | 284.7 KiB/s |  30.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 326/1521] libdvdread-0:7.0.1-1.fc44.x 100% | 446.4 KiB/s |  82.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 327/1521] gvfs-client-0:1.60.0-1.fc44 100% | 768.1 KiB/s | 764.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 328/1521] libnotify-0:0.8.8-1.fc44.x8 100% | 287.9 KiB/s |  56.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 329/1521] libhandy-0:1.8.3-10.fc44.x8 100% | 775.5 KiB/s | 397.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 330/1521] PackageKit-glib-0:1.3.4-3.f 100% | 596.1 KiB/s | 162.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 331/1521] libgudev-0:238-9.fc44.x86_6 100% | 306.0 KiB/s |  35.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 332/1521] libmtp-0:1.1.22-3.fc44.x86_ 100% | 581.2 KiB/s | 158.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 333/1521] PackageKit-0:1.3.4-3.fc44.x 100% | 809.6 KiB/s | 790.1 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 334/1521] libgusb-0:0.4.9-5.fc44.x86_ 100% | 333.6 KiB/s |  64.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 335/1521] colord-libs-0:1.4.8-4.fc44. 100% | 683.3 KiB/s | 233.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 336/1521] sane-backends-libs-0:1.4.0- 100% | 451.3 KiB/s |  48.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 337/1521] xdg-utils-0:1.2.1-5.fc44.no 100% | 408.8 KiB/s |  78.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 338/1521] glibmm2.68-0:2.88.0-1.fc44. 100% | 789.9 KiB/s | 778.1 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 339/1521] libgtop2-0:2.41.3-5.fc44.x8 100% | 543.7 KiB/s | 164.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 340/1521] gtkmm4.0-0:4.22.0-1.fc44.x8 100% | 819.6 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 341/1521] libgphoto2-0:2.5.33-2.fc44. 100% | 818.6 KiB/s |   1.4 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 342/1521] fonts-filesystem-1:5.0.0-2. 100% |  76.7 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 343/1521] librsvg2-0:2.62.0-1.fc44.x8 100% | 855.8 KiB/s |   1.9 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 344/1521] glycin-libs-0:2.1.1-1.fc44. 100% | 849.9 KiB/s |   1.5 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 345/1521] fribidi-0:1.0.16-4.fc44.x86 100% | 455.6 KiB/s |  53.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 346/1521] libical-0:3.0.20-7.fc44.x86 100% | 739.0 KiB/s | 262.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 347/1521] libical-glib-0:3.0.20-7.fc4 100% | 618.3 KiB/s | 120.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 348/1521] glycin-loaders-0:2.1.1-1.fc 100% |   1.3 MiB/s |   3.3 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 349/1521] lcms2-0:2.16-7.fc44.x86_64  100% | 719.4 KiB/s | 191.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 350/1521] folks-1:0.15.12-1.fc44.x86_ 100% |   2.2 MiB/s | 603.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 351/1521] libgee-0:0.20.8-3.fc44.x86_ 100% |   2.5 MiB/s | 284.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 352/1521] glycin-gtk4-libs-0:2.1.1-1. 100% | 559.5 KiB/s | 149.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 353/1521] libplist-0:2.6.0-6.fc44.x86 100% | 622.8 KiB/s |  99.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 354/1521] libimobiledevice-0:1.3.0^20 100% | 551.4 KiB/s | 146.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 355/1521] usbmuxd-0:1.1.1^20240915git 100% | 632.1 KiB/s |  68.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 356/1521] genisoimage-0:1.1.11-63.fc4 100% |   2.9 MiB/s | 332.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 357/1521] libosinfo-0:1.12.0-5.fc44.x 100% |   2.7 MiB/s | 317.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 358/1521] libportal-gtk3-0:0.9.1-4.fc 100% | 150.4 KiB/s |  17.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 359/1521] libvirt-client-0:12.0.0-3.f 100% |   3.8 MiB/s | 435.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 360/1521] adwaita-icon-theme-0:50.0-1 100% | 803.3 KiB/s | 404.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 361/1521] libvirt-daemon-config-netwo 100% | 129.8 KiB/s |  13.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 362/1521] libvirt-daemon-kvm-0:12.0.0 100% | 106.2 KiB/s |  11.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 363/1521] libvirt-gconfig-0:5.0.0-8.f 100% | 954.1 KiB/s | 102.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 364/1521] spice-glib-0:0.42-8.fc44.x8 100% |   3.3 MiB/s | 372.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 365/1521] libvirt-gobject-0:5.0.0-8.f 100% | 384.0 KiB/s |  72.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 366/1521] spice-gtk3-0:0.42-8.fc44.x8 100% | 358.5 KiB/s |  67.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 367/1521] gtk-vnc2-0:1.5.0-4.fc44.x86 100% | 384.3 KiB/s |  42.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 368/1521] freerdp-libs-2:3.24.2-1.fc4 100% |   3.9 MiB/s |   1.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 369/1521] gvncpulse-0:1.5.0-4.fc44.x8 100% | 356.8 KiB/s |  40.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 370/1521] gvnc-0:1.5.0-4.fc44.x86_64  100% | 584.5 KiB/s | 108.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 371/1521] httpd-0:2.4.66-4.fc44.x86_6 100% | 423.3 KiB/s |  46.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 372/1521] mod_dnssd-0:0.6-36.fc44.x86 100% | 241.9 KiB/s |  26.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 373/1521] msgraph-0:0.3.4-5.fc44.x86_ 100% | 532.4 KiB/s |  58.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 374/1521] gstreamer1-plugin-gtk4-0:0. 100% |   1.8 MiB/s | 344.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 375/1521] libwinpr-2:3.24.2-1.fc44.x8 100% | 697.2 KiB/s | 407.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 376/1521] evince-libs-0:48.1-2.fc44.x 100% |   1.9 MiB/s | 356.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 377/1521] libwayland-client-0:1.24.0- 100% | 323.1 KiB/s |  34.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 378/1521] libepoxy-0:1.5.10-12.fc44.x 100% | 667.8 KiB/s | 230.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 379/1521] hypervkvpd-0:6.10-3.fc44.x8 100% | 221.4 KiB/s |  24.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 380/1521] hypervvssd-0:6.10-3.fc44.x8 100% | 148.5 KiB/s |  16.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 381/1521] hypervfcopyd-0:6.10-3.fc44. 100% |  47.8 KiB/s |  16.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 382/1521] atkmm-0:2.28.4-7.fc44.x86_6 100% | 508.1 KiB/s |  95.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 383/1521] cairomm-0:1.14.5-15.fc44.x8 100% | 335.3 KiB/s |  62.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 384/1521] glibmm2.4-0:2.66.8-3.fc44.x 100% | 761.4 KiB/s | 690.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 385/1521] libXi-0:1.8.2-4.fc44.x86_64 100% | 357.0 KiB/s |  41.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 386/1521] libXinerama-0:1.1.5-10.fc44 100% | 120.2 KiB/s |  14.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 387/1521] libXtst-0:1.2.5-4.fc44.x86_ 100% | 181.2 KiB/s |  21.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 388/1521] firefox-0:150.0-1.fc44.x86_ 100% | 882.4 KiB/s |  84.0 MiB |  01m37s[0m
[1;31m==> proxmox-clone.fedora: [ 389/1521] gtkmm3.0-0:3.24.10-3.fc44.x 100% | 767.8 KiB/s |   1.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 390/1521] libsigc++20-0:2.12.1-7.fc44 100% | 354.1 KiB/s |  39.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 391/1521] libpciaccess-0:0.16-17.fc44 100% | 254.3 KiB/s |  27.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 392/1521] avahi-gobject-0:0.9~rc2-8.f 100% | 235.9 KiB/s |  25.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 393/1521] usb_modeswitch-data-0:20191 100% | 678.1 KiB/s | 186.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 394/1521] open-vm-tools-0:13.0.10-2.f 100% | 809.3 KiB/s | 863.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 395/1521] libsamplerate-0:0.2.2-12.fc 100% | 863.8 KiB/s |   1.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 396/1521] libcupsfilters-1:2.1.1-7.fc 100% | 762.9 KiB/s | 626.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 397/1521] color-filesystem-0:1-38.fc4 100% |  77.6 KiB/s |   8.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 398/1521] bluez-0:5.86-4.fc44.x86_64  100% | 860.0 KiB/s |   1.4 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 399/1521] libppd-1:2.1.1-3.fc44.x86_6 100% | 633.5 KiB/s | 266.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 400/1521] avahi-glib-0:0.9~rc2-8.fc44 100% | 143.8 KiB/s |  15.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 401/1521] avahi-libs-0:0.9~rc2-8.fc44 100% | 383.4 KiB/s |  71.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 402/1521] gutenprint-libs-0:5.3.5-7.f 100% | 563.1 KiB/s | 150.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 403/1521] hplip-libs-0:3.25.8-2.fc44. 100% | 637.4 KiB/s | 170.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 404/1521] keyutils-0:1.6.3-7.fc44.x86 100% | 390.9 KiB/s |  73.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 405/1521] fedora-third-party-0:0.10-1 100% | 410.3 KiB/s |  45.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 406/1521] ntfs-3g-libs-2:2022.10.3-12 100% | 694.3 KiB/s | 184.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 407/1521] wget2-0:2.2.1-2.fc44.x86_64 100% | 673.9 KiB/s | 292.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 408/1521] system-config-printer-libs- 100% | 824.2 KiB/s |   1.2 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 409/1521] gutenprint-0:5.3.5-7.fc44.x 100% | 868.7 KiB/s |   2.6 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 410/1521] libpinyin-0:2.11.91-2.fc44. 100% | 767.5 KiB/s | 330.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 411/1521] libhangul-0:0.2.0-3.fc44.x8 100% | 862.4 KiB/s |   2.0 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 412/1521] m17n-lib-0:1.8.6-3.fc44.x86 100% | 587.3 KiB/s | 206.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 413/1521] libreport-filesystem-0:2.17 100% |  88.2 KiB/s |   9.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 414/1521] libchewing-0:0.11.0-2.fc44. 100% | 855.2 KiB/s |   2.8 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 415/1521] libpcap-14:1.10.6-2.fc44.x8 100% | 707.5 KiB/s | 184.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 416/1521] abrt-addon-ccpp-0:2.17.8-3. 100% | 564.5 KiB/s | 105.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 417/1521] abrt-addon-kerneloops-0:2.1 100% | 391.5 KiB/s |  43.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 418/1521] abrt-addon-pstoreoops-0:2.1 100% | 175.5 KiB/s |  18.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 419/1521] abrt-addon-vmcore-0:2.17.8- 100% | 256.1 KiB/s |  27.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 420/1521] abrt-0:2.17.8-3.fc44.x86_64 100% | 799.6 KiB/s | 534.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 421/1521] abrt-addon-xorg-0:2.17.8-3. 100% | 207.8 KiB/s |  34.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 422/1521] abrt-plugin-bodhi-0:2.17.8- 100% | 173.4 KiB/s |  27.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 423/1521] abrt-tui-0:2.17.8-3.fc44.no 100% | 436.7 KiB/s |  48.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 424/1521] libreport-fedora-0:2.17.15- 100% | 155.2 KiB/s |  16.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 425/1521] libreport-plugin-bugzilla-0 100% | 421.8 KiB/s |  47.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 426/1521] libreport-plugin-logger-0:2 100% | 251.9 KiB/s |  27.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 427/1521] libreport-plugin-ureport-0: 100% | 286.1 KiB/s |  33.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 428/1521] python3-abrt-addon-0:2.17.8 100% | 177.2 KiB/s |  19.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 429/1521] passwdqc-utils-0:2.0.3-9.fc 100% | 350.7 KiB/s |  39.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 430/1521] quota-nls-1:4.11-2.fc44.noa 100% | 447.9 KiB/s |  85.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 431/1521] libevdev-0:1.13.6-2.fc44.x8 100% | 362.7 KiB/s |  39.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 432/1521] f44-backgrounds-gnome-0:44. 100% |  66.3 KiB/s |   7.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 433/1521] plymouth-plugin-two-step-0: 100% | 289.6 KiB/s |  33.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 434/1521] python3-nftables-1:1.1.6-2. 100% | 194.9 KiB/s |  21.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 435/1521] abattis-cantarell-fonts-0:0 100% | 632.1 KiB/s | 269.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 436/1521] gsm-0:1.0.24-2.fc44.x86_64  100% | 318.8 KiB/s |  36.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 437/1521] flac-libs-0:1.5.0-8.fc44.x8 100% | 644.8 KiB/s | 225.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 438/1521] libogg-2:1.3.6-2.fc44.x86_6 100% | 296.4 KiB/s |  33.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 439/1521] lame-libs-0:3.100-21.fc44.x 100% | 979.7 KiB/s | 341.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 440/1521] mpg123-libs-0:1.32.10-3.fc4 100% |   3.0 MiB/s | 362.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 441/1521] libvorbis-1:1.3.7-14.fc44.x 100% | 707.5 KiB/s | 191.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 442/1521] opus-0:1.6-2.fc44.x86_64    100% |   2.2 MiB/s | 255.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 443/1521] libasyncns-0:0.8-32.fc44.x8 100% | 266.8 KiB/s |  30.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 444/1521] libXrender-0:0.9.12-4.fc44. 100% | 249.0 KiB/s |  27.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 445/1521] xml-common-0:0.6.3-68.fc44. 100% | 278.0 KiB/s |  31.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 446/1521] gtk-update-icon-cache-0:3.2 100% | 302.6 KiB/s |  34.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 447/1521] libXcursor-0:1.2.3-4.fc44.x 100% | 282.5 KiB/s |  32.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 448/1521] libcloudproviders-0:0.4.0-1 100% | 413.0 KiB/s |  46.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 449/1521] libwayland-cursor-0:1.24.0- 100% | 171.8 KiB/s |  19.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 450/1521] libwayland-egl-0:1.24.0-3.f 100% | 116.6 KiB/s |  12.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 451/1521] libX11-common-0:1.8.13-1.fc 100% | 652.3 KiB/s | 175.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 452/1521] libXau-0:1.0.12-4.fc44.x86_ 100% | 309.4 KiB/s |  33.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 453/1521] espeak-ng-0:1.52.0-3.fc44.x 100% |   6.0 MiB/s |   9.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 454/1521] nss-sysinit-0:3.122.1-1.fc4 100% | 173.9 KiB/s |  19.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 455/1521] libXft-0:2.3.8-10.fc44.x86_ 100% | 669.0 KiB/s |  74.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 456/1521] nss-softokn-0:3.122.1-1.fc4 100% | 754.3 KiB/s | 440.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 457/1521] libthai-0:0.1.30-2.fc44.x86 100% |   1.9 MiB/s | 216.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 458/1521] google-noto-fonts-common-0: 100% | 161.2 KiB/s |  17.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 459/1521] google-noto-sans-ethiopic-v 100% |   1.6 MiB/s | 184.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 460/1521] google-noto-sans-bengali-vf 100% | 897.5 KiB/s |  98.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 461/1521] google-noto-sans-arabic-vf- 100% | 619.1 KiB/s | 118.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 462/1521] google-noto-sans-cherokee-v 100% | 796.0 KiB/s |  87.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 463/1521] google-noto-sans-thaana-vf- 100% | 269.7 KiB/s |  30.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 464/1521] vazirmatn-vf-fonts-0:33.003 100% |   1.3 MiB/s | 149.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 465/1521] google-noto-sans-gothic-fon 100% | 175.0 KiB/s |  19.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 466/1521] google-noto-sans-gujarati-v 100% | 738.8 KiB/s |  83.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 467/1521] jomolhari-fonts-0:0.003-45. 100% | 792.1 KiB/s | 527.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 468/1521] google-noto-sans-hebrew-vf- 100% | 242.9 KiB/s |  27.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 469/1521] google-noto-sans-armenian-v 100% | 269.4 KiB/s |  29.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 470/1521] google-noto-sans-devanagari 100% | 614.0 KiB/s | 116.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 471/1521] google-noto-sans-yi-fonts-0 100% | 794.6 KiB/s |  85.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 472/1521] google-noto-sans-georgian-v 100% | 415.0 KiB/s |  45.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 473/1521] google-noto-sans-canadian-a 100% | 347.8 KiB/s |  65.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 474/1521] google-noto-sans-khmer-vf-f 100% | 469.0 KiB/s |  50.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 475/1521] google-noto-sans-lao-vf-fon 100% | 274.6 KiB/s |  30.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 476/1521] rit-meera-new-fonts-0:1.6.2 100% |   1.3 MiB/s | 152.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 477/1521] google-noto-sans-meetei-may 100% | 277.9 KiB/s |  31.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 478/1521] google-noto-sans-kannada-vf 100% | 148.2 KiB/s |  75.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 479/1521] sil-padauk-fonts-0:3.003-21 100% |   2.9 MiB/s | 801.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 480/1521] madan-fonts-0:2.000-43.fc44 100% | 467.9 KiB/s |  88.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 481/1521] google-noto-sans-nko-fonts- 100% | 287.8 KiB/s |  31.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 482/1521] google-noto-sans-oriya-vf-f 100% | 498.3 KiB/s |  93.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 483/1521] google-noto-sans-gurmukhi-v 100% | 354.9 KiB/s |  38.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 484/1521] google-noto-sans-ol-chiki-v 100% | 279.2 KiB/s |  30.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 485/1521] google-noto-sans-sinhala-vf 100% | 412.9 KiB/s |  76.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 486/1521] google-noto-sans-syriac-vf- 100% | 452.7 KiB/s |  48.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 487/1521] google-noto-sans-tamil-vf-f 100% | 465.4 KiB/s |  50.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 488/1521] google-noto-sans-telugu-vf- 100% | 489.6 KiB/s |  92.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 489/1521] google-noto-sans-thai-vf-fo 100% | 284.9 KiB/s |  31.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 490/1521] paktype-naskh-basic-fonts-0 100% |   3.0 MiB/s | 589.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 491/1521] accountsservice-0:23.13.9-1 100% | 481.0 KiB/s | 128.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 492/1521] gnome-keyring-pam-0:50.0-1. 100% | 190.6 KiB/s |  20.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 493/1521] python3-pam-0:2.0.2-18.fc44 100% | 238.8 KiB/s |  27.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 494/1521] xorg-x11-xinit-0:1.4.3-4.fc 100% | 313.1 KiB/s |  59.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 495/1521] iso-codes-0:4.20.1-3.fc44.n 100% |   3.7 MiB/s |   4.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 496/1521] gnome-desktop3-0:44.5-1.fc4 100% | 806.0 KiB/s | 663.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 497/1521] appstream-0:1.1.0-3.fc44.x8 100% |   3.1 MiB/s | 874.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 498/1521] libnma-common-0:1.10.6-11.f 100% |   1.6 MiB/s | 190.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 499/1521] mobile-broadband-provider-i 100% | 600.4 KiB/s |  69.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 500/1521] simdutf-0:7.2.1-3.fc44.x86_ 100% |   1.4 MiB/s | 167.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 501/1521] gcr-libs-0:4.4.0.1-7.fc44.x 100% | 740.2 KiB/s | 501.1 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 502/1521] vte291-0:0.84.0-1.fc44.x86_ 100% |   2.6 MiB/s | 500.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 503/1521] hunspell-0:1.7.2-11.fc44.x8 100% |   2.6 MiB/s | 517.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 504/1521] libxslt-0:1.1.43-6.fc44.x86 100% | 721.8 KiB/s | 192.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 505/1521] libproxy-0:0.5.12-2.fc44.x8 100% | 420.6 KiB/s |  45.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 506/1521] libfprint-0:1.94.10-1.fc44. 100% |   1.8 MiB/s | 351.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 507/1521] libpskc-0:2.6.14-1.fc44.x86 100% | 322.2 KiB/s |  35.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 508/1521] pcsc-lite-libs-0:2.4.1-2.fc 100% | 310.8 KiB/s |  33.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 509/1521] stoken-libs-0:0.93-2.fc44.x 100% | 415.3 KiB/s |  46.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 510/1521] libpinyin-data-0:2.11.91-2. 100% | 883.8 KiB/s |   9.5 MiB |  00m11s[0m
[1;31m==> proxmox-clone.fedora: [ 511/1521] vpnc-script-0:20230907-7.gi 100% | 162.1 KiB/s |  17.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 512/1521] vpnc-0:0.5.3^20241114.git11 100% | 496.0 KiB/s | 102.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 513/1521] libcdio-0:2.3.0-1.fc44.x86_ 100% |   1.3 MiB/s | 255.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 514/1521] libbluray-0:1.4.0-3.fc44.x8 100% | 553.8 KiB/s | 149.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 515/1521] wsdd-0:0.8-6.fc44.noarch    100% | 363.2 KiB/s |  40.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 516/1521] libcdio-paranoia-0:10.2+2.0 100% | 459.1 KiB/s |  88.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 517/1521] desktop-file-utils-0:0.28-5 100% | 629.1 KiB/s |  69.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 518/1521] libcanberra-0:0.30-39.fc44. 100% | 455.8 KiB/s |  88.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 519/1521] pangomm2.48-0:2.56.1-3.fc44 100% | 788.0 KiB/s |  86.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 520/1521] cairomm1.16-0:1.18.0-16.fc4 100% | 351.6 KiB/s |  67.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 521/1521] gd-0:2.3.3-21.fc44.x86_64   100% | 509.2 KiB/s | 140.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 522/1521] libexif-0:0.6.26-1.fc44.x86 100% |   1.8 MiB/s | 512.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 523/1521] lockdev-0:1.0.4-0.54.201110 100% | 279.1 KiB/s |  32.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 524/1521] bubblewrap-0:0.11.0-4.fc44. 100% | 561.7 KiB/s |  66.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 525/1521] libdav1d-0:1.5.3-1.fc44.x86 100% | 775.5 KiB/s | 641.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 526/1521] libimobiledevice-glue-0:1.3 100% | 289.3 KiB/s |  55.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 527/1521] libjxl-1:0.11.1-8.fc44.x86_ 100% |   2.1 MiB/s |   1.2 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 528/1521] libusbmuxd-0:2.1.0-5.fc44.x 100% | 333.0 KiB/s |  37.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 529/1521] adwaita-cursor-theme-0:50.0 100% |   1.9 MiB/s | 380.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 530/1521] libheif-0:1.21.2-1.fc44.x86 100% | 806.2 KiB/s | 668.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 531/1521] libusal-0:1.1.11-63.fc44.x8 100% |   1.2 MiB/s | 136.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 532/1521] osinfo-db-tools-0:1.12.0-5. 100% | 636.1 KiB/s |  74.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 533/1521] osinfo-db-0:20251212-1.fc44 100% | 725.3 KiB/s | 491.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 534/1521] libvirt-daemon-driver-netwo 100% | 707.8 KiB/s | 250.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 535/1521] libvirt-daemon-common-0:12. 100% | 499.1 KiB/s | 137.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 536/1521] libvirt-daemon-driver-inter 100% | 563.3 KiB/s | 200.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 537/1521] libvirt-libs-0:12.0.0-3.fc4 100% |   3.3 MiB/s |   5.5 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 538/1521] libvirt-daemon-driver-nwfil 100% |   2.0 MiB/s | 236.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 539/1521] libvirt-daemon-driver-noded 100% | 643.8 KiB/s | 224.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 540/1521] libvirt-daemon-driver-secre 100% |   1.1 MiB/s | 197.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 541/1521] libvirt-daemon-driver-stora 100% |  95.5 KiB/s |  11.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 542/1521] libvirt-daemon-lock-0:12.0. 100% | 415.3 KiB/s |  48.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 543/1521] libvirt-daemon-log-0:12.0.0 100% | 457.2 KiB/s |  52.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 544/1521] libvirt-daemon-plugin-lockd 100% | 186.5 KiB/s |  22.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 545/1521] libvirt-daemon-proxy-0:12.0 100% |   1.6 MiB/s | 192.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 546/1521] adwaita-icon-theme-legacy-0 100% | 852.5 KiB/s |   2.5 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 547/1521] libvirt-ssh-proxy-0:12.0.0- 100% | 174.5 KiB/s |  19.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 548/1521] qemu-kvm-2:10.2.2-1.fc44.x8 100% | 139.5 KiB/s |  15.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 549/1521] libvirt-glib-0:5.0.0-8.fc44 100% | 479.2 KiB/s |  53.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 550/1521] libphodav-0:3.0-13.fc44.x86 100% | 565.7 KiB/s |  65.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 551/1521] libcacard-3:2.8.2-1.fc44.x8 100% | 262.3 KiB/s |  56.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 552/1521] libvirt-daemon-driver-qemu- 100% | 817.2 KiB/s |   1.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 553/1521] usbredir-0:0.15.0-3.fc44.x8 100% | 457.2 KiB/s |  51.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 554/1521] libwayland-server-0:1.24.0- 100% | 383.6 KiB/s |  42.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 555/1521] soxr-0:0.1.3-21.fc44.x86_64 100% | 808.7 KiB/s |  88.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 556/1521] libxkbfile-0:1.1.3-5.fc44.x 100% | 495.9 KiB/s |  93.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 557/1521] uriparser-0:1.0.0-2.fc44.x8 100% | 300.6 KiB/s |  72.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 558/1521] apr-0:1.7.6-5.fc44.x86_64   100% | 485.3 KiB/s | 133.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 559/1521] httpd-core-0:2.4.66-4.fc44. 100% |   4.0 MiB/s |   1.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 560/1521] gspell-0:1.14.3-1.fc44.x86_ 100% | 470.4 KiB/s | 125.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 561/1521] libspectre-0:0.2.12-11.fc44 100% | 406.7 KiB/s |  45.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 562/1521] libgxps-0:0.3.2-12.fc44.x86 100% | 411.8 KiB/s |  78.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 563/1521] poppler-glib-0:26.01.0-3.fc 100% |   1.9 MiB/s | 216.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 564/1521] hyperv-daemons-license-0:6. 100% | 137.0 KiB/s |  14.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 565/1521] pangomm-0:2.46.4-5.fc44.x86 100% | 606.5 KiB/s |  68.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 566/1521] libtiff-0:4.7.1-2.fc44.x86_ 100% | 662.2 KiB/s | 229.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 567/1521] xmlsec1-1:1.2.41-4.fc44.x86 100% |   1.7 MiB/s | 197.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 568/1521] libmspack-0:0.10.1-0.16.alp 100% | 414.3 KiB/s |  77.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 569/1521] poppler-cpp-0:26.01.0-3.fc4 100% | 308.8 KiB/s |  59.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 570/1521] qpdf-libs-0:12.3.2-1.fc44.x 100% |   3.7 MiB/s |   1.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 571/1521] hplip-common-0:3.25.8-2.fc4 100% | 637.2 KiB/s |  73.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 572/1521] poppler-utils-0:26.01.0-3.f 100% | 716.0 KiB/s | 305.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 573/1521] net-snmp-libs-1:5.9.5.2-4.f 100% |   3.8 MiB/s | 775.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 574/1521] python3-cups-0:2.0.4-8.fc44 100% | 454.9 KiB/s |  85.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 575/1521] wget2-libs-0:2.2.1-2.fc44.x 100% |   1.3 MiB/s | 151.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 576/1521] avahi-0:0.9~rc2-8.fc44.x86_ 100% | 777.8 KiB/s | 454.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 577/1521] m17n-db-0:1.8.10-3.fc44.noa 100% |   4.0 MiB/s | 816.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 578/1521] abrt-libs-0:2.17.8-3.fc44.x 100% | 318.2 KiB/s |  36.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 579/1521] dmidecode-1:3.6-9.fc44.x86_ 100% | 838.9 KiB/s |  98.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 580/1521] kyotocabinet-libs-0:1.2.80- 100% | 724.5 KiB/s | 366.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 581/1521] libreport-plugin-systemd-jo 100% | 157.2 KiB/s |  18.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 582/1521] python3-abrt-0:2.17.8-3.fc4 100% | 330.1 KiB/s |  39.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 583/1521] libibverbs-0:61.0-2.fc44.x8 100% | 725.7 KiB/s | 492.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 584/1521] python3-augeas-0:1.2.0-7.fc 100% | 458.7 KiB/s |  50.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 585/1521] libreport-0:2.17.15-10.fc44 100% | 787.5 KiB/s | 530.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 586/1521] satyr-0:0.43-10.fc44.x86_64 100% | 253.2 KiB/s | 129.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 587/1521] libreport-plugin-kerneloops 100% | 183.6 KiB/s |  21.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 588/1521] python3-libreport-0:2.17.15 100% | 532.9 KiB/s | 143.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 589/1521] kexec-tools-0:2.0.32-3.fc44 100% | 532.7 KiB/s | 103.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 590/1521] python3-systemd-0:235-18.fc 100% | 581.5 KiB/s | 108.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 591/1521] libreport-web-0:2.17.15-10. 100% | 288.5 KiB/s |  30.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 592/1521] libreport-cli-0:2.17.15-10. 100% | 214.3 KiB/s |  24.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 593/1521] abrt-dbus-0:2.17.8-3.fc44.x 100% | 333.9 KiB/s |  63.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 594/1521] python3-satyr-0:0.43-10.fc4 100% | 348.6 KiB/s |  41.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 595/1521] python3-argcomplete-0:3.6.3 100% | 520.6 KiB/s |  98.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 596/1521] libpasswdqc-0:2.0.3-9.fc44. 100% | 263.2 KiB/s |  51.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 597/1521] plymouth-graphics-libs-0:24 100% | 340.8 KiB/s |  64.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 598/1521] plymouth-plugin-label-0:24. 100% | 219.3 KiB/s |  26.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 599/1521] pcaudiolib-0:1.1-19.fc44.x8 100% | 246.2 KiB/s |  29.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 600/1521] nss-softokn-freebl-0:3.122. 100% | 731.8 KiB/s | 373.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 601/1521] libdatrie-0:0.2.14-2.fc44.x 100% | 282.5 KiB/s |  33.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 602/1521] setxkbmap-0:1.3.4-7.fc44.x8 100% | 186.3 KiB/s |  22.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 603/1521] xhost-0:1.0.9-11.fc44.x86_6 100% | 173.1 KiB/s |  20.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 604/1521] xmodmap-0:1.0.11-10.fc44.x8 100% | 277.5 KiB/s |  31.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 605/1521] xorg-x11-xauth-1:1.1.5-1.fc 100% | 291.0 KiB/s |  34.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 606/1521] xrdb-0:1.2.2-7.fc44.x86_64  100% | 244.4 KiB/s |  29.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 607/1521] gdb-headless-0:17.1-4.fc44. 100% | 873.5 KiB/s |   5.5 MiB |  00m06s[0m
[1;31m==> proxmox-clone.fedora: [ 608/1521] libfyaml-0:0.8-9.fc44.x86_6 100% | 597.3 KiB/s | 212.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 609/1521] libstemmer-0:3.0.1-11.fc44. 100% | 527.9 KiB/s | 146.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 610/1521] hunspell-filesystem-0:1.7.2 100% |  66.5 KiB/s |   7.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 611/1521] usermode-0:1.114-16.fc44.x8 100% | 669.5 KiB/s | 187.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 612/1521] libudfread-0:1.2.0-3.fc44.x 100% | 296.4 KiB/s |  34.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 613/1521] sound-theme-freedesktop-0:0 100% | 750.0 KiB/s | 382.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 614/1521] emacs-filesystem-1:30.2-2.f 100% |  71.8 KiB/s |   8.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 615/1521] libXpm-0:3.5.17-7.fc44.x86_ 100% | 352.8 KiB/s |  66.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 616/1521] libavif-0:1.3.0-4.fc44.x86_ 100% | 465.9 KiB/s | 125.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 617/1521] libimagequant-0:4.1.0-2.fc4 100% | 747.6 KiB/s | 323.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 618/1521] libopenjph-0:0.25.3-3.fc44. 100% | 584.5 KiB/s | 161.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 619/1521] appstream-data-0:44-4.fc44. 100% |   2.3 MiB/s |  15.0 MiB |  00m07s[0m
[1;31m==> proxmox-clone.fedora: [ 620/1521] openjpeg-0:2.5.4-3.fc44.x86 100% | 531.1 KiB/s | 198.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 621/1521] rav1e-libs-0:0.8.1-3.fc44.x 100% |   3.9 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 622/1521] highway-0:1.3.0-2.fc44.x86_ 100% |   2.5 MiB/s | 694.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 623/1521] libssh2-0:1.11.1-5.fc44.x86 100% |   1.3 MiB/s | 148.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 624/1521] libwsman1-0:2.8.1-14.fc44.x 100% |   1.2 MiB/s | 143.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 625/1521] iproute-tc-0:6.17.0-2.fc44. 100% |   2.4 MiB/s | 468.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 626/1521] mdevctl-0:1.4.0-3.fc44.x86_ 100% |   3.5 MiB/s | 956.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 627/1521] libnbd-0:1.25.4-1.fc44.x86_ 100% |   1.7 MiB/s | 191.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 628/1521] lzop-0:1.04-18.fc44.x86_64  100% | 502.8 KiB/s |  56.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 629/1521] numad-0:0.5-50.20251104git. 100% | 351.3 KiB/s |  39.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 630/1521] qemu-img-2:10.2.2-1.fc44.x8 100% |   4.0 MiB/s |   2.7 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 631/1521] f44-backgrounds-base-0:44.0 100% | 885.7 KiB/s |   9.3 MiB |  00m11s[0m
[1;31m==> proxmox-clone.fedora: [ 632/1521] swtpm-tools-0:0.10.1-3.fc44 100% |   1.0 MiB/s | 116.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 633/1521] libvirt-daemon-driver-stora 100% | 144.3 KiB/s |  22.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 634/1521] libvirt-daemon-driver-stora 100% | 222.7 KiB/s |  24.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 635/1521] svt-av1-libs-0:3.1.2-2.fc44 100% | 855.4 KiB/s |   2.0 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 636/1521] libvirt-daemon-driver-stora 100% | 730.3 KiB/s | 251.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 637/1521] libvirt-daemon-driver-stora 100% | 179.6 KiB/s |  19.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 638/1521] libvirt-daemon-driver-stora 100% | 204.6 KiB/s |  21.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 639/1521] libvirt-daemon-driver-stora 100% | 160.8 KiB/s |  17.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 640/1521] libvirt-daemon-driver-stora 100% | 143.5 KiB/s |  23.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 641/1521] libvirt-daemon-driver-stora 100% | 261.4 KiB/s |  27.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 642/1521] libvirt-daemon-driver-stora 100% | 178.3 KiB/s |  19.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 643/1521] qemu-system-x86-2:10.2.2-1. 100% | 155.4 KiB/s |  17.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 644/1521] apr-util-0:1.6.3-27.fc44.x8 100% | 943.7 KiB/s | 100.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 645/1521] apr-util-lmdb-0:1.6.3-27.fc 100% | 126.6 KiB/s |  13.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 646/1521] httpd-filesystem-0:2.4.66-4 100% | 109.1 KiB/s |  11.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 647/1521] httpd-tools-0:2.4.66-4.fc44 100% | 738.8 KiB/s |  79.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 648/1521] jbigkit-libs-0:2.1-33.fc44. 100% | 484.6 KiB/s |  54.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 649/1521] liblerc-0:4.0.0-10.fc44.x86 100% |   2.0 MiB/s | 225.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 650/1521] libdaemon-0:0.14-33.fc44.x8 100% | 288.7 KiB/s |  32.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 651/1521] gnutls-dane-0:3.8.12-1.fc44 100% | 351.8 KiB/s |  39.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 652/1521] rdma-core-common-0:61.0-2.f 100% | 155.4 KiB/s |  16.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 653/1521] python3-cffi-0:2.0.0-3.fc44 100% |   2.9 MiB/s | 324.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 654/1521] libbabeltrace-0:1.5.11-17.f 100% |   1.7 MiB/s | 200.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 655/1521] libipt-0:2.1.2-4.fc44.x86_6 100% | 548.7 KiB/s |  60.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 656/1521] source-highlight-0:3.1.9-27 100% |   2.9 MiB/s | 784.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 657/1521] xmlrpc-c-0:1.60.04-5.fc44.x 100% |   1.7 MiB/s | 190.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 658/1521] xmlrpc-c-client-0:1.60.04-5 100% | 274.1 KiB/s |  28.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 659/1521] dbus-tools-1:1.16.2-1.fc44. 100% | 414.8 KiB/s |  44.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 660/1521] libXmu-0:1.2.1-5.fc44.x86_6 100% | 710.5 KiB/s |  79.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 661/1521] libuser-0:0.64-17.fc44.x86_ 100% |   2.1 MiB/s | 404.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 662/1521] libyuv-0:0-0.61.20260213git 100% |   1.8 MiB/s | 209.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 663/1521] poppler-0:26.01.0-3.fc44.x8 100% | 821.9 KiB/s |   1.4 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 664/1521] swtpm-0:0.10.1-3.fc44.x86_6 100% | 307.3 KiB/s |  34.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 665/1521] scrub-0:2.6.1-12.fc44.x86_6 100% | 404.3 KiB/s |  43.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 666/1521] glusterfs-cli-0:11.2-5.fc44 100% |   1.6 MiB/s | 190.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 667/1521] gnutls-utils-0:3.8.12-1.fc4 100% | 724.3 KiB/s | 311.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 668/1521] glusterfs-fuse-0:11.2-5.fc4 100% |   1.3 MiB/s | 140.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 669/1521] libiscsi-0:1.20.3-4.fc44.x8 100% | 913.6 KiB/s | 100.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 670/1521] libgfapi0-0:11.2-5.fc44.x86 100% | 519.2 KiB/s |  98.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 671/1521] qemu-audio-alsa-2:10.2.2-1. 100% | 238.1 KiB/s |  25.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 672/1521] qemu-audio-jack-2:10.2.2-1. 100% | 218.0 KiB/s |  24.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 673/1521] qemu-audio-dbus-2:10.2.2-1. 100% | 414.6 KiB/s |  77.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 674/1521] qemu-audio-oss-2:10.2.2-1.f 100% | 217.0 KiB/s |  24.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 675/1521] qemu-audio-pa-2:10.2.2-1.fc 100% | 233.8 KiB/s |  25.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 676/1521] qemu-audio-pipewire-2:10.2. 100% | 295.8 KiB/s |  32.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 677/1521] qemu-audio-sdl-2:10.2.2-1.f 100% | 204.3 KiB/s |  22.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 678/1521] qemu-audio-spice-2:10.2.2-1 100% | 198.2 KiB/s |  21.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 679/1521] qemu-block-blkio-2:10.2.2-1 100% | 266.0 KiB/s |  27.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 680/1521] qemu-block-curl-2:10.2.2-1. 100% | 250.1 KiB/s |  27.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 681/1521] qemu-block-dmg-2:10.2.2-1.f 100% | 177.4 KiB/s |  19.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 682/1521] qemu-block-gluster-2:10.2.2 100% | 264.1 KiB/s |  28.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 683/1521] qemu-block-iscsi-2:10.2.2-1 100% | 333.9 KiB/s |  36.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 684/1521] qemu-block-nfs-2:10.2.2-1.f 100% | 250.8 KiB/s |  27.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 685/1521] qemu-block-rbd-2:10.2.2-1.f 100% | 286.2 KiB/s |  32.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 686/1521] qemu-block-ssh-2:10.2.2-1.f 100% | 275.4 KiB/s |  30.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 687/1521] qemu-char-baum-2:10.2.2-1.f 100% | 229.9 KiB/s |  24.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 688/1521] qemu-char-spice-2:10.2.2-1. 100% | 211.6 KiB/s |  23.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 689/1521] qemu-device-display-qxl-2:1 100% | 414.5 KiB/s |  45.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 690/1521] qemu-device-display-virtio- 100% | 375.7 KiB/s |  42.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 691/1521] qemu-device-display-virtio- 100% | 180.7 KiB/s |  19.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 692/1521] qemu-device-display-virtio- 100% | 294.7 KiB/s |  31.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 693/1521] qemu-device-display-vhost-u 100% | 624.3 KiB/s | 270.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 694/1521] qemu-device-display-virtio- 100% | 185.2 KiB/s |  20.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 695/1521] qemu-device-display-virtio- 100% | 168.3 KiB/s |  19.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 696/1521] qemu-device-display-virtio- 100% | 182.7 KiB/s |  19.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 697/1521] qemu-device-display-virtio- 100% | 264.8 KiB/s |  29.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 698/1521] qemu-device-display-virtio- 100% | 196.7 KiB/s |  22.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 699/1521] qemu-device-display-virtio- 100% | 180.2 KiB/s |  19.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 700/1521] qemu-device-display-virtio- 100% | 179.0 KiB/s |  19.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 701/1521] qemu-device-uefi-vars-2:10. 100% | 348.5 KiB/s |  38.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 702/1521] qemu-device-usb-host-2:10.2 100% | 310.0 KiB/s |  33.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 703/1521] qemu-device-usb-redirect-2: 100% | 373.5 KiB/s |  40.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 704/1521] qemu-device-usb-smartcard-2 100% | 252.3 KiB/s |  28.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 705/1521] libgs-0:10.06.0-2.fc44.x86_ 100% | 878.3 KiB/s |   3.9 MiB |  00m05s[0m
[1;31m==> proxmox-clone.fedora: [ 706/1521] qemu-ui-curses-2:10.2.2-1.f 100% | 246.7 KiB/s |  27.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 707/1521] qemu-ui-egl-headless-2:10.2 100% | 194.0 KiB/s |  21.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 708/1521] qemu-ui-gtk-2:10.2.2-1.fc44 100% | 411.8 KiB/s |  44.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 709/1521] qemu-pr-helper-2:10.2.2-1.f 100% | 729.2 KiB/s | 367.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 710/1521] qemu-ui-opengl-2:10.2.2-1.f 100% | 266.0 KiB/s |  29.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 711/1521] qemu-ui-sdl-2:10.2.2-1.fc44 100% | 292.3 KiB/s |  32.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 712/1521] qemu-ui-spice-app-2:10.2.2- 100% | 197.2 KiB/s |  21.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 713/1521] qemu-ui-spice-core-2:10.2.2 100% | 368.0 KiB/s |  40.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 714/1521] qemu-system-x86-core-2:10.2 100% |   5.7 MiB/s |   8.9 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 715/1521] adobe-mappings-cmap-depreca 100% | 893.3 KiB/s | 102.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 716/1521] virtiofsd-0:1.13.3-1.fc44.x 100% | 810.4 KiB/s | 996.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 717/1521] adobe-mappings-pdf-0:201904 100% |   2.2 MiB/s | 619.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 718/1521] jbig2dec-libs-0:0.20-8.fc44 100% | 653.7 KiB/s |  75.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 719/1521] libXt-0:1.3.1-4.fc44.x86_64 100% |   1.6 MiB/s | 184.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 720/1521] libijs-0:0.35-26.fc44.x86_6 100% | 258.2 KiB/s |  29.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 721/1521] libpaper-1:2.1.1-10.fc44.x8 100% | 232.7 KiB/s |  26.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 722/1521] urw-base35-fonts-0:20200910 100% |  87.8 KiB/s |  10.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 723/1521] gpgmepp-0:2.0.1-3.fc44.x86_ 100% |   1.3 MiB/s | 149.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 724/1521] poppler-data-0:0.4.11-11.fc 100% |   3.8 MiB/s |   2.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 725/1521] adobe-mappings-cmap-0:20231 100% | 868.4 KiB/s |   2.2 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 726/1521] python3-pycparser-0:2.22-8. 100% |   2.0 MiB/s | 373.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 727/1521] boost-regex-0:1.90.0-7.fc44 100% | 621.0 KiB/s | 121.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 728/1521] ctags-0:6.2.1-3.fc44.x86_64 100% |   3.3 MiB/s | 920.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 729/1521] swtpm-libs-0:0.10.1-3.fc44. 100% | 567.3 KiB/s |  65.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 730/1521] gperftools-libs-0:2.18.1-1. 100% |   2.7 MiB/s | 316.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 731/1521] libgfrpc0-0:11.2-5.fc44.x86 100% | 450.6 KiB/s |  51.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 732/1521] libgfxdr0-0:11.2-5.fc44.x86 100% | 210.3 KiB/s |  24.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 733/1521] libtpms-0:0.10.2-3.fc44.x86 100% | 745.5 KiB/s | 431.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 734/1521] libglusterfs0-0:11.2-5.fc44 100% |   2.7 MiB/s | 296.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 735/1521] glusterfs-client-xlators-0: 100% |   2.8 MiB/s | 794.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 736/1521] librdmacm-0:61.0-2.fc44.x86 100% | 678.2 KiB/s |  78.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 737/1521] qemu-common-2:10.2.2-1.fc44 100% |   1.6 MiB/s | 578.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 738/1521] glusterfs-0:11.2-5.fc44.x86 100% | 722.4 KiB/s | 599.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 739/1521] google-droid-sans-fonts-0:2 100% | 863.9 KiB/s |   2.7 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 740/1521] sdl2-compat-0:2.32.64-1.fc4 100% | 510.4 KiB/s | 139.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 741/1521] spice-server-0:0.16.0-2.fc4 100% |   1.3 MiB/s | 401.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 742/1521] libnfs-0:6.0.2-7.fc44.x86_6 100% | 643.0 KiB/s | 176.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 743/1521] virglrenderer-0:1.3.0-1.fc4 100% |   1.6 MiB/s | 444.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 744/1521] libblkio-0:1.5.0-5.fc44.x86 100% | 665.3 KiB/s | 340.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 745/1521] device-mapper-multipath-lib 100% |   1.5 MiB/s | 301.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 746/1521] daxctl-libs-0:84-1.fc44.x86 100% | 371.6 KiB/s |  42.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 747/1521] rutabaga-gfx-ffi-0:0.1.3-5. 100% | 637.3 KiB/s | 270.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 748/1521] igvm-libs-0:0.4.0-9.fc44.x8 100% |   1.2 MiB/s | 235.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 749/1521] libfdt-0:1.7.2-9.fc44.x86_6 100% | 343.1 KiB/s |  36.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 750/1521] libslirp-0:4.9.1-3.fc44.x86 100% | 685.7 KiB/s |  80.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 751/1521] libpmem-0:2.1.0-5.fc44.x86_ 100% | 584.3 KiB/s | 108.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 752/1521] libxdp-0:1.6.3-1.fc44.x86_6 100% | 659.7 KiB/s |  71.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 753/1521] seabios-bin-0:1.17.0-10.fc4 100% |   1.7 MiB/s | 189.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 754/1521] qatzip-libs-0:1.3.1-3.fc44. 100% | 366.3 KiB/s |  68.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 755/1521] seavgabios-bin-0:1.17.0-10. 100% | 263.5 KiB/s |  51.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 756/1521] SDL2_image-0:2.8.8-4.fc44.x 100% | 586.5 KiB/s | 110.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 757/1521] capstone-0:5.0.6-4.fc44.x86 100% | 843.7 KiB/s |   1.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 758/1521] snappy-0:1.2.2-4.fc44.x86_6 100% |  91.4 KiB/s |  43.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 759/1521] libSM-0:1.2.5-4.fc44.x86_64 100% | 416.6 KiB/s |  44.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 760/1521] libICE-0:1.1.2-4.fc44.x86_6 100% | 421.9 KiB/s |  80.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 761/1521] urw-base35-d050000l-fonts-0 100% | 382.9 KiB/s |  75.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 762/1521] urw-base35-fonts-common-0:2 100% | 178.2 KiB/s |  20.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 763/1521] urw-base35-bookman-fonts-0: 100% | 790.8 KiB/s | 845.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 764/1521] urw-base35-c059-fonts-0:202 100% | 768.5 KiB/s | 873.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 765/1521] urw-base35-gothic-fonts-0:2 100% | 771.4 KiB/s | 641.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 766/1521] urw-base35-nimbus-mono-ps-f 100% | 801.2 KiB/s | 794.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 767/1521] urw-base35-nimbus-roman-fon 100% | 790.1 KiB/s | 853.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 768/1521] urw-base35-standard-symbols 100% | 294.0 KiB/s |  57.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 769/1521] urw-base35-nimbus-sans-font 100% | 814.5 KiB/s |   1.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 770/1521] urw-base35-z003-fonts-0:202 100% | 622.4 KiB/s | 275.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 771/1521] libunwind-0:1.8.3-1.fc44.x8 100% | 389.8 KiB/s |  76.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 772/1521] urw-base35-p052-fonts-0:202 100% | 790.5 KiB/s | 972.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 773/1521] orc-0:0.4.41-3.fc44.x86_64  100% | 631.6 KiB/s | 224.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 774/1521] libva-0:2.23.0-3.fc44.x86_6 100% | 631.6 KiB/s | 121.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 775/1521] ndctl-libs-0:84-1.fc44.x86_ 100% | 465.4 KiB/s |  90.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 776/1521] qatlib-0:25.08.0-4.fc44.x86 100% | 712.9 KiB/s | 254.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 777/1521] libglvnd-glx-1:1.7.0-9.fc44 100% | 489.0 KiB/s | 132.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 778/1521] libglvnd-1:1.7.0-9.fc44.x86 100% | 579.3 KiB/s | 114.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 779/1521] libxshmfence-0:1.3.2-8.fc44 100% | 112.0 KiB/s |  13.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 780/1521] lm_sensors-libs-0:3.6.0-24. 100% | 355.4 KiB/s |  41.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 781/1521] mesa-dri-drivers-0:26.0.5-3 100% |  17.4 MiB/s |  13.3 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 782/1521] mesa-filesystem-0:26.0.5-3. 100% | 139.8 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 783/1521] mesa-libgbm-0:26.0.5-3.fc44 100% | 237.2 KiB/s |  14.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 784/1521] mesa-libGL-0:26.0.5-3.fc44. 100% |   2.0 MiB/s | 136.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 785/1521] ipxe-roms-qemu-0:20240119-5 100% | 847.5 KiB/s |   1.7 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 786/1521] libXxf86vm-0:1.1.6-4.fc44.x 100% | 163.6 KiB/s |  18.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 787/1521] libdisplay-info-0:0.3.0-1.f 100% | 457.3 KiB/s |  89.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 788/1521] mesa-vulkan-drivers-0:26.0. 100% |  65.3 MiB/s |  26.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 789/1521] swtpm-selinux-0:0.10.1-3.fc 100% | 197.5 KiB/s |  23.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 790/1521] libdnf5-plugin-appstream-0: 100% | 254.6 KiB/s |  62.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 791/1521] spirv-tools-libs-0:2026.1-1 100% | 842.6 KiB/s |   1.7 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 792/1521] dnf5daemon-server-0:5.4.1.0 100% | 671.6 KiB/s | 319.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 793/1521] dnf5daemon-server-polkit-0: 100% | 229.4 KiB/s |  49.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 794/1521] gnome-software-0:50.0-2.fc4 100% | 835.9 KiB/s |   2.6 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 795/1521] flatpak-0:1.17.6-1.fc44.x86 100% | 860.0 KiB/s |   1.9 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 796/1521] flatpak-libs-0:1.17.6-1.fc4 100% | 784.3 KiB/s | 456.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 797/1521] gnome-app-list-0:3.0-4.fc44 100% | 164.2 KiB/s |  19.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 798/1521] gnome-menus-0:3.38.1-2.fc44 100% | 582.5 KiB/s | 202.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 799/1521] malcontent-libs-0:0.14.0-1. 100% | 323.7 KiB/s |  64.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 800/1521] rpm-plugin-dbus-announce-0: 100% | 175.9 KiB/s |  20.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 801/1521] flatpak-selinux-0:1.17.6-1. 100% | 203.1 KiB/s |  23.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 802/1521] dconf-0:0.49.0-5.fc44.x86_6 100% | 575.4 KiB/s | 113.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 803/1521] flatpak-session-helper-0:1. 100% | 371.8 KiB/s |  44.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 804/1521] redhat-menus-0:12.0.2-39.fc 100% | 578.3 KiB/s | 155.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 805/1521] at-spi2-atk-0:2.60.3-1.fc44 100% | 286.7 KiB/s |  89.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 806/1521] at-spi2-core-0:2.60.3-1.fc4 100% |   1.8 MiB/s | 401.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 807/1521] atk-0:2.60.3-1.fc44.x86_64  100% |   1.1 MiB/s |  82.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 808/1521] xprop-0:1.2.8-5.fc44.x86_64 100% | 291.7 KiB/s |  35.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 809/1521] orca-0:50.1.2-1.fc44.noarch 100% |  13.6 MiB/s |   3.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 810/1521] python3-brlapi-0:0.8.7-8.fc 100% | 391.7 KiB/s | 108.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 811/1521] python3-dasbus-0:1.7-14.fc4 100% | 435.7 KiB/s | 121.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 812/1521] python3-louis-0:3.33.0-7.fc 100% | 166.2 KiB/s |  19.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 813/1521] fwupd-0:2.1.1-1.fc44.x86_64 100% | 871.1 KiB/s |   2.9 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 814/1521] python3-pyatspi-0:2.58.2-1. 100% | 608.7 KiB/s | 115.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 815/1521] libglvnd-gles-1:1.7.0-9.fc4 100% | 174.4 KiB/s |  28.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 816/1521] python3-speechd-0:0.12.1-6. 100% | 381.2 KiB/s |  74.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 817/1521] mesa-libEGL-0:26.0.5-3.fc44 100% |   2.0 MiB/s | 139.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 818/1521] libglvnd-egl-1:1.7.0-9.fc44 100% | 332.2 KiB/s |  37.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 819/1521] gnome-control-center-0:50.1 100% |  40.7 MiB/s |   6.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 820/1521] colord-gtk4-0:0.3.1-6.fc44. 100% | 171.1 KiB/s |  18.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 821/1521] gsound-0:1.0.3-12.fc44.x86_ 100% | 318.8 KiB/s |  35.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 822/1521] libwacom-0:2.18.0-1.fc44.x8 100% | 259.1 KiB/s |  51.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 823/1521] pulseaudio-libs-glib2-0:17. 100% | 140.9 KiB/s |  16.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 824/1521] gnome-control-center-filesy 100% | 150.8 KiB/s |  10.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 825/1521] malcontent-0:0.14.0-1.fc44. 100% | 711.4 KiB/s | 300.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 826/1521] gnome-settings-daemon-0:50. 100% |  14.6 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 827/1521] geoclue2-0:2.8.0-2.fc44.x86 100% | 540.8 KiB/s | 146.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 828/1521] libwacom-data-0:2.18.0-1.fc 100% | 680.6 KiB/s | 342.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 829/1521] gnome-shell-0:50.1-2.fc44.x 100% |  22.8 MiB/s |   1.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 830/1521] gcr-0:4.4.0.1-7.fc44.x86_64 100% | 298.0 KiB/s |  56.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 831/1521] gjs-0:1.88.0-1.fc44.x86_64  100% | 813.4 KiB/s | 675.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 832/1521] gnome-autoar-0:0.4.5-4.fc44 100% | 293.3 KiB/s |  57.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 833/1521] switcheroo-control-0:3.0-5. 100% | 240.3 KiB/s |  47.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 834/1521] gnome-shell-common-0:50.1-2 100% | 236.3 KiB/s |  15.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 835/1521] gobject-introspection-0:1.8 100% | 447.9 KiB/s | 122.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 836/1521] gettext-0:0.26-4.fc44.x86_6 100% | 847.5 KiB/s |   1.7 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 837/1521] nautilus-0:50.1-1.fc44.x86_ 100% |  20.8 MiB/s |   2.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 838/1521] libgexiv2-0:0.16.0-2.fc44.x 100% | 509.8 KiB/s | 102.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 839/1521] nautilus-extensions-0:50.1- 100% | 573.1 KiB/s |  36.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 840/1521] exiv2-libs-0:0.28.6-3.fc44. 100% | 814.5 KiB/s | 938.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 841/1521] inih-cpp-0:62-2.fc44.x86_64 100% | 209.9 KiB/s |  25.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 842/1521] NetworkManager-ssh-gnome-0: 100% | 623.8 KiB/s |  43.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 843/1521] NetworkManager-ssh-0:1.4.4- 100% |   1.3 MiB/s |  88.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 844/1521] sshpass-0:1.09-12.fc44.x86_ 100% | 229.5 KiB/s |  27.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 845/1521] gnome-calculator-0:50.0-1.f 100% | 846.2 KiB/s |   1.7 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 846/1521] gvfs-fuse-0:1.60.0-1.fc44.x 100% | 269.1 KiB/s |  30.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 847/1521] glibc-all-langpacks-0:2.43- 100% |   1.0 MiB/s |  17.6 MiB |  00m17s[0m
[1;31m==> proxmox-clone.fedora: [ 848/1521] libieee1284-0:0.2.11-48.fc4 100% | 356.0 KiB/s |  42.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 849/1521] sane-backends-0:1.4.0-6.fc4 100% |   3.1 MiB/s | 885.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 850/1521] sane-airscan-0:0.99.36-2.fc 100% | 772.8 KiB/s |  87.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 851/1521] libsane-airscan-0:0.99.36-2 100% |   1.1 MiB/s | 139.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 852/1521] ModemManager-0:1.24.2-3.fc4 100% |   4.7 MiB/s |   1.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 853/1521] libmbim-0:1.32.0-3.fc44.x86 100% |   2.5 MiB/s | 299.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 854/1521] libmbim-utils-0:1.32.0-3.fc 100% | 973.1 KiB/s | 111.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 855/1521] sane-backends-drivers-scann 100% | 870.0 KiB/s |   2.9 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [ 856/1521] libqmi-0:1.36.0-3.fc44.x86_ 100% |   4.0 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 857/1521] libqrtr-glib-0:1.2.2-9.fc44 100% | 316.1 KiB/s |  36.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 858/1521] libqmi-utils-0:1.36.0-3.fc4 100% | 688.0 KiB/s | 242.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 859/1521] glib-networking-0:2.80.1-4. 100% |   1.7 MiB/s | 202.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 860/1521] bluez-obexd-0:5.86-4.fc44.x 100% |   1.4 MiB/s | 155.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 861/1521] gnome-bluetooth-1:47.2-1.fc 100% | 177.5 KiB/s |  43.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 862/1521] gnome-classic-session-0:50. 100% | 205.8 KiB/s |  15.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 863/1521] gnome-shell-extension-apps- 100% | 222.3 KiB/s |  16.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 864/1521] mozjs140-0:140.6.0-4.fc44.x 100% | 873.4 KiB/s |   7.3 MiB |  00m09s[0m
[1;31m==> proxmox-clone.fedora: [ 865/1521] gnome-shell-extension-launc 100% | 152.9 KiB/s |  11.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 866/1521] gnome-bluetooth-libs-1:47.2 100% | 674.4 KiB/s | 282.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 867/1521] gnome-shell-extension-windo 100% | 335.4 KiB/s |  27.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 868/1521] gnome-shell-extension-place 100% |  85.9 KiB/s |  15.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 869/1521] gnome-shell-extension-commo 100% |   1.7 MiB/s | 166.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 870/1521] rest-0:0.10.2-5.fc44.x86_64 100% | 294.7 KiB/s |  71.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 871/1521] libsane-hpaio-0:3.25.8-2.fc 100% | 382.1 KiB/s |  89.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 872/1521] gnome-maps-0:50.1-1.fc44.x8 100% |   4.2 MiB/s |   1.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 873/1521] papers-previewer-0:49.6-1.f 100% | 495.6 KiB/s |  31.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 874/1521] papers-thumbnailer-0:49.6-1 100% |   7.8 MiB/s | 636.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 875/1521] papers-libs-0:49.6-1.fc44.x 100% |   1.0 MiB/s | 304.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 876/1521] papers-0:49.6-1.fc44.x86_64 100% |  12.1 MiB/s |   3.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 877/1521] papers-nautilus-0:49.6-1.fc 100% | 256.6 KiB/s |  17.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 878/1521] exempi-0:2.6.4-9.fc44.x86_6 100% |   1.7 MiB/s | 611.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 879/1521] PackageKit-gtk3-module-0:1. 100% | 160.9 KiB/s |  18.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 880/1521] decibels-0:49.6.1-1.fc44.no 100% |   2.0 MiB/s | 133.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 881/1521] gnome-remote-desktop-0:50.1 100% |   6.6 MiB/s | 555.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 882/1521] libei-0:1.5.0-2.fc44.x86_64 100% | 482.2 KiB/s |  54.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 883/1521] djvulibre-libs-0:3.5.28-16. 100% | 781.3 KiB/s | 701.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 884/1521] localsearch-0:3.11.1-1.fc44 100% |   9.4 MiB/s | 880.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 885/1521] xdg-desktop-portal-0:1.21.1 100% | 635.7 KiB/s | 522.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 886/1521] libvncserver-0:0.9.15-6.fc4 100% |   1.7 MiB/s | 333.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 887/1521] libgsf-0:1.14.56-1.fc44.x86 100% |   2.4 MiB/s | 268.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 888/1521] libcue-0:2.3.0-14.fc44.x86_ 100% | 310.5 KiB/s |  35.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 889/1521] libzip-0:1.11.4-3.fc44.x86_ 100% | 662.5 KiB/s |  74.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 890/1521] game-music-emu-0:0.6.4-3.fc 100% | 628.6 KiB/s | 172.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 891/1521] libavutil-free-0:8.0.1-6.fc 100% | 744.6 KiB/s | 379.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 892/1521] libchromaprint-0:1.6.0-4.fc 100% | 386.1 KiB/s |  44.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 893/1521] libdvdnav-0:7.0.0-1.fc44.x8 100% | 307.2 KiB/s |  58.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 894/1521] libavcodec-free-0:8.0.1-6.f 100% |   4.2 MiB/s |   4.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 895/1521] libmodplug-1:0.8.9.0-29.fc4 100% | 677.3 KiB/s | 182.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 896/1521] libavformat-free-0:8.0.1-6. 100% | 812.4 KiB/s |   1.2 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 897/1521] librabbitmq-0:0.15.0-4.fc44 100% | 411.1 KiB/s |  44.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 898/1521] librist-0:0.2.11-1.fc44.x86 100% | 456.9 KiB/s |  88.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 899/1521] aribb24-0:1.0.3^20160216git 100% | 355.6 KiB/s |  40.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 900/1521] zeromq-0:4.3.5-22.fc43.x86_ 100% | 754.0 KiB/s | 468.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 901/1521] ilbc-0:3.0.4-19.fc44.x86_64 100% | 299.6 KiB/s |  57.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 902/1521] codec2-0:1.2.0-9.fc44.x86_6 100% | 778.1 KiB/s | 644.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 903/1521] libaribcaption-0:1.1.1-4.fc 100% | 434.2 KiB/s | 117.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 904/1521] libopenmpt-0:0.8.6-1.fc44.x 100% | 553.1 KiB/s | 807.5 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 905/1521] liblc3-0:1.1.3-7.fc44.x86_6 100% | 532.6 KiB/s | 106.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 906/1521] libswresample-free-0:8.0.1- 100% | 374.7 KiB/s |  71.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 907/1521] libtheora-1:1.1.1-41.fc44.x 100% | 627.2 KiB/s | 170.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 908/1521] libvpl-1:2.16.0-2.fc44.x86_ 100% | 622.9 KiB/s | 167.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 909/1521] openapv-libs-0:0.2.1.2-1.fc 100% | 358.2 KiB/s |  68.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 910/1521] opencore-amr-0:0.1.6-10.fc4 100% | 682.0 KiB/s | 183.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 911/1521] speex-0:1.2.0-21.fc44.x86_6 100% | 378.8 KiB/s |  71.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 912/1521] twolame-libs-0:0.4.0-9.fc44 100% | 364.9 KiB/s |  68.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 913/1521] vo-amrwbenc-0:0.1.3-24.fc44 100% | 462.1 KiB/s |  85.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 914/1521] xevd-libs-0:0.5.0-6.fc44.x8 100% | 630.6 KiB/s | 169.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 915/1521] xeve-libs-0:0.5.1-6.fc44.x8 100% | 674.3 KiB/s | 283.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 916/1521] libshaderc-0:2026.1-1.fc44. 100% | 818.2 KiB/s |   1.2 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 917/1521] libvdpau-0:1.5-11.fc44.x86_ 100% | 144.6 KiB/s |  16.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 918/1521] xvidcore-0:1.3.7-19.fc44.x8 100% | 628.2 KiB/s | 267.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 919/1521] cjson-0:1.7.18-5.fc44.x86_6 100% | 259.6 KiB/s |  32.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 920/1521] zvbi-0:0.2.44-3.fc44.x86_64 100% | 760.6 KiB/s | 443.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 921/1521] openpgm-0:5.3.128-6.fc44.x8 100% | 316.0 KiB/s | 184.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 922/1521] gssdp-0:1.6.4-6.fc44.x86_64 100% | 304.7 KiB/s |  58.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 923/1521] gupnp-0:1.6.9-3.fc44.x86_64 100% | 581.2 KiB/s | 109.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 924/1521] gupnp-av-0:0.14.4-4.fc44.x8 100% | 528.2 KiB/s | 101.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 925/1521] gupnp-dlna-0:0.12.0-12.fc44 100% | 509.3 KiB/s |  96.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 926/1521] libmediaart-0:1.9.7-4.fc44. 100% | 338.0 KiB/s |  37.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 927/1521] rygel-0:45.1-1.fc44.x86_64  100% | 828.2 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 928/1521] tinysparql-0:3.11.1-1.fc44. 100% |   2.0 MiB/s |   1.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 929/1521] libtinysparql-0:3.11.1-1.fc 100% | 882.1 KiB/s | 364.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 930/1521] linux-firmware-whence-0:202 100% |   1.1 MiB/s |  77.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 931/1521] amd-gpu-firmware-0:20260410 100% |  49.5 MiB/s |  26.4 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 932/1521] tiwilink-firmware-0:2026041 100% |  12.5 MiB/s |   4.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 933/1521] qcom-wwan-firmware-0:202604 100% |   9.6 MiB/s | 763.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 934/1521] realtek-firmware-0:20260410 100% |  43.2 MiB/s |   5.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 935/1521] nxpwireless-firmware-0:2026 100% |  12.4 MiB/s | 943.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 936/1521] mt7xxx-firmware-0:20260410- 100% |  37.2 MiB/s |  20.3 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 937/1521] linux-firmware-0:20260410-1 100% |  46.0 MiB/s |  50.4 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 938/1521] nvidia-gpu-firmware-0:20260 100% |  54.4 MiB/s |  99.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 939/1521] libertas-firmware-0:2026041 100% |   9.8 MiB/s |   1.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 940/1521] iwlwifi-dvm-firmware-0:2026 100% |  11.8 MiB/s |   1.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 941/1521] iwlegacy-firmware-0:2026041 100% |   2.3 MiB/s | 161.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 942/1521] intel-vsc-firmware-0:202604 100% |  30.1 MiB/s |   7.8 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 943/1521] intel-gpu-firmware-0:202604 100% |  35.5 MiB/s |   8.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 944/1521] intel-audio-firmware-0:2026 100% |  17.4 MiB/s |   3.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 945/1521] cirrus-audio-firmware-0:202 100% |  16.2 MiB/s |   2.8 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 946/1521] iwlwifi-mvm-firmware-0:2026 100% |  50.9 MiB/s |  60.6 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 947/1521] brcmfmac-firmware-0:2026041 100% |  33.3 MiB/s |   9.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 948/1521] amd-ucode-firmware-0:202604 100% |   7.8 MiB/s | 587.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 949/1521] iwlwifi-mld-firmware-0:2026 100% |  37.2 MiB/s |  17.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 950/1521] atheros-firmware-0:20260410 100% |  49.5 MiB/s |  39.7 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 951/1521] libreoffice-calc-1:26.2.2.2 100% |  37.6 MiB/s |   9.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 952/1521] libetonyek-0:0.1.13-2.fc44. 100% | 679.2 KiB/s | 750.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 953/1521] libnumbertext-0:1.0.11-10.f 100% | 679.3 KiB/s | 241.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 954/1521] libodfgen-0:0.1.8-16.fc44.x 100% | 659.8 KiB/s | 282.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 955/1521] liborcus-0:0.21.0-5.fc44.x8 100% | 776.7 KiB/s | 643.1 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 956/1521] librevenge-0:0.0.5-13.fc44. 100% | 707.4 KiB/s | 248.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 957/1521] lpcnetfreedv-0:0.5-10.fc44. 100% | 778.5 KiB/s |   7.3 MiB |  00m10s[0m
[1;31m==> proxmox-clone.fedora: [ 958/1521] libmwaw-0:0.3.22-8.fc44.x86 100% | 773.6 KiB/s |   2.7 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [ 959/1521] libstaroffice-0:0.0.7-17.fc 100% | 828.6 KiB/s | 827.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 960/1521] lpsolve-0:5.5.2.14-2.fc44.x 100% | 678.1 KiB/s | 347.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 961/1521] md4c-0:0.5.1-5.fc44.x86_64  100% | 454.5 KiB/s |  83.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 962/1521] libwps-0:0.4.14-7.fc44.x86_ 100% | 831.8 KiB/s | 954.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 963/1521] libreoffice-data-1:26.2.2.2 100% |   1.2 MiB/s | 556.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 964/1521] libreoffice-pyuno-1:26.2.2. 100% |   4.8 MiB/s | 506.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 965/1521] libreoffice-pdfimport-1:26. 100% | 605.7 KiB/s | 237.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 966/1521] liblangtag-0:0.6.7-7.fc44.x 100% | 394.7 KiB/s |  77.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 967/1521] libreoffice-ure-1:26.2.2.2- 100% |   9.4 MiB/s |   2.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 968/1521] boost-iostreams-0:1.90.0-7. 100% | 381.7 KiB/s |  40.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 969/1521] Box2D-0:2.4.2-7.fc44.x86_64 100% | 413.7 KiB/s | 111.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 970/1521] boost-locale-0:1.90.0-7.fc4 100% | 695.4 KiB/s | 245.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 971/1521] clucene-contribs-lib-0:2.3. 100% | 525.6 KiB/s |  96.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 972/1521] libreoffice-core-1:26.2.2.2 100% |  59.3 MiB/s | 117.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [ 973/1521] clucene-core-0:2.3.3.4-55.2 100% | 781.1 KiB/s | 606.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 974/1521] google-crosextra-caladea-fo 100% | 520.2 KiB/s |  98.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 975/1521] hyphen-0:2.8.8-28.fc44.x86_ 100% | 160.9 KiB/s |  29.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 976/1521] libargon2-0:20190702-10.fc4 100% | 278.4 KiB/s |  29.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 977/1521] google-carlito-fonts-0:1.10 100% | 791.7 KiB/s | 802.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 978/1521] libeot-0:0.01-35.fc44.x86_6 100% | 354.8 KiB/s |  38.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 979/1521] libcmis-0:0.6.2-11.fc44.x86 100% | 668.5 KiB/s | 427.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 980/1521] liberation-mono-fonts-1:2.1 100% | 767.0 KiB/s | 507.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 981/1521] liberation-sans-fonts-1:2.1 100% | 747.2 KiB/s | 611.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 982/1521] libexttextcat-0:3.4.6-13.fc 100% | 733.7 KiB/s | 253.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 983/1521] mythes-0:1.2.5-10.fc44.x86_ 100% | 170.7 KiB/s |  18.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 984/1521] mariadb-connector-c-0:3.4.8 100% | 608.5 KiB/s | 211.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 985/1521] liberation-serif-fonts-1:2. 100% | 830.1 KiB/s | 611.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 986/1521] raptor2-0:2.0.15-50.fc44.x8 100% | 625.6 KiB/s | 218.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 987/1521] xmlsec1-nss-1:1.2.41-4.fc44 100% | 397.4 KiB/s |  75.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 988/1521] redland-0:1.0.17-41.fc44.x8 100% | 636.2 KiB/s | 177.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 989/1521] libreoffice-langpack-en-1:2 100% | 278.9 KiB/s |  91.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 990/1521] libreoffice-opensymbol-font 100% | 961.4 KiB/s | 142.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 991/1521] zxing-cpp-0:2.2.1-6.fc44.x8 100% | 778.9 KiB/s | 641.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 992/1521] libreoffice-ure-common-1:26 100% |   5.7 MiB/s |   1.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 993/1521] libreoffice-filters-1:26.2. 100% |  56.0 KiB/s |   7.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 994/1521] boost-random-0:1.90.0-7.fc4 100% | 213.5 KiB/s |  22.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 995/1521] boost-atomic-0:1.90.0-7.fc4 100% | 176.8 KiB/s |  19.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 996/1521] liblangtag-data-0:0.6.7-7.f 100% | 508.1 KiB/s | 214.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 997/1521] boost-charconv-0:1.90.0-7.f 100% | 474.0 KiB/s |  89.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [ 998/1521] zxcvbn-c-0:2.6-2.fc44.x86_6 100% | 821.2 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [ 999/1521] boost-chrono-0:1.90.0-7.fc4 100% | 230.6 KiB/s |  26.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1000/1521] boost-container-0:1.90.0-7. 100% | 370.2 KiB/s |  40.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1001/1521] boost-date-time-0:1.90.0-7. 100% | 126.5 KiB/s |  13.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1002/1521] mariadb-connector-c-config- 100% |  82.5 KiB/s |   9.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1003/1521] boost-thread-0:1.90.0-7.fc4 100% | 248.4 KiB/s |  57.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1004/1521] hyphen-en-0:2.8.8-28.fc44.n 100% | 419.6 KiB/s |  47.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1005/1521] libquadmath-0:16.0.1-0.10.f 100% | 573.1 KiB/s | 197.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1006/1521] libreoffice-graphicfilter-1 100% |   3.2 MiB/s | 266.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1007/1521] libreoffice-impress-1:26.2. 100% |   2.2 MiB/s | 166.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1008/1521] rasqal-0:0.9.33-32.fc44.x86 100% | 686.8 KiB/s | 287.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1009/1521] libreoffice-writer-1:26.2.2 100% |  22.5 MiB/s |   4.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1010/1521] libreoffice-emailmerge-1:26 100% | 198.4 KiB/s |  13.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1011/1521] libreoffice-xsltfilter-1:26 100% |   1.0 MiB/s | 309.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1012/1521] libfreehand-0:0.1.2-27.fc44 100% | 652.9 KiB/s | 280.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1013/1521] libcdr-0:0.1.8-5.fc44.x86_6 100% | 699.0 KiB/s | 464.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1014/1521] libmspub-0:0.1.4-39.fc44.x8 100% | 655.0 KiB/s | 174.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1015/1521] libpagemaker-0:0.0.4-28.fc4 100% | 389.6 KiB/s |  72.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1016/1521] libqxp-0:0.0.2-33.fc44.x86_ 100% | 520.4 KiB/s | 138.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1017/1521] libwpg-0:0.3.4-7.fc44.x86_6 100% | 414.2 KiB/s |  77.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1018/1521] libvisio-0:0.1.10-1.fc44.x8 100% | 657.8 KiB/s | 277.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1019/1521] libreoffice-ogltrans-1:26.2 100% |   2.0 MiB/s | 153.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1020/1521] libzmf-0:0.0.2-42.fc44.x86_ 100% | 472.3 KiB/s |  89.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1021/1521] libabw-0:0.1.3-19.fc44.x86_ 100% | 469.0 KiB/s | 123.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1022/1521] libe-book-0:0.1.3-41.fc44.x 100% | 679.0 KiB/s | 179.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1023/1521] libepubgen-0:0.1.1-22.fc44. 100% | 561.6 KiB/s | 150.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1024/1521] pipewire-pulseaudio-0:1.6.4 100% |   2.9 MiB/s | 220.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1025/1521] libwpd-0:0.10.3-24.fc44.x86 100% | 758.9 KiB/s | 261.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1026/1521] pipewire-libs-0:1.6.4-1.fc4 100% |  22.5 MiB/s |   2.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1027/1521] libebur128-0:1.2.6-15.fc44. 100% | 240.4 KiB/s |  25.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1028/1521] libldac-0:2.0.2.3-19.fc44.x 100% | 406.8 KiB/s |  43.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1029/1521] libsbc-0:2.1-2.fc44.x86_64  100% | 455.9 KiB/s |  50.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1030/1521] spandsp-0:0.0.6-22.fc44.x86 100% | 799.5 KiB/s | 335.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1031/1521] mythes-en-0:3.0-43.fc44.noa 100% | 857.4 KiB/s |   3.0 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [1032/1521] webrtc-audio-processing-0:2 100% | 768.5 KiB/s | 441.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1033/1521] pipewire-utils-0:1.6.4-1.fc 100% |   7.6 MiB/s | 615.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1034/1521] pipewire-gstreamer-0:1.6.4- 100% |   1.2 MiB/s |  85.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1035/1521] fftw-libs-single-0:3.3.10-1 100% | 814.0 KiB/s |   1.2 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1036/1521] pipewire-config-raop-0:1.6. 100% | 176.9 KiB/s |  12.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1037/1521] rtkit-0:0.11-70.fc44.x86_64 100% | 297.2 KiB/s |  55.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1038/1521] wireplumber-0:0.5.14-1.fc44 100% |   1.8 MiB/s | 122.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1039/1521] pipewire-0:1.6.4-1.fc44.x86 100% | 418.2 KiB/s | 139.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1040/1521] wireplumber-libs-0:0.5.14-1 100% |   6.1 MiB/s | 442.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1041/1521] pipewire-alsa-0:1.6.4-1.fc4 100% | 766.5 KiB/s |  64.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1042/1521] gstreamer1-plugins-ugly-fre 100% |   2.9 MiB/s | 219.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1043/1521] abseil-cpp-0:20260107.1-1.f 100% | 808.5 KiB/s | 799.6 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1044/1521] liba52-0:0.7.4-53.fc44.x86_ 100% | 398.3 KiB/s |  44.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1045/1521] libmpeg2-0:0.5.1-33.fc44.x8 100% | 412.3 KiB/s |  77.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1046/1521] gstreamer1-plugins-bad-free 100% |  28.6 MiB/s |   3.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1047/1521] libsrtp-0:2.8.0-1.fc44.x86_ 100% | 329.9 KiB/s |  62.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1048/1521] faad2-libs-1:2.11.2-6.fc44. 100% | 645.7 KiB/s | 230.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1049/1521] gstreamer1-plugins-bad-free 100% |  13.8 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1050/1521] soundtouch-0:2.4.0-3.fc44.x 100% | 502.0 KiB/s |  91.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1051/1521] gupnp-igd-0:1.6.0-8.fc44.x8 100% | 318.4 KiB/s |  34.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1052/1521] gstreamer1-plugins-good-0:1 100% |  21.2 MiB/s |   2.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1053/1521] libnice-0:0.1.23-2.fc44.x86 100% | 605.0 KiB/s | 206.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1054/1521] libshout-0:2.4.6-10.fc44.x8 100% | 422.6 KiB/s |  78.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1055/1521] openal-soft-0:1.24.2-6.fc44 100% | 811.1 KiB/s | 670.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1056/1521] libv4l-0:1.32.0-3.fc44.x86_ 100% | 521.5 KiB/s | 139.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1057/1521] gstreamer1-plugin-openh264- 100% | 512.9 KiB/s |  37.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1058/1521] PackageKit-gstreamer-plugin 100% | 183.8 KiB/s |  19.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1059/1521] wavpack-0:5.9.0-2.fc44.x86_ 100% | 698.6 KiB/s | 241.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1060/1521] gstreamer1-plugin-libav-0:1 100% |   2.3 MiB/s | 171.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1061/1521] taglib-0:2.2.1-1.fc44.x86_6 100% | 744.7 KiB/s | 487.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1062/1521] gstreamer1-plugin-dav1d-0:0 100% | 719.9 KiB/s | 247.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1063/1521] libass-0:0.17.4-2.fc44.x86_ 100% | 503.4 KiB/s | 133.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1064/1521] libbs2b-0:3.1.0-37.fc44.x86 100% | 271.9 KiB/s |  29.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1065/1521] libmysofa-0:1.3.3-4.fc44.x8 100% | 425.5 KiB/s |  45.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1066/1521] libplacebo-0:7.360.1-3.fc44 100% | 688.3 KiB/s | 454.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1067/1521] libswscale-free-0:8.0.1-6.f 100% | 623.1 KiB/s | 263.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1068/1521] libavfilter-free-0:8.0.1-6. 100% | 838.4 KiB/s |   1.6 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1069/1521] lilv-libs-0:0.26.4-1.fc44.x 100% | 296.0 KiB/s |  58.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1070/1521] libvmaf-0:3.0.0-5.fc44.x86_ 100% | 588.0 KiB/s | 202.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1071/1521] rubberband-libs-0:4.0.0-5.f 100% | 641.9 KiB/s | 177.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1072/1521] vid.stab-0:1.1.1-8.fc44.x86 100% | 259.9 KiB/s |  50.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1073/1521] zimg-0:3.0.6-3.fc44.x86_64  100% | 671.9 KiB/s | 236.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1074/1521] libunibreak-0:6.1-5.fc44.x8 100% | 289.4 KiB/s |  33.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1075/1521] libdovi-0:3.3.2-2.fc44.x86_ 100% | 615.6 KiB/s | 265.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1076/1521] serd-0:0.32.8-1.fc44.x86_64 100% | 348.1 KiB/s |  67.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1077/1521] tesseract-libs-0:5.5.2-1.fc 100% | 833.9 KiB/s |   1.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1078/1521] sord-0:0.16.22-1.fc44.x86_6 100% | 347.5 KiB/s |  37.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1079/1521] sratom-0:0.6.22-1.fc44.x86_ 100% | 255.6 KiB/s |  27.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1080/1521] zix-0:0.8.0-2.fc44.x86_64   100% | 327.6 KiB/s |  35.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1081/1521] fftw-libs-double-0:3.3.10-1 100% | 849.8 KiB/s |   1.2 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1082/1521] tesseract-common-0:5.5.2-1. 100% | 214.4 KiB/s |  24.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1083/1521] leptonica-0:1.87.0-3.fc44.x 100% | 835.5 KiB/s |   1.3 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1084/1521] tesseract-tessdata-doc-0:4. 100% | 117.3 KiB/s |  13.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1085/1521] tesseract-langpack-eng-0:4. 100% | 848.3 KiB/s |   1.7 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1086/1521] intel-gmmlib-0:22.10.0-1.fc 100% | 573.7 KiB/s | 203.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1087/1521] ghostscript-0:10.06.0-2.fc4 100% | 332.6 KiB/s |  35.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1088/1521] ghostscript-tools-fontutils 100% | 101.3 KiB/s |  11.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1089/1521] ghostscript-tools-printing- 100% | 106.5 KiB/s |  12.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1090/1521] cups-1:2.4.18-1.fc44.x86_64 100% |   2.6 MiB/s |   1.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1091/1521] cups-client-1:2.4.18-1.fc44 100% |   1.0 MiB/s |  72.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1092/1521] cups-filesystem-1:2.4.18-1. 100% | 180.7 KiB/s |  12.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1093/1521] cups-libs-1:2.4.18-1.fc44.x 100% |   3.4 MiB/s | 270.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1094/1521] samba-client-2:4.24.1-1.fc4 100% |   8.5 MiB/s | 796.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1095/1521] samba-client-libs-2:4.24.1- 100% |  18.7 MiB/s |   3.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1096/1521] libva-intel-media-driver-0: 100% | 860.8 KiB/s |   3.1 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [1097/1521] samba-common-2:4.24.1-1.fc4 100% |   2.5 MiB/s | 182.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1098/1521] samba-ndr-libs-2:4.24.1-1.f 100% |  15.4 MiB/s |   1.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1099/1521] libsmbclient-2:4.24.1-1.fc4 100% |   1.1 MiB/s |  82.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1100/1521] nss-mdns-0:0.15.1-28.fc44.x 100% | 237.5 KiB/s |  46.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1101/1521] samba-core-libs-2:4.24.1-1. 100% |   1.1 MiB/s | 513.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1102/1521] git-0:2.54.0-1.fc44.x86_64  100% | 598.8 KiB/s |  41.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1103/1521] perl-Getopt-Long-1:2.58-521 100% | 327.9 KiB/s |  63.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1104/1521] perl-TermReadKey-0:2.38-27. 100% | 214.9 KiB/s |  35.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1105/1521] perl-PathTools-0:3.94-521.f 100% | 255.3 KiB/s |  87.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1106/1521] git-core-0:2.54.0-1.fc44.x8 100% |  38.7 MiB/s |   5.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1107/1521] perl-Git-0:2.54.0-1.fc44.no 100% | 549.3 KiB/s |  37.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1108/1521] git-core-doc-0:2.54.0-1.fc4 100% |  12.2 MiB/s |   3.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1109/1521] perl-Exporter-0:5.79-521.fc 100% | 293.5 KiB/s |  30.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1110/1521] perl-Pod-Usage-4:2.05-521.f 100% | 373.0 KiB/s |  40.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1111/1521] perl-Text-ParseWords-0:3.31 100% | 151.1 KiB/s |  16.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1112/1521] perl-constant-0:1.33-522.fc 100% | 220.2 KiB/s |  22.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1113/1521] perl-Carp-0:1.54-521.fc44.n 100% | 269.0 KiB/s |  28.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1114/1521] perl-Scalar-List-Utils-5:1. 100% | 380.8 KiB/s |  75.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1115/1521] perl-Pod-Perldoc-0:3.28.01- 100% | 448.5 KiB/s |  86.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1116/1521] perl-Error-1:0.17030-3.fc44 100% | 115.8 KiB/s |  40.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1117/1521] flite-0:2.2-13.fc44.x86_64  100% |   1.1 MiB/s |  12.5 MiB |  00m11s[0m
[1;31m==> proxmox-clone.fedora: [1118/1521] perl-File-Temp-1:0.231.200- 100% | 246.1 KiB/s |  59.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1119/1521] perl-podlators-1:6.0.2-521. 100% | 483.0 KiB/s | 128.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1120/1521] perl-HTTP-Tiny-0:0.092-2.fc 100% | 529.4 KiB/s |  57.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1121/1521] perl-Pod-Simple-1:3.47-4.fc 100% |   2.0 MiB/s | 220.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1122/1521] perl-parent-1:0.244-521.fc4 100% | 140.4 KiB/s |  14.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1123/1521] perl-Term-ANSIColor-0:5.01- 100% | 253.6 KiB/s |  47.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1124/1521] perl-Term-Cap-0:1.18-521.fc 100% | 207.5 KiB/s |  22.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1125/1521] perl-File-Path-0:2.18-522.f 100% | 320.5 KiB/s |  35.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1126/1521] perl-IO-Socket-SSL-0:2.098- 100% |   2.1 MiB/s | 234.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1127/1521] perl-MIME-Base64-0:3.16-521 100% | 270.6 KiB/s |  29.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1128/1521] perl-Socket-4:2.040-3.fc44. 100% | 517.0 KiB/s |  55.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1129/1521] perl-Time-HiRes-4:1.9778-52 100% | 307.5 KiB/s |  57.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1130/1521] perl-Time-Local-2:1.350-521 100% | 322.5 KiB/s |  34.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1131/1521] perl-Pod-Escapes-1:1.07-521 100% | 181.6 KiB/s |  19.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1132/1521] perl-Text-Tabs+Wrap-0:2024. 100% | 199.5 KiB/s |  21.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1133/1521] perl-IO-Socket-IP-0:0.43-52 100% | 390.4 KiB/s |  42.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1134/1521] perl-Net-SSLeay-0:1.94-12.f 100% | 742.4 KiB/s | 373.4 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1135/1521] perl-Data-Dumper-0:2.191-52 100% | 523.6 KiB/s |  56.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1136/1521] perl-MIME-Base32-0:1.303-25 100% | 159.1 KiB/s |  20.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1137/1521] perl-URI-0:5.34-3.fc44.noar 100% | 540.7 KiB/s | 149.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1138/1521] perl-libnet-0:3.15-522.fc44 100% |   1.1 MiB/s | 128.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1139/1521] perl-Digest-MD5-0:2.59-521. 100% | 336.6 KiB/s |  36.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1140/1521] default-editor-0:8.7.1-2.fc 100% | 119.8 KiB/s |   8.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1141/1521] perl-Digest-0:1.20-521.fc44 100% | 241.3 KiB/s |  24.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1142/1521] ibus-anthy-0:1.5.18-1.fc44. 100% |   3.2 MiB/s | 887.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1143/1521] ibus-anthy-python-0:1.5.18- 100% | 686.5 KiB/s | 181.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1144/1521] kasumi-unicode-0:2.5-50.fc4 100% | 703.5 KiB/s |  75.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1145/1521] kasumi-common-0:2.5-50.fc44 100% | 133.6 KiB/s |  14.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1146/1521] ibus-gtk3-0:1.5.34-1.fc44.x 100% | 499.0 KiB/s |  33.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1147/1521] ibus-0:1.5.34-1.fc44.x86_64 100% |  47.8 MiB/s |  15.5 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1148/1521] python3-ibus-0:1.5.34-1.fc4 100% | 337.1 KiB/s |  23.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1149/1521] ibus-libs-0:1.5.34-1.fc44.x 100% | 609.9 KiB/s | 270.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1150/1521] ibus-gtk4-0:1.5.34-1.fc44.x 100% | 480.6 KiB/s |  33.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1151/1521] ibus-typing-booster-0:2.30. 100% |   6.1 MiB/s |   1.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1152/1521] python3-enchant-0:3.3.0-2.f 100% | 431.3 KiB/s | 113.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1153/1521] python3-pyxdg-0:0.28-1.fc44 100% | 500.7 KiB/s | 133.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1154/1521] cldr-emoji-annotation-1:48. 100% |   6.5 MiB/s |   9.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1155/1521] unicode-ucd-0:17.0.0-2.fc44 100% |   4.3 MiB/s |   6.2 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1156/1521] cldr-emoji-annotation-dtd-1 100% | 281.1 KiB/s |  32.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1157/1521] python3-rapidfuzz-0:3.14.3- 100% | 849.0 KiB/s |   1.9 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1158/1521] openpace-0:1.1.3-5.fc44.x86 100% | 928.3 KiB/s | 105.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1159/1521] pcsc-lite-0:2.4.1-2.fc44.x8 100% | 856.4 KiB/s |  97.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1160/1521] opensc-0:0.27.1-2.fc44.x86_ 100% | 989.8 KiB/s | 439.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1161/1521] pinentry-gnome3-0:1.3.2-3.f 100% | 679.0 KiB/s |  45.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1162/1521] bind-utils-32:9.18.48-1.fc4 100% |   2.6 MiB/s | 225.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1163/1521] bind-libs-32:9.18.48-1.fc44 100% |   7.3 MiB/s |   1.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1164/1521] opensc-libs-0:0.27.1-2.fc44 100% |   1.7 MiB/s | 970.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1165/1521] fstrm-0:0.6.1-14.fc44.x86_6 100% | 280.2 KiB/s |  29.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1166/1521] libmaxminddb-0:1.13.3-1.fc4 100% | 415.4 KiB/s |  44.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1167/1521] cyrus-sasl-plain-0:2.1.28-3 100% | 228.5 KiB/s |  24.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1168/1521] ethtool-2:7.0-1.fc44.x86_64 100% |   4.1 MiB/s | 331.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1169/1521] mediawriter-0:5.3.1-1.fc44. 100% |  11.0 MiB/s |   1.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1170/1521] libuv-1:1.51.0-3.fc44.x86_6 100% | 636.9 KiB/s | 270.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1171/1521] nfs-utils-1:2.8.7-1.fc44.x8 100% |   3.4 MiB/s | 239.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1172/1521] gssproxy-0:0.9.2-10.fc44.x8 100% | 604.0 KiB/s | 117.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1173/1521] rpcbind-0:1.2.8-1.fc44.x86_ 100% | 254.3 KiB/s |  60.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1174/1521] libnfsidmap-1:2.8.7-1.fc44. 100% |   1.0 MiB/s |  63.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1175/1521] nfs-client-utils-1:2.8.7-1. 100% | 183.6 KiB/s |  12.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1176/1521] nfs-common-utils-1:2.8.7-1. 100% |   2.3 MiB/s | 159.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1177/1521] nfsv3-client-utils-1:2.8.7- 100% |   1.0 MiB/s |  69.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1178/1521] sssd-nfs-idmap-0:2.12.0-4.f 100% | 272.6 KiB/s |  34.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1179/1521] nfsv4-client-utils-1:2.8.7- 100% | 660.6 KiB/s |  45.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1180/1521] pciutils-0:3.14.0-3.fc44.x8 100% |   1.1 MiB/s | 125.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1181/1521] pciutils-libs-0:3.14.0-3.fc 100% | 498.4 KiB/s |  53.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1182/1521] qt6-qtwayland-adwaita-decor 100% | 891.2 KiB/s |  57.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1183/1521] cmake-filesystem-0:4.3.0-1. 100% | 142.8 KiB/s |  15.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1184/1521] qt6-qtwayland-0:6.10.3-1.fc 100% |   8.8 MiB/s | 787.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1185/1521] libglvnd-opengl-1:1.7.0-9.f 100% | 357.2 KiB/s |  37.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1186/1521] double-conversion-0:3.4.0-3 100% | 513.3 KiB/s |  53.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1187/1521] qt6-qtbase-0:6.10.3-1.fc44. 100% |  22.6 MiB/s |   4.3 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1188/1521] libb2-0:0.98.1-15.fc44.x86_ 100% | 242.4 KiB/s |  26.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1189/1521] qt6-qtbase-common-0:6.10.3- 100% | 174.3 KiB/s |  11.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1190/1521] qt6-qtsvg-0:6.10.3-1.fc44.x 100% |   4.5 MiB/s | 309.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1191/1521] pcre2-utf16-0:10.47-1.fc44. 100% | 738.6 KiB/s | 256.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1192/1521] qt6-qtdeclarative-0:6.10.3- 100% |  62.9 MiB/s |  14.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1193/1521] libxkbcommon-x11-0:1.13.1-2 100% | 221.5 KiB/s |  23.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1194/1521] qt6-qtbase-gui-0:6.10.3-1.f 100% |  28.1 MiB/s |   8.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1195/1521] mtdev-0:1.1.6-12.fc44.x86_6 100% | 203.7 KiB/s |  21.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1196/1521] xcb-util-cursor-0:0.1.6-2.f 100% | 171.8 KiB/s |  18.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1197/1521] tslib-0:1.24-2.fc44.x86_64  100% | 838.6 KiB/s | 156.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1198/1521] xcb-util-image-0:0.4.1-9.fc 100% | 179.6 KiB/s |  18.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1199/1521] xcb-util-keysyms-0:0.4.1-9. 100% | 127.5 KiB/s |  14.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1200/1521] xcb-util-renderutil-0:0.3.1 100% | 166.0 KiB/s |  17.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1201/1521] anthy-unicode-0:1.0.0.20260 100% | 814.5 KiB/s |   5.7 MiB |  00m07s[0m
[1;31m==> proxmox-clone.fedora: [1202/1521] xcb-util-wm-0:0.4.2-9.fc44. 100% | 273.1 KiB/s |  30.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1203/1521] xcb-util-0:0.4.1-9.fc44.x86 100% | 170.7 KiB/s |  17.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1204/1521] sos-0:4.11.1-1.fc44.noarch  100% |  15.8 MiB/s |   1.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1205/1521] python3-packaging-0:25.0-8. 100% |   1.4 MiB/s | 161.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1206/1521] python3-ptyprocess-0:0.7.0- 100% | 343.9 KiB/s |  36.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1207/1521] gamemode-0:1.8.2-4.fc44.x86 100% |   1.0 MiB/s | 113.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1208/1521] libwbclient-2:4.24.1-1.fc44 100% | 758.7 KiB/s |  49.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1209/1521] python3-pexpect-0:4.9.0-15. 100% | 663.5 KiB/s | 177.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1210/1521] pam_afs_session-0:2.6-25.fc 100% | 428.9 KiB/s |  46.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1211/1521] ngtcp2-crypto-gnutls-0:1.22 100% | 390.1 KiB/s |  24.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1212/1521] imath-0:3.1.12-6.fc44.x86_6 100% | 549.9 KiB/s | 101.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1213/1521] kf6-kimageformats-0:6.25.0- 100% |   2.9 MiB/s | 777.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1214/1521] kf6-filesystem-0:6.25.0-1.f 100% | 102.7 KiB/s |  11.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1215/1521] jxrlib-0:1.1-33.fc44.x86_64 100% |   2.4 MiB/s | 460.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1216/1521] LibRaw-0:0.22.1-1.fc44.x86_ 100% | 732.9 KiB/s | 485.2 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1217/1521] kf6-karchive-0:6.25.0-1.fc4 100% | 647.2 KiB/s | 222.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1218/1521] kde-filesystem-0:5-7.fc44.x 100% | 350.1 KiB/s |  37.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1219/1521] openexr-libs-0:3.2.4-7.fc44 100% |   3.3 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1220/1521] libdrm-0:2.4.133-1.fc44.x86 100% |   2.4 MiB/s | 166.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1221/1521] glx-utils-0:9.0.0-11.fc44.x 100% | 677.4 KiB/s |  70.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1222/1521] libdeflate-0:1.25-3.fc44.x8 100% | 369.1 KiB/s |  69.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1223/1521] libinput-0:1.31.1-1.fc44.x8 100% |   4.1 MiB/s | 275.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1224/1521] qt6-filesystem-0:6.10.3-1.f 100% | 154.8 KiB/s |  10.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1225/1521] gstreamer1-0:1.28.2-1.fc44. 100% |  20.9 MiB/s |   1.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1226/1521] python3-gobject-base-0:3.56 100% |   2.1 MiB/s | 403.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1227/1521] gstreamer1-plugins-base-0:1 100% |  11.1 MiB/s |   2.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1228/1521] cdparanoia-libs-0:10.2-50.f 100% | 296.1 KiB/s |  56.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1229/1521] libXv-0:1.0.13-4.fc44.x86_6 100% | 177.8 KiB/s |  18.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1230/1521] perl-interpreter-4:5.42.2-5 100% |   1.0 MiB/s |  72.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1231/1521] perl-libs-4:5.42.2-524.fc44 100% |  28.3 MiB/s |   2.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1232/1521] perl-Errno-0:1.38-524.fc44. 100% | 216.3 KiB/s |  14.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1233/1521] gsettings-desktop-schemas-0 100% |  10.3 MiB/s | 864.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1234/1521] libvisual-1:0.4.2-4.fc44.x8 100% | 585.0 KiB/s | 158.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1235/1521] gtk4-0:4.22.4-1.fc44.x86_64 100% |  35.8 MiB/s |   6.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1236/1521] udisks2-0:2.11.1-2.fc44.x86 100% |   7.9 MiB/s | 565.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1237/1521] llvm-filesystem-0:22.1.4-1. 100% |  69.8 KiB/s |   9.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1238/1521] libudisks2-0:2.11.1-2.fc44. 100% |   3.2 MiB/s | 220.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1239/1521] totem-pl-parser-0:3.26.7-1. 100% |   2.2 MiB/s | 148.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1240/1521] giflib-0:6.1.3-1.fc44.x86_6 100% | 322.8 KiB/s |  55.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1241/1521] uchardet-0:0.0.8-10.fc44.x8 100% |   1.0 MiB/s | 106.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1242/1521] upower-libs-0:1.91.2-1.fc44 100% | 931.5 KiB/s |  60.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1243/1521] upower-0:1.91.2-1.fc44.x86_ 100% | 771.1 KiB/s | 132.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1244/1521] javapackages-filesystem-0:6 100% | 127.4 KiB/s |  13.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1245/1521] llvm-libs-0:22.1.4-1.fc44.x 100% |  46.9 MiB/s |  34.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1246/1521] lksctp-tools-0:1.0.21-3.fc4 100% | 918.9 KiB/s |  97.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1247/1521] java-25-openjdk-crypto-adap 100% |   1.9 MiB/s | 143.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1248/1521] tzdata-java-0:2026a-1.fc44. 100% | 441.9 KiB/s |  45.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1249/1521] autocorr-en-1:26.2.2.2-2.fc 100% |   1.4 MiB/s | 103.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1250/1521] hunspell-en-US-0:0.20260225 100% |   1.5 MiB/s | 171.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1251/1521] harfbuzz-icu-0:14.1.0-2.fc4 100% | 251.4 KiB/s |  16.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1252/1521] libaom-0:3.13.3-1.fc44.x86_ 100% |   6.1 MiB/s |   1.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1253/1521] openh264-0:2.6.0-3.fc44.x86 100% |   1.4 MiB/s | 435.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1254/1521] mozilla-openh264-0:2.6.0-3. 100% |   3.6 MiB/s | 442.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1255/1521] evolution-data-server-0:3.6 100% |  15.7 MiB/s |   2.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1256/1521] java-25-openjdk-headless-1: 100% |  48.5 MiB/s |  58.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1257/1521] evolution-data-server-langp 100% |   8.3 MiB/s |   1.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1258/1521] mutter-0:50.1-1.fc44.x86_64 100% |  26.0 MiB/s |   2.4 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1259/1521] libphonenumber-0:8.13.55-9. 100% |   2.4 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1260/1521] startup-notification-0:0.12 100% | 380.2 KiB/s |  41.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1261/1521] libeis-0:1.5.0-2.fc44.x86_6 100% | 209.4 KiB/s |  54.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1262/1521] mutter-common-0:50.1-1.fc44 100% | 313.2 KiB/s |  20.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1263/1521] tecla-0:50.0-1.fc44.x86_64  100% | 636.0 KiB/s |  69.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1264/1521] libatomic-0:16.0.1-0.10.fc4 100% | 423.3 KiB/s |  45.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1265/1521] libmanette-0:0.2.13-2.fc44. 100% | 645.8 KiB/s |  67.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1266/1521] webkitgtk6.0-0:2.52.3-1.fc4 100% |  64.8 MiB/s |  27.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1267/1521] javascriptcoregtk6.0-0:2.52 100% |  32.8 MiB/s |   8.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1268/1521] hidapi-0:0.15.0-3.fc44.x86_ 100% | 452.8 KiB/s |  48.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1269/1521] libshumate-0:1.6.1-1.fc44.x 100% |   3.2 MiB/s | 221.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1270/1521] iio-sensor-proxy-0:3.8-2.fc 100% | 624.6 KiB/s |  66.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1271/1521] gnome-online-accounts-0:3.5 100% |   5.1 MiB/s | 358.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1272/1521] gnome-online-accounts-libs- 100% |   3.1 MiB/s | 219.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1273/1521] perl-File-Basename-0:2.86-5 100% | 264.6 KiB/s |  16.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1274/1521] perl-IPC-Open3-0:1.24-524.f 100% | 343.5 KiB/s |  23.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1275/1521] perl-lib-0:0.65-524.fc44.x8 100% | 237.3 KiB/s |  14.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1276/1521] javascriptcoregtk4.1-0:2.52 100% |  37.8 MiB/s |   8.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1277/1521] protobuf-0:3.19.6-20.fc44.x 100% | 714.4 KiB/s |   1.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1278/1521] NetworkManager-ssh-selinux- 100% | 291.1 KiB/s |  18.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1279/1521] libsodium-0:1.0.22-1.fc44.x 100% |   2.8 MiB/s | 210.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1280/1521] hwdata-0:0.406-1.fc44.noarc 100% |  17.8 MiB/s |   1.7 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1281/1521] webkit2gtk4.1-0:2.52.3-1.fc 100% |  47.9 MiB/s |  27.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1282/1521] libtommath-0:1.3.1~rc1-7.fc 100% | 354.3 KiB/s |  64.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1283/1521] python3-gobject-0:3.56.2-1. 100% | 163.9 KiB/s |  18.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1284/1521] tcl-1:9.0.2-1.fc44.x86_64   100% |   2.7 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1285/1521] SDL3-0:3.4.4-1.fc44.x86_64  100% |  15.1 MiB/s |   1.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1286/1521] python3-cairo-0:1.28.0-5.fc 100% | 378.9 KiB/s | 130.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1287/1521] gst-editing-services-0:1.28 100% |   6.5 MiB/s | 461.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1288/1521] libdecor-0:0.2.5-2.fc44.x86 100% | 533.5 KiB/s |  59.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1289/1521] xen-libs-0:4.21.1-2.fc44.x8 100% |   7.6 MiB/s | 672.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1290/1521] librados2-2:20.2.1-1.fc44.x 100% |  24.2 MiB/s |   4.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1291/1521] edk2-ovmf-0:20260213-6.fc44 100% |  48.5 MiB/s |  17.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1292/1521] lttng-ust-0:2.14.0-5.fc44.x 100% |   2.0 MiB/s | 376.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1293/1521] librbd1-2:20.2.1-1.fc44.x86 100% |  33.4 MiB/s |   3.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1294/1521] libpmemobj-0:2.1.0-5.fc44.x 100% |   1.5 MiB/s | 163.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1295/1521] liblouis-0:3.33.0-7.fc44.x8 100% |   1.9 MiB/s | 214.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1296/1521] gtksourceview4-0:4.8.4-11.f 100% | 789.7 KiB/s | 897.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1297/1521] augeas-libs-0:1.14.2-0.11.2 100% |   5.8 MiB/s | 426.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1298/1521] perl-Encode-4:3.21-521.fc44 100% | 828.8 KiB/s |   1.1 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1299/1521] perl-Storable-1:3.37-522.fc 100% | 519.9 KiB/s | 100.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1300/1521] perl-POSIX-0:2.23-524.fc44. 100% |   1.3 MiB/s |  96.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1301/1521] perl-Fcntl-0:1.20-524.fc44. 100% | 454.0 KiB/s |  29.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1302/1521] perl-FileHandle-0:2.05-524. 100% | 238.7 KiB/s |  15.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1303/1521] thrift-0:0.20.0-9.fc44.x86_ 100% | 851.7 KiB/s |   1.9 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1304/1521] perl-IO-0:1.55-524.fc44.x86 100% |   1.3 MiB/s |  81.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1305/1521] perl-base-0:2.27-524.fc44.n 100% | 246.0 KiB/s |  16.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1306/1521] perl-overload-0:1.40-524.fc 100% | 708.5 KiB/s |  45.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1307/1521] perl-Symbol-0:1.09-524.fc44 100% |  68.9 KiB/s |  14.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1308/1521] perl-DynaLoader-0:1.57-524. 100% | 402.8 KiB/s |  25.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1309/1521] perl-vars-0:1.05-524.fc44.n 100% | 163.7 KiB/s |  12.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1310/1521] perl-if-0:0.61.000-524.fc44 100% | 222.3 KiB/s |  13.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1311/1521] perl-Getopt-Std-0:1.14-524. 100% | 245.7 KiB/s |  15.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1312/1521] perl-AutoLoader-0:5.74-524. 100% | 236.2 KiB/s |  21.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1313/1521] perl-B-0:1.89-524.fc44.x86_ 100% |   2.6 MiB/s | 177.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1314/1521] pam_passwdqc-0:2.0.3-9.fc44 100% | 163.9 KiB/s |  17.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1315/1521] libsigc++30-0:3.8.0-1.fc44. 100% | 639.3 KiB/s |  40.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1316/1521] pcsc-lite-ccid-0:1.7.1-2.fc 100% | 455.9 KiB/s | 122.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1317/1521] xmlsec1-openssl-1:1.2.41-4. 100% | 495.4 KiB/s |  96.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1318/1521] iscsi-initiator-utils-iscsi 100% | 429.4 KiB/s |  82.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1319/1521] isns-utils-libs-0:0.103-4.f 100% | 555.8 KiB/s | 111.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1320/1521] iscsi-initiator-utils-0:6.2 100% | 671.1 KiB/s | 401.3 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1321/1521] liblouis-tables-0:3.33.0-7. 100% | 744.1 KiB/s |   2.3 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [1322/1521] gweather-locations-common-0 100% | 702.1 KiB/s | 187.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1323/1521] srt-libs-0:1.5.5-1.fc44.x86 100% |   5.6 MiB/s | 423.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1324/1521] python3-pillow-0:12.2.0-1.f 100% |  14.0 MiB/s |   1.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1325/1521] libraqm-0:0.10.1-4.fc44.x86 100% | 206.3 KiB/s |  22.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1326/1521] python3-olefile-0:0.47-13.f 100% | 401.0 KiB/s |  75.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1327/1521] epiphany-runtime-1:50.3-1.f 100% |  13.9 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1328/1521] libxmlb-0:0.3.26-1.fc44.x86 100% |   1.8 MiB/s | 119.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1329/1521] ostree-libs-0:2026.1-1.fc44 100% |   6.8 MiB/s | 489.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1330/1521] systemd-container-0:259.5-1 100% | 802.1 KiB/s | 908.8 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1331/1521] xorg-x11-server-Xwayland-0: 100% |  13.8 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1332/1521] libXdmcp-0:1.1.5-5.fc44.x86 100% | 350.2 KiB/s |  37.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1333/1521] liboeffis-0:1.5.0-2.fc44.x8 100% | 208.8 KiB/s |  22.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1334/1521] libXfont2-0:2.0.7-4.fc44.x8 100% | 567.5 KiB/s | 149.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1335/1521] libxcvt-0:0.1.2-11.fc44.x86 100% | 129.6 KiB/s |  13.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1336/1521] libmpc-0:1.4.1-1.fc44.x86_6 100% |   1.0 MiB/s |  75.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1337/1521] libfontenc-0:1.1.8-5.fc44.x 100% | 299.5 KiB/s |  32.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1338/1521] libjcat-0:0.2.6-1.fc44.x86_ 100% |   1.3 MiB/s |  85.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1339/1521] passim-libs-0:0.1.11-1.fc44 100% | 504.3 KiB/s |  32.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1340/1521] xdg-dbus-proxy-0:0.1.7-1.fc 100% | 728.4 KiB/s |  46.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1341/1521] distribution-gpg-keys-0:1.1 100% |  10.0 MiB/s | 806.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1342/1521] python3-click-1:8.3.3-1.fc4 100% |   3.8 MiB/s | 271.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1343/1521] texlive-lib-12:20260301-109 100% |   7.6 MiB/s | 538.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1344/1521] elfutils-0:0.195-1.fc44.x86 100% |   8.3 MiB/s | 588.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1345/1521] wireless-regdb-0:2026.03.18 100% | 259.6 KiB/s |  16.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1346/1521] iw-0:6.17-2.fc44.x86_64     100% | 466.2 KiB/s | 124.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1347/1521] ppp-0:2.5.1-7.fc44.x86_64   100% | 775.6 KiB/s | 391.7 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1348/1521] linux-atm-libs-0:2.5.1-46.f 100% | 366.5 KiB/s |  39.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1349/1521] openvpn-0:2.7.3-1.fc44.x86_ 100% |   9.2 MiB/s | 717.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1350/1521] pkcs11-helper-0:1.30.0-5.fc 100% | 375.3 KiB/s |  69.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1351/1521] gweather-locations-0:2026.2 100% | 857.8 KiB/s |   2.8 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: [1352/1521] xen-licenses-0:4.21.1-2.fc4 100% | 620.2 KiB/s |  43.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1353/1521] xkbcomp-0:1.5.0-2.fc44.x86_ 100% | 552.9 KiB/s | 103.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1354/1521] libblockdev-0:3.5.0-1.fc44. 100% |   1.6 MiB/s | 107.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1355/1521] libblockdev-crypto-0:3.5.0- 100% | 662.0 KiB/s |  42.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1356/1521] libblockdev-utils-0:3.5.0-1 100% | 161.7 KiB/s |  32.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1357/1521] libblockdev-fs-0:3.5.0-1.fc 100% | 854.8 KiB/s |  55.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1358/1521] libblockdev-loop-0:3.5.0-1. 100% | 374.8 KiB/s |  24.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1359/1521] volume_key-libs-0:0.3.12-29 100% | 565.0 KiB/s | 149.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1360/1521] libblockdev-mdraid-0:3.5.0- 100% | 456.2 KiB/s |  29.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1361/1521] libblockdev-nvme-0:3.5.0-1. 100% | 527.2 KiB/s |  33.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1362/1521] libbytesize-0:2.12-2.fc44.x 100% | 435.2 KiB/s |  46.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1363/1521] libblockdev-part-0:3.5.0-1. 100% | 491.0 KiB/s |  31.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1364/1521] libblockdev-smart-0:3.5.0-1 100% | 267.4 KiB/s |  25.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1365/1521] libblockdev-swap-0:3.5.0-1. 100% | 373.1 KiB/s |  24.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1366/1521] perl-mro-0:1.29-524.fc44.x8 100% | 462.4 KiB/s |  29.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1367/1521] libatasmart-0:0.19-32.fc44. 100% | 250.2 KiB/s |  48.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1368/1521] perl-overloading-0:0.02-524 100% | 160.5 KiB/s |  12.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1369/1521] perl-locale-0:1.13-524.fc44 100% | 179.5 KiB/s |  13.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1370/1521] perl-File-stat-0:1.14-524.f 100% | 263.1 KiB/s |  16.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1371/1521] perl-SelectSaver-0:1.02-524 100% | 155.5 KiB/s |  11.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1372/1521] perl-Class-Struct-0:0.68-52 100% | 331.3 KiB/s |  21.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1373/1521] pipewire-jack-audio-connect 100% |   2.3 MiB/s | 151.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1374/1521] pipewire-jack-audio-connect 100% | 195.6 KiB/s |  12.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1375/1521] libreoffice-gtk4-1:26.2.2.2 100% |   1.4 MiB/s | 505.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1376/1521] fedora-logos-httpd-0:42.0.1 100% |  79.9 KiB/s |  14.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1377/1521] libverto-libev-0:0.3.2-12.f 100% | 119.1 KiB/s |  12.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1378/1521] libev-0:4.33-15.fc44.x86_64 100% | 288.6 KiB/s |  53.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1379/1521] ntfs-3g-system-compression- 100% | 266.7 KiB/s |  29.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1380/1521] gstreamer1-plugins-good-qt6 100% |   1.3 MiB/s |  93.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1381/1521] hunspell-en-0:0.20260225-2. 100% | 218.3 KiB/s |  14.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1382/1521] hunspell-en-AU-0:0.20260225 100% |   2.5 MiB/s | 168.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1383/1521] hunspell-en-CA-0:0.20260225 100% |   2.5 MiB/s | 168.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1384/1521] hunspell-en-GB-0:0.20260225 100% |   3.3 MiB/s | 224.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1385/1521] libreoffice-gtk3-1:26.2.2.2 100% |   7.7 MiB/s | 547.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1386/1521] gstreamer1-plugins-good-gtk 100% | 536.0 KiB/s |  33.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1387/1521] ipset-0:7.24-3.fc44.x86_64  100% | 237.1 KiB/s |  43.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1388/1521] ipset-libs-0:7.24-3.fc44.x8 100% | 371.4 KiB/s |  69.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1389/1521] libcap-ng-python3-0:0.9.2-1 100% | 285.4 KiB/s |  35.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1390/1521] fedora-logos-0:42.0.1-3.fc4 100% | 842.3 KiB/s |   1.5 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1391/1521] libavdevice-free-0:8.0.1-6. 100% | 434.6 KiB/s |  81.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1392/1521] binutils-0:2.46-1.fc44.x86_ 100% |   1.2 MiB/s |   6.1 MiB |  00m05s[0m
[1;31m==> proxmox-clone.fedora: [1393/1521] libcaca-0:0.99-0.82.beta20. 100% |   1.4 MiB/s | 227.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1394/1521] libavc1394-0:0.5.4-27.fc44. 100% | 291.9 KiB/s |  55.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1395/1521] libiec61883-0:1.2.0-39.fc44 100% | 378.7 KiB/s |  41.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1396/1521] libraw1394-0:2.1.2-25.fc44. 100% | 618.1 KiB/s |  65.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1397/1521] libdc1394-0:2.2.7-9.fc44.x8 100% | 502.3 KiB/s | 133.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1398/1521] freeglut-0:3.8.0-2.fc44.x86 100% |   1.4 MiB/s | 153.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1399/1521] slang-0:2.3.3-9.fc44.x86_64 100% |   4.0 MiB/s | 463.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1400/1521] mesa-libGLU-0:9.0.3-8.fc44. 100% | 639.6 KiB/s | 170.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1401/1521] speech-dispatcher-utils-0:0 100% | 238.2 KiB/s |  25.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1402/1521] pulseaudio-utils-0:17.0-9.f 100% | 485.7 KiB/s |  90.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1403/1521] polkit-pkla-compat-0:0.1-32 100% | 401.8 KiB/s |  43.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1404/1521] braille-printer-app-1:2.0~b 100% | 293.2 KiB/s |  55.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1405/1521] liblouisutdml-utils-0:2.12. 100% | 274.3 KiB/s |  29.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1406/1521] antiword-0:0.37-44.fc44.x86 100% | 668.2 KiB/s | 176.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1407/1521] liblouisutdml-0:2.12.0-8.fc 100% | 620.4 KiB/s | 163.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1408/1521] avahi-tools-0:0.9~rc2-8.fc4 100% | 378.0 KiB/s |  40.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1409/1521] ffmpeg-free-0:8.0.1-6.fc44. 100% | 862.0 KiB/s |   2.0 MiB |  00m02s[0m
[1;31m==> proxmox-clone.fedora: [1410/1521] p11-kit-server-0:0.26.2-1.f 100% | 207.6 KiB/s |  23.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1411/1521] cifs-utils-info-0:7.5-1.fc4 100% | 181.4 KiB/s |  19.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1412/1521] fedora-chromium-config-gnom 100% | 145.4 KiB/s |  15.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1413/1521] sane-backends-drivers-camer 100% | 594.2 KiB/s | 156.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1414/1521] skopeo-1:1.22.2-1.fc44.x86_ 100% |  10.8 MiB/s |   7.8 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1415/1521] mod_http2-0:2.0.37-2.fc44.x 100% | 623.7 KiB/s | 167.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1416/1521] libvirt-daemon-0:12.0.0-3.f 100% | 546.1 KiB/s | 195.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1417/1521] evince-djvu-0:48.1-2.fc44.x 100% | 281.4 KiB/s |  30.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1418/1521] mod_lua-0:2.4.66-4.fc44.x86 100% | 315.9 KiB/s |  58.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1419/1521] nbdkit-0:1.47.7-1.fc44.x86_ 100% | 236.8 KiB/s |  16.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1420/1521] nbdkit-basic-plugins-0:1.47 100% |   3.1 MiB/s | 217.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1421/1521] nbdkit-server-0:1.47.7-1.fc 100% |   2.1 MiB/s | 146.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1422/1521] zlib-ng-0:2.3.3-3.fc44.x86_ 100% | 530.8 KiB/s |  98.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1423/1521] nbdkit-basic-filters-0:1.47 100% | 912.9 KiB/s | 393.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1424/1521] nbdkit-curl-plugin-0:1.47.7 100% | 747.9 KiB/s |  47.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1425/1521] nbdkit-ssh-plugin-0:1.47.7- 100% | 565.3 KiB/s |  37.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1426/1521] apr-util-openssl-0:1.6.3-27 100% | 149.1 KiB/s |  15.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1427/1521] qatlib-service-0:25.08.0-4. 100% | 212.7 KiB/s |  39.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1428/1521] gnome-software-fedora-langp 100% | 196.5 KiB/s |  26.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1429/1521] jq-0:1.8.1-3.fc44.x86_64    100% |   3.0 MiB/s | 215.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1430/1521] oniguruma-0:6.9.10-4.fc44.x 100% | 630.5 KiB/s | 220.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1431/1521] passim-0:0.1.11-1.fc44.x86_ 100% |   1.5 MiB/s |  99.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1432/1521] fwupd-plugin-flashrom-0:2.1 100% | 230.1 KiB/s |  24.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1433/1521] firefox-langpacks-0:150.0-1 100% |   5.2 MiB/s |  32.9 MiB |  00m06s[0m
[1;31m==> proxmox-clone.fedora: [1434/1521] libftdi-0:1.5-22.fc44.x86_6 100% | 408.5 KiB/s |  45.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1435/1521] libjaylink-0:0.3.0-10.fc44. 100% | 387.8 KiB/s |  42.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1436/1521] fwupd-plugin-modem-manager- 100% | 502.7 KiB/s |  54.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1437/1521] fwupd-efi-0:1.8-1.fc44.x86_ 100% | 442.3 KiB/s |  46.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1438/1521] fwupd-plugin-uefi-capsule-d 100% |   3.9 MiB/s |   5.8 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1439/1521] libwnck3-0:43.3-2.fc44.x86_ 100% |   2.1 MiB/s | 410.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1440/1521] libXres-0:1.2.2-7.fc44.x86_ 100% | 131.4 KiB/s |  15.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1441/1521] bolt-0:0.9.11-1.fc44.x86_64 100% | 504.6 KiB/s | 191.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1442/1521] cpp-0:16.0.1-0.10.fc44.x86_ 100% |   2.3 MiB/s |  14.5 MiB |  00m06s[0m
[1;31m==> proxmox-clone.fedora: [1443/1521] tuned-ppd-0:2.27.0-1.fc44.n 100% | 171.9 KiB/s |  19.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1444/1521] nm-connection-editor-0:1.36 100% |   2.4 MiB/s | 862.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1445/1521] hdparm-0:9.65-10.fc44.x86_6 100% | 554.8 KiB/s |  96.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1446/1521] tuned-0:2.27.0-1.fc44.noarc 100% |   2.7 MiB/s | 536.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1447/1521] python3-inotify-0:0.9.6-43. 100% | 611.4 KiB/s |  66.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1448/1521] python3-linux-procfs-0:0.7. 100% | 342.2 KiB/s |  37.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1449/1521] python3-pyudev-0:0.24.4-3.f 100% | 912.8 KiB/s |  97.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1450/1521] virt-what-0:1.27-5.fc44.x86 100% | 365.3 KiB/s |  39.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1451/1521] malcontent-control-0:0.14.0 100% | 856.4 KiB/s |  94.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1452/1521] malcontent-ui-libs-0:0.14.0 100% | 377.4 KiB/s |  41.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1453/1521] flashrom-0:1.6.0-3.fc44.x86 100% | 867.1 KiB/s |   5.0 MiB |  00m06s[0m
[1;31m==> proxmox-clone.fedora: [1454/1521] gnome-tour-0:50.0-1.fc44.x8 100% |   3.6 MiB/s | 837.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1455/1521] intel-mediasdk-0:23.2.2-11. 100% |  15.0 MiB/s |   3.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1456/1521] exiv2-0:0.28.6-3.fc44.x86_6 100% |   4.0 MiB/s |   2.0 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1457/1521] langpacks-en-0:4.3-1.fc44.n 100% |  76.3 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1458/1521] ipp-usb-0:0.9.31-2.fc44.x86 100% |   3.7 MiB/s |   2.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1459/1521] langpacks-core-en-0:4.3-1.f 100% |  82.9 KiB/s |   8.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1460/1521] langpacks-fonts-en-0:4.3-1. 100% |  85.9 KiB/s |   9.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1461/1521] libreoffice-help-en-1:26.2. 100% |  29.1 MiB/s |   3.2 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1462/1521] libcamera-0:0.7.0-1.fc44.x8 100% |   3.9 MiB/s | 777.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1463/1521] pipewire-plugin-libcamera-0 100% | 271.1 KiB/s |  77.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1464/1521] cups-filters-driverless-1:2 100% | 263.7 KiB/s |  28.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1465/1521] cups-ipptool-1:2.4.18-1.fc4 100% |  36.2 MiB/s |   3.9 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1466/1521] ibus-setup-0:1.5.34-1.fc44. 100% | 749.2 KiB/s |  90.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1467/1521] google-noto-emoji-fonts-0:2 100% |   2.7 MiB/s | 546.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1468/1521] python3-httpx-0:0.28.1-11.f 100% |   1.8 MiB/s | 212.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1469/1521] python3-anyio-0:4.12.1-3.fc 100% | 895.2 KiB/s | 314.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1470/1521] python3-certifi-0:2026.01.0 100% | 130.9 KiB/s |  14.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1471/1521] python3-httpcore-0:1.0.9-6. 100% |   1.3 MiB/s | 157.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1472/1521] python3-h11-0:0.16.0-6.fc44 100% | 710.8 KiB/s |  81.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1473/1521] gdouros-symbola-fonts-0:10. 100% |   2.5 MiB/s |   2.4 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1474/1521] langtable-0:0.0.70-1.fc44.n 100% | 540.2 KiB/s |  62.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1475/1521] python3-pyaudio-0:0.2.13-11 100% | 387.4 KiB/s |  44.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1476/1521] portaudio-0:19.7.0-3.fc44.x 100% | 821.5 KiB/s |  96.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1477/1521] python3-langtable-0:0.0.70- 100% |   2.6 MiB/s |   1.5 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1478/1521] python3-regex-0:2026.2.28-1 100% |   1.5 MiB/s | 425.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1479/1521] wl-clipboard-0:2.2.1^git202 100% | 513.9 KiB/s |  56.5 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1480/1521] qt6-qttranslations-0:6.10.3 100% |  22.5 MiB/s |   2.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1481/1521] python3-jmespath-0:1.0.1-14 100% | 507.6 KiB/s |  59.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1482/1521] python3-boto3-0:1.42.84-1.f 100% |   2.2 MiB/s | 482.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1483/1521] python3-s3transfer-0:0.16.0 100% |   1.5 MiB/s | 166.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1484/1521] python3-botocore-0:1.42.84- 100% |  39.5 MiB/s |   8.6 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1485/1521] python3-dateutil-1:2.9.0.po 100% |   1.8 MiB/s | 344.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1486/1521] python3-file-magic-0:5.46-9 100% | 157.0 KiB/s |  19.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1487/1521] xdriinfo-0:1.0.7-6.fc44.x86 100% | 190.3 KiB/s |  21.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1488/1521] perl-NDBM_File-0:1.18-524.f 100% | 348.4 KiB/s |  22.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1489/1521] adwaita-mono-fonts-0:50.0-1 100% |   2.7 MiB/s |   1.4 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1490/1521] adwaita-sans-fonts-0:50.0-1 100% |   1.5 MiB/s | 764.9 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1491/1521] f2fs-tools-0:1.16.0-10.fc44 100% |   1.3 MiB/s | 242.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1492/1521] udftools-0:2.3-13.fc44.x86_ 100% |   1.4 MiB/s | 167.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1493/1521] evolution-ews-core-0:3.60.1 100% |   7.5 MiB/s | 561.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1494/1521] evolution-ews-langpacks-0:3 100% |   4.2 MiB/s | 293.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1495/1521] edk2-shell-x64-0:20260213-6 100% |   4.6 MiB/s | 322.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1496/1521] qemu-kvm-core-2:10.2.2-1.fc 100% | 129.2 KiB/s |  15.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1497/1521] nilfs-utils-0:2.2.11-8.fc44 100% | 249.3 KiB/s | 167.0 KiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1498/1521] nbdkit-selinux-0:1.47.7-1.f 100% | 468.6 KiB/s |  31.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1499/1521] intel-vpl-gpu-rt-0:26.1.0-1 100% | 866.6 KiB/s |   3.7 MiB |  00m04s[0m
[1;31m==> proxmox-clone.fedora: [1500/1521] ImageMagick-1:7.1.2.13-2.fc 100% | 360.3 KiB/s |  71.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1501/1521] liblqr-1-0:0.4.2-29.fc44.x8 100% | 254.6 KiB/s |  50.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1502/1521] libultrahdr-0:1.4.0^2025120 100% | 603.6 KiB/s | 166.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1503/1521] julietaula-montserrat-fonts 100% |   2.0 MiB/s |   1.6 MiB |  00m01s[0m
[1;31m==> proxmox-clone.fedora: [1504/1521] graphviz-libs-0:14.1.4-2.fc 100% |   6.4 MiB/s | 497.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1505/1521] libwmf-lite-0:0.2.13-9.fc44 100% | 394.6 KiB/s |  74.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1506/1521] kernel-tools-0:6.19.14-300. 100% |   9.9 MiB/s | 752.3 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1507/1521] python3-perf-0:6.19.14-300. 100% |  22.9 MiB/s |   2.0 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1508/1521] libpfm-0:4.13.0-19.fc44.x86 100% |   1.1 MiB/s | 226.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1509/1521] kernel-tools-libs-0:6.19.14 100% |   1.0 MiB/s | 459.1 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1510/1521] libtraceevent-0:1.8.4-5.fc4 100% |   1.4 MiB/s | 279.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1511/1521] open-sans-fonts-0:1.10-25.f 100% |   1.7 MiB/s | 471.7 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1512/1521] libcamera-ipa-0:0.7.0-1.fc4 100% | 551.2 KiB/s | 192.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1513/1521] libldb-2:4.24.1-1.fc44.x86_ 100% |   2.8 MiB/s | 199.6 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1514/1521] pinentry-0:1.3.2-3.fc44.x86 100% |   1.6 MiB/s | 112.9 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1515/1521] ngtcp2-0:1.22.1-1.fc44.x86_ 100% |   2.2 MiB/s | 157.4 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1516/1521] ngtcp2-crypto-ossl-0:1.22.1 100% | 427.0 KiB/s |  27.8 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1517/1521] harfbuzz-0:14.1.0-2.fc44.x8 100% |  14.5 MiB/s |   1.1 MiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1518/1521] elfutils-debuginfod-client- 100% | 700.7 KiB/s |  46.2 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1519/1521] elfutils-libelf-0:0.195-1.f 100% |   3.1 MiB/s | 210.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1520/1521] elfutils-libs-0:0.195-1.fc4 100% |   3.2 MiB/s | 283.0 KiB |  00m00s[0m
[1;31m==> proxmox-clone.fedora: [1521/1521] ImageMagick-libs-1:7.1.2.13 100% | 857.0 KiB/s |   2.6 MiB |  00m03s[0m
[1;31m==> proxmox-clone.fedora: --------------------------------------------------------------------------------[0m
[1;31m==> proxmox-clone.fedora: [1521/1521] Total                       100% |   6.7 MiB/s |   1.7 GiB |  04m14s[0m
[1;31m==> proxmox-clone.fedora: Running transaction[0m
[1;31m==> proxmox-clone.fedora: Importing OpenPGP key 0x6D9F90A6:[0m
[1;31m==> proxmox-clone.fedora:  UserID     : "Fedora (44) <fedora-44-primary@fedoraproject.org>"[0m
[1;31m==> proxmox-clone.fedora:  Fingerprint: 36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6[0m
[1;31m==> proxmox-clone.fedora:  From       : file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-44-x86_64[0m
[1;31m==> proxmox-clone.fedora: The key was successfully imported.[0m
[1;31m==> proxmox-clone.fedora: Transaction failed: Rpm transaction failed.[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-system-x86-core-2:10.2.2-1.fc44.x86_64 needs 52MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package device-mapper-multipath-libs-0.13.1-1.fc44.x86_64 needs 53MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-pr-helper-2:10.2.2-1.fc44.x86_64 needs 54MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package rutabaga-gfx-ffi-0.1.3-5.fc44.x86_64 needs 55MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-device-display-virtio-gpu-rutabaga-2:10.2.2-1.fc44.x86_64 needs 55MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libnfs-6.0.2-7.fc44.x86_64 needs 56MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-block-nfs-2:10.2.2-1.fc44.x86_64 needs 56MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libblkio-1.5.0-5.fc44.x86_64 needs 56MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-block-blkio-2:10.2.2-1.fc44.x86_64 needs 57MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ctags-6.2.1-3.fc44.x86_64 needs 59MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package source-highlight-3.1.9-27.fc44.x86_64 needs 64MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-pycparser-2.22-8.fc44.noarch needs 66MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-cffi-2.0.0-3.fc44.x86_64 needs 68MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-augeas-1.2.0-7.fc44.x86_64 needs 68MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package poppler-data-0.4.11-11.fc44.noarch needs 82MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libpaper-1:2.1.1-10.fc44.x86_64 needs 82MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libijs-0.35-26.fc44.x86_64 needs 82MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package jbig2dec-libs-0.20-8.fc44.x86_64 needs 82MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adobe-mappings-pdf-20190401-12.fc44.noarch needs 87MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package scrub-2.6.1-12.fc44.x86_64 needs 87MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libuser-0.64-17.fc44.x86_64 needs 90MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package usermode-1.114-16.fc44.x86_64 needs 91MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package vpnc-0.5.3^20241114.git11e15a1-4.fc44.x86_64 needs 91MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-vpnc-1:1.4.0-6.fc44.x86_64 needs 92MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package dbus-tools-1:1.16.2-1.fc44.x86_64 needs 92MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-dbus-2.17.8-3.fc44.x86_64 needs 93MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-abrt-2.17.8-3.fc44.x86_64 needs 93MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-2.17.8-3.fc44.x86_64 needs 96MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-addon-kerneloops-2.17.8-3.fc44.x86_64 needs 96MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-addon-pstoreoops-2.17.8-3.fc44.x86_64 needs 96MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-addon-xorg-2.17.8-3.fc44.x86_64 needs 96MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-plugin-bodhi-2.17.8-3.fc44.x86_64 needs 97MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-abrt-addon-2.17.8-3.fc44.noarch needs 97MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libipt-2.1.2-4.fc44.x86_64 needs 97MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gdb-headless-17.1-4.fc44.x86_64 needs 115MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-addon-ccpp-2.17.8-3.fc44.x86_64 needs 116MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-tui-2.17.8-3.fc44.noarch needs 116MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libdaemon-0.14-33.fc44.x86_64 needs 116MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package avahi-0.9~rc2-8.fc44.x86_64 needs 118MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cups-ipptool-1:2.4.18-1.fc44.x86_64 needs 123MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package liblerc-4.0.0-10.fc44.x86_64 needs 124MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libtiff-4.7.1-2.fc44.x86_64 needs 125MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package poppler-26.01.0-3.fc44.x86_64 needs 129MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package poppler-cpp-26.01.0-3.fc44.x86_64 needs 129MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libsane-airscan-0.99.36-2.fc44.x86_64 needs 129MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sane-airscan-0.99.36-2.fc44.x86_64 needs 129MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sane-backends-1.4.0-6.fc44.x86_64 needs 134MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spandsp-0.0.6-22.fc44.x86_64 needs 135MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package leptonica-1.87.0-3.fc44.x86_64 needs 138MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tesseract-libs-5.5.2-1.fc44.x86_64 needs 141MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-pillow-12.2.0-1.fc44.x86_64 needs 147MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package httpd-filesystem-2.4.66-4.fc44.noarch needs 147MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package numad-0.5-50.20251104git.fc44.x86_64 needs 147MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package lzop-1.04-18.fc44.x86_64 needs 148MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mdevctl-1.4.0-3.fc44.x86_64 needs 150MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libwsman1-2.8.1-14.fc44.x86_64 needs 151MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libssh2-1.11.1-5.fc44.x86_64 needs 151MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-libs-12.0.0-3.fc44.x86_64 needs 184MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-common-12.0.0-3.fc44.x86_64 needs 185MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-core-12.0.0-3.fc44.x86_64 needs 186MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-lock-12.0.0-3.fc44.x86_64 needs 186MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-log-12.0.0-3.fc44.x86_64 needs 186MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-plugin-lockd-12.0.0-3.fc44.x86_64 needs 186MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-proxy-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-disk-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-iscsi-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-iscsi-direct-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-logical-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-mpath-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-rbd-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-scsi-12.0.0-3.fc44.x86_64 needs 187MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-interface-12.0.0-3.fc44.x86_64 needs 188MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-nodedev-12.0.0-3.fc44.x86_64 needs 189MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-nwfilter-12.0.0-3.fc44.x86_64 needs 190MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-secret-12.0.0-3.fc44.x86_64 needs 191MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-client-12.0.0-3.fc44.x86_64 needs 192MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-ssh-proxy-12.0.0-3.fc44.x86_64 needs 192MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-glib-5.0.0-8.fc44.x86_64 needs 193MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-gobject-5.0.0-8.fc44.x86_64 needs 193MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package highway-1.3.0-2.fc44.x86_64 needs 199MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libjxl-1:0.11.1-8.fc44.x86_64 needs 203MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libopenjph-0.25.3-3.fc44.x86_64 needs 204MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libheif-1.21.2-1.fc44.x86_64 needs 206MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package emacs-filesystem-1:30.2-2.fc44.x86_64 needs 206MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package desktop-file-utils-0.28-5.fc44.x86_64 needs 206MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-utils-1.2.1-5.fc44.noarch needs 206MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sound-theme-freedesktop-0.8-31.fc44.noarch needs 207MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libudfread-1.2.0-3.fc44.x86_64 needs 207MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libbluray-1.4.0-3.fc44.x86_64 needs 208MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libfyaml-0.8-9.fc44.x86_64 needs 208MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package appstream-1.1.0-3.fc44.x86_64 needs 213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libdnf5-plugin-appstream-5.4.1.0-1.fc44.x86_64 needs 213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package PackageKit-1.3.4-3.fc44.x86_64 needs 217MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libdatrie-0.2.14-2.fc44.x86_64 needs 217MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libthai-0.1.30-2.fc44.x86_64 needs 218MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package kexec-tools-2.0.32-3.fc44.x86_64 needs 219MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-addon-vmcore-2.17.8-3.fc44.x86_64 needs 219MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package m17n-db-1.8.10-3.fc44.noarch needs 223MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package m17n-lib-1.8.6-3.fc44.x86_64 needs 223MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package kyotocabinet-libs-1.2.80-9.fc44.x86_64 needs 224MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libpinyin-2.11.91-2.fc44.x86_64 needs 225MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libpinyin-data-2.11.91-2.fc44.x86_64 needs 264MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package hplip-common-3.25.8-2.fc44.x86_64 needs 266MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package hplip-libs-3.25.8-2.fc44.x86_64 needs 266MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package uriparser-1.0.0-2.fc44.x86_64 needs 266MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libwinpr-2:3.24.2-1.fc44.x86_64 needs 268MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libusal-1.1.11-63.fc44.x86_64 needs 268MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package genisoimage-1.1.11-63.fc44.x86_64 needs 270MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adwaita-icon-theme-legacy-46.2-7.fc44.noarch needs 279MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adwaita-cursor-theme-50.0-1.fc44.noarch needs 292MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adwaita-icon-theme-50.0-1.fc44.noarch needs 296MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package lockdev-1.0.4-0.54.20111007git.fc44.x86_64 needs 296MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wsdd-0.8-6.fc44.noarch needs 296MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-1.60.0-1.fc44.x86_64 needs 298MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package stoken-libs-0.93-2.fc44.x86_64 needs 298MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package openconnect-9.12-10.fc44.x86_64 needs 302MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-openconnect-1.2.10-11.fc44.x86_64 needs 306MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-pam-2.0.2-18.fc44.noarch needs 306MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libX11-common-1.8.13-1.fc44.noarch needs 308MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libX11-1.8.13-1.fc44.x86_64 needs 309MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXext-1.3.6-5.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXfixes-6.0.1-7.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXi-1.8.2-4.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXinerama-1.1.5-10.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXdamage-1.1.6-7.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXrender-0.9.12-4.fc44.x86_64 needs 310MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cairo-1.18.4-6.fc44.x86_64 needs 312MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cairo-gobject-1.18.4-6.fc44.x86_64 needs 312MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXrandr-1.5.4-7.fc44.x86_64 needs 312MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gjs-1.88.0-1.fc44.x86_64 needs 314MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXtst-1.2.5-4.fc44.x86_64 needs 314MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package brlapi-0.8.7-8.fc44.x86_64 needs 315MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cairomm-1.14.5-15.fc44.x86_64 needs 315MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package poppler-glib-26.01.0-3.fc44.x86_64 needs 316MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package poppler-utils-26.01.0-3.fc44.x86_64 needs 317MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXcursor-1.2.3-4.fc44.x86_64 needs 317MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXcomposite-0.4.6-7.fc44.x86_64 needs 317MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libxkbfile-1.1.3-5.fc44.x86_64 needs 318MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXt-1.3.1-4.fc44.x86_64 needs 318MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libgs-10.06.0-2.fc44.x86_64 needs 346MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ghostscript-10.06.0-2.fc44.x86_64 needs 346MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ghostscript-tools-fontutils-10.06.0-2.fc44.noarch needs 346MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ghostscript-tools-printing-10.06.0-2.fc44.noarch needs 346MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXmu-1.2.1-5.fc44.x86_64 needs 346MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cairomm1.16-1.18.0-16.fc44.x86_64 needs 347MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libgxps-0.3.2-12.fc44.x86_64 needs 347MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-cairo-1.28.0-5.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-gobject-3.56.2-1.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXv-1.0.13-4.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mesa-libEGL-26.0.5-3.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libglvnd-egl-1:1.7.0-9.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libglvnd-gles-1:1.7.0-9.fc44.x86_64 needs 348MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcamera-0.7.0-1.fc44.x86_64 needs 351MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package startup-notification-0.12-33.fc44.x86_64 needs 351MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xhost-1.0.9-11.fc44.x86_64 needs 351MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xorg-x11-xauth-1:1.1.5-1.fc44.x86_64 needs 351MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xrdb-1.2.2-7.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libspectre-0.2.12-11.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package setxkbmap-1.3.4-7.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xkbcomp-1.5.0-2.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package liblouisutdml-utils-2.12.0-8.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-char-baum-2:10.2.2-1.fc44.x86_64 needs 352MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-brlapi-0.8.7-8.fc44.x86_64 needs 353MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXft-2.3.8-10.fc44.x86_64 needs 353MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pango-1.57.1-1.fc44.x86_64 needs 354MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package librsvg2-2.62.0-1.fc44.x86_64 needs 359MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glycin-loaders-2.1.1-1.fc44.x86_64 needs 374MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glycin-libs-2.1.1-1.fc44.x86_64 needs 379MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gdk-pixbuf2-2.44.4-2.fc44.x86_64 needs 382MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libnotify-0.8.8-1.fc44.x86_64 needs 382MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvnc-1.5.0-4.fc44.x86_64 needs 382MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package geoclue2-2.8.0-2.fc44.x86_64 needs 383MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtk-update-icon-cache-3.24.52-1.fc44.x86_64 needs 383MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package flatpak-1.17.6-1.fc44.x86_64 needs 392MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libgsf-1.14.56-1.fc44.x86_64 needs 393MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ImageMagick-libs-1:7.1.2.13-2.fc44.x86_64 needs 404MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ImageMagick-1:7.1.2.13-2.fc44.x86_64 needs 405MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libmediaart-1.9.7-4.fc44.x86_64 needs 405MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pangomm2.48-2.56.1-3.fc44.x86_64 needs 405MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pangomm-2.46.4-5.fc44.x86_64 needs 405MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package plymouth-plugin-label-24.004.60-24.fc44.x86_64 needs 406MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package plymouth-plugin-two-step-24.004.60-24.fc44.x86_64 needs 406MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package plymouth-theme-spinner-24.004.60-24.fc44.x86_64 needs 406MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXxf86vm-1.1.6-4.fc44.x86_64 needs 406MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mesa-libGL-26.0.5-3.fc44.x86_64 needs 407MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libglvnd-glx-1:1.7.0-9.fc44.x86_64 needs 407MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-base-1.28.2-1.fc44.x86_64 needs 416MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libva-2.23.0-3.fc44.x86_64 needs 416MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-opengl-2:10.2.2-1.fc44.x86_64 needs 416MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spice-server-0.16.0-2.fc43.x86_64 needs 418MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-spice-core-2:10.2.2-1.fc44.x86_64 needs 418MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-bad-free-libs-1.28.2-1.fc44.x86_64 needs 422MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtk4-4.22.4-1.fc44.x86_64 needs 452MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libadwaita-1.9.0-1.fc44.x86_64 needs 456MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-online-accounts-libs-3.58.1-1.fc44.x86_64 needs 457MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libnma-gtk4-1.10.6-11.fc44.x86_64 needs 457MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libportal-gtk4-0.9.1-4.fc44.x86_64 needs 457MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtksourceview5-5.20.0-1.fc44.x86_64 needs 462MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tecla-50.0-1.fc44.x86_64 needs 463MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glycin-gtk4-libs-2.1.1-1.fc44.x86_64 needs 463MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugin-gtk4-0.15.0-1.fc44.x86_64 needs 464MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spice-glib-0.42-8.fc44.x86_64 needs 465MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libspelling-0.4.10-1.fc44.x86_64 needs 466MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package papers-libs-49.6-1.fc44.x86_64 needs 467MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-char-spice-2:10.2.2-1.fc44.x86_64 needs 467MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package virglrenderer-1.3.0-1.fc44.x86_64 needs 469MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-device-display-virtio-gpu-gl-2:10.2.2-1.fc44.x86_64 needs 469MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-device-display-virtio-gpu-pci-gl-2:10.2.2-1.fc44.x86_64 needs 469MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-device-display-vhost-user-gpu-2:10.2.2-1.fc44.x86_64 needs 470MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-spice-app-2:10.2.2-1.fc44.x86_64 needs 470MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package papers-previewer-49.6-1.fc44.x86_64 needs 470MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package papers-thumbnailer-49.6-1.fc44.x86_64 needs 472MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package msgraph-0.3.4-5.fc44.x86_64 needs 472MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-goa-1.60.0-1.fc44.x86_64 needs 472MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-online-accounts-3.58.1-1.fc44.x86_64 needs 474MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package malcontent-ui-libs-0.14.0-1.fc44.x86_64 needs 474MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtkmm4.0-4.22.0-1.fc44.x86_64 needs 480MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package colord-gtk4-0.3.1-6.fc44.x86_64 needs 480MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gcr-4.4.0.1-7.fc44.x86_64 needs 480MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libshumate-1.6.1-1.fc44.x86_64 needs 481MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-audio-spice-2:10.2.2-1.fc44.x86_64 needs 481MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-device-display-qxl-2:10.2.2-1.fc44.x86_64 needs 482MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-egl-headless-2:10.2.2-1.fc44.x86_64 needs 482MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gupnp-dlna-0.12.0-12.fc44.x86_64 needs 482MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugin-openh264-1.28.2-1.fc44.x86_64 needs 482MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gst-editing-services-1.28.2-1.fc44.x86_64 needs 484MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glx-utils-9.0.0-11.fc44.x86_64 needs 484MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package freeglut-3.8.0-2.fc44.x86_64 needs 485MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcaca-0.99-0.82.beta20.fc44.x86_64 needs 486MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvdpau-1.5-11.fc44.x86_64 needs 486MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libavutil-free-8.0.1-6.fc44.x86_64 needs 487MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libswresample-free-8.0.1-6.fc44.x86_64 needs 487MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libavcodec-free-8.0.1-6.fc44.x86_64 needs 498MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libswscale-free-8.0.1-6.fc44.x86_64 needs 499MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libchromaprint-1.6.0-4.fc44.x86_64 needs 499MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libavformat-free-8.0.1-6.fc44.x86_64 needs 502MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package localsearch-3.11.1-1.fc44.x86_64 needs 507MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXres-1.2.2-7.fc44.x86_64 needs 507MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xmodmap-1.0.11-10.fc44.x86_64 needs 507MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xorg-x11-xinit-1.4.3-4.fc44.x86_64 needs 507MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libXpm-3.5.17-7.fc44.x86_64 needs 507MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gd-2.3.3-21.fc44.x86_64 needs 508MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libgphoto2-2.5.33-2.fc44.x86_64 needs 515MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xprop-1.2.8-5.fc44.x86_64 needs 515MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package at-spi2-core-2.60.3-1.fc44.x86_64 needs 517MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package atk-2.60.3-1.fc44.x86_64 needs 517MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package atkmm-2.28.4-7.fc44.x86_64 needs 518MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package at-spi2-atk-2.60.3-1.fc44.x86_64 needs 518MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtk3-3.24.52-1.fc44.x86_64 needs 543MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libnma-1.10.6-11.fc44.x86_64 needs 543MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libhandy-1.8.3-10.fc44.x86_64 needs 545MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gcr3-3.41.1-12.fc44.x86_64 needs 547MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-keyring-50.0-1.fc44.x86_64 needs 551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spice-gtk3-0.42-8.fc44.x86_64 needs 552MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-autoar-0.4.5-4.fc44.x86_64 needs 552MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libdecor-0.2.5-2.fc44.x86_64 needs 552MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package SDL3-3.4.4-1.fc44.x86_64 needs 556MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sdl2-compat-2.32.64-1.fc44.x86_64 needs 556MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-audio-sdl-2:10.2.2-1.fc44.x86_64 needs 556MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package SDL2_image-2.8.8-4.fc44.x86_64 needs 556MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-sdl-2:10.2.2-1.fc44.x86_64 needs 557MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tslib-1.24-2.fc44.x86_64 needs 557MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qtbase-gui-6.10.3-1.fc44.x86_64 needs 587MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qtsvg-6.10.3-1.fc44.x86_64 needs 588MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qtdeclarative-6.10.3-1.fc44.x86_64 needs 652MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qtwayland-6.10.3-1.fc44.x86_64 needs 656MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package kf6-kimageformats-6.25.0-2.fc44.x86_64 needs 660MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package f44-backgrounds-base-44.0.0-1.fc44.noarch needs 669MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package f44-backgrounds-gnome-44.0.0-1.fc44.noarch needs 669MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xorg-x11-server-Xwayland-24.1.11-1.fc44.x86_64 needs 672MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-keyring-pam-50.0-1.fc44.x86_64 needs 672MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-ssh-1.4.4-1.fc44.x86_64 needs 673MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libportal-gtk3-0.9.1-4.fc44.x86_64 needs 673MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtk-vnc2-1.5.0-4.fc44.x86_64 needs 673MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtkmm3.0-3.24.10-3.fc44.x86_64 needs 678MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package system-config-printer-libs-1.5.18-17.fc44.noarch needs 685MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-desktop3-44.5-1.fc44.x86_64 needs 689MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-desktop4-44.5-1.fc44.x86_64 needs 690MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-session-50.0-1.fc44.x86_64 needs 692MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nautilus-50.1-1.fc44.x86_64 needs 707MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gspell-1.14.3-1.fc44.x86_64 needs 708MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evince-libs-48.1-2.fc44.x86_64 needs 709MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-bad-free-1.28.2-1.fc44.x86_64 needs 721MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package kasumi-unicode-2.5-50.fc44.x86_64 needs 721MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-gtk3-1.5.34-1.fc44.x86_64 needs 721MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-1.5.34-1.fc44.x86_64 needs 879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-ibus-1.5.34-1.fc44.x86_64 needs 879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-anthy-1.5.18-1.fc44.x86_64 needs 888MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-anthy-python-1.5.18-1.fc44.noarch needs 889MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gtksourceview4-4.8.4-11.fc44.x86_64 needs 895MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-pyatspi-2.58.2-1.fc44.noarch needs 895MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libasyncns-0.8-32.fc44.x86_64 needs 895MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pulseaudio-libs-17.0-9.fc44.x86_64 needs 899MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-libs-1.6.4-1.fc44.x86_64 needs 911MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcanberra-0.30-39.fc44.x86_64 needs 911MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-jack-audio-connection-kit-libs-1.6.4-1.fc44.x86_64 needs 912MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-jack-audio-connection-kit-1.6.4-1.fc44.x86_64 needs 912MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-good-1.28.2-1.fc44.x86_64 needs 921MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pulseaudio-libs-glib2-17.0-9.fc44.x86_64 needs 921MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package flite-2.2-13.fc44.x86_64 needs 944MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package webkitgtk6.0-2.52.3-1.fc44.x86_64 needs 1040MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libavfilter-free-8.0.1-6.fc44.x86_64 needs 1044MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package webkit2gtk4.1-2.52.3-1.fc44.x86_64 needs 1140MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcanberra-gtk3-0.30-39.fc44.x86_64 needs 1140MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evolution-data-server-3.60.1-1.fc44.x86_64 needs 1150MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evolution-data-server-langpacks-3.60.1-1.fc44.noarch needs 1160MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gsound-1.0.3-12.fc44.x86_64 needs 1160MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-bluetooth-libs-1:47.2-1.fc44.x86_64 needs 1162MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-desktop-portal-1.21.1-1.fc44.x86_64 needs 1164MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-gstreamer-1.6.4-1.fc44.x86_64 needs 1164MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package freerdp-libs-2:3.24.2-1.fc44.x86_64 needs 1168MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-desktop-portal-gtk-1.15.3-3.fc44.x86_64 needs 1169MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-desktop-portal-gnome-50.0-1.fc44.x86_64 needs 1170MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package folks-1:0.15.12-1.fc44.x86_64 needs 1174MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evolution-ews-core-3.60.1-1.fc44.x86_64 needs 1176MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evolution-ews-langpacks-3.60.1-1.fc44.noarch needs 1178MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libavdevice-free-8.0.1-6.fc44.x86_64 needs 1178MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package yelp-libs-2:49.0-2.fc44.x86_64 needs 1178MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package epiphany-runtime-1:50.3-1.fc44.x86_64 needs 1186MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-software-50.0-2.fc44.x86_64 needs 1201MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-good-gtk-1.28.2-1.fc44.x86_64 needs 1201MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-core-1:26.2.2.2-2.fc44.x86_64 needs 1513MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-langpack-en-1:26.2.2.2-2.fc44.x86_64 needs 1514MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-gtk3-1:26.2.2.2-2.fc44.x86_64 needs 1516MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-pyuno-1:26.2.2.2-2.fc44.x86_64 needs 1519MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-pdfimport-1:26.2.2.2-2.fc44.x86_64 needs 1519MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-writer-1:26.2.2.2-2.fc44.x86_64 needs 1533MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-graphicfilter-1:26.2.2.2-2.fc44.x86_64 needs 1534MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-calc-1:26.2.2.2-2.fc44.x86_64 needs 1563MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-xsltfilter-1:26.2.2.2-2.fc44.x86_64 needs 1568MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-ogltrans-1:26.2.2.2-2.fc44.x86_64 needs 1568MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-impress-1:26.2.2.2-2.fc44.x86_64 needs 1569MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-filters-1:26.2.2.2-2.fc44.x86_64 needs 1569MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-audio-jack-2:10.2.2-1.fc44.x86_64 needs 1569MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package portaudio-19.7.0-3.fc44.x86_64 needs 1569MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package firefox-150.0-1.fc44.x86_64 needs 1853MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-audio-pipewire-2:10.2.2-1.fc44.x86_64 needs 1853MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-pulseaudio-1.6.4-1.fc44.x86_64 needs 1854MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wireplumber-libs-0.5.14-1.fc44.x86_64 needs 1856MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wireplumber-0.5.14-1.fc44.x86_64 needs 1857MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-1.6.4-1.fc44.x86_64 needs 1857MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libao-1.2.0-31.fc44.x86_64 needs 1858MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvncpulse-1.5.0-4.fc44.x86_64 needs 1858MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pcaudiolib-1.1-19.fc44.x86_64 needs 1858MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package espeak-ng-1.52.0-3.fc44.x86_64 needs 1885MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package speech-dispatcher-0.12.1-6.fc44.x86_64 needs 1917MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package speech-dispatcher-espeak-ng-0.12.1-6.fc44.x86_64 needs 1917MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-audio-pa-2:10.2.2-1.fc44.x86_64 needs 1917MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pulseaudio-utils-17.0-9.fc44.x86_64 needs 1917MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-nftables-1:1.1.6-2.fc44.noarch needs 1917MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-firewall-2.4.0-2.fc44.noarch needs 1921MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package quota-nls-1:4.11-2.fc44.noarch needs 1921MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package quota-1:4.11-2.fc44.x86_64 needs 1922MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libhangul-0.2.0-3.fc44.x86_64 needs 1929MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libchewing-0.11.0-2.fc44.x86_64 needs 1937MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package color-filesystem-1-38.fc44.noarch needs 1937MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package colord-1.4.8-4.fc44.x86_64 needs 1941MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcupsfilters-1:2.1.1-7.fc44.x86_64 needs 1942MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-settings-daemon-50.1-1.fc44.x86_64 needs 1950MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-control-center-50.1-1.fc44.x86_64 needs 1976MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mutter-50.1-1.fc44.x86_64 needs 1986MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libmtp-1.1.22-3.fc44.x86_64 needs 1986MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-user-dirs-0.18-11.fc43.x86_64 needs 1987MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdg-user-dirs-gtk-0.16-2.fc44.x86_64 needs 1987MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-50.1-2.fc44.x86_64 needs 2003MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-session-wayland-session-50.0-1.fc44.x86_64 needs 2003MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gdm-1:50.0-1.fc44.x86_64 needs 2009MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-common-50.1-1.fc44.noarch needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-apps-menu-50.1-1.fc44.noarch needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-launch-new-instance-50.1-1.fc44.noarch needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-places-menu-50.1-1.fc44.noarch needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-window-list-50.1-1.fc44.noarch needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package editorconfig-libs-0.12.10-1.fc44.x86_64 needs 2010MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package yelp-xsl-49.0-2.fc44.noarch needs 2012MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pcre2-utf32-10.47-1.fc44.1.x86_64 needs 2013MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package firewalld-filesystem-2.4.0-2.fc44.noarch needs 2013MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mailcap-2.1.54-10.fc44.noarch needs 2013MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package httpd-core-2.4.66-4.fc44.x86_64 needs 2020MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package httpd-2.4.66-4.fc44.x86_64 needs 2020MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mod_dnssd-0.6-36.fc44.x86_64 needs 2020MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package attr-2.5.2-8.fc44.x86_64 needs 2020MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glusterfs-fuse-11.2-5.fc44.x86_64 needs 2021MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-gluster-12.0.0-3.fc44.x86_64 needs 2021MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-storage-12.0.0-3.fc44.x86_64 needs 2021MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package acl-2.3.2-6.fc44.x86_64 needs 2022MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libppd-1:2.1.1-3.fc44.x86_64 needs 2022MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cups-filters-1:2.0.1-14.fc44.x86_64 needs 2024MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cups-1:2.4.18-1.fc44.x86_64 needs 2036MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bzip2-1.0.8-23.fc44.x86_64 needs 2036MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-qemu-12.0.0-3.fc44.x86_64 needs 2039MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wpa_supplicant-1:2.11-9.fc44.x86_64 needs 2046MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package dnsmasq-2.92-4.fc44.x86_64 needs 2047MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-driver-network-12.0.0-3.fc44.x86_64 needs 2048MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-config-network-12.0.0-3.fc44.x86_64 needs 2048MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package vte-profile-0.84.0-1.fc44.x86_64 needs 2048MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package vte291-0.84.0-1.fc44.x86_64 needs 2050MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package vte291-gtk4-0.84.0-1.fc44.x86_64 needs 2051MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-ui-gtk-2:10.2.2-1.fc44.x86_64 needs 2051MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-system-x86-2:10.2.2-1.fc44.x86_64 needs 2051MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-kvm-2:10.2.2-1.fc44.x86_64 needs 2051MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-kvm-12.0.0-3.fc44.x86_64 needs 2051MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-boxes-50.0-1.fc44.x86_64 needs 2061MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ptyxis-50.1-1.fc44.x86_64 needs 2063MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-wifi-1:1.56.0-1.fc44.x86_64 needs 2063MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bluez-cups-5.86-4.fc44.x86_64 needs 2064MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gutenprint-cups-5.3.5-7.fc44.x86_64 needs 2065MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package hplip-3.25.8-2.fc44.x86_64 needs 2102MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package braille-printer-app-1:2.0~b0^386eea385f-11.fc44.x86_64 needs 2102MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cups-browsed-1:2.1.1-7.fc44.x86_64 needs 2102MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cups-filters-driverless-1:2.0.1-14.fc44.x86_64 needs 2103MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-user-share-48.2-1.fc44.x86_64 needs 2104MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mod_http2-2.0.37-2.fc44.x86_64 needs 2104MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mod_lua-2.4.66-4.fc44.x86_64 needs 2104MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package firewalld-2.4.0-2.fc44.noarch needs 2109MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package brltty-6.8-8.fc44.x86_64 needs 2120MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package yelp-2:49.0-2.fc44.x86_64 needs 2123MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-text-editor-50.0-1.fc44.x86_64 needs 2127MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-classic-session-50.1-1.fc44.noarch needs 2127MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-initial-setup-50.0-3.fc44.x86_64 needs 2129MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-browser-connector-42.1-14.fc44.x86_64 needs 2130MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-shell-extension-background-logo-50~beta-2.fc44.noarch needs 2130MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-mtp-1.60.0-1.fc44.x86_64 needs 2130MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-chewing-2.1.7-2.fc44.x86_64 needs 2131MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-hangul-1.5.5-12.fc44.x86_64 needs 2131MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nfs-utils-1:2.8.7-1.fc44.x86_64 needs 2132MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package speech-dispatcher-utils-0.12.1-6.fc44.x86_64 needs 2132MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package orca-50.1.2-1.fc44.noarch needs 2161MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-connections-50.0-1.fc44.x86_64 needs 2163MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-remote-desktop-50.1-1.fc44.x86_64 needs 2165MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-utils-1.6.4-1.fc44.x86_64 needs 2167MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-bluetooth-1:47.2-1.fc44.x86_64 needs 2167MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package firefox-langpacks-150.0-1.fc44.x86_64 needs 2213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-pyaudio-0.2.13-11.fc44.x86_64 needs 2213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package unoconv-0.9.0-18.fc44.noarch needs 2213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-emailmerge-1:26.2.2.2-2.fc44.x86_64 needs 2213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-gtk4-1:26.2.2.2-2.fc44.x86_64 needs 2215MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libreoffice-help-en-1:26.2.2.2-2.fc44.x86_64 needs 2246MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-software-fedora-langpacks-50.0-2.fc44.x86_64 needs 2246MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ffmpeg-free-8.0.1-6.fc44.x86_64 needs 2249MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-contacts-50.0-1.fc44.x86_64 needs 2252MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-calendar-50.0-1.fc44.x86_64 needs 2255MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-disk-utility-46.1-4.fc44.x86_64 needs 2262MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-openconnect-gnome-1.2.10-11.fc44.x86_64 needs 2263MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugin-libav-1.28.2-1.fc44.x86_64 needs 2263MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gst-thumbnailers-1.0.0-1.fc44.x86_64 needs 2265MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-good-qt6-1.28.2-1.fc44.x86_64 needs 2265MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package uresourced-0.5.4-5.fc44.x86_64 needs 2265MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-config-raop-1.6.4-1.fc44.x86_64 needs 2265MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-alsa-1.6.4-1.fc44.x86_64 needs 2266MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pipewire-plugin-libcamera-1.6.4-1.fc44.x86_64 needs 2266MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sushi-50~rc.1-1.fc44.x86_64 needs 2267MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-libpinyin-1.16.5-3.fc44.x86_64 needs 2270MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-m17n-1.4.38-1.fc44.x86_64 needs 2270MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-typing-booster-2.30.7-1.fc44.noarch needs 2280MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-setup-1.5.34-1.fc44.noarch needs 2281MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package snapshot-50.0-1.fc44.x86_64 needs 2285MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package evince-djvu-48.1-2.fc44.x86_64 needs 2286MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package papers-nautilus-49.6-1.fc44.x86_64 needs 2286MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-clocks-50.0-1.fc44.x86_64 needs 2291MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-characters-50.0-1.fc44.x86_64 needs 2294MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package system-config-printer-udev-1.5.18-17.fc44.x86_64 needs 2294MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package open-vm-tools-desktop-13.0.10-2.fc44.x86_64 needs 2295MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-ssh-gnome-1.4.4-1.fc44.x86_64 needs 2295MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package desktop-backgrounds-gnome-44.0.0-2.fc44.noarch needs 2295MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qtwayland-adwaita-decoration-6.10.3-1.fc44.x86_64 needs 2295MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mediawriter-5.3.1-1.fc44.x86_64 needs 2299MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-vpnc-gnome-1:1.4.0-6.fc44.x86_64 needs 2299MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-openvpn-gnome-1:1.12.5-4.fc44.x86_64 needs 2299MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nm-connection-editor-1.36.0-7.fc44.x86_64 needs 2305MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-color-manager-3.36.2-3.fc44.x86_64 needs 2309MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libwnck3-43.3-2.fc44.x86_64 needs 2311MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-gphoto2-1.60.0-1.fc44.x86_64 needs 2312MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sane-backends-drivers-cameras-1.4.0-6.fc44.x86_64 needs 2312MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package rygel-45.1-1.fc44.x86_64 needs 2318MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package showtime-50.0-1.fc44.noarch needs 2319MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-maps-50.1-1.fc44.x86_64 needs 2326MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-system-monitor-50.0-1.fc44.x86_64 needs 2334MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package malcontent-control-0.14.0-1.fc44.x86_64 needs 2335MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package papers-49.6-1.fc44.x86_64 needs 2359MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-calculator-50.0-1.fc44.x86_64 needs 2372MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package simple-scan-49.1-2.fc44.x86_64 needs 2378MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-logs-50.0-1.fc44.x86_64 needs 2380MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package baobab-50.0-1.fc44.x86_64 needs 2384MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-font-viewer-50.0-1.fc44.x86_64 needs 2386MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-weather-50.0-1.fc44.noarch needs 2387MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package loupe-50.0-1.fc44.x86_64 needs 2397MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package decibels-49.6.1-1.fc44.noarch needs 2398MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-tour-50.0-1.fc44.x86_64 needs 2400MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ibus-gtk4-1.5.34-1.fc44.x86_64 needs 2400MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-mediasdk-23.2.2-11.fc44.x86_64 needs 2426MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-vpl-gpu-rt-26.1.0-1.fc44.x86_64 needs 2439MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugins-ugly-free-1.28.2-1.fc44.x86_64 needs 2439MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gstreamer1-plugin-dav1d-0.15.0-1.fc44.x86_64 needs 2440MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package xdriinfo-1.0.7-6.fc44.x86_64 needs 2440MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package plymouth-system-theme-24.004.60-24.fc44.x86_64 needs 2440MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-flathub-remote-1-12.fc44.noarch needs 2440MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-epub-thumbnailer-1.8-4.fc44.x86_64 needs 2440MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-backgrounds-50.0-1.fc44.noarch needs 2480MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-workstation-backgrounds-1.6-9.fc44.noarch needs 2486MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glycin-thumbnailer-2.1.1-1.fc44.x86_64 needs 2486MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package paps-0.8.0-15.fc44.x86_64 needs 2487MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package PackageKit-gtk3-module-1.3.4-3.fc44.x86_64 needs 2487MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcamera-ipa-0.7.0-1.fc44.x86_64 needs 2488MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spice-vdagent-0.23.0-2.fc44.x86_64 needs 2488MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-smb-1.60.0-1.fc44.x86_64 needs 2488MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-archive-1.60.0-1.fc44.x86_64 needs 2488MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-afc-1.60.0-1.fc44.x86_64 needs 2488MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-afp-1.60.0-1.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gvfs-fuse-1.60.0-1.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libsane-hpaio-3.25.8-2.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package abrt-cli-2.17.8-3.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package PackageKit-command-not-found-1.3.4-3.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pinfo-0.6.13-10.fc44.x86_64 needs 2489MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libvirt-daemon-12.0.0-3.fc44.x86_64 needs 2490MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sane-backends-drivers-scanners-1.4.0-6.fc44.x86_64 needs 2504MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package spice-webdavd-3.0-13.fc44.x86_64 needs 2504MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nss-mdns-0.15.1-28.fc44.x86_64 needs 2505MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package avahi-tools-0.9~rc2-8.fc44.x86_64 needs 2505MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qemu-kvm-core-2:10.2.2-1.fc44.x86_64 needs 2505MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package exiv2-0.28.6-3.fc44.x86_64 needs 2518MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libva-intel-media-driver-25.4.6-2.fc44.x86_64 needs 2529MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bind-utils-32:9.18.48-1.fc44.x86_64 needs 2530MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tuned-ppd-2.27.0-1.fc44.noarch needs 2530MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sos-4.11.1-1.fc44.noarch needs 2538MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mesa-vulkan-drivers-26.0.5-3.fc44.x86_64 needs 2706MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-perf-6.19.14-300.fc44.x86_64 needs 2718MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-workstation-repositories-38-9.fc44.x86_64 needs 2718MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-ppp-1:1.56.0-1.fc44.x86_64 needs 2718MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ipset-7.24-3.fc44.x86_64 needs 2718MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nbdkit-1.47.7-1.fc44.x86_64 needs 2719MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package jq-1.8.1-3.fc44.x86_64 needs 2719MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fwupd-plugin-flashrom-2.1.1-1.fc44.x86_64 needs 2719MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-httpx-0.28.1-11.fc44.noarch needs 2720MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-langtable-0.0.70-1.fc44.noarch needs 2722MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-boto3-1.42.84-1.fc44.noarch needs 2725MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package kernel-tools-6.19.14-300.fc44.x86_64 needs 2728MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pinentry-gnome3-1.3.2-3.fc44.x86_64 needs 2728MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-other-sans-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-other-serif-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-core-math-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-core-emoji-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-cjk-serif-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-cjk-sans-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-cjk-mono-4.3-1.fc44.noarch needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fwupd-plugin-modem-manager-2.1.1-1.fc44.x86_64 needs 2729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fwupd-plugin-uefi-capsule-data-2.1.1-1.fc44.x86_64 needs 2736MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package iwlwifi-mvm-firmware-20260410-1.fc44.noarch needs 2803MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package alsa-utils-1.2.15.2-3.fc44.x86_64 needs 2806MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-bluetooth-1:1.56.0-1.fc44.x86_64 needs 2806MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package hunspell-en-0.20260225-2.fc44.noarch needs 2807MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fprintd-pam-1.94.5-5.fc44.x86_64 needs 2807MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package langpacks-en-4.3-1.fc44.noarch needs 2807MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package samba-client-2:4.24.1-1.fc44.x86_64 needs 2810MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package hyperv-daemons-6.10-3.fc44.x86_64 needs 2810MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package opensc-0.27.1-2.fc44.x86_64 needs 2812MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wget2-wget-2.2.1-2.fc44.x86_64 needs 2812MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package passwdqc-2.0.3-9.fc44.x86_64 needs 2812MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cifs-utils-info-7.5-1.fc44.x86_64 needs 2812MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package iptstate-2.2.7-11.fc44.x86_64 needs 2812MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glib-networking-2.80.1-4.fc44.x86_64 needs 2813MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package realmd-0.17.1-19.fc44.x86_64 needs 2814MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package polkit-pkla-compat-0.1-32.fc44.x86_64 needs 2814MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tinysparql-3.11.1-1.fc44.x86_64 needs 2817MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nmap-ncat-4:7.92-8.fc44.x86_64 needs 2818MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tcpdump-14:4.99.6-3.fc44.x86_64 needs 2819MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qatlib-service-25.08.0-4.fc44.x86_64 needs 2820MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package toolbox-0.3-4.fc44.x86_64 needs 2832MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cpp-16.0.1-0.10.fc44.x86_64 needs 2877MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package passim-0.1.11-1.fc44.x86_64 needs 2877MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ntfs-3g-2:2022.10.3-12.fc44.x86_64 needs 2878MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ntfsprogs-2:2022.10.3-12.fc44.x86_64 needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ntfs-3g-system-compression-1.1-2.fc44.x86_64 needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package sssd-nfs-idmap-2.12.0-4.fc44.x86_64 needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ngtcp2-crypto-ossl-1.22.1-1.fc44.x86_64 needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-core-serif-4.3-1.fc44.noarch needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-core-mono-4.3-1.fc44.noarch needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-fonts-other-mono-4.3-1.fc44.noarch needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package apr-util-openssl-1.6.3-27.fc44.x86_64 needs 2879MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package PackageKit-gstreamer-plugin-1.3.4-3.fc44.x86_64 needs 2880MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package thermald-2.5.9-3.fc44.x86_64 needs 2880MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nbdkit-curl-plugin-1.47.7-1.fc44.x86_64 needs 2880MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nbdkit-ssh-plugin-1.47.7-1.fc44.x86_64 needs 2880MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-lpmd-0.0.9-3.fc44.x86_64 needs 2881MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package ipp-usb-0.9.31-2.fc44.x86_64 needs 2888MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package amd-gpu-firmware-20260410-1.fc44.noarch needs 2919MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tiwilink-firmware-20260410-1.fc44.noarch needs 2924MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package realtek-firmware-20260410-1.fc44.noarch needs 2931MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qcom-wwan-firmware-20260410-1.fc44.noarch needs 2932MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nxpwireless-firmware-20260410-1.fc44.noarch needs 2933MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nvidia-gpu-firmware-20260410-1.fc44.noarch needs 3041MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mt7xxx-firmware-20260410-1.fc44.noarch needs 3064MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package linux-firmware-20260410-1.fc44.noarch needs 3122MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libertas-firmware-20260410-1.fc44.noarch needs 3123MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package iwlwifi-dvm-firmware-20260410-1.fc44.noarch needs 3125MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package iwlegacy-firmware-20260410-1.fc44.noarch needs 3126MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-vsc-firmware-20260410-1.fc44.noarch needs 3134MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-gpu-firmware-20260410-1.fc44.noarch needs 3144MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package intel-audio-firmware-20260410-1.fc44.noarch needs 3148MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cirrus-audio-firmware-20260410-1.fc44.noarch needs 3158MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package brcmfmac-firmware-20260410-1.fc44.noarch needs 3169MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package atheros-firmware-20260410-1.fc44.noarch needs 3212MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package amd-ucode-firmware-20260410-1.fc44.noarch needs 3213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package wl-clipboard-2.2.1^git20251124.e808203-2.fc44.x86_64 needs 3213MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bolt-0.9.11-1.fc44.x86_64 needs 3214MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package perl-NDBM_File-0:1.18-524.fc44.x86_64 needs 3214MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adobe-source-code-pro-fonts-2.042.1.062.1.026-9.fc44.noarch needs 3215MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package google-noto-emoji-fonts-20250623-4.fc44.noarch needs 3216MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gdouros-symbola-fonts-10.24-19.fc44.noarch needs 3220MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adwaita-mono-fonts-50.0-1.fc44.noarch needs 3226MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package adwaita-sans-fonts-50.0-1.fc44.noarch needs 3228MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package julietaula-montserrat-fonts-1:9.000-4.fc44.noarch needs 3234MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package open-sans-fonts-1.10-25.fc44.noarch needs 3236MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package edk2-shell-x64-20260213-6.fc44.noarch needs 3238MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package udftools-2.3-13.fc44.x86_64 needs 3238MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package nilfs-utils-2.2.11-8.fc44.x86_64 needs 3239MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package f2fs-tools-1.16.0-10.fc44.x86_64 needs 3240MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-file-magic-5.46-9.fc44.noarch needs 3240MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package qt6-qttranslations-6.10.3-1.fc44.noarch needs 3257MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package python3-regex-2026.2.28-1.fc44.x86_64 needs 3259MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fwupd-efi-1.8-1.fc44.x86_64 needs 3260MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-chromium-config-gnome-3.0-9.fc44.noarch needs 3260MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package p11-kit-server-0.26.2-1.fc44.x86_64 needs 3260MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package skopeo-1:1.22.2-1.fc44.x86_64 needs 3286MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package libcap-ng-python3-0.9.2-1.fc44.x86_64 needs 3286MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package pam_afs_session-2.6-25.fc44.x86_64 needs 3286MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gamemode-1.8.2-4.fc44.x86_64 needs 3287MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cyrus-sasl-plain-2.1.28-35.fc44.x86_64 needs 3287MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package default-editor-8.7.1-2.fc44.noarch needs 3287MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package glibc-all-langpacks-2.43-2.fc44.x86_64 needs 3526MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-release-workstation-44-17.noarch needs 3526MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-chromium-config-3.0-9.fc44.noarch needs 3526MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package zip-3.0-45.fc44.x86_64 needs 3527MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package words-3.0-63.fc44.noarch needs 3532MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package tree-2.2.1-4.fc44.x86_64 needs 3532MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package traceroute-3:2.1.6-4.fc44.x86_64 needs 3532MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package time-1.9-28.fc44.x86_64 needs 3532MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package symlinks-1.7-14.fc44.x86_64 needs 3532MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package psacct-6.6.4-26.fc44.x86_64 needs 3533MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package plocate-1.1.24-1.fc44.x86_64 needs 3533MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package net-tools-2.0-0.77.20160912git.fc44.x86_64 needs 3534MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mcelog-3:175-14.fc44.x86_64 needs 3535MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package man-pages-6.13-3.fc44.noarch needs 3547MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package lsof-4.98.0-9.fc44.x86_64 needs 3548MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package lrzsz-0.12.20-76.fc44.x86_64 needs 3548MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package logrotate-3.22.0-5.fc44.x86_64 needs 3548MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package dos2unix-7.5.3-3.fc44.x86_64 needs 3549MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package deltarpm-3.6.5-8.fc44.x86_64 needs 3550MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package compsize-1.5^git20250123.d79eacf-15.fc44.x86_64 needs 3550MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bc-1.08.2-4.fc44.x86_64 needs 3550MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package whois-5.6.6-1.fc44.x86_64 needs 3550MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mtr-2:0.95-14.fc44.x86_64 needs 3551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fpaste-0.5.0.0-4.fc44.noarch needs 3551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package exfatprogs-1.3.2-1.fc44.x86_64 needs 3551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package dosfstools-4.2-18.fc44.x86_64 needs 3551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-config-connectivity-fedora-1:1.56.0-1.fc44.noarch needs 3551MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package cryptsetup-2.8.4-1.fc44.x86_64 needs 3553MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package bash-color-prompt-0.7.1-3.fc44.noarch needs 3553MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package microcode_ctl-2:2.1-74.fc44.x86_64 needs 3570MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package mpage-2.5.7-24.fc44.x86_64 needs 3570MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package b43-openfwwf-5.2-48.fc44.noarch needs 3570MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package b43-fwcutter-019-41.fc44.x86_64 needs 3571MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package alsa-sof-firmware-2025.12.2-1.fc44.noarch needs 3583MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package virtualbox-guest-additions-7.2.6-1.fc44.x86_64 needs 3587MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package gnome-user-docs-50.0-1.fc44.noarch needs 3729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package NetworkManager-adsl-1:1.56.0-1.fc44.x86_64 needs 3729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package fedora-bookmarks-28-36.fc44.noarch needs 3729MB more space on the / filesystem[0m
[1;31m==> proxmox-clone.fedora:   - installing package dracut-config-rescue-108-6.fc44.x86_64 needs 3729MB more space on the / filesystem[0m
[1;32m==> proxmox-clone.fedora: Provisioning step had errors: Running the cleanup provisioner, if present...[0m
[1;32m==> proxmox-clone.fedora: Stopping VM[0m
[1;32m==> proxmox-clone.fedora: Deleting VM[0m
[1;32m==> proxmox-clone.fedora: Deleted generated ISO from local:iso/packer3206625237.iso[0m
[1;31mBuild 'proxmox-clone.fedora' errored after 4 minutes 50 seconds: Script exited with non-zero exit status: 1. Allowed exit codes are: [0][0m

==> Wait completed after 4 minutes 50 seconds

==> Some builds didn't complete successfully and had errors:
--> proxmox-clone.fedora: Script exited with non-zero exit status: 1. Allowed exit codes are: [0]

==> Builds finished but no artifacts were created.
```

