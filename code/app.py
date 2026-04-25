import streamlit as st
import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from datetime import timedelta, datetime
import os
import re
from difflib import get_close_matches
import heapq
import requests
import pydeck as pdk

# --- NEW: Task 5 AI Agent Imports ---
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Page Configuration ---
st.set_page_config(page_title="CDA Transit Analytics", layout="wide")

# --- Professional UI Styling ---
st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(37, 99, 235, 0.20), transparent 40%),
            radial-gradient(circle at 85% 10%, rgba(14, 165, 233, 0.18), transparent 35%),
            linear-gradient(180deg, #050b18 0%, #020613 70%);
        color: #ffffff;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(2, 6, 23, 0.97) 0%, rgba(15, 23, 42, 0.96) 100%);
        border-right: 1px solid rgba(125, 211, 252, 0.18);
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 4.3rem;
        animation: pageFade 0.55s ease-out;
    }
    
    /* Header Styling - Forced Bold */
    .main-title { 
        font-size: clamp(2.2rem, 5vw, 3.4rem) !important; 
        font-weight: 800 !important; 
        color: #e6f0ff !important;
        margin-bottom: 0px !important; 
        line-height: 1.2 !important;
        display: block !important;
        animation: riseIn 0.5s ease-out;
        letter-spacing: 0.02em;
    }
    
    .sub-title { 
        font-size: clamp(1.1rem, 2.2vw, 1.7rem) !important;
        color: #7dd3fc !important; 
        margin-bottom: 25px !important; 
        font-weight: 700 !important; 
        display: block !important;
        animation: riseIn 0.7s ease-out;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(2, 6, 23, 0.95));
        border: 1px solid rgba(125, 211, 252, 0.28);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 10px 24px rgba(2, 6, 23, 0.42);
        animation: riseIn 0.6s ease-out;
    }

    .stats-box {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(3, 7, 18, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
        border: 1px solid rgba(125, 211, 252, 0.45);
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 14px 30px rgba(1, 4, 14, 0.45);
        animation: riseIn 0.8s ease-out;
    }
    .stats-title { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 5px; }
    .stats-value { font-size: 2.8rem; font-weight: 800; color: #7dd3fc; }

    .section-card {
        border: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(2, 6, 23, 0.88), rgba(15, 23, 42, 0.92));
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 10px 24px rgba(2, 6, 23, 0.34);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }

    .section-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 30px rgba(2, 6, 23, 0.45);
    }

    .hero-strip {
        margin: 8px 0 18px 0;
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid rgba(125, 211, 252, 0.28);
        background: linear-gradient(120deg, rgba(2, 6, 23, 0.86), rgba(8, 47, 73, 0.78));
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        animation: riseIn 0.9s ease-out;
    }

    .hero-pill {
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(125, 211, 252, 0.4);
        background: rgba(12, 74, 110, 0.35);
        color: #bae6fd;
        font-size: 0.83rem;
        letter-spacing: 0.02em;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(2, 6, 23, 0.92)) !important;
        border: 1px solid rgba(125, 211, 252, 0.2) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="input"] > div:hover {
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.13);
    }

    button[kind="primary"],
    button[kind="secondary"],
    .stButton > button {
        border-radius: 10px !important;
        border: 1px solid rgba(125, 211, 252, 0.35) !important;
        background: linear-gradient(135deg, rgba(8, 47, 73, 0.9), rgba(2, 132, 199, 0.75)) !important;
        color: #e0f2fe !important;
        font-weight: 700 !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(3, 105, 161, 0.35);
        filter: brightness(1.06);
    }

    [data-baseweb="tab-list"] {
        border-bottom: 1px solid rgba(125, 211, 252, 0.22) !important;
    }

    [data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
    }

    [aria-selected="true"][data-baseweb="tab"] {
        color: #7dd3fc !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid rgba(125, 211, 252, 0.2);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Chat Styling */
    .chat-container {
        border: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(2, 6, 23, 0.88), rgba(17, 24, 39, 0.8));
        padding: 10px;
    }

    @keyframes riseIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pageFade {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    xes_path = 'data/merged_event_log.xes'
    trips_csv = 'data/Total_Trips.csv'
    extracted_dir = 'data/extracted_routes'
    if not os.path.exists(xes_path): return None, None, None
    
    log = pm4py.read_xes(xes_path)
    df = pm4py.convert_to_dataframe(log)
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    
    trips_df = pd.DataFrame()
    if os.path.exists(trips_csv):
        trips_df = pd.read_csv(trips_csv)
        trips_df.columns = trips_df.columns.str.strip()
        if 'Total_Trips' in trips_df.columns:
            trips_df['Total_Trips_Numeric'] = pd.to_numeric(trips_df['Total_Trips'], errors='coerce').fillna(0).astype(int)

    schedule_frames = []
    if os.path.exists(extracted_dir):
        for file in os.listdir(extracted_dir):
            if not file.endswith('.csv'):
                continue

            file_path = os.path.join(extracted_dir, file)
            temp = pd.read_csv(file_path)
            temp.columns = temp.columns.str.strip()
            if not {'StopName', 'ArrivalTime', 'DepartureTime'}.issubset(set(temp.columns)):
                continue

            parts = file.replace('.csv', '').split('_')
            if len(parts) < 3:
                continue

            temp['case:concept:name'] = f"{parts[1]}_{parts[2]}"
            temp['concept:name'] = temp['StopName'].astype(str).str.strip()
            temp['stop_norm'] = temp['concept:name'].apply(normalize_stop_name)
            temp['ArrivalTime'] = temp['ArrivalTime'].astype(str).str.strip()
            temp['DepartureTime'] = temp['DepartureTime'].astype(str).str.strip()
            schedule_frames.append(temp[['case:concept:name', 'concept:name', 'stop_norm', 'ArrivalTime', 'DepartureTime']])

    schedule_df = pd.concat(schedule_frames, ignore_index=True) if schedule_frames else pd.DataFrame()
    return df, trips_df, schedule_df


def to_seconds(hms_text):
    try:
        t = datetime.strptime(str(hms_text), '%H:%M:%S')
        return (t.hour * 3600) + (t.minute * 60) + t.second
    except Exception:
        return None


def hms_from_seconds(total_seconds):
    total_seconds = int(total_seconds) % 86400
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def normalize_stop_name(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value).lower()).strip()


def resolve_stop_name(user_text, known_stops):
    if not known_stops:
        return None

    norm_to_original = {}
    for stop in known_stops:
        norm_to_original.setdefault(normalize_stop_name(stop), stop)

    q_norm = normalize_stop_name(user_text)
    if q_norm in norm_to_original:
        return norm_to_original[q_norm]

    for norm, original in norm_to_original.items():
        if q_norm and q_norm in norm:
            return original

    candidates = list(norm_to_original.keys())
    close = get_close_matches(q_norm, candidates, n=1, cutoff=0.65)
    if close:
        return norm_to_original[close[0]]
    return None


def resolve_stop_name_with_reason(user_text, known_stops):
    if not known_stops:
        return None, 'none', []

    q_norm = normalize_stop_name(user_text)
    norm_to_original = {}
    for stop in known_stops:
        norm_to_original.setdefault(normalize_stop_name(stop), stop)

    if q_norm in norm_to_original:
        return norm_to_original[q_norm], 'exact', [norm_to_original[q_norm]]

    contains = [s for s in known_stops if q_norm and q_norm in normalize_stop_name(s)]
    if contains:
        return contains[0], 'contains', contains

    candidates = list(norm_to_original.keys())
    close = get_close_matches(q_norm, candidates, n=3, cutoff=0.55)
    if close:
        nearest = norm_to_original[close[0]]
        nearest_list = [norm_to_original[item] for item in close]
        return nearest, 'nearest', nearest_list

    return None, 'none', []


def find_matching_stops(raw_text, known_stops):
    q_norm = normalize_stop_name(raw_text)
    matches = [s for s in known_stops if q_norm and q_norm in normalize_stop_name(s)]
    if matches:
        return sorted(set(matches))

    resolved, reason, related = resolve_stop_name_with_reason(raw_text, known_stops)
    if resolved:
        return sorted(set(related if related else [resolved]))
    return []


def duration_samples_for_case(case_df, origin_stop, destination_stop):
    case_df = case_df.reset_index(drop=True).copy()
    origin_norm = normalize_stop_name(origin_stop)
    dest_norm = normalize_stop_name(destination_stop)
    case_df['origin_sec'] = case_df['DepartureTime'].apply(to_seconds)
    case_df['dest_sec'] = case_df['ArrivalTime'].apply(to_seconds)

    if case_df.empty:
        return []

    route_start = case_df.loc[0, 'stop_norm']
    origin_indices = case_df.index[case_df['stop_norm'] == origin_norm].tolist()
    samples = []

    for origin_idx in origin_indices:
        origin_dep = case_df.at[origin_idx, 'origin_sec']
        if origin_dep is None:
            continue

        cursor = origin_idx + 1
        while cursor < len(case_df):
            current_stop = case_df.at[cursor, 'stop_norm']

            # Reaching route start again indicates a new trip cycle.
            if current_stop == route_start:
                break

            if current_stop == dest_norm:
                dest_arr = case_df.at[cursor, 'dest_sec']
                if dest_arr is not None and dest_arr >= origin_dep:
                    samples.append(dest_arr - origin_dep)
                break

            cursor += 1

    return samples


def average_duration_for_case(case_df, origin_stop, destination_stop):
    durations = duration_samples_for_case(case_df, origin_stop, destination_stop)
    if not durations:
        return None
    return int(sum(durations) / len(durations))


def next_departure_for_case(case_df, origin_stop):
    case_df = case_df.copy()
    origin_norm = normalize_stop_name(origin_stop)
    case_df['origin_sec'] = case_df['DepartureTime'].apply(to_seconds)
    departures = sorted(case_df.loc[case_df['stop_norm'] == origin_norm, 'origin_sec'].dropna().tolist())
    if not departures:
        return None

    now = datetime.now()
    now_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    return next((d for d in departures if d >= now_sec), departures[0])


def extract_stops_from_text(prompt_text):
    text = prompt_text.strip()
    from_to_match = re.search(r'from\s+(.+?)\s+to\s+(.+?)(?:\s+[—-]\s+|\?|$)', text, flags=re.IGNORECASE)
    if from_to_match:
        return from_to_match.group(1).strip(' .?!,'), from_to_match.group(2).strip(' .?!,')

    connect_match = re.search(r'connect\s+(.+?)\s+to\s+(.+?)(?:\s+[—-]\s+|\?|$)', text, flags=re.IGNORECASE)
    if connect_match:
        return connect_match.group(1).strip(' .?!,'), connect_match.group(2).strip(' .?!,')

    return None, None


def grounded_trip_response(prompt_text, schedule_df):
    if schedule_df is None or schedule_df.empty:
        return "I could not find extracted route schedule data in data/extracted_routes."

    known_stops = sorted(schedule_df['concept:name'].dropna().astype(str).str.strip().unique().tolist())
    lower_prompt = prompt_text.lower().strip()

    if lower_prompt in {'hi', 'hello', 'assalam o alaikum', 'salam'}:
        return "Hello! Ask me about routes, travel time, transfers, and next departures between CDA stops."

    through_match = re.search(r'through\s+(.+?)(?:\?|$)', prompt_text, flags=re.IGNORECASE)
    if through_match and ('which route' in lower_prompt or 'goes through' in lower_prompt):
        raw_stop = through_match.group(1).strip(' .?!,')
        matched_stops = find_matching_stops(raw_stop, known_stops)
        if not matched_stops:
            return f"Stop not found in CDA records: {raw_stop}."

        routes = sorted(schedule_df.loc[schedule_df['concept:name'].isin(matched_stops), 'case:concept:name'].unique().tolist())
        if not routes:
            return f"No route currently includes {raw_stop}."

        stops_text = ", ".join(matched_stops[:5])
        suffix = "" if len(matched_stops) <= 5 else ", ..."
        return (
            f"Routes that go through {raw_stop}: {', '.join(routes)}."
            f"\nMatched stop names: {stops_text}{suffix}."
        )

    last_bus_match = re.search(r'last\s+bus.*from\s+(.+?)(?:\?|$)', prompt_text, flags=re.IGNORECASE)
    if last_bus_match:
        raw_stop = last_bus_match.group(1).strip(' .?!,')
        stop, reason, near_list = resolve_stop_name_with_reason(raw_stop, known_stops)
        if not stop:
            return f"Stop not found in CDA records: {raw_stop}."

        rows = schedule_df[schedule_df['concept:name'] == stop].copy()
        if rows.empty:
            return f"No departures found for {stop}."

        rows['dep_sec'] = rows['DepartureTime'].apply(to_seconds)
        rows = rows.dropna(subset=['dep_sec'])
        if rows.empty:
            return f"No valid departure times found for {stop}."

        last_by_route = rows.groupby('case:concept:name')['dep_sec'].max().sort_values(ascending=False)
        all_lines = []
        for route_case, dep_sec in last_by_route.items():
            all_lines.append(f"- {route_case}: {hms_from_seconds(dep_sec)}")

        if reason == 'nearest' and normalize_stop_name(raw_stop) != normalize_stop_name(stop):
            near_text = ", ".join(near_list[:3]) if near_list else stop
            return (
                f"There is no CDA stop exactly named {raw_stop}. "
                f"Closest matching stop(s): {near_text}.\n"
                f"Last available departures from {stop}:\n"
                + "\n".join(all_lines)
            )

        return "Last available departures from " + stop + ":\n" + "\n".join(all_lines)

    origin_raw, dest_raw = extract_stops_from_text(prompt_text)
    if origin_raw and dest_raw:
        origin, origin_reason, origin_near = resolve_stop_name_with_reason(origin_raw, known_stops)
        destination, dest_reason, dest_near = resolve_stop_name_with_reason(dest_raw, known_stops)

        if not origin or not destination:
            missing = origin_raw if not origin else dest_raw
            return f"Stop not found in CDA records: {missing}."

        schedule_norm = schedule_df['concept:name'].apply(normalize_stop_name)
        origin_norm = normalize_stop_name(origin)
        dest_norm = normalize_stop_name(destination)

        origin_routes = set(schedule_df.loc[schedule_norm == origin_norm, 'case:concept:name'].unique().tolist())
        dest_routes = set(schedule_df.loc[schedule_norm == dest_norm, 'case:concept:name'].unique().tolist())
        direct_route_cases = sorted(origin_routes.intersection(dest_routes))

        direct_options = []
        for route_case in direct_route_cases:
            case_df = schedule_df[schedule_df['case:concept:name'] == route_case]
            avg_duration = average_duration_for_case(case_df, origin, destination)
            next_dep = next_departure_for_case(case_df, origin)
            direct_options.append({
                'route': route_case,
                'duration': avg_duration,
                'next_dep': next_dep
            })

        if direct_options:
            direct_options = sorted(
                direct_options,
                key=lambda x: x['duration'] if x['duration'] is not None else 10**9
            )
            lines = []
            for option in direct_options[:5]:
                duration_text = format_duration_long(option['duration']) if option['duration'] is not None else "N/A"
                next_dep_text = hms_from_seconds(option['next_dep']) if option['next_dep'] is not None else "N/A"
                lines.append(
                    f"- {option['route']} | est. travel time: {duration_text} | next departure from {origin}: {next_dep_text}"
                )
            return (
                f"Options from {origin} to {destination} (grounded in CDA extracted schedules):\n"
                + "\n".join(lines)
            )

        transfer_candidates = []
        for route_a in origin_routes:
            route_a_stops = set(schedule_df.loc[schedule_df['case:concept:name'] == route_a, 'concept:name'].unique().tolist())
            for route_b in dest_routes:
                if route_a == route_b:
                    continue
                route_b_stops = set(schedule_df.loc[schedule_df['case:concept:name'] == route_b, 'concept:name'].unique().tolist())
                common_stops = sorted(route_a_stops.intersection(route_b_stops) - {origin, destination})
                for transfer_stop in common_stops[:2]:
                    transfer_candidates.append((route_a, transfer_stop, route_b))

        if transfer_candidates:
            lines = []
            for route_a, transfer_stop, route_b in transfer_candidates[:5]:
                lines.append(f"- {route_a} -> transfer at {transfer_stop} -> {route_b}")
            warning_lines = []
            if origin_reason == 'nearest' and normalize_stop_name(origin_raw) != normalize_stop_name(origin):
                warning_lines.append(f"No exact CDA stop named {origin_raw}; using nearest stop {origin}.")
            if dest_reason == 'nearest' and normalize_stop_name(dest_raw) != normalize_stop_name(destination):
                warning_lines.append(f"No exact CDA stop named {dest_raw}; using nearest stop {destination}.")

            prefix = "\n".join(warning_lines)
            if prefix:
                prefix += "\n"
            return (
                prefix
                + f"No direct single-route option found from {origin} to {destination}. Possible transfer options:\n"
                + "\n".join(lines)
            )

        return f"No direct or one-transfer option found from {origin} to {destination} in current CDA extracted schedules."

    return (
        "I can answer these query types right now:"
        "\n- routes through a stop"
        "\n- last bus from a stop"
        "\n- travel options from STOP A to STOP B"
        "\nExample: How long does it take from Khanna Pul to Faizabad?"
    )

def format_duration_long(seconds):
    if pd.isna(seconds): return "00:00:00"
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@st.cache_data
def compute_dfg_metrics(df_input):
    log_to_process = log_converter.apply(df_input)
    dfg_perf = dfg_discovery.apply(log_to_process, variant=dfg_discovery.Variants.PERFORMANCE)
    dfg_freq = dfg_discovery.apply(log_to_process, variant=dfg_discovery.Variants.FREQUENCY)
    return dfg_perf, dfg_freq


@st.cache_data
def compute_route_boundaries(df_input):
    if df_input is None or df_input.empty:
        return set(), set()

    starts = set()
    ends = set()
    grouped = df_input.sort_values('time:timestamp').groupby('case:concept:name')

    for _, case_df in grouped:
        if case_df.empty:
            continue
        starts.add(str(case_df.iloc[0]['concept:name']))
        ends.add(str(case_df.iloc[-1]['concept:name']))

    return starts, ends


def build_network_dot(
    dfg_perf,
    dfg_freq,
    max_edges=80,
    title="Route Network",
    highlight_top_n=3,
    start_nodes=None,
    end_nodes=None,
    blocked_edges=None
):
    if not dfg_freq:
        return "digraph G { label=\"No edges found\"; }"

    ranked_edges = sorted(dfg_freq.items(), key=lambda item: item[1], reverse=True)[:max_edges]
    max_freq = max([freq for _, freq in ranked_edges]) if ranked_edges else 1

    # Identify top-N bottlenecks by highest transition duration.
    bottleneck_edges = set()
    if dfg_perf:
        perf_ranked = sorted(
            [(edge, dur) for edge, dur in dfg_perf.items() if dur is not None],
            key=lambda x: x[1],
            reverse=True
        )
        bottleneck_edges = set([edge for edge, _ in perf_ranked[:highlight_top_n]])

    lines = [
        "digraph G {",
        "  graph [bgcolor=\"transparent\", fontname=\"Helvetica\", fontcolor=\"#e2e8f0\", labelloc=\"t\", labeljust=\"l\", overlap=false, splines=true, ranksep=1.0, nodesep=0.35, layout=sfdp];",
        f"  label=\"{title}\";",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"#f8fafc\", color=\"#3b82f6\", penwidth=1.1, fontname=\"Helvetica\", fontsize=10];",
        "  edge [fontname=\"Helvetica\", fontsize=11, fontcolor=\"#f8fafc\", color=\"#22d3ee\"];"
    ]

    blocked_edges = blocked_edges or set()

    for (origin, destination), freq in ranked_edges:
        if (origin, destination) in blocked_edges:
            continue

        perf = dfg_perf.get((origin, destination), None)
        freq_ratio = freq / max_freq if max_freq else 0
        pen_width = 1.0 + (5.5 * freq_ratio)
        blue_tone = int(120 + 110 * min(1, freq_ratio))
        edge_color = f"#1d{blue_tone:02x}d8"
        dur_text = format_duration_long(perf) if perf is not None else "N/A"
        label = f"{dur_text} | n={freq}"

        if (origin, destination) in bottleneck_edges:
            edge_color = "#ef4444"
            pen_width = max(pen_width, 8.0)
            label = f"BOTTLENECK | {dur_text} | n={freq}"

        lines.append(
            f'  "{origin}" -> "{destination}" [label="{label}", penwidth={pen_width:.2f}, color="{edge_color}"];'
        )

    # Highlight start and end points for each route with light green nodes.
    start_nodes = start_nodes or set()
    end_nodes = end_nodes or set()
    boundary_nodes = sorted(start_nodes.union(end_nodes))
    for node in boundary_nodes:
        lines.append(
            f'  "{node}" [fillcolor="#dcfce7", color="#16a34a", penwidth=2.2, fontcolor="#14532d"];'
        )

    lines.append("}")
    return "\n".join(lines)


@st.cache_data
def compute_cycle_break_edges(schedule_subset_df):
    if schedule_subset_df is None or schedule_subset_df.empty:
        return set()

    blocked = set()
    for _, route_df in schedule_subset_df.groupby('case:concept:name'):
        case_df = route_df.reset_index(drop=True)
        if len(case_df) < 2:
            continue

        route_start_norm = case_df.loc[0, 'stop_norm']
        for idx in range(len(case_df) - 1):
            next_norm = case_df.loc[idx + 1, 'stop_norm']
            if idx > 0 and next_norm == route_start_norm:
                curr_name = str(case_df.loc[idx, 'concept:name'])
                next_name = str(case_df.loc[idx + 1, 'concept:name'])
                blocked.add((curr_name, next_name))

    return blocked


def extract_segment_stop_sequence(schedule_df, route_case, from_norm, to_norm):
    case_df = schedule_df[schedule_df['case:concept:name'] == route_case].reset_index(drop=True)
    if case_df.empty:
        return []

    route_start = case_df.loc[0, 'stop_norm']
    from_indices = case_df.index[case_df['stop_norm'] == from_norm].tolist()
    for from_idx in from_indices:
        seq = [str(case_df.loc[from_idx, 'concept:name'])]
        cursor = from_idx + 1
        while cursor < len(case_df):
            current_norm = case_df.loc[cursor, 'stop_norm']
            if current_norm == route_start:
                break

            seq.append(str(case_df.loc[cursor, 'concept:name']))
            if current_norm == to_norm:
                return seq
            cursor += 1

    from_rows = case_df.loc[case_df['stop_norm'] == from_norm, 'concept:name']
    to_rows = case_df.loc[case_df['stop_norm'] == to_norm, 'concept:name']
    if not from_rows.empty and not to_rows.empty:
        return [str(from_rows.iloc[0]), str(to_rows.iloc[0])]
    return []


def build_ordered_stop_list_from_segments(schedule_df, path_result):
    segments = path_result.get('segments', [])
    if not segments:
        return []

    ordered = []
    for seg in segments:
        part = extract_segment_stop_sequence(schedule_df, seg['route'], seg['from'], seg['to'])
        if not part:
            continue

        if not ordered:
            ordered.extend(part)
        elif ordered[-1] == part[0]:
            ordered.extend(part[1:])
        else:
            ordered.extend(part)

    return ordered


@st.cache_data(show_spinner=False)
def geocode_stop(stop_name):
    queries = [
        f"{stop_name} bus stop, Islamabad, Rawalpindi, Pakistan",
        f"{stop_name}, Islamabad, Pakistan",
        f"{stop_name}, Rawalpindi, Pakistan",
        f"{stop_name}, Pakistan"
    ]

    for query in queries:
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "viewbox": "72.80,33.90,73.35,33.45",
                    "bounded": 1
                },
                headers={"User-Agent": "CDA-Transit-Analytics-Task6/1.0"},
                timeout=8
            )
            response.raise_for_status()
            data = response.json()
            if data:
                return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
        except Exception:
            continue

    return None


@st.cache_data(show_spinner=False)
def get_road_path_between_points(from_lon, from_lat, to_lon, to_lat):
    try:
        url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{from_lon},{from_lat};{to_lon},{to_lat}"
        )
        response = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson"},
            timeout=8
        )
        response.raise_for_status()
        payload = response.json()
        routes = payload.get("routes", [])
        if not routes:
            return None
        return routes[0].get("geometry", {}).get("coordinates", None)
    except Exception:
        return None


def render_personal_route_real_map(schedule_df, path_result):
    segments = path_result.get('segments', [])
    if segments:
        with st.expander("Complete Route Steps", expanded=True):
            for step_idx, seg in enumerate(segments, start=1):
                from_name = path_result.get('norm_to_name', {}).get(seg['from'], seg['from'])
                to_name = path_result.get('norm_to_name', {}).get(seg['to'], seg['to'])
                st.markdown(
                    f"{step_idx}. Use **{seg['route']}** from **{from_name}** to **{to_name}** "
                    f"(est. {format_duration_long(seg['dur'])})"
                )

    ordered_stops = build_ordered_stop_list_from_segments(schedule_df, path_result)
    if len(ordered_stops) < 2:
        st.warning("Not enough stop points to render a real map. Please use the complete route steps above.")
        return

    points = []
    missing_stops = []
    for idx, stop_name in enumerate(ordered_stops):
        coords = geocode_stop(stop_name)
        if not coords:
            missing_stops.append(stop_name)
            continue

        if idx == 0 or idx == len(ordered_stops) - 1:
            color = [34, 197, 94, 220]
            radius = 95
        else:
            color = [59, 130, 246, 210]
            radius = 65

        points.append({
            "stop": stop_name,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "color": color,
            "radius": radius
        })

    if len(points) < 2:
        st.warning("Could not geocode enough stops to draw the route on an actual map. Follow the complete route steps above.")
        if missing_stops:
            st.caption("Missing geocodes: " + ", ".join(sorted(set(missing_stops))[:8]))
        return

    if missing_stops:
        st.info(
            "Some stops could not be geocoded exactly, so the map is rendered with available points. "
            "Use the complete route steps above for exact stop-by-stop guidance."
        )

    snapped_path = []
    for idx in range(len(points) - 1):
        p1 = points[idx]
        p2 = points[idx + 1]
        road_coords = get_road_path_between_points(p1["lon"], p1["lat"], p2["lon"], p2["lat"])
        if road_coords and len(road_coords) >= 2:
            if snapped_path and snapped_path[-1] == road_coords[0]:
                snapped_path.extend(road_coords[1:])
            else:
                snapped_path.extend(road_coords)
        else:
            # Fallback to straight segment when road service is unavailable.
            if not snapped_path:
                snapped_path.append([p1["lon"], p1["lat"]])
            snapped_path.append([p2["lon"], p2["lat"]])

    path_df = pd.DataFrame([{"path": snapped_path}])
    points_df = pd.DataFrame(points)

    path_layer = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        get_width=7,
        width_min_pixels=4,
        width_max_pixels=11,
        get_color=[34, 211, 238]
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points_df,
        get_position='[lon, lat]',
        get_fill_color='color',
        get_radius='radius',
        radius_min_pixels=4,
        radius_max_pixels=11,
        pickable=True
    )

    text_layer = pdk.Layer(
        "TextLayer",
        data=points_df,
        get_position='[lon, lat]',
        get_text='stop',
        get_color=[15, 23, 42],
        get_size=12,
        get_alignment_baseline='top'
    )

    center_lat = sum(p["lat"] for p in points) / len(points)
    center_lon = sum(p["lon"] for p in points) / len(points)
    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
            initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=11, pitch=25),
            layers=[path_layer, scatter_layer, text_layer],
            tooltip={"text": "{stop}"}
        ),
        use_container_width=True
    )


def find_optimal_path(schedule_df, origin_stop, destination_stop):
    if schedule_df is None or schedule_df.empty:
        return {"ok": False, "message": "Route schedule data is not available."}

    origin_norm = normalize_stop_name(origin_stop)
    dest_norm = normalize_stop_name(destination_stop)

    if origin_norm == dest_norm:
        return {
            "ok": True,
            "total_buses": 0,
            "total_duration": 0,
            "next_departure": None,
            "segments": [],
            "norm_to_name": {origin_norm: origin_stop},
            "message": f"You selected the same stop for both origin and destination: {origin_stop}."
        }

    route_edge_samples = {}
    norm_to_name = {}

    for route_case, route_df in schedule_df.groupby('case:concept:name'):
        case_df = route_df.reset_index(drop=True).copy()
        if case_df.empty:
            continue

        route_start = case_df.loc[0, 'stop_norm']
        for _, row in case_df.iterrows():
            norm_to_name.setdefault(row['stop_norm'], row['concept:name'])

        for idx in range(len(case_df) - 1):
            u_norm = case_df.at[idx, 'stop_norm']
            v_norm = case_df.at[idx + 1, 'stop_norm']
            dep_u = to_seconds(case_df.at[idx, 'DepartureTime'])
            arr_v = to_seconds(case_df.at[idx + 1, 'ArrivalTime'])

            if idx > 0 and v_norm == route_start:
                continue
            if dep_u is None or arr_v is None or arr_v < dep_u:
                continue

            key = (route_case, u_norm, v_norm)
            route_edge_samples.setdefault(key, []).append(arr_v - dep_u)

    adjacency = {}
    for (route_case, u_norm, v_norm), samples in route_edge_samples.items():
        avg_dur = int(sum(samples) / len(samples)) if samples else None
        if avg_dur is None:
            continue
        adjacency.setdefault(u_norm, []).append((route_case, v_norm, avg_dur))

    if origin_norm not in adjacency and origin_norm != dest_norm:
        return {"ok": False, "message": f"No outgoing route found from {origin_stop}."}

    start_state = (origin_norm, None)
    pq = [(0, 0, origin_norm, None)]
    best_cost = {start_state: (0, 0)}
    prev = {}
    best_destination_state = None
    best_destination_cost = None

    while pq:
        buses_used, total_dur, stop_norm, current_route = heapq.heappop(pq)
        state = (stop_norm, current_route)
        if best_cost.get(state, (10**9, 10**12)) != (buses_used, total_dur):
            continue

        if stop_norm == dest_norm:
            best_destination_state = state
            best_destination_cost = (buses_used, total_dur)
            break

        for next_route, next_stop, edge_dur in adjacency.get(stop_norm, []):
            add_bus = 0 if current_route == next_route else 1
            candidate_cost = (buses_used + add_bus, total_dur + edge_dur)
            next_state = (next_stop, next_route)

            if candidate_cost < best_cost.get(next_state, (10**9, 10**12)):
                best_cost[next_state] = candidate_cost
                prev[next_state] = (state, next_route, edge_dur)
                heapq.heappush(pq, (candidate_cost[0], candidate_cost[1], next_stop, next_route))

    if best_destination_state is None:
        return {
            "ok": False,
            "message": f"No route path found from {origin_stop} to {destination_stop} in current CDA schedules."
        }

    segments = []
    edge_path = []
    cursor = best_destination_state
    while cursor != start_state:
        if cursor not in prev:
            break
        parent_state, route_used, edge_dur = prev[cursor]
        edge_path.append((parent_state[0], cursor[0], route_used, edge_dur))
        cursor = parent_state
    edge_path.reverse()

    if not edge_path:
        return {
            "ok": True,
            "total_buses": 0,
            "total_duration": 0,
            "next_departure": None,
            "segments": [],
            "norm_to_name": norm_to_name,
            "message": f"You are already at destination: {destination_stop}."
        }

    current_segment = {
        'route': edge_path[0][2],
        'from': edge_path[0][0],
        'to': edge_path[0][1],
        'dur': edge_path[0][3]
    }
    for u_norm, v_norm, route_used, edge_dur in edge_path[1:]:
        if route_used == current_segment['route']:
            current_segment['to'] = v_norm
            current_segment['dur'] += edge_dur
        else:
            segments.append(current_segment)
            current_segment = {
                'route': route_used,
                'from': u_norm,
                'to': v_norm,
                'dur': edge_dur
            }
    segments.append(current_segment)

    total_buses = best_destination_cost[0]
    total_duration = best_destination_cost[1]

    first_route_df = schedule_df[schedule_df['case:concept:name'] == segments[0]['route']]
    next_dep = next_departure_for_case(first_route_df, origin_stop)

    return {
        "ok": True,
        "total_buses": total_buses,
        "total_duration": total_duration,
        "next_departure": next_dep,
        "segments": segments,
        "norm_to_name": norm_to_name,
        "message": ""
    }


def build_personal_route_dot(path_result, title="Personal Route Map"):
    if not path_result.get("ok"):
        msg = path_result.get("message", "No path found")
        return f'digraph G {{ label="{msg}"; }}'

    segments = path_result.get("segments", [])
    norm_to_name = path_result.get("norm_to_name", {})
    if not segments:
        return f'digraph G {{ label="{title}"; }}'

    lines = [
        "digraph G {",
        "  graph [bgcolor=\"transparent\", fontname=\"Helvetica\", fontcolor=\"#e2e8f0\", labelloc=\"t\", labeljust=\"l\", ranksep=1.2, nodesep=0.45, splines=true];",
        f"  label=\"{title}\";",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"#f8fafc\", color=\"#3b82f6\", penwidth=1.2, fontsize=11];",
        "  edge [fontname=\"Helvetica\", fontsize=10, fontcolor=\"#f8fafc\", color=\"#22d3ee\", penwidth=4.2];"
    ]

    start_norm = segments[0]['from']
    end_norm = segments[-1]['to']
    start_name = norm_to_name.get(start_norm, start_norm)
    end_name = norm_to_name.get(end_norm, end_norm)

    for seg in segments:
        from_name = norm_to_name.get(seg['from'], seg['from'])
        to_name = norm_to_name.get(seg['to'], seg['to'])
        seg_label = f"{seg['route']} | {format_duration_long(seg['dur'])}"
        lines.append(f'  "{from_name}" -> "{to_name}" [label="{seg_label}"];')

    lines.append(f'  "{start_name}" [fillcolor="#dcfce7", color="#16a34a", penwidth=2.5, fontcolor="#14532d"];')
    lines.append(f'  "{end_name}" [fillcolor="#dcfce7", color="#16a34a", penwidth=2.5, fontcolor="#14532d"];')
    lines.append("}")
    return "\n".join(lines)


def best_route_recommendation(schedule_df, origin_stop, destination_stop):
    result = find_optimal_path(schedule_df, origin_stop, destination_stop)
    if not result.get("ok"):
        return result.get("message", "No route found.")

    if result.get("message") and not result.get("segments"):
        return result["message"]

    dep_text = hms_from_seconds(result['next_departure']) if result['next_departure'] is not None else "N/A"
    lines = [
        "Best option (optimized for fewer buses, then shortest travel time):",
        f"- Total buses: {result['total_buses']}",
        f"- Estimated travel time: {format_duration_long(result['total_duration'])}",
        f"- Next departure from {origin_stop}: {dep_text}",
        "- Trip plan:"
    ]

    for seg in result['segments']:
        from_name = result['norm_to_name'].get(seg['from'], seg['from'])
        to_name = result['norm_to_name'].get(seg['to'], seg['to'])
        lines.append(
            f"  - Take {seg['route']} from {from_name} to {to_name} ({format_duration_long(seg['dur'])})"
        )

    return "\n".join(lines)

# --- Execution ---
df, trips_df, schedule_df = load_data()

if df is not None:
    # --- Sidebar ---
    st.sidebar.title("Network Control")
    
    # NEW: AI Agent Configuration in Sidebar
    st.sidebar.divider()
    st.sidebar.subheader("AI Agent Settings")
    enable_analytics = st.sidebar.checkbox("Enable process map analytics", value=False)
    show_enhanced_maps = st.sidebar.checkbox("Use enhanced network maps", value=True)
    graph_max_edges = st.sidebar.slider("Map detail (max edges)", min_value=20, max_value=220, value=110, step=10)
    fast_mode = st.sidebar.checkbox("Fast mode (local grounded answers)", value=True)
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    st.sidebar.caption("Fast mode is recommended for instant and reliable responses.")
    st.sidebar.caption("Leave process map analytics off for much faster initial page load.")
    
    all_routes = sorted(df['case:concept:name'].unique())
    selected_case = st.sidebar.selectbox("Select Route Segment", ["Full Network"] + all_routes)

    # Filtering Logic
    if selected_case != "Full Network":
        filtered_df = df[df['case:concept:name'] == selected_case]
        selected_schedule_df = schedule_df[schedule_df['case:concept:name'] == selected_case] if schedule_df is not None and not schedule_df.empty else pd.DataFrame()
        display_name = selected_case
        if "_" in selected_case and not trips_df.empty:
            route_part, dir_part = selected_case.split("_", 1)
            match = trips_df[(trips_df['Route_ID'].astype(str) == route_part) & (trips_df['Direction'].astype(str) == dir_part)]
            display_trips = int(match.iloc[0]['Total_Trips_Numeric']) if (not match.empty and 'Total_Trips_Numeric' in match.columns) else 0
        else:
            display_trips = 0
    else:
        filtered_df = df
        selected_schedule_df = schedule_df if schedule_df is not None else pd.DataFrame()
        display_name = "Comprehensive Network"
        display_trips = int(trips_df['Total_Trips_Numeric'].sum()) if (not trips_df.empty and 'Total_Trips_Numeric' in trips_df.columns) else "N/A"

    # --- Header ---
    st.markdown(f'<span class="main-title">CDA Transit Analytics</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="sub-title">Route Analytics: {display_name}</span>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-strip">'
        '<span class="hero-pill">Process Discovery Ready</span>'
        '<span class="hero-pill">Agentic Planner Active</span>'
        '<span class="hero-pill">Personal Maps Enabled</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(f"""
        <div class="stats-box">
            <div class="stats-title">Verified Trip Frequency</div>
            <div class="stats-value">{display_trips}</div>
        </div>
    """, unsafe_allow_html=True)

    if enable_analytics:
        st.markdown('<div class="section-card"><b>Analytics</b><br/>Combined and route-focused network maps with readable transition labels.</div>', unsafe_allow_html=True)

        combined_perf, combined_freq = compute_dfg_metrics(df)
        selected_perf, selected_freq = compute_dfg_metrics(filtered_df)
        combined_starts, combined_ends = compute_route_boundaries(df)
        selected_starts, selected_ends = compute_route_boundaries(filtered_df)
        combined_blocked_edges = compute_cycle_break_edges(schedule_df)
        selected_blocked_edges = compute_cycle_break_edges(selected_schedule_df)

        case_durations = filtered_df.groupby('case:concept:name')['time:timestamp'].agg(['min', 'max'])
        case_durations['duration'] = (case_durations['max'] - case_durations['min']).dt.total_seconds()

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Throughput", format_duration_long(case_durations['duration'].mean()))
        col2.metric("Minimum Time", format_duration_long(case_durations['duration'].min()))
        col3.metric("Maximum Time", format_duration_long(case_durations['duration'].max()))

        map_tab_1, map_tab_2 = st.tabs(["Combined Network Map", "Selected Route Map"])

        with map_tab_1:
            st.subheader("Combined Network Overview")
            if show_enhanced_maps:
                dot_text = build_network_dot(
                    combined_perf,
                    combined_freq,
                    max_edges=graph_max_edges,
                    title="All Routes Combined",
                    highlight_top_n=3,
                    start_nodes=combined_starts,
                    end_nodes=combined_ends,
                    blocked_edges=combined_blocked_edges
                )
                st.graphviz_chart(dot_text, use_container_width=True)
            else:
                combined_log = log_converter.apply(df)
                parameters = {
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.FORMAT: "png",
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.RANKDIR: "TB",
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.AGGREGATION_MEASURE: "mean"
                }
                gviz = dfg_visualization.apply(combined_perf, log=combined_log, variant=dfg_visualization.Variants.PERFORMANCE, parameters=parameters)
                st.graphviz_chart(gviz.source, use_container_width=True)

        with map_tab_2:
            st.subheader(f"Route Focus: {display_name}")
            if show_enhanced_maps:
                selected_edges = max(20, min(graph_max_edges, 100))
                dot_text = build_network_dot(
                    selected_perf,
                    selected_freq,
                    max_edges=selected_edges,
                    title=f"Selected Route: {display_name}",
                    highlight_top_n=3,
                    start_nodes=selected_starts,
                    end_nodes=selected_ends,
                    blocked_edges=selected_blocked_edges
                )
                st.graphviz_chart(dot_text, use_container_width=True)
            else:
                selected_log = log_converter.apply(filtered_df)
                parameters = {
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.FORMAT: "png",
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.RANKDIR: "TB",
                    dfg_visualization.Variants.PERFORMANCE.value.Parameters.AGGREGATION_MEASURE: "mean"
                }
                gviz = dfg_visualization.apply(selected_perf, log=selected_log, variant=dfg_visualization.Variants.PERFORMANCE, parameters=parameters)
                st.graphviz_chart(gviz.source, use_container_width=True)

        st.subheader("Critical Bottlenecks")
        perf_list = []
        for edge, duration in selected_perf.items():
            freq = selected_freq.get(edge, 0)
            perf_list.append({
                "Origin": edge[0],
                "Destination": edge[1],
                "Travel Time": format_duration_long(duration),
                "Transition Count": freq,
                "raw": duration
            })

        if perf_list:
            bottleneck_df = pd.DataFrame(perf_list).sort_values(by="raw", ascending=False).head(8)
            st.dataframe(bottleneck_df[["Origin", "Destination", "Travel Time", "Transition Count"]], use_container_width=True)

        
    else:
        st.info("Process map analytics are disabled for a faster GUI. Enable them from the sidebar when needed.")

    # --- Task 5: Powerful Agentic AI Trip Planner ---
    st.divider()
    st.subheader("Agentic AI Trip Planner")

    st.markdown('<div class="section-card"><b>Quick Planner (Dropdown Mode)</b><br/>Select origin and destination stops for an optimized recommendation based on minimum buses first, then minimum travel time.</div>', unsafe_allow_html=True)
    unique_stops = sorted(schedule_df['concept:name'].dropna().astype(str).str.strip().unique().tolist()) if schedule_df is not None and not schedule_df.empty else []
    planner_col1, planner_col2 = st.columns(2)
    with planner_col1:
        from_stop = st.selectbox("From", unique_stops, key="from_stop_dropdown") if unique_stops else None
    with planner_col2:
        to_stop = st.selectbox("Where to", unique_stops, key="to_stop_dropdown") if unique_stops else None

    if st.button("Find Best Route", use_container_width=True):
        if not from_stop or not to_stop:
            st.warning("Please select both stops.")
        else:
            plan_text = best_route_recommendation(schedule_df, from_stop, to_stop)
            st.success(plan_text)

    # --- Task 6: Personal Route Map (Bonus) ---
    st.divider()
    st.subheader("Personal Route Map")
    st.markdown(
        '<div class="section-card"><b>Member Route Builder</b><br/>'
        'For each member, choose the nearest CDA stop to home. The app computes the best route from FAST University '
        'to that stop (minimum buses first, then minimum travel time), and visualizes the route map.</div>',
        unsafe_allow_html=True
    )

    if "task6_records" not in st.session_state:
        st.session_state.task6_records = []
    if "task6_selected_member_idx" not in st.session_state:
        st.session_state.task6_selected_member_idx = 0

    if unique_stops:
        default_fast = resolve_stop_name("FAST University", unique_stops)
        fast_origin_stop = default_fast if default_fast else unique_stops[0]

        member_col1, member_col2 = st.columns(2)
        with member_col1:
            member_name = st.text_input("Member Name", key="task6_member_name")
            home_area = st.text_input("Home Area", key="task6_home_area")
        with member_col2:
            nearest_stop = st.selectbox(
                "Nearest CDA Stop to Home",
                unique_stops,
                key="task6_nearest_stop"
            )
            origin_preview = st.text_input(
                "Origin (Fixed as FAST University)",
                value=fast_origin_stop,
                disabled=True,
                key="task6_origin_preview"
            )

        if st.button("Generate Personal Route", key="task6_generate", use_container_width=True):
            if not member_name.strip() or not home_area.strip():
                st.warning("Please provide both member name and home area.")
            else:
                result = find_optimal_path(schedule_df, fast_origin_stop, nearest_stop)
                if not result.get("ok"):
                    st.error(result.get("message", "Could not build route."))
                else:
                    route_lines = []
                    for seg in result.get("segments", []):
                        from_name = result['norm_to_name'].get(seg['from'], seg['from'])
                        to_name = result['norm_to_name'].get(seg['to'], seg['to'])
                        route_lines.append(
                            f"{seg['route']}: {from_name} -> {to_name} ({format_duration_long(seg['dur'])})"
                        )

                    record = {
                        "Member": member_name.strip(),
                        "Home_Area": home_area.strip(),
                        "Origin": fast_origin_stop,
                        "Nearest_Stop": nearest_stop,
                        "Total_Buses": int(result.get("total_buses", 0)),
                        "Estimated_Travel_Time": format_duration_long(result.get("total_duration", 0)),
                        "Next_Departure": hms_from_seconds(result.get("next_departure")) if result.get("next_departure") is not None else "N/A",
                        "Route_Plan": " | ".join(route_lines) if route_lines else result.get("message", "No movement required."),
                        "path_result": result
                    }

                    existing_idx = None
                    for idx, existing in enumerate(st.session_state.task6_records):
                        if normalize_stop_name(existing["Member"]) == normalize_stop_name(record["Member"]):
                            existing_idx = idx
                            break

                    if existing_idx is not None:
                        st.session_state.task6_records[existing_idx] = record
                        st.session_state.task6_selected_member_idx = existing_idx
                        st.success(f"Route updated for {record['Member']} to nearest stop {record['Nearest_Stop']}.")
                    else:
                        st.session_state.task6_records.append(record)
                        st.session_state.task6_selected_member_idx = len(st.session_state.task6_records) - 1
                        st.success(f"Personal route generated for {record['Member']} ({record['Nearest_Stop']}) and saved.")

        if st.session_state.task6_records:
            st.markdown("### Member-wise Route Outputs")
            member_names = [f"{idx+1}. {rec['Member']} ({rec['Nearest_Stop']})" for idx, rec in enumerate(st.session_state.task6_records)]
            default_idx = min(st.session_state.task6_selected_member_idx, len(member_names) - 1)
            selected_member_label = st.selectbox("Select member to view route map", member_names, index=default_idx, key="task6_view_member")
            selected_idx = int(selected_member_label.split(".")[0]) - 1
            st.session_state.task6_selected_member_idx = selected_idx
            selected_record = st.session_state.task6_records[selected_idx]

            st.info(
                f"Member: {selected_record['Member']} | Home Area: {selected_record['Home_Area']} | "
                f"Nearest Stop: {selected_record['Nearest_Stop']} | Buses: {selected_record['Total_Buses']} | "
                f"Est. Time: {selected_record['Estimated_Travel_Time']}"
            )

            personal_dot = build_personal_route_dot(
                selected_record["path_result"],
                title=f"Task 6 Personal Map: {selected_record['Member']}"
            )
            map_tab_a, map_tab_b = st.tabs(["Schematic Route Map", "Actual Map View"])
            with map_tab_a:
                st.graphviz_chart(personal_dot, use_container_width=True)
            with map_tab_b:
                render_personal_route_real_map(schedule_df, selected_record["path_result"])

            summary_rows = []
            for rec in st.session_state.task6_records:
                summary_rows.append({
                    "Member": rec["Member"],
                    "Home_Area": rec["Home_Area"],
                    "Origin": rec["Origin"],
                    "Nearest_Stop": rec["Nearest_Stop"],
                    "Total_Buses": rec["Total_Buses"],
                    "Estimated_Travel_Time": rec["Estimated_Travel_Time"],
                    "Next_Departure": rec["Next_Departure"],
                    "Route_Plan": rec["Route_Plan"]
                })

            summary_df = pd.DataFrame(summary_rows)
            st.dataframe(summary_df, use_container_width=True)
            st.download_button(
                label="Download Summary CSV",
                data=summary_df.to_csv(index=False),
                file_name="personal_route_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "I'm your CDA AI Agent. I have access to your Event Logs and Trip CSV. Ask me anything!"}]

    # Scrollable chat container
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # --- Updated Task 5 Logic ---
    if prompt := st.chat_input("Ex: How long does it take from Khanna Pul to Faizabad?"):
        with chat_container:
            st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Agent is checking routes..."):
                        grounded_text = grounded_trip_response(prompt, schedule_df)

                        # Fast mode returns immediately from local data for low latency and no API dependency.
                        if fast_mode:
                            final_text = grounded_text
                        elif not api_key:
                            final_text = grounded_text + "\n\n(Enable Gemini key to rewrite this response style.)"
                        else:
                            llm = ChatGoogleGenerativeAI(
                                model="gemini-2.0-flash",
                                google_api_key=api_key,
                                temperature=0
                            )

                            rewrite_prompt = (
                                "You are a CDA transit assistant. Rewrite the following grounded answer into clear natural language. "
                                "Do not add any new facts and do not invent stops or routes.\n\n"
                                f"Grounded answer:\n{grounded_text}"
                            )
                            llm_response = llm.invoke(rewrite_prompt)
                            final_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

                        st.markdown(final_text)
                        st.session_state.messages.append({"role": "assistant", "content": final_text})

                except Exception:
                    # Fallback remains fully grounded in local route schedule data.
                    fallback_text = grounded_trip_response(prompt, schedule_df)
                    st.markdown(fallback_text)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_text})

else:
    st.error("Data files not found in /data directory.")