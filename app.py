from flask import Flask, render_template , request , abort
import pickle
import requests
import os
import json
import pandas as pd
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import StackingClassifier
from sklearn.metrics import accuracy_score

#print(twee.statuses_count,twee.followers_count,twee.friends_count,twee.favourites_count,twee.listed_count)


app=Flask(__name__)



# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


os.environ['TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAABMciAEAAAAAuk1APjmYyeDJqqm0nouX9cujamQ%3DbkmyCZsf7D3Rkx9cfZNGpVQEW3nKQjvL3KkgcDONc8vt0WV4DQ'
bearer_token = os.environ.get('TOKEN')



def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r





@app.route('/')
def index():
    return render_template('index.html')



@app.errorhandler(404)
def page_not_found(e):
    
    return render_template("404error.html"),404


@app.route('/', methods=['POST'])
def my_form_post():
    global username
    global auth
    username = request.form['username']
    search_url = f"https://api.twitter.com/1.1/users/show.json?screen_name={username}"
    def connect_to_endpoint(url):
        response = requests.request("GET", search_url, auth=bearer_oauth,)
        if response.status_code != 200:
            abort(404,description="Not found.")
        return response.json()
    
    url = search_url
    json_response = connect_to_endpoint(url)
    x=json.dumps(json_response, indent=4, sort_keys=True)
    global y,screen_name
    y=json.loads(x)
    global statuses_count
    statuses_count=int(y['statuses_count'])
    global followers_count 
    followers_count=int(y['followers_count'])
    global friends_count
    friends_count=int(y['friends_count'])
    global favourites_count 
    favourites_count=int(y['favourites_count'])
    global listed_count
    listed_count=int(y['listed_count'])
    global full_name
    full_name=y['name']+" "+y['screen_name']

    screen_name=y['screen_name']
    name=y['name']
    def maxSubsequence(screen_name, name): 
    # find the length of the strings
        global m,n 
        m = len(screen_name) 
        n = len(name) 
  
    # declaring the array for storing the dp values 
        global L
        L = [[None]*(n + 1) for i in range(m + 1)] 
  
        for i in range(m + 1): 
            for j in range(n + 1): 
                if i == 0 or j == 0 : 
                    L[i][j] = 0
                elif screen_name[i-1] == name[j-1]: 
                    L[i][j] = L[i-1][j-1]+1
                else: 
                    L[i][j] = max(L[i-1][j], L[i][j-1]) 
  
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1] 
        return L[m][n]

    print(statuses_count,followers_count,friends_count,favourites_count,listed_count)


    def normaliseNameWeight(y):
        name = y['name']
        subseq = maxSubsequence(screen_name,name)
        return (subseq/len(name))

    name_wt=normaliseNameWeight(y)

    arr = np.array([[name_wt,statuses_count,followers_count,friends_count,favourites_count,listed_count]])
    global z
    z=pd.DataFrame(arr)
    print(z)
   
    with open('stacking_classifier', 'rb') as file:
        stacking = pickle.load(file)
    
    pickleTest = stacking.predict(z)
    # Define a list of reasons for the classification result
    reasons = []
    
    # Check the values of the account features to identify reasons for the classification result
    if statuses_count < 1000:
        reasons.append("low number of tweets")
    else:
        reasons.append("Good number of tweets")
    if followers_count < 100:
        reasons.append("low number of followers")
    else:
        reasons.append("Good number of followers")
    if friends_count < 100:
        reasons.append("low number of friends")
    else:
        reasons.append("Good number of friends")
    if favourites_count < 100:
        reasons.append("low number of favorites")
    else:
        reasons.append("Good number of favorites")
    if listed_count < 10:
        reasons.append("low number of lists")
    else:
        reasons.append("Good number of lists")
    if pickleTest==0:
        auth='Real'
      #  reasons.append("classified as real")
        return render_template('index.html',res='real',value=screen_name, reasons=reasons)
    else:
        auth='Fake'
      #  reasons.append("classified as fake")
        return render_template('index.html',res='fake',value=screen_name, reasons=reasons)
    


@app.route('/predict')
def predict():
    return "<h1>{{pickleTest}}</h1>"





if __name__ == "__main__":
    app.run(debug=True)
