import os
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import re

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
def index():
    """Returns the landing page"""
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    """Returns all recipes, recipes by category, all appliances or appliances by category"""
    if request.args['collection'] == 'recipes':
        if request.args['find'] == 'all':
            return render_template('search.html', recipes=mongo.db.recipes.find().sort('title'))
        else:
            return render_template('search.html', recipes=mongo.db.recipes.find({"category": request.args['find']}).sort('title'))
    elif request.args['collection'] == 'recipe_categories':
        return render_template('search.html', recipe_categories=mongo.db.recipe_categories.find().sort('name'))
    elif request.args['collection'] == 'appliances':
        if request.args['find'] == 'all':
            return render_template('search.html', appliances=mongo.db.appliances.find().sort('brand'))
        else:
            return render_template('search.html', appliances=mongo.db.appliances.find({"type": request.args['find']}).sort('brand'))
    elif request.args['collection'] == 'appliance_categories':
        return render_template('search.html', appliance_categories=mongo.db.appliance_categories.find().sort('name'))
    else:
        return render_template('error.html', msg='Bad argument error! (/search)')


@app.route('/', methods=['POST'])
@app.route('/navsearch', methods=['POST'])
def navsearch():
    """Returns ingredient search results"""
    search_text = re.compile(request.form.get('search'), re.IGNORECASE)
    recipes = mongo.db.recipes.find({'ingredients': {'$in': [search_text]}}).sort('title')
    return render_template('navsearch.html', recipes=recipes)


@app.route('/view/<db_id>', methods=['GET'])
def view(db_id):
    """Returns a recipe or an appliance to view individually"""
    if request.args['collection'] == 'recipes':
        mongo.db.recipes.update({'_id': ObjectId(db_id)},
        {
            '$inc' : {
                'view_stat' : 1
            }
        })
        return render_template('view.html', recipe=mongo.db.recipes.find_one({"_id": ObjectId(db_id)}))
    elif request.args['collection'] == 'appliances':
        mongo.db.appliances.update({'_id': ObjectId(db_id)},
        {
            '$inc' : {
                'view_stat' : 1
            }
        })
        return render_template('view.html', appliance=mongo.db.appliances.find_one({"_id": ObjectId(db_id)}))
    else:
        return render_template('error.html', msg='Bad argument error! (/view)')


@app.route('/add_form', methods=['GET'])
def add_form():
    """Returns a form for a new recipe or reicpe category"""
    if request.args['collection'] == 'recipe':
        return render_template('add_form.html', collection=mongo.db.recipe_categories.find())
    elif request.args['collection'] == 'category':
        return render_template('add_form.html')
    else:
        return render_template('error.html', msg='Bad argument error! (/add_form)')


@app.route('/edit_form/<db_id>', methods=['GET'])
def edit_form(db_id):
    """Returns a form to edit an existing recipe or recipe category"""
    if request.args['collection'] == 'recipe':
        return render_template('edit_form.html', collection=mongo.db.recipe_categories.find(), recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}))
    elif request.args['collection'] == 'recipe_category':
        return render_template('edit_form.html', recipe_category=mongo.db.recipe_categories.find_one({"_id": ObjectId(db_id)}))
    else:
        return render_template('error.html', msg='Bad argument error! (/edit_form)')


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    """Inserts a recipe into the database and redirects to the list of all recipes"""
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
    return redirect(url_for('search', collection='recipes', find='all'))


@app.route('/insert_recipe_category', methods=['POST'])
def insert_recipe_category():
    """Inserts a recipe category into the database and redirects to the list of all recipe categories"""
    recipe_category = {
        'name' :  request.form.get('name'),
        'img_link' : request.form.get('img_link')
    }
    mongo.db.recipe_categories.insert_one(recipe_category)
    return redirect(url_for('search', collection='recipe_categories'))


@app.route('/update_recipe/<db_id>', methods=['POST'])
def update_recipe(db_id):
    """Updates a recipe in the database and redirects to the list of all recipes"""
    mongo.db.recipes.update({'_id': ObjectId(db_id)},
    {
        '$set': {
            'title' :  request.form.get('title'),
            'category' : request.form.get('category'),
            'ingredients' : request.form.get('ingredients').split('\n'),
            'method' : request.form.get('method').split('\n'),
            'img_link' : request.form.get('img_link'),
            'servings' : request.form.get('servings')
        }
    })
    return redirect(url_for('search', collection='recipes', find ='all'))


@app.route('/update_recipe_category/<db_id>', methods=['POST'])
def update_recipe_category(db_id):
    """Updates a recipe category in the database and redirects to the list of all recipe categories"""
    mongo.db.recipe_categories.update({'_id': ObjectId(db_id)},
    {
        'name' :  request.form.get('name'),
        'img_link' : request.form.get('img_link')
    })
    return redirect(url_for('search', collection='recipe_categories'))


@app.route('/delete_recipe/<db_id>')
def delete_recipe(db_id):
    """Removes a recipe from the database and redirects to the list of all recipes"""
    mongo.db.recipes.remove({'_id': ObjectId(db_id)})
    return redirect(url_for('search', collection='recipes', find ='all'))


@app.route('/delete_recipe_category/<db_id>')
def delete_recipe_category(db_id):
    """Removes a recipe category from the database and redirects to the list of all recipe categories"""
    mongo.db.recipe_categories.remove({'_id': ObjectId(db_id)})
    return redirect(url_for('search', collection='recipe_categories'))


@app.route('/add_review/<db_id>', methods=['POST'])
def add_review(db_id):
    """Adds a review to a recipe or an appliance and refreshes the view page"""
    if request.args['collection'] == 'recipe':
        mongo.db.recipes.update({'_id': ObjectId(db_id)},
        {
            '$push' : {
                'reviews' : request.form.get('review')
            }
        })
        return redirect(url_for('view', db_id=db_id, collection='recipes'))
    elif request.args['collection'] == 'appliance':
        mongo.db.appliances.update({'_id': ObjectId(db_id)},
        {
            '$push' : {
                'reviews' : request.form.get('review')
            }
        })
        return redirect(url_for('view', db_id=db_id, collection='appliances'))
    else:
        return render_template('error.html', msg='Bad argument error! (/add_review)')


@app.errorhandler(404)
def not_found():
    """Page not found."""
    return render_template('error.html', msg='Page not found error! (404)')


@app.errorhandler(400)
def handle_bad_request(e):
    """Bad request error."""
    return render_template('error.html', msg='Bad request error! (400)')


@app.errorhandler(500)
def server_error():
    """Internal server error."""
    return render_template('error.html', msg='Internal server error! (500)')


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=True)
