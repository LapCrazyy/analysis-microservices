import docker
#singleton
class DockerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = cls._instance._connect_to_docker()
            cls._instance._image_list = cls._instance._get_available_images()
            cls._instance._networks_list = cls._instance._get_available_networks()
        return cls._instance

    def _connect_to_docker(self):
        try:
            client = docker.from_env()
            return client
        except Exception as e:
            raise Exception(f"Error while connecting to Docker:\n{str(e)}")

    def _get_available_images(self):
        try:
            images = self._client.images.list()
            return images
        except Exception as e:
            raise Exception(f"Error while retrieving images from Docker:\n{str(e)}")
    
    def _get_available_networks(self):
        try:
            networks = self._client.networks.list()
            return networks
        except Exception as e:
            raise Exception(f"Error while retrieving networks from Docker:\n{str(e)}")

    def get_image_id_by_name(self, image_name):
        image_name += ":latest"
        for image in self._image_list:
            if image_name in image.tags:
                return image.id
        raise Exception(f"Image not found: {image_name}")

    def get_network_id_by_name(self, name):
        for network in self._networks_list:
            if name == network.name:
                return network.id
        raise Exception(f"Network not found: {name}")

    @staticmethod
    def check_status(container):
        return container.attrs['State']['ExitCode'] == 0    #IF SERVICE CRASH executed is not False

    @staticmethod
    def wait_check_remove_container(container):
        container.wait()
        executed = DockerManager.check_status(container)    #IF SERVICE CRASH executed is not False
        container.remove()
        return executed


    def run_python_container(self, image, name, command=None, environment=None, network=None, parallelize=False):
        try:
            new_container = self._client.containers.create(
                image=image,
                name=name,
                command=command,
                environment=environment,
                network=network
            )
            new_container.start()
            if not parallelize:
                new_container.wait()
                executed = DockerManager.check_status(new_container)    #IF SERVICE CRASH executed is not False
                new_container.remove()
                return executed
            else:
                return new_container
        except Exception as e:
            raise Exception(f"Error while running container:\n{str(e)}")
