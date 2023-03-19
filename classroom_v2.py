from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import random

import classroom_v1 as v1

class Annoucement:
    def __init__(self, course_id, body):
        self.course_id_ = course_id
        self.body_ = body

    def post(self, creds): 
        try: 
            service = build('classroom', 'v1', credentials = creds)
            results = service.courses().announcements().create(courseId = self.course_id_, body = {
                'text': self.body_ 
            }).execute()
            return results

        except HttpError as error: print('An error occurred: %s' % error)

class Assignment:
    def __init__(self, course_id, title, due_date, due_time = 10): # 10 is 7pm
        self.course_id_ = course_id
        self.title_ = title
        self.descr_ = ''
        self.due_date_ = due_date
        self.due_time_ = due_time
        self.material_ = None

    def set_descr(self, descr): 
        self.descr = descr
        print('Updated description to:', descr, sep = '\n')

    def set_daily(self):
        daily, choices = [], []
        with open('tasks_daily.txt', 'r') as handle: 
            daily = [x.strip().replace('\n', '') for x in handle.readlines()]
        with open('tasks_choice.txt', 'r') as handle: 
            choices = [x.strip().replace('\n', '') for x in handle.readlines()]
        
        todays = {}
        for item in daily: todays[item] = random.choice([25, 30, 40])
        for item in random.sample(choices, k = 4): todays[item] = random.choice([25, 30, 40])

        descr = 'Dailies:\n'
        count = 0
        for key, value in todays.items():
            descr += f'[{str(value)} mins] {key}\n'

            count += 1
            if count == 4: descr += '\nChoose 3 out of the 4:\n'
        
        total = sum(todays.values())
        descr += f'\nTotal: {str(total - 40)} - {str(total - 25)} mins '
        descr += f'({str(round((total - 40) / 60, 2))} - {str(round((total - 25) / 60, 2))} h)'

        self.descr_ = descr

    def post(self, creds):
        # Checks
        assert self.due_date_ >= datetime.now()

        try: 
            service = build('classroom', 'v1', credentials = creds)
            results = service.courses().courseWork().create(courseId = self.course_id_, body = {
                'title': self.title_,
                'description': self.descr_,
                # 'material': self.material_,
                'dueDate': {
                    'day': self.due_date_.day,
                    'month': self.due_date_.month,
                    'year': self.due_date_.year
                },
                'dueTime': {
                    'hours': self.due_time_
                },
                'workType': 'ASSIGNMENT',
                'state': 'PUBLISHED'
            }).execute()
            return results

        except HttpError as error: print('An error occurred: %s' % error)

if __name__ == '__main__':
    creds = v1.authenticate()

    tdy = datetime.today() + 1
    daily = Assignment('504713357003', f'{tdy.month}/{tdy.day}', tdy)

    daily.set_daily()
    daily.post(creds)

