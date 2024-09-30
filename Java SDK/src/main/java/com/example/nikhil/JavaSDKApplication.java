package com.example.nikhil;


import com.nutanix.pri.java.client.ApiClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;


@Slf4j
@SpringBootApplication
public class JavaSDKApplication {

	public static void main(String[] args) throws KeyStoreException, NoSuchAlgorithmException {
		SpringApplication.run(JavaSDKApplication.class, args);
		log.info("Application started successfully");
		// run the SDK
		javaSDK sdk = new javaSDK();
		sdk.runSDK();
	}



}