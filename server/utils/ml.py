# utils/ml.py
def predictive_correction():
    ...
    
# main.py
from utils.ml import predictive_correction
@app.get("/predictive")
def predictive():
    return predictive_correction()
