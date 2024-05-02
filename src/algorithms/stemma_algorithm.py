"""Base class for all implementation of stemma algorithms.

    Have the Stemma_algo object be the representation off all stemmas through inheritance.

    Name stemma
            stemma_method
            
    Where to store the new edge file? --> New Folder "Stemma_models" = lsit of edge files

    Seperate YAML file for each model OR all in one and check if YAML header in file OR YAML for stema builds?

    In Compute() do we use folder name and check contense (as files should all be in same place) OR specify for each file.
    OR
    Put optional parameters to specify which to do.
"""
class Stemma_algo:

    is_built = False # Indicates if the tree is built ???

    # Use the 

    def Compute(folder_path = None,file_Path = None, YAML = None): # Or fol

        if folder_path != None:
            # Check files exist and and raise exception if param missing
            # Check if correct YAML header and parameters exist
            raise NotImplemented    
        
        # Check if correct YAML header and parameters exist
        raise NotImplemented
    
    # Have it common to all classes --> do not implement in children ?????????????? do we implement in children?
    def Print():
        print("Not yet implemented!")

    # Have it common to all classes --> do not implement in children
    def Eval(stemma):
        print("Not yet implemented!")