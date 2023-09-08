import pickle
from spellX.utils.evaluation import rouge_1_metrics, bleu_score
import yaml 
import datetime
from spellX.entity.config_entity import ModelEvaluationConfig

class ModelEvaluator:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config
        self.avg_rouge_1 = (0, 0, 0)  # Initialize with zeros for precision, recall, and F1
        self.avg_bleu_1 = 0
        self.model_count = 0
        

    def get_model_filename(self):
        # Generate the filename for the current model
        model_path = f"{self.config.model_path}/model{self.model_count}.pkl"
        with open(model_path, 'rb') as file:
            sp = pickle.load(file)
        return sp

    def evaluate(self):
        # Load the pre-trained model
        model = self.get_model_filename()

        # Read the test data from spell-testset1.txt
        with open("./artifacts/data_ingestion/data/test/spell-testset2.txt", "r") as f:
            test_data = f.readlines()

        # Initialize lists to store ROUGE and BLEU scores
        rouge_1_scores = []
        bleu_1_scores = []

        # Correct sentences and calculate metrics
        for sentence in test_data:
            # Assuming your model takes a sentence and returns a corrected sentence
            corrected_sentence = model.spell_correct(sentence.strip())['spell_corrected_text']

            # Replace this with the corresponding reference sentences if you have them
            reference_sentence = sentence.strip()

            # Calculate ROUGE-1 metrics
            rouge_1_precision, rouge_1_recall, rouge_1_f1 = rouge_1_metrics(corrected_sentence, reference_sentence)

            # Calculate BLEU-1 score
            bleu_1 = bleu_score(corrected_sentence, reference_sentence, n=1)

            # Append scores to lists
            rouge_1_scores.append((rouge_1_precision, rouge_1_recall, rouge_1_f1))
            bleu_1_scores.append(bleu_1)

        # Calculate average ROUGE-1 and BLEU-1 scores
        total_rouge_1_precision = sum(precision for precision, _, _ in rouge_1_scores)
        total_rouge_1_recall = sum(recall for _, recall, _ in rouge_1_scores)
        total_rouge_1_f1 = sum(f1 for _, _, f1 in rouge_1_scores)
        total_bleu_1 = sum(bleu for bleu in bleu_1_scores)

        num_samples = len(test_data)

        self.avg_rouge_1 = (
            total_rouge_1_precision / num_samples,
            total_rouge_1_recall / num_samples,
            total_rouge_1_f1 / num_samples,
        )
        self.avg_bleu_1 = total_bleu_1 / num_samples

        return  self.avg_rouge_1 ,self.avg_bleu_1 

    def print_results(self):
        result = {
            "Average ROUGE-1 Precision": self.avg_rouge_1[0],
            "Average ROUGE-1 Recall": self.avg_rouge_1[1],
            "Average ROUGE-1 F1 Score": self.avg_rouge_1[2],
            "Average BLEU-1 Score": self.avg_bleu_1
        }

        # Print the results to the console
        for key, value in result.items():
            print(f"{key}: {value}")

        # Generate a unique filename with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.config.root_dir}/metrics_{timestamp}.yaml"

        # Save the results to the unique YAML file
        with open(filename, "w") as yaml_file:
            yaml.dump(result, yaml_file)

        file = f"{self.config.root_dir}/metrics.txt"

        with open(file, "w") as txt_file:
            yaml.dump(result, txt_file)