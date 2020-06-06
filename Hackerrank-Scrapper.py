import os.path
import requests
import logging
from constants import output_dir, base_url, language_extension
from credentials import CSRF_TOKEN, COOKIE, USER_AGENT
from models import problem

logging.basicConfig(filename='scrapper.log', format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_extension(language):
    return language_extension.get(language, 'txt')


def create_parameters(offset, limit):
    return {'offset': offset, 'limit': limit}


class Scraper:
    HEADERS = {
        'x-csrf-token': CSRF_TOKEN,
        'cookie': COOKIE,
        'user-agent': USER_AGENT
    }

    def hr_scrapper(self):
        logger.info('Getting all the submission - Calling method: get_all_submissions')
        try:
            all_sub = scraper.get_all_submissions()
        except Exception as e:
            logger.error('Something Went wrong ' + str(e))
        for item in all_sub:
            status = item.get('status')
            challenge_id = item.get('id')
            challenge = item.get('challenge')
            if status == "Accepted":
                try:
                    details = scraper.get_challenge_details(challenge.get('slug'), challenge_id)
                    scraper.create_file(details)
                    print('Problem solution saved ' + str(challenge.get('name')))
                except Exception as e:
                    logger.error('Something went wrong' + str(e))
            else:
                print("Problem solution wasn't correct: " + challenge.get('name'))

        print("All Submissions Scrapped and Stored at +" + output_dir)

    def create_file(self, details):
        dir = os.path.join(output_dir, details.sub_domain)
        file_path = os.path.join(dir, details.domain)
        if not os.path.exists(dir):
            os.mkdir(dir)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        extension = get_extension(details.language)
        solution_file = open(file_path + "/" + details.name + "." + extension, "w")
        solution_file.writelines(details.code)
        solution_file.close()

    def get_all_submissions(self):
        url = base_url + '/submissions/'
        logger.debug('URL to get submission' + str(url))
        total: int = scraper.get_total_submission()
        final_list = {'models': [], 'total': 0}
        offset = 0
        limit = 100
        while True:
            params = create_parameters(offset, limit)
            try:
                data = requests.get(url=url, params=params, headers=self.HEADERS)
                final_list['models'].extend(data.json()['models'])
            except Exception as e:
                logger.error('Bad Response' + str(e))
                print("Something went wrong: " + str(e))
            if limit < total:
                offset = limit + 1
                limit = limit + 100
            else:
                break
        return final_list['models']

    def get_total_submission(self):
        url = base_url + '/submissions'
        logger.debug('getting Total Submission' + str(url))
        data = None
        params = create_parameters(0, 0)
        try:
            data = requests.get(url=url, params=params, headers=self.HEADERS)
        except Exception as e:
            logger.error('Bad Response ' + str(e))
            print("Bad Response: " + str(e))
        return data.json()['total']

    def get_challenge_details(self, slug, chal_id):
        logger.info('Get Challenge details: ' + str(slug))
        problem_details = scraper.get_problem_details(slug)
        code_details = scraper.get_challenge_submission(slug, chal_id)
        code = code_details.get('code')
        language = code_details.get('language')
        statement = problem_details.get('body_html')
        domain = problem_details.get('track').get('name')
        sub_domain = problem_details.get('track').get('track_name')
        return problem.Problem(slug, statement, code, domain, sub_domain, language)

    def get_problem_details(self, slug):
        logger.info('Get problem details: ' + str(slug))
        url = base_url + "/challenges/" + slug
        data = None
        try:
            data = requests.get(url=url, headers=self.HEADERS)
        except Exception as e:
            logger.error('Bad Response' + str(e))
        return data.json()['model']

    def get_challenge_submission(self, slug, chal_id):
        logger.info('Get Problem Code: ' + str(chal_id))
        url = base_url + "/challenges/" + slug + "/" + "submissions" + "/" + str(chal_id)
        data = None
        try:
            data = requests.get(url=url, headers=self.HEADERS)
        except Exception as e:
            logger.error('Bad Response' + str(e))
        return data.json()['model']


logger.info('Starts Scrapping')
print("Starting Application....")
scraper = Scraper()
scraper.hr_scrapper()

"""
problem_object = problem.Problem("ABC", "STATEMENT", "XYZ^XYZ", "Algo", "Practice", "java")
problem_object1 = problem.Problem("ABC", "STATEMENT", "XYZ^XYZ", "Algo", "Practice", "cpp")
problem_object2 = problem.Problem("ABC", "STATEMENT", "XYZ^XYZ", "Algo", "Advance", "java8")
problem_object3 = problem.Problem("ABC", "STATEMENT", "XYZ^XYZ", "Algo", "Medium", "java")
problem_object4 = problem.Problem("ABC", "STATEMENT", "XYZ^XYZ", "Java", "Practice", "java")
scraper.create_file(problem_object)
scraper.create_file(problem_object1)
scraper.create_file(problem_object2)
scraper.create_file(problem_object3)
scraper.create_file(problem_object4)
"""
