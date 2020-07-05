from django.conf.urls import url
from . import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^busqueda/', views.busqueda, name="busqueda"),
url(r'^episodio/(?P<epi_id>[0-9]+)', views.episodio, name='episodio'),
url(r'^personaje/(?P<char_id>[0-9]+)', views.personaje, name='personaje'),
url(r'^lugar/(?P<loc_id>[0-9]+)', views.lugar, name='lugar'),
]