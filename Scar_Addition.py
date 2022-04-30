import numpy as np
from enum import Enum

# enumerated type for assembly standards
class assembly_standard(Enum):
    biobrick = 1  #endonuclease mediated assembly
    igem_type2s_phytobricks = 2  #typeII restriction enzyme assembly
    gg_moClo = 3   #typeII restriction enzyme assembly for larger parts made up of composite parts
    # gibson = 4   #scarless assembly
    # d_dna_synthesis = 5   #scarless assembly   ##IMPORTANT_NOTE: tool does not yet support gibson or direct DNA synthesis
    ##                                                           ## but additional standards can be added as part of a class or new one

#class for assembling individual parts into larger composite part
class assemble_part:

    #constructor (incl. exception handling for invalid inputs)
    def __init__(self, parts, part_id, arr_size, k):
        self.part_array = ['A'] * arr_size
        self.part_type = ['A'] * arr_size

        #initlialize array or parts type (pro, rbs, cds, term, etc)
        for i in range(arr_size):
            self.part_type[i] = part_id[i]

        #initialize array of part sequences
        for i in range(arr_size):
            self.part_array[i] = parts[i]

        self.standard = assembly_standard(k).name
        self.isCompatible = False

   
    #check if parts are valid for selected assembly method
    def check_compatability(self):
        if self.standard == assembly_standard(1).name:  ##check compatability with biobrick standard
            for i in range(len(self.part_array)):
                if 'GAATTC' in self.part_array[i] or 'TCTAGA' in self.part_array[i] or 'ACTAGT' in self.part_array[i] or 'CTGCAG' in self.part_array[i] or 'GCGGCCG' in self.part_array[i]:
                    self.isCompatible = False
                    break
                else: self.isCompatible = True
        if self.standard == assembly_standard(2).name:  ##check compatability with igem_typeIIs standard
            for i in range(len(self.part_array)):
                if 'GGTCTC' in self.part_array[i] or 'GAGACC' in self.part_array[i] or 'GAAGGAGC' in self.part_array[i] or 'GCTCTTC' in self.part_array[i]:
                    self.isCompatible = False
                    break
                else: self.isCompatible = True

    #create array of scars to be added in assembly of composite part
    def add_scars(self):

        if self.standard == assembly_standard(1).name:  #biobrick assembly
            scar_array = ['A'] * (len(self.part_array)+1)
            for i in range(len(self.part_array)-1):
                if self.part_array[i+1][0:2] == 'AT':  #if next part in design starts with AT different scar required
                    scar_array[i+1] = 'TACTAG'
                else:
                    scar_array[i+1] = 'TACTAGAG'
            
            scar_array[0] = 'GAATTCGCGGCCGCTTCTAGATG'  # add biobrick prefix
            
            scar_array[len(self.part_array)] = 'TACTAGTAGCGGCCGCTGCAG' #add biobrick suffix
            
            self.total_sequence = ['A'] * (len(self.part_array)+len(scar_array)) #initialize array for total seqeunece of design
            self.total_sequence[::2] = scar_array
            self.total_sequence[1::2] = self.part_array

            self.return_part_type = ['A'] * (2*(len(self.part_array))+1) #initialize array to contain part id no's (for conversion to .xml file and SBOLCanvas compatability)
            self.return_part_type[::2] = ['0001953'] * len(scar_array)     #(scar code)
            self.return_part_type[1::2] = self.part_type

        
        if self.standard == assembly_standard(2).name: #typeIIs assembly (igem standards)
            scar_array = ['A'] * (len(self.part_array)+1)
            for i in range(len(self.part_array)-1):
                if self.part_type[i] == '0000167':  #add correct fusion site based on part (following igem standards) (part id from SBOLCanvas) (promoter)
                    scar_array[i+1] = 'TACT'
                elif self.part_type[i] == '0000139':  #(rbs)
                    scar_array[i+1] = 'AATG'
                elif self.part_type[i] == '0000316':  #(cds)
                    scar_array[i+1] = 'GCTT'
                elif self.part_type[i] == '0000141':  #(term)
                    scar_array[i+1] = 'CGCT'
                else:
                    print('Error, there is an invalid part component, our tool currently supports designs of promoter, RBS, CDS, and terminators')
                    break
            
            scar_array[0] = 'GGAG'  # add prefix
            
            scar_array[len(self.part_array)] = 'CGCT' #add suffix

            self.return_part_type = ['A'] * (2*(len(self.part_array))+1) #initialize array to contain part id no's (for conversion to .xml file and SBOLCanvas compatability)
            self.return_part_type[::2] = ['0001953'] * len(scar_array)    
            self.return_part_type[1::2] = self.part_type
            
            self.total_sequence = ['A'] * (len(self.part_array)+len(scar_array))  #total sequence accurate design
            self.total_sequence[::2] = scar_array
            self.total_sequence[1::2] = self.part_array
        

    def create_part_names(self):
        self.part_names = ['A'] * len(self.return_part_type)
        self.part_names[0] = 'prefix' 
        self.part_names[len(self.return_part_type)-1] = 'suffix'

        for i in range(1, len(self.part_names)-1):  #create unique names for each part (for SBOL2 file in order to reupload back to SBOLCanvas)
            if self.return_part_type[i] == '0001953':
                self.part_names[i] = 'scar' + str(i)
            elif self.return_part_type[i] == '0000167':
                self.part_names[i] = 'prom' + str(i)
            elif self.return_part_type[i] == '0000139':
                self.part_names[i] = 'rbs' + str(i)
            elif self.return_part_type[i] == '0000316':
                self.part_names[i] = 'cds' + str(i)
            elif self.return_part_type[i] == '0000141':
                self.part_names[i] = 'term' + str(i)
            else:
                raise ValueError('unsupported part was used in design')

#class for assembling already created composite parts together into larger composite designs
class assemble_composite_parts:   

    #constructor
    def __init__(self, arr_genes, num_genes, k):

        ##check that valid standard is selected for moclo
        if k != 3:
            raise ValueError('Only the Golden Gate Modular Cloning standard and method is supported for assembling composite parts together')
        if k==3 and num_genes > 7:
            raise ValueError('Error, you can only assemble up to 7 composite parts together under GG MoClo restrictions')

        # self.part_type = ['A'] * num_genes  #array of part id numbers
        # for i in range(num_genes):            
        #     self.part_type[i] = part_id[i]

        ##array of all the composite parts
        self.genes = arr_genes   
        self.num_parts = num_genes  #num parts
        self.scar_array = ['A'] * (num_genes+1) #array of scars
        self.standard = assembly_standard(k).name
    
    def add_scars(self):

        #scar seqeunce depends of length/total number of transcriptional units being combined
        fusion_seqs_moclo = ['TGCC', 'GCAA', 'ACTA', 'TTAC', 'CAGA', 'TGTG', 'GAGC', 'TGCC'] #typeII enzyme seqeunces needed for fusion of parts

        if self.standard == assembly_standard(3).name:
            for i in range(self.num_parts+1):
                self.scar_array[i] = fusion_seqs_moclo[i]

            self.total_sequence = ['A'] * (self.num_parts+len(self.scar_array))
            self.total_sequence[::2] = self.scar_array
            self.total_sequence[1::2] = self.genes

        self.return_part_type = ['A'] * (self.num_parts+len(self.scar_array))
        self.return_part_type[::2] = ['0001953'] * len(self.scar_array)
        self.return_part_type[1::2] = ['0000804'] * len(self.genes)

 
    def create_part_names(self):
        self.part_names = ['A'] * len(self.return_part_type)
        self.part_names[0] = 'prefix' 
        self.part_names[len(self.return_part_type)-1] = 'suffix'

        for i in range(1, len(self.part_names)-1):  #create unique names for each part (for SBOL2 file in order to reupload back to SBOLCanvas)
            if self.return_part_type[i] == '0001953':
                self.part_names[i] = 'scar' + str(i)
            else:
                self.part_names[i] = 'gene_TU' + str(i)


#helper function for assemble_comp_parts class which takes in an various number of arrays of genetic transcriptional units (TU's)
#and combines them together into one array, where each index in the array is on TU. This then allows us to pass this array of 
#TUs to our assemble_comp_parts and the necessary scars are added to combine the parts into a large function unit

def create_composite_part_array(k, *argv): #*argv allows this function to take a variable number of arguments depending on user input
    composite_array = ['a'] * k
    i = 0 
    for arg in argv:
        composite_array[i] = ''.join(arg)
        i += 1
    return composite_array


############################################ driver code ###########################################################

# arr1 = ['GGGATCTC', 'ACCAAACTTCCT', 'TAAAAACCT', 'CCTGGGAA']
# arr2 = ['AATTTGGGCC', 'GGGCTATTTTT', 'CACATGTCA', 'TTTTTTTTT']
# arr_id = ['0000167', '0000139', '0000316', '0000141']


# obj = assemble_part(arr1, arr_id, 4, 1)

# obj.check_compatability()
# print('Object is compatible? ', obj.isCompatible)

# obj.add_scars()
# print('\n')

# print('parts seqs are: ', obj.part_array)
# print('\n')
# print('parts are: ', obj.part_type)
# print('\n')
# print('total sequence is:', obj.total_sequence)
# print('\n')
# print("part id's are" , obj.return_part_type)
# print('\n')
# obj.create_part_names()
# print('object names are ', obj.part_names)
# print('\n')
 
# c_arr = create_composite_part_array(2, arr1, arr2) 
# obj2 = assemble_composite_parts(c_arr, 2, 3)
# obj2.add_scars()
# print('Total return Seq is: ' , obj2.total_sequence)
# print('\n')
# print('return part ids are: ', obj2.return_part_type)
# print('\n')
# obj2.create_part_names()
# print('return part names are: ', obj2.part_names)


# input = ['ft','lr', 'test']
# input2 = ['jk', 'pow', 'tz']
# joined = create_composite_part_array(3, input, input2, arr1)
# print(joined)
