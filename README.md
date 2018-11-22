# molecule-ansible-vagrant
Example project showing how to test Ansible roles with Molecule and Vagrant

### TDD for Infrastructure code with Molecule!

![tdd-for-iac](https://yuml.me/diagram/scruffy/class/[Given:%20Spin%20up%20Infrastructure%20with%20Vagrant]-&gt;[Then:%20Execute%20Ansible%20Playbooks/Roles],[Then:%20Execute%20Ansible%20Playbooks/Roles]-&gt;[Then:%20Assert%20with%20Testinfra],[Then:%20Assert%20with%20Testinfra]-&gt;[Cleanup%20Infrastructure])


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