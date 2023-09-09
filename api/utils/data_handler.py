import pandas as pd
import os

class DataHandler:
    def __init__(self):
        self.feedback_csv_path = './out/feedback_spellx.csv'
        self.correction_csv_path = './out/correction_spellx.csv'
        self.feedback_df = pd.DataFrame(columns=['Name','Email','FeedBack' ,'Satisfied'])
        self.correction = pd.DataFrame(columns=['original_text', 'spell_corrected_text'])

    def add_feedback(self, name,email, feedback,satisfied):
        new_row = {'Name': name, 'Email' : email ,'FeedBack' : feedback,'Satisfied': satisfied}
        self.feedback_df = pd.concat([self.feedback_df, pd.DataFrame([new_row])], ignore_index=True)
        self.feedback_df.to_csv('./out/feedback_spellx.csv', index=False)

    def add_correction(self, input_text, corrected_text):
        new_row = {'original_text': input_text, 'spell_corrected_text': corrected_text}
        self.correction = pd.concat([self.correction, pd.DataFrame([new_row])], ignore_index=True)
        self.correction.to_csv('./out/correction_spellx.csv', index=False)

    def get_feedback(self): 
        return pd.read_csv(self.feedback_csv_path) if os.path.isfile(self.feedback_csv_path) else pd.DataFrame(columns=['Name','Email','FeedBack', 'Satisfied'])

    def get_correction(self):
        return pd.read_csv(self.correction_csv_path) if os.path.isfile(self.correction_csv_path) else pd.DataFrame(columns=['original_text', 'spell_corrected_text'])
    
    def counts_feedback(self):
        df = self.get_feedback()
        avg_feed = df.groupby(['Name', 'Email'])['Satisfied'].mean()
        
        # Filter average satisfaction scores greater than 5
        filter1 = avg_feed[avg_feed > 5]
        filter2 = avg_feed[avg_feed <= 5]
  
        # Count the occurrences of scores greater than 5
        counts1 = filter1.value_counts()
        counts2 = filter2.value_counts()

        # Return the counts
        satisfied = counts1.sum()
        unsatisfied = counts2.sum()
        return satisfied, unsatisfied