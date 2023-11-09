import os

def file_exists(path_to_file : str) -> bool :
    return os.path.exists(path_to_file) and os.path.isfile(path_to_file)

def write_ref_file(path_to_file : str, ref_list : list[str]) -> int :
    # check if file already exists
    if os.path.exists(path_to_file) and os.path.isfile(path_to_file) :
        return 0
    else :
        # write everything in output file
        entry_length = 0
        with open(path_to_file, "w") as file :
            # saves references to other files after spacer
            for ref in ref_list :
                try :
                    file.write(ref + '\n')
                    entry_length += 1
                except:
                    None

            # close file
            file.close()
        return entry_length
