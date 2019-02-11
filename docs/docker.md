# Installation of Docker (Community Edition) on Ubuntu 18.04

### This guide shamefulyl copied from: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)

# Introduction
Docker is an application that simplifies the process of managing application processes in containers. Containers let you run your applications in resource-isolated processes. They're similar to virtual machines, but containers are more portable, more resource-friendly, and more dependent on the host operating system.

## Step 1 — Installing Docker
The Docker installation package available in the official Ubuntu repository may not be the latest version. To ensure we get the latest version, we'll install Docker from the official Docker repository. To do that, we'll add a new package source, add the GPG key from Docker to ensure the downloads are valid, and then install the package.

First, update your existing list of packages:

    sudo apt update

Next, install a few prerequisite packages which let apt use packages over HTTPS:

    sudo apt install apt-transport-https ca-certificates curl software-properties-common

Then add the GPG key for the official Docker repository to your system:

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

Add the Docker repository to APT sources:

    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

Next, update the package database with the Docker packages from the newly added repo:

    sudo apt update


Finally, install Docker:

    sudo apt install docker-ce

Docker should now be installed, the daemon started, and the process enabled to start on boot. Check that it's running:

    sudo systemctl status docker

The output should be similar to the following, showing that the service is active and running:

```bash
Output
● docker.service - Docker Application Container Engine
   Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2018-07-05 15:08:39 UTC; 2min 55s ago
     Docs: https://docs.docker.com
 Main PID: 10096 (dockerd)
    Tasks: 16
   CGroup: /system.slice/docker.service
           ├─10096 /usr/bin/dockerd -H fd://
           └─10113 docker-containerd --config /var/run/docker/containerd/containerd.toml
```

Installing Docker now gives you not just the Docker service (daemon) but also the docker command line utility, or the Docker client. We'll explore how to use the docker command later in this tutorial.


## Step 2 — Executing the Docker Command Without Sudo 

By default, the docker command can only be run the root user or by a user in the docker group, which is automatically created during Docker's installation process. If you attempt to run the docker command without prefixing it with sudo or without being in the docker group, you'll get an output like this:

    Output
    docker: Cannot connect to the Docker daemon. Is the docker daemon running on this host?.
    See 'docker run --help'.

If you want to avoid typing sudo whenever you run the docker command, add your username to the docker group:

    sudo usermod -aG docker ${USER}

To apply the new group membership, log out of the server and back in, or type the following:

    su - ${USER}


The rest of this article assumes you are running the docker command as a user in the docker group. If you choose not to, please prepend the commands with `sudo`.

## Step 3 — Using the Docker Command

Using docker consists of passing it a chain of options and commands followed by arguments. The syntax takes this form:

    docker [option] [command] [arguments]

To view all available subcommands, type:

    docker

To view the options available to a specific command, type:

    docker docker-subcommand --help

i.e:

    docker exec --help

To view system-wide information about Docker, use:

    docker info


## Congratulations

You've completed this section, proceed to [pgRouting Quick Start](/docs/quickStart.md)