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

# Premium dark theme with custom CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #0f1535 100%);
    }

    [data-testid="stSidebar"] { display: none; }

    /* Header */
    .header-container {
        text-align: center;
        padding: 40px 0 30px 0;
        background: linear-gradient(135deg, #1a1f3a 0%, #16213e 100%);
        border-bottom: 2px solid #00d4ff;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 12px 12px;
    }

    .header-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .header-subtitle {
        color: #8b949e;
        font-size: 16px;
        margin-top: 8px;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #16213e 100%);
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
    }

    .metric-label {
        color: #8b949e;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: #00d4ff;
        margin-top: 8px;
    }

    /* News cards */
    .news-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #16213e 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.05);
    }

    .news-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
    }

    .news-headline {
        font-size: 18px;
        font-weight: 700;
        color: #e6edf3;
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .news-source {
        color: #8b949e;
        font-size: 12px;
        margin-bottom: 12px;
    }

    .news-summary {
        color: #c9d1d9;
        font-size: 14px;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Impact badge */
    .impact-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .impact-high {
        background-color: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid #f85149;
    }

    .impact-medium {
        background-color: rgba(255, 166, 87, 0.2);
        color: #ffa657;
        border: 1px solid #ffa657;
    }

    .impact-low {
        background-color: rgba(121, 192, 255, 0.2);
        color: #79c0ff;
        border: 1px solid #79c0ff;
    }

    /* Bias badges */
    .bias-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }

    .bias-hawkish {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
    }

    .bias-dovish {
        background-color: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
    }

    .bias-neutral {
        background-color: rgba(139, 148, 158, 0.15);
        color: #8b949e;
    }

    .news-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid #30363d;
        font-size: 12px;
        color: #8b949e;
    }

    .section-title {
        font-size: 24px;
        font-weight: 800;
        color: #e6edf3;
        margin-top: 40px;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #00d4ff;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_storage_manager():
    """Initialize storage manager."""
    return StorageManager()


def format_event_card(event: dict) -> str:
    """Format event as a clean news card."""
    bias = event.get('bias', 'neutral').lower()
    impact = event.get('impact', 'low').lower()

    # Impact badge styling
    impact_badge = f'<span class="impact-badge impact-{impact}">🎯 {impact.upper()}</span>'

    # Bias indicator
    bias_emoji = {'hawkish': '🔴', 'dovish': '🔵', 'neutral': '⚪'}.get(bias, '⚪')
    bias_badge = f'<span class="bias-badge bias-{bias}">{bias_emoji} {bias.title()}</span>'

    # Prediction accuracy
    if event.get('prediction_correct') is True:
        accuracy_text = '<span style="color: #58a6ff;">✓ Prediction Correct</span>'
    elif event.get('prediction_correct') is False:
        accuracy_text = '<span style="color: #f85149;">✗ Prediction Missed</span>'
    else:
        accuracy_text = '<span style="color: #8b949e;">⏳ Pending</span>'

    source = event.get('source', 'Unknown').replace('_', ' ').title()
    date = event.get('published_at', 'N/A')[:10]

    return f"""
    <div class="news-card">
        <div class="news-headline">{event.get('headline', 'Untitled')}</div>
        <div class="news-source">📰 {source} · {date}</div>
        <div class="news-summary">{event.get('summary', event.get('headline', '')[:200])}</div>
        <div style="margin-bottom: 12px;">
            {impact_badge}
            {bias_badge}
        </div>
        <div class="news-meta">
            <span>Direction: {event.get('price_direction', 'N/A')}</span>
            <span>{accuracy_text}</span>
        </div>
    </div>
    """


def main():
    """Main dashboard app."""
    storage = get_storage_manager()

    # Premium header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📊 MacroSentry</h1>
        <p class="header-subtitle">Autonomous Fed & Market Surveillance with Real-Time Bias Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Get data
    dashboard_data = storage.get_dashboard_data()

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        bias = dashboard_data["bias_summary"]["bias"].upper()
        bias_emoji = {'HAWKISH': '🔴', 'DOVISH': '🔵', 'NEUTRAL': '⚪'}.get(bias, '❓')
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Bias</div>
            <div class="metric-value" style="color: #00d4ff;">{bias_emoji} {bias}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        accuracy = dashboard_data["accuracy"]["accuracy"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Accuracy</div>
            <div class="metric-value">{accuracy:.1%}</div>
            <div style="font-size: 12px; color: #8b949e; margin-top: 4px;">{dashboard_data['accuracy']['total_runs']} runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        events = dashboard_data["accuracy"]["events_processed"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Events Tracked</div>
            <div class="metric-value">{events}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        bias_data = dashboard_data["bias_summary"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Today's Events</div>
            <div class="metric-value">{bias_data['hawkish'] + bias_data['dovish'] + bias_data['neutral']}</div>
        </div>
        """, unsafe_allow_html=True)

    # News feed - main focus
    st.markdown('<div class="section-title">📰 Market Events & News Feed</div>', unsafe_allow_html=True)

    recent = dashboard_data["recent_events"]
    if recent:
        for event in recent:
            st.markdown(format_event_card(event), unsafe_allow_html=True)
    else:
        st.info("No events yet. Run the pipeline to generate events.")

    # Bias distribution chart
    st.markdown('<div class="section-title">📊 Sentiment Distribution</div>', unsafe_allow_html=True)

    bias_data = dashboard_data["bias_summary"]
    bias_df = pd.DataFrame({
        "Sentiment": ["🔴 Hawkish", "🔵 Dovish", "⚪ Neutral"],
        "Count": [bias_data["hawkish"], bias_data["dovish"], bias_data["neutral"]],
    })

    col_chart, col_stats = st.columns([3, 1])
    with col_chart:
        st.bar_chart(bias_df.set_index("Sentiment")["Count"])
    with col_stats:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1f3a 0%, #16213e 100%); border: 1px solid #00d4ff; border-radius: 8px; padding: 16px;">
            <div style="color: #8b949e; font-size: 11px;">BREAKDOWN</div>
            <div style="color: #f85149; font-size: 14px; margin-top: 8px;">🔴 {bias_data['hawkish']} Hawkish</div>
            <div style="color: #58a6ff; font-size: 14px;">🔵 {bias_data['dovish']} Dovish</div>
            <div style="color: #8b949e; font-size: 14px;">⚪ {bias_data['neutral']} Neutral</div>
        </div>
        """, unsafe_allow_html=True)

    # Admin section
    st.markdown("---")
    st.markdown('<div style="font-size: 12px; color: #8b949e; text-align: center;">⚙️ Pipeline Controls</div>', unsafe_allow_html=True)

    col_admin1, col_admin2 = st.columns(2)
    with col_admin1:
        if st.button("▶️ Run Pipeline Now", use_container_width=True):
            with st.spinner("Processing events..."):
                pipeline = MacroSentryPipeline()
                result = pipeline.run()
                st.success(f"✅ Processed {result['events_processed']} events")
                st.rerun()

    with col_admin2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()


if __name__ == "__main__":
    main()
