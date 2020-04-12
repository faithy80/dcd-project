import os
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import re
import requests

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

def update_quantity_in_category(category):
    """Updates the number of recipes in the given recipe category"""

    # count the number of recipes
    counter = mongo.db.recipes.find({'category' : category}).count()

    # update in database
    mongo.db.recipe_categories.update({'name': category},
        {
            '$set' : {
                'number_of_recipes' : counter
            }
        })


def validate_form(form, collection):
    """Returns an error list if the recipe, recipe collection or review form fails on validation"""
    
    # variable initialization
    max_title = 50
    max_ingredients = 500
    max_method = 1500
    max_recipe_img_URL = 250
    max_servings = 100
    max_category_name = 50
    max_category_img_URL = 250
    max_review = 250
    error_list = []

    # validate recipe form
    if collection == 'recipe':
        if not form['title'] or len(form['title']) > max_title:
            error_list.append('Title must not be empty or more than {} characters!'.format(max_title))

        if not form['ingredients'] or len(form['ingredients']) > max_ingredients:
            error_list.append('Ingredients must not be empty or more than {} characters!'.format(max_ingredients))

        if not form['method'] or len(form['method']) > max_method:
            error_list.append('Method must not be empty or more than {} characters!'.format(max_method))

        if 'appliance_categories' not in form:
            error_list.append('At least one of the appliances should be checked!')

        if not form['img_link'] or len(form['img_link']) > max_recipe_img_URL:
            error_list.append('Image URL must not be empty or more than {} characters!!'.format(max_recipe_img_URL))

        try:
            if not form['servings'] or int(form['servings']) > max_servings:
                error_list.append('Servings must not be empty or more than {}!'.format(max_servings))

        except ValueError:
            error_list.append('Servings is not a number!')
    
    # validate recipe category form
    elif collection == 'recipe_category':
        if not form['name'] or len(form['name']) > max_category_name:
            error_list.append('Category name must not be empty or more than {} characters!'.format(max_category_name))

        if not form['img_link'] or len(form['img_link']) > max_category_img_URL:
            error_list.append('Image URL must not be empty or more than {} characters!'.format(max_category_img_URL))
    
    # validate review form
    elif collection == 'review':
        if not form['review'] or len(form['review']) > max_review:
            error_list.append('Review must not be empty or more than {} characters!'.format(max_review))

    # return errors if there is any        
    return error_list


def validate_image(image):
    """Returns image URL if the URL is an image, otherwise returns a fallback URL"""
    
    # set fallback URL
    fallback_URL = url_for('static', filename='images/default.png')

    try:
        resp = requests.get(image)
        r = resp.headers.get('content-type')

        # test if the URL is valid and image
        if resp.status_code == 200:
            # URL is valid
            if r == 'image/jpeg' or r == 'image/bmp' or r == 'image/png' or r == 'image/gif':
                # URL is image
                return image
            else:
                # URL is not an image
                return fallback_URL
        else:
            # URL is invalid
            return fallback_URL
    except:
        # URL is invalid
        return fallback_URL


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
            recipes = mongo.db.recipes.find({"category": request.args['find']}).sort('title')
            if recipes.count() > 0:
                return render_template('search.html', recipes=recipes)
            else:
                return render_template('error.html', msg='No results found!')
    elif request.args['collection'] == 'recipe_categories':
        return render_template('search.html', recipe_categories=mongo.db.recipe_categories.find().sort('name'))
    elif request.args['collection'] == 'appliances':
        if request.args['find'] == 'all':
            return render_template('search.html', appliances=mongo.db.appliances.find().sort('brand'))
        else:
            appliances = mongo.db.appliances.find({"type": request.args['find']}).sort('brand')
            if appliances.count() > 0:
                return render_template('search.html', appliances=appliances)
            else:
                return render_template('error.html', msg='No results found!')
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
    if recipes.count() > 0:
        return render_template('navsearch.html', recipes=recipes)
    else:
        return render_template('error.html', msg='No result found!')


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
        return render_template('add_form.html', collection=mongo.db.recipe_categories.find().sort('name'), categories=mongo.db.appliance_categories.find().sort('name)'))
    elif request.args['collection'] == 'category':
        return render_template('add_form.html')
    else:
        return render_template('error.html', msg='Bad argument error! (/add_form)')


@app.route('/edit_form/<db_id>', methods=['GET'])
def edit_form(db_id):
    """Returns a form to edit an existing recipe or recipe category"""
    if request.args['collection'] == 'recipe':
        return render_template('edit_form.html', collection=mongo.db.recipe_categories.find().sort('name'), recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), categories=mongo.db.appliance_categories.find().sort('name'))
    elif request.args['collection'] == 'recipe_category':
        return render_template('edit_form.html', recipe_category=mongo.db.recipe_categories.find_one({"_id": ObjectId(db_id)}))
    else:
        return render_template('error.html', msg='Bad argument error! (/edit_form)')


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    """Inserts a recipe into the database and redirects to the list of all recipes"""

    # validate request form
    form = request.form
    appliance_list = request.form.getlist('appliance_categories')
    error_list = validate_form(form, 'recipe')

    if error_list == []:
        # validate image URL
        image_URL = validate_image(form['img_link'])

        # insert recipe
        recipe = {
            'title' :  request.form.get('title'),
            'category' : request.form.get('category'),
            'ingredients' : request.form.get('ingredients').split('\n'),
            'method' : request.form.get('method').split('\n'),
            'appliances' : request.form.getlist('appliance_categories'),
            'img_link' : image_URL,
            'reviews' : [],
            'servings' : request.form.get('servings'),
            'view_stat' : 0
        }
        mongo.db.recipes.insert_one(recipe)

        # update recipe numbers in category
        update_quantity_in_category(request.form.get('category'))

        # redirect to the landing page
        return redirect(url_for('index'))
    else:
        # send error list back to the form to correct mistakes
        return render_template('add_form.html', collection=mongo.db.recipe_categories.find().sort('name'), categories=mongo.db.appliance_categories.find().sort('name)'), errors=error_list, form=form, appliance_list=appliance_list)


@app.route('/insert_recipe_category', methods=['POST'])
def insert_recipe_category():
    """Inserts a recipe category into the database and redirects to the list of all recipe categories"""

    # validate request form
    form = request.form
    error_list = validate_form(form, 'recipe_category')

    if error_list == []:
        # validate image URL
        image_URL = validate_image(form['img_link'])

        # insert recipe category
        recipe_category = {
            'name' :  request.form.get('name'),
            'img_link' : image_URL,
            'number_of_recipes' : 0
        }
        mongo.db.recipe_categories.insert_one(recipe_category)

        # redirect to the landing page
        return redirect(url_for('index'))
    else:
        # send error list back to the form to correct mistakes
        return render_template('add_form.html', errors=error_list, form=form)


@app.route('/update_recipe/<db_id>', methods=['POST'])
def update_recipe(db_id):
    """Updates a recipe in the database and redirects to the list of all recipes"""

    # validate request form
    form = request.form
    appliance_list = request.form.getlist('appliance_categories')
    error_list = validate_form(form, 'recipe')

    if error_list == []:
        # validate image URL
        image_URL = validate_image(form['img_link'])

        # keep the old category name in case of change
        previous_category = mongo.db.recipes.find_one({'_id': ObjectId(db_id)})['category']
        
        # update recipe
        mongo.db.recipes.update({'_id': ObjectId(db_id)},
        {
            '$set': {
                'title' :  request.form.get('title'),
                'category' : request.form.get('category'),
                'ingredients' : request.form.get('ingredients').split('\n'),
                'method' : request.form.get('method').split('\n'),
                'appliances' : request.form.getlist('appliance_categories'),
                'img_link' : image_URL,
                'servings' : request.form.get('servings')
            }
        })

        # update counter in the old category (the recipe was taken from)
        update_quantity_in_category(previous_category)

        # update counter in the new category (the recipe was moved to)
        update_quantity_in_category(request.form.get('category'))

        # redirect to the landing page
        return redirect(url_for('index'))
    else:
        # send error list back to the form to correct mistakes
        return render_template('edit_form.html', collection=mongo.db.recipe_categories.find().sort('name'), recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), categories=mongo.db.appliance_categories.find().sort('name'), errors=error_list, form=form, appliance_list=appliance_list)


@app.route('/update_recipe_category/<db_id>', methods=['POST'])
def update_recipe_category(db_id):
    """Updates a recipe category in the database and redirects to the list of all recipe categories"""

    # validate request form
    form = request.form
    error_list = validate_form(form, 'recipe_category')

    if error_list == []:
        # validate image URL
        image_URL = validate_image(form['img_link'])

        # keep the old category name in case of change
        previous_name = mongo.db.recipe_categories.find_one({'_id': ObjectId(db_id)})['name']

        # update recipe category
        mongo.db.recipe_categories.update({'_id': ObjectId(db_id)},
        {
            '$set':{
                'name' :  request.form.get('name'),
                'img_link' : image_URL
            }
        })

        # update the old category name to the new one in the correspondent recipes
        mongo.db.recipes.update_many({'category' : previous_name},
        {
            '$set': {
                'category' : request.form.get('name')
            }
        })

        # redirect to the landing page
        return redirect(url_for('index'))
    else:
        # send error list back to the form to correct mistakes
        return render_template('edit_form.html', recipe_category=mongo.db.recipe_categories.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form)


@app.route('/delete_recipe/<db_id>')
def delete_recipe(db_id):
    """Removes a recipe from the database"""

    # keeps recipe category link
    category = mongo.db.recipes.find_one({'_id': ObjectId(db_id)})['category']

    # removes recipe
    mongo.db.recipes.remove({'_id': ObjectId(db_id)})

    # updates counter in the category
    update_quantity_in_category(category)

    # redirects to the landing page
    return redirect(url_for('index'))


@app.route('/delete_recipe_category/<db_id>')
def delete_recipe_category(db_id):
    """Removes a recipe category and all the recipes in the category from the database"""

    # determines the category name by id
    category_name = mongo.db.recipe_categories.find_one({'_id': ObjectId(db_id)})['name']

    # removes all the recipes in the category
    mongo.db.recipes.remove({'category' : category_name})

    # removes the recipe category
    mongo.db.recipe_categories.remove({'_id': ObjectId(db_id)})

    # redirects to the landing page
    return redirect(url_for('index'))


@app.route('/add_review/<db_id>', methods=['POST'])
def add_review(db_id):
    """Adds a review to a recipe or an appliance and refreshes the view page"""
    if request.args['collection'] == 'recipe':
        form = request.form
        error_list = validate_form(form, 'review')
        if error_list == []:
            mongo.db.recipes.update({'_id': ObjectId(db_id)},
            {
                '$push' : {
                    'reviews' : request.form.get('review')
                }
            })
            return redirect(url_for('view', db_id=db_id, collection='recipes'))
        else:
            return render_template('view.html', recipe=mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form)
    elif request.args['collection'] == 'appliance':
        form = request.form
        error_list = validate_form(form, 'review')
        if error_list == []:
            mongo.db.appliances.update({'_id': ObjectId(db_id)},
            {
                '$push' : {
                    'reviews' : request.form.get('review')
                }
            })
            return redirect(url_for('view', db_id=db_id, collection='appliances'))
        else:
            return render_template('view.html', appliance=mongo.db.appliances.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form)
    else:
        return render_template('error.html', msg='Bad argument error! (/add_review)')


@app.errorhandler(404)
def page_not_found(e):
    """Page not found."""
    return render_template('error.html', msg='Page not found error! (404)')


@app.errorhandler(400)
def handle_bad_request(e):
    """Bad request error."""
    return render_template('error.html', msg='Bad request error! (400)')


@app.errorhandler(500)
def server_error(e):
    """Internal server error."""
    return render_template('error.html', msg='Internal server error! (500)')


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=True)
