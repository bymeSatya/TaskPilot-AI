import streamlit as st

st.title("Knowledge Base")
st.info("Add links to Snowflake and Matillion docs you reference often. Paste URLs and short notes.")
links = st.session_state.setdefault("kb_links", [])
new = st.text_input("Add doc URL")
note = st.text_input("Short note")
if st.button("Add"):
    links.append((new, note))
for url, n in links:
    st.markdown(f"- [{n or url}]({url})")