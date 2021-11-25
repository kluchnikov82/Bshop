# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "ubuntu/bionic64"
  config.vm.synced_folder ".", "/opt/bshop", type: "rsync",
    rsync__exclude: [".git/", ".vscode/", "frontend/node_modules/"]
  
  config.vm.host_name = "bshop"

  config.vm.network "forwarded_port", guest: 5432, host: 44432

  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
    # Customize the amount of memory on the VM:
    vb.memory = "4096"
    vb.cpus = 4
  end

  config.vm.provision  :shell, :path => "bootstrap_ubuntu1804.sh"
end
