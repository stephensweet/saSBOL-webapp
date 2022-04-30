import xml.dom.minidom as xmlmdom

def getSequence(filename):
    doc = xmlmdom.parse(filename)


    sequences = doc.getElementsByTagName("sbol:Sequence")
    seqDict = {}
    for elem in sequences:
        sequence = elem.getElementsByTagName("sbol:elements")
        name = elem.getElementsByTagName("sbol:displayId")
        # this loop will only run once, essentially just to unpack sequence
        for i in sequence:
            seq = i.firstChild.data
            # print(seq.data)

        # this loop will only run once, essentially just to unpack name
        for i in name:
            n = i.firstChild.data
        n = n.split('_')
        n = '_'.join(n[0:-1])
        seqDict[n] = seq

    
    componentDefs = doc.getElementsByTagName("sbol:ComponentDefinition")
    ordDict = {}
    for elem in componentDefs:
        components = elem.getElementsByTagName("sbol:component")
        for component in components:
            if (component.getElementsByTagName("sbol:displayId") != []):
                for name in component.getElementsByTagName("sbol:displayId"):
                    # print(name.firstChild.data)
                    ID = name.firstChild.data
                    splitID = ID.split('_')
                    n = '_'.join(splitID[0:-1])
                    IDnum = int(splitID[-1])
                    #compOrder += [IDnum]
                    ordDict[n] = IDnum
                    #print(IDnum)

    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # GET TYPES --> CODE AFTER "SO:"

    typeDict = {}
    for elem in componentDefs:
        names = elem.getElementsByTagName("sbol:displayId")
        if (names != []):
            name = names[0].firstChild.data
            for typeStr in elem.getElementsByTagName("sbol:role"):
                #print("3"*40)
                typeCode = typeStr.getAttribute("rdf:resource")
                if "/so/SO:" in typeCode:
                    splitCode = typeCode.split(':')
                    code = splitCode[-1]
                    print(code)
                    print(name)
                    if code != "0000110":
                        typeDict[name] = code
                    break

    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------
    

    #print(typelist)
    seqArray = []
    names = []
    compOrder = []
    types = []
    for key in seqDict:
        # names: out-of-order list of displayIDs
        # seqArray: out-of-order list of nuc. seqs.
        # compOrder: indicates the correct order for seqArrays and names
        # types: out-of-order list of types
        seqArray += [seqDict[key]]
        names += [key]
        compOrder += [ordDict[key]]
        types += [typeDict[key]]

    if len(compOrder) != len(seqArray):
        print("Not all components have sequences assigned")
        return ([],[],[])
    # print(compOrder)
    # print(seqArray)

    # to sort in order of compOrder, combine the lists into tuples
    tupListSeq = [(compOrder[i], seqArray[i]) for i in range(len(compOrder))]
    tupListName = [(compOrder[i], names[i]) for i in range(len(compOrder))]
    tupListType = [(compOrder[i], types[i]) for i in range(len(compOrder))]

    # here, we sort using my_order as the expected order, compOrder as the current
    my_order = [i+1 for i in range(len(compOrder))]
    tupListSeq = sorted(tupListSeq,key=lambda i: my_order.index(i[0]))
    tupListName = sorted(tupListName,key=lambda i: my_order.index(i[0]))
    tupListType = sorted(tupListType,key=lambda i: my_order.index(i[0]))
    
    # in-order lists for seqs, names, and types
    seqArray = [i for (_,i) in tupListSeq]
    names = [i for (_,i) in tupListName]
    types = [i for (_,i) in tupListType]


    return seqArray,types,names
    


if __name__ == "__main__":
    filename = "FullCirc.xml"
    out = getSequence(filename)
    # print (out)