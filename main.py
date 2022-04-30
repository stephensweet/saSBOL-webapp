#driver code for our tool
#below are our imported files which perform the necessary steps to execute our functionality
import Scar_Addition
import readXML
import XMLfuncs


# assembly = ord(input("Choose assembly (BB=1, T2=2, GG=3): "))

#GET FILE(s) <input_SBOL2> <input2_SBOL2>, GET assembly 

#function to be called in views , flask webapp 

def saSBOL(filename,method):

    seq_array, part_types, part_names = readXML.getSequence("./XML_UPLOADS//"+filename)

    assembly=method

    if(assembly == 1 or assembly == 2):
    
        build_1  = Scar_Addition.assemble_part(seq_array, part_types, len(seq_array), assembly)

        build_1.check_compatability()

        if(build_1.isCompatible==False):
            raise ValueError('Illegal sequence found in design, use an alternate assembly standard')

        build_1.add_scars()
        build_1.create_part_names()

        return_seq = build_1.total_sequence
        return_part_types = build_1.return_part_type
        return_part_names = build_1.part_names

        XMLfuncs.writeXML(return_seq, return_part_types, return_part_names)

    elif (assembly == 3):

        k = input('Enter number of genes to be assembled in transcriptional unit: ')
        composite_part_array = Scar_Addition.create_composite_part_array(k, *argv)   ##argv are input_SBOL2 files

        build_2 = Scar_Addition.assemble_composite_parts(composite_part_array, k, assembly)
        build_2.add_scars()

        return_seq = build_2.total_sequence
        return_part_types = build_2.return_part_type
        return_part_names = build_2.part_names

        XMLfuncs.writeXML(return_seq, return_part_types, return_part_names)

    else:
         raise ValueError('Invalid or unsuported Assembly chosen')