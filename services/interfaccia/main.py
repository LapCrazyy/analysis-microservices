from DockerManager import DockerManager
from Enviroment import EnviromentLoader
from executepipe import executePipeline
from buildServices import buildServices
from minio_connect import connect
import os
import downloadData
import uploadData
import glob

'''
MAIN for interface service
'''

def search_files_by_patterns(directory, patterns):
    matched_files = []
    for pattern in patterns:
        matched_files.extend([os.path.basename(file) for file in glob.glob(os.path.join(directory, pattern))])
    return matched_files

shared_folder= "/datashare"
env = EnviromentLoader(os.path.join(shared_folder,"envs"))

working_dir="/app"
buckets=["data","model"]
#patterns to look for when client want to upload from shared folder
patterns=['Scoring*.xlsx', 'actigraph*.zip', 'real.csv', 'generated.csv']
#getting enviroment

#name of docker network of the containers
net_name="minio_server_minio_net"

#connection to minio  #get minio conf
minio_client = connect()

#check envs
try:
    env.check_default()
except Exception as e: #the meaning of an empty pipeline is to update shareddirectory status --> effects, the shared dir is now a copy of buckets
    if False == downloadData.download_file_by_patterns_from_buckets(minio_client, shared_folder, buckets , [""]):  #keep update shared folder on whats in minioDb
        print("download of minio db situation failed")
    raise Exception(f"No buildable pipeline from envs, downloaded MinioDB situation\n{str(e)}")

#instanciate docker manager
manager = DockerManager()
#getting network
rete=manager.get_network_id_by_name(net_name)
#load buckets on minio for 1st start.
uploadData.create_bucket(minio_client, buckets)
    
if env.uploadData!="n":  #Up data from shared folder to minio, if requested
    if uploadData.upload_files_to_minio(minio_client, shared_folder, buckets[0], search_files_by_patterns(shared_folder,patterns), remove=False)==False:
        raise Exception("Error while uploading files from shared folder, no new data avaible on minio")

#create services
services= buildServices(env,manager)

#services has now been linked to containerEnvs
services=EnviromentLoader.link_envs_command(env.get_container_envs(), services)
#execute pipeline
try:
    executePipeline(services, rete, manager) #run pipe
    
    if downloadData.download_file_by_patterns_from_buckets(minio_client, shared_folder, buckets, [""], reset=env.resetDb!="n") == False: #all obj download / download and reset buckets
        raise Exception("download/reset of minio db situation failed")
except Exception as e:
    if downloadData.download_file_by_patterns_from_buckets(minio_client, shared_folder, buckets, [""], reset=env.resetDb!="n") == False: #all obj download / download and reset buckets
         print("download/reset of minio db situation failed")
    raise Exception("error while executing pipeline\n",e)
print("pipeline executed")

 