import streamlit as st
import pandas as pd
import os
import urllib.parse

LANG = 'fi-FI'
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
        if 'edit_index' not in st.session_state:
            st.session_state.edit_index = None
        search_query = st.text_input("Filter by")
        filtered_df = search_word(search_query) if search_query else df
        for index, row in filtered_df.iterrows():
            if st.session_state.edit_index == index:
                st.subheader('Editing')
                with st.form(key=f"edit_form{index}"):
                    edit_word = st.text_input("Word", value=row['Word'])
                    edit_trans = st.text_input("Translation", value=row['Translation'])
                    edit_example = st.text_input("Example", value=(row['Example'] if pd.notna(row['Example']) else ""))
                    col_save, col_cancel = st.columns(2, gap="xsmall", wrap=False)

                    st.divider()
                    with col_save:
                        save_btn = st.form_submit_button("Save")
                    with col_cancel:
                        cancel_btn = st.form_submit_button("Cancel")
                    if save_btn:
                        df.at[index, 'Word'] = edit_word
                        df.at[index, 'Translation'] = edit_trans
                        df.at[index, 'Example'] = edit_example
                        save_data(df)
                    if save_btn or cancel_btn:
                        st.session_state.edit_index = None
                        st.rerun()
            else:
                col_info, col_audio, col_edit = st.columns([4,1,1], gap="xsmall", wrap=False)
                with col_info:
                    example_html = f"<br><span style='color: gray; font-size: 0.85em;'>{row['Example']}</span>" if pd.notna(row['Example']) else ""
                    st.markdown(f"**{row['Word']}** - _{row['Translation']}_{example_html}", unsafe_allow_html=True)
                with col_audio:
                    if st.button("🔊", key=f"audio_{index}"):
                        st.components.v1.html(get_audio(row['Word'], lang=LANG), height=0)
                with col_edit:
                    if st.button("✏️", key=f"edit_{index}"):
                        st.session_state.edit_index = index
                        st.rerun()

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