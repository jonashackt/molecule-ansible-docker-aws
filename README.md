# molecule-ansible-vagrant
Example project showing how to test Ansible roles with Molecule and Vagrant

### TDD for Infrastructure code with Molecule!

[Molecule](https://molecule.readthedocs.io/en/latest/#) seems to be a pretty neat TDD framework for testing Infrastructur-as-Code using Ansible. Molecule executes the following steps:

![tdd-for-iac](https://yuml.me/diagram/scruffy/class/[Given:%20Spin%20up%20Infrastructure%20with%20Vagrant]-&gt;[When:%20Execute%20Ansible%20Playbooks/Roles],[When:%20Execute%20Ansible%20Playbooks/Roles]-&gt;[Then:%20Assert%20with%20Testinfra],[Then:%20Assert%20with%20Testinfra]-&gt;[Cleanup%20Infrastructure])

In the `Then` phase Molecule executes different [Verifiers](https://molecule.readthedocs.io/en/latest/configuration.html#verifier), one of them is [Testinfra](https://testinfra.readthedocs.io/en/latest/), where you can write Unittest with a Python DSL. 

> Beware of old links to v1 of Molecule! As I followed blog posts that were just from a year or two ago, I walked into the trap of using Molecule v1. This is especially problematic if you try to install Molecule via `homebrew` where you currently also get the v1 version. So always double check, if there´s no `/v1/` in the docs´ url:

![current-docs-url](screenshots/current-docs-url.png)

### Project structure

Molecule introduces a well known project structure (at least for a Java developer like me):

![projectstructure](screenshots/projectstructure.png)

As you may notice the role standard directory `tasks` is now accompanied by a `tests` directory where the Testinfra testcases reside.

This repository uses [a Ansible role](docker/tasks/main.yml) that installs Docker into an Ubuntu Box:

```yaml
- name: add Docker apt key
  apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    id: 9DC858229FC7DD38854AE2D88D81803C0EBFCD88
    state: present
  ignore_errors: true

- name: add docker apt repo
  apt_repository:
    repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_lsb.codename }} stable"
    update_cache: yes
  become: true

- name: install Docker apt package
  apt:
    pkg: docker-ce
    state: latest
    update_cache: yes
  become: true

- name: add vagrant user to docker group.
  user:
    name: vagrant
    groups: docker
    append: yes
  become: true
```

With Testinfra we can assert on things we want to achieve with our Ansible role: Install the `docker` package and add the user `vagrant` to the group `docker`. Our testcases could be found in [test_docker.py](docker/tests/test_docker.py):

```python
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_is_docker_installed(host):
    package_docker = host.package('docker-ce')

    assert package_docker.is_installed


def test_vagrant_user_is_part_of_group_docker(host):
    user_vagrant = host.user('vagrant')

    assert 'docker' in user_vagrant.groups
    
```

### Prerequisites

* `brew install ansible`
* `brew cask install virtualbox`
* `brew cask install vagrant`

> Please don´t install molecule with homebrew on Mac, but always with pip since you only get old versions and need to manually install testinfra, ansible, flake8 and other packages
* `pip install molecule --user`

> For using Vagrant with Molecule we also need `python-vagrant` module installed
* `pip install python-vagrant`


### How to

See the [Molecule docs](https://molecule.readthedocs.io/en/latest/configuration.html)

Execute:

`molecule init role --driver-name vagrant --role-name docker --verifier-name testinfra`

this will give:

`--> Initializing role docker...
 Successfully initialized new role in /Users/jonashecht/dev/molecule-ansible-vagrant/docker.`
 
Now we´re able to run our first test. Go into `docker` directory and run:

`molecule verify`

As Molecule has different phases, you can also explicitely run `molecule destroy` or `molecule converge` - the commands will recognice required upstream phases like `create` and skips them if they where already run before (e.g. if the Vagrant Box is running already).