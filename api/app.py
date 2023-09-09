import pickle
from flask import Flask, render_template, request, redirect, url_for
from utils.data_handler import DataHandler

app = Flask(__name__)



# Load the spell corrector model
with open('../artifacts/model_trainer/model0.pkl', 'rb') as f:
    sp = pickle.load(f)

data_handler = DataHandler()

# Route 1 : Home page

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        corrected_text = correct_text(user_input)
        return render_template('index.html', user_input=user_input, corrected_text=corrected_text)

    return render_template('index.html')


def correct_text(input_text):

    
    # Correct text using the loaded model
    result = sp.spell_correct(input_text)
    # Extract the original and corrected text from the result
    original_text = result['original_text']
    corrected_text = result['spell_corrected_text']
    # Add the correction to the data handler
    data_handler.add_correction(original_text, corrected_text)
    return corrected_text

# Route 2 : Feedback page

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    feedback = request.form.get('comments')
    satisfied = request.form.get('satisfied')
    data_handler.add_feedback(name, email,feedback,satisfied)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
