from alto.description import *
from alto.actorsAPI import *
import alto.context

def buildInstances(services):
    instances = {}

    for service in services:
        s_id = service["id"]
        s_attributes = service["attributes"]
        s_type = s_attributes["type"]

        if s_type not in instances:
            instances[s_type] = [s_id]
        else:
            instances[s_type].append(s_id)

    instances["Boolean"] = ["true", "false"]
    instances["State"] = ["available", "broken"]

    return instances


def findType(instances, value):
    for t in instances.keys():
        if value in instances[t]:
            return t
    return None


def buildAtomicTerms(services, instances):
    atomicTerms = []

    for service in services:
        s_id = service["id"]
        s_attributes = service["attributes"]
        s_type = s_attributes["type"]
        s_features = service["features"]

        for feature in s_features.keys():
            predicate_name = feature
            argument_1 = f"o - {s_type}"
            
            value = s_features[feature]["properties"]["value"]
            t = findType(instances, value)
            assert t is not None
            argument_2 = f"b - {t}"

            at = atomicTerm(predicate_name, argument_1, argument_2)

            if at not in atomicTerms:
                atomicTerms.append(at)

    return atomicTerms


def buildRequirements():
    requirements = []
    requirements.append("strips")
    requirements.append("equality")
    requirements.append("typing")
    return requirements


def buildGoal(target):
    goal = []

    for single_target in target:
        tokens = single_target.split(",")
        tokens_stripped = [token.strip() for token in tokens]

        gat = groundAtomicTerm(tokens_stripped[0], tokens_stripped[1], tokens_stripped[2])

        if gat not in goal:
            goal.append(gat)

    return goal


def buildPDDL(servicesAPI, domain, problem, target):
    config_json = json.load(open(target))
    target = config_json['target']

    services = [] 
    capabilities = [] 
    tasks = [] 
    groundAtomicTerms = []

    goal = buildGoal(target)
    instances = buildInstances(servicesAPI)
    atomicTerms = buildAtomicTerms(servicesAPI, instances)
    requirements = context.requirements

    subtypes_service = []

    for service in servicesAPI:
        s = service["id"]
        services.append(s)

        features = service["features"]
        attributes = service["attributes"]
        serviceType = attributes["type"]

        for f in features.keys():
            feature = features[f]
            value = feature["properties"]["value"]
            groundAtomicTerms.append(groundAtomicTerm(f,s,value))

        if "Service" in serviceType:
            subtypes_service.append(serviceType)
            actions = attributes["actions"]
            for a in actions:
                action = actions[a]
                props = action["properties"]
                featureType = props["type"]
                
                if featureType == "operation":
                    capabilities.append(a)
                    name = props["command"]
                    cost = props["cost"]
                    params = props["parameters"]
                    
                    posPrec = []
                    negPrec = []
                    addEff = []
                    delEff = []
                    try:
                        posPrec = props["requirements"]["positive"]
                    except KeyError:
                        pass
                    try:
                        negPrec = props["requirements"]["negative"]
                    except KeyError:
                        pass
                    try:
                        addEff = props["effects"]["added"]
                    except KeyError:
                        pass
                    try:
                        delEff = props["effects"]["deleted"]
                    except KeyError:
                        pass

                    providedBy = s 
                    
                    task = Task(name,
                                params,
                                posPrec,
                                negPrec,
                                addEff,
                                delEff,
                                providedBy,
                                a,
                                cost,
                                serviceType
                                )
                    tasks.append(task)
                
    desc = Description(services,capabilities,
                       instances,subtypes_service,tasks,atomicTerms,
                       groundAtomicTerms)

    domain_name = domain[:domain.rfind(".")]
    problem_name = problem[:problem.rfind(".")]

    domainFile = open(f"{domain}", 'w+')
    domainFile.write(desc.getPDDLDomain(domain_name,requirements))
    domainFile.close()

    problemFile = open(f"{problem}", 'w+')
    problemFile.write(desc.getPDDLProblem(domain_name,problem_name,goal))
    problemFile.close()

    return desc
    
if __name__ == "__main__":
    buildPDDL()             
    
