from spellX.config.configuration import ConfigurationManager
from spellX.components.model_evaluator import ModelEvaluator
from spellX import logger

class ModelEvaluationPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        model_evaluation_config = config.get_model_evaluation_config()
        model_evaluation_config = ModelEvaluator(config=model_evaluation_config)
        model_evaluation_config.evaluate()
        model_evaluation_config.print_results()