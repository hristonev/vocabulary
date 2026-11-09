import streamlit as st
import pandas as pd
import os
import urllib.parse

CSV_FILE = "dictinary.csv"

st.set_page_config(page_title="Online dictinary")
st.markdown("""
## Learn, add and test foreign language words
""")

tab1, tab2, tab3 = st.tabs(["Dictionary", "Add a word", "Test my knowladge"])

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["Word", "Translation", "Example"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)

def search_word(word: str):
    return df[
        df['Word'].str.contains(word, case=False, na=False) |
        df['Translation'].str.contains(word, case=False, na=False)
    ]

def get_audio(text: str, lang='fi-FI'):
    return f"""
    <script>
        if('speechSynthesis' in window) {{
            window.speechSynthesis.cancel()
            var utterance = new SpeechSynthesisUtterance("{text}")
            utterance.lang = "{lang}"
            utterance.rate = 0.9
            window.speechSynthesis.speak(utterance)
        }}else{{
            alert("Not supported")
        }}
    </script>
    """

df = load_data()

# --- TAB 1 Review and search
with tab1:
    st.header("All learnings")
    if df.empty:
        st.info("Your dictionary is empty!")
    else:
        search_query = st.text_input("Filter by")
        filtered_df = search_word(search_query) if search_query else df
        for index, row in filtered_df.iterrows():
            col_w, col_t, col_e, col_b = st.columns([2, 2, 2, 10])
            with col_w:
                st.markdown(f"**{row['Word']}**")
            with col_t:
                st.markdown(f"{row['Translation']}")
            with col_e:
                st.markdown(f"{row['Example']}")
            with col_b:
                if st.button("🔊", key=f"audio_{index}"):
                    st.components.v1.html(get_audio(row['Word']), height=0)

        st.dataframe(filtered_df, hide_index=True)
        st.caption(f"Showing {len(filtered_df)}/{len(df)} words")
        

# --- TAB 2 Add a word
with tab2:
    st.header("Add new word")
    with st.form("add_word_form", clear_on_submit=True):
        new_word = st.text_input("Word")
        new_trans = st.text_input("Translation")
        new_example = st.text_input("Example")
        submitted = st.form_submit_button("Add")

        if submitted:
            if new_word.strip() and new_trans.strip():
                if len(search_word(new_word.strip())):
                    st.warning("Word is in the dictionary!")
                else:
                    new_row = pd.DataFrame({
                        "Word": [new_word.strip()],
                        "Translation": [new_trans.strip()],
                        "Example": [new_example.strip()],
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"The '{new_word}' word is added successfuly")
            else:
                st.warning("Please, fill a word and translation fields")