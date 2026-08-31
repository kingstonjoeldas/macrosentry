"""Phase 6: Streamlit Dashboard - Live Fed/market surveillance dashboard."""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from macrosentry.storage import StorageManager
from macrosentry.pipeline import MacroSentryPipeline

st.set_page_config(
    page_title="MacroSentry",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme with custom CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .bias-hawkish { color: #f85149; }
    .bias-dovish { color: #58a6ff; }
    .bias-neutral { color: #8b949e; }
    .impact-high { color: #f85149; font-weight: bold; }
    .impact-medium { color: #ffa657; }
    .impact-low { color: #79c0ff; }
    .event-row {
        background-color: #0d1117;
        border-left: 3px solid #30363d;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_storage_manager():
    """Initialize storage manager."""
    return StorageManager()


def format_event_row(event: dict) -> str:
    """Format event for display."""
    bias_class = f"bias-{event.get('bias', 'neutral')}"
    impact_class = f"impact-{event.get('impact', 'low')}"

    return f"""
    <div class="event-row">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <div style="flex: 1;">
                <strong>{event.get('headline', 'Untitled')}</strong>
            </div>
            <div style="margin-left: 8px;">
                <span class="{bias_class}">●</span> {event.get('bias', 'N/A')}
            </div>
        </div>
        <div style="font-size: 0.85em; color: #8b949e; margin-bottom: 6px;">
            {event.get('source', 'unknown').replace('_', ' ').title()}
            · {event.get('published_at', 'N/A')[:10]}
        </div>
        <div style="font-size: 0.9em; color: #c9d1d9; margin-bottom: 6px;">
            {event.get('summary', event.get('headline', '')[:150])}...
        </div>
        <div style="display: flex; gap: 12px; font-size: 0.85em;">
            <span class="{impact_class}">Impact: {event.get('impact', 'N/A').upper()}</span>
            <span style="color: #8b949e;">
                Pred: {event.get('price_direction', 'N/A')}
                · Actual: {'✓' if event.get('prediction_correct') else '✗' if event.get('prediction_correct') is False else '?'}
            </span>
        </div>
    </div>
    """


def main():
    """Main dashboard app."""
    storage = get_storage_manager()

    # Header
    st.markdown("# 📊 MacroSentry")
    st.markdown("**Autonomous Fed & Market Surveillance · Self-Evaluating Predictions**")
    st.markdown("---")

    # Tabs
    tab_dashboard, tab_events, tab_runs, tab_settings = st.tabs(
        ["Dashboard", "Event Feed", "Pipeline Runs", "Settings"]
    )

    with tab_dashboard:
        # Get data
        dashboard_data = storage.get_dashboard_data()

        # Metrics row 1: Bias and accuracy
        col1, col2, col3 = st.columns(3)

        with col1:
            bias = dashboard_data["bias_summary"]["bias"].upper()
            bias_color = {
                "HAWKISH": "🔴",
                "DOVISH": "🔵",
                "NEUTRAL": "⚪"
            }.get(bias, "❓")

            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #8b949e; font-size: 0.9em;">TODAY'S BIAS</div>
                <div style="font-size: 2em; font-weight: bold; margin-top: 8px;">
                    {bias_color} {bias}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            accuracy = dashboard_data["accuracy"]["accuracy"]
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #8b949e; font-size: 0.9em;">SELF-EVAL ACCURACY</div>
                <div style="font-size: 2em; font-weight: bold; margin-top: 8px;">
                    {accuracy:.1%}
                </div>
                <div style="font-size: 0.85em; color: #8b949e; margin-top: 4px;">
                    {dashboard_data['accuracy']['total_runs']} runs
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            events_processed = dashboard_data["accuracy"]["events_processed"]
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #8b949e; font-size: 0.9em;">EVENTS TRACKED</div>
                <div style="font-size: 2em; font-weight: bold; margin-top: 8px;">
                    {events_processed}
                </div>
                <div style="font-size: 0.85em; color: #8b949e; margin-top: 4px;">
                    all-time
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Bias breakdown
        st.markdown("### Bias Distribution")
        bias_data = dashboard_data["bias_summary"]
        bias_df = pd.DataFrame({
            "Sentiment": ["Hawkish", "Dovish", "Neutral"],
            "Count": [bias_data["hawkish"], bias_data["dovish"], bias_data["neutral"]],
            "Color": ["#f85149", "#58a6ff", "#8b949e"]
        })

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.bar_chart(
                bias_df.set_index("Sentiment")["Count"],
                color=bias_df.set_index("Sentiment")["Color"].to_list()
            )
        with col_b:
            st.metric("Total Events", bias_data["hawkish"] + bias_data["dovish"] + bias_data["neutral"])

        st.markdown("---")

        # Latest events preview
        st.markdown("### Latest Events")
        recent = dashboard_data["recent_events"][:5]
        for event in recent:
            st.markdown(format_event_row(event), unsafe_allow_html=True)

    with tab_events:
        st.markdown("### Full Event Feed")
        recent = dashboard_data["recent_events"]
        if recent:
            for event in recent:
                st.markdown(format_event_row(event), unsafe_allow_html=True)
        else:
            st.info("No events yet. Run the pipeline to generate events.")

    with tab_runs:
        st.markdown("### Pipeline Run History")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Runs", dashboard_data["accuracy"]["total_runs"])
        with col2:
            st.metric("Overall Accuracy", f"{dashboard_data['accuracy']['accuracy']:.1%}")

        if st.button("Run Pipeline Now"):
            with st.spinner("Running MacroSentry pipeline..."):
                pipeline = MacroSentryPipeline()
                result = pipeline.run()

                st.success(f"Pipeline completed!")
                st.json({
                    "run_id": result["run_id"],
                    "events_processed": result["events_processed"],
                    "accuracy": f"{result['accuracy']:.1%}",
                    "errors": len(result["errors"])
                })

                # Refresh dashboard
                st.rerun()

    with tab_settings:
        st.markdown("### Configuration")

        st.markdown("#### API Keys")
        st.warning(
            "Note: Set environment variables instead of entering here:\n"
            "- `HUGGINGFACE_API_KEY`\n"
            "- `SUPABASE_URL`\n"
            "- `SUPABASE_KEY`\n"
            "- `ALPHA_VANTAGE_API_KEY`"
        )

        st.markdown("#### Futures Monitored")
        tickers = {
            "Gold (XAUUSD)": "XAUUSD",
            "Silver (XAGUSD)": "XAGUSD",
            "10-Year Notes (ZN)": "ZN",
            "Corn (ZC)": "ZC",
            "Soybeans (ZS)": "ZS",
            "S&P 500 (ES)": "ES",
        }
        for label, _ in tickers.items():
            st.checkbox(label, value=True, disabled=True)

        st.markdown("#### Evaluation Window")
        st.slider("Minutes after event to check price", 1, 60, 30, disabled=True)

        st.markdown("#### About")
        st.markdown("""
        **MacroSentry** is an autonomous pipeline that:
        1. Monitors Federal Reserve statements, speeches, and economic calendar
        2. Classifies each event (hawkish/dovish/neutral, low/medium/high impact)
        3. Grounds classifications using RAG and historical FOMC context
        4. Self-evaluates: checks price movements 30 minutes after each event
        5. Publishes results and accuracy scores to this dashboard

        **Stack:**
        - Ingestion: Fed.gov, economic calendars, market news
        - RAG: Sentence-Transformers + historical FOMC statements
        - Classification: Hugging Face Inference API (zero-shot)
        - Orchestration: LangGraph
        - Storage: Supabase
        - Scheduling: GitHub Actions
        - Dashboard: Streamlit

        **Cost:** $0 (free tier APIs only)
        """)


if __name__ == "__main__":
    main()
