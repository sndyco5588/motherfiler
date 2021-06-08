import os,datetime
from pathlib import Path
import json, logging


class MotherFiler():

    def __init__(self) -> None:
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
            self.abend()
        return(content)

    def parse_json_file(self, fileContent):
        try:
            return json.loads(fileContent)
        except:
            logging.error("Error deserializing JSON")
            self.abend()

    def create_extension_dict(self, root, stucture):
        extension_dict = dict()
        for folder in stucture:
            for extension in stucture[folder]:
                extension_dict[extension] = os.path.join(root,folder)
        return extension_dict
    
    def prepare_paths(self, root, structure):

        self.create_destination_folders(root,structure)
        extension_dict = self.create_extension_dict(root, structure)
        root_contents = os.scandir(Path(root))
        source_and_destination = list()
        for content in root_contents: 
            ext = content.name.split(".")[-1]
            if(content.is_file() and ext in extension_dict):
                destination = os.path.join(root, extension_dict[ext],content.name)
                source_and_destination.append([content.path,destination])
        return source_and_destination
    
    def move_files(self, list_of_paths):
        for paths in list_of_paths:
            try:
                logging.debug(paths[0] + "  -->  " + paths[1])
            except:
                logging.error("error moving",paths[0])
    
    def create_destination_folders(self,root,structure):

        for folder in structure:
            destination_folder = os.path.join(root,folder)
            if not Path(destination_folder).exists():
                try:
                    os.mkdir(destination_folder)
                    logging.debug(destination_folder,"created")
                except:
                    logging.error("cannot create the folder")
                    self.abend()
            else:
                logging.info(destination_folder + " exist")

    def abend(self):
        logging.info("motherfiler encountered an error! Ending the program now")
        quit()

    def organize_files(self, configFilePath):
        config = self.parse_json_file(self.get_file_content(configFilePath))
        list_of_paths = self.prepare_paths(config["root"],config["structure"])
        self.move_files(list_of_paths)

if __name__ == '__main__':
    mf = MotherFiler()
    mf.organize_files("config\downloads.txt")