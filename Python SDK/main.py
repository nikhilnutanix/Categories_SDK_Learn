# import sys
# import os

# # Add the directory to sys.path
# sys.path.append('/Users/nikhil.saraswat/ntnx-api-categories/categories-mvc-api-codegen/categories-mvc-python-client-sdk/target/generated-sources/swagger')

# Now you can import modules from this directory
import json
import uuid
import ntnx_categories_py_client  # Replace with the actual module name

# suppress warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging

    
def createClient():
    config = ntnx_categories_py_client.Configuration()
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
    client_ = ntnx_categories_py_client.ApiClient(configuration=config)
    
    return client_

def ListCategories(categories_api, filter):
    try:
        # Get all categories
        api_response = categories_api.list_categories(_filter=filter)
        return api_response
    except Exception as e:
        # print(e)
        return None
        
        
def GetCategoryById(categories_api, extId):
    try:
        # Get all categories
        api_response = categories_api.get_category_by_id(extId)
        return api_response, None
    except Exception as e:
        # print(e)
        code = getErrorCode(e)
        return None, code

def getErrorCode(e):
    data = json.loads(e.body)
    # Extract the "code"
    code = data['error'][0]['code']
    return code

        
def CreateCategory(categories_api, key, value, description):
    try:
        # Get all categories
        cat = ntnx_categories_py_client.Category(key=key, value=value, description=description)
        # print(cat.to_str())
        try:
            api_response = categories_api.create_category(body=cat)
            # print(api_response)
            return api_response, None
        except Exception as e:
            # print(e)
            code = getErrorCode(e)
            print(f"Error Code: {code}")
            return None, code
    except Exception as e:
        print(e)
        return None, None


def DeleteCategoryById(categories_api, extId):
    try:
        # Get all categories
        api_response = categories_api.delete_category_by_id(extId)
        return api_response, None
    except Exception as e:
        # print(e)
        code = getErrorCode(e)
        return None, code


def UpdateCategoryById(categories_api, extId, cat, kwargs):
    try:
        # Get all categories
        api_response = categories_api.update_category_by_id(extId, body=cat, **kwargs)
        return api_response
    except Exception as e:
        print(e)
        return None


def setupLogger():
    # Configure logging
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(threadName)s:%(module)s:%(lineno)d] %(message)s'
)
    # Create a logger
    logger = logging.getLogger(__name__)
    return logger

if __name__ == "__main__":
    logger = setupLogger()
    logger.info("Starting the Categories API Python SDK")

    client = createClient()
    # Create an instance of the API class
    categories_api = ntnx_categories_py_client.CategoriesApi(api_client=client)
    # random uuid append to key and value
    key = f"key-{uuid.uuid4()}"
    value = f"value-{uuid.uuid4()}"
    # print(f"Key: {key}, Value: {value}")
    logger.info(f"Key: {key}, Value: {value}")
    description = "Description"
    # CreateCategory 
    createCategoryResp, _ = CreateCategory(categories_api, key, value, description)
    # print(createCategoryResp)
    # get extId from createCategoryResp
    extId = createCategoryResp.data.ext_id
    # print(f"extId: {extId}")
    logger.info(f"Category Created successfully with extId: {extId}")
    # print(f"Category Created successfully with extId: {extId}")
    logger.info(f"Category Created successfully with extId: {extId}")

    createCategoryResp, err_code = CreateCategory(categories_api, key, value, description)
    if err_code != "CTGRS-50023":
        # print(f"CreateCategory: Expected Error Code: CTGRS-50023, Got: {err_code}")
        logger.error(f"CreateCategory: Expected Error Code: CTGRS-50023, Got: {err_code}")

    # Use ListCategories to get the created category using filter
    filter = f"key eq '{key}' and value eq '{value}'"
    # check count of categories
    ListCategoriesResp = ListCategories(categories_api, filter)
    # print(ListCategoriesResp)
    if ListCategoriesResp.metadata.total_available_results != 1:
        # print(f"ListCategories: Expected Total Entities: 1, Got: {ListCategoriesResp.data.total_entities}")
        logger.error(f"ListCategories: Expected Total Entities: 1, Got: {ListCategoriesResp.data.total_entities}")
    elif ListCategoriesResp.data[0].ext_id != extId:
        # print(f"ListCategories: Expected extId: {extId}, Got: {ListCategoriesResp.data[0].ext_id}")
        logger.error(f"ListCategories: Expected extId: {extId}, Got: {ListCategoriesResp.data[0].ext_id}")
    else:
        # print(f"ListCategories: Success --> Category Created with extId: {extId}")
        logger.info(f"ListCategories: Success --> Category Created with extId: {extId}")


    # use the get api to get the category by ext_id
    GetCategoryByIdResp, _ = GetCategoryById(categories_api, extId)
    # get eTag from GetCategoryByIdResp
    eTag = ntnx_categories_py_client.ApiClient().get_etag(GetCategoryByIdResp)
    # print(f"eTag: {eTag}")
    logger.info(f"Category Retrieved successfully with extId: {extId}")
    newDescription = "New Description"
    # update the category with new description
    cat = ntnx_categories_py_client.Category(key=key, value=value, description=newDescription, owner_uuid=GetCategoryByIdResp.data.owner_uuid)
    # create kwargs for update_category
    kwargs = {"if_match": eTag}
    UpdateCategoryByIdResp = UpdateCategoryById(categories_api, extId, cat, kwargs)
    # print(UpdateCategoryByIdResp)
    # print(f"Category Updated successfully with extId: {extId}")
    logger.info(f"Category Updated successfully with extId: {extId}")

    # use list apis to verify that the update is successful
    ListCategoriesResp = ListCategories(categories_api, filter)
    # print(ListCategoriesResp)
    if ListCategoriesResp.metadata.total_available_results != 1:
        # print(f"ListCategories: Expected Total Entities: 1, Got: {ListCategoriesResp.data.total_entities}")
        logger.error(f"ListCategories: Expected Total Entities: 1, Got: {ListCategoriesResp.data.total_entities}")
    elif ListCategoriesResp.data[0].description != newDescription:
        # print(f"ListCategories: Expected Description: {newDescription}, Got: {ListCategoriesResp.data[0].description}")
        logger.error(f"ListCategories: Expected Description: {newDescription}, Got: {ListCategoriesResp.data[0].description}")
    else:
        # print("ListCategories: Success --> Category Description Updated")
        logger.info("ListCategories: Success --> Category Description Updated")

    # use get apis to verify that the update is successful
    GetCategoryByIdResp, _ = GetCategoryById(categories_api, extId)
    # print(GetCategoryByIdResp)
    if GetCategoryByIdResp.data.description != newDescription:
        # print(f"GetCategoryById: Expected Description: {newDescription}, Got: {GetCategoryByIdResp.data.description}")
        logger.error(f"GetCategoryById: Expected Description: {newDescription}, Got: {GetCategoryByIdResp.data.description}")
    else:
        # print("GetCategoryById: Success --> Category Description Updated")
        logger.info("GetCategoryById: Success --> Category Description Updated")

    # use the delete api to delete the category
    DeleteCategoryByIdResp, _ = DeleteCategoryById(categories_api, extId)
    # print(DeleteCategoryByIdResp)
    # print(f"Category Deleted successfully with extId: {extId}")
    logger.info(f"Category Deleted successfully with extId: {extId}")

    # use the get api to verify that the category is deleted and validate the response code is 404
    GetCategoryByIdResp, err_code = GetCategoryById(categories_api, extId)
    if err_code != "CTGRS-50006":
        # print(f"GetCategoryById: Expected Error Code: CTGRS-50006, Got: {err_code}")
        logger.error(f"GetCategoryById: Expected Error Code: CTGRS-50006, Got: {err_code}")
    else:
        # print("GetCategoryById: Success --> Category Already Deleted")
        logger.info("GetCategoryById: Success --> Category Already Deleted")

    # use delete api to verify that the category is already deleted and validate the response code is 404
    DeleteCategoryByIdResp, err_code = DeleteCategoryById(categories_api, extId)
    if err_code != "CTGRS-50006":
        # print(f"DeleteCategoryById: Expected Error Code: CTGRS-50006, Got: {err_code}")
        logger.error(f"DeleteCategoryById: Expected Error Code: CTGRS-50006, Got: {err_code}")
    else:
        # print("DeleteCategoryById: Success --> Category Already Deleted")
        logger.info("DeleteCategoryById: Success --> Category Already Deleted")

    # use the list api to verify that the category is deleted
    ListCategoriesResp = ListCategories(categories_api, filter)
    if ListCategoriesResp.metadata.total_available_results != 0:
        # print(f"ListCategories: Expected Total Entities: 0, Got: {ListCategoriesResp.data.total_entities}")
        logger.error(f"ListCategories: Expected Total Entities: 0, Got: {ListCategoriesResp.data.total_entities}")
    else:
        # print("ListCategories: Success --> Category Already Deleted")
        logger.info("ListCategories: Success --> Category Already Deleted")