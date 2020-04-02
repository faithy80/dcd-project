import os
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    if request.args['collection'] == 'recipes':
        if request.args['find'] == 'all':
            return render_template('search.html', recipes = mongo.db.recipes.find())
        else:
            return render_template('search.html', recipes = mongo.db.recipes.find({"category": request.args['find']}))
    elif request.args['collection'] == 'recipe_categories':
        return render_template('search.html', recipe_categories = mongo.db.recipe_categories.find())
    elif request.args['collection'] == 'appliances':
        if request.args['find'] == 'all':
            return render_template('search.html', appliances = mongo.db.appliances.find())
        else:
            return render_template('search.html', appliances = mongo.db.appliances.find({"type": request.args['find']}))
    elif request.args['collection'] == 'appliance_categories':
        return render_template('search.html', appliance_categories = mongo.db.appliance_categories.find())
    else:
        return 'Bad arguments!'


@app.route('/view/<db_id>', methods=['GET'])
def view(db_id):
    if request.args['collection'] == 'recipes':
        return render_template('view.html', recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}))
    elif request.args['collection'] == 'appliances':
        return render_template('view.html', appliance = mongo.db.appliances.find_one({"_id": ObjectId(db_id)}))
    else:
        return 'Bad arguments!'


@app.route('/add_form', methods=['GET'])
def add_form():
    if request.args['collection'] == 'recipe':
        return render_template('add_form.html', collection = mongo.db.recipe_categories.find())
    if request.args['collection'] == 'category':
        return render_template('add_form.html')


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipe = {
        'title' :  request.form.get('title'),
        'category' : request.form.get('category'),
        'ingredients' : request.form.get('ingredients').split('\n'),
        'method' : request.form.get('method').split('\n'),
        'img_link' : request.form.get('img_link'),
        'reviews' : [],
        'servings' : request.form.get('servings'),
        'view_stat' : 0
    }
    mongo.db.recipes.insert_one(recipe)
    return redirect(url_for('search', collection = 'recipes', find ='all'))

@app.route('/insert_recipe_category', methods=['POST'])
def insert_recipe_category():
    recipe_category = {
        'name' :  request.form.get('name'),
        'img_link' : request.form.get('img_link')
    }
    mongo.db.recipe_categories.insert_one(recipe_category)
    return redirect(url_for('search', collection = 'recipe_categories'))


@app.route('/delete_recipe/<db_id>')
def delete_recipe(db_id):
    mongo.db.recipes.remove({'_id': ObjectId(db_id)})
    return redirect(url_for('search', collection = 'recipes', find ='all'))


@app.route('/delete_recipe_category/<db_id>')
def delete_recipe_category(db_id):
    mongo.db.recipe_categories.remove({'_id': ObjectId(db_id)})
    return redirect(url_for('search', collection = 'recipe_categories'))


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=True)
