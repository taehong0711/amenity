import sqlite3
from datetime import date, timedelta, datetime
import calendar
import pandas as pd
import streamlit as st
import altair as alt

DB_PATH = "inventory.db"

# ==========================================
# 일본 공휴일 데이터 (2025-2026 하드코딩)
# ==========================================
JAPAN_HOLIDAYS = {
    # 2025
    "2025-01-01": "元日", "2025-01-13": "成人の日", "2025-02-11": "建国記念の日",
    "2025-02-23": "天皇誕生日", "2025-02-24": "振替休日", "2025-03-20": "春分の日",
    "2025-04-29": "昭和の日", "2025-05-03": "憲法記念日", "2025-05-04": "みどりの日",
    "2025-05-05": "こどもの日", "2025-05-06": "振替休日", "2025-07-21": "海の日",
    "2025-08-11": "山の日", "2025-09-15": "敬老の日", "2025-09-23": "秋分の日",
    "2025-10-13": "スポーツの日", "2025-11-03": "文化の日", "2025-11-23": "勤労感謝の日",
    "2025-11-24": "振替休日",
    # 2026
    "2026-01-01": "元日", "2026-01-12": "成人の日", "2026-02-11": "建国記念の日",
    "2026-02-23": "天皇誕生日", "2026-03-20": "春分の日", "2026-04-29": "昭和の日",
    "2026-05-03": "憲法記念日", "2026-05-04": "みどりの日", "2026-05-05": "こどもの日",
    "2026-05-06": "振替休日", "2026-07-20": "海の日", "2026-08-11": "山の日",
    "2026-09-21": "敬老の日", "2026-09-22": "国民の休日", "2026-09-23": "秋分の日",
    "2026-10-12": "スポーツの日", "2026-11-03": "文化の日", "2026-11-23": "勤労感謝の日",
}

# ==========================================
# 다국어 텍스트
# ==========================================
TEXTS = {
    "jp": {
        "title": "ホテル在庫予測システム",
        "lang": "Language / 言語 / 언어",
        "menu_title": "メニュー",
        "menu_home": "🏠 ホーム・サマリー",
        "menu_items": "📦 1. 品目マスター",
        "menu_stock": "📝 2. 在庫記録",
        "menu_forecast": "📊 3. 予測＆発注",
        "menu_toothbrush": "🪥 4. 歯ブラシ予測",
        "menu_calendar": "📅 5. 発注カレンダー",
        "dashboard_alert": "発注推奨品目数",
        "dashboard_incoming": "入荷待ち件数",
        "dashboard_total_items": "登録品目数",
        "download_excel": "予測結果をExcelでダウンロード",
        "stock_level_chart": "在庫推移予測チャート",
        "items_header": "品目マスター管理",
        "items_new": "新規登録",
        "items_list": "登録済み一覧",
        "item_name": "品目名",
        "unit": "単位",
        "safety": "安全在庫",
        "cs_total": "1CS入数",
        "units_per_box": "1箱入数",
        "boxes_per_cs": "1CS箱数",
        "btn_register": "登録",
        "btn_update": "更新",
        "items_edit": "編集・削除",
        "select_item_edit": "品目選択",
        "err_itemname": "品目名は必須です。",
        "success_register": "登録しました。",
        "success_update": "更新しました。",
        "stock_header": "在庫記録管理",
        "stock_tab_input": "新規入力",
        "stock_tab_history": "履歴確認・削除",
        "stock_select_item": "品目選択",
        "stock_date": "日付",
        "stock_cs": "CS",
        "stock_box": "箱/袋",
        "stock_note": "備考",
        "btn_save_stock": "保存",
        "err_conv": "換算設定エラー。マスターを確認してください。",
        "success_save_stock": "保存しました。",
        "recent_stock": "最新在庫状況",
        "history_list": "最近の入力履歴（削除可能）",
        "btn_delete": "選択した記録を削除",
        "select_delete": "削除する記録を選択 (ID: 日付 - 品目)",
        "success_delete": "記録を削除しました。",
        "warn_no_data": "データがありません。",
        "forecast_header": "在庫予測・発注",
        "days_label": "過去平均算出期間(日)",
        "horizon_label": "予測期間(日)",
        "forecast_result": "発注推奨リスト",
        "info_forecast": "赤色は在庫不足の可能性がある品目です。",
        "tab_list_view": "📋 リスト表示",
        "tab_chart_view": "📈 チャート表示",
        "tb_header": "歯ブラシ特化予測",
        "warn_tb_items": "品目名に「ナチュラル」「グリーン」「アッシュグレー」を含む品目が必要です。",
        "rooms": "客室数",
        "occ": "稼働率(%)",
        "tb_horizon": "予測期間",
        "tb_result": "色別必要数シミュレーション",
        "tb_info": "2.5名/室 想定",
        "cal_header": "入荷予定カレンダー",
        "cal_tab_new": "予定登録",
        "cal_tab_list": "カレンダー・検索・削除",
        "cal_item": "品目",
        "cal_order_date": "発注日",
        "cal_arrival_date": "入荷予定日",
        "cal_cs": "CS",
        "cal_box": "箱/袋",
        "cal_note": "備考",
        "btn_save_cal": "登録",
        "success_save_cal": "登録しました。",
        "cal_list": "入荷予定一覧",
        "cal_search_item": "品目検索",
        "weekdays": ["月", "火", "水", "木", "金", "土", "日"],
        "prev_month": "◀ 前月",
        "next_month": "翌月 ▶",
        "today": "今日",
    },
    "en": {
        "title": "Hotel Inventory Forecast",
        "lang": "Language",
        "menu_title": "Menu",
        "menu_home": "🏠 Home & Summary",
        "menu_items": "📦 1. Item Master",
        "menu_stock": "📝 2. Stock Input",
        "menu_forecast": "📊 3. Forecast & Order",
        "menu_toothbrush": "🪥 4. Toothbrush Sim",
        "menu_calendar": "📅 5. Calendar",
        "dashboard_alert": "Items to Order",
        "dashboard_incoming": "Pending Deliveries",
        "dashboard_total_items": "Total Items",
        "download_excel": "Download Forecast",
        "stock_level_chart": "Projected Stock Chart",
        "items_header": "Item Management",
        "items_new": "New Item",
        "items_list": "Item List",
        "item_name": "Name",
        "unit": "Unit",
        "safety": "Safety Stock",
        "cs_total": "Units/CS",
        "units_per_box": "Units/Box",
        "boxes_per_cs": "Box/CS",
        "btn_register": "Register",
        "btn_update": "Update",
        "items_edit": "Edit / Delete",
        "select_item_edit": "Select Item",
        "err_itemname": "Name required.",
        "success_register": "Saved.",
        "success_update": "Updated.",
        "stock_header": "Stock Management",
        "stock_tab_input": "New Input",
        "stock_tab_history": "History & Delete",
        "stock_select_item": "Select Item",
        "stock_date": "Date",
        "stock_cs": "CS",
        "stock_box": "Box",
        "stock_note": "Note",
        "btn_save_stock": "Save",
        "err_conv": "Conversion error. Check master.",
        "success_save_stock": "Saved.",
        "recent_stock": "Latest Status",
        "history_list": "Recent Input History",
        "btn_delete": "Delete Selected Record",
        "select_delete": "Select record to delete",
        "success_delete": "Record deleted.",
        "warn_no_data": "No Data.",
        "forecast_header": "Forecast & Order",
        "days_label": "Avg Calc Days",
        "horizon_label": "Forecast Days",
        "forecast_result": "Order Recommendation",
        "info_forecast": "Red items are below required levels.",
        "tab_list_view": "📋 List View",
        "tab_chart_view": "📈 Chart View",
        "tb_header": "Toothbrush Simulator",
        "warn_tb_items": "Need items with 'Natural', 'Green', 'Ash Grey'.",
        "rooms": "Rooms",
        "occ": "Occupancy(%)",
        "tb_horizon": "Days",
        "tb_result": "Simulation",
        "tb_info": "Assumed 2.5 pax/room.",
        "cal_header": "Order Calendar",
        "cal_tab_new": "New Schedule",
        "cal_tab_list": "Calendar / Search / Delete",
        "cal_item": "Item",
        "cal_order_date": "Order Date",
        "cal_arrival_date": "Arrival Date",
        "cal_cs": "CS",
        "cal_box": "Box",
        "cal_note": "Note",
        "btn_save_cal": "Save",
        "success_save_cal": "Saved.",
        "cal_list": "Schedule List",
        "cal_search_item": "Search Item",
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "prev_month": "◀ Prev",
        "next_month": "Next ▶",
        "today": "Today",
    },
    "ko": {
        "title": "호텔 재고 예측 시스템",
        "lang": "Language / 言語 / 언어",
        "menu_title": "메뉴",
        "menu_home": "🏠 홈 & 요약",
        "menu_items": "📦 1. 품목 마스터",
        "menu_stock": "📝 2. 재고 입력",
        "menu_forecast": "📊 3. 예측 & 발주",
        "menu_toothbrush": "🪥 4. 칫솔 시뮬레이션",
        "menu_calendar": "📅 5. 발주 캘린더",
        "dashboard_alert": "발주 필요 품목",
        "dashboard_incoming": "입고 예정 건수",
        "dashboard_total_items": "등록 품목 수",
        "download_excel": "예측 결과 엑셀 다운로드",
        "stock_level_chart": "재고 소진 예측 차트",
        "items_header": "품목 관리",
        "items_new": "새 품목 등록",
        "items_list": "품목 목록",
        "item_name": "품목명",
        "unit": "단위",
        "safety": "안전 재고",
        "cs_total": "1CS 총개수",
        "units_per_box": "1박스 개수",
        "boxes_per_cs": "1CS 박스수",
        "btn_register": "등록",
        "btn_update": "수정 저장",
        "items_edit": "수정 및 삭제",
        "select_item_edit": "수정할 품목",
        "err_itemname": "품목명은 필수입니다.",
        "success_register": "저장되었습니다.",
        "success_update": "수정되었습니다.",
        "stock_header": "실재고(스냅샷) 관리",
        "stock_tab_input": "새 재고 입력",
        "stock_tab_history": "입력 기록 / 삭제",
        "stock_select_item": "품목 선택",
        "stock_date": "측정일",
        "stock_cs": "CS",
        "stock_box": "박스/봉투",
        "stock_note": "비고",
        "btn_save_stock": "저장",
        "err_conv": "환산 설정 오류. 마스터를 확인하세요.",
        "success_save_stock": "저장되었습니다.",
        "recent_stock": "최신 재고 현황",
        "history_list": "최근 입력 기록 (삭제 가능)",
        "btn_delete": "선택한 기록 삭제",
        "select_delete": "삭제할 기록 선택 (ID: 날짜 - 품목)",
        "success_delete": "기록을 삭제했습니다.",
        "warn_no_data": "데이터가 없습니다.",
        "forecast_header": "재고 예측 및 발주 권고",
        "days_label": "평균 사용량 산출 기간(일)",
        "horizon_label": "예측 기간(일)",
        "forecast_result": "발주 추천 리스트",
        "info_forecast": "붉은색 행은 재고 부족이 예상되는 품목입니다.",
        "tab_list_view": "📋 리스트 보기",
        "tab_chart_view": "📈 차트 보기",
        "tb_header": "칫솔 소진 시뮬레이션",
        "warn_tb_items": "마스터에 'ナチュラル', 'グリーン', 'アッシュグレー'가 포함된 품목이 필요합니다.",
        "rooms": "객실 수",
        "occ": "가동률(%)",
        "tb_horizon": "예측 기간",
        "tb_result": "색상별 소진 예측",
        "tb_info": "객실당 2.5명 기준 시뮬레이션입니다.",
        "cal_header": "발주/입고 캘린더",
        "cal_tab_new": "입고 예정 등록",
        "cal_tab_list": "달력 / 검색 / 삭제",
        "cal_item": "품목",
        "cal_order_date": "발주일",
        "cal_arrival_date": "도착 예정일",
        "cal_cs": "CS",
        "cal_box": "박스",
        "cal_note": "비고",
        "btn_save_cal": "등록",
        "success_save_cal": "저장되었습니다.",
        "cal_list": "입고 예정 목록",
        "cal_search_item": "품목 검색",
        "weekdays": ["월", "화", "수", "목", "금", "토", "일"],
        "prev_month": "◀ 이전 달",
        "next_month": "다음 달 ▶",
        "today": "오늘",
    },
}

def get_lang_code():
    return st.session_state.get("lang_code", "ko")

def t(key: str) -> str:
    lang = get_lang_code()
    return TEXTS.get(lang, TEXTS["ko"]).get(key, key)

# ==========================================
# DB 관련
# ==========================================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            unit TEXT,
            cs_total_units INTEGER,
            units_per_box INTEGER,
            boxes_per_cs INTEGER,
            safety_stock INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            snap_date TEXT NOT NULL,
            qty_cs INTEGER NOT NULL,
            qty_box INTEGER NOT NULL,
            total_units INTEGER NOT NULL,
            note TEXT,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            arrival_date TEXT NOT NULL,
            qty_cs INTEGER NOT NULL,
            qty_box INTEGER NOT NULL,
            total_units INTEGER NOT NULL,
            note TEXT,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    """)
    conn.commit()
    conn.close()

def add_item(name, unit, cs_total_units, units_per_box, boxes_per_cs, safety_stock):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO items
            (name, unit, cs_total_units, units_per_box, boxes_per_cs, safety_stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, unit, cs_total_units, units_per_box, boxes_per_cs, safety_stock))
        conn.commit()
    finally:
        conn.close()

def update_item(item_id, name, unit, cs_total_units, units_per_box, boxes_per_cs, safety_stock):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE items
            SET name = ?, unit = ?, cs_total_units = ?, units_per_box = ?, boxes_per_cs = ?, safety_stock = ?
            WHERE id = ?
        """, (name, unit, cs_total_units, units_per_box, boxes_per_cs, safety_stock, item_id))
        conn.commit()
    finally:
        conn.close()

def delete_item_if_unused(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stock_snapshots WHERE item_id = ?", (item_id,))
    snap_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM deliveries WHERE item_id = ?", (item_id,))
    deliv_count = cur.fetchone()[0]
    
    if snap_count == 0 and deliv_count == 0:
        cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True, snap_count, deliv_count
    else:
        conn.close()
        return False, snap_count, deliv_count

def get_items_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM items ORDER BY id", conn)
    conn.close()
    return df

def add_snapshot(item_id, snap_date, qty_cs, qty_box, total_units, note):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO stock_snapshots (item_id, snap_date, qty_cs, qty_box, total_units, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, snap_date, qty_cs, qty_box, total_units, note))
        conn.commit()
    finally:
        conn.close()

def delete_snapshot(snap_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM stock_snapshots WHERE id = ?", (snap_id,))
        conn.commit()
    finally:
        conn.close()

def add_delivery(item_id, order_date, arrival_date, qty_cs, qty_box, total_units, note):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO deliveries (item_id, order_date, arrival_date, qty_cs, qty_box, total_units, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item_id, order_date, arrival_date, qty_cs, qty_box, total_units, note))
        conn.commit()
    finally:
        conn.close()

def delete_delivery(delivery_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM deliveries WHERE id = ?", (delivery_id,))
        conn.commit()
    finally:
        conn.close()

def get_latest_stock_df():
    items = get_items_df()
    conn = get_connection()
    snaps = pd.read_sql_query("SELECT * FROM stock_snapshots", conn)
    conn.close()
    
    if snaps.empty:
        items["current_stock"] = 0
        items["last_snap_date"] = None
        return items
        
    snaps["snap_date"] = pd.to_datetime(snaps["snap_date"])
    snaps = snaps.sort_values(["item_id", "snap_date"])
    latest = snaps.groupby("item_id").tail(1)
    latest = latest.rename(columns={"total_units": "current_stock", "snap_date": "last_snap_date"})[["item_id", "current_stock", "last_snap_date"]]
    
    merged = items.merge(latest, left_on="id", right_on="item_id", how="left").drop(columns=["item_id"])
    merged["current_stock"] = merged["current_stock"].fillna(0)
    return merged

def get_recent_snapshots_per_item():
    latest_stock = get_latest_stock_df()
    return latest_stock[["id", "name", "current_stock", "last_snap_date"]]

def get_snapshot_history():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT s.id, s.snap_date, i.name, s.qty_cs, s.qty_box, s.total_units, s.note
        FROM stock_snapshots s
        JOIN items i ON s.item_id = i.id
        ORDER BY s.snap_date DESC, s.id DESC
        LIMIT 50
    """, conn)
    conn.close()
    return df

def get_usage_from_snapshots(days=60):
    conn = get_connection()
    snaps = pd.read_sql_query("SELECT * FROM stock_snapshots", conn)
    conn.close()
    if snaps.empty: return pd.DataFrame(columns=["id", "daily_avg_usage"])
    
    snaps["snap_date"] = pd.to_datetime(snaps["snap_date"])
    cutoff = pd.to_datetime(date.today() - timedelta(days=days))
    snaps = snaps[snaps["snap_date"] >= cutoff]
    
    records = []
    for item_id, group in snaps.groupby("item_id"):
        group = group.sort_values("snap_date").reset_index(drop=True)
        if len(group) < 2: continue
        
        daily_usages = []
        for i in range(1, len(group)):
            prev, curr = group.iloc[i-1], group.iloc[i]
            days_diff = (curr["snap_date"] - prev["snap_date"]).days
            if days_diff <= 0: continue
            usage = prev["total_units"] - curr["total_units"]
            if usage <= 0: continue
            daily_usages.append(usage / days_diff)
            
        if daily_usages:
            avg = sum(daily_usages) / len(daily_usages)
            records.append({"id": item_id, "daily_avg_usage": avg})
            
    if not records: return pd.DataFrame(columns=["id", "daily_avg_usage"])
    return pd.DataFrame(records)

def get_future_deliveries(horizon_days: int):
    conn = get_connection()
    today = date.today()
    end_date = today + timedelta(days=horizon_days)
    df = pd.read_sql_query("""
        SELECT item_id, SUM(total_units) AS incoming_units
        FROM deliveries
        WHERE DATE(arrival_date) > DATE(?) AND DATE(arrival_date) <= DATE(?)
        GROUP BY item_id
    """, conn, params=(today.isoformat(), end_date.isoformat()))
    conn.close()
    return df

def get_delivery_list():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT d.id, d.order_date, d.arrival_date, i.name AS item, d.qty_cs, d.qty_box, d.total_units, d.note
        FROM deliveries d JOIN items i ON d.item_id = i.id
        ORDER BY d.arrival_date, d.order_date
    """, conn)
    conn.close()
    return df

def seed_initial_items():
    initial = [
       ("歯ブラシ (ナチュラル)", "本", 1000, 250, 4, 1000),
       ("歯ブラシ (グリーン)", "本", 1000, 250, 4, 1000),
       ("歯ブラシ (アッシュグレー)", "本", 1000, 250, 4, 1000),
       ("ヘアブラシ", "本", 800, 200, 4, 400),
       ("レザークリーム", "個", 2500, 500, 5, 500),
       ("レザー_ドルコ_TG-711_白", "本", 1000, 125, 8, 200),
       ("コットン・綿棒", "個", 2000, 500, 4, 500),
       ("綿棒", "本", 10000, 0, 0, 1000),
       ("コスメセット(500枚)", "枚", 500, 50, 10, 100),
       ("緑茶", "個", 1000, 0, 0, 200),
       ("コーヒー", "個", 500, 0, 0, 100),
       ("シュガースリムスティック 3g", "本", 1800, 300, 6, 300),
       ("マドラー", "本", 16000, 1000, 16, 1000),
       ("水 (うきは)", "本", 24, 0, 0, 48),
       ("スリッパ (王子客室)", "足", 100, 0, 0, 20),
       ("ゴミ袋 (洗面)", "枚", 3000, 50, 60, 100),
       ("ゴミ袋 マチ付 (室内)", "枚", 1600, 20, 80, 100),
       ("ゴミ袋 (70L)", "枚", 400, 10, 40, 50),
       ("トイレットペーパー", "ロール", 60, 0, 0, 120),
       ("クッションブラシ", "本", 240, 60, 4, 30),
       ("シャンプー", "個", 200, 50, 4, 20),
       ("固形石鹸", "個", 500, 50, 10, 50),
       ("入浴剤", "個", 600, 30, 20, 60),
       ("コスメセット(60個)", "個", 60, 15, 4, 10),
    ]
    for name, unit, cs_total, upb, bcs, safety in initial:
        add_item(name, unit, cs_total, upb, bcs, safety)


# ==========================================
# 페이지: 홈 (대시보드)
# ==========================================
def page_home():
    st.header(t("menu_home"))
    
    stock_df = get_latest_stock_df()
    if stock_df.empty:
        st.info("No Data")
        return

    days, horizon = 60, 30
    usage_df = get_usage_from_snapshots(days=days)
    merged = stock_df.merge(usage_df, on="id", how="left")
    merged["daily_avg_usage"] = merged["daily_avg_usage"].fillna(0)
    merged["forecast_usage"] = merged["daily_avg_usage"] * horizon
    incoming_df = get_future_deliveries(horizon)
    merged = merged.merge(incoming_df, left_on="id", right_on="item_id", how="left")
    merged["incoming_units"] = merged["incoming_units"].fillna(0)
    
    merged["order_qty"] = (
        merged["forecast_usage"] + merged["safety_stock"]
        - merged["current_stock"] - merged["incoming_units"]
    ).apply(lambda x: x if x > 0 else 0)
    
    order_needed_count = len(merged[merged["order_qty"] > 0])
    incoming_count = len(get_delivery_list())
    total_items = len(merged)

    col1, col2, col3 = st.columns(3)
    col1.metric(t("dashboard_alert"), f"{order_needed_count}", delta_color="inverse")
    col2.metric(t("dashboard_incoming"), f"{incoming_count}")
    col3.metric(t("dashboard_total_items"), f"{total_items}")

    st.divider()

    if order_needed_count > 0:
        st.subheader("🚨 Urgent Orders")
        urgent_df = merged[merged["order_qty"] > 0][["name", "current_stock", "safety_stock", "order_qty", "unit"]]
        st.dataframe(
            urgent_df.style.background_gradient(cmap="Reds", subset=["order_qty"]),
            use_container_width=True
        )
    else:
        st.success("✅ All stocks are safe.")


# ==========================================
# 페이지: 품목 마스터
# ==========================================
def page_items():
    st.header(t("items_header"))

    tab1, tab2 = st.tabs([t("items_list"), t("items_new")])

    with tab1:
        items_df = get_items_df()
        st.dataframe(
            items_df,
            column_config={
                "safety_stock": st.column_config.NumberColumn("Safety", format="%d"),
            },
            use_container_width=True,
            height=400
        )
        
        st.divider()
        st.subheader(t("items_edit"))
        
        if not items_df.empty:
            item_list = [f"{row['name']} (ID:{row['id']})" for _, row in items_df.iterrows()]
            sel = st.selectbox(t("select_item_edit"), item_list)
            selected_id = int(sel.split("ID:")[1].replace(")", ""))
            row = items_df[items_df["id"] == selected_id].iloc[0]

            with st.expander(t("items_edit"), expanded=True):
                with st.form("item_form_edit"):
                    c1, c2 = st.columns(2)
                    with c1:
                        name_e = st.text_input(t("item_name"), value=row["name"])
                        unit_e = st.text_input(t("unit"), value=row["unit"] or "")
                        safety_e = st.number_input(t("safety"), min_value=0, value=int(row["safety_stock"] or 0))
                    with c2:
                        cs_total_e = st.number_input(t("cs_total"), min_value=0, value=int(row["cs_total_units"] or 0))
                        units_per_box_e = st.number_input(t("units_per_box"), min_value=0, value=int(row["units_per_box"] or 0))
                        boxes_per_cs_e = st.number_input(t("boxes_per_cs"), min_value=0, value=int(row["boxes_per_cs"] or 0))

                    if st.form_submit_button(t("btn_update"), use_container_width=True):
                        update_item(selected_id, name_e, unit_e, int(cs_total_e), int(units_per_box_e), int(boxes_per_cs_e), int(safety_e))
                        st.success(t("success_update"))
                        st.rerun()
                
                if st.button("Delete / 削除 / 삭제", type="secondary"):
                    ok, s_c, d_c = delete_item_if_unused(selected_id)
                    if ok:
                        st.success("Deleted.")
                        st.rerun()
                    else:
                        st.error(f"Cannot delete. Used in {s_c} snapshots, {d_c} deliveries.")

    with tab2:
        with st.form("item_form_new"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input(t("item_name"))
                unit = st.text_input(t("unit"), value="本")
                safety = st.number_input(t("safety"), min_value=0, step=1)
            with c2:
                cs_total = st.number_input(t("cs_total"), min_value=0)
                units_per_box = st.number_input(t("units_per_box"), min_value=0)
                boxes_per_cs = st.number_input(t("boxes_per_cs"), min_value=0)

            if st.form_submit_button(t("btn_register"), use_container_width=True):
                if not name:
                    st.error(t("err_itemname"))
                else:
                    add_item(name, unit, int(cs_total), int(units_per_box), int(boxes_per_cs), int(safety))
                    st.success(t("success_register"))
                    st.rerun()

# ==========================================
# 페이지: 재고 스냅샷
# ==========================================
def page_stock():
    st.header(t("stock_header"))
    
    tab_input, tab_history = st.tabs([t("stock_tab_input"), t("stock_tab_history")])
    
    items_df = get_items_df()
    if items_df.empty: return

    with tab_input:
        col_input, col_view = st.columns([1, 1.5])
        
        with col_input:
            st.subheader("📥 Input")
            item_map = {f"{row['name']}": row["id"] for _, row in items_df.iterrows()}
            label = st.selectbox(t("stock_select_item"), list(item_map.keys()))
            item_id = item_map[label]
            row = items_df[items_df["id"] == item_id].iloc[0]
            
            st.caption(f"Spec: 1CS={row['cs_total_units']}, 1Box={row['units_per_box']}")

            with st.form("stock_input_form"):
                snap_date = st.date_input(t("stock_date"), value=date.today())
                c1, c2 = st.columns(2)
                with c1: qty_cs = st.number_input(t("stock_cs"), min_value=0)
                with c2: qty_box = st.number_input(t("stock_box"), min_value=0)
                
                note = st.text_area(t("stock_note"), height=68)
                
                if st.form_submit_button(t("btn_save_stock"), use_container_width=True):
                    cs_t = int(row["cs_total_units"] or 0)
                    upb = int(row["units_per_box"] or 0)
                    if cs_t == 0 and upb == 0:
                        st.error(t("err_conv"))
                    else:
                        total = qty_cs * cs_t + qty_box * upb
                        add_snapshot(item_id, snap_date.isoformat(), int(qty_cs), int(qty_box), int(total), note)
                        st.success(t("success_save_stock"))
                        st.rerun()

        with col_view:
            st.subheader(t("recent_stock"))
            latest_df = get_recent_snapshots_per_item()
            st.dataframe(
                latest_df,
                column_config={
                    "last_snap_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "current_stock": st.column_config.NumberColumn("Stock", format="%d"),
                },
                use_container_width=True
            )

    with tab_history:
        st.subheader(t("history_list"))
        
        history_df = get_snapshot_history()
        if history_df.empty:
            st.info("No history found.")
        else:
            st.dataframe(
                history_df,
                column_config={
                    "snap_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "total_units": st.column_config.NumberColumn("Total Units"),
                },
                use_container_width=True
            )
            
            st.divider()
            st.subheader("🗑️ Delete Record")
            
            del_options = [
                f"ID {r['id']}: {r['snap_date']} - {r['name']} ({r['total_units']} units)" 
                for _, r in history_df.iterrows()
            ]
            
            sel_del = st.selectbox(t("select_delete"), del_options)
            
            if st.button(t("btn_delete"), type="primary"):
                if sel_del:
                    del_id = int(sel_del.split(":")[0].replace("ID", "").strip())
                    delete_snapshot(del_id)
                    st.success(t("success_delete"))
                    st.rerun()


# ==========================================
# 페이지: 재고 & 발주 예측
# ==========================================
def page_forecast_general():
    st.header(t("forecast_header"))

    with st.expander("⚙️ Settings / 설정", expanded=False):
        c1, c2 = st.columns(2)
        days = c1.slider(t("days_label"), 7, 120, 60)
        horizon = c2.slider(t("horizon_label"), 7, 120, 30)

    stock_df = get_latest_stock_df()
    if stock_df.empty: return

    usage_df = get_usage_from_snapshots(days=days)
    merged = stock_df.merge(usage_df, on="id", how="left")
    merged["daily_avg_usage"] = merged["daily_avg_usage"].fillna(0)
    merged["forecast_usage"] = merged["daily_avg_usage"] * horizon
    incoming_df = get_future_deliveries(horizon)
    merged = merged.merge(incoming_df, left_on="id", right_on="item_id", how="left")
    merged["incoming_units"] = merged["incoming_units"].fillna(0)
    
    merged["order_qty"] = (
        merged["forecast_usage"] + merged["safety_stock"]
        - merged["current_stock"] - merged["incoming_units"]
    ).apply(lambda x: int(x) if x > 0 else 0)
    
    merged["status"] = merged.apply(
        lambda x: "🚨 Order" if x["order_qty"] > 0 else "✅ OK", axis=1
    )

    st.subheader(t("forecast_result"))
    
    tab_list, tab_chart = st.tabs([t("tab_list_view"), t("tab_chart_view")])

    with tab_list:
        st.info(t("info_forecast"))
        
        display_df = merged[[
            "name", "status", "order_qty", "current_stock", "incoming_units", 
            "safety_stock", "daily_avg_usage", "unit"
        ]].sort_values("order_qty", ascending=False)

        def highlight_row(row):
            return ['background-color: #ffcdd2' if row.status == "🚨 Order" else '' for _ in row]

        st.dataframe(
            display_df.style.apply(highlight_row, axis=1).format({
                "daily_avg_usage": "{:.1f}",
                "order_qty": "{:.0f}",
                "current_stock": "{:.0f}"
            }),
            use_container_width=True,
            height=600
        )
        
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"💾 {t('download_excel')}",
            data=csv,
            file_name=f"inventory_forecast_{date.today()}.csv",
            mime="text/csv",
        )

    with tab_chart:
        merged["required_total"] = merged["forecast_usage"] + merged["safety_stock"]
        chart_data = merged[merged["order_qty"] > 0].copy()
        if not chart_data.empty:
            chart_data = chart_data[["name", "current_stock", "required_total"]]
            chart_data = chart_data.melt("name", var_name="Type", value_name="Units")
            
            c = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('name', sort=None),
                y='Units',
                color='Type',
                tooltip=['name', 'Type', 'Units']
            )
            st.altair_chart(c, use_container_width=True)
        else:
            st.success("No items need ordering.")

# ==========================================
# 페이지: 칫솔 특화
# ==========================================
def page_toothbrush():
    st.header(t("tb_header"))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container(border=True):
            rooms = st.number_input(t("rooms"), value=238)
            occ = st.slider(t("occ"), 10, 100, 90, 5) / 100.0
            horizon = st.slider(t("tb_horizon"), 1, 60, 30)
    
    stock_df = get_latest_stock_df()
    if stock_df.empty: return

    def get_stock(kwd):
        r = stock_df[stock_df["name"].str.contains(kwd, na=False)]
        return float(r.iloc[0]["current_stock"]) if not r.empty else 0.0
    
    cur_nat = get_stock("ナチュラル")
    cur_green = get_stock("グリーン")
    cur_ash = get_stock("アッシュグレー")
    
    daily_nat = rooms * occ * 1.0
    daily_green = rooms * occ * 1.0
    daily_ash = rooms * occ * 0.5
    
    data = []
    for d in range(horizon + 1):
        data.append({"day": d, "color": "Natural", "stock": cur_nat - (daily_nat * d)})
        data.append({"day": d, "color": "Green", "stock": cur_green - (daily_green * d)})
        data.append({"day": d, "color": "AshGrey", "stock": cur_ash - (daily_ash * d)})
    
    chart_df = pd.DataFrame(data)
    
    with col2:
        line_chart = alt.Chart(chart_df).mark_line().encode(
            x='day',
            y='stock',
            color='color',
            tooltip=['day', 'color', 'stock']
        ).properties(title=t("stock_level_chart"))
        
        zero_rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red').encode(y='y')
        st.altair_chart(line_chart + zero_rule, use_container_width=True)

    st.subheader(t("tb_result"))
    final_df = chart_df[chart_df["day"] == horizon].copy()
    final_df["status"] = final_df["stock"].apply(lambda x: "✅ OK" if x > 0 else "🚨 Short")
    st.dataframe(final_df[["color", "stock", "status"]], use_container_width=True)
    st.caption(t("tb_info"))


# ==========================================
# 페이지: 캘린더 (리얼 달력 + CS 표시 구현)
# ==========================================
def get_jp_holiday_name(dt: date):
    iso = dt.isoformat()
    return JAPAN_HOLIDAYS.get(iso, None)

def page_calendar():
    st.header(t("cal_header"))
    
    tab_new, tab_list = st.tabs([t("cal_tab_new"), t("cal_tab_list")])
    items_df = get_items_df()
    
    # 탭 1: 신규 등록
    with tab_new:
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.subheader(t("cal_new"))
                if not items_df.empty:
                    item_map = {f"{r['name']}": r["id"] for _, r in items_df.iterrows()}
                    sel = st.selectbox(t("cal_item"), list(item_map.keys()))
                    item_id = item_map[sel]
                    row = items_df[items_df["id"] == item_id].iloc[0]
                    
                    with st.form("cal_form"):
                        od = st.date_input(t("cal_order_date"))
                        ad = st.date_input(t("cal_arrival_date"))
                        c1, c2 = st.columns(2)
                        qc = c1.number_input(t("cal_cs"), min_value=0)
                        qb = c2.number_input(t("cal_box"), min_value=0)
                        nt = st.text_input(t("cal_note"))
                        
                        if st.form_submit_button(t("btn_save_cal"), use_container_width=True):
                            cs_t, upb = int(row["cs_total_units"] or 0), int(row["units_per_box"] or 0)
                            tot = qc * cs_t + qb * upb
                            add_delivery(item_id, od.isoformat(), ad.isoformat(), int(qc), int(qb), int(tot), nt)
                            st.success(t("success_save_cal"))
                            st.rerun()

    # 탭 2: 달력 보기 및 리스트 (CS 단위 표시)
    with tab_list:
        df = get_delivery_list()
        
        # --- 달력 컨트롤 ---
        if "cal_year" not in st.session_state:
            st.session_state["cal_year"] = date.today().year
            st.session_state["cal_month"] = date.today().month

        c_prev, c_label, c_next = st.columns([1, 2, 1])
        with c_prev:
            if st.button(t("prev_month"), use_container_width=True):
                if st.session_state["cal_month"] == 1:
                    st.session_state["cal_month"] = 12
                    st.session_state["cal_year"] -= 1
                else:
                    st.session_state["cal_month"] -= 1
                st.rerun()
        with c_next:
            if st.button(t("next_month"), use_container_width=True):
                if st.session_state["cal_month"] == 12:
                    st.session_state["cal_month"] = 1
                    st.session_state["cal_year"] += 1
                else:
                    st.session_state["cal_month"] += 1
                st.rerun()
        with c_label:
            st.markdown(f"<h3 style='text-align: center;'>{st.session_state['cal_year']} / {st.session_state['cal_month']}</h3>", unsafe_allow_html=True)

        # --- 달력 그리기 ---
        year = st.session_state["cal_year"]
        month = st.session_state["cal_month"]
        
        df["arrival_dt"] = pd.to_datetime(df["arrival_date"])
        month_df = df[
            (df["arrival_dt"].dt.year == year) & 
            (df["arrival_dt"].dt.month == month)
        ]
        
        # 요일 헤더
        cols = st.columns(7)
        weekdays = t("weekdays")
        for i, day in enumerate(weekdays):
            color = "black"
            if i == 5: color = "blue"
            if i == 6: color = "red"
            cols[i].markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)

        # 날짜 그리드
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.container(height=100, border=False)
                    else:
                        current_date = date(year, month, day)
                        is_today = current_date == date.today()
                        holiday_name = get_jp_holiday_name(current_date)
                        
                        day_color = "black"
                        bg_color = "white"
                        
                        if i == 5: day_color = "blue"
                        if i == 6 or holiday_name: day_color = "red"
                        if is_today: bg_color = "#e3f2fd"

                        with st.container(border=True):
                            label = f"{day}"
                            if holiday_name:
                                label += f" <span style='font-size:0.8em'>({holiday_name})</span>"
                            
                            st.markdown(
                                f"<div style='text-align: right; color: {day_color}; background-color: {bg_color}; padding: 2px;'>{label}</div>", 
                                unsafe_allow_html=True
                            )
                            
                            # 아이템 표시 (CS 단위)
                            day_items = month_df[month_df["arrival_dt"].dt.day == day]
                            for _, item_row in day_items.iterrows():
                                # CS와 Box 표시 (예: 10 CS, 10 CS + 2 B)
                                qty_text = f"{item_row['qty_cs']} CS"
                                if item_row['qty_box'] > 0:
                                    qty_text += f" + {item_row['qty_box']} B"
                                
                                st.markdown(
                                    f"<div style='background-color: #f0f0f0; border-radius: 4px; padding: 2px; margin-top: 2px; font-size: 0.8em;'>"
                                    f"📦 {item_row['item']}<br><b>{qty_text}</b>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )

        st.divider()

        # --- 검색 및 삭제 ---
        if df.empty:
            st.info("No schedules.")
            return

        st.subheader("🔍 Search & Delete")
        c1, c2 = st.columns(2)
        with c1:
            unique_items = ["All"] + list(df["item"].unique())
            search_item = st.selectbox(t("cal_search_item"), unique_items)
        
        filtered_df = df.copy()
        if search_item != "All":
            filtered_df = filtered_df[filtered_df["item"] == search_item]
            
        # 리스트에도 CS 단위 추가
        st.dataframe(
            filtered_df[["id", "order_date", "arrival_date", "item", "qty_cs", "qty_box", "total_units", "note"]],
            column_config={
                "order_date": st.column_config.DateColumn("Ordered"),
                "arrival_date": st.column_config.DateColumn("Arrival"),
                "qty_cs": st.column_config.NumberColumn("CS"),
                "qty_box": st.column_config.NumberColumn("Box"),
                "total_units": st.column_config.NumberColumn("Total Units"),
            },
            use_container_width=True
        )
        
        # 삭제
        del_options = [
            f"ID {r['id']}: {r['arrival_date']} - {r['item']} ({r['qty_cs']} CS, {r['total_units']} units)" 
            for _, r in filtered_df.iterrows()
        ]
        
        c_del_1, c_del_2 = st.columns([3, 1])
        with c_del_1:
            sel_del = st.selectbox(t("select_delete"), del_options, key="del_cal_sel")
        with c_del_2:
            st.write("")
            st.write("")
            if st.button(t("btn_delete"), type="primary", key="del_cal_btn"):
                if sel_del:
                    del_id = int(sel_del.split(":")[0].replace("ID", "").strip())
                    delete_delivery(del_id)
                    st.success(t("success_delete"))
                    st.rerun()


# ==========================================
# 메인
# ==========================================
def main():
    if "lang_code" not in st.session_state:
        st.session_state["lang_code"] = "ko"

    st.set_page_config(
        page_title="Hotel Inventory System", 
        page_icon="🏨", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_db()
    seed_initial_items()

    with st.sidebar:
        st.title("🏨 Inventory AI")
        
        lang_display = {"jp": "🇯🇵 日本語", "en": "🇺🇸 English", "ko": "🇰🇷 한국어"}
        st.selectbox(
            TEXTS[get_lang_code()]["lang"],
            options=list(lang_display.keys()),
            format_func=lambda x: lang_display[x],
            key="lang_code"
        )
        
        st.divider()
        
        menu_keys = ["menu_home", "menu_items", "menu_stock", "menu_forecast", "menu_toothbrush", "menu_calendar"]
        menu_labels = [t(k) for k in menu_keys]
        
        selection_label = st.radio(t("menu_title"), menu_labels)
        
        if selection_label == t("menu_home"): selection = "home"
        elif selection_label == t("menu_items"): selection = "items"
        elif selection_label == t("menu_stock"): selection = "stock"
        elif selection_label == t("menu_forecast"): selection = "forecast"
        elif selection_label == t("menu_toothbrush"): selection = "toothbrush"
        elif selection_label == t("menu_calendar"): selection = "calendar"
        else: selection = "home"

        st.divider()
        st.caption("v2.1 Calendar CS Unit")

    if selection == "home":
        page_home()
    elif selection == "items":
        page_items()
    elif selection == "stock":
        page_stock()
    elif selection == "forecast":
        page_forecast_general()
    elif selection == "toothbrush":
        page_toothbrush()
    elif selection == "calendar":
        page_calendar()

if __name__ == "__main__":
    main()