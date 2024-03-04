#CREATING SERVICES
from Services import Services


#returns list in order of declaration of the elements
def get_all_values_as_lists(dictionary, idx):
    values_as_lists = []
    for value in dictionary.values():
        for item in value:
            values_as_lists.append(item[idx])
    return values_as_lists


#DEFINITION OF IMAGES, CONTAINER NAMES, ENVS, COMMANDS AND PIPELINE ORDER
def buildServices(env, dockermanager):
    containersNameNoEnvNoCommands = {}  #add containers without envs, cmds configurations
    #image -> [[cName, ordeer, envRelated to attivation],...,[,,]]
    imageContainersWithEnvsorCommand = {
        "converter": [["converter_execution", 1,env.convert]],
        "gan": [["gantrain_execution", 2, env.tG], ["augmentation_execution", 3, env.aug]],
        "analisi": [["trainclass_execution", 5, env.tC], ["logit_calc_execution", 5, env.tL], ["analyze_logit_execution", 6, env.testLogit],
                    ["analyze_class_execution", 6, env.testC]]
    }
    #containersName --> list based on the order in imageContainersWithEnvsorCommand
    #this has to be the same of associatedEnvsCommands, ICWEC idx [0] -need-> AEC idx[0]
    containersName = get_all_values_as_lists(imageContainersWithEnvsorCommand,0)
    envs = get_all_values_as_lists(imageContainersWithEnvsorCommand,2)
    associatedEnvsCommands = [
        ({'nHoursBeforeSleep': env.nHbB, 'exclude_y': env.exclude_y, **env.minio}, ['python', '/app/Acty_Analisi_converter.py']),
        ({'numEpochs': env.gan_epochs, **env.minio}, ['python', '/app/gan_train.py']),
        ({'numSamples': env.n_samples, 'as_real_percentage': env.asRealPerc, **env.minio}, ['python', '/app/amplification_GAN_TF.py']),
        ({'numEpochs': env.c_epochs, 'class_margin': env.class_margin, **env.minio}, ['python', '/app/classificator_train.py']),
        ({'class_margin': env.class_margin, **env.minio}, ['python', '/app/Reg_Logistica.py']),
        ({'type': env.requiredAnalysis, 'class_margin': env.class_margin, **env.minio}, ['python', '/app/logit_test.py']),
        ({'type': env.requiredAnalysis, 'class_margin': env.class_margin, **env.minio}, ['python', '/app/logit_calc.py'])
    ]

    services = Services()
    i=0
    for env_params, commands in associatedEnvsCommands:
        if envs[i]!="n": #n = default conf, no
            env.addEnvMapping(containersName[i], env_params, commands) #map only when env start container != default
        i=i+1
        
    for key, value in containersNameNoEnvNoCommands.items():  #join all containers ens, cmds & no envs,cmds
        if key in imageContainersWithEnvsorCommand:
            imageContainersWithEnvsorCommand[key].extend(value)
        else:
            imageContainersWithEnvsorCommand[key] = value
    #prblema sta qua ho solo gantrain_execution
    for imageName, containers in imageContainersWithEnvsorCommand.items():  #instanciate services
        for container_info in containers:
            namecontainer, order, env = container_info
            if env != "n":
                services.add(dockermanager.get_image_id_by_name(imageName), namecontainer, order)
    return services


