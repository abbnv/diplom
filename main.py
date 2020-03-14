import requests
import json
import time


# Небольшой класс для обработки исключений
class APIError(Exception):
    def __init__(self, text, error_code):
        self.text = text
        self.error_code = error_code

        print("API VK Вернул ошибку")
        print("Ошибка:", self.text)
        print("Код ошибки:", self.error_code)

        print("---" * 30)


class VK:
    URL = 'https://api.vk.com/method/'
    API_VERSION = '5.52'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def run(self):
        user_groups_list_set = set(self.get_user_groups())
        user_friends_group_list_set = set(self.get_user_friends_groups())

        result = user_groups_list_set.difference(user_friends_group_list_set)
        result = list(result)

        print("Ура, вот результат — группы пользователя, в которых не состоит никто из друзей.")
        print(result)

        groups_result = []
        for group_info in result:
            response = self.make_request('groups.getById', group_id=group_info, fields='members_count')
            response = response['response'][0]
            groups_result.append({
                'name': response['name'],
                'gid': response['id'],
                'members_count': response['members_count']
            })

        print(groups_result)

        with open("groups.json", 'w', encoding="utf-8") as f:
            json.dump(groups_result, f, indent=2, ensure_ascii=False)

    def make_request(self, method, **data):
        # теперь для остальных методов будем делать execute с полученным user_id
        params = {
            'v': self.API_VERSION,
            'access_token': self.token,
        }
        params.update(data)

        response = requests.post(url=f'{self.URL}{method}', params=params)
        return response.json()

    def get_user_groups(self):

        print(f"Получаем список групп {self.user_id}")

        response = self.make_request('groups.get')

        print(f"Список групп: {response['response']['items']}")
        print("===" * 10)

        return response['response']['items']

    def get_user_friends_groups(self):
        print(f"Получаем список друзей {self.user_id}")

        response = self.make_request('friends.get')

        user_friends_count = response['response']['count']
        user_friends_list = response['response']['items']

        print(f'У жервы {self.user_id} друзей: {user_friends_count}')
        print(f'Вот их ID: {user_friends_list}')

        print("===" * 10)

        print("Получаем список групп этих друзей")
        # test_list = [4929, 7858, 11952, 48807, 58439, 71491, 75458, 78540, 105932, 143611, 144253, 193264, 209254]
        all_friends_group_list = []

        i = 0
        for number, user in enumerate(user_friends_list):
            try:
                response = self.make_request('groups.get', user_id=user)
                if 'error' in response:
                    raise APIError(text=response['error']['error_msg'], error_code=response['error']['error_code'])
                else:
                    user_friends_groups_count = response['response']['count']
                    user_friends_groups_list = response['response']['items']
                    print(f'У друга жертвы #{number} с ID: {user} групп: {user_friends_groups_count}')
                    print(f'Вот их ID: {user_friends_groups_list}')
                    print("---" * 30)

                for gr in user_friends_groups_list:
                    all_friends_group_list.append(gr)
                i += 1
            except APIError as e:
                print(e)
                if response['error']['error_msg'] == 6:
                    i -= 1
                    print("Заснём на пару секунд...")
                    time.sleep(2)

        print("===" * 10)

        print("Вот список всех групп всех друзей в одном списке:")
        print(all_friends_group_list)
        return all_friends_group_list


if __name__ == '__main__':
    TOKEN = input("Введите токен: ")
    USER_ID = input("Введите user_id: ")
    # '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
    # eshmargunov
    friends = VK(token=TOKEN, user_id=USER_ID)
    friends.run()

