# Scale

This part of the system is responsible for adding new Azure containers with redis using the [rahuliyer95/csc724-redis-collectd](https://hub.docker.com/r/rahuliyer95/csc724-redis-collectd) image.

## Azure Credentials

You can obtain the Azure SDK credentials using the following command

`az ad sp create-for-rbac --sdk-auth`

## Environment Variables

The application needs the following environment variables configured for it to run.

- `KAFKA_HOST` - Host where kafka is running
- `KAFKA_PORT` - Port on which kafka in listening to
- `KAFKA_TOPIC` - Kafka topic to listen for predictions (should be set to `prediction`
- `KAFKA_GROUP` - Group Id for Kafka consumer
- `AZURE_CLIENT_ID` - Client ID from azure credentials
- `AZURE_CLIENT_SECRET` - Client Secret from azure credentials
- `AZURE_SUBSCRIPTION_ID` - Subscription Id from azure credentials
- `AZURE_TENANT_ID` - Tenant Id from azure credentials
- `AZ_RESOURCE_GROUP` - Resource Group in Azure
- `DD_API_KEY` - DataDog API Key (skip if you are not using it)
- `ENV_INTERVAL` - Interval for collectd (needed for newer containers created)
- `DEBUG_FLAG` - Keep it "--no-verbose" if you don't want verbose logs else make it "--verbose"

## Building Image

Run `docker build . -t <TAG>` to build the image.

The `TAG` should be your [Docker Hub](https://hub.docker.com/) repository where you wil be push ing the image to.

## Deployment on Azure

Need to deploy it in a [Azure Virtual Network](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview) named `csc724`
