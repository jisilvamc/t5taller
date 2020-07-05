from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import requests
import json

url = "https://t5taller-jisilvamc.herokuapp.com/"  # "http://127.0.0.1:8000/"


class Lista:
    def __init__(self, tipo, id, *args):
        if tipo == "episode":
            self.url = url + "episodio/" + str(id)
        elif tipo == "character":
            self.url = url + "personaje/" + str(id)
        elif tipo == "location":
            self.url = url + "lugar/" + str(id)
        self.texto = paragraph(*args)


api = 'https://integracion-rick-morty-api.herokuapp.com/graphql'
# cha, loc, epi = api + 'character', api + 'location', api + 'episode'


def paragraph(*args):
    ans = str(args[0])
    if len(args) > 1:
        for a in args[1:]:
            ans += ", " + str(a)
    return ans

def index(request):
    epi_query = """query($page_num: Int!) {
        episodes (page: $page_num) {
        results {
          id
          name
          air_date
          episode
        }
        info {
          next
        }
      }
    }"""
    page = 1
    episodes = []
    while True:
        r = requests.post(api, json={'query': epi_query, 'variables': {"page_num": page}})
        json_data = json.loads(r.text)
        for episode in json_data["data"]["episodes"]["results"]:
            episodes.append(episode)
        if json_data["data"]["episodes"]["info"]["next"] == None:
            break
        else:
            page = json_data["data"]["episodes"]["info"]["next"]
    answer = []
    for e in episodes:
        answer.append(Lista("episode", e["id"], e["name"], e["air_date"], e["episode"]))
    context = {'answer': answer}
    return render(request, 'polls/index.html', context)


    iterador = get(epi).json()
    episodes = iterador["results"]
    while iterador["info"]["next"]:
        iterador = get(iterador["info"]["next"]).json()
        episodes.extend(iterador["results"])
    answer = []
    for e in episodes:
        answer.append(Lista("episode", e["id"], e["name"], e["air_date"], e["episode"]))
    context = {'answer': answer}
    return render(request, 'polls/index.html', context)

def episodio(request, epi_id):
    epi_query = """query($id: ID!) {
        episode (id: $id) {
          id
          name
          air_date
          episode
          characters {
            id
            name
          }
        }
    }"""
    r = requests.post(api, json={'query': epi_query, 'variables': {"id": epi_id}})
    json_data = json.loads(r.text)["data"]["episode"]
    texto = [json_data["name"], json_data["air_date"], json_data["episode"]]
    # Lista("episode", e["id"], e["name"], e["air_date"], e["episode"])
    answer = []
    for char in json_data["characters"]:
        answer.append(Lista("character", char["id"], char["name"])) 
    context = {'texto': texto, 'answer': answer}
    return render(request, 'polls/episodio.html', context)

def personaje(request, char_id):
    char_query = """query($id: ID!) {
        character (id: $id) {
          id
          name
          species
          status
          type
          gender
          image
          location {
            id
            name
          }
          origin {
            id
            name
          }
          episode {
            id
            name
          }
        }
    }"""
    r = requests.post(api, json={'query': char_query, 'variables': {"id": char_id}})
    json_data = json.loads(r.text)["data"]["character"]
    texto = [json_data["name"], json_data["status"], json_data["species"], json_data["type"], 
        json_data["gender"], json_data["location"]["name"], url + "lugar/" + json_data["location"]["id"]]
    if json_data["origin"]["name"] != "unknown":
        origen_nombre = json_data["origin"]["name"]
        origen_url = url + "lugar/" + json_data["origin"]["id"]
    else:
        origen_nombre = "unknown"
        origen_url = "unknown"
    foto = json_data["image"]
    episodes = []
    for e in json_data["episode"]:
        episodes.append([e["id"], e["name"]])
    answer = []
    for e in episodes:
        answer.append(Lista("episode", e[0], e[1]))
    context = {'texto': texto, 'answer': answer, 'origen': origen_nombre, 'origen_url': origen_url, 'foto': foto}
    return render(request, 'polls/personaje.html', context)

def lugar(request, loc_id):  # CAMBIAR ordenar
    loc_query = """query($id: ID!) {
        location (id: $id) {
          id
          name
          type
          dimension
          residents {
            id
            name
          }
        }
    }"""
    r = requests.post(api, json={'query': loc_query, 'variables': {"id": loc_id}})
    json_data = json.loads(r.text)["data"]["location"]
    texto = [json_data["name"], json_data["type"], json_data["dimension"]]
    characters = []
    for c in json_data["residents"]:
        characters.append([c["id"], c["name"]])
    answer = []
    for c in characters:
        answer.append(Lista("character", c[0], c[1]))
    context = {'texto': texto, 'answer': answer}
    return render(request, 'polls/lugar.html', context)

def busqueda(request):
    bus = request.GET.get('mytextbox')

    query = """query($page_num: Int!, $texto: String!) {
        episodes (page: $page_num, filter: {name: $texto}) {
        results {
          id
          name
        }
        info {
          next
        }
      }
    }"""
    page = 1
    episodes = []
    while True:
        r = requests.post(api, json={'query': query, 'variables': {"page_num": page, "texto": bus}})
        try:
            json_data = json.loads(r.text)
            for x in json_data["data"]["episodes"]["results"]:
                episodes.append([url + "episodio/" + x["id"], x["name"]])
            if json_data["data"]["episodes"]["info"]["next"] == None:
                break
            else:
                page = json_data["data"]["episodes"]["info"]["next"]
        except json.decoder.JSONDecodeError:
            print("No hay episodios en la búsqueda")
            episodes = ""
            break
    context = {"episodios": episodes}

    query = """query($page_num: Int!, $texto: String!) {
        characters (page: $page_num, filter: {name: $texto}) {
        results {
          id
          name
        }
        info {
          next
        }
      }
    }"""
    page = 1
    personajes = []
    while True:
        r = requests.post(api, json={'query': query, 'variables': {"page_num": page, "texto": bus}})
        print(r)
        print(r.text)
        try:
            json_data = json.loads(r.text)
            for x in json_data["data"]["characters"]["results"]:
                personajes.append([url + "personaje/" + x["id"], x["name"]])
            if json_data["data"]["characters"]["info"]["next"] == None:
                break
            else:
                page = json_data["data"]["characters"]["info"]["next"]
        except json.decoder.JSONDecodeError:
            print("No hay personajes en la búsqueda")
            personajes = ""
            break
    context["personajes"] = personajes

    query = """query($page_num: Int!, $texto: String!) {
        locations (page: $page_num, filter: {name: $texto}) {
        results {
          id
          name
        }
        info {
          next
        }
      }
    }"""
    page = 1
    lugares = []
    while True:
        r = requests.post(api, json={'query': query, 'variables': {"page_num": page, "texto": bus}})
        try:
            json_data = json.loads(r.text)
            for x in json_data["data"]["locations"]["results"]:
                lugares.append([url + "lugar/" + x["id"], x["name"]])
            if json_data["data"]["locations"]["info"]["next"] == None:
                break
            else:
                page = json_data["data"]["locations"]["info"]["next"]
        except json.decoder.JSONDecodeError:
            print("No hay lugares en la búsqueda")
            lugares = ""
            break
    context["lugares"] = lugares
    return render(request, 'polls/busqueda.html', context)
