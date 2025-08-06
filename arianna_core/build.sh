#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_VERSION="${KERNEL_VERSION:-6.6.4}"
ALPINE_VERSION="${ALPINE_VERSION:-3.19.0}"

# //: fetch kernel sources
mkdir -p "$ROOT_DIR/kernel"
cd "$ROOT_DIR/kernel"
if [ ! -f "linux-${KERNEL_VERSION}.tar.xz" ]; then
  curl -LO "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz"  # //: upstream kernel archive
fi

if [ ! -d "linux-${KERNEL_VERSION}" ]; then
  tar xf "linux-${KERNEL_VERSION}.tar.xz"  # //: unpack kernel tree
fi

cd "linux-${KERNEL_VERSION}"

# //: kernel configuration
if [ ! -f .config ]; then
  cp "$ROOT_DIR/kernel.config" .config  # //: baseline config with ext4, overlayfs, cgroups, namespaces
fi

# //: interactive customization when needed
# make menuconfig  # //: enable extra modules as project evolves

# //: build kernel and modules
make -j"$(nproc)" bzImage modules
make modules_install INSTALL_MOD_PATH="$ROOT_DIR/core"  # //: install to initramfs staging

# //: assemble initramfs with Alpine userland
cd "$ROOT_DIR"
if [ ! -f "alpine-minirootfs-${ALPINE_VERSION}-x86_64.tar.gz" ]; then
  curl -LO "https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION%.*}/releases/x86_64/alpine-minirootfs-${ALPINE_VERSION}-x86_64.tar.gz"  # //: minimal rootfs
fi
mkdir -p rootfs
if [ ! -f rootfs/.unpacked ]; then
  tar xf "alpine-minirootfs-${ALPINE_VERSION}-x86_64.tar.gz" -C rootfs
  touch rootfs/.unpacked
fi

# //: install runtime packages
apk --root rootfs --repositories-file /etc/apk/repositories add --no-cache \
  bash curl nano python3 py3-pip py3-virtualenv nodejs npm  # //: essential tools and runtimes

# //: include assistant and log dir
install -Dm755 cmd/assistant.py rootfs/usr/bin/assistant
mkdir -p rootfs/arianna_core/log

# //: create initramfs image
cd rootfs
find . | cpio -o -H newc | gzip -9 > "$ROOT_DIR/arianna.initramfs.gz"
cd "$ROOT_DIR"

# //: build final disk image
cat "kernel/linux-${KERNEL_VERSION}/arch/x86/boot/bzImage" "arianna.initramfs.gz" > "arianna-core.img"  # //: flat image for qemu

# //: quick smoke test with QEMU
qemu-system-x86_64 \
  -kernel "kernel/linux-${KERNEL_VERSION}/arch/x86/boot/bzImage" \
  -initrd "arianna.initramfs.gz" \
  -append "console=ttyS0" \
  -nographic \
  -no-reboot \
  -serial mon:stdio \
  -m 512M  # //: lightweight memory footprint

# //: verify language runtimes inside the VM (executed via expect or manual)
# python3 --version  # //: confirm Python 3.10+
# node --version     # //: confirm Node.js 18+
