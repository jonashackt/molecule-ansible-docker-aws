import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_is_docker_installed(host):
    package_docker = host.package('docker-ce')

    assert package_docker.is_installed


def test_vagrant_user_is_part_of_group_docker(host):
    user_vagrant = host.user('vagrant')

    assert 'docker' in user_vagrant.groups


def test_run_hello_world_container_successfully(host):
    hello_world_ran = host.run("sudo docker run hello-world")

    assert 'Hello from Docker!' in hello_world_ran.stdout
