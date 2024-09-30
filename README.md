# Category SDK Exercise

## Overview

This exercise focuses on using category SDKs in three programming languages: Java, Go, and Python. The goal is to perform basic CRUD (Create, Read, Update, Delete) operations on categories, handling errors and verifying API responses.

## Problem Statement

The script will perform the following steps using the SDK's methods:

1. **Create a Category**:
   - Create a category with the key: `key-{random-uuid}` and value: `value-{random-uuid}`.
   - Extract the `extId` from the response.

2. **Attempt Duplicate Creation**:
   - Try to create the same category again.
   - Verify that the error message indicates a duplicate entry and that the error code is appropriate for the scenario.

3. **List Category with OData Filter**:
   - Use the list API with `$filter` to search for the created category using the key and value fields in the OData filter.
   - Ensure the response contains exactly one entry matching the created category.
   - Verify that the `extId` of the list API output matches the `extId` from the create API response.

4. **Update Category**:
   - Use the PUT API to update the description of the category.

5. **Verify Update**:
   - Use both the GET and LIST APIs to confirm that the update was successful.

6. **Delete Category**:
   - Delete the category using the DELETE API.

7. **Verify Deletion**:
   - Confirm that subsequent GET, PUT, and DELETE API invocations produce a 404 error.
   - Check that the LIST API with key and value OData filters returns no results.
