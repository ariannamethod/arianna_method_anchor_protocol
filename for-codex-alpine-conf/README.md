# `alpine-conf`

This repo contains a set of utilities for making backup of config files and for setting up a new Alpine Linux computer.

# LBU

## Basic usage

  * To add a file or folder to be backed up, `lbu include /path/to/foo`
  * To remove a file from being backed up, `lbu exclude /path/to/foo`
  * To setup LBU options, edit `/etc/lbu/lbu.conf`
  * To create a package as specified in lbu.conf, `lbu commit`
  * To override destination of the backup package, `lbu package /path/to/bar.apkovl.tar.gz`

# Setup scripts

The main script is called `setup-alpine`, and it will perform basic system setup. Each script can be called independently, for example:

  * `setup-acf` sets up ACF web interface
  * `setup-ntp` sets up NTP service
  * etc.

For further information, please see <https://pkgs.alpinelinux.org/package/edge/main/x86_64/alpine-conf> or the Alpine Linux documentation wiki at <https://wiki.alpinelinux.org>.

## Minimal build exclusions

The default build omits several optional setup utilities that are not
required for a minimal bootable system:

- `setup-acf` – ACF web interface
- `setup-desktop` – desktop environment helpers
- `setup-devd` – device management with devd
- `setup-dns` – DNS resolver configuration
- `setup-mta` – mail transfer agent setup
- `setup-ntp` – network time synchronisation
- `setup-proxy` – proxy configuration
- `setup-sshd` – SSH server
- `setup-wayland-base` – Wayland graphics stack
- `setup-xen-dom0` – Xen Dom0 support
- `setup-xorg-base` – Xorg graphics stack

These scripts remain in the source tree but are excluded from the build by
default.  Maintainers can reintroduce them by appending
`OPTIONAL_SBIN_FILES` to `SBIN_FILES` in the `Makefile`.
