import streamlit as st

# Set page configuration at the top of the script
st.set_page_config(layout="wide")

# Import necessary modules and functions
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
    plot_shots,
    get_matches,
    calculate_possession,
    calculate_field_tilt,
    calculate_opp_passes_per_def_action,
    plot_xg_race,
    plot_xt_flow,
    plot_pass_networks
)
from statsbombpy import sb
from enum import Enum
import warnings
import matplotlib.pyplot as plt
from mplsoccer import Pitch


warnings.filterwarnings("ignore", message="The use_column_width parameter has been deprecated")


# Initialize session state variables
if "selected_player_data" not in st.session_state:
    st.session_state.selected_player_data = None

# Use sidebar for navigation with fixed options
page = st.sidebar.radio("Navigation", ["Player Profile", "Collective Analysis"])

def main():
    """Main function to run the Streamlit app."""
    setup_page()
    if page == "Player Profile":
        if st.session_state.selected_player_data is None:
            display_home_page()
        else:
            display_player_profile()
    elif page == "Collective Analysis":
        display_collective_analysis()

def setup_page():
    """Set up the Streamlit page configuration and styles."""
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
            st.image(player_image)

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
        return

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

# New function to display collective analysis page
def display_collective_analysis():
    """Display the collective analysis page with match selection and statistics."""
    st.header("Collective Analysis")
    competitions = get_competitions_cached()
    world_cup_competitions = competitions[competitions['competition_name'] == 'FIFA World Cup']
    season_df = world_cup_competitions[world_cup_competitions['season_name'] == '1970']
    if not season_df.empty:
        season_data = season_df.iloc[0]
        competition_id = season_data['competition_id']
        season_id = season_data['season_id']
        matches = get_matches_cached(competition_id, season_id)

        match_names = matches['match_id'].astype(str) + ": " + matches['home_team'] + " vs " + matches['away_team']
        selected_match = st.selectbox("Select a match", match_names)
        match_id = matches[matches['match_id'].astype(str) + ": " + matches['home_team'] + " vs " + matches['away_team'] == selected_match]['match_id'].values[0]
        events = get_events_competition_cached(competition_id, season_id)
        match_events = events[events['match_id'] == match_id]

        # Determine home and away teams
        home_team = matches[matches['match_id'] == match_id]['home_team'].values[0]
        away_team = matches[matches['match_id'] == match_id]['away_team'].values[0]
        home_score = matches[matches['match_id'] == match_id]['home_score'].values[0]
        away_score = matches[matches['match_id'] == match_id]['away_score'].values[0]

        # Ensure Brazil is always on the left
        if home_team == 'Brazil':
            brazil_team, brazil_score, opponent_team, opponent_score = home_team, home_score, away_team, away_score
        else:
            brazil_team, brazil_score, opponent_team, opponent_score = away_team, away_score, home_team, home_score

        st.subheader(f"{brazil_team} {brazil_score} x {opponent_score} {opponent_team}")

        # Calculate and display match statistics
        st.write("### Match Statistics")
        brazil_events = match_events[match_events['team'] == brazil_team]
        opponent_events = match_events[match_events['team'] == opponent_team]

        brazil_xg = brazil_events[brazil_events['type'] == 'Shot']['shot_statsbomb_xg'].sum().round(2)
        opponent_xg = opponent_events[opponent_events['type'] == 'Shot']['shot_statsbomb_xg'].sum().round(2)

        brazil_xt_pass, brazil_xt_carries = calculate_xT(brazil_events)
        opponent_xt_pass, opponent_xt_carries = calculate_xT(opponent_events)

        brazil_possession, opponent_possession = calculate_possession(match_events, brazil_team, opponent_team)
        brazil_field_tilt, opponent_field_tilt = calculate_field_tilt(match_events, brazil_team, opponent_team)
        brazil_ppda, opponent_ppda = calculate_opp_passes_per_def_action(match_events, brazil_team, opponent_team)

        # Display statistics and plots in the desired layout
        cols = st.columns(4)

        with cols[0]:
            st.metric(label="Brazil xG", value=brazil_xg)
            st.metric(label="Brazil Pass xT", value=brazil_xt_pass.round(2))
            st.metric(label="Brazil Carry xT", value=brazil_xt_carries.round(2))
            st.metric(label="Brazil Possession %", value=brazil_possession)
            st.metric(label="Brazil Field Tilt %", value=brazil_field_tilt)
            st.metric(label="Brazil Opp. Passes per Def. Action", value=brazil_ppda)

        with cols[1]:
            st.subheader('Brazil Visualizations')
            st.subheader('xG Race')
            fig_xg_race = plot_xg_race(brazil_events, brazil_team, opponent_team)
            st.pyplot(fig_xg_race)

            st.subheader('xT Flow')
            fig_xt_flow = plot_xt_flow(brazil_events, brazil_team, opponent_team)
            st.pyplot(fig_xt_flow)

            st.subheader('Pass Networks')
            fig_pass_networks = plot_pass_networks(brazil_events)
            st.pyplot(fig_pass_networks)

        with cols[2]:
            st.subheader('Opponent Visualizations')
            st.subheader('xG Race')
            fig_xg_race_opponent = plot_xg_race(opponent_events, opponent_team, brazil_team)
            st.pyplot(fig_xg_race_opponent)

            st.subheader('xT Flow')
            fig_xt_flow_opponent = plot_xt_flow(opponent_events, opponent_team, brazil_team)
            st.pyplot(fig_xt_flow_opponent)

            st.subheader('Pass Networks')
            fig_pass_networks_opponent = plot_pass_networks(opponent_events)
            st.pyplot(fig_pass_networks_opponent)

        with cols[3]:
            st.metric(label="Opponent xG", value=opponent_xg)
            st.metric(label="Opponent Pass xT", value=opponent_xt_pass.round(2))
            st.metric(label="Opponent Carry xT", value=opponent_xt_carries.round(2))
            st.metric(label="Opponent Possession %", value=opponent_possession)
            st.metric(label="Opponent Field Tilt %", value=opponent_field_tilt)
            st.metric(label="Opponent Opp. Passes per Def. Action", value=opponent_ppda)
    else:
        st.error("1970 World Cup data not found.")

# Caching function for matches
@st.cache_data
def get_matches_cached(competition_id, season_id):
    """Cache the matches data for a competition and season."""
    return get_matches(competition_id, season_id)

if __name__ == '__main__':
    main()
