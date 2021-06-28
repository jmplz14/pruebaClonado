# Setup SENAITE's host/VM baseline

First, install Debian buster. The easiest is to download the latest net installer
iso from Debian's website and use it as the boot device of the target machine/host/VM.
https://www.debian.org/distrib/

Follow the [Debian buster Installation Guide]( https://www.debian.org/releases/stable/installmanual) 
to install a minimal Debian server. Is strongly recommended to not install any 
of the Graphical Desktop environments of choice. The rendering of graphical 
interface consumes RAM and CPU; in a production environment this usually means 
a waste of space and resources. Also, remote access to this server will be done 
through an SSH connection, without graphical support.

Be sure to set the right settings within the installation process in the 
following screens:

* `Setup users and passwords`: Leave ``root`` user without password. System's
  initial user account will be ``senaite``.

* `Software selection`: Leave all options unchecked except "SSH server" and
  "standard system utilities". We want a "minimal" debian server.

After the base system installation, and in order to be able to use ansible
playbook to setup the instance, we need to setup the target host.

## Add senaite user to sudoers

Login to the host with a superuser (usually `root`) and add `senaite` user to 
the group of `sudoers`:

```sh
# nano /etc/sudoers.d/senaite
```

Add the following:

```sh
# User rules for SENAITE
senaite ALL=(ALL) NOPASSWD:ALL
```

## Configure static IP (for host-only interface)

This configuration of the static IP for a host-only interface is **only required
if the system is a Virtual Machine with vboxnet interface enabled**. You can 
skip this step otherwise.

Login to the host and configure the network interface properly:


```sh
$ ifconfig
$ sudo nano /etc/network/interfaces
```

Add the following configuration (it may differ depending on your interface id):

```
# The hostonly network interface
auto enp0s8
iface enp0s8 inet static
address 192.168.33.10
netmask 255.255.255.0
network 192.168.33.0
broadcast 192.168.33.255
```

Reboot for the changes to take effect:

```sh
$ sudo reboot -h now
```

## Add your public key to the authorized_keys

Add your public ssh to have remote access granted with `ssh-copy-id`. Run
the following command *from your local machine*:

```sh
$ ssh-copy-id -i ~/.ssh/user_id_rsa.pub senaite@192.168.33.10
```

Note we use here 192.168.33.10 as the host IP, which is the default value
we've set when the host is a VM with a vboxnet0 interface (host-only network)
enabled (see previous section). Change this IP accordingly.


# Deploy SENAITE application stack with Ansible

## Install Python

Login to the host with `senaite` user and install python, that is required by 
Ansible:

```sh
$ sudo apt install python
```    

## Install Ansible requirements

Now, *in your local machine*, go to `ansible` directory from the add-on and 
check all is in place and we are able to reach the target host with ansible:

```sh
$ ansible senaite-buster -i hosts.cfg -m setup
```

Note that the real IP of the host to where SENAITE will be installed is defined 
in the file `hosts.cfg`. You might need to change the default host IP used in
this recipe: 192.168.33.10.

If ansible is able to connect with the target host and everything is correct, a
long json should be displayed in the terminal after running the previous 
command. The output might look similar to:

```
[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details
[WARNING]: Platform linux on host senaite is using the discovered Python interpreter at
/usr/bin/python, but future installation of another Python interpreter could change this. See
https://docs.ansible.com/ansible/2.9/reference_appendices/interpreter_discovery.html for more
information.
senaite | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "10.0.2.15", 
            "192.168.33.10"
        ], 
        "ansible_all_ipv6_addresses": [
            "fe80::a00:27ff:fe1e:9eab", 
            "fe80::a00:27ff:fe01:b85b"
        ], 
        "ansible_apparmor": {
            "status": "enabled"
        }, 
        "ansible_architecture": "x86_64", 
        "ansible_bios_date": "12/01/2006", 
        "ansible_bios_version": "VirtualBox", 
        "ansible_cmdline": {
            "BOOT_IMAGE": "/boot/vmlinuz-4.19.0-14-amd64", 
            "quiet": true, 
            "ro": true, 
            "root": "UUID=786467f3-284a-4a31-9e68-0a62bf4d8eb7"
        },
        ...
    "changed": false
}
```

Install ansible dependencies afterwards. With the following command the system
will automatically download other ansible recipes and templates the current
playbook depends on.

```sh
$ ansible-galaxy install -f -r senaite.ansible-playbook/requirements.yml
```


## Run the Ansible playbook

Run the following command from your *local machine*:

```sh
$ ansible-playbook -vv -i hosts.cfg playbook.yml --vault-password-file vault.txt
```

Note `vault.txt` file is not in the repository, and it **never** should!.

The system will automatically install everything. The generates an SSH key
that will use for the automatic download of the latest source code of your
add-on. The following message will appear:

```
TASK [Wait for user to copy SSH public key] ******************************************************************************************
task path: /home/naralabs/dnota.lims/ansible/custom_pre.yml:35
[Wait for user to copy SSH public key]
Please, add the SSH public key above to the GitHub account ...:
```

Send the output to jp@naralabs.com. Naralabs will add this public SSH key to
the source code repos and notify back to you. Then, you can press intro and
resume the process.


## Create a new SENAITE site

After Ansible playbook is run and succeed, there is still one action that
must be done manually: the creation of the SENAITE site on top of the Plone 
framework. 

Login to the host through SSH and grab the Zope admin user credentials:

```sh
$ cat senaite/live.cfg | grep "user="
```

Create a new SENAITE site by using lynx:

```sh
$ lynx http://localhost:8081
```

You can move through the links with the cursor. Choose "Create a new SENAITE 
site" and press "Enter". Type then the username and password and submit. 

A "Site Installation" form is displayed. Change the "Default timezone" by a 
suitable value and leave the defaults on the rest of the settings ("Path 
identifier", "Title", "Language"). Move with the cursor to "Create SENAITE Site"
and press "Enter".

Once the SENAITE site is created, you should be able to access to SENAITE from
outside the host: http://192.168.33.10

Remember to change the IP in accordance and accept the self-signed certificate.
You can  login with the same credentials you've used previously for the site 
creation. Go to the add-ons installation page thereafter:
https://192.168.33.10/prefs_install_products_form

If not yet activated, press the button "Install" above "DNOTA.LIMS" to 
install the SENAITE extension.



## Troubleshooting

This section provides answers and solutions to some common answsers and pitfalls.

### Resume the installation process

If the process was not able to finish properly (e.g. because lack of
internet connectivity), you can always re-run the Ansible playbook to resume
the installation:

```sh
$ ansible-playbook -vv -i hosts.cfg playbook.yml --vault-password-file vault.txt
```

### Error setting locale

I get this message in the terminal:

    perl: warning: Setting locale failed.
    perl: warning: Please check that your locale settings:
            LANGUAGE = "en_US:en",
            LC_ALL = (unset),
            LC_MESSAGES = "en_US.UTF-8",
            LANG = "en_US.UTF-8"
        are supported and installed on your system.

See this link for a solution:
https://askubuntu.com/questions/162391/how-do-i-fix-my-locale-issue

Once resolved, rerun the Ansible playbook.

### Permission denied

Traceback:

```
zope.configuration.xmlconfig.ZopeXMLConfigurationError: File "/home/senaite/senaitelims/parts/client1/etc/site.zcml", line 16.2-16.23
    ZopeXMLConfigurationError: File "/home/senaite/buildout-cache/eggs/Products.CMFPlone-4.3.17-py2.7.egg/Products/CMFPlone/configure.zcml", line 98.4-102.10
    ZopeXMLConfigurationError: File "/home/senaite/senaitelims/src/senaite.core/bika/lims/configure.zcml", line 15.0-15.35
    ZopeXMLConfigurationError: File "/home/senaite/buildout-cache/eggs/Products.TextIndexNG3-3.4.14-py2.7.egg/Products/TextIndexNG3/configure.zcml", line 8.2-8.61
    IOError: [Errno 13] Permission denied: '/home/senaite/buildout-cache/eggs/zopyx.txng3.core-3.6.2-py2.7.egg/zopyx/txng3/core/configure.zcml'
```

Also see this issue: https://github.com/senaite/senaite.core/issues/861

Change the permissions on the `eggs` directory:

    chmod -R ug+rwX,o-rwx /home/senaite/buildout-cache/eggs

And rerun the Ansible playbook.
 

### Global Python interpreter is used

Add this to the end of `/home/senaite/.profile` to use the local python 
interpreter from the buildout.

    if [ -d "$HOME/python2.7" ] ; then
        echo "Using local Python installation"
        PATH="$HOME/python2.7/bin:$PATH"
    fi


### I see only a plain Plone website installed

You need to go to the add-ons control panel and install SENAITE Core/LIMS, e.g.
https://192.168.33.10/prefs_install_products_form


### Error: Wheels are not supported

Traceback:

```
handler in zc.buildout.easy_install.UNPACKERS
While:
  Installing.
  Loading extensions.
  Getting distribution for 'mr.developer==1.37'.
Error: Wheels are not supported
```

Setuptools `38.2.0` started supporting wheels which fails in `zc.buildout < 2.10.0`.
Please pin `zc.buildout` to version `2.10.0` in your buildout.cfg


### Error: Couldn't find a distribution for 'plone.api'

Please add this index section to your `buildout.cfg`:

```
[buildout]
...
index = https://pypi.python.org/simple/
...
```

### Permission denied (pip and setuptools)

Traceback:

```
An internal error occurred due to a bug in either zc.buildout or in a
recipe being used:
Traceback (most recent call last):
  File "/home/senaite/python2.7/local/lib/python2.7/site-packages/zc/buildout/buildout.py", line 2174, in main
    getattr(buildout, command)(args)
  File "/home/senaite/python2.7/local/lib/python2.7/site-packages/zc/buildout/buildout.py", line 716, in install
    self._compute_part_signatures(install_parts)
  File "/home/senaite/python2.7/local/lib/python2.7/site-packages/zc/buildout/buildout.py", line 962, in _compute_part_signatures
    sig = _dists_sig(pkg_resources.working_set.resolve([req]))
  File "/home/senaite/python2.7/local/lib/python2.7/site-packages/zc/buildout/buildout.py", line 1880, in _dists_sig
    result.append(dist.project_name + '-' + _dir_hash(location))
  File "/home/senaite/python2.7/local/lib/python2.7/site-packages/zc/buildout/buildout.py", line 1864, in _dir_hash
    f = open(path, 'rb')
IOError: [Errno 13] Permission denied: '/home/senaite/python2.7/lib/python2.7/site-packages/pip-19.3.1.dist-info/INSTALLER'
```

Change the permissions of the pip package contents:

```
sudo chmod -R +r /home/senaite/python2.7/lib/python2.7/site-packages
```

And rerun the Ansible playbook.
