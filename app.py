import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd

# Configuração do Streamlit
st.set_page_config(page_title="Células El Shaddai", layout="wide")
st.markdown("""
    <h1 style='text-align: center; font-size: 24px;'>Encontre uma célula da El Shaddai perto de você!</h1>
""", unsafe_allow_html=True)

# Carregar os dados do JSON com validação
json_file = "celulas_com_coordenadas.json"
cell_groups = []
try:
    with open(json_file, "r", encoding="utf-8") as f:
        data = f.read()
        if data.strip():  # Verifica se o arquivo não está vazio
            cell_groups = json.loads(data)
        else:
            st.error("O arquivo JSON está vazio.")
except (FileNotFoundError, json.JSONDecodeError):
    st.error("Erro ao carregar os dados. Verifique se o arquivo JSON está disponível e válido.")

# Exibir o mapa
st.markdown("""
    <h2 style='text-align: center;'>Mapa das Células</h2>
""", unsafe_allow_html=True)
m = folium.Map(location=[-20.468189, -54.618708], zoom_start=12)

for cell in cell_groups:
    coords = cell.get("COORDENADAS", {})
    latitude = coords.get("latitude")
    longitude = coords.get("longitude")
    
    if latitude and longitude:
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
        popup_text = f"""
            <b>{cell['LIDERES DA CELULA']}</b> ({cell['TIPO DE CELULA']})<br>
            {cell['ENDERECO']}<br>
            <a href='{google_maps_url}' target='_blank' style='color: blue; text-decoration: none;'>📍 Rotas no Google Maps</a>
        """
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

st_folium(m, use_container_width=True, height=700)

# Exibir lista de células abaixo do mapa
st.markdown("""
    <h2 style='text-align: center;'>Lista de Células</h2>
""", unsafe_allow_html=True)

if cell_groups:
    df = pd.DataFrame(cell_groups)
    df = df[["LIDERES DA CELULA", "LIDERES DA REDE", "TIPO DE CELULA", "ENDERECO", "COORDENADAS"]]
    
    # Criar coluna de botões para rotas no Google Maps
    def create_route_button(coords):
        if coords:
            latitude, longitude = coords['latitude'], coords['longitude']
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
            return f"<a href='{google_maps_url}' target='_blank'><button style='background-color:#008CBA; color:white; padding:5px 10px; border:none; border-radius:5px;'>📍 Rota</button></a>"
        return ""
    
    df["Rotas"] = df["COORDENADAS"].apply(create_route_button)
    df = df.drop(columns=["COORDENADAS"])  # Remover a coluna de coordenadas para exibição limpa
    
    # Adicionar filtro de busca com botão
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input("Buscar célula por líder, tipo ou endereço:")
    with col2:
        if st.button("Buscar"):
            st.experimental_rerun()
    
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)]
    
    # Exibir tabela com botões clicáveis e cabeçalhos alinhados à esquerda
    st.markdown(
        df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    st.markdown("""
        <style>
            table { width: 100%; }
            th { text-align: left !important; }
            input[type=text] { width: 100%; padding: 8px; }
            button { width: 100%; padding: 8px; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.write("Nenhuma célula encontrada.")

# Ajustar layout responsivo para melhor experiência em telas menores
st.markdown("""
    <style>
        @media (max-width: 768px) {
            .block-container { padding: 1rem; }
            h1, h2 { font-size: 20px !important; text-align: center !important; }
        }
    </style>
""", unsafe_allow_html=True)
