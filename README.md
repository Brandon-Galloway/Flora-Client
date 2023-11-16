# Flora Client
![Last Commit](https://img.shields.io/github/last-commit/Brandon-Galloway/Flora-Client/master)
![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![AWSIoTPythonSDK](https://img.shields.io/badge/AWSIoTPythonSDK-v1.5.2-orange.svg)

## Overview
The Flora Client is an AWS IoT client to enable the measurement and submission of sensor data to the [Flora Backend](https://github.com/Brandon-Galloway/Flora).

<details closed>
<summary> Future Enhancements </summary>  

- Automatic client registration
- Multichannel MQTT distribution
- OTA update capability
- Device configuration settings (e.g. C/F temperature settings)
</details>

## GPIO Configuration
Attach an Adafruit [Soil Sensor](https://www.adafruit.com/product/4026), [Atmospheric Sensor](https://www.adafruit.com/product/3251), and [Light Sensor](https://www.adafruit.com/product/1980) to your pi's I2C interface. Verify each sensor individually utilizing the Adafruit documentation before proceeding with setup.

## Installation

### Clone Project
```shell
git clone https://github.com/Brandon-Galloway/Flora-Client.git
```

### Install Dependencies
```shell
pip install -r requirements.txt
```

### Populate Certificates
Navigate to [AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html) and then to:

> Manage -> All devices -> Things  

Select "Create Things" and proceed to create a new thing, selecting "Auto-generate a new certificate" and attaching the "Flora_Policy" previously configured during [backend](https://github.com/Brandon-Galloway/Flora) deployment.

When prompted, download the supplied private key, public key, certificate, and AmazonRootCA1 files provided and place them in a /certs directory below the project root with the names AmazonRootCA1.pem, cert.pem, private.key, and public.key

### Configuration
Create a config.ini file in the project root following the below format:
```
[aws]
iot_endpoint = 
thing_name = 

[flora]
serial_number = 
```

Your AWS IoT endpoint can be found under Settings. Security policy may need to be adjusted. thing_name should be set to the above-configured thing name and serial_number can be any unique string, though the UUID V4 format is suggested.

## Scheduling
On your pi run `crontab -e` and add the entries below:
```shell
0 0 * * * echo -n > SCRIPT_DIR/output.log
*/5 * * * * /usr/bin/python3 SCRIPT_DIR/flora_client_upload.py >> SCRIPT_DIR/output.log 2>&1
```
This will schedule your pi to run the flora_client_upload script once every 5 minutes, logging the results each time and clearing the log file at midnight.

## Verification
Following these steps, your pi should now be able to run the flora client and publish data to AWS IoT. To troubleshoot issues, the client can be manually ran and verified.  
*Note the I2C interface does **NOT** support simulanious multi-connection to sensors. If two instances of the script are executed in parallel they will not complete succesfully.

## Contributors
Brandon Galloway

