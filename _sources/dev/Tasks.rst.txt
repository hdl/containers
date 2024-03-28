.. _Development:tasks:

Tasks
#####

.. _Development:credentials:

Credentials
===========

In order to push images to container registries, credentials are required.
The default ``github.token`` is enough for publishint to GHCR, however, docker.io and GCR do need specific secrets to be
setup.

In The Google Cloud Platform (GCP), credentials are managed through a CLI tool named ``gcloud``.
Periodically, a new key needs to be created and the outdated ones need to be removed.

.. sourcecode:: shell

   # List the projects:
   ~ gcloud projects list

   # Set the project for the current workspace:
   ~ gcloud config set project [PROJECT_ID]

   # List the available service accounts:
   ~ gcloud iam service-accounts list

   # Note the e-mail of the service account, and list the keys:
   ~ gcloud iam service-accounts keys list --iam-account=[NAME]@[PROJECT_ID].iam.gserviceaccount.com

   # Create a new key and save it to a file:
   ~ gcloud iam service-accounts keys create keyfile.json --iam-account [NAME]@[PROJECT_ID].iam.gserviceaccount.com

   # Go to organisation secrets and update the GCR_JSON_KEY secret with the whole content of the JSON file
   # https://github.com/organizations/hdl/settings/secrets/actions

   # Remove the JSON file
   ~ rm keyfile.json

   # Remove other (expired) keys
   ~ gcloud iam service-accounts keys delete KEY_ID --iam-account [NAME]@[PROJECT_ID].iam.gserviceaccount.com

See `cloud.google.com/container-registry/docs/advanced-authentication#json-key <https://cloud.google.com/container-registry/docs/advanced-authentication#json-key>`__.
