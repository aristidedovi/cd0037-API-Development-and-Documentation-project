import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import math

from sqlalchemy import desc, func


from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student','student','localhost:5433', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get("/api/v1/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))


    def test_get_questions_paginate(self):
        '''
        tests getting all questions with pagination
        '''
        #use client to get json response
        response = self.client().get("/api/v1/questions")
        data = json.loads(response.data)

        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # question should be presente in data
        self.assertIn('questions',data)

        # total_question should be present in data
        self.assertIn('total_questions', data)

        #question length should be greater than 0
        self.assertGreater(len(data['questions']), 0)

        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)
    

    def test_invalid_question_page(self):
        '''
        tests for invalid question page
        '''
        # get total question from DB
        total_questions = len(Question.query.all())

        # get response json, requesting the page 
        response = self.client().get(
            f'/api/v1/questions?page={math.ceil(total_questions / 10) + 2}'
        ) 
        data = json.loads(response.data)

        # status code should be 404
        self.assertEqual(response.status_code, 404)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'resources not found'
        self.assertEqual(data['message'], 'resource not found')


    def test_for_deleted_question_by_id(self):
        '''
        test for deleted question by here id
        '''
        # get all questions data
        response = self.client().get("/api/v1/questions")
        data = json.loads(response.data)

        # check questions length before deleted
        question_before_delete = len(Question.query.all())
        self.assertEqual(data['total_questions'], question_before_delete)

        # get last question in all questions
        question = Question.query.order_by(Question.id.desc()).first()
        # delete last question in all question
        question.delete()
        # check questions data length after deleted
        question_after_delete = len(Question.query.all())
        # check if question are very deleted
        self.assertEqual(question_before_delete - question_after_delete, 1)
    
    def test_post_new_question(self):
        '''
        test to post a new question
        '''
        # posting data for create new question
        response = self.client().post('/api/v1/questions', json={
            "question": "test question",
            "answer": "test answer",
            "difficulty": 3,
            "category": 1
        })
        data = json.loads(response.data)
        
        # check status code, if is 200
        self.assertEqual(response.status_code, 200)
        # check if success in data is True
        self.assertTrue(data['success'])
        # check if questions, id, question, total_questions is in data
        self.assertIn('questions', data)
        self.assertIn('id', data)
        self.assertIn('question', data)
        self.assertIn('total_questions', data)

        # questions and total_questions length should be more than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)
    

    def test_empty_post_question(self):
        '''
        test posting empty question json
        '''
        # posting null value for creating new question
        response = self.client().post('/api/v1/questions', json={})
        data = json.loads(response.data)

        # check if status code is 400
        self.assertEqual(response.status_code, 400)
        #check if success in data is False
        self.assertFalse(data['success'])
        #check if message is data is 'bad request'
        self.assertEqual(data['message'], 'bad request')

    
    def test_post_search_questions(self):
        '''
        test searching questions
        '''
        # post good search trem for search question
        response = self.client().post('/api/v1/questions/search', json={'searchTerm': 'title'})
        data = json.loads(response.data)

        # check if status code is 200
        self.assertEqual(response.status_code, 200)
        # check if success in data is True
        self.assertTrue(data['success'])
        # check if questions, total_question is in data
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        # check if questions, total_questions are greater than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        self.assertEqual(type(data['total_questions']), int)


    def test_invalid_post_search_questions(self):
        '''
        test invalid search for questions
        '''
        # post wrong search trem for search question
        response = self.client().post('/api/v1/questions/search', json={'searchTerm': 'hguguyhuy'})
        data = json.loads(response.data)

        # check if status code is 404
        self.assertEqual(response.status_code, 404)
        # check if success in data is False
        self.assertFalse(data['success'])
        # check if message in data is 'resource not found'
        self.assertEqual(data['message'], 'resource not found')

    def test_bad_post_search_questions(self):
        '''
        test search whit empty value
        '''
        # post null search trem for search question
        response = self.client().post('/api/v1/questions/search', json={'searchTerm': ''})
        data = json.loads(response.data)

        # check if status code is 400
        self.assertEqual(response.status_code, 400)
        # check if success in data is False
        self.assertFalse(data['success'])
        # check if message in data is 'bad request'
        self.assertEqual(data['message'], 'bad request')
    
    def test_get_catgory_questions(self):
        '''
        test to get questions by category
        '''
        # get one and random category 
        category = Category.query.order_by(func.random()).first()

        # get all questions from database by her category 
        response= self.client().get(f'/api/v1/categories/{category.id}/questions')
        data = json.loads(response.data)

        # check if status code is 200
        self.assertEqual(response.status_code, 200)
        # check if success in data is True
        self.assertTrue(data['success'])
        # check if questions, total_questions is in data
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        # check if questions, total_question is greater than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        self.assertEqual(type(data['total_questions']), int)
        # check if current_category in data is equal category id
        self.assertEqual(data['current_category'], category.type)

        # check if question, category id should be the same id from db
        for question in data['questions']:
            self.assertEqual(question['category'], category.id)
    
    def test_get_invalid_category(self):
        '''
        tests getting questions by invalid category
        '''
        # get the first random category from db
        category = Category.query.order_by(desc(Category.id)).first()
        # get response json, then load the data
        response = self.client().get(
            f'/api/v1/categories/{category.id + 1}/questions')
        data = json.loads(response.data)

        # check if status_code is 404
        self.assertEqual(response.status_code, 404)
        # check if success in data is False
        self.assertFalse(data['success'])
        # check if message in data is 'resource not found'
        self.assertEqual(data['message'], 'resource not found')

    def test_play_quiz(self):
        '''
        tests playing a quizs
        '''
        # query db for 2 random questions
        questions = Question.query.order_by(func.random()).limit(2).all()
        previous_questions = [question.id for question in questions]
        # post response json, then load the data
        response = self.client().post('/api/v1/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': {'id': 2}
        })
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # question should be present
        self.assertTrue(data['question'])

    def test_failed_play_quiz(self):
        '''
        tests playing a quizs with empty json
        '''
        # post empty json response json, then load the data
        response = self.client().post('/api/v1/quizzes', json={})
        data = json.loads(response.data)
        # status code should be 400
        self.assertEqual(response.status_code, 400)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'bad request'
        self.assertEqual(data['message'], 'bad request')





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()