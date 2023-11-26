import os.path
import random
import json
import matplotlib.pyplot as plt

import streamlit as st
from PIL import Image


def write_history(win, changed_choice):
    with open('history.json', 'r') as f:
        history = json.load(f)
    history['num_games'] += 1

    if win:
        history['wins'] += 1
    else:
        history['looses'] += 1

    if win and changed_choice:
        history['wins_changed'] += 1
    elif win and not changed_choice:
        history['wins_not_changed'] += 1
    elif not win and changed_choice:
        history['looses_changed'] += 1
    else:
        history['looses_not_changed'] += 1

    with open('history.json', 'w') as f:
        json.dump(history, f)


st.header("Парадокс Монти Холла")

if 'game_state' not in st.session_state:
    st.session_state['game_state'] = 'start'

if st.session_state['game_state'] == 'start':
    image = Image.open(os.path.join('images', 'white.png'))
    correct_door = random.choice([0, 1, 2])
    if 'correct_door' not in st.session_state:
        st.session_state['correct_door'] = correct_door
elif st.session_state['game_state'] == 'first_choice':
    image = Image.open(os.path.join('images', f'red_{st.session_state["opened_door"]}.png'))
elif st.session_state['game_state'].startswith('final'):
    image = Image.open(
        os.path.join('images', f'red_{st.session_state["opened_door"]}_green_{st.session_state["correct_door"]}.png'))
    if st.session_state['game_state'] == 'final_win':
        st.balloons()

st.image(image)

button_cols = {}

cols = st.columns([2, 6, 6, 3])

for i in range(len(cols) - 1):
    with cols[i + 1]:
        button_cols[i] = st.button(f'{i + 1}', disabled=((('opened_door' in st.session_state)
                                                      and (i == st.session_state['opened_door'])))
                                                    or st.session_state['game_state'].startswith('final'))

for i, b in button_cols.items():
    if b and (st.session_state['game_state'] == 'start' or False):
        st.session_state['game_state'] = 'first_choice'
        arr = []
        for j in range(3):
            if (j != i) and (j != st.session_state['correct_door']):
                arr.append(j)

        open_door = random.choice(arr)
        if 'opened_door' not in st.session_state:
            st.session_state['opened_door'] = open_door
        else:
            st.session_state['opened_door'] = open_door

        if 'first_number' not in st.session_state:
            st.session_state['first_number'] = i
        else:
            st.session_state['first_number'] = i

        st.rerun()

    elif b and (st.session_state['game_state'] == 'first_choice'):
        st.session_state['game_state'] = 'final'
        changed_choice = i != st.session_state['first_number']
        win = i == st.session_state['correct_door']

        write_history(win, changed_choice)

        if i == st.session_state['correct_door']:
            st.session_state['game_state'] = 'final_win'

        st.rerun()


# print(st.session_state['correct_door'], st.session_state['game_state'])
restart = st.button('Restart game')
if restart:
    st.session_state.pop('game_state')
    if 'first_number' in st.session_state:
        st.session_state.pop('first_number')
    st.session_state.pop('correct_door')
    if 'opened_door' in st.session_state:
        st.session_state.pop('opened_door')

    st.rerun()


with st.expander('История', expanded=True):
    with open('history.json', 'r') as f:
        history = json.load(f)

    if (history['num_games'] != 0) and (history['wins_changed'] + history['looses_changed'] != 0) and (history['wins_not_changed'] + history['looses_not_changed'] != 0):
        fig, axs = plt.subplots(1, 3, figsize=(8, 3))
        axs[0].pie([history['wins'] / history['num_games'], history['looses'] / history['num_games']],
                   autopct='%1.1f%%',
                   colors=['green', 'red'])
        axs[0].set_title('Все игры')

        axs[1].pie([history['wins_changed'] / (history['wins_changed'] + history['looses_changed']), history['looses_changed'] / (history['wins_changed'] + history['looses_changed'])],
                   autopct='%1.1f%%',
                   colors=['green', 'red'])
        axs[1].set_title('При изменении выбора')

        axs[2].pie([history['wins_not_changed'] / (history['wins_not_changed'] + history['looses_not_changed']), history['looses_not_changed'] / (history['wins_not_changed'] + history['looses_not_changed'])],
                   autopct='%1.1f%%',
                   colors=['green', 'red'])
        axs[2].set_title('Без изменения выбора')
        st.pyplot(fig)

    st.subheader('Статистика')
    st.markdown(f"""
Всего игр: {history['num_games']} \n
Всего побед: {history['wins']} \n
Всего поражений: {history['looses']} \n
Побед при изменении выбора: {history['wins_changed']} \n
Поражений при изменении выбора: {history['looses_changed']} \n
Побед без изменения выбора: {history['wins_not_changed']} \n
Поражений без изменения выбора: {history['looses_not_changed']} \n
""")



    reset_history = st.button('Сбросить историю')
    if reset_history:
        history = {
            'num_games': 0,
            'wins': 0,
            'looses': 0,
            'wins_changed': 0,
            'wins_not_changed': 0,
            'looses_changed': 0,
            'looses_not_changed': 0
        }

        with open('history.json', 'w') as f:
            json.dump(history, f)

        st.rerun()

