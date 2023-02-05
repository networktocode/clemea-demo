# Take advantage of the Telemetry Stack!

This repository aims to provide a lab environment to practice concepts for the DevNet workshop "Take Advantage of your Telemetry Stack! How to Retrieve Data Programmatically to Aid in your Network Operations - DEVWKS-2452".

It provides setup instructions for a network lab with multiple CSR1kv devices to get telemetry data on. It also provides setup and instructions to setup a small Telemetry Stack based on Telegraf, Prometheus and Grafana to capture, normalize, store and visualize the data.

Optionally you can setup a Nautobot instance that hold extra information of the network devices topology that can further enrich the data obtained from the Telemetry Stack.

![Lab Topology](docs/images/lab-topology.png)

The lab topology has 2 setups.

- Network Topology: The lab is running with [containerlab](https://containerlab.dev/).
- Telemetry Stack: It is based on a popular setup of Telegraf, Prometheus and Grafana containers.

**Specs:** The lab is best run on Linux-based OS system with around 8 GB of RAM due to the amount of resources. For the demo it is running on Digital Ocean General purpose Ubuntu VMs with 4 vCPUs and 8 GB of RAM.

**Dependencies:** This is a container-based setup for the network and the Telemetry stack services. And for this you will need:
- [Install containerlab](https://containerlab.dev/install/)
- [Install docker](https://docs.docker.com/engine/install/ubuntu/). The package should container `docker compose` as well.

## Setup Network Lab (containerlab)

The `clemea-demo` topology is under the `./containerlab` folder. To deploy the lab you will need to have the necessary network container images. For example see [here](https://containerlab.dev/manual/kinds/ceos/).

After having the necessary container images, you can deploy the lab:

```shell
# Position into the containerlab folder
cd ./containerlab

# Deploy the clemea-demo lab
containerlab deploy -t clemea-demo.yml

# Go back to root folder
cd ../
```

You should be able to see the devices connected as depicted on the picture above.

## Setup Telemetry Stack (TPG)

The `tlm_stack` folder has the necessary configuration and files to spin up the Telemetry Stack.

```shell
# Position into the tlm_stack folder
cd ./tlm_stack

# You will need environment variables to run the TPG stack containers
cp example.env .env

# Deploy the Telemetry Stack
docker compose --project-name tpg -f docker-compose.yml up -d --remove-orphans

# Check all containers are up and running
docker ps

# Go back to root folder
cd ../
```

## Demo Nautobot for data enrichment

For the week of the Cisco Live Amsterdam event (2023), the devices for the lab are populated in [Nautobot Demo](https://nautobot.demo.networktocode.com/).

If you want to setup a local Nautobot lab to run this examples in the future, checkout [nautobot-lab](https://github.com/nautobot/nautobot-lab).

## Labs

The workshop is divided into 2 sections to better understand the concept of telemetry modeled data and the capabilitites of the telemetry stack. For more information around the questions and answers of the labs follow the links below.

- [Lab 1 - Let's play with  PromQL and Grafana](lab-1.md)
- [Lab 2 - Using Telemetry Data programatically](lab-2.md)

### Sauron example (using the stored data programatically)

![Sauron Help](docs/images/sauron-help.png)

![Sauron script for getting links with high bandwidth](docs/images/sauron-links-high.png)

![Sauron progress bar script for watching interface bandwidth](docs/images/sauron-watch-intf.png)
