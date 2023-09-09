from utils.data_handler import DataHandler

class DataProcessing(DataHandler):

    def __init__(self):
        super().__init__()
    
    def get_feedback(self):
        return super().get_feedback()
    
    def get_correction(self):
        return super().get_correction()
    
    def counts_feedback(self):
        df= self.get_feedback()
        avg_feed = df.groupby('Name')['Satisfied'].mean()
                # Filter average satisfaction scores greater than 5
        filter1 = avg_feed[avg_feed > 5]
        filter2 = avg_feed[avg_feed <= 5]
  
        statisfied = filter1.value_counts()
        unsatisfied = filter2.value_counts()
        return statisfied, unsatisfied
