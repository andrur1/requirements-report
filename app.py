import streamlit as st
import duckdb

st.title("📊 Requirements Evaluation Dashboard")

con = duckdb.connect("requirements.duckdb")

project = st.selectbox(
    "Select project",
    ["ALL", "AURORA", "BOLT", "COMET"]
)

if project == "ALL":
    df = con.execute("""
        SELECT *
        FROM requirements_report
        ORDER BY project, requirement_id
    """).fetchdf()
else:
    df = con.execute(f"""
        SELECT *
        FROM requirements_report
        WHERE project = '{project}'
        ORDER BY requirement_id
    """).fetchdf()

st.dataframe(df)

counts = con.execute(f"""
    SELECT evaluation_status, COUNT(*) AS cnt
    FROM requirements_report
    {"" if project == "ALL" else f"WHERE project = '{project}'"}
    GROUP BY 1
    ORDER BY 1
""").fetchdf()

st.subheader("Status Summary")
st.dataframe(counts)
st.bar_chart(counts.set_index("evaluation_status"))
