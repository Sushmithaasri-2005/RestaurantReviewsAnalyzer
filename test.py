from fastapi.responses import FileResponse
import pandas as pd
import aspect_based_sentiment_analysis as absa
from mlc_predict import process_reviews_mlc
import os
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Load the sentiment analysis model with the default pattern recognizer
nlp = absa.load()

# Define a function to perform aspect-based sentiment analysis
def analyze_sentiment(text, aspects):
    # Perform aspect-based sentiment analysis
    completed_task = nlp(text, aspects=aspects)
    # Extract sentiment results for each aspect
    results = {aspect: completed_task.examples[i].sentiment for i, aspect in enumerate(aspects)}
    print("analyze_sentiment!")
    return results

# Define a function to map numeric sentiment values to human-readable labels
def map_sentiments(sentiment_results):
    sentiment_map = {
        absa.Sentiment.positive: "Positive",
        absa.Sentiment.negative: "Negative",
        absa.Sentiment.neutral: "Neutral"
    }
    mapped_results = {aspect: sentiment_map[sentiment] for aspect, sentiment in sentiment_results.items()}
    print("map_sentiments")
    return mapped_results

# Function to analyze sentiments from a CSV file and save results to another CSV file
def process_reviews(input_csv):
    # Load restaurant reviews from a CSV file
    reviews_df = pd.read_csv(input_csv)
    reviews_df = reviews_df.iloc[0:40]
    print("first 5: ", reviews_df)
    print("file loaded succesfuly!")
    # Assuming the review column is named 'Review', adjust if needed
    #reviews_df = reviews_df.drop(['Restaurant','Reviewer','Rating','Metadata','Time','Pictures','7514'], axis=1, errors='ignore')
    
    # Define aspects to analyze
    aspects = ['service', 'food', 'anecdotes/miscellaneous', 'price', 'ambience']
    
    # Initialize a list to store results
    result_senti_list = []

    # Iterate through each review in the DataFrame
    for index, row in reviews_df.iterrows():
        print(row)
        text = str(row['Review'])
        sentiment_results = analyze_sentiment(text, aspects)
        mapped_results = map_sentiments(sentiment_results)
        
        # Create a dictionary for the current review
        review_sentiments = {
            "Review": text,
            "Service Sentiment": mapped_results['service'],
            "Food Sentiment": mapped_results['food'],
            "Anecdotes Sentiment": mapped_results['anecdotes/miscellaneous'],
            "Price Sentiment": mapped_results['price'],
            "Ambience Sentiment": mapped_results['ambience']
        }
        print(review_sentiments)
        # Append the dictionary to the list
        result_senti_list.append(review_sentiments)
    print("file loaded succesfuly!")
    # Convert the result list to a DataFrame
    result_df = pd.DataFrame(result_senti_list)
    output_csv='output/Result.csv'
    # Save the DataFrame to a CSV file
    result_df.to_csv(output_csv, index=False)
    print(f"Sentiment analysis results have been saved to '{output_csv}'.")

    # Example usage:
# input_csv = 'input_data/Restaurant_reviews_50data.csv'

# # Call the function to process the reviews and save the results
# process_reviews(input_csv)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

directory= "input_data"
@app.post("/upload")
async def uploadfile(file1: UploadFile):
      print("FileName: ", file1.filename)
      file_path = f"input_data/{file1.filename}"
      if not os.path.exists(directory):
        os.makedirs(directory)
      with open(file_path, "wb") as f:
        f.write(file1.file.read())
      process_reviews(file_path)
      process_reviews_mlc(file_path)
      return {"message": "File saved successfully"}

@app.get("/download")
async def downloadFile():
    download_pathdir="output/Result_mlc.csv"
    if os.path.exists(download_pathdir):
        return FileResponse(download_pathdir)
    else:
        return "File not found"
     
@app.get("/download_bert")
async def downloadFile():
    download_pathdir="output/Result.csv"
    if os.path.exists(download_pathdir):
        return FileResponse(download_pathdir)
    else:
        return "File not found"