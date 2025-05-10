# utils.py
from statsbombpy import sb
import pandas as pd
from mplsoccer import VerticalPitch as Pitch
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


def load_and_resize_image_url(image_url, final_size=(128, 160), aspect_ratio=4/5):
    # Faz o download da imagem a partir do URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Resto do código permanece o mesmo
    width, height = img.size

    # Calcula a nova largura e altura mantendo a proporção desejada
    if width / height > aspect_ratio:
        new_width = int(height * aspect_ratio)
        new_height = height
    else:
        new_width = width
        new_height = int(width / aspect_ratio)

    # Calcula as coordenadas para o corte centralizado
    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2

    # Recorta e redimensiona a imagem
    img = img.crop((left, top, right, bottom))
    img = img.resize(final_size, Image.LANCZOS)

    return img

def set_light_mode():
    st.markdown(
        """
        <style>
        /* Define o fundo da página e o texto em modo claro */
        .stApp {
            background-color: #ffffff; /* Fundo branco */
            color: #000000; /* Texto preto */
        }

        /* Define o fundo claro para componentes interativos */
        .stTextInput, .stSelectbox {
            background-color: #f8f9fa;
            color: #333333;
        }

        /* Estilo personalizado para botões com borda cinza escura e fundo cinza claro */
        .stButton>button {
            background-color: #ffffff; /* Fundo cinza claro */
            color: #000000; /* Texto preto */
            border: 2px solid #a9a9a9; /* Contorno cinza escuro */
            padding: 10px 20px;
            border-radius: 8px; /* Bordas levemente arredondadas */
            font-size: 16px;
            font-weight: bold;
        }

        /* Efeito de hover para os botões */
        .stButton>button:hover {
            background-color: #d3d3d3; /* Fundo cinza mais escuro no hover */
            border-color: #8c8c8c; /* Borda cinza escuro no hover */
            color: #000000;
        }

        /* Estilo para cabeçalhos */
        h1, h2, h3, h4, h5, h6 {
            color: #000000; /* Cor preta para os cabeçalhos */
        }
        
        /* Remove fundo escuro nos containers */
        .css-1adrfps {
            background-color: #ffffff !important;
        }

        div[data-testid="stMetricLabel"] {
            color: black !important;
    }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def calculate_xA(events, player_name):
    # Filtra os eventos do jogador e encontra as assistências de chute
    player_events = events[events['player'] == player_name]
    
    xA_value = (
        events.loc[np.clip(player_events.index + 1, 0, len(events) - 1), 'shot_statsbomb_xg'].fillna(0).sum() +
        events.loc[np.clip(player_events.index + 2, 0, len(events) - 1), 'shot_statsbomb_xg'].fillna(0).sum()
    )


    return xA_value


def calculate_xT(player_events):
    
    

    xt_url = 'https://karun.in/blog/data/open_xt_12x8_v1.json'
    
 
    response = requests.get(xt_url)
    xt_grid = np.array(response.json())

    def get_xt_value(x, y, xt_grid):
        grid_x = min(int(x / (120 / 12)), 11)
        grid_y = min(int(y / (80 / 8)), 7)
        return xt_grid[grid_y, grid_x]
    

    player_events['xT_start'] = np.nan
    player_events['xT_end'] = np.nan
    player_events['xT_delta'] = np.nan
    

    for idx, event in player_events.iterrows():
        if (event['type'] == 'Carry') or (pd.isna(event.get('pass_outcome')) and event['type'] == 'Pass'):

            start_location = event['location']
            end_location = event['pass_end_location'] if event['type'] == 'Pass' else event['carry_end_location']
    

            if start_location and end_location:
                x_start, y_start = start_location
                x_end, y_end = end_location

                xT_start = get_xt_value(x_start, y_start, xt_grid)
                xT_end = get_xt_value(x_end, y_end, xt_grid)
                xT_delta = xT_end - xT_start
    
                # Atualizar o DataFrame
                player_events.at[idx, 'xT_start'] = xT_start
                player_events.at[idx, 'xT_end'] = xT_end
                player_events.at[idx, 'xT_delta'] = xT_delta
    

    xt_passes = player_events[player_events['type'] == 'Pass']['xT_delta'].fillna(0).sum()
    xt_carries = player_events[player_events['type'].isin(['Carry'])]['xT_delta'].fillna(0).sum()
    
    return xt_passes,xt_carries

def crop_figure(fig, height_crop_percent=0.05,width_crop_percent = 0.275):
    # Salvar o gráfico temporariamente em um buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    

    img = Image.open(buf)
    width, height = img.size
    

    left = int(width * width_crop_percent)
    top = int(height * height_crop_percent)
    right = width - left
    bottom = height - top
    
    # Recortar a imagem
    img = img.crop((left, top, right, bottom))
    

    return img

def load_and_resize_image(player_name, final_size=(128, 160), aspect_ratio = 4/5):

    file_path = f"images/{player_name}.jpg"
    

    img = Image.open(file_path)
    

    width, height = img.size
    

    
    if width / height > aspect_ratio:

        new_width = int(height * aspect_ratio)
        new_height = height
    else:

        new_width = width
        new_height = int(width / aspect_ratio)
    

    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2
    

    img = img.crop((left, top, right, bottom))
    img = img.resize(final_size, Image.LANCZOS)
    
    return img




def get_competitions():
    competitions = sb.competitions()
    return competitions

def get_matches(competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    return matches

def get_events_competition(competition_id, season_id):
    matches = get_matches(competition_id, season_id)
    events_list = []

    for _, match in matches.iterrows():
        events_df = sb.events(match_id=match['match_id'], flatten_attrs=True)
 
        events_list.append(events_df)

    if events_list:
        all_events = pd.concat(events_list).reset_index()
        return all_events
    else:
        return pd.DataFrame()
def get_player_events_competition(events, player_name):

    player_events = events[events['player'] == player_name]

    
    return player_events


def plot_passes(events_df, title=''):
    pitch = Pitch()
    fig, ax = pitch.draw()

    passes = events_df[(events_df['type'] == 'Pass') & (events_df['pass_outcome'].isna())]

    if passes.empty:
        return fig

    pass_start_x = passes['location'].apply(lambda loc: loc[0])
    pass_start_y = passes['location'].apply(lambda loc: loc[1])
    pass_end_x = passes['pass_end_location'].apply(lambda loc: loc[0])
    pass_end_y = passes['pass_end_location'].apply(lambda loc: loc[1])
    
    pitch.arrows(pass_start_x, pass_start_y, pass_end_x, pass_end_y, ax=ax, width=1,  color='black', alpha = 0.2)
    
    key_passes = passes[(passes['xT_delta'] >= 0.05)]
    
    if key_passes.empty:
        return fig
    pass_start_x = key_passes['location'].apply(lambda loc: loc[0])
    pass_start_y = key_passes['location'].apply(lambda loc: loc[1])
    pass_end_x = key_passes['pass_end_location'].apply(lambda loc: loc[0])
    pass_end_y = key_passes['pass_end_location'].apply(lambda loc: loc[1])
    
    pitch.arrows(pass_start_x, pass_start_y, pass_end_x, pass_end_y, ax=ax, width=2,  color='black', alpha = 0.8)
    ax.set_title(title)

    return fig

def plot_carries(events_df, title=''):
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()

    carries = events_df[events_df['type'] == 'Carry']

    if carries.empty:
        return fig

    carry_start_x = carries['location'].apply(lambda loc: loc[0])
    carry_start_y = carries['location'].apply(lambda loc: loc[1])
    carry_end_x = carries['carry_end_location'].apply(lambda loc: loc[0])
    carry_end_y = carries['carry_end_location'].apply(lambda loc: loc[1])

    pitch.arrows(carry_start_x, carry_start_y, carry_end_x, carry_end_y, ax=ax, width=1.5, color='black', alpha = 0.2)
    
    
    key_carries = carries[carries['xT_delta'] >= 0.025]
    if key_carries.empty:
        return fig
    carry_start_x = key_carries['location'].apply(lambda loc: loc[0])
    carry_start_y = key_carries['location'].apply(lambda loc: loc[1])
    carry_end_x = key_carries['carry_end_location'].apply(lambda loc: loc[0])
    carry_end_y = key_carries['carry_end_location'].apply(lambda loc: loc[1])
    
    pitch.arrows(carry_start_x, carry_start_y, carry_end_x, carry_end_y, ax=ax, width=2,  color='black', alpha = 0.8)
    ax.set_title(title)

    return fig




def plot_reception_actions(events_df, title=''):

    pitch = Pitch(line_zorder=2)

    fig, ax = pitch.draw()


    reception_types = ['Ball Receipt*']
    reception_events = events_df[events_df['type'].isin(reception_types)]

    if reception_events.empty:
        return fig


    x = reception_events['location'].apply(lambda loc: loc[0])
    y = reception_events['location'].apply(lambda loc: loc[1])


    x = np.array(x)
    y = np.array(y)


    pitch.kdeplot(x, y, ax=ax, cmap='Greys', alpha=1, thresh=0.5, shade=True,
                  levels=100, n_levels=10, cut=1, zorder=1, fill=True)

    ax.set_title(title)
    return fig



def plot_shots(events_df, title=''):
    pitch = Pitch()
    fig, ax = pitch.draw()

    shots = events_df[events_df['type'] == 'Shot']

    if shots.empty:
        return fig


    goals = shots[shots['shot_outcome'] == 'Goal']
    non_goals = shots[shots['shot_outcome'] != 'Goal']



    if not non_goals.empty:
        non_goal_x = non_goals['location'].apply(lambda loc: loc[0])
        non_goal_y = non_goals['location'].apply(lambda loc: loc[1])
        non_goal_s = non_goals['shot_statsbomb_xg'].apply(lambda x: max(x, 0.075)*250)
        pitch.scatter(non_goal_x, non_goal_y, ax=ax, edgecolors='black', c='black', s=non_goal_s, alpha = 0.25)


    if not goals.empty:
        goal_x = goals['location'].apply(lambda loc: loc[0])
        goal_y = goals['location'].apply(lambda loc: loc[1])
        goal_s = goals['shot_statsbomb_xg'].apply(lambda x: max(x, 0.075)*250)
        pitch.scatter(goal_x, goal_y, ax=ax, edgecolors='black', c='black', s=goal_s, alpha = 1)

    ax.set_title(title)


    return fig

# Calculation functions

def calculate_possession(events, home_team, away_team):
    possession_events = events[events['type'].isin(['Pass', 'Carry'])]
    total_possession = len(possession_events)
    home_possession = len(possession_events[possession_events['team'] == home_team])
    away_possession = len(possession_events[possession_events['team'] == away_team])
    home_possession_pct = (home_possession / total_possession) * 100
    away_possession_pct = (away_possession / total_possession) * 100
    return home_possession_pct, away_possession_pct


def calculate_field_tilt(events, home_team, away_team):
    final_third_passes = events[(events['type'] == 'Pass') & (events['location'].apply(lambda loc: isinstance(loc, (list, tuple)) and loc[0] > 80))]
    home_final_third_passes = len(final_third_passes[final_third_passes['team'] == home_team])
    away_final_third_passes = len(final_third_passes[final_third_passes['team'] == away_team])
    total_final_third_passes = home_final_third_passes + away_final_third_passes
    home_field_tilt = (home_final_third_passes / total_final_third_passes) * 100
    away_field_tilt = (away_final_third_passes / total_final_third_passes) * 100
    return home_field_tilt, away_field_tilt


def calculate_opp_passes_per_def_action(events, home_team, away_team):
    defensive_actions = events[events['type'].isin(['Tackle', 'Interception', 'Foul Won'])]
    passes = events[events['type'] == 'Pass']
    home_ppda = len(passes[passes['team'] == away_team]) / len(defensive_actions[defensive_actions['team'] == home_team])
    away_ppda = len(passes[passes['team'] == home_team]) / len(defensive_actions[defensive_actions['team'] == away_team])
    return home_ppda, away_ppda

# Plotting functions

def plot_xg_race(events, home_team, away_team):
    fig, ax = plt.subplots()
    home_shots = events[(events['type'] == 'Shot') & (events['team'] == home_team)]
    away_shots = events[(events['type'] == 'Shot') & (events['team'] == away_team)]
    home_xg_cumsum = home_shots['shot_statsbomb_xg'].cumsum()
    away_xg_cumsum = away_shots['shot_statsbomb_xg'].cumsum()
    ax.plot(home_shots['minute'], home_xg_cumsum, label=f'{home_team} xG', color='blue')
    ax.plot(away_shots['minute'], away_xg_cumsum, label=f'{away_team} xG', color='red')
    ax.set_title('xG Race')
    ax.set_xlabel('Minute')
    ax.set_ylabel('Cumulative xG')
    ax.legend()
    return fig


def plot_xt_flow(events, home_team, away_team):
    fig, ax = plt.subplots()
    home_events = events[events['team'] == home_team]
    away_events = events[events['team'] == away_team]
    home_xt = home_events['xT_delta'].cumsum()
    away_xt = away_events['xT_delta'].cumsum()
    ax.plot(home_events['minute'], home_xt, label=f'{home_team} xT', color='blue')
    ax.plot(away_events['minute'], away_xt, label=f'{away_team} xT', color='red')
    ax.set_title('xT Flow')
    ax.set_xlabel('Minute')
    ax.set_ylabel('Cumulative xT')
    ax.legend()
    return fig


def plot_pass_networks(events):
    fig, ax = plt.subplots()
    pitch = Pitch()
    pitch.draw(ax=ax)
    passes = events[events['type'] == 'Pass']
    for _, pass_event in passes.iterrows():
        start_x, start_y = pass_event['location']
        end_x, end_y = pass_event['pass_end_location']
        pitch.arrows(start_x, start_y, end_x, end_y, ax=ax, color='black', alpha=0.3)
    ax.set_title('Pass Networks')
    return fig