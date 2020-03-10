Vagrant.configure("2") do |config|
    config.vm.box = "generic/ubuntu1804"

    config.vm.define 'ubuntu'

    config.vm.provider :virtualbox do |vb|
        vb.name = 'ubuntu'
        vb.memory = 128
        vb.cpus = 1
    end
end