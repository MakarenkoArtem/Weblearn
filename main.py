from flask import Flask, render_template
from flask_restful import reqparse, abort, Api, Resource
from data import db_session, jobs_api, users_api
# from api_2.jobs_rsource import JobsResource
import requests

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/users_show/<int:user_id>')
def index(user_id):
    get = requests.get(f'http://127.0.0.1:8080/api/users/{user_id}').json()
    print(get)
    if 'error' in get.keys():
        return get
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={get['city_from']}&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(toponym_coodrinates.split())}&z=9&l=sat"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return render_template("users_show.html", pic='map.png', name=get['name'] + " " + get['surname'], city=get['city_from'])


def main():
    db_session.global_init("db/base_date.db")
    '''try:
        user = User()
        user.name = "Пользователь 1"
        user.about = "биография пользователя 1"
        user.email = "email@email.ru"
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
    except Exception as e:
        print(e.__class__.__name__, e)'''
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
