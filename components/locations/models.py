from django.db import models
from core.models import BaseModel

class Country(BaseModel):
    name = models.CharField('Nome País', max_length=50)

    def __str__(self):
        return self.name

class State(BaseModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField('Nome', max_length=150)

    def __str__(self):
        return self.name

class Location(BaseModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.CharField('Cidade', max_length=100)

    def __str__(self):
        return f"{self.city} - {self.state.name} - {self.state.country.name}"