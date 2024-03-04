from dotenv import load_dotenv
import os
from Services import Services
from ContainerEnvs import ContainerEnvs

#singleton
class EnviromentLoader:
    _instance = None

    def __new__(cls, sharedFilePath):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sharedFilePath = sharedFilePath
            cls._instance.container_envs = ContainerEnvs()
            cls._instance.load_pipe_environment()
            cls._instance.load_minio_environment()
        return cls._instance

    def addEnvMapping(self, namecontainer, envs, command):
        self.container_envs.add(namecontainer, envs, command)

    def rmEvnMapping(self, namecontainer):
        return self.container_envs.remove(namecontainer)

    def get_container_envs(self):
        return self.container_envs.clone()

    def load_pipe_environment(self):
        #loading from env file on shared volume does not work
        load_dotenv(dotenv_path=os.path.join(self.sharedFilePath, 'pipeline.env'))

        self.requiredAnalysis = os.getenv('analyze', 'n')
        self.testC = "n"
        self.testLogit = "n"
        if self.requiredAnalysis == "all":
            self.testC = "y"
            self.testLogit = "y"
        elif self.requiredAnalysis == "logit":
            self.testLogit = "y"
        elif self.requiredAnalysis == "classificator":
            self.testC = "y"

        self.uploadData = os.getenv('upData', 'n')
        self.resetDb = os.getenv('resetData', 'n')
        self.convert = os.getenv('convert', 'n')
        self.nHbB = int(os.getenv('t_before_bed', 12))
        self.exclude_y = os.getenv('exclude_y', 'n')
        self.tG = os.getenv('ganTrain', 'n')
        self.gan_epochs = int(os.getenv('numEpochs_G', 200))
        self.aug = os.getenv('augmentation', 'n')
        self.n_samples = int(os.getenv('numSamples', 2000))
        self.asRealPerc = float(os.getenv('as_real_percentage', 0.1))
        self.tC = os.getenv('classificatorTrain', "n")
        self.c_epochs = int(os.getenv('numEpochs_C', 100))
        self.tL = os.getenv('logitTrain', "n")
        self.class_margin = float(os.getenv("class_margin", 28))


    def load_minio_environment(self):
        #loading from env file on shared volume does not work
        load_dotenv(dotenv_path=os.path.join(self.sharedFilePath, 'minio.env'))
        self.access_key = os.environ.get('MINIO_ROOT_USER', "ste")
        self.secret_key = os.environ.get('MINIO_ROOT_PASSWORD', "steflois")
        self.endpoint_url = os.environ.get('MINIO_SERVER_ADDRESS', 'http://minio:9000')
        self.minio = {
            'MINIO_ROOT_USER': self.access_key,
            'MINIO_ROOT_PASSWORD': self.secret_key,
            'MINIO_SERVER_ADDRESS': self.endpoint_url
        }

    def check_default(self):
        default_values = {
            'uploadData': 'n',
            'resetDb': 'n',
            'convert': 'n',
            'tG': 'n',
            'aug': 'n',
            'requiredAnalysis': 'n',
            'tC': 'n',
            'tL': 'n',
        }
        for key, value in default_values.items():
            if getattr(self, key) != value:
                return
        raise Exception("given pipeline is empty!")


    @staticmethod
    def link_envs_command(container_envs, services):    #link envs and command to the Service that need them
        namesService = services.getNames()
        if len(namesService) == 0:
            raise Exception("services is na empty collection of service, no link")
        envsContainerNames = container_envs.getNames()
        if len(envsContainerNames) == 0:
            return services  
        for containerNameEnvs in envsContainerNames:  
            if all(names not in containerNameEnvs for names in namesService):
                raise Exception(f"Envs and Services are not joinable, names must match, \nServices_name: {services.getNames()}\nenvs mapping to Service_name:{container_envs.getNames()}")
            else:
                envs, commands = container_envs.get_envs_and_commands_of(containerNameEnvs)
                services.addEnvs(containerNameEnvs, envs)  
                services.addCommands(containerNameEnvs, commands)
        return services
