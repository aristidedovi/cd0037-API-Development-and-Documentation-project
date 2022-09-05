# routes.py
# for rendering api routes
#from crypt import methods
from models import db
from models import Question, Category
from . import api1
from flask import abort, request, jsonify, current_app
from sqlalchemy import func

import random

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

"""
@TODO: Use the after_request decorator to set Access-Control-Allow
"""
@api1.after_request
def after_request(response):
    '''defining extra headers'''
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    response.headers.add('Content-Type', 'application/json')
    return response

"""
@TODO:
Create an endpoint to handle GET requests
for all available categories.
"""
@api1.route('/categories')
def get_categories():
    '''get all categories'''
    categories = Category.query.order_by(Category.id).all()

    categories_dictionairy = {category.id: category.type for category in categories}

    #print(categories)
    if len(categories) == 0:
        abort(404)
        
    return jsonify({
        'success': True,
        'categories': categories_dictionairy,
        'total_categories': len(Category.query.all())
    })

"""
@TODO:
Create an endpoint to handle GET requests for questions,
including pagination (every 10 questions).
This endpoint should return a list of questions,
number of total questions, current category, categories.

TEST: At this point, when you start the application
you should see questions and categories generated,
ten questions per page and pagination at the bottom of the screen for three pages.
Clicking on the page numbers should update the questions.
"""
@api1.route('/questions')
def get_questions():
    ''' Get all Question '''
    questions = Question.query.order_by(Question.id).all()

    ''' Paginate question Question '''
    current_questions = paginate_questions(request, questions)

    ''' Get all catégories'''
    categories = Category.query.all()
    categories_dictionairy = {category.id: category.type for category in categories}

    if len(current_questions) == 0:
        abort(404)
    
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': categories_dictionairy
    })

"""
@TODO:
Create an endpoint to DELETE question using a question ID.

TEST: When you click the trash icon next to a question, the question will be removed.
This removal will persist in the database and when you refresh the page.
"""
@api1.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    '''
    Delete question from database by here id
    '''
    try:
        question = Question.query.filter(Question.id == question_id).one_or_none()

        # return 404 if question is not available
        if question is None:
            abort(404)
        
        question.delete()

        return jsonify({
            'success': True,
            'delete': question_id
        })
    except:
        db.session.rollback()
        abort(422)


"""
@TODO:
Create an endpoint to POST a new question,
which will require the question and answer text,
category, and difficulty score.

TEST: When you submit a question on the "Add" tab,
the form will clear and the question will appear at the end of the last page
of the questions list in the "List" tab.
"""
@api1.route('/questions', methods=['POST'])
def post_new_question(): 
    body = request.get_json()

    if not body:
        abort(400)
    
    if (body.get('question') and body.get('answer') and body.get('difficulty') and body.get('category')):
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        if not 1 <= int(new_difficulty) < 6 :
            abort(400)
        
        try:
            question = Question(new_question, new_answer, new_category, new_difficulty)
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            if len(questions) == 0:
                abort(404)
            current_questions = paginate_questions(request, questions)
           
            return jsonify({
                'success': True,
                'id': question.id,
                'question': question.question,
                'questions': current_questions,
                'total_questions': len(questions)
            })
        except:
            db.session.rollback()
            abort(422)
    else:
        abort(400)

"""
@TODO:
Create a POST endpoint to get questions based on a search term.
It should return any questions for whom the search term
is a substring of the question.

TEST: Search by any phrase. The questions list will update to include
only question that include that string within their question.
Try using the word "title" to start.
"""
@api1.route('/questions/search', methods=['POST'])
def search_questions():
    ''' search for question in database '''
    body = request.get_json()

    if not body:
        abort(404)
    
    if body.get('searchTerm'):
        search_term = body.get('searchTerm')

        page = request.args.get('page', 1, type=int)
        
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%'))

        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(current_questions)
        })
    else:
        abort(400)

"""
@TODO:
Create a GET endpoint to get questions based on category.

TEST: In the "List" tab / main screen, clicking on one of the
categories in the left column will cause only questions of that
category to be shown.
"""
@api1.route('/categories/<category_id>/questions')
def get_questions_by_category(category_id):
    '''
    get all questions by specific category
    '''
    category = Category.query.filter(Category.id == category_id).one_or_none()

    if category is None:
        abort(404)
    
    page = request.args.get('page', 1, type=int)

    selection = Question.query.filter(Question.category == category.id).order_by(Question.id)

    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
        abort(404)
    
    

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(current_questions),
        'current_category': category.type
    })

"""
@TODO:
Create a POST endpoint to get questions to play the quiz.
This endpoint should take category and previous question parameters
and return a random questions within the given category,
if provided, and that is not one of the previous questions.

TEST: In the "Play" tab, after a user selects "All" or a category,
one question at a time is displayed, the user is allowed to answer
and shown whether they were correct or not.
"""
@api1.route('/quizzes', methods=['POST'])
def play_quiz():
    '''play quiz game'''
    # load the request body
    body = request.get_json()
    if not body:
        # posting an envalid json should return a 400 error.
        abort(400)
    if (body.get('previous_questions') is None or body.get('quiz_category') is None):
        # if previous_questions or quiz_category are missing, return a 400 error
        abort(400)
    previous_questions = body.get('previous_questions')
    if type(previous_questions) != list:
        # previous_questions should be a list, otherwise return a 400 error
        abort(400)
    category = body.get('quiz_category')
    # just incase, convert category id to integer
    category_id = int(category['id'])
    # insure that there are questions to be played.
    if category_id == 0:
        # if category id is 0, query the database for a random object of all questions
        selection = Question.query.order_by(func.random())
    else:
        # load a random object of questions from the specified category
        selection = Question.query.filter(
            Question.category == category_id).order_by(func.random())
    if not selection.all():
        # No questions available, abort with a 404 error
        abort(404)
    else:
        # load a random question from our previous query, which is not in the previous_questions list.
        question = selection.filter(Question.id.notin_(
            previous_questions)).first()
    if question is None:
        # all questions were played, returning a success message without a question signifies the end of the game
        return jsonify({
            'success': True
        })
    # Found a question that wasn't played before, let's return it to the user
    return jsonify({
        'success': True,
        'question': question.format()
    })



        


"""
@TODO:
Create error handlers for all expected errors
including 404 and 422.
"""
@api1.errorhandler(404)
def not_found(error):
    return jsonify({
       "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@api1.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 442,
        "message": "unprocessable"
    }), 422
    
@api1.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
    
@api1.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

