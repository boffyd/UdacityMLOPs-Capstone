from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
import argparse
import os
import numpy as np
from sklearn.metrics import mean_squared_error
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from azureml.core.run import Run
from azureml.data.dataset_factory import TabularDatasetFactory
from azureml.data.dataset_factory import DataType
from azureml.core import Dataset


run = Run.get_context()
ws = run.experiment.workspace 

def clean_data(data):
    #drop nas, need to work as a dataframe, can be handled before or in function

    #df = data.to_pandas_dataframe().dropna #comment out as req'd
    df = data.dropna() #comment out as req'd needed for blobstore
    
    #Feature engineering look to drop unneeded features (i.e. education and education = correlation)    
    #Working class no obvious difference in categories
    #native country is dominated by one country, which is in the same currency as the target
    
    #df[df['native-country'].str.contains("United States")]
    
    #drop unwanted variables
    df = df.drop(columns=['workclass','education','race','fnlwgt','Column2'])
    
    #Encode categorical variables, for simplicity Label Encoding is used.
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtypes =='object':
            df[col] = le.fit_transform(df[col])
    x_df = df.drop(columns=['wage'])
    y_df = df['wage']
    
    return x_df,y_df #one output

# Import data

dataset = Dataset.get_by_name(ws, name='Adult')
ds = dataset.to_pandas_dataframe()

# clean data and create x and y sets            

x, y = clean_data(ds)

#Split data into train and test sets.

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

def main():
    # Add arguments to script
    parser = argparse.ArgumentParser()
  
    parser.add_argument('--max_depth', type=int, default=5, help="maximum depth of each tree")
    parser.add_argument('--learning_rate', type=float, default=0.1, help="Factor by which each tree's contribution shrinks")
    
    args = parser.parse_args()

    model = XGBClassifier(max_depth=args.max_depth, learning_rate=args.learning_rate)
    model.fit(x_train,y_train)
    
    Accuracy = model.score(x_test, y_test)
    run.log("Accuracy", np.float(Accuracy))
    #run.log("Max depth:", np.float(args.max_depth))
    #run.log("Learning rate:", np.int(args.learning_rate))
    
    os.makedirs('outputs', exist_ok = True)
    joblib.dump(value = model, filename = './outputs/best_hyperdrive_model.joblib')

if __name__ == '__main__':
    main()
    
