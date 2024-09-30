
import ntnx_prism_py_client

if __name__ == "__main__":
    # Configure the client
    config = ntnx_prism_py_client.Configuration()
    config.verify_ssl = False
    # IPv4/IPv6 address or FQDN of the cluster
    config.host = "10.15.4.38"
    # Port to which to connect to
    config.port = 9440
    # Max retry attempts while reconnecting on a loss of connection
    config.max_retry_attempts = 3
    # Backoff factor to use during retry attempts
    config.backoff_factor = 3
    # UserName to connect to the cluster
    config.username = "admin"
    # Password to connect to the cluster
    config.password = "Nutanix.123"
    # Please add authorization information here if needed.
    client = ntnx_prism_py_client.ApiClient(configuration=config)
    #disable SSL verification
    client.rest_client.pool_manager.ca_certs = False
    # Create an instance of the API class
    categories_api = ntnx_prism_py_client.CategoriesApi(api_client=client)
    page = 10
    limit = 100


    try:
        # disable SSL verification

        # Get all categories
        api_response = categories_api.get_all_categories(_page=page, _limit=limit)
        print(api_response)
        # print("hello")
    except ntnx_prism_py_client.rest.ApiException as e:
        print(e)
