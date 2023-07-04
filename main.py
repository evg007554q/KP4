# Создание экземпляра класса для работы с API сайтов с вакансиями
from classes import HeadHunterAPI, SuperJobAPI, Connector


def main():
    vacancy_json = []

    # keyword = input("Введите ключевое слово для поиска")
    keyword = "Python"

    hh_api = HeadHunterAPI(keyword)
    superjob_api = SuperJobAPI(keyword)

    for api in (hh_api,superjob_api):
        api.get_vacancies(pages_count=10)
        vacancy_json.extend(api.det_formatted_vacancies())

    connector = Connector(keyword=keyword, vacancy_json=vacancy_json)

    while True:
        command = input(
            "1 - Статистика \n"
            "2 - 5 лучших вакансий \n"
            "3 - Все вакансии вакансии по порядку \n"
            "0 - Назад \n"
        )

        if command == '0':
            break
        elif command == '1':
            vacancies = connector.select()
        elif command == '3':
            vacancies = connector.sort_by_salary_from()

#
# # Получение вакансий с разных платформ
# hh_vacancies = hh_api.get_vacancies("Python")
# superjob_vacancies = superjob_api.get_vacancies("Python")
#
# # Создание экземпляра класса для работы с вакансиями
# vacancy = Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.", "Требования: опыт работы от 3 лет...")
#
# # Сохранение информации о вакансиях в файл
# json_saver = JSONSaver()
# json_saver.add_vacancy(vacancy)
# json_saver.get_vacancies_by_salary("100 000-150 000 руб.")
# json_saver.delete_vacancy(vacancy)
#
# # Функция для взаимодействия с пользователем
# def user_interaction():
#     platforms = ["HeadHunter", "SuperJob"]
#     search_query = input("Введите поисковый запрос: ")
#     top_n = int(input("Введите количество вакансий для вывода в топ N: "))
#     filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
#     filtered_vacancies = filter_vacancies(hh_vacancies, superjob_vacancies, filter_words)
#
#     if not filtered_vacancies:
#         print("Нет вакансий, соответствующих заданным критериям.")
#         return
#
#     sorted_vacancies = sort_vacancies(filtered_vacancies)
#     top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
#     print_vacancies(top_vacancies)
#
#
# if name == "main":
#     user_interaction()