class Description:
    def __init__(self,services,capabilities,
                 instances,tasks,
                 atomicTerms,groundAtomicTerms):
        self.services = services
        self.capabilities = capabilities
        self.instances = instances
        self.tasks = tasks
        self.atomicTerms = atomicTerms
        self.groundAtomicTerms = groundAtomicTerms

    def getPDDLDomain(self,domainName,requirements):
        res = "(define" + " " + "(domain" + " " \
              + domainName + ")" + "\n"
        res += getRequirements(requirements)
        res += getTypes(self.instances)
        res += getPredicates(self.atomicTerms)
        res += getActions(self.tasks)
        #res += "(:functions (total-cost))" + "\n"
        res += "\n"
        res += ")"
        return res

    def getPDDLProblem(self,domainName,problemName,goal):
        res = "(define" + " " + "(problem" + " " \
              + problemName + ")" + "\n"
        res += "(:domain" + " " + domainName + ")" + "\n"
        res += getObjects(self.instances, self.tasks)
        res += getInit(self.groundAtomicTerms, self.tasks)
        res += getGoal(goal)
        #res += "(:metric minimize (total-cost))" + "\n"
        res += "\n"
        res += ")"
        return res

    def getGroundedEffect(self, name, inp):
        for t in self.tasks:
            if t.name == name:
                addEff = list(t.addEff)
                added = []

                for a in t.addEff:
                    temp = a.strip().split(":")[1]
                    if temp == "true" or temp == "false":
                        added.append(a)
                i = 0
                for p in t.params:
                    p = p.strip().split(" - ")[1]
                    for a in t.addEff:
                        temp = a.strip().split(":")
                        if p == temp[1]:
                            added.append(temp[0] + ":" + inp[i])
                    i += 1

                added2 = []
                for a in added:
                    if not("." in a):
                        added2.append(a)
                        
                i = 0
                for p in t.params:
                    p = p.strip().split(" - ")[1]
                    for a in added:
                        if "." in a:
                            temp = a.strip().split(".")
                            if p == temp[0]:
                                added2.append(inp[i] + "." + temp[1])
                    i += 1
                    
                delEff = list(t.delEff)
                deleted = []

                for a in t.delEff:
                    temp = a.strip().split(":")[1]
                    if temp == "true" or temp == "false":
                        deleted.append(a)
                i = 0
                for p in t.params:
                    p = p.strip().split(" - ")[1]
                    for a in t.delEff:
                        temp = a.strip().split(":")
                        if p == temp[1]:
                            deleted.append(temp[0] + ":" + inp[i])
                    i += 1

                deleted2 = []
                for a in deleted:
                    if not("." in a):
                        deleted2.append(a)
                        
                i = 0
                for p in t.params:
                    p = p.strip().split(" - ")[1]
                    for a in deleted:
                        if "." in a:
                            temp = a.strip().split(".")
                            if p == temp[0]:
                                deleted2.append(inp[i] + "." + temp[1])
                    i += 1

                return dict(added = added2, deleted = deleted2)
                
                        
class Task:
    def __init__(self, name, params,\
                 posPrec, negPrec, addEff,\
                 delEff,providedBy, capability, cost):
        self.name = name             #"move"
        self.params = params         #["Location - from", "Location - to"]
        self.posPrec = posPrec       #["o.at:from"]
        self.negPrec = negPrec       #["at:to"]
        self.addEff = addEff
        self.delEff = delEff
        self.providedBy = providedBy  # "rb1"
        self.capability = capability  # "movement"
        self.cost = cost

    def getGroundedEffect(self, inp):
        
        addEff = list(self.addEff)
        added = []

        for a in self.addEff:
            temp = a.strip().split(":")[1]
            if temp == "true" or temp == "false":
                added.append(a)
        i = 0
        for p in self.params:
            p = p.strip().split(" - ")[1]
            for a in self.addEff:
                temp = a.strip().split(":")
                if p == temp[1]:
                    added.append(temp[0] + ":" + inp[i])
            i += 1

        added2 = []
        for a in added:
            if not("." in a):
                added2.append(a)
                
        i = 0
        for p in self.params:
            p = p.strip().split(" - ")[1]
            for a in added:
                if "." in a:
                    temp = a.strip().split(".")
                    if p == temp[0]:
                        added2.append(inp[i] + "." + temp[1])
            i += 1
            
        delEff = list(self.delEff)
        deleted = []

        for a in self.delEff:
            temp = a.strip().split(":")[1]
            if temp == "true" or temp == "false":
                deleted.append(a)
        i = 0
        for p in self.params:
            p = p.strip().split(" - ")[1]
            for a in self.delEff:
                temp = a.strip().split(":")
                if p == temp[1]:
                    deleted.append(temp[0] + ":" + inp[i])
            i += 1

        deleted2 = []
        for a in deleted:
            if not("." in a):
                deleted2.append(a)
                
        i = 0
        for p in self.params:
            p = p.strip().split(" - ")[1]
            for a in deleted:
                if "." in a:
                    temp = a.strip().split(".")
                    if p == temp[0]:
                        deleted2.append(inp[i] + "." + temp[1])
            i += 1

        return dict(added = added2, deleted = deleted2)

            

class groundAtomicTerm:
    def __init__(self, name, inp, out):
        self.name = name    #"at"
        self.inp = inp      #"s"
        self.out = out      #"l"

class atomicTerm:
    def __init__(self, name, inp, out):
        self.name = name    #"at"
        self.inp = inp      #"s - Service"
        self.out = out      #"l - Location"

def getInit(groundAtomicTerms, tasks):
    res = "(:init \n"
    
    for t in tasks:
        res += "(provides" + " " + \
               t.providedBy + \
               " " + t.capability + ")\n"
        
    for a in groundAtomicTerms:
        if a.out == None:
            continue
        res += "(" + a.name + " " + a.inp + " " + a.out + ")\n"

    #res += "(= (total-cost) 0)" + "\n"
    res += ")\n"
    return res

def getGoal(goal):
    res = "(:goal \n"
    res += "(and \n"
    for a in goal:
        res += "(" + a.name + " " + a.inp + " " + a.out + ")\n"

    res += ")\n"
    res += ")\n"
    return res

def getObjects(instances, tasks):  #{"Object":["ball","box"]}
    res = "(:objects \n"
    
    for k in instances:
        for v in instances[k]:
            res += v + " - " + k + "\n"

    capabilities = []
    for t in tasks:
        if t.capability in capabilities:
            continue
        res += t.capability + " - " + "Capability" + "\n"
        capabilities.append(t.capability)

    services = []
    for t in tasks:
        if t.providedBy in services:
            continue
        res += t.providedBy + " - " + "Service" + "\n"
        services.append(t.providedBy)
        
    res += ")\n"

    return res

def getTypes(instances):
    res = "(:types \nService - Thing\nCapability\n"

    for k in instances:
        if k == "Object":
            res += k + " - " + "Thing" + "\n"
            continue
        res += k + "\n"

    res += ")\n"

    return res
        
def getFormula(f):
    res = ""
    for p in f:
        l = p.strip().split(":")
        if "." in l[0]:
            s = l[0].strip().split(".")
            res += "(" + s[1] +  " " + "?" + s[0] + " " + "?" + l[1] + ")" + " "
            continue
        res += "(" + l[0] +  " " + "?srv" + " " + "?" + l[1] + ")" + " "
    res = res.replace("?true","true")
    res = res.replace("?false","false")
    return res

def getNegativeFormula(f):
    res = ""
    for p in f:
        l = p.strip().split(":")
        if "." in l[0]:
            s = l[0].strip().split(".")
            res += "(not(" + s[1] +  " " + "?" + s[0] + " " + "?" + l[1] + "))" + " "
            continue
        res += "(not(" + l[0] +  " " + "?srv" + " " + "?" + l[1] + "))" + " "
    res = res.replace("?true","true")
    res = res.replace("?false","false")
    return res

def getActions(tasks):
    res = ""
    names = []
    for t in tasks:
        if t.name in names:
            continue
        names.append(t.name)
        
        params = ":parameters (?srv - " + "Service"
        for p in t.params:
            params += " " + "?" + \
                      p.strip().split(" - ")[1] + " - " + \
                      p.strip().split(" - ")[0]
        params += ")\n"
        prec = ":precondition (and (provides ?srv " + t.capability + ")" + " "
        prec += getFormula(t.posPrec)
        prec += getNegativeFormula(t.negPrec)
        prec += ")" + "\n"

        eff = ":effect (and "
        eff += getFormula(t.addEff)
        eff += getNegativeFormula(t.delEff)
        #eff += "(increase (total-cost)" + " " + str(t.cost) + ")"
        eff += ")" + "\n"
        res += "(:action" + " " + t.name + "\n" + params + prec + eff + ")\n"
    return res
      
def getPredicates(atomicTerms):
    res = "(:predicates \n" + \
          "(provides ?srv - Service ?c - Capability) \n"

    names = []
    for a in atomicTerms:
        if a.name in names:
            continue
        names.append(a.name)
        inp = "?" + a.inp.strip().replace(":", " - ")
        out = "?" + a.out.strip().replace(":", " - ")
        s = "(" + a.name + " " + \
            inp + " " + out + ")" + "\n"
        res += s
        
    res += ")\n"
    return res


def getRequirements(requirements):
    res =  "(:requirements"
    for r in requirements:
        res += " " + ":" + r
    res += ")\n"
    return res     
