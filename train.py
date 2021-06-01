from sklearn.linear_model import LogisticRegression
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

run = Run.get_context()

def clean_data(data):
    #import data, this has already been looked at and inspected.
    #define the header names
    df = pd.read_csv(data,
                   sep=',',
                   header=None,
                   names=['age',
                          'workclass',
                          'fnlwgt',
                          'education',
                          'education-num.',
                          'marital-status',
                          'occupation',
                          'relationship',
                          'race',
                          'sex',
                          'capital-gain',
                          'capital-loss',
                          'hours-per-week',
                          'native-country',
                          'wage-outcome'])
    #Feature engineering look to drop correlated (i.e. education and education number features)
    #Working class no obvious difference in categories
    #race is dominated by one race
    #native country is dominated by one country, which is in the same currency as the target
    #first filter by this then drop
    df = df.to_pandas_dataframe().dropna()
    df[df['native-country'].str.contains("United States")]
    #drop unwanted variables as mentioned above.
    df = df.drop(columns=['workclass','education','race','native-country','fnlwgt'])
    
    #Encode categorical variables, for simplicity Label Encoding is used.
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtypes =='object':
            df[col] = le.fit_transform(df[col])
    
    x_df = df
    #x_df = df.drop("wage-outcome", inplace=True, axis=1)
    x_df = df.drop(columns=['wage-outcome'])
    y_df = df.drop(columns=['age',
                            'education-num.',
                            'marital-status',
                            'occupation',
                            'relationship',
                            'sex',
                            'capital-gain',
                            'capital-loss',
                            'hours-per-week'
                           ])
    #y_df = df.wage-outcome
    
    return x_df,y_df #one output

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

#  read remote URL data to DataFrame
ds = TabularDatasetFactory.from_delimited_files(url)
   
# clean data and create x and y sets            

x, y = clean_data(ds)

#Split data into train and test sets.

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

def main():
    # Add arguments to script
    parser = argparse.ArgumentParser()
  
    parser.add_argument('--max_depth', type=int, default=3, help="maximum depth of each tree that limits number of nodes")
    parser.add_argument('--learning_rate', type=float, default=0.1, help="Factor by which each tree's contribution shrinks")
    

    args = parser.parse_args()

    run.log("Regularization Strength:", np.float(args.C))
    run.log("Max iterations:", np.int(args.max_iter))

    #model = LogisticRegression(C=args.C, max_iter=args.max_iter).fit(x_train, y_train)
    model = XGBClassifier(max_depth=args.max_depth, learning_rate=args.learning_rate).fit(x_train, y_train)
  
    accuracy = model.score(x_test, y_test)
    run.log("Accuracy", np.float(accuracy))
    run.log("Max depth:", np.float(args.max_depth))
    run.log("Learning rate:", np.int(args.learning_rate))
    
    os.makedirs('outputs', exist_ok = True)
    joblib.dump(value = model, filename = './outputs/best_hyperdrive_model.joblib')

if __name__ == '__main__':
    main()
    
