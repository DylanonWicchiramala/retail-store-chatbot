import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import joblib

# getting train datasets.
df = pd.read_csv("document/restaurant sale/restaurant_sale.csv", index_col="id")


def fitModel(model, X_train, y_train):
    
    return model.fit(X_train, y_train)


def trainModel(X_train, Y_train):
    hgb = fitModel(GradientBoostingRegressor(n_estimators=100,
                                            max_depth=5,
                                            min_samples_leaf=5,
                                            learning_rate=0.1),
                   X_train,
                   Y_train)
    
    return hgb


# Convert categorical columns to dummy variables
df = pd.get_dummies(df, columns=['category'], drop_first=True)

# Split the data into features (X) and target (y)
X = df.drop('num_orders', axis=1)
y = df['num_orders']

model = trainModel(X, y)

joblib.dump(model, 'model/restaurant_sale_predictive.pkl')

if __name__ == "__main__":
    print("R square: ", model.score(X, y))