import os,datetime, shutil
from pathlib import Path
import json, logging


class MotherFiler():

    def __init__(self) -> None:
        self.root_folder = ""
        self.logfilename = str(datetime.date.today()) + '_motherfiler.log'
        logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        filename=  self.logfilename,
        level=logging.DEBUG)
        logging.info('Starting motherfiler')

    def get_file_content(self, configFilePath):
        content = None
        try:
            file = open(configFilePath)
            content = file.read()
            file.close()
        except OSError:
            logging.error("Error reading file:",configFilePath)
        return(content)

    def parse_json_file(self, fileContent):
        try:
            return json.loads(fileContent)
        except:
            logging.error("Error deserializing JSON")
            

    def create_extension_dict(self,stucture):
        extension_dict = dict()
        for folder in stucture:
            for extension in stucture[folder]:
                extension_dict[extension] = os.path.join(self.root_folder,folder)
        return extension_dict
    
    def prepare_paths(self,structure):
        self.create_destination_folders(structure)
        extension_dict = self.create_extension_dict(structure)
        root_contents = os.scandir(Path(self.root_folder))
        source_and_destination = list()
        for content in root_contents: 
            ext = content.name.split(".")[-1]
            if(content.is_file() and ext in extension_dict):
                destination = os.path.join(self.root_folder, extension_dict[ext],content.name)
                source_and_destination.append([content.path,destination])
        return source_and_destination
    
    def move_files(self, list_of_paths):
        for paths in list_of_paths:
            self.move_file(paths)

    def move_file(self, paths):
        try:
            logging.debug(paths[0] + "  -->  " + paths[1])
            shutil.move(paths[0],paths[1])
        except:
            logging.error("error moving" + paths[0])
            
    
    def move_log_file_to_root(self):
        destination_folder = os.path.join(self.root_folder,"Logs")
        logging.info("moving Logs to " + destination_folder)
        self.create_destination_folder(destination_folder)
        logging.shutdown()
        shutil.move(os.path.abspath(self.logfilename),os.path.join(destination_folder,self.logfilename))

    def create_destination_folders(self,structure):
        for folder in structure:
            destination_folder = os.path.join(self.root_folder,folder)
            self.create_destination_folder(destination_folder)

    def create_destination_folder(self, destination_folder):
        if not Path(destination_folder).exists():
            try:
                os.mkdir(destination_folder)
                logging.debug(destination_folder + "created")
            except:
                logging.error("cannot create the folder " + destination_folder)
               
        else:
            logging.info(destination_folder + " exist")

    def end_motherfiler(self):
        self.move_log_file_to_root()
        quit()

    def organize_files(self, configFilePath):
        config = self.parse_json_file(self.get_file_content(configFilePath))
        self.root_folder = config["root"]
        list_of_paths = self.prepare_paths(config["structure"])
        self.move_files(list_of_paths)
        self.end_motherfiler()

if __name__ == '__main__':
    mf = MotherFiler()
    mf.organize_files("config\downloads.txt")