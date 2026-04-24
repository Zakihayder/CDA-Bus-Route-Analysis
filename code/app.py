import streamlit as st
import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from datetime import timedelta
import os

# --- Page Configuration ---
st.set_page_config(page_title="CDA Process Mining Dashboard", layout="wide")

# Custom CSS for the Trip Statistics Box
st.markdown("""
    <style>
    .stats-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1E1E1E;
        border: 1px solid #464b5d;
        margin-bottom: 25px;
        text-align: center;
    }
    .stats-title {
        color: #00d4ff;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    .stats-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# --- Data Loading Function ---
@st.cache_data
def load_data():
    xes_path = 'data/merged_event_log.xes'
    trips_csv = 'data/Total_Trips.csv'
    
    if not os.path.exists(xes_path):
        st.error(f"XES file not found at {xes_path}.")
        return None, None
    
    # Load standardized XES log
    log = pm4py.read_xes(xes_path)
    df = pm4py.convert_to_dataframe(log)
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    
    # Load official Trip Counts from your Task 1 extractor
    trips_df = pd.DataFrame()
    if os.path.exists(trips_csv):
        trips_df = pd.read_csv(trips_csv)
        
    return df, trips_df

# --- Main Logic ---
st.title("🚌 CDA Transit Process Analytics")
df, trips_df = load_data()

if df is not None:
    # --- Sidebar Filtering (Task 3b) ---
    st.sidebar.header("Route Settings")
    all_routes = sorted(df['case:concept:name'].unique())
    selected_case = st.sidebar.selectbox("Filter by Route ID", ["All Routes"] + all_routes)

    # Filtering Logic
    if selected_case != "All Routes":
        filtered_df = df[df['case:concept:name'] == selected_case]
        route_header = f"Route: {selected_case}"
        
        # Fetch verified trip count from Total_Trips.csv
        # Note: Route_ID in Total_Trips.csv is 'ID_Direction'
        display_trips = "0"
        if not trips_df.empty:
            match = trips_df[trips_df['Route_ID'] == selected_case]
            if not match.empty:
                display_trips = match.iloc[0]['Total_Trips']
    else:
        filtered_df = df
        route_header = "CDA Transit Network (All Routes)"
        # Sum total trips across all routes
        display_trips = trips_df['Total_Trips'].sum() if not trips_df.empty else "N/A"

    # --- Header & Trip Statistics Box (Task 3d) ---
    st.markdown(f"# {route_header}")
    
    st.markdown(f"""
        <div class="stats-box">
            <div class="stats-title">OFFICIAL TRIP COUNT (FROM PDF)</div>
            <div class="stats-value">{display_trips}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- Performance Metrics (Task 4a) ---
    st.subheader("Task 4a: Throughput Time Metrics")
    case_durations = filtered_df.groupby('case:concept:name')['time:timestamp'].agg(['min', 'max'])
    case_durations['duration'] = (case_durations['max'] - case_durations['min']).dt.total_seconds()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Average Trip Duration", str(timedelta(seconds=int(case_durations['duration'].mean()))))
    m2.metric("Minimum Trip Duration", str(timedelta(seconds=int(case_durations['duration'].min()))))
    m3.metric("Maximum Trip Duration", str(timedelta(seconds=int(case_durations['duration'].max()))))

    # --- Process Discovery (Task 3a, 3c) ---
    st.divider()
    st.subheader("Task 3: Process Discovery Map")
    st.info("Labels show the actual time difference between stop arrivals.")

    # Convert to log for PM4Py
    log_to_process = log_converter.apply(filtered_df)
    
    # Task 3c: Calculate transition durations correctly
    # We use the DFG with performance variant 'mean' to show edge travel time
    dfg_freq = dfg_discovery.apply(log_to_process, variant=dfg_discovery.Variants.FREQUENCY)
    
    # Discovery of performance with explicit time aggregation
    parameters = {
        dfg_visualization.Variants.PERFORMANCE.value.Parameters.FORMAT: "png",
        dfg_visualization.Variants.PERFORMANCE.value.Parameters.AGGREGATION_MEASURE: "mean"
    }

    gviz = dfg_visualization.apply(dfg_freq, log=log_to_process, 
                                   variant=dfg_visualization.Variants.PERFORMANCE,
                                   parameters=parameters)
    
    st.graphviz_chart(gviz.source)

    # --- Bottleneck Detection (Task 4b) ---
    st.divider()
    st.subheader("Task 4b: Bottleneck Summary (Slowest Segments)")
    
    dfg_perf = dfg_discovery.apply(log_to_process, variant=dfg_discovery.Variants.PERFORMANCE)
    perf_list = []
    for edge, duration in dfg_perf.items():
        perf_list.append({
            "From Stop": edge[0],
            "To Stop": edge[1],
            "Avg Travel Time": str(timedelta(seconds=int(duration))),
            "raw_seconds": duration
        })
    
    if perf_list:
        bottleneck_df = pd.DataFrame(perf_list).sort_values(by="raw_seconds", ascending=False).head(3)
        st.table(bottleneck_df[["From Stop", "To Stop", "Avg Travel Time"]])

else:
    st.warning("Please ensure merged_event_log.xes and Total_Trips.csv exist in the data folder.")