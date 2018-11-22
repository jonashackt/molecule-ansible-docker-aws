# molecule-ansible-vagrant
Example project showing how to test Ansible roles with Molecule and Vagrant


### Prerequisites

* `brew install ansible`
* `brew install ansible-lint`
* `brew install flake8`
* `pip install testinfra`
* `pip install ansible`
* `brew cask install virtualbox`
* `brew cask install vagrant`
* `brew install molecule`

### Let´s go

Execute:

`molecule init --driver vagrant --role install-docker --verifier testinfra`

this will give:

`--> Initializing role install-docker...
 Successfully initialized new role in /Users/jonashecht/dev/molecule-ansible-vagrant/install-docker.`
 
Now we´re able to run our first test. Go into `install-docker` directory and run:

`molecule test`