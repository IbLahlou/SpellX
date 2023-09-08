from spellX.constants import *
from spellX.utils.common import read_yaml , create_directories 
from spellX.entity.config_entity import (DataIngestionConfig,
                                         DataValidationConfig,
                                         ModelTrainerConfig,
                                         ModelEvaluationConfig)

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])


    # DATA INGESTION CONFIG METHOD
    
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir 
        )

        return data_ingestion_config
      
      # DATA VALIDATION CONFIG METHOD

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            STATUS_FILE=config.STATUS_FILE,
            ALL_REQUIRED_FILES=config.ALL_REQUIRED_FILES,
        )

        return data_validation_config

        # MODEL TRAINER CONFIG METHOD

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer

        create_directories([config.root_dir])

        model_trainer_config = ModelTrainerConfig(
            root_dir=config.root_dir,
            data_path=config.data_path,
            data_file = config.data_file,
            
        )

        return model_trainer_config
          
    def get_model_evaluation_config(self) -> ModelEvaluationConfig: 
        config = self.config.model_evaluation

        create_directories([config.root_dir])
        
        model_evaluation_config = ModelEvaluationConfig(
            root_dir = config.root_dir,
            data_path = config.data_path,
            data_file = config.data_file,
            model_path = config.model_path
        )

        return model_evaluation_config