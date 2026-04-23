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
df = df[df["requirement_id"] != ""]

top_left, top_right = st.columns([1, 2])

with top_left:
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style='text-align: center'>
            <div style='font-size: 18px; color: gray;'>Total Requirements</div>
            <div style='font-size: 40px; font-weight: bold;'>{len(df)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_right:
    st.subheader("Status Distribution")

    if not counts.empty:
        chart = alt.Chart(counts).mark_bar(size=40).encode(
    x=alt.X(
    "evaluation_status:N",
    title="Status",
    sort=["In Assignment", "In Evaluation", "Evaluated"],  # 👈 AICI
    axis=alt.Axis(labelAngle=0)
),
    y=alt.Y("cnt:Q", title="Count"),
    color=alt.Color(
        "evaluation_status:N",
        scale=alt.Scale(
            domain=["Evaluated", "In Evaluation", "In Assignment"],
            range=["#22c55e", "#facc15", "#ef4444"]
        ),
        legend=None
    )
).properties(
    height=220,
    width=300
)

        text = chart.mark_text(
            align="center",
            baseline="bottom",
            dy=-5,
            fontSize=14
        ).encode(
            text="cnt:Q"
        )

        st.altair_chart(chart + text, use_container_width=True)

st.divider()

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
    hide_index=True
)

if project == "ALL" and not counts_by_project.empty:
    st.subheader("By Project")
    pivot_df = counts_by_project.pivot(
        index="project",
        columns="evaluation_status",
        values="cnt"
    ).fillna(0)

    pivot_df = pivot_df[["In Assignment", "In Evaluation", "Evaluated"]]

    st.dataframe(pivot_df, use_container_width=True)

st.divider()

st.subheader("Export")
st.download_button(
    label="Download filtered CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"requirements_report_{project.lower()}.csv",
    mime="text/csv"
)