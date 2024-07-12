import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from skmultilearn.problem_transform import ClassifierChain
from sklearn.tree import DecisionTreeClassifier
import pickle

# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()

def process_sentence(sent):
    words = nltk.word_tokenize(sent)
    words = [lemmatizer.lemmatize(word) for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

# Load restaurant reviews from a CSV file
reviews_df = pd.read_csv('semeval2014.csv')
reviews_df['processed_Review'] = reviews_df['text'].apply(process_sentence)

# Initialize TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=3000, max_df=0.85)
X_tfidf = vectorizer.fit_transform(reviews_df['processed_Review'])

# Assuming your labels are in columns 'service', 'food', 'anecdotes/miscellaneous', 'price', 'ambience'
y = reviews_df[['service', 'food', 'anecdotes/miscellaneous', 'price', 'ambience']]

# Initialize ClassifierChain with DecisionTreeClassifier
cc_dtree = ClassifierChain(DecisionTreeClassifier())
cc_dtree.fit(X_tfidf, y)

with open('vectorizer.pkl', 'wb') as vec_file:
    pickle.dump(vectorizer, vec_file)