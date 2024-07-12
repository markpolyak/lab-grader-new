1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and create a service account.
2. Create a key for the service account and download the JSON file.
3. Ensure the JSON file contains the following fields:

    ```json
    {
      "type": "",
      "project_id": "",
      "private_key_id": "",
      "private_key": "",
      "client_email": "",
      "client_id": "",
      "auth_uri": "",
      "token_uri": "",
      "auth_provider_x509_cert_url": "",
      "client_x509_cert_url": "",
      "universe_domain": ""
    }
    ```

4. Save the JSON file as `credentials.json` in the root directory of your project.