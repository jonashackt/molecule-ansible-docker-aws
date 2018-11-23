# molecule-ansible-vagrant
Example project showing how to test Ansible roles with Molecule and Vagrant

### TDD for Infrastructure code with Molecule!

[Molecule](https://molecule.readthedocs.io/en/latest/#) seems to be a pretty neat TDD framework for testing Infrastructur-as-Code using Ansible. Molecule executes the following steps:

![tdd-for-iac](https://yuml.me/diagram/scruffy/class/[Given:%20Spin%20up%20Infrastructure%20with%20Vagrant]-&gt;[When:%20Execute%20Ansible%20Playbooks/Roles],[When:%20Execute%20Ansible%20Playbooks/Roles]-&gt;[Then:%20Assert%20with%20Testinfra],[Then:%20Assert%20with%20Testinfra]-&gt;[Cleanup%20Infrastructure])

In the `Then` phase Molecule executes different [Verifiers](https://molecule.readthedocs.io/en/latest/configuration.html#verifier), one of them is [Testinfra](https://testinfra.readthedocs.io/en/latest/), where you can write Unittest with a Python DSL. This repository uses [a Ansible role](docker/tasks/main.yml) that installs Docker into an Ubuntu Box:

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

With Testinfra we can assert on things we want to achieve with our Ansible role: Install the `docker` package and add the user `vagrant` to the group `docker`. Our testcases reside in [test_docker.py](docker/tests/test_docker.py)

```python
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_is_docker_installed(host):
    package_docker = host.package('docker-ce')

    assert package_docker.is_installed


def test_vagrant_user_is_part_of_group_docker(host):
    user_vagrant = host.user('vagrant')

    assert 'docker' in user_vagrant.groups
    
```

### Prerequisites

* `brew install ansible`
* `brew install ansible-lint`
* `brew install flake8`
* `pip install testinfra`
* `pip install ansible`
* `brew cask install virtualbox`
* `brew cask install vagrant`
* `brew install molecule`


### How to

Execute:

`molecule init --driver vagrant --role docker --verifier testinfra`

this will give:

`--> Initializing role docker...
 Successfully initialized new role in /Users/jonashecht/dev/molecule-ansible-vagrant/docker.`
 
Now we´re able to run our first test. Go into `docker` directory and run:

`molecule test`