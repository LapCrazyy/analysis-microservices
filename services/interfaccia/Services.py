
'''
    entry of services: (PIPELINE)
        service = {
            'imageId':  (idOfImage),  
            'namecontainer': (name of the service)
            'command': (all commands service neeed)
            'env':  (all envs needed by the service)
            'order':(int, rappresenting the order of execution of the service ascending) service with same order can parallelize execution
        }
'''
class Services:
    def __init__(self):
        self.services = []

    def add(self,imageId, namecontainer,order, command=[],env={}):
        if any(service['namecontainer'] == namecontainer for service in self.services): #no duplicated containers names
            raise Exception(f"Container name '{namecontainer}' già presente nella lista dei servizi.")
        
        service = {
            'imageId': imageId,  
            'namecontainer': namecontainer,
            'command': command,
            'env': env,  #will be linked by enviroment  maybe try with a list for docker creation
            'order':order
        }
        self.services.append(service)
    
    #override envs
    def addEnvs(self, namecontainer, env={}):
        for service in self.services:
            if service['namecontainer'] == namecontainer:
                service['env']=env
                return True
        return False
    
    #override commands
    def addCommands(self, namecontainer, commands=[]):
        for service in self.services:
            if service['namecontainer'] == namecontainer:
                service['command']=commands
                return True
        return False
    
    def remove(self, namecontainer):    #remove namecontainer associated service from services
        for service in self.services:
            if service['namecontainer'] == namecontainer:
                self.services.remove(service)
                return True
        return False
    
    def getNames(self):
        return [service['namecontainer'] for service in self.services]

    def getServicesByOrder(self, order): #get services associated to order order of execution
        finded = [service for service in self.services if service['order'] == order]
        return finded if finded else []


    def min_max_order(self):   #get range valueus of orders, min max
        if not self.services:
            raise Exception("Service contacted with an empty pipeline")

        min_order = min(service['order'] for service in self.services)
        max_order = max(service['order'] for service in self.services)
        return min_order, max_order
