import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """
    This class represents the trivia test case
    """

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_category(self):
        res = self.client().get('/categories')
        # load the data using json.load of the response.
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        # load the data using json.load of the response.
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_delete_question(self):
        res = self.client().delete('questions/15')
        # load the data using json.load of the response.
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_create_new_questions(self):

        question1 = {
            'question': 'add question',
            'answer': 'add answer',
            'category': 1,
            'difficulty': '1'
        }
        res = self.client().post('/questions', json=question1)
        # load the data using json.load of the response.
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_category(self):

        res = self.client().post('/categories/16/questions')
        # load the data using json.load of the response.
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_questions_422(self):

        res = self.client().get('/questions?page=5000')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertTrue(data['error'], 422)

    def test_delete_questions_422(self):
        res = self.client().delete('questions/5000')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertTrue(data['error'], 422)

    def test_questions_by_category_422(self):
        res = self.client().get('/categories/5000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_questions_search(self):
        res = self.client().post('/search', json={'searchTerm': "man"})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['status_message'], 'OK')

    def test_play_quizz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [],
                                 'quiz_category': {'type': 'Science',
                                                   'id': '1'}
                                                   })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['status_message'], 'OK')

# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()
