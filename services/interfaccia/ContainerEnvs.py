class ContainerEnvs:
    def __init__(self):
        self.mapping = {}

    def add(self, namecontainer, envs, commands):
        if not envs and not commands:
            raise ValueError("Environment variables and commands are empty, fill at least one.")
        if namecontainer in self.mapping:
            raise Exception(f"Container name '{namecontainer}' already exists in the list of services.")
        self.mapping[namecontainer] = {"envs": envs, "commands": commands}

    def remove(self, namecontainer):
        if namecontainer in self.mapping:
            del self.mapping[namecontainer]
            return True
        return False

    def getNames(self):
        return list(self.mapping.keys())

    def get_envs_and_commands_of(self, namecontainer):
        if namecontainer in self.mapping:
            container_data = self.mapping.get(namecontainer)
            envs = container_data.get("envs", {})
            commands = container_data.get("commands", [])
            return envs, commands
        else:
            return {}, []

    def clone(self):
        cloned_container_envs = ContainerEnvs()
        for namecontainer, data in self.mapping.items():
            envs = data.get("envs", {})
            commands = data.get("commands", [])
            cloned_container_envs.add(namecontainer, dict(envs), list(commands))
        return cloned_container_envs
