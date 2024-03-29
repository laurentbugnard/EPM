import h5py
import numpy as np
import pandas as pd

#TODO: look what to do with all of this

def to_dict(param_str:str) -> dict:
    """This function transforms a string of parameter of the form
    'a=1_b=2.3_c=text' into a dictionary, i.e. {'a':1, 'b':2.3, 'c':'text'},
    where the types are automatically recognized (int, float or str). 
    If the string doesn't have the expected format, an error message is displayed.

    Args:
        param_str (str): The input string.

    Returns:
        dict: The output dictionary.
    """
    #Initialize output dictionary
    res_dict = {}
    #Parse string into a list
    str_list = param_str.replace('\\','/').replace('*','.').split('___')
    
    for string in str_list:
        #Try to extract name and value
        try:
            k, v = string.split('=')
            
        except ValueError:
            print(f'Error: "{string}" is not a valid parsing.')
            return
        
        #Try to convert it to an integer
        try:
            v = int(v)
        except ValueError:
            #Try to convert it to a float
            try:
                v = float(v)
            except ValueError:
                pass
        
        res_dict.update({k: v})
        
            
        
    return res_dict

def to_str(param_dict:dict) -> str:
    """This function transforms a dictionary of parameters,
    e.g. {'b':2.3, 'a':1, 'c':'text'} into a string of the form
    'a=1_b=2.3_c=text', where the parameters are sorted in alphabetical order.

    Args:
        param_dict (dict): The input dictionary.

    Returns:
        str: The output string.
    """
        
    assert(not('___' in ''.join(param_dict.keys()))), "'___' not allowed in parameter names."
    
    #Initialize output string
    str_list = []
    #Create individual parameter strings in alphabetical order
    for key in sorted(param_dict):
        str_list.append(key + '=' + str((param_dict[key])).replace('/','\\').replace('.','*'))

    #Join individual parameter strings
    return '___'.join(str_list)
    

def summary_df(file:type[h5py.File]) -> type[pd.DataFrame]:
    """This function summarizes in a Pandas Dataframe the parameters of all simulations
    contained in a HDF5 file.

    Args:
        file (type[h5py.File]): HDF5 file to summarize.

    Returns:
        type[pd.DataFrame]: Summarized parameters in Pandas Dataframe format.
    """
    #Initialize a list that will contain the parameter dictionaries for each of the simulations
    param_dict_list = []
    #Initialize the set of all parameters used throughout all simulations.
    unique_param = set()
    
    #Loop through all simulations to get the info
    for name in file:
        param_dict = to_dict(name)
        
        #update each lis
        param_dict_list.append(param_dict)
        unique_param.update(param_dict.keys())
    
    #Initialize output dataframe
    df = pd.DataFrame(index=range(len(file)), columns=sorted(unique_param))
    #Fill dataframe
    for i, param_dict in enumerate(param_dict_list):
        df.loc[i] = param_dict
    
    return df