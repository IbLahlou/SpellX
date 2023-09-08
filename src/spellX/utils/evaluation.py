import nltk
from nltk.util import ngrams

# Function to calculate ROUGE-1 precision, recall, and F1 score
def rouge_1_metrics(corrected_tokens, reference_tokens):
    intersection = len(set(corrected_tokens) & set(reference_tokens))
    precision = intersection / len(corrected_tokens) if len(corrected_tokens) > 0 else 0
    recall = intersection / len(reference_tokens) if len(reference_tokens) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1

# Function to calculate BLEU score
def bleu_score(candidate, reference, n):
    candidate_ngrams = list(ngrams(candidate, n))
    reference_ngrams = list(ngrams(reference, n))
    candidate_ngram_count = len(candidate_ngrams)
    reference_ngram_count = len(reference_ngrams)
    overlap_count = len(set(candidate_ngrams) & set(reference_ngrams))
    bleu = (overlap_count / candidate_ngram_count) if candidate_ngram_count > 0 else 0
    return bleu