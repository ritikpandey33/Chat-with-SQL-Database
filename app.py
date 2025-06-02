import streamlit as st
from pathlib import Path
import pandas as pd
import altair as alt
import sqlite3
from sqlalchemy import create_engine, inspect
# Updated imports for LangChain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

# --- Constants ---
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

# --- Sidebar Options ---
radio_opt = ["Use SQLite 3 Database - Student.db", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio("Choose the DB you want to chat with", options=radio_opt)
db_uri = LOCALDB if radio_opt.index(selected_opt) == 0 else MYSQL

# Role-based Access
role = st.sidebar.selectbox("Select Role", ["Read-Only", "Admin"])
is_admin = role == "Admin"

# MySQL connection fields
mysql_host = st.sidebar.text_input("MySQL Host") if db_uri == MYSQL else None
mysql_user = st.sidebar.text_input("MySQL User") if db_uri == MYSQL else None
mysql_password = st.sidebar.text_input("MySQL Password", type="password") if db_uri == MYSQL else None
mysql_db = st.sidebar.text_input("MySQL Database") if db_uri == MYSQL else None

# Groq API
api_key = st.sidebar.text_input("Groq API Key", type="password")

# --- DB Config ---
@st.cache_resource(ttl="2h")
def configure_db():
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=rw", uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    else:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Provide full MySQL details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if not api_key:
    st.warning("Please provide the Groq API key.")
    st.stop()

db = configure_db()

# --- Groq LLM ---
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# --- Agent Toolkit ---
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# --- Chat Interface ---
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)
    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

# --- File Upload and Dynamic Table Creation ---
st.sidebar.markdown("### Upload CSV to Add Table")
csv_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if is_admin and csv_file is not None:
    df = pd.read_csv(csv_file)
    table_name = st.sidebar.text_input("Table name for new data", value="uploaded_table")
    if st.sidebar.button("Create Table"):
        conn = sqlite3.connect("student.db")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        st.sidebar.success(f"Table `{table_name}` created!")

# --- Table Explorer + Visualization ---
st.markdown("## 📊 Explore & Visualize Tables")

engine = create_engine("sqlite:///student.db")
inspector = inspect(engine)
tables = inspector.get_table_names()

if tables:
    selected_table = st.selectbox("Select Table", tables)
    df_view = pd.read_sql_query(f"SELECT * FROM {selected_table}", engine)
    st.dataframe(df_view)

    if not df_view.empty:
        st.markdown("### 🔎 Data Summary")
        st.write(df_view.describe())

        numeric_cols = df_view.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) >= 1:
            col_to_plot = st.selectbox("Select numeric column to plot", numeric_cols)
            chart = alt.Chart(df_view).mark_bar().encode(
                x=alt.X(col_to_plot, bin=True),
                y='count()'
            ).properties(width=600, height=400)
            st.altair_chart(chart)
        else:
            st.info("No numeric columns found for charting.")
