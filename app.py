import streamlit as st
import random

# --- CONFIGURATION ---
CARD_IMAGE_BASE_URL = "https://raw.githubusercontent.com/hayeah/playing-cards-assets/master/png/"
CARD_BACK_URL = "https://raw.githubusercontent.com/hayeah/playing-cards-assets/master/png/back.png"

# --- ROYAL CASINO THEME ---
def apply_styles():
    st.markdown("""
        <style>
        /* DARK POKER TABLE BACKGROUND */
        .stApp {
            background: radial-gradient(circle at center, #35654d 0%, #0f2027 100%);
            color: #ffffff;
            font-family: 'Roboto', sans-serif;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #1c1c1c;
            border-right: 1px solid #333;
        }
        section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: #d4af37 !important; /* Gold Text */
        }
        
        /* PLAYER BOXES (GLASSMORPHISM) */
        .player-box {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        
        /* ACTIVE PLAYER GLOW */
        .active-turn {
            border: 2px solid #ffd700; /* Gold Border */
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
            transform: scale(1.02);
            background: rgba(0, 0, 0, 0.8);
        }

        /* TEXT STYLES */
        .p-name { font-size: 1.3rem; font-weight: bold; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .p-money { font-size: 1.1rem; color: #4caf50; font-weight: bold; background: #111; padding: 2px 10px; border-radius: 8px; border: 1px solid #333; display:inline-block; margin-top:5px;}
        
        /* BADGES */
        .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; margin-top: 5px; display: inline-block; }
        .badge-out { background: #b71c1c; color: white; border: 1px solid #ff5252; }
        .badge-fold { background: #e65100; color: white; border: 1px solid #ff9800; }

        /* CARDS */
        div[data-testid="stImage"] img {
            border-radius: 6px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.5);
            border: 1px solid #ddd;
        }

        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(180deg, #ffd700 0%, #d4af37 100%);
            color: #000;
            border: none;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 0 #8c7324;
            transition: all 0.1s;
        }
        .stButton>button:hover {
            background: #ffeb3b;
            transform: translateY(-2px);
            color: black;
        }
        .stButton>button:active {
            transform: translateY(2px);
            box-shadow: 0 1px 0 #8c7324;
        }

        /* WINNER OVERLAY */
        .winner-box {
            background: rgba(0,0,0,0.85);
            border: 3px solid #ffd700;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 50px rgba(255, 215, 0, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def get_rank_value(rank):
    mapping = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    return mapping[rank]

def evaluate_hand(hand):
    if len(hand) != 3: return (0, 0, 0, "Empty")
    ranks = sorted([get_rank_value(c[:-1]) for c in hand], reverse=True)
    suits = [c[-1] for c in hand]
    is_flush = len(set(suits)) == 1
    is_seq = False
    if ranks == [14, 3, 2]: is_seq = True; ranks = [3, 2, 1]
    elif ranks[0] - ranks[1] == 1 and ranks[1] - ranks[2] == 1: is_seq = True
    
    if len(set(ranks)) == 1: return (6, ranks[0], 0, "Trail (Three of a Kind) 🔥")
    if is_seq and is_flush: return (5, ranks[0], 0, "Pure Sequence 🌈")
    if is_seq: return (4, ranks[0], 0, "Sequence 📏")
    if is_flush: return (3, ranks[0], ranks[1], "Color (Flush) 🎨")
    if ranks[0] == ranks[1]: return (2, ranks[0], ranks[2], "Pair 👥")
    if ranks[1] == ranks[2]: return (2, ranks[1], ranks[0], "Pair 👥")
    if ranks[0] == ranks[2]: return (2, ranks[0], ranks[1], "Pair 👥")
    return (1, ranks[0], ranks[1], "High Card 🃏")

def get_winner():
    active_players = [p for p in st.session_state.players if p["status"] == "Active" and not p["folded"]]
    if not active_players: return None
    best_player = active_players[0]
    best_score = evaluate_hand(best_player["cards"])
    for p in active_players[1:]:
        score = evaluate_hand(p["cards"])
        if score[:3] > best_score[:3]:
            best_score = score
            best_player = p
    return best_player, best_score[3]

def add_to_log(msg):
    if "game_log" not in st.session_state: st.session_state.game_log = []
    st.session_state.game_log.insert(0, msg)
    if len(st.session_state.game_log) > 10: st.session_state.game_log.pop()

def get_card_image_url(card_code):
    if not card_code: return None
    suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
    rank_map = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
    return f"{CARD_IMAGE_BASE_URL}{rank_map[card_code[:-1]]}_of_{suit_map[card_code[-1]]}.png"

def create_deck():
    return [f"{r}{s}" for s in ['♠', '♥', '♦', '♣'] for r in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]

def initialize_game(num_players, starting_money):
    st.session_state.players = [{"name": f"P{i+1}", "money": starting_money, "status": "Active", "cards": [], "has_seen": False, "folded": False} for i in range(num_players)]
    st.session_state.pot = 0
    st.session_state.game_started = True
    st.session_state.current_round = 1
    st.session_state.cards_dealt = False
    st.session_state.current_stake = 20
    st.session_state.winner_declared = False
    st.session_state.game_over = False
    st.session_state.game_log = ["Game initialized."]

def next_turn():
    active = [p for p in st.session_state.players if p["status"] == "Active" and not p["folded"]]
    if len(active) <= 1: st.session_state.winner_declared = True; return
    st.session_state.current_turn = (st.session_state.current_turn + 1) % len(st.session_state.players)
    while st.session_state.players[st.session_state.current_turn]["status"] != "Active" or st.session_state.players[st.session_state.current_turn]["folded"]:
        st.session_state.current_turn = (st.session_state.current_turn + 1) % len(st.session_state.players)

# --- UI ---
def main():
    apply_styles()
    
    # Sidebar
    with st.sidebar:
        st.title("♠️ Teen Patti Pro")
        if 'game_started' in st.session_state and st.session_state.game_started:
            st.metric("💰 TOTAL POT", f"₹{st.session_state.pot}")
            st.write("---")
            st.subheader("📜 Activity Log")
            for log in st.session_state.get("game_log", []):
                st.markdown(f"<span style='color:#ccc'>• {log}</span>", unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🔴 Restart Game"): st.session_state.clear(); st.rerun()
    
    # Main Content
    if 'game_started' not in st.session_state: st.session_state.game_started = False

    if not st.session_state.game_started:
        st.markdown("<h1 style='text-align: center; color: #ffd700; text-shadow: 0 0 10px black;'>♣️ VIP TABLE SETUP</h1>", unsafe_allow_html=True)
        st.write("")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown('<div class="player-box">', unsafe_allow_html=True)
            n = st.slider("Number of Players", 2, 6, 3)
            m = st.number_input("Starting Money (₹)", 100, 10000, 1000, 100)
            st.write("")
            if st.button("OPEN TABLE", use_container_width=True): initialize_game(n, m); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.get("game_over"):
        st.balloons()
        champ = [p["name"] for p in st.session_state.players if p["status"] == "Active"][0]
        st.markdown(f"""
        <div class="winner-box">
            <h1 style="color:#D4AF37">🏆 TOURNAMENT WINNER</h1>
            <h2 style="color:white">{champ}</h2>
            <p style="color:#ccc">You cleaned out the table!</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("NEW GAME"): st.session_state.clear(); st.rerun()

    else:
        # --- GAMEPLAY AREA ---
        
        # 1. Dealing Phase
        if not st.session_state.cards_dealt:
            st.info(f"Round {st.session_state.current_round} • Place your bets")
            dm = st.radio("Dealer Mode:", ["Auto-Deal", "Manual Selection"], horizontal=True)
            if dm == "Auto-Deal":
                if st.button("Shuffle & Deal Cards"):
                    deck = create_deck(); random.shuffle(deck)
                    for p in st.session_state.players:
                        if p["status"] == "Active": p["cards"] = [deck.pop() for _ in range(3)]; p["has_seen"] = False; p["folded"] = False
                    st.session_state.cards_dealt = True
                    for i, p in enumerate(st.session_state.players):
                        if p["status"] == "Active": st.session_state.current_turn = i; break
                    add_to_log("Cards dealt."); st.rerun()
            else:
                full = create_deck()
                cols = st.columns(len(st.session_state.players))
                all_set = True
                for i, p in enumerate(st.session_state.players):
                    with cols[i]:
                        if p["status"] != "Active": continue
                        taken = [c for other in st.session_state.players if other != p for c in other["cards"]]
                        sel = st.multiselect(f"{p['name']}", [c for c in full if c not in taken], default=p["cards"], key=f"f{i}", max_selections=3)
                        p["cards"] = sel
                        if len(sel) != 3: all_set = False
                if st.button("Confirm Manual") and all_set:
                    st.session_state.cards_dealt = True
                    for i, p in enumerate(st.session_state.players):
                        if p["status"] == "Active": st.session_state.current_turn = i; break
                    add_to_log("Manual Deal Confirmed."); st.rerun()

        # 2. Betting Phase
        elif not st.session_state.winner_declared:
            curr_idx = st.session_state.get("current_turn", 0)
            
            # Display Players
            cols = st.columns(len(st.session_state.players))
            for i, p in enumerate(st.session_state.players):
                with cols[i]:
                    box_class = "player-box"
                    if i == curr_idx: box_class += " active-turn"
                    
                    st.markdown(f"""
                    <div class="{box_class}">
                        <div class="p-name">{p['name']}</div>
                        <div class="p-money">₹{p['money']}</div>
                    """, unsafe_allow_html=True)
                    
                    if p["status"] == "Out": 
                        st.markdown("<div class='badge badge-out'>ELIMINATED</div>", unsafe_allow_html=True)
                    elif p["folded"]: 
                        st.markdown("<div class='badge badge-fold'>FOLDED</div>", unsafe_allow_html=True)
                    else:
                        if p["has_seen"]:
                            c_cols = st.columns(3)
                            for k, c in enumerate(p["cards"]):
                                with c_cols[k]: st.image(get_card_image_url(c))
                        else:
                            st.image(CARD_BACK_URL)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

            # Actions Area
            st.write("---")
            curr_p = st.session_state.players[curr_idx]
            st.markdown(f"<h3 style='text-align:center; color:#ffd700'>👉 {curr_p['name']}'s Turn</h3>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([1,1,1,1])
            with c1:
                if not curr_p["has_seen"]:
                    if st.button("👀 See Cards", use_container_width=True): curr_p["has_seen"] = True; add_to_log(f"{curr_p['name']} saw cards."); st.rerun()
            with c2:
                stake = st.session_state.current_stake * (2 if curr_p["has_seen"] else 1)
                if st.button(f"Bet ₹{stake}", use_container_width=True):
                    if curr_p["money"] >= stake:
                        curr_p["money"] -= stake; st.session_state.pot += stake
                        add_to_log(f"{curr_p['name']} bet ₹{stake}."); next_turn(); st.rerun()
                    else: st.error("Broke!")
            with c3:
                if st.button("❌ Fold", use_container_width=True): curr_p["folded"] = True; add_to_log(f"{curr_p['name']} folded."); next_turn(); st.rerun()
            with c4:
                active = [p for p in st.session_state.players if p["status"] == "Active" and not p["folded"]]
                if len(active) == 2:
                    if st.button("🏁 Show", use_container_width=True): st.session_state.winner_declared = True; add_to_log("🏁 Showdown!"); st.rerun()

        # 3. Showdown Phase
        else:
             winner, hand = get_winner()
             st.balloons()
             
             st.markdown(f"""
             <div class="winner-box">
                 <h2 style="color:#ffd700">🎉 {winner['name']} Wins!</h2>
                 <h3 style="color:white">{hand}</h3>
                 <p style="color:#ccc">Pot Won: ₹{st.session_state.pot}</p>
             </div>
             """, unsafe_allow_html=True)
             
             st.write("")
             cols = st.columns(len(st.session_state.players))
             for i, p in enumerate(st.session_state.players):
                 with cols[i]:
                     st.markdown(f"<div class='player-box'><b>{p['name']}</b>", unsafe_allow_html=True)
                     if p["cards"]:
                         cc = st.columns(3)
                         for k, c in enumerate(p["cards"]):
                             with cc[k]: st.image(get_card_image_url(c))
                     st.markdown("</div>", unsafe_allow_html=True)

             if st.button("💰 Collect Money & Next Round", use_container_width=True):
                 winner["money"] += st.session_state.pot
                 st.session_state.pot = 0
                 active_n = 0
                 for p in st.session_state.players:
                     if p["status"] == "Active" and p["money"] <= 0: p["status"] = "Out"; add_to_log(f"💀 {p['name']} is OUT.")
                     if p["status"] == "Active": active_n += 1
                 if active_n <= 1: st.session_state.game_over = True
                 else:
                     st.session_state.winner_declared = False; st.session_state.cards_dealt = False; st.session_state.current_round += 1
                 st.rerun()

if __name__ == "__main__": main()