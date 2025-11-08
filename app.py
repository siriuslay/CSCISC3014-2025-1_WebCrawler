"""
Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json

from config import settings
from scraper.core import DamaiScraper
from utils.database import db
from utils.logger import log


st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
            
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
            
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .concert-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .concert-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .progress-text {
        font-size: 1.1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .success-msg {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-msg {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .grab-panel {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Init Session State"""
    if 'concerts' not in st.session_state:
        st.session_state.concerts = []
    if 'scraping' not in st.session_state:
        st.session_state.scraping = False
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'show_grab_dialog' not in st.session_state:
        st.session_state.show_grab_dialog = False
    if 'current_concert' not in st.session_state:
        st.session_state.current_concert = None
    if 'grabbing' not in st.session_state:
        st.session_state.grabbing = False

    if 'grab_session_index' not in st.session_state:
        st.session_state.grab_session_index = 0
    if 'grab_ticket_index' not in st.session_state:
        st.session_state.grab_ticket_index = 0
    if 'grab_ticket_count' not in st.session_state:
        st.session_state.grab_ticket_count = 1


def show_header():
    st.markdown('<h1 class="main-header">🎫 Damai Ticket Scraper</h1>', unsafe_allow_html=True)
    st.markdown("---")


def show_sidebar():
    with st.sidebar:
        st.markdown("### 📊 System Setting")

        with st.expander("⚙️ Scraper Setting", expanded=True):
            max_pages = st.number_input("Page", 1, 20, 5, help="10 per page")
            page_size = st.number_input("#record per page", 5, 20, 10)
            delay = st.slider("time delay (second)", 0.5, 5.0, 2.0, 0.5)
        
        st.markdown("---")
        
        # database
        st.markdown("### 📈 Data Statistics")
        stats = db.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Concert", stats['total_concerts'])
        with col2:
            st.metric("Details", stats['total_details'])
        
        if stats['cities']:
            st.markdown("#### Venue TOP5")
            for city_stat in stats['cities'][:5]:
                st.text(f"{city_stat['city']}: {city_stat['count']}")
        
        return {'max_pages': max_pages, 'page_size': page_size, 'delay': delay}


def show_search_tab(config):
    st.markdown("### 🔍 Search Concert")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        keyword = st.text_input(
            "keyword",
            placeholder="such as: 周杰伦、演唱会、音乐节...",
            help="People、Concert Name..."
        )
    
    with col2:
        city = st.selectbox(
            "Choose City",
            ["全国", "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "南京", "武汉"]
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🚀 Begin Searching")
    
    if search_btn and keyword:
        with st.spinner("🔄 running..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.markdown('<p class="progress-text">⏳ Init Scraper...</p>', unsafe_allow_html=True)
                progress_bar.progress(20)
                
                status_text.markdown('<p class="progress-text">🌐 Connect Damai API...</p>', unsafe_allow_html=True)
                progress_bar.progress(40)

                scraper = DamaiScraper(cookie_str=settings.COOKIE)
                concerts = scraper.search_concerts(
                    keyword=keyword,
                    city=city,
                    max_pages=config['max_pages'],
                    page_size=config['page_size']
                )
                scraper.close()
                
                progress_bar.progress(80)
                status_text.markdown('<p class="progress-text">💾 Save Data...</p>', unsafe_allow_html=True)

                if concerts:
                    db.save_concerts(concerts)
                    st.session_state.concerts = concerts
                    st.session_state.search_history.append({
                        'keyword': keyword,
                        'city': city,
                        'count': len(concerts),
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                progress_bar.progress(100)
                status_text.markdown(
                    f'<div class="success-msg">✅ Get {len(concerts)} live Events!</div>',
                    unsafe_allow_html=True
                )
                
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                progress_bar.empty()
                status_text.markdown(
                    f'<div class="error-msg">❌ Failed: {str(e)}</div>',
                    unsafe_allow_html=True
                )
                log.error(f"Failed: {e}")
    
    if st.session_state.search_history:
        with st.expander("📜 Search History"):
            history_df = pd.DataFrame(st.session_state.search_history)
            st.dataframe(history_df)


def show_results_tab():
    st.markdown("### 📋 Search Results")
    
    if not st.session_state.concerts:
        st.info("🔍 No records found. Please search first.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Event Count</div>
            <div class="stat-number">{len(st.session_state.concerts)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cities = set(c.get('city', '') for c in st.session_state.concerts if c.get('city'))
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Venues</div>
            <div class="stat-number">{len(cities)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        available = sum(1 for c in st.session_state.concerts if 'Available for sale' in str(c.get('status', '')))
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Ticket sales</div>
            <div class="stat-number">{available}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_price = 0
        try:
            import re
            prices = []
            for c in st.session_state.concerts:
                price_str = str(c.get('price', ''))
                numbers = re.findall(r'\d+', price_str)
                if numbers:
                    prices.append(float(numbers[0]))
            if prices:
                avg_price = sum(prices) / len(prices)
        except:
            pass
        
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Average Fare</div>
            <div class="stat-number">¥{avg_price:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    view_mode = st.radio(
        "Mode",
        ["Card View", "Table View", "Data Analytics"],
        horizontal=True
    )
    
    if view_mode == "Card View":
        show_card_view()
    elif view_mode == "Table View":
        show_table_view()
    else:
        show_analytics_view()


def show_card_view():
    for i, concert in enumerate(st.session_state.concerts):
        with st.container():
            cols = st.columns([1, 1, 1, 1])
            
            with cols[0]:
                if concert.get('image'):
                    try:
                        st.image(concert['image'])
                    except:
                        st.image("https://via.placeholder.com/200x300?text=No+Image")
                else:
                    st.image("https://via.placeholder.com/200x300?text=No+Image")

            with cols[1]:
                st.markdown(f"**{concert.get('title', 'unknown')}**")
                st.markdown(f"🎤 {concert.get('artist', 'unknown')}")
                st.markdown(f"📍 {concert.get('venue', 'unknown')}")
            
            with cols[2]:
                st.markdown(f"🏙️ {concert.get('city', 'unknown')}")
                st.markdown(f"📅 {concert.get('date', 'unknown')}")
                st.markdown(f"💰 {concert.get('price', 'unknown')}")
            
            with cols[3]:
                st.markdown(f"🎫 {concert.get('status', 'unknown')}")
                if concert.get('link'):
                    st.markdown(f"[🔗 View Details]({concert['link']})")
                if st.button("🎯 Ticket Grab", key=f"grab_{concert.get('id', i)}"):
                    st.session_state.current_concert = concert
                    st.session_state.show_grab_dialog = True
                    st.experimental_rerun()

        if (st.session_state.show_grab_dialog and 
            st.session_state.current_concert and 
            st.session_state.current_concert.get('id') == concert.get('id')):
            show_grab_ticket_dialog_inline(concert)
        
        st.markdown("---")


def show_grab_ticket_dialog_inline(concert):

    st.markdown('<div class="grab-panel">', unsafe_allow_html=True)
    st.markdown("## 🎯 Ticket-Snatching Configuration")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {concert.get('title', 'unknown')}")
        st.markdown(f"**artist**: {concert.get('artist', 'unknown')}")
        st.markdown(f"**venue**: {concert.get('venue', 'unknown')}")
        st.markdown(f"**date**: {concert.get('date', 'unknown')}")
        st.markdown(f"**price**: {concert.get('price', 'unknown')}")
    
    with col2:
        if concert.get('image'):
            try:
                st.image(concert['image'], width=150)
            except:
                pass
    
    st.markdown("### ⚙️ Ticket Purchase Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        session_index = st.number_input(
            "Select a session",
            min_value=0,
            max_value=10,
            value=st.session_state.grab_session_index,
            step=1,
            help="0 indicates the first, 1 indicates the second....",
            key=f"session_{concert.get('id')}"
        )
        st.session_state.grab_session_index = session_index
    
    with col2:
        ticket_index = st.number_input(
            "Select Ticket Category",
            min_value=0,
            max_value=10,
            value=st.session_state.grab_ticket_index,
            step=1,
            help="0 means the first category",
            key=f"ticket_{concert.get('id')}"
        )
        st.session_state.grab_ticket_index = ticket_index
    
    with col3:
        ticket_count = st.number_input(
            "Quantity to Purchase",
            min_value=1,
            max_value=6,
            value=st.session_state.grab_ticket_count,
            step=1,
            help="less than 6 tickets at a time",
            key=f"count_{concert.get('id')}"
        )
        st.session_state.grab_ticket_count = ticket_count
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start", key=f"start_{concert.get('id')}"):
            start_grab_ticket(
                concert, 
                st.session_state.grab_session_index, 
                st.session_state.grab_ticket_index, 
                st.session_state.grab_ticket_count
            )
    
    with col2:
        if st.button("❌ Cancel", key=f"cancel_{concert.get('id')}"):
            st.session_state.show_grab_dialog = False
            st.session_state.current_concert = None
            st.session_state.grab_session_index = 0
            st.session_state.grab_ticket_index = 0
            st.session_state.grab_ticket_count = 1
            st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_table_view():
    df = pd.DataFrame(st.session_state.concerts)
    
    display_columns = ['title', 'artist', 'venue', 'city', 'date', 'price', 'status']
    available_columns = [col for col in display_columns if col in df.columns]
    
    if available_columns:
        st.dataframe(
            df[available_columns],
            height=600,
        )

        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 Export CSV",
                csv,
                "concerts.csv",
                "text/csv",
            )
        
        with col2:
            json_str = df.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                "📥 Export JSON",
                json_str,
                "concerts.json",
                "application/json",
            )


def show_analytics_view():
    st.markdown("### 📊 Data Analysis")
    
    df = pd.DataFrame(st.session_state.concerts)
    
    if 'city' in df.columns:
        st.markdown("#### City Distribution")
        city_counts = df['city'].value_counts().head(10)
        
        fig = px.bar(
            x=city_counts.index,
            y=city_counts.values,
            labels={'x': 'City', 'y': 'Events Count'},
            title='TOP 10 city with most events',
            color=city_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'price' in df.columns:
            st.markdown("#### Ticket Price Distribution")
            import re
            prices = []
            for price in df['price']:
                try:
                    price_str = str(price)
                    numbers = re.findall(r'\d+', price_str)
                    if numbers:
                        prices.append(float(numbers[0]))
                except:
                    continue
            
            if prices:
                fig = go.Figure(data=[go.Histogram(x=prices, nbinsx=20)])
                fig.update_layout(
                    title='Ticket Price Distribution',
                    xaxis_title='Price (¥)',
                    yaxis_title='Count',
                )
                st.plotly_chart(fig)
    
    with col2:
        if 'status' in df.columns:
            st.markdown("#### Ticket Sales Status")
            status_counts = df['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Ticket Status Distribution',
            )
            st.plotly_chart(fig)


def start_grab_ticket(concert, session_idx, ticket_idx, count):
    import threading
    from scraper.ticket_grabber import TicketGrabber
    
    concert_url = concert.get('link')
    
    ticket_config = {
        'session': session_idx,
        'ticket_type': ticket_idx,
        'ticket_count': count
    }

    def grab_thread():
        grabber = TicketGrabber()
        grabber.start_browser(headless=False)
        
        success = grabber.grab_ticket(concert_url, ticket_config)
        
        if success:
            log.success("Successfully grabbed the ticket, please proceed to payment")
        else:
            log.error("Failed to grab the ticket")
        
        import time
        time.sleep(300)
        grabber.close()
            
    
    thread = threading.Thread(target=grab_thread, daemon=True)
    thread.start()
    
    st.session_state.show_grab_dialog = False
    st.session_state.current_concert = None
    st.success("Ticket grabbing started in background")
        


def show_database_tab():
    st.markdown("### 💾 Database Management")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        db_keyword = st.text_input("Search the database", placeholder="Enter keywords to search saved data")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_db_btn = st.button("🔍 Search")
    
    if search_db_btn and db_keyword:
        concerts = db.search_concerts(db_keyword, limit=100)
        if concerts:
            st.success(f"Find {len(concerts)} records")
            df = pd.DataFrame(concerts)
            st.dataframe(df)
        else:
            st.warning("Failed to find any records")
    
    st.markdown("---")
    
    if st.button("📋 Show the latest records"):
        concerts = db.get_all_concerts(limit=1000)
        if concerts:
            df = pd.DataFrame(concerts)
            display_cols = ['id', 'title', 'artist', 'city', 'venue', 'date', 'price', 'status']
            available_cols = [c for c in display_cols if c in df.columns]
            if available_cols:
                st.dataframe(df[available_cols])
            else:
                st.dataframe(df)
        else:
            st.info("Empty database")


def main():
    init_session_state()
    show_header()

    config = show_sidebar()

    tab1, tab2, tab3 = st.tabs(["🔍 Scraper", "📋 Results", "💾 Database"])
    
    with tab1:
        show_search_tab(config)
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_database_tab()


if __name__ == "__main__":
    main()