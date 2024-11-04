import streamlit as st
from utils import (
    set_light_mode,
    calculate_xT,
    crop_figure,
    load_and_resize_image,
    get_competitions,
    get_player_events_competition,
    plot_passes,
    plot_carries,
    plot_reception_actions,
    plot_shots
)
from statsbombpy import sb



def main():
    st.set_page_config(layout="wide")  
    set_light_mode()
    st.title('Brasil 70')
    

    players = {
        'Ado': ('Eduardo Roberto Stinghen', 'https://upload.wikimedia.org/wikipedia/commons/8/82/Eduardo_Roberto_Stinghen.jpg'),
        'Baldocchi': ('José Guilherme Baldocchi', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Baldocchi_%281970%29.jpg/227px-Baldocchi_%281970%29.jpg'),
        'Brito': ('Hercules Brito Ruas', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/H%C3%A9rcules_de_Brito_Ruas.jpg/330px-H%C3%A9rcules_de_Brito_Ruas.jpg'),
        'Caju': ('Paulo Cézar Lima', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Caju_1978.jpg/1200px-Caju_1978.jpg'),
        'Carlos Alberto': ('Carlos Alberto Torres', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Carlos_Alberto_%281970%29.jpg/220px-Carlos_Alberto_%281970%29.jpg'),
        'Clodoaldo': ('Clodoaldo Tavares de Santana', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Clodoaldo_1970.jpg/220px-Clodoaldo_1970.jpg'),
        'Dada Maravilha': ('Dario José dos Santos', 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Dad%C3%A1_Maravilha_%281970%29.jpg'),
        'Edu': ('Jonas Eduardo Américo', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Edu_1970.jpg/220px-Edu_1970.jpg'),
        'Émerson Leão': ('Emerson Leão', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/%C3%89merson_Le%C3%A3o.jpg/220px-%C3%89merson_Le%C3%A3o.jpg'),
        'Everaldo': ('Everaldo Marques da Silva', 'https://upload.wikimedia.org/wikipedia/commons/2/20/Everaldo_Marques_da_Silva.jpg'),
        'Félix': ('Félix Miéli Venerando', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/F%C3%A9lix_Brasil.jpg/220px-F%C3%A9lix_Brasil.jpg'),
        'Fontana': ('José de Anchieta Fontana', 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Jos%C3%A9_de_Anchieta_Fontana_%281970%29.jpg'),
        'Gérson': ('Gérson de Oliveira Nunes', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/G%C3%A9rson_1970.jpg/1200px-G%C3%A9rson_1970.jpg'),
        'Jairzinho': ('Jair Ventura Filho', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Jairzinho_%28Jair_Ventura_Filho%2C_1970%29.jpg/150px-Jairzinho_%28Jair_Ventura_Filho%2C_1970%29.jpg'),
        'Joel Camargo': ('Joel Camargo', 'https://upload.wikimedia.org/wikipedia/commons/1/1d/Joel_Camargo_%281970%29.jpg'),
        'Marco Antônio': ('Marco Antônio Feliciano', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Marco_Ant%C3%B4nio_%281974%29.jpg/230px-Marco_Ant%C3%B4nio_%281974%29.jpg'),
        'Pelé': ('Édson Arantes do Nascimento', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Panini_pele_photo_only.jpg/160px-Panini_pele_photo_only.jpg'),
        'Piazza': ('Wilson da Silva Piazza', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Wilson_Piazza.jpg/220px-Wilson_Piazza.jpg'),
        'Roberto Miranda': ('Roberto Lopes de Miranda', 'https://upload.wikimedia.org/wikipedia/commons/d/d2/Roberto_Miranda_%281970%29%2C_%27Mexico_70%27%2C_Panini_figurina.jpg'),
        'Roberto Rivelino': ('Roberto Rivelino', 'https://upload.wikimedia.org/wikipedia/commons/d/df/Rivelino_brasil_figurita.jpg'),
        'Tostão': ('Eduardo Gonçalves de Andrade', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Tost%C3%A3o_%28Eduardo_Gon%C3%A7alves_de_Andrade%2C_1970%29.jpg/640px-Tost%C3%A3o_%28Eduardo_Gon%C3%A7alves_de_Andrade%2C_1970%29.jpg'),
        'Zé Maria': ('José Maria Rodrigues Alves', 'https://upload.wikimedia.org/wikipedia/commons/1/14/Z%C3%A9_Maria_1970.png')
    }


    if "selected_player" not in st.session_state:
        st.header("Selecione um jogador:")


        cols = st.columns(5)  
        for i, (player, (name, image_url)) in enumerate(players.items()):
            with cols[i % 5]:  
                if st.button(player):  
                    st.session_state.selected_player = player
                    st.session_state.player_name = name
                    st.session_state.player_image_url = image_url
                    st.experimental_rerun()
                player_image = load_and_resize_image(name)  
                st.image(player_image, use_column_width=True)


    else:
        
        selected_player = st.session_state.selected_player
        player_name = st.session_state.player_name
        player_image_url = st.session_state.player_image_url
        
        
        if st.button("Voltar à página inicial"):
            del st.session_state.selected_player
            del st.session_state.player_name
            del st.session_state.player_image_url
            st.experimental_rerun()

        
        competitions = get_competitions()
        world_cup_competitions = competitions[competitions['competition_name'] == 'FIFA World Cup']
        season_data = world_cup_competitions[world_cup_competitions['season_name'] == '1970'].iloc[0]
        competition_id = season_data['competition_id']
        season_id = season_data['season_id']
    
       
        player_events = get_player_events_competition(competition_id, season_id, player_name)
    
        if player_events.empty:
            st.write(f"Nenhum evento encontrado para {player_name} na competição selecionada.")
            return
    
       
        passes = player_events[player_events['type'] == 'Pass']
        assists = passes[passes['pass_goal_assist'] == True]
        total_assists = len(assists)

    
        shots = player_events[player_events['type'] == 'Shot']
        goals = shots[shots['shot_outcome'] == 'Goal']
        total_goals = len(goals)
        total_xg = shots['shot_statsbomb_xg'].sum().round(2)
    

        total_xt_pass, total_xt_carries = calculate_xT(player_events)

        st.header(f'{selected_player}')
    
        stats_container = st.container()
        with stats_container:
            cols = st.columns(6)

            with cols[0]:
                player_image = load_and_resize_image(player_name, final_size = (300,500), aspect_ratio=3/5)  #
                st.image(player_image)
                
            with cols[1]:
                st.metric(label="Gols", value=int(total_goals))
                st.metric(label="Assistências", value=int(total_assists))
                st.metric(label="xG", value=total_xg)
                st.metric(label="Pass xT", value=total_xt_pass.round(2))
                st.metric(label="Carry xT", value=total_xt_carries.round(2))
            with cols[2]:
                st.subheader('Recepçoes')
                fig_rec_actions = plot_reception_actions(player_events)
                cropped_rec_actions = crop_figure(fig_rec_actions)
                st.image(cropped_rec_actions,  width = 190)
            with cols[3]:
                st.subheader('Conduções')
                fig_carries = plot_carries(player_events)
                cropped_carries = crop_figure(fig_carries)
                st.image(cropped_carries, width = 190)
            with cols[4]:
                st.subheader('Passes')
                fig_passes = plot_passes(player_events)
                cropped_passes = crop_figure(fig_passes)
                st.image(cropped_passes, width = 190 )
            with cols[5]:
                st.subheader('Finalizações')
                fig_possession_losses = plot_shots(player_events)
                cropped_shots = crop_figure(fig_possession_losses)
                st.image(cropped_shots,  width = 190)
    
 
       
        st.markdown("""
            <style>
            .stContainer {
                padding: 0em 0em;
            }
            </style>
            """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
