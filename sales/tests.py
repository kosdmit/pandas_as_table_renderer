import random

from django.test import TestCase
from mixer.backend.django import mixer
import mimesis
from mimesis.builtins import RussiaSpecProvider

# Create your tests here.


def create_test_data(count=10):
    for _ in range(count):
        person = mimesis.Person(locale=mimesis.Locale.RU)
        decision_maker = mixer.blend(
            'sales.decisionmaker',
            last_name=person.last_name(),
            first_name=person.first_name(),
            middle_name=RussiaSpecProvider().patronymic(),
            title=person.occupation(),
            phone=person.phone_number(),
            email=person.email(),
            birthdate=person.birthdate(),
        )

        company = mimesis.Finance(locale=mimesis.Locale.RU)
        customer = mixer.blend(
            'sales.customer',
            status=mixer.SELECT('sales.status'),
            inn=random.randint(100000000000, 999999999999),
            name=company.company(),
            decision_maker=decision_maker,
            source=mixer.RANDOM('search', 'exhibition', 'recommendation', 'website', 'call'),
            purchase_method=mixer.RANDOM('tender', 'free', 'demand', 'quarterly'),
            total_volume=mixer.RANDOM,
            target_volume=mixer.RANDOM,
            current_supplier=company.company(),
            consumed_items=', '.join((mimesis.Food(locale=mimesis.Locale.RU).fruit() for _ in range(5))),
            problematic=mimesis.Text(locale=mimesis.Locale.RU).sentence(),
            note=mimesis.Text(locale=mimesis.Locale.RU).sentence(),
        )
