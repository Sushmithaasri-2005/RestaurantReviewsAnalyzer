import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split 
from sklearn.feature_extraction.text import TfidfVectorizer 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
lemmatizer=WordNetLemmatizer()
import nltk
from skmultilearn.problem_transform import ClassifierChain
from sklearn.metrics import hamming_loss, accuracy_score
from sklearn.tree import DecisionTreeClassifier
import pickle

#loading the data 
aspects_df = pd.read_csv('semeval2014.csv') 

def process_sentence(sent):
    words = nltk.word_tokenize(sent)
    words = [lemmatizer.lemmatize(word) for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

# Apply the function to each sentence in 'text' column and create a new column 'processed_text'
aspects_df['processed_text'] = aspects_df['text'].apply(process_sentence)
X = aspects_df["processed_text"] 
y = aspects_df.drop(['text','processed_text'],axis=1)

# initializing TfidfVectorizer  
vectorizer = TfidfVectorizer(max_features=3000, max_df=0.85) 
# fitting the tf-idf on the given data 
vectorizer.fit(X) 

# splitting the data to training and testing data set 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42) 

# transforming the data 
X_train_tfidf = vectorizer.transform(X_train) 
X_test_tfidf = vectorizer.transform(X_test) 

#Decision Tree
cc_dtree=ClassifierChain(classifier=DecisionTreeClassifier())
cc_dtree.fit(X_train_tfidf,y_train)
# save the model 
filename = 'cc_dtree.pkl'
pickle.dump(cc_dtree, open(filename, 'wb'))
print("Model saved") 
# load the model 
load_model = pickle.load(open(filename, 'rb')) 
cc_dtree_predict=load_model.predict(X_test_tfidf)
print(accuracy_score(y_test,cc_dtree_predict))
