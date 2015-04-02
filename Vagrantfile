Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu-12.04"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.synced_folder '.', '/vagrant', disabled: true

  # Manage /etc/hosts on host and VMs
  config.hostmanager.enabled = false
  config.hostmanager.manage_host = true
  config.hostmanager.include_offline = true
  config.hostmanager.ignore_private_ip = false

  config.vm.define :head, primary: true do |machine|
    machine.vm.provider :virtualbox do |v|
      v.name = "cc-head"
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end

    machine.vm.synced_folder "./salt", "/srv/salt"
    machine.vm.synced_folder "./pillar", "/srv/pillar"

    machine.vm.hostname = "head"
    machine.vm.network :private_network, ip: "10.10.10.100"
    machine.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh", disabled: true
    machine.vm.network :forwarded_port, guest: 22, host: 2022
    machine.vm.network :forwarded_port, guest: 50070, host: 50070  # Namenode
    machine.vm.network :forwarded_port, guest: 5555, host: 5555    # Mesos
    machine.vm.network :forwarded_port, guest: 8888, host: 8888    # IPython Notebook

    machine.vm.provision :hostmanager

    machine.vm.provision :salt do |salt|
      salt.master_config = "vagrant/master.head"
      salt.minion_config = "vagrant/minion.head"
      salt.install_master = true
      salt.run_highstate = false
      salt.verbose = true
    end
  end

  config.vm.define :compute do |machine|
    machine.vm.provider :virtualbox do |v|
      v.name = "cc-compute"
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end

    machine.vm.hostname = "compute"
    machine.vm.network :private_network, ip: "10.10.10.101"
    machine.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh", disabled: true
    machine.vm.network :forwarded_port, guest: 22, host: 2023

    machine.vm.provision :hostmanager

    machine.vm.provision :salt do |salt|
      salt.minion_config = "vagrant/minion.compute"
      salt.run_highstate = false
      salt.verbose = true
    end
  end
end
