# necessary imports
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import pymongo
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)  #initialising the flask app

@app.route('/', methods=['POST','GET'])
@cross_origin()
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        searchstring = request.form['content'].replace(' ','')
        try:
            dbconnection = pymongo.MongoClient("mongodb+srv://ashwini:qwerty123@cluster0.j29my.mongodb.net/crawlerDB?retryWrites=true&w=majority")
            db = dbconnection['crawlerDB']  #connecting to database 'crawlerDB'
            reviews = db[searchstring].find({})
            if reviews.count()>0:
                return render_template('results.html',reviews=reviews)
            else:
                url = "https://www.flipkart.com/search?q=" + searchstring
                flipkartpage = requests.get(url)
                flipkart_html = bs(flipkartpage.text,'html')
                bigboxes = flipkart_html.findAll('div',{'class':'_1AtVbE col-12-12'})
                del bigboxes[:3]
                box = bigboxes[0]

                # for box in bigboxes:
                product_link = "https://www.flipkart.com" + box.div.div.div.a['href'] # actual product link
                product = requests.get(product_link)
                product_html = bs(product.text, 'html')
                commentboxes = product_html.find_all('div', {'class': "_16PBlm"})  # select all commentboxes

                table = db[searchstring] # creating a collection with the same name as search string. Tables and Collections are analogous.
                reviews = []  # initializing an empty list for reviews

                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'

                    mydict = {"Product": searchstring, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}  # saving that detail to a dictionary
                    table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list

                return render_template('results.html',reviews=reviews)

        except:
            return "Something is wrong"

if __name__ == "__main__":
    app.run(debug=True)