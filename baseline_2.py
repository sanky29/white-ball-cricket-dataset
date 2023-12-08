import pandas as pd 
import numpy as np 
import pdb 
from sklearn.preprocessing import OneHotEncoder
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
data = pd.read_csv('train_full.csv')
categorical_columns = ['team','opp', 'host',"month","day_match"]
continuous_columns = ["year","toss","bat_first","format" ,"fow","score" ,"rpo" ,"result"]

encoder = OneHotEncoder(sparse=False)
encoded_categories = encoder.fit_transform(data[categorical_columns])
feature_names = encoder.get_feature_names_out(input_features=categorical_columns)

encoded_df = pd.DataFrame(encoded_categories, columns=feature_names)
final_data = pd.concat([encoded_df, data[continuous_columns]], axis=1)

X_train =  final_data.iloc[:,:-1]
y_train =  final_data.iloc[:,-1:]

data = pd.read_csv('test_full.csv')
encoded_categories = encoder.transform(data[categorical_columns])
feature_names = encoder.get_feature_names_out(input_features=categorical_columns)
encoded_df = pd.DataFrame(encoded_categories, columns=feature_names)
final_data = pd.concat([encoded_df, data[continuous_columns]], axis=1)

X_test =  final_data.iloc[:,:-1]
y_test =  final_data.iloc[:,-1:]

clf = RandomForestClassifier(n_estimators=250, criterion='entropy',min_samples_split = 8, max_features = 0.9)
clf.fit(X_train, y_train.iloc[:,0])
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test.iloc[:,0], y_pred)
print(accuracy)


importances = clf.feature_importances_

result = permutation_importance(
    clf, X_test, y_test, n_repeats=10, random_state=42, n_jobs=16
)
importances = results['importances_mean']
fig, axes = plt.subplots()
fname = X_train.iloc[1].keys().tolist()

data = [(imp, name) for (imp, name) in zip(importances, fname)]
data.sort(key = lambda x: -1*x[0])

axes.set_xticklabels([d[1] for d in data], rotation=90)
axes.bar([d[1] for d in data], [d[0] for d in data])
plt.show()
pdb.set_trace()