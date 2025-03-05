from pymongo import MongoClient
import requests
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc

URI = "mongodb+srv://User:Password@cluster.krvhb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"

try:
    connection = MongoClient(URI)
    db = connection['StarWars']
    collection = db['Characters']
    print("Conexión exitosa a MongoDB")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

def obtenerDatos():
    try:
        url = "https://www.swapi.tech/api/people/?page=1&limit=100"
        response = requests.get(url)
        response.raise_for_status()  # Verifica si la petición fue exitosa
        data = response.json().get("results", [])

        personajes = []
        for item in data:
            detalle = requests.get(item["url"]).json().get("result", {}).get("properties", {})
            personajes.append({
                "name": detalle.get("name", "Desconocido"),
                "gender": detalle.get("gender", "unknown")
            })
            
        if collection.count_documents({}) == 0:
            collection.insert_many(personajes)
            print("Datos insertados en MongoDB")
        else:
            print("Los datos ya existen en la base de datos, no se insertarán nuevamente.")

        return personajes

    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return pd.DataFrame()
    
def crearGrafico():
        
    data = list(collection.find({}, {"_id": 0, "name": 1, "gender": 1}))

    df = pd.DataFrame(data)
    df_count = df["gender"].value_counts().reset_index()
    df_count.columns = ["gender", "count"]
    
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("Cantidad de Personajes de Star Wars por Género"),
        dcc.Graph(
            id="grafico",
            figure=px.bar(df_count, x="gender", y="count", title="Personajes de Star Wars por Género")
            )
        ])
    return app

#obtenerDatos()
app = crearGrafico()

if __name__ == "__main__":
    app.run_server(debug=True)
