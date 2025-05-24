import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.title("🏘️부동산 분석 플랫폼")

# 데이터 불러오기
data_df = pd.read_csv("C:/Users/82102/OneDrive/바탕 화면/programing files/project file/data/아파트_매매지수_정제완료.csv")
with open("C:/Users/82102/OneDrive/바탕 화면/programing files/project file/data/시군구_세부수정.geojson", encoding='utf-8') as f:
    map_data = json.load(f)

# 날짜 정리
data_df['날짜'] = pd.to_datetime(data_df['날짜'])
data_df['날짜'] = data_df['날짜'].dt.normalize()
data_df['매매지수'] = pd.to_numeric(data_df['매매지수'], errors='coerce')

# 메뉴 선택
menu_sel = st.sidebar.selectbox("메뉴 선택", ["📈증감률 지도", "예측 (준비중)"])

if menu_sel == "📈증감률 지도":
    st.subheader("📈증감률 지도 보기")

    date_start = st.sidebar.date_input("시작일", datetime(2024, 5, 13))
    date_end = st.sidebar.date_input("종료일", datetime(2025, 5, 12))

    date_list = data_df['날짜'].sort_values().unique()
    picked_start = date_list[0]
    picked_end = date_list[-1]
    min_gap_s = abs(picked_start - pd.to_datetime(date_start))
    min_gap_e = abs(picked_end - pd.to_datetime(date_end))

    for d in date_list:
        if abs(d - pd.to_datetime(date_start)) < min_gap_s:
            picked_start = d
            min_gap_s = abs(d - pd.to_datetime(date_start))
        if abs(d - pd.to_datetime(date_end)) < min_gap_e:
            picked_end = d
            min_gap_e = abs(d - pd.to_datetime(date_end))

    st.write("실제 선택된 날짜:", picked_start.date(), "~", picked_end.date())

    start_df = data_df[data_df['날짜'] == picked_start]
    end_df = data_df[data_df['날짜'] == picked_end]

    change_list = []
    for loc in start_df['지역명'].unique():
        region_row_s = start_df[start_df['지역명'] == loc]
        region_row_e = end_df[end_df['지역명'] == loc]
        if not region_row_s.empty and not region_row_e.empty:
            old_price = region_row_s.iloc[0]['매매지수']
            new_price = region_row_e.iloc[0]['매매지수']
            if pd.notna(old_price) and pd.notna(new_price) and old_price != 0:
                rate = ((new_price - old_price) / old_price) * 100
                change_list.append({'지역': loc, '증감률': rate})

    change_df = pd.DataFrame(change_list)

    folium_map = folium.Map(location=[36.5, 127.8], zoom_start=7)
    folium.Choropleth(
        geo_data=map_data,
        data=change_df,
        columns=['지역', '증감률'],
        key_on='feature.properties.SIG_KOR_NM',
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name='증감률 (%)',
        nan_fill_color='lightgray'
    ).add_to(folium_map)

    st.subheader("🗺️ 지도")
    st_folium(folium_map, width=1000, height=700)

    st.subheader("📊 데이터")
    st.dataframe(change_df.sort_values(by='증감률', ascending=False))

elif menu_sel == "예측 (준비중)":
    st.subheader("매매가 예측")
    st.write("아직 구현되지 않았습니다. 추후 업데이트 예정입니다.")
