import streamlit as st
import duckdb
import pandas as pd
import altair as alt

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

    counts = con.execute(f"""
        SELECT evaluation_status, COUNT(*) AS cnt
        FROM requirements_report
        WHERE project = '{project}'
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    counts_by_project = pd.DataFrame()

df = df.fillna("")

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

    def add_status_color(val):
        if val == "Evaluated":
            return "🟢 Evaluated"
        elif val == "In Evaluation":
            return "🟡 In Evaluation"
        elif val == "In Assignment":
            return "🔴 In Assignment"
        return val

    display_df["Evaluation Status"] = display_df["Evaluation Status"].apply(add_status_color)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True
    )

with right:
    st.subheader("Status Summary")
    st.dataframe(counts, use_container_width=True, hide_index=True)

    if not counts.empty:
        chart = alt.Chart(counts).mark_bar().encode(
            x=alt.X("evaluation_status:N", title="Status"),
            y=alt.Y("cnt:Q", title="Count"),
            color=alt.Color(
                "evaluation_status:N",
                scale=alt.Scale(
                    domain=["Evaluated", "In Evaluation", "In Assignment"],
                    range=["#22c55e", "#facc15", "#ef4444"]
                ),
                legend=None
            )
        )

        text = chart.mark_text(
            align="center",
            baseline="bottom",
            dy=-5
        ).encode(
            text="cnt:Q"
        )

        st.altair_chart(chart + text, use_container_width=True)

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