import streamlit as st
import duckdb
import pandas as pd


st.title("📊 Requirements Evaluation Dashboard")

st.set_page_config(
    page_title="Requirements Evaluation Dashboard",
    layout="wide"
)


st.title("📊 Requirements Evaluation Dashboard")
st.caption("Unified evaluation report for AURORA, BOLT, and COMET")

@st.cache_resource
def get_connection():
    return duckdb.connect("requirements.duckdb")

con = get_connection()

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

    counts = con.execute("""
        SELECT evaluation_status, COUNT(*) AS cnt
        FROM requirements_report
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    counts_by_project = con.execute("""
        SELECT project, evaluation_status, COUNT(*) AS cnt
        FROM requirements_report
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchdf()
else:
    df = con.execute(f"""
        SELECT *
        FROM requirements_report
        WHERE project = '{project}'
        ORDER BY requirement_id
    """).fetchdf()

<<<<<<< HEAD
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
=======
    counts = con.execute(f"""
        SELECT evaluation_status, COUNT(*) AS cnt
        FROM requirements_report
        WHERE project = '{project}'
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    counts_by_project = pd.DataFrame()

df = df.fillna("")

# KPI metrics
total_requirements = len(df)
evaluated_count = len(df[df["evaluation_status"] == "Evaluated"])
in_evaluation_count = len(df[df["evaluation_status"] == "In Evaluation"])
in_assignment_count = len(df[df["evaluation_status"] == "In Assignment"])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Requirements", total_requirements)
m2.metric("Evaluated", evaluated_count)
m3.metric("In Evaluation", in_evaluation_count)
m4.metric("In Assignment", in_assignment_count)

st.divider()

left, right = st.columns([2.2, 1])

with left:
    st.subheader("Requirements Table")

    display_df = df.copy()
    display_df.columns = [
        "Project",
        "Requirement ID",
        "Domain",
        "Evaluation Status",
        "Violations",
        "Title",
        "Source Reference"
    ]

    def color_status(val):
        if val == "Evaluated":
            return "background-color: #d1fae5; color: #065f46; font-weight: 600;"
        elif val == "In Evaluation":
            return "background-color: #fef3c7; color: #92400e; font-weight: 600;"
        elif val == "In Assignment":
            return "background-color: #fee2e2; color: #991b1b; font-weight: 600;"
        return ""

    styled_df = display_df.style.applymap(color_status, subset=["Evaluation Status"])

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=500
    )

with right:
    st.subheader("Status Summary")
    st.dataframe(counts, use_container_width=True, hide_index=True)

    if not counts.empty:
        chart_df = counts.set_index("evaluation_status")
        st.bar_chart(chart_df["cnt"])

    if project == "ALL" and not counts_by_project.empty:
        st.subheader("By Project")
        pivot_df = counts_by_project.pivot(
            index="project",
            columns="evaluation_status",
            values="cnt"
        ).fillna(0)
        st.dataframe(pivot_df, use_container_width=True)

st.divider()

st.subheader("Export")
st.download_button(
    label="Download filtered CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"requirements_report_{project.lower()}.csv",
    mime="text/csv"
)
>>>>>>> e370a9c (commit on app.py)
