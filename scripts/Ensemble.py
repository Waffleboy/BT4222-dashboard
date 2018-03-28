import numpy as np
import pandas as pd
from _pickle import load
from keras.models import load_model

from EnsembleModels import ML_Models, textpreprocessor

class Ensemble():
    def __init__(self, first_ML_layer, first_DL_layer, second_layer, preprocessor):
        self.first_ML_layer = first_ML_layer
        self.first_DL_layer = first_DL_layer
        self.second_layer = second_layer
        self.textpreprocessor = preprocessor
        
        self.num_first_layers = len(first_ML_layer.models) + len(first_DL_layer)
        
    def predict_first_layer(self, x):
        new_x = np.zeros((x.shape[0], self.num_first_layers * 2))
        curr_index = 0
        
        #for model in self.first_ML_layer:
        y_pred = self.first_ML_layer.predict(x)
        new_x[:, curr_index:(curr_index + y_pred.shape[1])] = y_pred
        curr_index = curr_index + y_pred.shape[1]
        
        x_ml = self._preprocess_x_DL(x)
        
        for model in self.first_DL_layer:
            y_pred = model.predict(x_ml)
            new_x[:, curr_index:(curr_index + y_pred.shape[1])] = y_pred
            curr_index = curr_index + y_pred.shape[1]
            
        new_x = np.reshape(new_x, new_x.shape + (1,))
        
        return new_x
    
    def predict(self, xtest):
        y_mapper = {0: 'negative', 1: 'positive'}
        
        if type(xtest) == str:
            xtest = pd.Series(xtest)
        
        new_xtest = self.predict_first_layer(xtest)
        ypred = self.second_layer.predict(new_xtest).argmax(axis = -1)
        
        return pd.Series(ypred).map(y_mapper)
    
    def _preprocess_x_DL(self, x):
        x = self.textpreprocessor.preprocess(x)
        x = self.textpreprocessor.tokenize_dl(x, tokenizer_dl)
        x = self.textpreprocessor.pad_x(x, 40)
        
        return x
    
ml_models = load(open('ml_models.pkl', 'rb'))
dl_models = load_model('dl_model.h5')
ensembler = load_model('ensembler_model.h5')
tokenizer_dl = load(open('tokenizer.pkl', 'rb'))

preprocessor = textpreprocessor()

ensemble = Ensemble(ml_models, [dl_models], ensembler, preprocessor)

