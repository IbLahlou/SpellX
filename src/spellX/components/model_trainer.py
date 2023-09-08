from spello.model import SpellCorrectionModel
import re
import pickle
from spellX.utils.trainer  import read_text
from spellX import logger
from spellX.entity.config_entity import ModelTrainerConfig
import os

class ModelTrainer :
    def __init__(self, config: ModelTrainerConfig):
        self.config = config
        self.model_count = 0 

    def get_model_filename(self):
        # Generate the filename for the current model
        return f"{self.config.root_dir}/model{self.model_count}.pkl"
    
    def get_data_filename(self):
        # Generate the filename for the current model
        return f"{self.config.data_path}/{self.config.data_file}"

    def train(self):
        try :
            model_path = self.get_model_filename()

            if not os.path.exists(model_path):
                with open("./artifacts/data_ingestion/data/train/big.txt", "r") as f:
                    big = f.readlines()
                with open("./artifacts/data_ingestion/data/train/wikipedia.txt", "r") as f:
                    wiki = f.readlines()
                with open("./artifacts/data_ingestion/data/train/aspell.txt", "r") as f:
                    aspell = f.readlines()
                with open("./artifacts/data_ingestion/data/train/birkbeck.txt", "r") as f:
                    birk = f.readlines()
                big  = [i.strip() for i in big]
                #Remove \t - tab
                big_t = [re.sub('\\t', ' ', text) for text in big]
                #Remove \\
                big_ = [re.sub("\\'", "", text) for text in big_t]
                #Remove
                big_r = [text for text in big_ if text != '']
                #Remove Special characters
                big_star = [re.sub(r'[^a-zA-Z]+', ' ', text) for text in big_r]
                #Remove leading and trailing spaces
                big_stripped = [text.strip() for text in big_star]
                sp = SpellCorrectionModel(language='en')
                sp.train(big_stripped)
                sp.train(wiki)
                sp.train(aspell)
                sp.train(birk)
                self.sp = sp

                with open(model_path, 'wb') as file:
                    pickle.dump(self.sp, file)


            else:
                # Model loading
                with open(model_path, 'rb') as file:
                    sp = pickle.load(file)

                # New Data gathering
                path = self.get_data_filename()
                with open(path, "r") as f:
                    data = f.readlines()
                sp.train(data)

                # Increment the model count for the next model
                self.model_count += 1
        except Exception as e:
            raise e

                







