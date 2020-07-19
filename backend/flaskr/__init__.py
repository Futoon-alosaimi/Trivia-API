import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.wrappers import Request, Response


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
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

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
        categories = Category.query.order_by(Category.type).all()
        return jsonify({
            'success': True,
            'categories': {
              Category.id: Category.type for Category in categories}
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        data = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, data)

        categories = Category.query.all()

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': {
                category.id: category.type for category in categories},
            'total_questions': len(data),
            'current_category ': None

        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            question.delete()
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():

        body = request.get_json()

        add_question = body.get('question')
        add_answer = body.get('answer')
        add_difficulty = body.get('difficulty')
        add_category = body.get('category')

        try:
            question = Question(question=add_question, answer=add_answer,
                                difficulty=add_difficulty,
                                category=add_category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except Exception:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)

        if search:
            results = Question.query.filter(
                Question.question.ilike(f'%{search}%')).all()

            return jsonify({
                'success': True,
                'questions': [
                  question.format() for question in results],
                'total_questions': len(Question.query.all()),
            })
        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        questions = Question.query.filter(
         Question.category == category_id).all()
        current_questions = paginate_questions(request, questions)
        return jsonify({
         'success': True,
         'questions': current_questions,
         'current_category': category_id,
         'total_questions': len(Question.query.all())
         })

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        body = request.get_json()
        prev_questions = body.get('previous_questions', [])
        category = body.get('quiz_category', None)
        selected = []

        if category['id'] == 0:
            quiz = Question.query.all()
        else:
            quiz = Question.query.filter_by(category=category['id']).all()

        for question in quiz:
            if question.id not in prev_questions:
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
