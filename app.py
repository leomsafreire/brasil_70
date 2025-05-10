import streamlit as st
from utils import (
    set_light_mode,
    calculate_xA,
    calculate_xT,
    crop_figure,
    load_and_resize_image,
    get_competitions,
    get_events_competition,
    get_player_events_competition,
    plot_passes,
    plot_carries,
    plot_reception_actions,
    plot_shots
)
from statsbombpy import sb
from enum import Enum
import warnings


warnings.filterwarnings("ignore", message="The use_column_width parameter has been deprecated")


# Initialize session state variables
if "selected_player_data" not in st.session_state:
    st.session_state.selected_player_data = None

def main():
    """Main function to run the Streamlit app."""
    setup_page()
    if st.session_state.selected_player_data is None:
        display_home_page()
    else:
        display_player_profile()

def setup_page():
    """Set up the Streamlit page configuration and styles."""
    st.set_page_config(layout="wide")
    st.markdown("""
    <style>
    /* Hide the header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* General styles */
    .stContainer {padding: 0em 0em;}
    p {font-size: 24px;}
    span {font-size: 24px;}
    </style>
    """, unsafe_allow_html=True)
    st.title('Brasil 70')
    st.markdown("<span style='font-size: 18px;'>by Leo M. Sa Freire</span>", unsafe_allow_html=True)

def display_home_page():
    """Display the main page with player selections."""
    st.markdown("<span style='font-size: 24px;'>The 1970 Brazilian national team is often hailed as the greatest World Cup team of all time. With Pelé in his final form, the iconic five-midfield lineup, and the controversial coaching change right before the tournament—everything aligned for Brazil's historic third world title.</span>", unsafe_allow_html=True)
    
    st.markdown("""
    <p style='font-size: 24px;'>
        This project pays tribute to the legendary players behind this achievement. The first page, styled like a sticker album, showcases each of them. By clicking on a player's name, you can open a data profile with their performance in the 1970 World Cup.
    </p>
    """, unsafe_allow_html=True)
    st.header("Pick a player:")

    # Display players by position
    display_players_by_position('Goalkeepers', players_by_position('Goalkeeper'))
    display_players_by_position('Defenders', players_by_position('Defender'))
    display_players_by_position('Midfielders', players_by_position('Midfielder'))
    display_players_by_position('Forwards', players_by_position('Forward'))

def display_players_by_position(position_name, players_list):
    """Display players of a specific position."""
    st.markdown(f"<p style='font-size: 24px;'>{position_name}</p>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, player in enumerate(players_list):
        with cols[i % 5]:
            if st.button(player['display_name']):
                st.session_state.selected_player_data = player
            player_image = get_player_image(player['full_name'])
            st.image(player_image, use_container_width=True)

def players_by_position(position):
    """Get players filtered by position."""
    return [player for player in players if player['position'] == position]

def display_player_profile():
    """Display the selected player's profile with statistics and visualizations."""
    selected_player_data = st.session_state.selected_player_data
    player_name = selected_player_data['full_name']
    player_age = selected_player_data['age']
    display_name = selected_player_data['display_name']

    if st.button("Back to main page"):
        st.session_state.selected_player_data = None
        st.experimental_rerun()

    with st.spinner('Loading player data...'):
        competitions = get_competitions_cached()
        world_cup_competitions = competitions[competitions['competition_name'] == 'FIFA World Cup']
        season_df = world_cup_competitions[world_cup_competitions['season_name'] == '1970']
        if not season_df.empty:
            season_data = season_df.iloc[0]
            competition_id = season_data['competition_id']
            season_id = season_data['season_id']
        else:
            st.error("1970 World Cup data not found.")
            return

        events = get_events_competition_cached(competition_id, season_id)
        player_events = get_player_events_competition(events, player_name)

        if player_events.empty:
            st.warning(f"No event data available for {player_name} in the 1970 World Cup.")
            return

    # Calculate statistics
    matches = player_events['match_id'].unique()
    n_matches = len(matches)
    passes = player_events[player_events['type'] == 'Pass']
    assists = passes[passes['pass_goal_assist'] == True]
    total_assists = len(assists)
    shots = player_events[player_events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    total_goals = len(goals)
    total_xg = shots['shot_statsbomb_xg'].sum().round(2)
    total_xt_pass, total_xt_carries = calculate_xT(player_events)
    total_xa = calculate_xA(events, player_name).round(2)

    st.header(f'{display_name}')

    stats_container = st.container()
    with stats_container:
        cols = st.columns(6)

        with cols[0]:
            player_image = get_player_image(player_name)
            st.image(player_image)

        with cols[1]:
            subcols = st.columns(2)
            with subcols[0]:
                st.metric(label="Age", value=player_age)
                st.metric(label="xG", value=total_xg)
                st.metric(label="xA", value=total_xa)
                st.metric(label="Pass xT", value=total_xt_pass.round(2))
            with subcols[1]:
                st.metric(label="Matches", value=n_matches)
                st.metric(label="Goals", value=total_goals)
                st.metric(label="Assists", value=total_assists)
                st.metric(label="Carry xT", value=total_xt_carries.round(2))

        # Plotting functions
        with cols[2]:
            st.subheader('Ball Receipts')
            fig_rec_actions = plot_reception_actions(player_events)
            st.pyplot(fig_rec_actions)

        with cols[3]:
            st.subheader('Carries')
            fig_carries = plot_carries(player_events)
            st.pyplot(fig_carries)

        with cols[4]:
            st.subheader('Passes')
            fig_passes = plot_passes(player_events)
            st.pyplot(fig_passes)

        with cols[5]:
            st.subheader('Shots')
            fig_shots = plot_shots(player_events)
            st.pyplot(fig_shots)

# Caching functions to improve performance
@st.cache_data
def get_competitions_cached():
    """Cache the competitions data."""
    return get_competitions()

@st.cache_data
def get_events_competition_cached(competition_id, season_id):
    """Cache the events data for a competition and season."""
    return get_events_competition(competition_id, season_id)

@st.cache_data
def get_player_image(name):
    """Cache the player image loading and resizing."""
    try:
        return load_and_resize_image(name, final_size=(300, 500), aspect_ratio=3/5)
    except Exception:
        st.warning(f"Image for {name} could not be loaded.")
        return None  # Or return a default image

# Player data
players = [
    {'display_name': 'Ado', 'full_name': 'Eduardo Roberto Stinghen', 'age': 23, 'position': 'Goalkeeper'},
    {'display_name': 'Émerson Leão', 'full_name': 'Emerson Leão', 'age': 20, 'position': 'Goalkeeper'},
    {'display_name': 'Félix', 'full_name': 'Félix Miéli Venerando', 'age': 32, 'position': 'Goalkeeper'},
    {'display_name': 'Carlos Alberto', 'full_name': 'Carlos Alberto Torres', 'age': 25, 'position': 'Defender'},
    {'display_name': 'Brito', 'full_name': 'Hercules Brito Ruas', 'age': 30, 'position': 'Defender'},
    {'display_name': 'Piazza', 'full_name': 'Wilson da Silva Piazza', 'age': 26, 'position': 'Defender'},
    {'display_name': 'Everaldo', 'full_name': 'Everaldo Marques da Silva', 'age': 25, 'position': 'Defender'},
    {'display_name': 'Zé Maria', 'full_name': 'José Maria Rodrigues Alves', 'age': 21, 'position': 'Defender'},
    {'display_name': 'Fontana', 'full_name': 'José de Anchieta Fontana', 'age': 29, 'position': 'Defender'},
    {'display_name': 'Baldocchi', 'full_name': 'José Guilherme Baldocchi', 'age': 24, 'position': 'Defender'},
    {'display_name': 'Joel Camargo', 'full_name': 'Joel Camargo', 'age': 23, 'position': 'Defender'},
    {'display_name': 'Marco Antônio', 'full_name': 'Marco Antônio Feliciano', 'age': 19, 'position': 'Defender'},
    {'display_name': 'Clodoaldo', 'full_name': 'Clodoaldo Tavares de Santana', 'age': 20, 'position': 'Midfielder'},
    {'display_name': 'Gérson', 'full_name': 'Gérson de Oliveira Nunes', 'age': 29, 'position': 'Midfielder'},
    {'display_name': 'Rivellino', 'full_name': 'Roberto Rivelino', 'age': 24, 'position': 'Midfielder'},
    {'display_name': 'Pelé', 'full_name': 'Édson Arantes do Nascimento', 'age': 29, 'position': 'Midfielder'},
    {'display_name': 'Paulo Cézar Caju', 'full_name': 'Paulo Cézar Lima', 'age': 20, 'position': 'Midfielder'},
    {'display_name': 'Jairzinho', 'full_name': 'Jair Ventura Filho', 'age': 25, 'position': 'Forward'},
    {'display_name': 'Tostão', 'full_name': 'Eduardo Gonçalves de Andrade', 'age': 23, 'position': 'Forward'},
    {'display_name': 'Roberto Miranda', 'full_name': 'Roberto Lopes de Miranda', 'age': 25, 'position': 'Forward'},
    {'display_name': 'Edu', 'full_name': 'Jonas Eduardo Américo', 'age': 20, 'position': 'Forward'},
    {'display_name': 'Dadá Maravilha', 'full_name': 'Dario José dos Santos', 'age': 24, 'position': 'Forward'},
]

if __name__ == '__main__':
    main()
