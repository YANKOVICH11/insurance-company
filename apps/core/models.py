from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date
import uuid

class Branch(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"


class InsuranceType(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    base_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид страхования"
        verbose_name_plural = "Виды страхования"


class InsuranceAgent(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='agents')
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return self.full_name


class Client(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class InsuranceContract(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('expired', 'Истек'),
        ('pending', 'На рассмотрении'),
    ]
    
    contract_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts')
    agent = models.ForeignKey(InsuranceAgent, on_delete=models.CASCADE, related_name='contracts')
    insurance_type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    insurance_sum = models.DecimalField(max_digits=12, decimal_places=2)
    tariff_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def insurance_payment(self):
        return self.insurance_sum * (self.tariff_rate / 100)

    def __str__(self):
        return f"Договор {self.contract_number}"


class News(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    content = models.TextField()
    published_date = models.DateField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Glossary(models.Model):
    term = models.CharField(max_length=200)
    definition = models.TextField()
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.term


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    posted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    client_name = models.CharField(max_length=200)
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Отзыв от {self.client_name}"


class PromoCode(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('archived', 'В архиве'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"