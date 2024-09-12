import pandas as pd
import os
import joblib
from typing import Literal

def restaurant_sale_project(
    base_price:float, 
    category: Literal[
        'Beverages',
        'Biryani',
        'Dessert',
        'Extras',
        'Fish',
        'Other Snacks',
        'Pasta',
        'Pizza',
        'Rice Bowl',
        'Salad',
        'Sandwich',
        'Seafood',
        'Soup',
        'Starters'
        ],  
    human_traffic:int=3000,
    week:int|list=[1, 5, 52]):

    def getModel():
        
        pkl_dir = os.path.abspath('model')
        
        model_path = os.path.join(pkl_dir, 'restaurant_sale_predictive.pkl')

        model = joblib.load(model_path)

        return model


    def runModel(X_test):

        model = getModel()
        Y_pred = model.predict(X_test)
        
        return model, Y_pred
    
    week = [week] if isinstance(week, int) else week
    
    result = {}
    
    for week in week:
        data = {
            "week": week,
            "base_price": base_price,
             "human_traffic":human_traffic,
        }
        
        ca_key = [ 'category_Biryani',
        'category_Desert', 'category_Extras', 'category_Fish',
        'category_Other Snacks', 'category_Pasta', 'category_Pizza',
        'category_Rice Bowl', 'category_Salad', 'category_Sandwich',
        'category_Seafood', 'category_Soup', 'category_Starters']
        
        for k in ca_key:
            data[k] = category==k.split("_")[-1]
            
        data = pd.DataFrame([data])
        
        _, y = runModel(data)
        
        result[week] = round(y[0], 1)
        
    return result
