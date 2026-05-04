# DEBUG Error

Running  `./scripts/build_template.sh fedora` fails with the following output.

```shell
unused0: successfully imported disk 'local-lvm:vm-9001-disk-1'
ERROR: could not parse imported disk name from 'qm importdisk' output
ERROR: expected line matching: Successfully imported disk as 'unusedN:local-lvm:vm-9001-disk-X'
```
