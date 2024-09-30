package main

import (
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"log"

	"github.com/nutanix-core/ntnx-api-golang-sdk-internal/prism-go-client/v17/api"
	"github.com/nutanix-core/ntnx-api-golang-sdk-internal/prism-go-client/v17/client"
	import1 "github.com/nutanix-core/ntnx-api-golang-sdk-internal/prism-go-client/v17/models/prism/v4/config"
)

// Define the structure to match the JSON format
type ErrorResponse struct {
	Error []ErrorMessage `json:"error"`
}

type ErrorMessage struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	// Add other fields if needed
}

func getApiClientInstance() *client.ApiClient {
	ApiClientInstance := client.NewApiClient()
	ApiClientInstance.SetVerifySSL(false)
	ApiClientInstance.Host = "10.36.240.49"
	ApiClientInstance.Port = 9440
	ApiClientInstance.RetryInterval = 5000
	ApiClientInstance.MaxRetryAttempts = 5
	ApiClientInstance.Username = "admin"
	ApiClientInstance.Password = "Nutanix.123"
	return ApiClientInstance
}

func getCategoriesApiInstance(ApiClientInstance *client.ApiClient) *api.CategoriesApi {
	CategoriesApiInstance := api.NewCategoriesApi(ApiClientInstance)
	return CategoriesApiInstance
}

func getErrorCode(err error) string {
	// Unmarshal the JSON data into the struct
	var response ErrorResponse
	err = json.Unmarshal([]byte(err.Error()), &response)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %v", err)
	}

	// Access the code field from the first error message
	if len(response.Error) > 0 {
		code := response.Error[0].Code
		return code
	} else {
		return ""
	}
}



func main() {
	ApiClientInstance := getApiClientInstance()
	CategoriesApiInstance := getCategoriesApiInstance(ApiClientInstance)


	key := "key-" + uuid.New().String()
	value := "value-" + uuid.New().String()
	println("key: ", key, " value: ", value)
	description := "description"
	category := &import1.Category{
		Key:         &key,
		Description: &description,
		Value:       &value,
	}
	createCategoryResponse, err := CategoriesApiInstance.CreateCategory(category, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	cat := createCategoryResponse.GetData().(import1.Category)
	fmt.Println("ExtId: ", *cat.ExtId)

	// try to again create the same category
	_, err = CategoriesApiInstance.CreateCategory(category, nil, nil)
	if err != nil {
		fmt.Println(err.Error())
		code := getErrorCode(err)
		if code != "CTGRS-50023" {
			fmt.Println("CreateCategory: Expected error code: CTGRS-50023, but got: ", code)
		}
	} else {
		fmt.Println("CreateCategory: Expected error: Category already exists, but got none")
	}
	// cat = createCategoryResponse.GetData().(import1.Category)
	filter := "key eq '" + key + "' and value eq '" + value + "'"
	listCategoriesResponse, err := CategoriesApiInstance.ListCategories(nil, nil, &filter, nil, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	data := listCategoriesResponse.GetData().([]import1.Category)
	if len(data) != 1 {
		fmt.Println("ListCategories: Expected 1 category, but got ", len(data))
	} else {
		fmt.Println("ListCategories: Category found!")
	}
	// print the ext_id of the category returned
	fmt.Println("ExtId: ", *data[0].ExtId)
	if *data[0].ExtId != *cat.ExtId {
		fmt.Println("ListCategories: Expected category ext_id: ", *cat.ExtId, " but got: ", *data[0].ExtId)
	}
	// use the get api to get the category by ext_id
	getCategoryResponse, err := CategoriesApiInstance.GetCategoryById(data[0].ExtId, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	cat = getCategoryResponse.GetData().(import1.Category)
	// get eTag of the category
	eTag := client.NewApiClient().GetEtag(getCategoryResponse.GetData())
	// print the eTag
	fmt.Println("eTag: ", eTag)
	newDescription := "new description"
	category.Description = &newDescription
	category.OwnerUuid = cat.OwnerUuid
	category.ObjectType_ = cat.ObjectType_
	category.Reserved_ = map[string]interface{}{"ETag": eTag}
	// update the category
	// mp := map[string]interface{}{"ETag": eTag}

	_, err = CategoriesApiInstance.UpdateCategoryById(data[0].ExtId, category, nil)
	if err != nil {
		fmt.Println(err)
		return
	} else {
		fmt.Println("update done successfully")
	}
	// use list apis to verify that the update is successful.
	listCategoriesResponse, err = CategoriesApiInstance.ListCategories(nil, nil, &filter, nil, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	data = listCategoriesResponse.GetData().([]import1.Category)
	if len(data) != 1 {
		fmt.Println("ListCategories: Expected 1 category, but got ", len(data))
	} else {
		// check if the description is updated
		if *data[0].Description != newDescription {
			fmt.Println("ListCategories: Expected description: ", newDescription, " but got: ", *data[0].Description)
		} else {
			fmt.Println("ListCategories: Category updated successfully!")
		}
	}

	// use get apis to verify that the update is successful
	getCategoryResponse, err = CategoriesApiInstance.GetCategoryById(data[0].ExtId, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	cat = getCategoryResponse.GetData().(import1.Category)
	// check if the description is updated
	if *cat.Description != newDescription {
		fmt.Println("GetCategoryById: Expected description: ", newDescription, " but got: ", *cat.Description)
	} else {
		fmt.Println("GetCategoryById: Category updated successfully!")
	}

	// use the delete api to delete the category
	_, err = CategoriesApiInstance.DeleteCategoryById(data[0].ExtId, nil)
	if err != nil {
		fmt.Println(err)
		return
	}

	// use the get api to verify that the category is deleted and validate the response code is 404
	_, err = CategoriesApiInstance.GetCategoryById(data[0].ExtId, nil, nil)
	if err != nil {
		code := getErrorCode(err)
		if code != "CTGRS-50006" {
			fmt.Println("GetCategoryById: Expected error code: CTGRS-50006, but got: ", code)
		} else {
			fmt.Println("GetCategoryById: Category deleted successfully!")
		}
	} else {
		fmt.Println("GetCategoryById: Expected error: Category not found, but got none")
	}

	// use delete api to verify that the category is already deleted and validate the response code is 404
	_, err = CategoriesApiInstance.DeleteCategoryById(data[0].ExtId, nil)
	if err != nil {
		code := getErrorCode(err)
		if code != "CTGRS-50006" {
			fmt.Println("DeleteCategoryById: Expected error code: CTGRS-50006, but got: ", code)
		} else {
			fmt.Println("DeleteCategoryById: Category already deleted!")
		}
	} else {
		fmt.Println("DeleteCategoryById: Expected error: Category not found, but got none")
	}

	// use the list api to verify that the category is deleted
	listCategoriesResponse, err = CategoriesApiInstance.ListCategories(nil, nil, &filter, nil, nil, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	if listCategoriesResponse.GetData() == nil {
		fmt.Println("ListCategories: Category deleted successfully!")
	} else {
		fmt.Println("ListCategories: Expected nil category, but got ", listCategoriesResponse.GetData())
	}

}
