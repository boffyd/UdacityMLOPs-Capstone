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
from azureml.core import Workspace

run = Run.get_context()
ws = run.experiment.workspace


def clean_data(data):
    #import data, this has already been looked at and inspected.
    #define the header names
    
    df = data.dropna()
     #Feature engineering look to drop correlated (i.e. education and education number features)    
    #Working class no obvious difference in categories
    #race is dominated by one race
    #native country is dominated by one country, which is in the same currency as the target
    #first filter by this then drop
    
    df[df['native-country'].str.contains("United States")]
    #drop unwanted variables as mentioned above.
    df = df.drop(columns=['workclass','education','race','native-country','fnlwgt','Column2'])
    
    #Encode categorical variables, for simplicity Label Encoding is used.
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtypes =='object':
            df[col] = le.fit_transform(df[col])
    x_df = df.drop(columns=['wage'])
    y_df = df['wage']
    
    return x_df,y_df #one output


#Import data
#  read remote URL data to DataFrame
##url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"


# pass url to Tabular dataset.  Note this is different to pandas dataframe, and gets converted to a dataframe in the function.
#ds = TabularDatasetFactory.from_delimited_files(url,header = False)



# azureml-core of version 1.0.72 or higher is required
# azureml-dataprep[pandas] of version 1.1.34 or higher is required
from azureml.core import Workspace, Dataset

subscription_id = 'a24a24d5-8d87-4c8a-99b6-91ed2d2df51f'
resource_group = 'aml-quickstarts-146487'
workspace_name = 'quick-starts-ws-146487'

workspace = Workspace(subscription_id, resource_group, workspace_name)

dataset = Dataset.get_by_name(workspace, name='Adult')
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
    
