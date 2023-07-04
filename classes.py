import json
from abc import ABC, abstractmethod
from configparser import ParsingError

import requests as requests


class Vacancy:
    def __init__(self, vacancy):
        self.name= vacancy['name']
        self.employer = vacancy['employer']
        self.alternate_url = vacancy['alternate_url']
        self.published_at = vacancy['published_at']
        self.created_at = vacancy['created_at']
        self.salary_from = vacancy['salary_from']
        self.salary_to = vacancy['salary_to']
        self.salary_currency = vacancy['salary_currency']
        self.employment = vacancy['employment']
        self.employment_id = vacancy['employment_id']
        self.experience = vacancy['experience']
        self.experience_id = vacancy['experience_id']
        self.area = vacancy['area']

    def __str__(self):
        if not self.salary_from and not self.salary_to:
            salary = "Не указана"
        else:
            salary_from, salary_to = "", ""
            if self.salary_from:
                salary_from = f'от {self.salary_from}{self.salary_currency}'
            if self.salary_to:
                salary_to = f'до {self.salary_to}{self.salary_currency}'
            salary = " ".join([salary_from,salary_to]).strip()

        return f"""
        Работодатель: {self.employer}
        Вакансия: {self.employer}
        Уровень ЗП: {salary}
        Место: {self.area}
        Ссылка: {self.alternate_url}
        """





class Connector:
    def __init__(self, keyword, vacancies_json):
        self.filename=f'{keyword.title()}.json'
        self.insert(vacancies_json)
        
    def insert(self,vacancies_json):  
        with open(self.filename, "w",encoding="utf-8") as file:
            json.dump(vacancies_json, file, indent=4)
            
    def select(self):
        with open(self.filename, "r",encoding="utf-8") as file:
            vacancies = json.load(file)
        return [Vacancy(x) for x in vacancies]
    
    def sort_by_salary_from(self):
        desc = True if input(
            "> - DESC \n"
            "< - ASC \n"
             ).lower() == '>' else False
        vacancies = self.select()
        return sorted(vacancies, key=lambda x: (x.salary_from if x.salary_from else 0, x.salary_to if x.salary_to else 0),reverse=desc)
            

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
            "name":vacancy['name'],
            "alternate_url":vacancy['alternate_url'],
            "published_at": vacancy['published_at'],
            "created_at": vacancy['created_at'],
            "salary_from": vacancy['salary']['from'],
            "salary_to": vacancy['salary']['to'],
            "salary_currency": vacancy['salary']['currency'],
            "employment": vacancy['employment']['name'],
            "employment_id": vacancy['employment']['id'],
            "experience": vacancy['experience']['name'],
            "experience_id": vacancy['experience']['id'],
            'area': vacancy['area']['name']
            }
            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        self.vacancies = []

        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f'({self.__class__.__name__}) Парсинг страница {page} - ',end=' ')
            try:
                page_vacancies = self.get_request
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
        self.params = {'count': 100,
                'page': None,
                'text': keywords,
                'archived': False,
                }
        self.headers = {
            "X-Api-App-Id": "v3.r.126959828.d69ac47c93594c6db358f41ab0cddffe5a852939.bc6c043f305dc3ea2a074d42e9103efb6c92600b"
        }
        self.vacancies = []


    def get_request(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f'Ошибка подключения к hh.ru! Статус:{response.status_code}')
        return response.json()["objects"]

    def det_formatted_vacancies(self):
        formatted_vacancies = []
        # Currencies = get_Currencies()

        for vacancy in self.vacancies:
            formatted_vacancy = {
            "api": 'sj',
            "employer": vacancy["employer"]["name"],
            "name":vacancy['name'],
            "alternate_url":vacancy['alternate_url'],
            "published_at": vacancy['published_at'],
            "created_at": vacancy['created_at'],
            "employment": vacancy['employment']['name'],
            "employment_id": vacancy['employment']['id'],
            "experience": vacancy['experience']['name'],
            "experience_id": vacancy['experience']['id'],
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
        self.vacancies = []

        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f'({self.__class__.__name__}) Парсинш страница {page} - ', end=' ')
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено {len(page_vacancies)} вакансий")
            if len(page_vacancies) == 0:
                break

