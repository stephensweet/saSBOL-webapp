import xml.dom.minidom as xmlmdom
from readXML import getSequence

def writeXML(sequences, types, names):
    ###################################################################
    '''
    In this function, we want to write an XML file with all the newly
    added scars, as well as the original parts. We need to be aware of
    types for each part, as well as ideally the names.

    SBOL XML files have certain characteristics that are needed.

    if n is the number of components in the DNA region, these are reqs:
        1 moduleDefinition
        n+1 ComponentDefinition, one of which is for the DNA region
        n Sequence
        n+2 Layout, 1 for each comp, 1 for module, one for DNA region

    The DNAreg ComponentDefinition will have the following parts:
        n component
        n sequenceAnnotation
        n-1 sequenceConstraint
    '''
    ###################################################################

    # Necessary template for XML
    XMLfile = '''<?xml version="1.0" ?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:sbol="http://sbols.org/v2#" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:prov="http://www.w3.org/ns/prov#" xmlns:om="http://www.ontology-of-units-of-measure.org/resource/om-2/" xmlns:SBOLCanvas="https://sbolcanvas.org/">
{0}
</rdf:RDF>
'''
    # 0 = All of the components/sequences/module def

    # ModuleDefinition Sample string:
    ModuleDefinition = '''  <sbol:ModuleDefinition rdf:about="https://sbolcanvas.org/{0}">
    <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}"/>
    <sbol:displayId>{0}</sbol:displayId>
    <sbol:functionalComponent>
      <sbol:FunctionalComponent rdf:about="https://sbolcanvas.org/{0}/{1}">
        <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}/{1}"/>
        <sbol:displayId>{1}</sbol:displayId>
        <sbol:definition rdf:resource="https://sbolcanvas.org/{1}"/>
        <sbol:access rdf:resource="http://sbols.org/v2#public"/>
        <sbol:direction rdf:resource="http://sbols.org/v2#inout"/>
      </sbol:FunctionalComponent>
    </sbol:functionalComponent>
  </sbol:ModuleDefinition>
'''
    # 0 = moduleID
    # 1 = FunctionalComponentID

    # -- Not for DNA region --
    ComponentDefinition = '''  <sbol:ComponentDefinition rdf:about="https://sbolcanvas.org/{0}">
    <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}"/>
    <sbol:displayId>{0}</sbol:displayId>
    <sbol:type rdf:resource="http://www.biopax.org/release/biopax-level3.owl#DnaRegion"/>
    <sbol:role rdf:resource="http://identifiers.org/so/SO:{1}"/>
    <sbol:sequence rdf:resource="https://sbolcanvas.org/{0}_sequence"/>
  </sbol:ComponentDefinition>
'''
    # 0 = partID
    # 1 = part code (what determines what the part is)

    # Sequence Definition
    SequenceDefinition = '''  <sbol:Sequence rdf:about="https://sbolcanvas.org/{0}_sequence">
    <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}_sequence"/>
    <sbol:displayId>{0}_sequence</sbol:displayId>
    <sbol:elements>{1}</sbol:elements>
    <sbol:encoding rdf:resource="http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html"/>
  </sbol:Sequence>
'''
    # 0 = partID
    # 1 = part nucleotide seq


    # ==================================================================================
    # ==================================================================================
    # The DNAreg componentDefinition is made with various other component subclasses
    DNAComponent = '''  <sbol:ComponentDefinition rdf:about="https://sbolcanvas.org/{0}">
    <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}"/>
    <sbol:displayId>{0}</sbol:displayId>
    <sbol:type rdf:resource="http://www.biopax.org/release/biopax-level3.owl#DnaRegion"/>
    <sbol:role rdf:resource="http://identifiers.org/so/SO:0000110"/>
{1}
  </sbol:ComponentDefinition>
'''
    # 0 = FunctionalComponentID
    # 1 = subComponents, DNAregSeqAnnos, DNAregSeqConst

    DNAregSubComponent = '''    <sbol:component>
      <sbol:Component rdf:about="https://sbolcanvas.org/{0}/{1}_{2}">
        <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}/{1}_{2}"/>
        <sbol:displayId>{1}_{2}</sbol:displayId>
        <sbol:access rdf:resource="http://sbols.org/v2#public"/>
        <sbol:definition rdf:resource="https://sbolcanvas.org/{1}"/>
      </sbol:Component>
    </sbol:component>
'''
    # 0 = FunctionalComponentID
    # 1 = partID
    # 2 = part order

    DNAregSeqAnno = '''    <sbol:sequenceAnnotation>
      <sbol:SequenceAnnotation rdf:about="https://sbolcanvas.org/{0}/{0}Annotation{1}">
        <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}/{0}Annotation{1}"/>
        <sbol:displayId>{0}Annotation{1}</sbol:displayId>
        <sbol:location>
          <sbol:Range rdf:about="https://sbolcanvas.org/{0}/{0}Annotation{1}/location7">
            <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}/{0}Annotation{1}/location7"/>
            <sbol:displayId>location{1}</sbol:displayId>
            <sbol:start>{2}</sbol:start>
            <sbol:end>{3}</sbol:end>
            <sbol:orientation rdf:resource="http://sbols.org/v2#inline"/>
          </sbol:Range>
        </sbol:location>
        <sbol:component rdf:resource="https://sbolcanvas.org/{0}/{4}_{5}"/>
      </sbol:SequenceAnnotation>
    </sbol:sequenceAnnotation>
'''
    # 0 = FunctionalComponentID
    # 1 = order number (starting at 0)
    # 2 = ((order number + 1) * 2) - 1 
    # 3 = (order number + 1) * 2
    # 4 = partID
    # 5 = order number + 1

    DNAregSeqConst = '''    <sbol:sequenceConstraint>
      <sbol:SequenceConstraint rdf:about="https://sbolcanvas.org/{0}/{0}Constraint{1}">
        <sbol:persistentIdentity rdf:resource="https://sbolcanvas.org/{0}/{0}Constraint{1}"/>
        <sbol:displayId>{0}Constraint{1}</sbol:displayId>
        <sbol:restriction rdf:resource="http://sbols.org/v2#precedes"/>
        <sbol:subject rdf:resource="https://sbolcanvas.org/{0}/{2}_{1}"/>
        <sbol:object rdf:resource="https://sbolcanvas.org/{0}/{3}_{4}"/>
      </sbol:SequenceConstraint>
    </sbol:sequenceConstraint>
'''
    # 0 = FunctionalComponentID
    # 1 = order number (starting at 1)
    # 2 = part1ID
    # 3 = part2ID
    # 4 = order number + 1

    ############################################
    '''
    DNAreg Component definition will most likely be structured like this:
        - component
        - related sequenceAnnotation
        - sequence constraint for itself and the next component (except for if it's the last part)
    '''
    ############################################

    # print(DNAComponent.format("!!!!!!",DNAregSubComponent))
    # print(ModuleDefinition+ModuleDefinition)

    ############################################
    '''
    For the writing algorithm, we need to iterate through the parts, create a componentDef,
    DNAsubCompDef, 
    '''
    ############################################

    moduleID = "module1"
    FunctionalComponentID = "id1"

    toWriteToFile = ModuleDefinition.format(moduleID,FunctionalComponentID)
    toWriteToDNAComp = ""
    
    joinedLists = [(sequences[i],types[i],names[i]) for i in range(len(names))]
    for (order,tup) in enumerate(joinedLists):
        sequence, type, partID = tup
        # print(i,sequence,type,partID)

        currCompDef = ComponentDefinition.format(partID, type)
        currSequence = SequenceDefinition.format(partID,sequence)

        currSubCompDef = DNAregSubComponent.format(FunctionalComponentID,partID,str(order+1))
        currSeqAnno = DNAregSeqAnno.format(FunctionalComponentID,str(order),str(((order + 1) * 2) - 1), str((order + 1) * 2), partID, str(order+1))
        if order < len(joinedLists)-1:
          nextPart = joinedLists[order+1][2]
          currSeqConst = DNAregSeqConst.format(FunctionalComponentID,str(order+1),partID,nextPart,str(order+2))
        else:
          currSeqConst = ""

        toWriteToFile = toWriteToFile + currCompDef + currSequence
        toWriteToDNAComp = toWriteToDNAComp + currSubCompDef + currSeqAnno + currSeqConst

    DNAComp = DNAComponent.format(FunctionalComponentID, toWriteToDNAComp)
    toWriteToFile = toWriteToFile + DNAComp

    file = XMLfile.format(toWriteToFile)

    retry = True
    addToName = ""
    count = 1
    while retry:
        try:
            with open("./DOWNLOAD_FOLDER//"+"CircuitWithScars" + addToName + ".xml", 'x') as f:
                f.write(file)

            retry = False
        except:
            addToName = "(" + str(count) + ")"
            count += 1



        
        




if __name__ == "__main__":
    s,t,n = getSequence("WithScars.xml")
    out = writeXML(s,t,n)
    print(out)