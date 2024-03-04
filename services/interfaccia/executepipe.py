#function to run pipeline
from DockerManager import DockerManager

def executePipeline(services, network, dockermanager):
    #execute pipeline, pipe order is given by presorting on order field
    minim, maxim = services.min_max_order()
    for order in range(minim, maxim+1):
        serviceToStart = services.getServicesByOrder(order)
        if len(serviceToStart)==0:
            continue  #nothing to execute at this order
        if len(serviceToStart)==1: #normal start
            #IF SERVICE CRASH executed is not False
            executed=dockermanager.run_python_container(serviceToStart[0]['imageId'], serviceToStart[0]['namecontainer'], command=serviceToStart[0]['command'],environment=serviceToStart[0]['env'],network=network)
            if not executed: 
                raise Exception(f"Errore while executing {serviceToStart[0]['namecontainer']}")
            continue   #executed, next order
        #have containers to run simtaniusly
        parallelizedContainers = []
        #IF SERVICE CRASH executed is not False
        for service in serviceToStart: #pass parallelize=True
            parallelizedContainers.append(dockermanager.run_python_container(service['imageId'], service['namecontainer'], command=service['command'],environment=service['env'],network=network,parallelize=True))
        for container in parallelizedContainers:    #wait all and check all...
            executed = DockerManager.wait_check_remove_container(container)
            if not executed:
                raise Exception(f"Errore while executing {service['namecontainer']}")
