import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="☕ Coffee Sales Dashboard",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Coffee Sales Dashboard")
st.caption("Interactive dashboard based on coffee transaction data (EDA subset + interactivity).")

# -----------------------------
# Color Map (고정 매핑)
# -----------------------------
coffee_color_map = {
    'Latte': '#C2A878',
    'Hot Chocolate': '#3B2416',
    'Americano': '#6F4E37',
    'Americano with Milk': '#8B5A2B',
    'Cocoa': '#9C6B4F',
    'Cortado': '#D2B48C',
    'Espresso': '#4B2E1E',
    'Cappuccino': '#A47148'
}

coffee_palette_fallback = ['#6F4E37', '#8B5A2B', '#C2A878', '#A47148', '#4B2E1E', '#D2B48C', '#9C6B4F', '#3B2416']

weekday_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
season_order = ['Spring','Summer','Fall','Winter']

# -----------------------------
# Helpers
# -----------------------------
def month_to_season(month: int) -> str:
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'
    else:
        return 'Winter'

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Date 처리
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # Weekday 만들기 (혹시 이미 있어도 덮어씀)
    df['Weekday'] = df['Date'].dt.day_name()
    # Season 만들기 (Monthsort가 있는 데이터셋 기준)
    if 'Season' not in df.columns:
        df['Season'] = df['Monthsort'].apply(month_to_season)

    # 문자열 정리(안전하게)
    df['coffee_name'] = df['coffee_name'].astype(str).str.strip()
    if 'cash_type' in df.columns:
        df['cash_type'] = df['cash_type'].astype(str).str.strip()

    return df

def metric_label(metric: str) -> str:
    return "Revenue" if metric == "Revenue" else "Sales Volume"

def agg_value(df: pd.DataFrame, metric: str) -> pd.Series:
    # metric: "Revenue" or "Sales Volume"
    if metric == "Revenue":
        return df['money']
    return pd.Series(1, index=df.index)

def safe_color_list(names):
    # coffee_color_map에 없는 이름이 나와도 fallback으로 색 부여
    colors = []
    for i, n in enumerate(names):
        colors.append(coffee_color_map.get(n, coffee_palette_fallback[i % len(coffee_palette_fallback)]))
    return colors

def donut_by_two_seasons(df: pd.DataFrame, season_a: str, season_b: str, metric: str, title: str):
    # season별 coffee 분포 도넛 2개
    if metric == "Revenue":
        tmp = df.groupby(['Season','coffee_name'], as_index=False)['money'].sum()
        value_col = 'money'
    else:
        tmp = df.groupby(['Season','coffee_name']).size().reset_index(name='sales_count')
        value_col = 'sales_count'

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type':'domain'}, {'type':'domain'}]],
        subplot_titles=[season_a, season_b]
    )

    for i, s in enumerate([season_a, season_b], start=1):
        d = tmp[tmp['Season'] == s].sort_values(value_col, ascending=False)
        fig.add_trace(
            go.Pie(
                labels=d['coffee_name'],
                values=d[value_col],
                hole=0.4,
                sort=False,
                marker=dict(
                    colors=safe_color_list(d['coffee_name']),
                    line=dict(color='white', width=1)
                ),
                textinfo='percent+label',
                textposition='inside'
            ),
            row=1, col=i
        )

    fig.update_layout(
        title=title,
        template='plotly_white',
        showlegend=False,
        margin=dict(t=70, l=10, r=10, b=10)
    )
    return fig

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Controls")

data_path = st.sidebar.text_input("CSV path", value="Coffe_sales.csv")
coffee = load_data(data_path)

metric_toggle = st.sidebar.radio(
    "Metric (매출/판매량)",
    options=["Revenue", "Sales Volume"],
    index=0,
    horizontal=True
)

selected_coffee = st.sidebar.selectbox(
    "Select coffee (Q9 / Q10용)",
    options=sorted(coffee['coffee_name'].unique())
)

scope_q10 = st.sidebar.radio(
    "Q10 Scope (전체/커피별)",
    options=["All coffees", "Selected coffee only"],
    index=0
)

# -----------------------------
# Q1 / Q2: Monthly Trend (Revenue or Volume)
# -----------------------------
st.subheader("Q1–Q2. Monthly trend (Revenue vs Sales Volume)")

# 월별 집계
if metric_toggle == "Revenue":
    monthly = coffee.groupby(['Month_name','Monthsort'], as_index=False)['money'].sum()
    ycol = 'money'
else:
    monthly = coffee.groupby(['Month_name','Monthsort']).size().reset_index(name='sales_count')
    ycol = 'sales_count'

monthly = monthly.sort_values('Monthsort')

max_row = monthly.loc[monthly[ycol].idxmax()]
max_month = max_row['Month_name']

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        monthly,
        x='Month_name',
        y=ycol,
        template='plotly_white',
        title=f"Monthly note: {metric_label(metric_toggle)} by Month",
        category_orders={'Month_name': monthly['Month_name'].tolist()}
    )
    fig.update_traces(marker_color='#6F4E37', marker_line_color='white', marker_line_width=1)
    fig.update_layout(xaxis_title="Month", yaxis_title=metric_label(metric_toggle))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"**Highest month:** `{max_month}`")
    # 최고 월에서 커피별 기여(도넛)
    df_max = coffee[coffee['Month_name'] == max_month].copy()

    if metric_toggle == "Revenue":
        share = df_max.groupby('coffee_name', as_index=False)['money'].sum()
        v = 'money'
    else:
        share = df_max.groupby('coffee_name').size().reset_index(name='sales_count')
        v = 'sales_count'

    share = share.sort_values(v, ascending=False)
    fig2 = px.pie(
        share,
        names='coffee_name',
        values=v,
        hole=0.45,
        template='plotly_white',
        title=f"{metric_label(metric_toggle)} share by coffee ({max_month})",
        color='coffee_name',
        color_discrete_map=coffee_color_map
    )
    fig2.update_traces(textinfo='percent+label', marker=dict(line=dict(color='white', width=1)))
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Q3: Best-selling coffee
# -----------------------------
st.subheader("Q3. Best-selling coffee (overall)")
vol_by_menu = coffee.groupby('coffee_name').size().reset_index(name='sales_count').sort_values('sales_count', ascending=False)

fig = px.bar(
    vol_by_menu,
    x='sales_count',
    y='coffee_name',
    orientation='h',
    template='plotly_white',
    title="Sales Volume by Coffee Menu",
)
fig.update_traces(marker_color='#4B2E1E')
fig.update_layout(xaxis_title="Sales Volume", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q4: Price distribution by menu
# -----------------------------
st.subheader("Q4. Price distribution by menu")
fig = px.box(
    coffee,
    x='coffee_name',
    y='money',
    template='plotly_white',
    title="Price Distribution by Coffee Menu",
    color='coffee_name',
    color_discrete_map=coffee_color_map
)
fig.update_layout(xaxis_title="", yaxis_title="Price (money)")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q5: Seasonal variation (Revenue/Volume toggle)
# -----------------------------
st.subheader("Q5. How do coffee sales vary by season?")

if metric_toggle == "Revenue":
    season_sum = coffee.groupby('Season', as_index=False)['money'].sum()
    ycol = 'money'
else:
    season_sum = coffee.groupby('Season').size().reset_index(name='sales_count')
    ycol = 'sales_count'

season_sum['Season'] = pd.Categorical(season_sum['Season'], categories=season_order, ordered=True)
season_sum = season_sum.sort_values('Season')

fig = px.bar(
    season_sum,
    x='Season',
    y=ycol,
    template='plotly_white',
    title=f"{metric_label(metric_toggle)} by Season",
    category_orders={'Season': season_order}
)
fig.update_traces(marker_color='#6F4E37', marker_line_color='white', marker_line_width=1)
fig.update_layout(xaxis_title="", yaxis_title=metric_label(metric_toggle))
st.plotly_chart(fig, use_container_width=True)

# (시즌 도넛: 2개씩)
st.markdown("**Seasonal donut comparison (2 panels)**")
c1, c2 = st.columns(2)
with c1:
    fig = donut_by_two_seasons(coffee, 'Spring', 'Summer', metric_toggle,
                               f"{metric_label(metric_toggle)} Share by Coffee (Spring vs Summer)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = donut_by_two_seasons(coffee, 'Fall', 'Winter', metric_toggle,
                               f"{metric_label(metric_toggle)} Share by Coffee (Fall vs Winter)")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q6: Which weekday has highest sales? (average per day)
# -----------------------------
st.subheader("Q6. Which weekday has the highest sales volume? (Average per day)")

daily_sales = (
    coffee
    .groupby([coffee['Date'].dt.date, 'Weekday'])
    .size()
    .reset_index(name='daily_sales')
)

weekday_avg = daily_sales.groupby('Weekday', as_index=False)['daily_sales'].mean()
max_v = weekday_avg['daily_sales'].max()
weekday_avg['color'] = weekday_avg['daily_sales'].apply(lambda x: '#4B2E1E' if x == max_v else '#C2A878')

fig = px.bar(
    weekday_avg,
    x='Weekday',
    y='daily_sales',
    template='plotly_white',
    title="Average Daily Sales Volume by Weekday",
    color='color',
    color_discrete_map='identity',
    category_orders={'Weekday': weekday_order}
)
fig.update_layout(xaxis_title="Weekday", yaxis_title="Average Sales per Day")
st.plotly_chart(fig, use_container_width=True)

coffee_gradient = [
    '#F5EFE6',  # very light latte
    '#E6D3B1',
    '#D2B48C',
    '#B08968',
    '#8B5A2B',
    '#6F4E37',
    '#4B2E1E'   # dark roast
]

# -----------------------------
# Q7: Weekday x Season (Revenue/Volume toggle)
# -----------------------------
st.subheader("Q7. Sales/Revenue by Weekday × Season")

if metric_toggle == "Revenue":
    pivot = pd.pivot_table(
        coffee,
        values='money',
        index='Season',
        columns='Weekday',
        aggfunc='sum'
    )
else:
    pivot = pd.pivot_table(
        coffee,
        values='coffee_name',
        index='Season',
        columns='Weekday',
        aggfunc='count'
    )

pivot = pivot.reindex(season_order)
pivot = pivot[weekday_order]

fig = px.imshow(
    pivot,
    text_auto=True,
    aspect="auto",
    template="plotly_white",
    title=f"{metric_label(metric_toggle)} Heatmap (Season × Weekday)",
    color_continuous_scale=coffee_gradient
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q8: Product Positioning (Volume vs Revenue)
# -----------------------------
st.subheader("Q8. Product Positioning: Sales Volume vs Revenue by Menu")

menu_pos = coffee.groupby('coffee_name', as_index=False).agg(
    sales_count=('coffee_name','count'),
    revenue=('money','sum')
)

fig = px.scatter(
    menu_pos,
    x='sales_count',
    y='revenue',
    text='coffee_name',
    template='plotly_white',
    title="Product Positioning (Sales Volume vs Revenue)",
    color='coffee_name',
    color_discrete_map=coffee_color_map
)
fig.update_traces(textposition='top center')
fig.update_layout(xaxis_title="Sales Volume", yaxis_title="Revenue")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q9: Does each coffee sell better on specific weekdays?
# -----------------------------
st.subheader("Q9. Coffee preference by weekday (Select coffee)")

df_c = coffee[coffee['coffee_name'] == selected_coffee].copy()
counts = df_c.groupby('Weekday').size().reset_index(name='sales_count')

fig = px.bar(
    counts,
    x='Weekday',
    y='sales_count',
    template='plotly_white',
    title=f"Sales Volume by Weekday — {selected_coffee}",
    category_orders={'Weekday': weekday_order}
)
fig.update_traces(marker_color=coffee_color_map.get(selected_coffee, '#6F4E37'),
                  marker_line_color='white', marker_line_width=1)
fig.update_layout(xaxis_title="Weekday", yaxis_title="Sales Volume")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Q10: Weekday vs Weekend (All vs Selected coffee) + metric toggle
# -----------------------------
st.subheader("Q10. Weekday vs Weekend comparison (All vs Selected coffee)")

df_scope = coffee.copy()
if scope_q10 == "Selected coffee only":
    df_scope = df_scope[df_scope['coffee_name'] == selected_coffee]

df_scope['Day_Type'] = df_scope['Weekday'].isin(['Saturday','Sunday']).map({True:'Weekend', False:'Weekday'})

# 하루 단위로 먼저 합치고 평균
if metric_toggle == "Revenue":
    daily = df_scope.groupby([df_scope['Date'].dt.date, 'Day_Type'])['money'].sum().reset_index(name='daily_value')
else:
    daily = df_scope.groupby([df_scope['Date'].dt.date, 'Day_Type']).size().reset_index(name='daily_value')

avg = daily.groupby('Day_Type', as_index=False)['daily_value'].mean()

fig = px.bar(
    avg,
    x='daily_value',
    y='Day_Type',
    orientation='h',
    template='plotly_white',
    title=f"Average Daily {metric_label(metric_toggle)} — {scope_q10}",
    color='Day_Type',
    color_discrete_map={'Weekday':'#C2A878', 'Weekend':'#4B2E1E'}
)
fig.update_layout(xaxis_title=f"Average Daily {metric_label(metric_toggle)}", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)
