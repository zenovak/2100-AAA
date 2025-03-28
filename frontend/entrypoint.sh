#!/bin/sh
set -e

# Replace env variable placeholders with real values
#
# ENV Variables required for NEXT_PUBLIC...
# See the following reference for issues arround compose.yml env variables not found in the client-side bundle
# https://medium.com/@ihcnemed/nextjs-on-docker-managing-environment-variables-across-different-environments-972b34a76203
# https://stackoverflow.com/questions/76280634/nextjs-app-not-read-environment-variables-from-docker-compose-yml
echo "Injecting NEXT_PUBLIC vars from compose.yml"

printenv | grep NEXT_PUBLIC_ | while read -r line ; do
  key=$(echo $line | cut -d "=" -f1)
  value=$(echo $line | cut -d "=" -f2)

  find /app/.next/ -type f -exec sed -i "s|$key|$value|g" {} \;
done

# Execute the container's main process (CMD in Dockerfile)
exec "$@"