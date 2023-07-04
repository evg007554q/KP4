# Создание экземпляра класса для работы с API сайтов с вакансиями
from classes import HeadHunterAPI, SuperJobAPI, Connector


def main():
    finish = False
    while not finish:
        # Первый уровень меню только ввод ключевого слова
        vacancy_json = []

        keyword = input("Введите ключевое слово для поиска \n")

        hh_api = HeadHunterAPI(keyword)
        superjob_api = SuperJobAPI(keyword)

        # загрузка из hh_api
        hh_api.get_vacancies(pages_count=10)
        vacancy_json.extend(hh_api.det_formatted_vacancies())

        # загрузка из superjob_api
        superjob_api.get_vacancies(pages_count=10)
        vacancy_json.extend(superjob_api.det_formatted_vacancies())

        connector = Connector(keyword=keyword, vacancies_json=vacancy_json)

        while True:
            # 2 уровень меню
            # вывод вакансий, возврат назад, выход
            command = input(
                "1 - Статистика \n"
                "2 - 3 лучших вакансий \n"
                "3 - 3 последних вакансий \n"
                "4 - Мне повезет \n"
                "9 - Назад \n"
                "0 - Выход \n"
            )

            if command == '0':
                finish = True
                break
            elif command == '9':
                break
            elif command == '1':
                vacancies = connector.statistics_keyword()
            elif command == '2':
                vacancies = connector.selectTop()
            elif command == '3':
                vacancies = connector.selectLast()
            elif command == '4':
                print('Попробуйте эти вакансии - вам точно повезет ')
                vacancies = connector.select_random()

            for vacancy in vacancies:
                  print(vacancy)



if __name__ == "__main__":
    main()