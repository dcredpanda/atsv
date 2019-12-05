import pymongo
import docker

# docker_client = docker.from_env()
# docker_
#
# # container = docker_client.containers.get()
#
# # vars( container )["attrs"]["NetworkSettings"]["Networks"]["<NETWORK_NAME>"]["IPAddress"]
#
# print(docker_client)
# # print(container)

myclient = pymongo.MongoClient("mongdb://192.168.99.101:2376")

mydb = myclient["mydatabase"]