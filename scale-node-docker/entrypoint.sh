#!/bin/bash

CREDENTIALS=$(
  cat <<EOF
{
  "clientId": "$AZURE_CLIENT_ID",
  "clientSecret": "$AZURE_CLIENT_SECRET",
  "subscriptionId": "$AZURE_SUBSCRIPTION_ID",
  "tenantId": "$AZURE_TENANT_ID",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
EOF
)

echo "$CREDENTIALS" >"$AZURE_AUTH_LOCATION"

python3 scale.py --kafka-host "$KAFKA_HOST" --kafka-port "$KAFKA_PORT" --topic "$KAFKA_TOPIC" "${DEBUG_FLAG:---no-verbose}"
