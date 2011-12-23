from fabric.api import sudo, task, settings
from fabric.contrib import files
from fabtools import require


@task
def setup_lxc():
    """
    Prepares the controller environment to host lxc instances

    - installs packages
    - configures network bridging
    - creates a mountpoint
    """

    # packages
    require.deb.packages([
        'lxc', 'vlan', 'bridge-utils', 'python-software-properties', 'screen', 'debootstrap', 'fabric'
    ])

    # bridging
    conf = [
        '# LXC bridge',
        'auto br-lxc',
        'iface br-lxc inet static',
        '    address 192.168.254.1',
        '    netmask 255.255.255.0',
        '    post-up echo 1 > /proc/sys/net/ipv4/ip_forward',
        '    post-up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE',
        '    pre-down echo 0 > /proc/sys/net/ipv4/ip_forward',
        '    pre-down iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE',
        '    bridge_ports none',
        '    bridge_stp off',
    ]
    files.append(filename='/etc/network/interfaces', text=conf, use_sudo=True)
    sudo('ifup br-lxc')

    # mountpoint
    require.directory('/sys/fs/cgroup/lxc', use_sudo=True)
    conf = 'cgroup          /sys/fs/cgroup/lxc          cgroup          rw              0 0'
    files.append(filename='/etc/fstab', text=conf, use_sudo=True)
    with settings(warn_only=True):
        sudo('mount /sys/fs/cgroup/lxc')


