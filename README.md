# molecule-ansible-docker-vagrant
[![Build Status](https://travis-ci.org/jonashackt/molecule-ansible-docker-vagrant.svg?branch=master)](https://travis-ci.org/jonashackt/molecule-ansible-docker-vagrant)
[![CircleCI](https://circleci.com/gh/jonashackt/molecule-ansible-docker-vagrant.svg?style=svg)](https://circleci.com/gh/jonashackt/molecule-ansible-docker-vagrant)
[![versionansible](https://img.shields.io/badge/ansible-2.7.11-brightgreen.svg)](https://docs.ansible.com/ansible/latest/index.html)
[![versionmolecule](https://img.shields.io/badge/molecule-2.20.1-brightgreen.svg)](https://molecule.readthedocs.io/en/latest/)
[![versiontestinfra](https://img.shields.io/badge/testinfra-1.19.0-brightgreen.svg)](https://testinfra.readthedocs.io/en/latest/)
[![versionawscli](https://img.shields.io/badge/awscli-1.16.130-brightgreen.svg)](https://aws.amazon.com/cli/)

Example project showing how to test Ansible roles with Molecule using Testinfra and a multiscenario approach with Vagrant, Docker & AWS EC2 as the infrastructure under test. 

[![asciicast](https://asciinema.org/a/214914.svg)](https://asciinema.org/a/214914)

There are already two blog posts complementing this repository:
* [Test-driven infrastructure development with Ansible & Molecule](https://blog.codecentric.de/en/2018/12/test-driven-infrastructure-ansible-molecule/)
* [Continuous Infrastructure with Ansible, Molecule & TravisCI](https://blog.codecentric.de/en/2018/12/test-driven-infrastructure-ansible-molecule/)
* [Continuous cloud infrastructure with Ansible, Molecule & TravisCI on AWS](https://blog.codecentric.de/en/2019/01/ansible-molecule-travisci-aws/)

## Table of Contents  
* [TDD for Infrastructure code with Molecule!](#tdd-for-infrastructure-code-with-molecule)
* [Prerequisites](#prerequisites)
* [Project structure](#project-structure)
* [Molecule configuration](#molecule-configuration)
* [Execute Molecule](#execute-molecule)
* [Multi-Scenario Molecule setup](#multi-scenario-molecule-setup)
* [Ubuntu based Docker-in-Docker builds](#ubuntu-based-docker-in-docker-builds)
* [Docker-in-Docker with ubuntu:bionic](#docker-in-docker-with-ubuntubionic)
* [Testing the Docker-in-Docker installation](#testing-the-docker-in-docker-installation)
* [Molecule with AWS EC2 as the infrastructure provider](#molecule-with-aws-ec2-as-the-infrastructure-provider)
* [Configure Molecule to use EC2](#configure-molecule-to-use-ec2)
* [Having a look into the create.yml](#having-a-look-into-the-createyml)
* [Install & configure AWS CLI](#install--configure-aws-cli)
* [Configure Region & VPC subnet id](#configure-region--vpc-subnet-id)
* [Choosing an Ubuntu 18.04 AMI](#choosing-an-ubuntu-1804-ami)
* [Creating a EC2 instance with Molecule](#creating-a-ec2-instance-with-molecule)
* [Run a first Test on EC2 with Molecule](#run-a-first-test-on-ec2-with-molecule)
* [Cleaning up](#cleaning-up)
* [Final check: molecule test](#final-check-molecule-test)
* [Use TravisCI to execute Molecule with EC2 infrastructure](#use-travisci-to-execute-molecule-with-ec2-infrastructure)
* [Problems with boto on Travis](#problems-with-boto-on-travis)
* [Use CircleCI to execute Molecule with EC2 infrastructure](#use-circleci-to-execute-molecule-with-ec2-infrastructure)
* [Schedule regular CircleCI builds with workflow triggers & cron](#schedule-regular-circleci-builds-with-workflow-triggers--cron)

## TDD for Infrastructure code with Molecule!

[Molecule](https://molecule.readthedocs.io/en/latest/#) seems to be a pretty neat TDD framework for testing Infrastructur-as-Code using Ansible. As previously announced on September 26 2018 [Ansible treats Molecule as a first class citizen](https://groups.google.com/forum/#!topic/ansible-project/ehrb6AEptzA) from now on - backed by Redhat also.

Molecule executes the following steps:

![tdd-for-iac](https://yuml.me/diagram/scruffy/class/[Given:%20Spin%20up%20Infrastructure%20with%20Docker%20or%20Vagrant%20or%20Other]-&gt;[When:%20Execute%20Ansible%20Playbooks/Roles],[When:%20Execute%20Ansible%20Playbooks/Roles]-&gt;[Then:%20Assert%20with%20Testinfra],[Then:%20Assert%20with%20Testinfra]-&gt;[Cleanup%20Infrastructure])

In the `Then` phase Molecule executes different [Verifiers](https://molecule.readthedocs.io/en/latest/configuration.html#verifier), one of them is [Testinfra](https://testinfra.readthedocs.io/en/latest/), where you can write Unittest with a Python DSL. 

> Beware of old links to v1 of Molecule! As I followed blog posts that were just from a year or two ago, I walked into the trap of using Molecule v1. This is especially problematic if you try to install Molecule via `homebrew` where you currently also get the v1 version. So always double check, if there´s no `/v1/` in the docs´ url:

![current-docs-url](screenshots/current-docs-url.png)

Just start here: [Molecule docs](https://molecule.readthedocs.io/en/latest/configuration.html)


## Prerequisites

* `brew cask install virtualbox`
* `brew cask install vagrant`

> Please don´t install Ansible and Molecule with homebrew on Mac, but always with pip3 since you only get old versions and need to manually install testinfra, ansible, flake8 and other packages
* `pip3 install ansible`
* `pip3 install molecule --user`

> For using Vagrant with Molecule we also need `python-vagrant` module installed
* `pip3 install python-vagrant`



## Project structure

To initialize a new Molecule powered Ansible role named `docker` with the Vagrant driver and the Testinfra verifier you have to execute the following command:

`molecule init role --driver-name vagrant --role-name docker --verifier-name testinfra`

This will give:

`--> Initializing role docker...
 Successfully initialized new role in /Users/jonashecht/dev/molecule-ansible-vagrant/docker.`

Molecule introduces a well known project structure (at least for a Java developer like me):

![projectstructure](screenshots/projectstructure.png)

As you may notice the role standard directory `tasks` is now accompanied by a `tests` directory inside the `molecule` folder where the Testinfra testcases reside.

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

With Testinfra we can assert on things we want to achieve with our Ansible role: Install the `docker` package and add the user `vagrant` to the group `docker`. Testinfra uses [pytest](https://docs.pytest.org/en/latest/example/index.html) to execute the tests. Our testcases could be found in [test_docker.py](docker/molecule/tests/test_docker.py):

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

__More Testinfra code examples:__

As you´re not an in-depth Python hacker (like me), you´ll be maybe also interested in example code. Have a look at:

https://github.com/philpep/testinfra#quick-start

https://github.com/openmicroscopy/ansible-role-prometheus/blob/0.2.0/tests/test_default.py

https://github.com/mongrelion/ansible-role-docker/blob/master/molecule/default/tests/test_default.py

https://blog.octo.com/test-your-infrastructure-topology-on-aws/


## Molecule configuration

The [molecule.yml](docker/molecule/vagrant-ubuntu/molecule.yml) configures Molecule:

```
scenario:
  name: vagrant-ubuntu

driver:
  name: vagrant
  provider:
    name: virtualbox
platforms:
  - name: vagrant-ubuntu
    box: ubuntu/bionic64
    memory: 512
    cpus: 1
    provider_raw_config_args:
    - "customize [ 'modifyvm', :id, '--uartmode1', 'disconnected' ]"

provisioner:
  name: ansible
  lint:
    name: ansible-lint
    enabled: false
  playbooks:
    converge: playbook.yml

lint:
  name: yamllint
  enabled: false
verifier:
  name: testinfra
  directory: ../tests/
  env:
    # get rid of the DeprecationWarning messages of third-party libs,
    # see https://docs.pytest.org/en/latest/warnings.html#deprecationwarning-and-pendingdeprecationwarning
    PYTHONWARNINGS: "ignore:.*U.*mode is deprecated:DeprecationWarning"
  lint:
    name: flake8
  options:
    # show which tests where executed in test output
    v: 1

```

We have some specialties here. First thing is the follow addition to the `platforms` key:

```
    provider_raw_config_args:
    - "customize [ 'modifyvm', :id, '--uartmode1', 'disconnected' ]"
```

Without this configuration Molecule isn´t able to spin up "standard" Vagrant Ubuntu boxes like `ubuntu/bionic64` and `ubuntu/xenial64`. If you do a `tail -f /var/folders/5p/l1cc1kqd69n_qxrftgln7xdm0000gn/T/molecule/docker/default/vagrant-ubuntu-docker.err`, you see errors like this:

```
There was an error while executing `VBoxManage`, a CLI used by Vagrant
for controlling VirtualBox. The command and stderr is shown below.

Command: ["startvm", "64c5ca1e-0f7c-4dea-bc07-8144a56a0029", "--type", "headless"]

Stderr: VBoxManage: error: RawFile#0 failed to create the raw output file /usr/local/lib/python2.7/site-packages/molecule/provisioner/ansible/playbooks/vagrant/ubuntu-bionic-18.04-cloudimg-console.log (VERR_ACCESS_DENIED)
```

This is a workaround until https://github.com/ansible/molecule/issues/1556 gets fixed. This shouldn´t be necessary to be configured.

The second thing is `PYTHONWARNINGS: "ignore:.*U.*mode is deprecated:DeprecationWarning"` environment variable definition. If you don´t configure this you´ll end up with bloated test logs like this:

![verify-with-deprecation-warnings](screenshots/verify-with-deprecation-warnings.png)

If you use the `PYTHONWARNINGS` environment variable you gather beautiful and __green__ test executions:

![verify-with-deprecation-warnings-ignored](screenshots/verify-with-deprecation-warnings-ignored.png)


In case everything runs green you may notice that there´s is no hint which tests were executed. But I think that´s rather a pity since we want to see our whole test suite executed. That was the whole point why we even started to use a testing framework like Molecule!

But luckily there´s a way to get those tests shown inside our output. As Molecule uses [Testinfra](https://testinfra.readthedocs.io/en/latest/invocation.html) which itself leverages [pytest](https://docs.pytest.org/en/latest/) to execute our test cases and Testinfra is able to invoke pytest with additional properties. And pytest has [many options we can experiment with](https://docs.pytest.org/en/latest/reference.html#configuration-options). To configure a more verbose output for our tests in Molecule, add the following to the `verifier` section of your `molecule.yml`:

```
verifier:
  name: testinfra
...
  options:
    # show which tests where executed in test output
    v: 1
...
```

If we now execute a `molecule verify` we should see a much nicer overview of which test cases where executed:

![verify-with-pytest-verbose](screenshots/verify-with-pytest-verbose.png)


## Execute Molecule
 
Now we´re able to run our first test. Go into `docker` directory and run:

`molecule test`

As Molecule has different phases, you can also explicitely run `molecule converge` or `molecule verify` - the commands will recognice required upstream phases like `create` and skips them if they where already run before (e.g. if the Vagrant Box is running already).



# Multi-Scenario Molecule setup

With Molecule we could not only test our Ansible roles against one infrastructure setup - but we can use multiple of them! We only need to leverage the power of [Molecule scenarios](https://molecule.readthedocs.io/en/latest/configuration.html#scenario).

To get an idea on how this works I sligthly restructured the repository. We started out with the Vagrant driver / scenario. Now after also implementing a Docker driver in this repository on it´s own: https://github.com/jonashackt/molecule-ansible-docker I integrated it into this repository.

And because Docker is the default Molecule driver for testing Ansible roles I changed the name of the Vagrant scenario to `vagrant-ubuntu`. Don´t forget to install `docker`:

```
pip3 install docker
```

Using `molecule test` as we´re used to will now execute the Docker (e.g. `default`) scenario. This change results in the following project structure:

![multi-scenario-projectstructure](screenshots/multi-scenario-projectstructure.png)

To execute the `vagrant-ubuntu` Scenario you have to explicitely call it´s name:

```
molecule test --scenario-name vagrant-ubuntu
```

[![asciicast](https://asciinema.org/a/213352.svg)](https://asciinema.org/a/213352)

All the files which belong only to a certain scenario are placed inside the scenarios directory. For example in the Docker scenario this is `Dockerfile.js` and in Vagrant one this is `prepare.yml`. Also the `molecule.yml` files have to access the `playbook.yml` and the testfiles differently since they are now separate from the scenario directory to be [able to reuse them over all scenarios](https://molecule.readthedocs.io/en/latest/examples.html#sharing-across-scenarios):

```
...
provisioner:
  name: ansible
...
  playbooks:
    converge: ../playbook.yml
...
verifier:
  name: testinfra
  directory: ../tests/
...
```

Now we can also integrate & use TravisCI in this repository since the [default scenario Docker is supported on Travis](https://molecule.readthedocs.io/en/latest/testing.html#travis-ci)! :)

![travisci-molecule-executing-testinfra-tests](screenshots/travisci-molecule-executing-testinfra-tests.png)



## Ubuntu based Docker-in-Docker builds

As we don´t have a Vagrant environment in a Cloud CI system available for us right now (see https://github.com/jonashackt/vagrant-ansible-on-appveyor), we should be enable us somehow to test our Ansible role only with the Docker driver.

The standard Docker-in-Docker image provided by Docker Inc is based on Alpine Linux (see https://stackoverflow.com/a/53459483/4964553 & the `dind` tags in https://hub.docker.com/_/docker/). But our role is designed for Ubuntu and thus uses the `apt` package manager instead of `apk`. So we can´t use the standard Docker-in-Docker image.

But there should be a way to do Docker-in-Docker installation with a Ubuntu base image like `ubuntu:bionic`! And there is :) 

Let´s assume the [standard Ubuntu Docker installation](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce-1) our starting point. Everything described there is done inside our Ansible role under test __docker__ inside the playbook [docker/tasks/main.yml](docker/tasks/main.yml).

All the extra steps needed to install Docker inside a Ubuntu Docker container will be handled inside the `prepare` step. Therefore we´ll use [Molecules´ prepare.yml playbook](https://molecule.readthedocs.io/en/latest/configuration.html#id12):

> The prepare playbook executes actions which bring the system to a given state prior to converge. It is executed after create, and only once for the duration of the instances life. This can be used to bring instances into a particular state, prior to testing.


### Configure a custom prepare step
 
The Docker-in-Docker build is only used ([and should only be used](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/)) inside our CI pipeline. The `prepare` step inside our Molecule test suites´s `default` Docker scenario will be only executed for testing purposes.
 
So let´s configure our `default` Docker scenario to use a `prepare.yml` which could be done inside the `molecule.yml`:

```yaml
...
  playbooks:
    prepare: prepare-docker-in-docker.yml
    converge: ../playbook.yml
...
```


### Docker-in-Docker with ubuntu:bionic

Now we should have a look into the [prepare-docker-in-docker.yml](docker/molecule/default/prepare-docker-in-docker.yml):

```yaml
# Prepare things only necessary in Ubuntu Docker-in-Docker scenario
- name: Prepare
  hosts: all
  tasks:
  - name: install gpg package
    apt:
      pkg: gpg
      state: latest
      update_cache: true
    become: true

    # We need to anticipate the installation of Docker before the role execution...
  - name: use our role to install Docker
    include_tasks: ../../tasks/main.yml

  - name: create /etc/docker
    file:
      state: directory
      path: /etc/docker

  - name: set storage-driver to vfs via daemon.json
    copy:
      content: |
        {
          "storage-driver": "vfs"
        }
      dest: /etc/docker/daemon.json

  # ...since we need to start Docker in a complete different way
  - name: start Docker daemon inside container see https://stackoverflow.com/a/43088716/4964553
    shell: "/usr/bin/dockerd -H unix:///var/run/docker.sock > dockerd.log 2>&1 &"
```

As the `ubuntu:bionic` Docker image is sligthly stripped down compared to a "real" Ubuntu virtual machine, we need to install the `gpg` package at first.

After that the Docker installation has to be executed just in the same way as on a virtual machine using Vagrant. So we simply re-use the existing Docker role here - so we´re not forced to copy code!

Then really being able to run Docker-in-Docker we need to do three things:

1. Run Docker with `--priviledged` (which should really only be used inside our CI environment, because it grant´s full access to the host environment (see https://hub.docker.com/_/docker/))
2. Use the [storage-driver `vfs`](https://docs.docker.com/storage/storagedriver/vfs-driver/#configure-docker-with-the-vfs-storage-driver), which is slow & inefficient but is the only one guaranteed to work regardless of underlying filesystems
3. Start the Docker daemon with `/usr/bin/dockerd -H unix:///var/run/docker.sock > dockerd.log 2>&1 &`, or otherwise you´ll run into errors like `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` (see https://stackoverflow.com/a/43088716/4964553)

You may noticed that __2.__ & __3.__ are handled by our `prepare-docker-in-docker.yml` already. To enable the __1.__ `--priviledged` mode we need to configure Molecules´ Docker driver inside the `molecule.yml`:

```yaml
...
driver:
  name: docker
platforms:
  - name: docker-ubuntu
    image: ubuntu:bionic
    privileged: true
...
```

### Testing the Docker-in-Docker installation

The last step - or the first, if you leverage the power of Test-Driven-Development (TDD) - was to create a suitable testcase. This test should verify whether the Docker-in-Docker installation was successful.

Therefore we can use the [hello-world](https://hub.docker.com/_/hello-world/) Docker image. Let´s execute a `docker run hello-world` straight inside our test case `test_run_hello_world_container_successfully` in our test suite [test_docker.py](docker/molecule/tests/test_docker.py):

```
def test_run_hello_world_container_successfully(host):
    hello_world_ran = host.run("docker run hello-world")

    assert 'Hello from Docker!' in hello_world_ran.stdout
```

This will verify that

1. the Docker client is able to contact the Docker daemon
2. the Docker daemon successfully pulled the image `hello-world` from the Docker Hub
3. the Docker daemon created a new container from that image and runs the executable inside
4. the Docker daemon streamed the executables output containing `Hello from Docker!` to the Docker client, which send it to the terminal


# Molecule with AWS EC2 as the infrastructure provider

Now that we successfully used Vagrant & Docker as infrastructure providers for Molecule, we should now start to use a cloud provider like AWS. 

We should be able to use [Molecule's EC2 driver](https://molecule.readthedocs.io/en/latest/configuration.html#ec2), which itself uses [Ansible's ec2 module](http://docs.ansible.com/ansible/latest/ec2_module.html) to interact with AWS.

First we need to install the [Boto Python packages](https://pypi.org/project/boto/). They will provide interfaces to Amazon Web Services:

```
pip3 install boto boto3
```


### Configure Molecule to use EC2

Then we just init a new Molecule scenario inside our existing multi scenario project called `aws-ec2-ubuntu`. Therefore we can leverage Molecule's `molecule init scenario` command:

```
cd molecule-ansible-docker-vagrant/docker

molecule init scenario --driver-name ec2 --role-name docker --scenario-name aws-ec2-ubuntu
```

That should create a new directory `aws-ec2-ubuntu` inside the `docker/molecule` folder.  We'll integrate the results into our multi scenario project in a second.

Now let's dig into the generated `molecule.yml`:

```yaml
scenario:
  name: aws-ec2-ubuntu

driver:
  name: ec2
platforms:
  - name: instance
    image: ami-a5b196c0
    instance_type: t2.micro
    vpc_subnet_id: subnet-6456fd1f

provisioner:
  name: ansible
  lint:
    name: ansible-lint
    enabled: false
  playbooks:
    converge: ../playbook.yml

lint:
  name: yamllint
  enabled: false

verifier:
  name: testinfra
  directory: ../tests/
  env:
    # get rid of the DeprecationWarning messages of third-party libs,
    # see https://docs.pytest.org/en/latest/warnings.html#deprecationwarning-and-pendingdeprecationwarning
    PYTHONWARNINGS: "ignore:.*U.*mode is deprecated:DeprecationWarning"
  lint:
    name: flake8
  options:
    # show which tests where executed in test output
    v: 1
```

As we already tuned the `molecule.yml` files for our other scenarios like `docker` and `vagrant-ubuntu`, we know what to change here. `provisioner.playbook.converge` needs to be configured, so the one `playbook.yml` could be found.

Also the `verifier` section has to be enhanced to gain all the described advantages like supressed deprecation warnings and the better test result overview.

As you may noticed, the driver now uses `ec2` and the platform is already pre-configured with a concrete Amazon Machine Image (AMI) and `instance_type` etc. I just tuned the instance name to `aws-ec2-ubuntu`, like we did in our Docker and Vagrant scenarios.


### Having a look into the create.yml

The generated `create.yml` and `destroy.yml` Ansible playbooks look rather stunning - especially to AWS newbees. Let's have a look into the `create.yml`:

```yaml
- name: Create
  hosts: localhost
  connection: local
  gather_facts: false
  no_log: "{{ not (lookup('env', 'MOLECULE_DEBUG') | bool or molecule_yml.provisioner.log|default(false) | bool) }}"
  vars:
    ssh_user: ubuntu
    ssh_port: 22

    security_group_name: molecule
    security_group_description: Security group for testing Molecule
    security_group_rules:
      - proto: tcp
        from_port: "{{ ssh_port }}"
        to_port: "{{ ssh_port }}"
        cidr_ip: '0.0.0.0/0'
      - proto: icmp
        from_port: 8
        to_port: -1
        cidr_ip: '0.0.0.0/0'
    security_group_rules_egress:
      - proto: -1
        from_port: 0
        to_port: 0
        cidr_ip: '0.0.0.0/0'

    keypair_name: molecule_key
    keypair_path: "{{ lookup('env', 'MOLECULE_EPHEMERAL_DIRECTORY') }}/ssh_key"
  tasks:
    - name: Create security group
      ec2_group:
        name: "{{ security_group_name }}"
        description: "{{ security_group_name }}"
        rules: "{{ security_group_rules }}"
        rules_egress: "{{ security_group_rules_egress }}"

    - name: Test for presence of local keypair
      stat:
        path: "{{ keypair_path }}"
      register: keypair_local

    - name: Delete remote keypair
      ec2_key:
        name: "{{ keypair_name }}"
        state: absent
      when: not keypair_local.stat.exists

    - name: Create keypair
      ec2_key:
        name: "{{ keypair_name }}"
      register: keypair

    - name: Persist the keypair
      copy:
        dest: "{{ keypair_path }}"
        content: "{{ keypair.key.private_key }}"
        mode: 0600
      when: keypair.changed

    - name: Create molecule instance(s)
      ec2:
        key_name: "{{ keypair_name }}"
        image: "{{ item.image }}"
        instance_type: "{{ item.instance_type }}"
        vpc_subnet_id: "{{ item.vpc_subnet_id }}"
        group: "{{ security_group_name }}"
        instance_tags:
          instance: "{{ item.name }}"
        wait: true
        assign_public_ip: true
        exact_count: 1
        count_tag:
          instance: "{{ item.name }}"
      register: server
      with_items: "{{ molecule_yml.platforms }}"
      async: 7200
      poll: 0

    - name: Wait for instance(s) creation to complete
      async_status:
        jid: "{{ item.ansible_job_id }}"
      register: ec2_jobs
      until: ec2_jobs.finished
      retries: 300
      with_items: "{{ server.results }}"

    # Mandatory configuration for Molecule to function.

    - name: Populate instance config dict
      set_fact:
        instance_conf_dict: {
          'instance': "{{ item.instances[0].tags.instance }}",
          'address': "{{ item.instances[0].public_ip }}",
          'user': "{{ ssh_user }}",
          'port': "{{ ssh_port }}",
          'identity_file': "{{ keypair_path }}",
          'instance_ids': "{{ item.instance_ids }}", }
      with_items: "{{ ec2_jobs.results }}"
      register: instance_config_dict
      when: server.changed | bool

    - name: Convert instance config dict to a list
      set_fact:
        instance_conf: "{{ instance_config_dict.results | map(attribute='ansible_facts.instance_conf_dict') | list }}"
      when: server.changed | bool

    - name: Dump instance config
      copy:
        content: "{{ instance_conf | to_json | from_json | molecule_to_yaml | molecule_header }}"
        dest: "{{ molecule_instance_config }}"
      when: server.changed | bool

    - name: Wait for SSH
      wait_for:
        port: "{{ ssh_port }}"
        host: "{{ item.address }}"
        search_regex: SSH
        delay: 10
        timeout: 320
      with_items: "{{ lookup('file', molecule_instance_config) | molecule_from_yaml }}"

    - name: Wait for boot process to finish
      pause:
        minutes: 2

``` 

If we skim over the code, we notice the usage of Ansible's [ec2_group module](https://docs.ansible.com/ansible/latest/modules/ec2_group_module.html). It is used to maintains AWS EC2 security groups. Using the parameters `rules` and `rules_egress`, it configures appropriate firewall inbound and outbound rules.

Thereafter Ansible's [ec2_key module](https://docs.ansible.com/ansible/latest/modules/ec2_key_module.html) is used to create a new EC2 key pair & store it locally, if non exists on your local machine already.

And then the [ec2 module](https://docs.ansible.com/ansible/latest/modules/ec2_module.html) takes over, which is able to create or terminate AWS EC2 instances without the need to hassle with the GUI.

Waiting for the EC2 instance to come up, the `create.yml` playbook uses the [async_status module](https://docs.ansible.com/ansible/latest/modules/async_status_module.html) on the pre-registered variable `server.results` from the `ec2` module.

The following Ansible module are solely used to create an inline Ansible inventory, which is finally used to connect into the EC2 instance via SSH.

The generated `destroy.yml` playbook is just the opposite to the `create.yml` playbook and tears the created EC2 instance down.


### Install & configure AWS CLI

Now let's give our configuration a shot. Just be sure to meet some prerequisites. 

First we need to sure to have the [AWS CLI installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html). We can also do this via pip package manager with:
 
```
pip3 install awscli
```
 
Now we should check, if AWS CLI was successfully installed. The `aws --version` command should print out sometime like:

```
$ aws --version
aws-cli/1.16.80 Python/3.7.2 Darwin/18.2.0 botocore/1.12.70
```

Now configure the AWS CLI to use the correct credentials. [According to the AWS docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration), the fastest way to accomplish that is to run `aws configure`:

```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: eu-central-1
Default output format [None]: json
```

### Configure Region & VPC subnet id 

As there currently is a discrepancy in the UX of Molecule, where every configuration parameter is generated correctly by a `molecule init --driver-name ec2` command and picked up from `~/.aws/credentials`. __Except__ the `region` configuration from `~/.aws/config`!

Running a Molecule test without setting the region correctly as environment variable, currently results [in the (already documented) error](https://github.com/ansible/molecule/issues/1570):

```
"msg": "Either region or ec2_url must be specified",
```

So for now we need to set the region manually before running our Molecule tests against EC2:

```
export EC2_REGION=eu-central-1
```

And there's another thing to do: We need to configure the correct `vpc_subnet_id` inside our `molecule.yml` - if not, we get an error like this:

```
    "    raise self.ResponseError(response.status, response.reason, body)",
    "boto.exception.EC2ResponseError: EC2ResponseError: 400 Bad Request",
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
    "<Response><Errors><Error><Code>InvalidSubnetID.NotFound</Code><Message>The subnet ID 'subnet-6456fd1f' does not exist</Message></Error></Errors><RequestID>1c971ba2-0d86-4335-9445-d989e988afce</RequestID></Response>"
]
```

We need to somehow figure out the correct VPC subnet id of our region. Therefore, you can simply use Ansible to gather that for you by using the [ec2_vpc_subnet_facts module](https://docs.ansible.com/ansible/latest/modules/ec2_vpc_subnet_facts_module.html):

```
    - name: Gather facts about all VPC subnets
      ec2_vpc_subnet_facts:
```

This will give the correct String inside the field `subnets.id`:

```
    ok: [localhost] => {
        "changed": false,
        "invocation": {
            "module_args": {
                "aws_access_key": null,
                ...
            }
        },
        "subnets": [
            {
                "assign_ipv6_address_on_creation": false,
                "availability_zone": "eu-central-1b",
                "availability_zone_id": "euc1-az3",
                ...
                "id": "subnet-a2efa1d9",
                ...
            },

```

As an alternative you can use AWS CLI with `aws ec2 describe-subnets` to find the correct ID inside the field `Subnets.SubnetId`:

```
$ aws ec2 describe-subnets

{
    "Subnets": [
        {
            "AvailabilityZone": "eu-central-1b",
            "AvailabilityZoneId": "euc1-az3",
            ...
            "SubnetId": "subnet-a2efa1d9",
            ...
        },
        {
            "AvailabilityZone": "eu-central-1c",
            ...
        },
        {
            "AvailabilityZone": "eu-central-1a",
            ...
        }
    ]
}
```

Now head over to your [molecule.yml](docker/molecule/aws-ec2-ubuntu/molecule.yml) and edit the `vpc_subnet_id` to contain the correct value:

```
scenario:
  name: aws-ec2-ubuntu

driver:
  name: ec2
platforms:
  - name: aws-ec2-ubuntu
    image: ami-a5b196c0
    instance_type: t2.micro
    vpc_subnet_id: subnet-a2efa1d9
...
```


### Choosing an Ubuntu 18.04 AMI

[As stated here[(https://askubuntu.com/a/1031156/451114), Amazon has a "official" Ubuntu 18.04 AMI - but this one isn't available under the free tier right now. 

But the official image is just the same as from Canonical, which could be found with the [ubuntu Amazon EC2 AMI Locator](https://cloud-images.ubuntu.com/locator/ec2/):

Fill in your region - e.g. for me this is `eu-central-1` - together with the desired Ubuntu version - like `18.04 LTS` - and the site should filter all available AMI images in this region:

![ubuntu-Amazon-EC2-AMI-Locator](screenshots/ubuntu-Amazon-EC2-AMI-Locator.png)

Now choose the AMI id with the __Instance Type__ `hvm:ebs-ssd`, which means that our EC2 instance will use Amazon Elastic Block Storage memory. Only this instance type is eligible for the free tier. In our region the the correct AMI id for Ubuntu 18.04 is `ami-080d06f90eb293a27`. We need to configure this inside our [molecule.yml](docker/molecule/aws-ec2-ubuntu/molecule.yml):

```
scenario:
  name: aws-ec2-ubuntu

driver:
  name: ec2
platforms:
  - name: aws-ec2-ubuntu
    image: ami-080d06f90eb293a27
    instance_type: t2.micro
    vpc_subnet_id: subnet-a2efa1d9
...
```


### Creating a EC2 instance with Molecule


Now we should have everything prepared. Let's try to run our first Molecule test on AWS EC2 (including `--debug` so that we see what's going on):

```
molecule --debug create --scenario-name aws-ec2-ubuntu
```

We could have a sneak peak into our Ansible EC2 Management console under https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1. We should see our EC2 instance starting up:

![aws-ec2-management-console-instance-startup](screenshots/aws-ec2-management-console-instance-startup.png)

If everything went fine, the `molecule create` command should succeed and your EC2 console should show the running EC2 instance:

![aws-ec2-management-console-instance-running](screenshots/aws-ec2-management-console-instance-running.png)



### Run a first Test on EC2 with Molecule

Now let's try to run our Ansible role against our new EC2 instance with Molecule:

```
molecule converge --scenario-name aws-ec2-ubuntu
```

That should just work fine. We then could head over to the verify-phase:

```
molecule verify --scenario-name aws-ec2-ubuntu
```

This should successfully execute our Testinfra test suite described in [test_docker.py](docker/molecule/tests/test_docker.py) onto our EC2 instance. If everything ran fine, it should give something like:

![aws-molecule-verify-success](screenshots/aws-molecule-verify-success.png)

If the last test function fails with an error like:
```
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```
you maybe have to add `sudo ` to the `docker run hello-world` statement:

```
def test_run_hello_world_container_successfully(host):
    hello_world_ran = host.run("sudo docker run hello-world")

    assert 'Hello from Docker!' in hello_world_ran.stdout
```


### Cleaning up

Finally it's time to clean up. Let's run a `molecule destroy` command to tear down or EC2 instance:

```
molecule --debug destroy --scenario-name aws-ec2-ubuntu
```

If that command went well, we can have a look into our AWS EC2 management console again:

![aws-ec2-management-console-instance-terminated](screenshots/aws-ec2-management-console-instance-terminated.png)

Our instance should have reached the state `terminated`, which is simmilar to `stopped` state - just for instances that used EBS storage (see the [AWS EC2 Instance Lifecycle chart](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html) for more info).

Here's a full asciinema cast of all the steps:

[![asciicast](https://asciinema.org/a/220434.svg)](https://asciinema.org/a/220434)


### Final check: molecule test

As you may remember, Molecule provides the consecutive list of steps that run one by one. For introductory reasons we choosed to execute each step manually.

But having everything configured and in place right now, we should be able to run the command that summarizes all the others: `molecule test`:

```
molecule test --scenario-name aws-ec2-ubuntu
```


## Use TravisCI to execute Molecule with EC2 infrastructure

My ultimate goal of the whole Molecule journey was to be able to let TravisCI create Cloud environments and execute Ansible roles on them.

So we should bring all the things learned togehter now: 

> Using Molecule to develop and test an Ansible role - togehter with the infrastructure provider AWS EC2 - automatically executed by TravisCI after commits or regularly with TravisCI cron jobs.

So let's do it! First we need to configure TravisCI. Therefore we need to enhance our [.travis.yml](.travis.yml). As we need the same python package additions as locally, we need to install `boto`, `boto3` and `awscli`:

```yaml
sudo: required
language: python

env:
- EC2_REGION=eu-central-1

services:
- docker

install:
- pip install molecule docker

# install AWS related packages
- pip install boto boto3
- pip install --upgrade awscli
# configure AWS CLI
- aws configure set aws_access_key_id $AWS_ACCESS_KEY
- aws configure set aws_secret_access_key $AWS_SECRET_KEY
- aws configure set default.region $DEPLOYMENT_REGION
# show AWS CLI config
- aws configure list

script:
- cd docker
# Molecule Testing Travis-locally with Docker
- molecule test
# Molecule Testing on AWS EC2
- molecule create --scenario-name aws-ec2-ubuntu
- molecule converge --scenario-name aws-ec2-ubuntu
- molecule verify --scenario-name aws-ec2-ubuntu
- molecule destroy --scenario-name aws-ec2-ubuntu
```

After that, we need to configure our AWS CLI to use the correct credentials and AWS region. This can be achieved by usind the `aws configure set` command. Then we need to head over to the settings tab of our TravisCI project (for the current project this can be found at https://travis-ci.org/jonashackt/molecule-ansible-docker-vagrant/settings) and insert the three environment variables `AWS_ACCESS_KEY`, `AWS_SECRET_KEY` and `DEPLOYMENT_REGION`:

![travisci-aws-settings-env-variables](screenshots/travisci-aws-settings-env-variables.png)

The last part is to add the molecule commands to the `script` section of the `.travis.yml`. 


### Problems with boto on Travis

As https://github.com/boto/boto/issues/3717 suggests, there are currently problems with the AWS connection library boto on TravisCI. They result in errors like:

```
        "msg": "Traceback (most recent call last):\n  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/async_wrapper.py\", line 147, in _run_module\n    (filtered_outdata, json_warnings) = _filter_non_json_lines(outdata)\n  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/async_wrapper.py\", line 88, in _filter_non_json_lines\n    raise ValueError('No start of json char found')\nValueError: No start of json char found\n", 
        "stderr": "Traceback (most recent call last):\n  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 113, in <module>\n    _ansiballz_main()\n  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 105, in _ansiballz_main\n    invoke_module(zipped_mod, temp_path, ANSIBALLZ_PARAMS)\n  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 48, in invoke_module\n    imp.load_module('__main__', mod, module, MOD_DESC)\n  File \"/tmp/ansible_ec2_payload_y3lfWH/__main__.py\", line 552, in <module>\n  File \"/home/travis/virtualenv/python2.7.14/lib/python2.7/site-packages/boto/__init__.py\", line 1216, in <module>\n    boto.plugin.load_plugins(config)\nAttributeError: 'module' object has no attribute 'plugin'\n", 
        "stderr_lines": [
            "Traceback (most recent call last):", 
            "  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 113, in <module>", 
            "    _ansiballz_main()", 
            "  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 105, in _ansiballz_main", 
            "    invoke_module(zipped_mod, temp_path, ANSIBALLZ_PARAMS)", 
            "  File \"/home/travis/.ansible/tmp/ansible-tmp-1547040777.3-69673074739502/AnsiballZ_ec2.py\", line 48, in invoke_module", 
            "    imp.load_module('__main__', mod, module, MOD_DESC)", 
            "  File \"/tmp/ansible_ec2_payload_y3lfWH/__main__.py\", line 552, in <module>", 
            "  File \"/home/travis/virtualenv/python2.7.14/lib/python2.7/site-packages/boto/__init__.py\", line 1216, in <module>", 
            "    boto.plugin.load_plugins(config)", 
            "AttributeError: 'module' object has no attribute 'plugin'"
        ]
    }
    
    PLAY RECAP *********************************************************************
    localhost                  : ok=6    changed=4    unreachable=0    failed=1   
    
    
ERROR: 
The command "molecule --debug create --scenario-name aws-ec2-ubuntu" exited with 2.
```

To fix this, there are two changes needed inside our [.travis.yml](.travis.yml). We need to set `sudo: false` and use the environment variable `BOTO_CONFIG=/dev/null`: 

```yaml
sudo: false
language: python

env:
- EC2_REGION=eu-central-1 BOTO_CONFIG="/dev/null"
...
```

And we need to add the `BOTO_CONFIG` environment variable to the same line as the already existing variable - otherwise Travis starts multiple builds with only one variable set to each build! See the docs (https://docs.travis-ci.com/user/environment-variables/#defining-multiple-variables-per-item)

> If you need to specify several environment variables for each build, put them all on the same line in the env array

Now head over to Travis and have a look into the log. It should look green and somehow like this: https://travis-ci.org/jonashackt/molecule-ansible-docker-vagrant/builds/477365844


## Use CircleCI to execute Molecule with EC2 infrastructure

As TravisCI is just one example of a cloud CI provider, let's use another one also - so let's just pick [CircleCI](https://circleci.com), let's go with this CI tool!  

> Using Molecule to develop and test an Ansible role - togehter with the infrastructure provider AWS EC2 - automatically executed by CircleCI after commits or regularly with CircleCI scheduled jobs.



So let's do it! First we need to configure CircleCI. Therefore we need to create a [.circleci/config.yml](.circleci/config.yml). As we need the same python package additions as locally, we need to install `boto`, `boto3` and `awscli`:

```yaml
version: 2
jobs:
  build:
    docker:
      - image: circleci/python:3.6.1

    environment:
      EC2_REGION: eu-central-1

    working_directory: ~/molecule-ansible-docker-vagrant

    steps:
      - checkout

      - run:
          name: Install Molecule dependencies
          command: |
            pip install molecule docker

      - run:
          name: Run Molecule Testing CircleCI-locally with Docker
          command: |
            cd docker
            molecule test

      - run:
          name: Install Molecule AWS dependencies
          command: |
            pip install boto boto3
            pip install --upgrade awscli

      - run:
          name: configure AWS CLI
          command: |
            aws configure set aws_access_key_id ${AWS_ACCESS_KEY}
            aws configure set aws_secret_access_key ${AWS_SECRET_KEY}
            aws configure set default.region ${EC2_REGION}
            aws configure list

      - run:
          name: Run Molecule Testing on AWS EC2
          command: |
            cd docker
            molecule create --scenario-name aws-ec2-ubuntu
            molecule converge --scenario-name aws-ec2-ubuntu
            molecule verify --scenario-name aws-ec2-ubuntu
            molecule destroy --scenario-name aws-ec2-ubuntu

```

After that, we need to configure our AWS CLI to use the correct credentials and AWS region. This can be achieved by usind the `aws configure set` command. Then we need to head over to the settings tab of our CircleCI project (for the current project this can be found at https://circleci.com/gh/jonashackt/molecule-ansible-docker-vagrant/edit#env-vars) and insert the three environment variables `AWS_ACCESS_KEY` & `AWS_SECRET_KEY`:

![circleci-aws-settings-env-variables](screenshots/circleci-aws-settings-env-variables.png)

The last part is to add the molecule commands to our `.circleci/config.yml`. 

### CircleCI gives Permission denied error at pip install

Using `circleci/python` Docker image it seems that you can't simply use `pip install xyz`:

```
PermissionError: [Errno 13] Permission denied: '/usr/local/lib/python3.6/site-packages/ptyprocess'
```

This error is also [reported here](https://discuss.circleci.com/t/circleci-python-docker-images-disallow-pip-install-due-to-directory-ownership/12504). To avoid this error, we need to use `sudo` to be able to install the pip packages successfully:

```yaml
version: 2
jobs:
  build:
    docker:
      - image: circleci/python:3.6.1
...
    steps:
      - checkout

      - run:
          name: Install Molecule dependencies
          command: |
            sudo pip install molecule docker

      - run:
          name: Run Molecule Testing CircleCI-locally with Docker
          command: |
            cd docker
            molecule test
```

### "msg": "Error connecting: Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))"

Molecule needs a Docker service available. Since CircleCI is mostly using pure Docker-based images to run it's CI jobs, there's no Docker service inside the Docker containers available. But there's help! [The docs state](https://circleci.com/docs/2.0/building-docker-images/):

> If your job requires docker or docker-compose commands, add the setup_remote_docker step into your .circleci/config.yml

We need to use `- setup_remote_docker`

```yaml
version: 2
jobs:
  build:
    docker:
      - image: circleci/python:3.6.1
...
    steps:
      - checkout
      
      - setup_remote_docker: 
          docker_layer_caching: true
```

Now head over to CircleCI and have a look into the log. It should look green and somehow like this: https://circleci.com/gh/jonashackt/molecule-ansible-docker-vagrant/16 :

![circleci-aws-full-run-docker-aws](screenshots/circleci-aws-full-run-docker-aws.png)


### Schedule regular CircleCI builds with workflow triggers & cron

As the docs at https://circleci.com/docs/2.0/triggers/#scheduled-builds state, we need to add the `workflows` section inside our [.circleci/config.yml](.circleci/config.yml) to be able to use cron-scheduled builds. First we introduce a `on-commit:` workflow, which will just be triggered by a normal git commit/push. Nothing new here.

But the second workflow item `weekly-schedule:` gets us where we wanted to be: using the `cron` trigger we can configure to run our Molecule tests e.g. once on friday 04:45 PM every week:

```yaml
workflows:
  version: 2
  on-commit:
    jobs:
      - build
  weekly-schedule:
    triggers:
      - schedule:
          # 17:55 every friday (see https://en.wikipedia.org/wiki/Cron)
          cron: "55 17 * * 5"
          filters:
            branches:
              only:
                - master
    jobs:
      - build
```

Now we should see our builds triggered by this cron regularly:

![circleci-cron-weekly-schedule](screenshots/circleci-cron-weekly-schedule.png)

Just mind the `UTC+2` timezone - for me, configuring `17:55` actually means, that my job will be scheduled to run at `19:55` - so don't think your config is wrong, maybe you're just in another timezone :)