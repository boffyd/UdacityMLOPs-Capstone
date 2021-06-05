# Run the swagger-ui project locally, requires docker to be installed and running
# Will pull the latest swagger-ui docker image and then will try to run it on port 9000
#
# Once running, it is accessible at: http://localhost:9000/
# In the local directory, you need to download the swaggeruri (swagger.json) file so that the uri can call it
# This file is accessed in the azure endpoints, model depoly Swagger Uri and is downloaded to the swagger directory
# running serve.py allows the ui to access the local directory
# to run these files in terminal (gitbash) you need to 
# run bash swagger.sh and python serve.py
# Once running in swagger, change to http://localhost:8000/swagger.json
#
# If the user doesn't have enough permissions to use port 80, modify the local
# port to something above 8000 that is available.

docker pull swaggerapi/swagger-ui
docker run -p 9000:8080 swaggerapi/swagger-ui
