from django.core.management.base import BaseCommand
from apps.core.models import *
from apps.users.models import CustomUser
from datetime import date, timedelta
import random
import uuid

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write("Заполнение базы данных...")
        
        # Очищаем старые данные
        InsuranceContract.objects.all().delete()
        PromoCode.objects.all().delete()
        Review.objects.all().delete()
        self.stdout.write("🗑️ Старые данные удалены")
        
        # 1. Филиалы
        branches = [
            Branch(name="Главный офис", address="г. Минск, пр. Независимости, 100", phone="+375 (29) 111-11-11"),
            Branch(name="Филиал Заводской", address="г. Минск, ул. Партизанская, 50", phone="+375 (29) 222-22-22"),
            Branch(name="Филиал Фрунзенский", address="г. Минск, ул. Притыцкого, 30", phone="+375 (29) 333-33-33"),
        ]
        for b in branches:
            b.save()
        self.stdout.write(f"✅ Создано {len(branches)} филиалов")
        
        # 2. Виды страхования
        types = [
            InsuranceType(name="КАСКО", description="Страхование автомобиля от угона и ущерба", commission_percent=15, base_rate=3.5),
            InsuranceType(name="ОСАГО", description="Обязательное страхование автогражданской ответственности", commission_percent=10, base_rate=2.0),
            InsuranceType(name="Медицинское", description="Добровольное медицинское страхование", commission_percent=20, base_rate=8.0),
            InsuranceType(name="Имущество", description="Страхование квартир и домов", commission_percent=12, base_rate=1.5),
            InsuranceType(name="Жизнь", description="Страхование жизни и здоровья", commission_percent=25, base_rate=5.0),
        ]
        for t in types:
            t.save()
        self.stdout.write(f"✅ Создано {len(types)} видов страхования")
        
        # 3. Агенты
        agents = [
            InsuranceAgent(first_name="Иван", last_name="Петров", phone="+375 (29) 123-45-67", branch=branches[0], is_active=True),
            InsuranceAgent(first_name="Мария", last_name="Сидорова", phone="+375 (29) 234-56-78", branch=branches[0], is_active=True),
            InsuranceAgent(first_name="Алексей", last_name="Иванов", phone="+375 (29) 345-67-89", branch=branches[1], is_active=True),
            InsuranceAgent(first_name="Елена", last_name="Козлова", phone="+375 (29) 456-78-90", branch=branches[1], is_active=True),
            InsuranceAgent(first_name="Дмитрий", last_name="Новиков", phone="+375 (29) 567-89-01", branch=branches[2], is_active=True),
        ]
        for a in agents:
            a.save()
        self.stdout.write(f"✅ Создано {len(agents)} агентов")
        
        # 4. Клиенты
        clients = [
            Client(first_name="Анна", last_name="Волкова", date_of_birth=date(1990, 5, 15), phone="+375 (29) 111-22-33", email="anna@example.com"),
            Client(first_name="Павел", last_name="Смирнов", date_of_birth=date(1985, 8, 20), phone="+375 (29) 222-33-44", email="pavel@example.com"),
            Client(first_name="Татьяна", last_name="Кузнецова", date_of_birth=date(1995, 3, 10), phone="+375 (29) 333-44-55", email="tatiana@example.com"),
            Client(first_name="Сергей", last_name="Михайлов", date_of_birth=date(1988, 11, 25), phone="+375 (29) 444-55-66", email="sergey@example.com"),
            Client(first_name="Наталья", last_name="Федорова", date_of_birth=date(1992, 7, 30), phone="+375 (29) 555-66-77", email="natalia@example.com"),
        ]
        for c in clients:
            c.save()
        self.stdout.write(f"✅ Создано {len(clients)} клиентов")
        
        # 5. Договоры (используем UUID для уникальности)
        for i in range(20):
            contract = InsuranceContract(
                contract_number=str(uuid.uuid4())[:13],
                client=random.choice(clients),
                agent=random.choice(agents),
                insurance_type=random.choice(types),
                branch=random.choice(branches),
                insurance_sum=random.randint(10000, 100000),
                tariff_rate=random.randint(1, 10),
                start_date=date.today() - timedelta(days=random.randint(1, 365)),
                status=random.choice(['active', 'active', 'active', 'pending']),
            )
            contract.save()
        self.stdout.write(f"✅ Создано 20 договоров")
        
        # 6. Новости
        news_list = [
            News(title="Новая программа страхования жизни", summary="Запущена новая программа с расширенным покрытием", content="Мы рады сообщить о запуске новой программы страхования жизни. Теперь вы можете застраховать свое здоровье и жизнь на выгодных условиях.", image="news/tamanna-rumee-mIqyYpSNq3o-unsplash_mc1wSHp.jpg", is_published=True),
            News(title="Скидки до 50% на ОСАГО", summary="Специальное предложение для новых клиентов", content="Только до конца месяца действуют скидки до 50% на оформление ОСАГО. Успейте сэкономить!", is_published=True),
            News(title="Открытие нового филиала", summary="Мы открыли новый офис в Московском районе", content="Компания продолжает расширяться! Новый филиал находится по адресу: ул. Колесникова, 15.", is_published=True),
            News(title="Онлайн-оформление страховки", summary="Теперь вы можете оформить страховку не выходя из дома", content="Запущен новый сервис онлайн-оформления. Выберите вид страхования, заполните форму и получите полис на email за 5 минут.", is_published=True),
        ]
        for n in news_list:
            n.save()
        self.stdout.write(f"✅ Создано {len(news_list)} новостей")
        
        # 7. Термины
        terms_list = [
            Glossary(term="Страховая сумма", definition="Денежная сумма, в пределах которой страховщик обязуется выплатить страховое возмещение при наступлении страхового случая."),
            Glossary(term="Страховая премия", definition="Плата за страхование, которую страхователь обязан уплатить страховщику в соответствии с договором страхования."),
            Glossary(term="Тарифная ставка", definition="Ставка страховой премии с единицы страховой суммы с учетом объекта страхования и характера страхового риска."),
            Glossary(term="Страховой случай", definition="Совершившееся событие, предусмотренное договором страхования, при наступлении которого возникает обязанность страховщика произвести страховую выплату."),
            Glossary(term="Франшиза", definition="Часть убытков страхователя, не подлежащая возмещению страховщиком."),
        ]
        for t in terms_list:
            t.save()
        self.stdout.write(f"✅ Создано {len(terms_list)} терминов")
        
        # 8. Сотрудники
        employees_list = [
            Employee(first_name="Анна", last_name="Ковалева", position="Генеральный директор", description="Руководство компанией", phone="+375 (29) 111-11-11", email="anna@zashita.by", branch=branches[0]),
            Employee(first_name="Игорь", last_name="Соколов", position="Руководитель отдела продаж", description="Управление отделом продаж", phone="+375 (29) 222-22-22", email="igor@zashita.by", branch=branches[0]),
            Employee(first_name="Ольга", last_name="Петрова", position="Главный бухгалтер", description="Финансовый учет и отчетность", phone="+375 (29) 333-33-33", email="olga@zashita.by", branch=branches[0]),
            Employee(first_name="Дмитрий", last_name="Сидоров", position="Старший страховой агент", description="Консультирование и оформление договоров", phone="+375 (29) 444-44-44", email="dmitry@zashita.by", branch=branches[1]),
            Employee(first_name="Екатерина", last_name="Васильева", position="Менеджер по работе с клиентами", description="Поддержка клиентов и решение вопросов", phone="+375 (29) 555-55-55", email="ekaterina@zashita.by", branch=branches[2]),
        ]
        for e in employees_list:
            e.save()
        self.stdout.write(f"✅ Создано {len(employees_list)} сотрудников")
        
        # 9. Вакансии
        vacancies_list = [
            Vacancy(title="Страховой агент", description="Поиск клиентов, консультирование, оформление договоров", requirements="Опыт работы от 1 года, коммуникабельность", location="Минск", is_active=True),
            Vacancy(title="Менеджер по продажам", description="Активные продажи страховых продуктов", requirements="Опыт продаж, знание ПК", location="Минск", is_active=True),
            Vacancy(title="Специалист по урегулированию убытков", description="Обработка страховых случаев, оценка ущерба", requirements="Юридическое или экономическое образование", location="Минск", is_active=True),
            Vacancy(title="Андеррайтер", description="Оценка рисков, расчет тарифов", requirements="Опыт работы от 2 лет", location="Минск", is_active=True),
        ]
        for v in vacancies_list:
            v.save()
        self.stdout.write(f"✅ Создано {len(vacancies_list)} вакансий")
        
        # 10. Промокоды (с проверкой на существование)
        promos_data = [
            {"code": "WELCOME2024", "discount_percent": 15, "description": "Приветственная скидка для новых клиентов", "valid_from": date.today(), "valid_to": date.today() + timedelta(days=30), "status": 'active'},
            {"code": "SUMMER24", "discount_percent": 20, "description": "Летняя распродажа страховок", "valid_from": date.today(), "valid_to": date.today() + timedelta(days=45), "status": 'active'},
            {"code": "FAMILY10", "discount_percent": 10, "description": "Скидка на семейное страхование", "valid_from": date.today(), "valid_to": date.today() + timedelta(days=60), "status": 'active'},
            {"code": "AUTO2024", "discount_percent": 12, "description": "Скидка на автострахование", "valid_from": date.today() - timedelta(days=30), "valid_to": date.today() - timedelta(days=1), "status": 'archived'},
        ]
        
        promos_created = 0
        for p_data in promos_data:
            promo, created = PromoCode.objects.get_or_create(
                code=p_data["code"],
                defaults={
                    'discount_percent': p_data["discount_percent"],
                    'description': p_data["description"],
                    'valid_from': p_data["valid_from"],
                    'valid_to': p_data["valid_to"],
                    'status': p_data["status"],
                }
            )
            if created:
                promos_created += 1
        self.stdout.write(f"✅ Создано {promos_created} новых промокодов")
        
        # 11. Создаем тестового пользователя для отзывов
        try:
            test_user, created = CustomUser.objects.get_or_create(
                username="testuser",
                defaults={
                    'email': "test@example.com",
                    'first_name': "Тестовый",
                    'last_name': "Пользователь",
                    'user_type': 'client'
                }
            )
            if created:
                test_user.set_password("test123")
                test_user.save()
                self.stdout.write("✅ Создан тестовый пользователь (логин: testuser, пароль: test123)")
            else:
                self.stdout.write("✅ Тестовый пользователь уже существует")
        except Exception as e:
            self.stdout.write(f"⚠️ Ошибка при создании пользователя: {e}")
            test_user = CustomUser.objects.first()
        
        # 12. Отзывы
        reviews_list = [
            Review(user=test_user, client_name="Алексей Иванов", rating=5, text="Отличная страховая компания! Быстро оформил КАСКО, все объяснили, помогли с выбором. Рекомендую!", date=date.today() - timedelta(days=5), is_approved=True),
            Review(user=test_user, client_name="Мария Смирнова", rating=5, text="Очень довольна обслуживанием. ДМС оформили за 20 минут. В клиниках без проблем принимают.", date=date.today() - timedelta(days=10), is_approved=True),
            Review(user=test_user, client_name="Сергей Козлов", rating=4, text="Хорошие тарифы на ОСАГО. Единственный минус - очередь в офисе.", date=date.today() - timedelta(days=15), is_approved=True),
            Review(user=test_user, client_name="Елена Петрова", rating=5, text="Лучшая страховая в городе! Уже 3 года страхую здесь всё - авто, квартиру, здоровье.", date=date.today() - timedelta(days=20), is_approved=True),
            Review(user=test_user, client_name="Дмитрий Новиков", rating=5, text="Профессиональные агенты, быстрое урегулирование убытков. Спасибо команде Защита!", date=date.today() - timedelta(days=25), is_approved=True),
            Review(user=test_user, client_name="Анна Волкова", rating=4, text="Хорошие условия страхования. Немного долго оформляли документы, но в целом все отлично.", date=date.today() - timedelta(days=30), is_approved=True),
        ]
        
        reviews_created = 0
        for r in reviews_list:
            try:
                r.save()
                reviews_created += 1
            except Exception as e:
                self.stdout.write(f"⚠️ Ошибка при сохранении отзыва: {e}")
        self.stdout.write(f"✅ Создано {reviews_created} отзывов")
        
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("🎉 БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(self.style.SUCCESS("\n📝 Тестовый пользователь:"))
        self.stdout.write(self.style.SUCCESS("   Логин: testuser"))
        self.stdout.write(self.style.SUCCESS("   Пароль: test123"))
        self.stdout.write(self.style.SUCCESS("\n🔑 Администратор:"))
        self.stdout.write(self.style.SUCCESS("   Выполните: python manage.py createsuperuser"))
        self.stdout.write(self.style.SUCCESS("\n🌐 Запустите сервер:"))
        self.stdout.write(self.style.SUCCESS("   python manage.py runserver"))
        self.stdout.write(self.style.SUCCESS("   Откройте: http://127.0.0.1:8000\n"))