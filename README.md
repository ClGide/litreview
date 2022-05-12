# Using Django to build an MVP social media.

The following Python code is the project 9 of my Open ClassRooms path. The goal is to get accustomed to Django 4 framework's basic (the Django Template Language, the Models, Forms, Views and url paths). 

## 🔧 SET UP

The dependencies to install can be found in requirements.txt. Once the repository is forked, you have to go to the litreview/litreview folder using the terminal. The command activiting the local server is `python manage.py runserver`. Once the local server is activated, you can look through the project with the browser of your choice.  

## 📄 Description

Litreview's goal is to allow readers to request and read reviews on articles and books. The MVP is divided into four set of functionalities : **login/signup, feed, posts, following**. In order to access all the other functionalities, a user need to create an account. It's pretty straight forward: username + password + confirm password. Then, in the **feed** he can access reviews or requests for reviews (tickets) from people he follows. He can also post reviews in response to other users tickets or on his own. Moreover, he can request reviews on books/articles he's interested in. In **posts**, the user can scroll through, edit or delete his posts. Finally, in **following** he can follow or unfollow other users. Furthermore, he can look at the table of his followers. 

The implementation leverage Django's powerful procedure. When a request is sent to the user, settings.py is used to choose the app inside the project able to handle it. In our case, all requests are going to be handled by the app named base. url.py is the first script visited in the app. The urlpatterns list tell Django which view can handle the request. Then, the corresponding class or function in views.py does the main work. If data needs to be retrieved from or saved to the DB, it handles it. We use Django's Object Relational Mapper (models.py) to reach the database. In the case where the user needs to input some data, the view leverage the class/functions from forms.py or Django's built-in forms. Finally, it uses the templates to dynamically create HTML files. 

## 👷‍♂️ Contributors

Gide Rutazihana, student, giderutazihana81@gmail.com Ashutosh Purushottam, mentor

## License
There's no license
