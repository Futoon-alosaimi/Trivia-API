import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app)

  
  @app.after_request
  def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

  

  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_category = [category.format() for category in categories]

    return jsonify({
            'success': True,
            'categories': formatted_category
        })
 

  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)
    categories = Category.query.all()
    formatted_category = {
        category.id: category.type for category in categories}

    return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': formatted_category,
            'total_questions': len(questions),
             'current categories ': None

        })
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)



      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

    
      
    

      return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
    except:
      abort(422)
    
 

  @app.route('/questions', methods=['POST'])
  def add_question():

            body = request.get_json()
            new_question = request.json.get('question')
            new_answer = request.json.get('answer')
            new_category = request.json.get('category')
            new_difficulty = request.json.get('difficulty')

            question1 = Question(new_question, new_answer,
                                new_category, new_difficulty)
            question1.insert()
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)



            return jsonify({
                'success': True,
                'question': question1.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

 

  @app.route('/search', methods=['POST'])
  def search_question():
   search_term = request.get_json()['searchTerm']
   data = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
   result = [question.format() for question in data]
   return jsonify({
     'success': True,
     'questions': result,
     'total_questions': len(Question.query.all())
   })
  
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):

    questions = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_selection(request, questions)
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all())
    })

  
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)

    try:
      if quiz_category:
        if quiz_category['id'] == 0:
          quiz = Question.query.all()
        else:
          quiz = Question.query.filter_by(Category=quiz_category['id']).all()
      if not quiz:
        return abort(422)
      selected = []
      for question in quiz:
        if question.id not in previous_questions:
         selected.append(question.format())
      if len(selected) != 0:
        result = random.choice(selected)
        return jsonify({
          'question': result
        })
      else:
        return jsonify({
          'question': False
        })
    except Exception:
            abort(422)


  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
        }), 400
   
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
        }), 404

  @app.errorhandler(422)
  def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
        }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
        }), 500

 

  
  return app

		
    
