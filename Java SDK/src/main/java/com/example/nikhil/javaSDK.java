package com.example.nikhil;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.nutanix.dp1.pri.prism.v4.config.*;
import com.nutanix.pri.java.client.ApiClient;
import com.nutanix.pri.java.client.api.CategoriesApi;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;

import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Objects;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import static java.lang.System.exit;


@Component
@Slf4j
public class javaSDK {
    public javaSDK() {
        log.info("javaSDK instance created");
    }

    public void runSDK() throws KeyStoreException, NoSuchAlgorithmException {
        ApiClient client = getApiClient();
        log.info("Client configured successfully");
        CategoriesApi categoriesApi = new CategoriesApi(client);
        log.info("CategoriesApi instance created");
        String key = "key-";
        String value = "value-";
        // append random uuid to key and value
        key += java.util.UUID.randomUUID().toString();
        value += java.util.UUID.randomUUID().toString();
        log.info("key: {}, value: {}", key, value);
        String description = "description";
        CreateCategoryApiResponse response = CreateCategory(categoriesApi, key, description, value);
        log.info(response.getData().toString());
        Category category = (Category) response.getData();
        log.info("category:extId:create:{}", category.getExtId());
        String extId = response.getMetadata().getLinks().get(0).getHref().split("/")[8];

        log.info("extId: {}", extId);

        // try to again create the same category
        try {
            CreateCategory(categoriesApi, key, description, value);
            log.error("CreateCategory: Expected error: Category already exists, but got none");
        } catch (RestClientException e) {
            log.error("Category already exists: {}", e.getMessage());
            String errorCode = getErrorCode(e.getMessage());
            if (!errorCode.equals("CTGRS-50023")) {
                log.error("Expected error code: CTGRS-50023, but got {}", errorCode);
                exit(1);
            }
        }
        // use the list api with $filter to search for the category just created, with key and value fields in the odata filter.
        ListCategoriesApiResponse response1 = ListCategories(categoriesApi, String.format("key eq '%s' and value eq '%s'", key, value));
        log.info("No. of categories returned: {}", ((ArrayList<?>) response1.getData()).size());
        // check if there is only one category returned
        if (((ArrayList<?>) response1.getData()).size() != 1) {
            log.error("Expected 1 category, but got {}", ((ArrayList<?>) response1.getData()).size());
            exit(1);
        }
        // print the ext_id of the category returned
        String extId1 = ((Category) ((ArrayList<?>) response1.getData()).get(0)).getExtId();
        if (!extId.equals(extId1)) {
            log.error("Expected extId: {}, but got {}", extId, extId1);
            exit(1);
        }
        // use the get api to get the category by ext_id
        GetCategoryApiResponse response2 = GetCategoryById(categoriesApi, extId);
        //  print the response headers
        String etag = ApiClient.getEtag(response2.getData());
        log.info("eTag: {}", etag);
//        log.info("Client response headers: {}", categoriesApi.getApiClient().getResponseHeaders());
//
//        log.info("eTag: {}", eTag);
        // use the put api to update the description of the category.
        String newDescription = "new description";
        UpdateCategoryApiResponse response3 = UpdateCategory(categoriesApi, extId, key, newDescription, value, etag);
//        log.info("Category updated: {}", response3.getData().toString());
//        // use list apis to verify that the update is successful.
        ListCategoriesApiResponse response4 = ListCategories(categoriesApi, String.format("key eq '%s' and value eq '%s'", key, value));
        if (((ArrayList<?>) response4.getData()).size() != 1) {
            log.error("Update failed. Expected 1 category, but got {}", ((ArrayList<?>) response4.getData()).size());
            exit(1);
        }
        // get the description of the category returned
        String description1 = ((Category) ((ArrayList<?>) response4.getData()).get(0)).getDescription();
        if (!newDescription.equals(description1)) {
            log.error("Expected description: {}, but got {}", newDescription, description1);
            exit(1);
        }
        // use get apis to verify that the update is successful
        GetCategoryApiResponse response5 = GetCategoryById(categoriesApi, extId);
        // get the description of the category returned
        String description2 = ((Category) response5.getData()).getDescription();
        if (!newDescription.equals(description2)) {
            log.error("Expected description: {}, but got {}", newDescription, description2);
            exit(1);
        }

        // use the delete api to delete the category
        try {
            DeleteCategory(categoriesApi, extId);
        } catch (Exception e) {
            log.error("Category not deleted: {}", e.getMessage());
        }

        // use the get api to verify that the category is deleted and validate the response code is 404
        try {
            GetCategoryById(categoriesApi, extId);
        } catch (RestClientException e) {
            // check if the response code is 404
            String errorCode = getErrorCode(e.getMessage());
            if (!errorCode.equals("CTGRS-50006")) {
                log.error("Expected error code: CTGRS-50006, but got {}", errorCode);
                exit(1);
            } else {
                log.info("GetCategoryById: Category already deleted!");
            }
        }


        // use delete api to verify that the category is already deleted and validate the response code is 404
        try {
            DeleteCategory(categoriesApi, extId);
        } catch (RestClientException e) {
            // check if the response code is 404
            String errorCode = getErrorCode(e.getMessage());
            if (!errorCode.equals("CTGRS-50006")) {
                log.error("Expected error code: CTGRS-50006, but got {}", errorCode);
                exit(1);
            } else {
                log.info("DeleteCategory: Category already deleted!");
            }
        }

        // use the list api to verify that the category is deleted
        ListCategoriesApiResponse response8 = ListCategories(categoriesApi, String.format("key eq '%s' and value eq '%s'", key, value));
        if (response8.getData() != null) {
            log.error("ListCategories: Category not deleted. Expected null, but got {}", response8.getData().toString());
            exit(1);
        } else {
            log.info("ListCategories: Category already deleted!");
        }


        exit(0);
    }

    private DeleteCategoryApiResponse DeleteCategory(CategoriesApi categoriesApi, String extId) {
        DeleteCategoryApiResponse deleteCategoryApiResponse = categoriesApi.deleteCategoryById(extId);
        log.info("Category deleted: {}", deleteCategoryApiResponse.getData().toString());
        return deleteCategoryApiResponse;
    }

    private UpdateCategoryApiResponse UpdateCategory(CategoriesApi categoriesApi, String extId, String key, String description, String value, String eTag) {
        Category cat = new Category();
        cat.setKey(key);
        cat.setDescription(description);
        cat.setValue(value);
        cat.setOwnerUuid("00000000-0000-0000-0000-000000000000");
        java.util.Map<String, Object> headers = new java.util.HashMap<>();
        headers.put("If-Match", eTag);
        UpdateCategoryApiResponse updateCategoryApiResponse = categoriesApi.updateCategoryById(extId, cat, headers);
        log.info("Category updated: {}", updateCategoryApiResponse.getData().toString());
        return updateCategoryApiResponse;
    }

    private static CreateCategoryApiResponse CreateCategory(CategoriesApi categoriesApi, String key, String description, String value) {
        Category cat = new Category();
        cat.setKey(key);
        cat.setDescription(description);
        cat.setValue(value);
        CreateCategoryApiResponse createCategoryApiResponse = null;
        createCategoryApiResponse = categoriesApi.createCategory(cat);
        log.info("Category created: {}", createCategoryApiResponse.getData().toString());
        return createCategoryApiResponse;
    }

    private static GetCategoryApiResponse GetCategoryById(CategoriesApi categoriesApi, String ext_id) {
        GetCategoryApiResponse getCategoryApiResponse = categoriesApi.getCategoryById(ext_id, null);
        log.info("Category: {}", getCategoryApiResponse.getData().toString());
        return getCategoryApiResponse;
    }

    private static ListCategoriesApiResponse ListCategories(CategoriesApi categoriesApi, String filter) {

        ListCategoriesApiResponse listCategoriesApiResponse = categoriesApi.listCategories(null, null, filter, null, null, null);
        if (listCategoriesApiResponse.getData() != null) {
            log.info("Categories: {}", listCategoriesApiResponse.getData().toString());
        } else {
            log.info("No categories found");
        }
        return listCategoriesApiResponse;
    }

    private static ApiClient getApiClient() throws KeyStoreException, NoSuchAlgorithmException {
        ApiClient client = new ApiClient();
        client.setHost("10.15.4.38"); // IPv4/IPv6 address or FQDN of the cluster
        client.setPort(9440); // Port to which to connect to
        client.setUsername("admin"); // UserName to connect to the cluster
        client.setPassword("Nutanix.123"); // Password to connect to the cluster
        client.setMaxRetryAttempts(5); // Max retry attempts while reconnecting on a loss of connection
        client.setRetryInterval(5000); // Interval in ms to use during retry attempts
        client.setVerifySsl(false); // Set to true to verify SSL certificates
        client.setDebugging(false);
        return client;
    }

    private static String getErrorCode(String error) {
        String jsonPart = Objects.requireNonNull(error).split(": ", 2)[1]; // Split only on the first occurrence
        // in the error e find the key "code" and print the value of the key
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode rootNode = objectMapper.readTree(jsonPart);
            JsonNode errorArray = rootNode.get(0).get("error");
            String code = errorArray.get(0).get("code").asText();
            return code;
        } catch (JsonProcessingException ex) {
            throw new RuntimeException(ex);
        }
    }


}
