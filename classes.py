import json
from abc import ABC, abstractmethod
from collections import Counter
from configparser import ParsingError
from datetime import datetime
from itertools import islice
from random import  sample

import requests as requests


class Vacancy:
    def __init__(self, vacancy):
        self.name= vacancy['name']
        self.employer = vacancy['employer']
        self.alternate_url = vacancy['alternate_url']
        self.published_at = vacancy['published_at']
        self.salary_from = vacancy['salary_from']
        self.salary_to = vacancy['salary_to']
        self.salary_currency = vacancy['salary_currency']

        self.area = vacancy['area']

    def __str__(self):
        if not self.salary_from and not self.salary_to:
            salary = "Не указана"
        else:
            salary_from, salary_to = "", ""
            if self.salary_from:
                salary_from = f'от {self.salary_from} {self.salary_currency}'
            if self.salary_to:
                salary_to = f'до {self.salary_to} {self.salary_currency}'
            salary = " ".join([salary_from,salary_to]).strip()

        return f""" 
        {self.name} 
        Работодатель: {self.employer}
        Уровень ЗП: {salary}
        Место: {self.area}
        Ссылка: {self.alternate_url}
        """





class Connector:
    def __init__(self, keyword, vacancies_json):
        self.keyword = keyword
        self.filename = f'{keyword.title()}.json'
        self.insert(vacancies_json)
        
    def insert(self, vacancies_json):
        "Загрулить в клас файл"
        with open(self.filename, "w",encoding="utf-8") as file:
            json.dump(vacancies_json, file, indent=4)
            
    def select(self):
        """
        Выбрать все вакансии
        :return: список вакансий
        """
        with open(self.filename, "r",encoding="utf-8") as file:
            vacancies = json.load(file)
        return [Vacancy(x) for x in vacancies]
    
    def sort_by_salary_from(self):
        """
        Сортирует список
        :return:список вакансий
        """
        desc = True if input(
            "> - DESC \n"
            "< - ASC \n"
             ).lower() == '>' else False
        vacancies = self.select()
        return sorted(vacancies, key=lambda x: (x.salary_from if x.salary_from else 0, x.salary_to if x.salary_to else 0),reverse=desc)

    def statistics_keyword(self):
        """
        Краткая статистика
        :return: список вакансий
        """
        vacancies = self.select()
        vacancies_return = []
        best_salary = 0
        count_salary = 0
        sum_salary = 0

        for item in range(len(vacancies)):
            vacancy = vacancies[item]
            if not vacancy.salary_from and not vacancy.salary_to:
                salary = 0
            else:
                count_salary +=1
                salary_from, salary_to = 0, 0
                if vacancy.salary_from:
                    salary_from = vacancy.salary_from
                if vacancy.salary_to:
                    salary_to = vacancy.salary_to

                if  salary_from > 0 and salary_to>0 :
                    salary = (salary_from + salary_to ) / 2
                else:
                    salary = salary_from + salary_to

                sum_salary += salary

            if salary > best_salary:
                best_salary = salary
                best_vacancy = item



        print(f""" 
    Ключевые слова: {self.keyword}
    Загружено вакансий: {len(vacancies)}
    Средняя зарплата: {round(sum_salary/count_salary,2)}
    Максимальная зарплата: {best_salary}
        
    Лучшая вакансия: """)
        vacancies_return.append(vacancies[best_vacancy])
        return vacancies_return

    def selectTop(self):
        """
        Самые дорогие вакансии
        :return: список вакансий
        """
        desc = True
        vacancies = self.select()
        vacanciesSort= sorted(vacancies,
                      key=lambda x: (x.salary_from if x.salary_from else 0, x.salary_to if x.salary_to else 0),
                      reverse=desc)



        return list(islice(vacanciesSort,3) )


    def selectLast(self):
        """
        Последние добавленые
        :return: список вакансий
        """
        desc = True
        vacancies = self.select()
        vacanciesSort= sorted(vacancies,
                      key=lambda x: (x.published_at ),
                      reverse=desc)


        return list(islice(vacanciesSort,3) )

    def select_random(self):
        """
        Список случайных вакансий
        :return: список вакансий
        """
        vacancies = self.select()
        return sample(vacancies,min(3,len(vacancies)))


class ParsingError(Exception):
    pass
    
class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

class HeadHunterAPI(Engine):
    url = "https://api.hh.ru/vacancies/"

    def __init__(self, keywords):
        self.params = {'page': 100,
                'per_page': None,
                'text': keywords,
                'archived': False,
                'area': '1',
                }
        self.headers = {
            "User_Agent": "MyImportantApp 1.0"
        }
        self.vacancies = []


    
    def get_request(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)

        if response.status_code != 200:
            raise ParsingError(f'Ошибка подключения к hh.ru! Статус:{response.status_code}')

        return response.json()["items"]

    def det_formatted_vacancies(self):
        formatted_vacancies = []
        # Currencies = get_Currencies()

        for vacancy in self.vacancies:

            formatted_vacancy = {
            "api": 'hh',
            "employer": vacancy["employer"]["name"],
            "name": vacancy['name'],
            "alternate_url":vacancy['alternate_url'],
            "published_at": vacancy['published_at'],
            'area': vacancy['area']['name']
            }
            if vacancy['salary']:
                formatted_vacancy["salary_from"] = vacancy['salary']['from']
                formatted_vacancy["salary_to"] = vacancy['salary']['to']
                formatted_vacancy["salary_currency"] = vacancy['salary']['currency']
            else:
                formatted_vacancy["salary_from"] = None
                formatted_vacancy["salary_to"] = None
                formatted_vacancy["salary_currency"] = None
            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """
        Получить вакансии
        :param pages_count:
        :return:
        """
        self.vacancies = []

        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f'({self.__class__.__name__}) Парсинг страницы {page+1} - ',end=' ')

            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:

                self.vacancies.extend(page_vacancies)
                print(f"Загружено { len(page_vacancies)} вакансий")
            if len(page_vacancies) == 0:
                break




class SuperJobAPI(Engine):
    url = "https://api.superjob.ru/2.0/vacancies/"

    def __init__(self, keywords):
        self.params = {'count': 20,
                'page': None,
                'keyword': keywords,
                'archive': False,
                'town': 4
                }
        self.headers = {
            "X-Api-App-Id": "v3.r.126959828.d69ac47c93594c6db358f41ab0cddffe5a852939.bc6c043f305dc3ea2a074d42e9103efb6c92600b"
        }
        self.vacancies = []


    def get_request(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f'Ошибка подключения к SuperJob.ru! Статус:{response.status_code}')
        return response.json()["objects"]

    def det_formatted_vacancies(self):
        formatted_vacancies = []
        # Currencies = get_Currencies()

        for vacancy in self.vacancies:
            # from datetime import datetime
            date_published = datetime.fromtimestamp(vacancy['date_published']).strftime("%Y-%m-%dT%H:%M:%S")

            formatted_vacancy = {
            "api": 'sj',
            "employer": vacancy["firm_name"],
            "name":vacancy['profession'],
            "alternate_url": vacancy['link'],
            "published_at": date_published,
            'area': vacancy['town']['title'],
            "salary_from" : vacancy['payment_from'],
            "salary_to" : vacancy['payment_to'],
            "salary_currency" : vacancy['currency'],
            }
            formatted_vacancies.append(formatted_vacancy)


        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        self.vacancies = []

        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f'({self.__class__.__name__}) Парсинг страницы {page+1} - ', end=' ')
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:

                self.vacancies.extend(page_vacancies)

                print(f"Загружено {len(page_vacancies)} вакансий")
            if len(page_vacancies) == 0:
                break

