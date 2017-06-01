def deleteDirectory (DIR_TO_BE_DELETED,RECURSIVE=False):
    # This function will Clean the directory that is  on disk directory. If Recursive is set to true then it will remove any Sub-directories too  	
	try:
		import os
		import shutil
	except Exception as e:
		print(str(e))
		sys.exit(-1)
	
    if os.path.isdir(DIR_TO_BE_DELETED):
        for del_file in os.listdir(DIR_TO_BE_DELETED):
            file_path = os.path.join(DIR_TO_BE_DELETED,del_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif (os.path.isdir(file_path) & RECURSIVE == True):
                    shutil.rmtree(file_path, True)
            except Exception as error:
                raise error
    else:
        return True
    
    return True