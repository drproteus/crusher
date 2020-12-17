import factory
import factory.fuzzy
from faker import Faker

fake = Faker()


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Client"

    company = factory.Faker("company")
    metadata = factory.LazyAttribute(lambda o: {"about": fake.text()})


class VesselFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Vessel"

    client = factory.SubFactory(ClientFactory)
    name = factory.LazyAttribute(
        lambda o: " ".join([fake.military_ship(), fake.first_name()])
    )


class StaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.SKU"

    metadata = factory.LazyAttribute(
        lambda o: {
            "type": "staff",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "mailing_address": fake.address(),
        }
    )
    units = "hours"


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.SKU"

    metadata = factory.LazyAttribute(
        lambda o: {
            "type": "item",
            "name": fake.word(),
            "stock": 99,
            "upc": fake.upc_e(),
        }
    )
    units = "unit"


TRANSPORT_OPTIONS = ("UBER", "LYFT", "SELF", "TAXI", "REMOTE")


class TransportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.SKU"

    metadata = factory.LazyFunction(
        lambda: {"vendor": fake.random_element(TRANSPORT_OPTIONS), "type": "transport"}
    )
    units = "mile"


