import pandas as pd
import streamlit as st
import altair as alt
from datetime import date, timedelta, datetime
import calendar
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 설정 및 DB 연결 (Google Sheets)
# ==========================================
SHEET_NAME = "inventory_system"  # 구글 시트 파일 이름

# 일본 공휴일 (유지)
JAPAN_HOLIDAYS = {
    "2025-01-01": "元日", "2025-01-13": "成人の日", "2025-02-11": "建国記念の日",
    "2025-02-23": "天皇誕生日", "2025-02-24": "振替休日", "2025-03-20": "春分の日",
    "2025-04-29": "昭和の日", "2025-05-03": "憲法記念日", "2025-05-04": "みどりの日",
    "2025-05-05": "こどもの日", "2025-05-06": "振替休日", "2025-07-21": "海の日",
    "2025-08-11": "山の日", "2025-09-15": "敬老の日", "2025-09-23": "秋分の日",
    "2025-10-13": "スポーツの日", "2025-11-03": "文化の日", "2025-11-23": "勤労感謝の日",
    "2025-11-24": "振替休日",
    "2026-01-01": "元日", "2026-01-12": "成人の日", "2026-02-11": "建国記念の日",
}

# 텍스트 리소스 (유지)
TEXTS = {
    "jp": {
        "title": "ホテル在庫予測システム (Google Sheets)", "menu_title": "メニュー", "menu_home": "🏠 ホーム・サマリー",
        "menu_items": "📦 1. 品目マスター", "menu_stock": "📝 2. 在庫記録", "menu_forecast": "📊 3. 予測＆発注",
        "menu_toothbrush": "🪥 4. 歯ブラシ予測", "menu_calendar": "📅 5. 発注カレンダー",
        "dashboard_alert": "発注推奨品目数", "dashboard_incoming": "入荷待ち件数", "dashboard_total_items": "登録品目数",
        "download_excel": "予測結果をExcelでダウンロード", "stock_level_chart": "在庫推移予測チャート",
        "items_header": "品目マスター管理", "items_new": "新規登録", "items_list": "登録済み一覧",
        "item_name": "品目名", "unit": "単位", "safety": "安全在庫", "cs_total": "1CS入数", "units_per_box": "1箱入数", "boxes_per_cs": "1CS箱数",
        "btn_register": "登録", "btn_update": "更新", "items_edit": "編集・削除", "select_item_edit": "品目選択",
        "err_itemname": "品目名は必須です。", "success_register": "登録しました。", "success_update": "更新しました。",
        "stock_header": "在庫記録管理", "stock_tab_input": "新規入力", "stock_tab_history": "履歴確認・削除",
        "stock_select_item": "品目選択", "stock_date": "日付", "stock_cs": "CS", "stock_box": "箱/袋", "stock_note": "備考",
        "btn_save_stock": "保存", "err_conv": "換算設定エラー。マスターを確認してください。", "success_save_stock": "保存しました。",
        "recent_stock": "最新在庫状況", "history_list": "最近の入力履歴（削除可能）", "btn_delete": "削除",
        "select_delete": "削除する記録を選択 (ID: 日付 - 品目)", "success_delete": "削除しました。", "warn_no_data": "データがありません。",
        "forecast_header": "在庫予測・発注", "days_label": "過去平均算出期間(日)", "horizon_label": "予測期間(日)",
        "forecast_result": "発注推奨リスト", "info_forecast": "赤色は在庫不足の可能性がある品目です。", "tab_list_view": "📋 リスト表示", "tab_chart_view": "📈 チャート表示",
        "tb_header": "歯ブラシ特化予測", "warn_tb_items": "品目名に「ナチュラル」「グリーン」「アッシュグレー」を含む品目が必要です。",
        "rooms": "客室数", "occ": "稼働率(%)", "tb_horizon": "予測期間", "tb_result": "色別必要数シミュレーション", "tb_info": "2.5名/室 想定",
        "cal_header": "入荷予定カレンダー", "cal_tab_new": "予定登録", "cal_tab_list": "カレンダー・検索・削除",
        "cal_item": "品目", "cal_order_date": "発注日", "cal_arrival_date": "入荷予定日", "cal_cs": "CS", "cal_box": "箱/袋", "cal_note": "備考",
        "btn_save_cal": "登録", "success_save_cal": "登録しました。", "cal_list": "入荷予定一覧", "cal_search_item": "品目検索",
        "weekdays": ["月", "火", "水", "木", "金", "土", "日"], "prev_month": "◀ 前月", "next_month": "翌月 ▶", "today": "今日",
        "lang": "Language"
    },
    "en": {"lang": "Language", "menu_title": "Menu", "menu_home": "🏠 Home", "menu_items": "📦 Items", "menu_stock": "📝 Stock", "menu_forecast": "📊 Forecast", "menu_toothbrush": "🪥 Toothbrush", "menu_calendar": "📅 Calendar", "dashboard_alert": "Alerts", "dashboard_incoming": "Incoming", "dashboard_total_items": "Items", "btn_delete": "Delete", "success_delete": "Deleted.", "warn_no_data": "No Data.", "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "prev_month": "Prev", "next_month": "Next", "today": "Today", "cal_search_item": "Search Item", "cal_list": "List", "cal_tab_new": "New", "cal_tab_list": "List/Del", "cal_header": "Calendar", "tb_header": "Toothbrush Sim", "forecast_header": "Forecast", "stock_header": "Stock Input", "items_header": "Item Master", "btn_save_stock": "Save", "btn_save_cal": "Save", "btn_register": "Register", "btn_update": "Update", "success_save_stock": "Saved", "success_save_cal": "Saved", "success_register": "Registered", "success_update": "Updated"},
    "ko": {
        "title": "호텔 재고 예측 시스템 (Google Sheets)", "lang": "Language / 言語 / 언어", "menu_title": "메뉴",
        "menu_home": "🏠 홈 & 요약", "menu_items": "📦 1. 품목 마스터", "menu_stock": "📝 2. 재고 입력",
        "menu_forecast": "📊 3. 예측 & 발주", "menu_toothbrush": "🪥 4. 칫솔 시뮬레이션", "menu_calendar": "📅 5. 발주 캘린더",
        "dashboard_alert": "발주 필요 품목", "dashboard_incoming": "입고 예정 건수", "dashboard_total_items": "등록 품목 수",
        "download_excel": "예측 결과 엑셀 다운로드", "stock_level_chart": "재고 소진 예측 차트",
        "items_header": "품목 관리", "items_new": "새 품목 등록", "items_list": "품목 목록",
        "item_name": "품목명", "unit": "단위", "safety": "안전 재고", "cs_total": "1CS 총개수", "units_per_box": "1박스 개수", "boxes_per_cs": "1CS 박스수",
        "btn_register": "등록", "btn_update": "수정 저장", "items_edit": "수정 및 삭제", "select_item_edit": "수정할 품목",
        "err_itemname": "품목명은 필수입니다.", "success_register": "저장되었습니다.", "success_update": "수정되었습니다.",
        "stock_header": "실재고(스냅샷) 관리", "stock_tab_input": "새 재고 입력", "stock_tab_history": "입력 기록 / 삭제",
        "stock_select_item": "품목 선택", "stock_date": "측정일", "stock_cs": "CS", "stock_box": "박스/봉투", "stock_note": "비고",
        "btn_save_stock": "저장", "err_conv": "환산 설정 오류. 마스터를 확인하세요.", "success_save_stock": "저장되었습니다.",
        "recent_stock": "최신 재고 현황", "history_list": "최근 입력 기록 (삭제 가능)", "btn_delete": "삭제",
        "select_delete": "삭제할 기록 선택 (ID: 날짜 - 품목)", "success_delete": "삭제했습니다.", "warn_no_data": "데이터가 없습니다.",
        "forecast_header": "재고 예측 및 발주 권고", "days_label": "평균 사용량 산출 기간(일)", "horizon_label": "예측 기간(일)",
        "forecast_result": "발주 추천 리스트", "info_forecast": "붉은색 행은 재고 부족이 예상되는 품목입니다.",
        "tab_list_view": "📋 리스트 보기", "tab_chart_view": "📈 차트 보기",
        "tb_header": "칫솔 소진 시뮬레이션", "warn_tb_items": "마스터에 'ナチュラル', 'グリーン', 'アッシュグレー'가 포함된 품목이 필요합니다.",
        "rooms": "객실 수", "occ": "가동률(%)", "tb_horizon": "예측 기간", "tb_result": "색상별 소진 예측", "tb_info": "객실당 2.5명 기준 시뮬레이션입니다.",
        "cal_header": "발주/입고 캘린더", "cal_tab_new": "입고 예정 등록", "cal_tab_list": "달력 / 검색 / 삭제",
        "cal_item": "품목", "cal_order_date": "발주일", "cal_arrival_date": "도착 예정일", "cal_cs": "CS", "cal_box": "박스", "cal_note": "비고",
        "btn_save_cal": "등록", "success_save_cal": "저장되었습니다.", "cal_list": "입고 예정 목록",
        "cal_search_item": "품목 검색", "weekdays": ["월", "화", "수", "목", "금", "토", "일"],
        "prev_month": "◀ 이전 달", "next_month": "다음 달 ▶", "today": "오늘",
    },
}

def get_lang_code():
    return st.session_state.get("lang_code", "ko")

def t(key: str) -> str:
    lang = get_lang_code()
    return TEXTS.get(lang, TEXTS["ko"]).get(key, key)

# ==========================================
# Google Sheets 연결 함수
# ==========================================
@st.cache_resource
def get_sheet_connection():
    """Streamlit Secrets에서 키를 가져와 구글 시트에 연결"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Secrets에서 gcp_service_account 정보를 가져옵니다.
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    return sheet

def get_data(worksheet_name):
    """시트에서 데이터를 읽어 DataFrame으로 반환"""
    try:
        sh = get_sheet_connection()
        wks = sh.worksheet(worksheet_name)
        data = wks.get_all_records()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"DB Error ({worksheet_name}): {e}")
        return pd.DataFrame()

def add_row(worksheet_name, row_dict):
    """시트에 행 추가 (Auto ID 포함)"""
    sh = get_sheet_connection()
    wks = sh.worksheet(worksheet_name)
    
    # ID 생성 로직
    data = wks.get_all_records()
    if data:
        df = pd.DataFrame(data)
        new_id = int(df["id"].max()) + 1 if "id" in df.columns and not df.empty else 1
    else:
        new_id = 1
    
    row_dict["id"] = new_id
    
    # 헤더 순서대로 값 정렬
    headers = wks.row_values(1)
    row_values = [row_dict.get(h, "") for h in headers]
    
    wks.append_row(row_values)
    st.cache_data.clear() # 캐시 초기화

def update_row(worksheet_name, row_id, update_dict):
    """ID로 행을 찾아 수정"""
    sh = get_sheet_connection()
    wks = sh.worksheet(worksheet_name)
    data = wks.get_all_records()
    df = pd.DataFrame(data)
    
    # ID로 행 번호 찾기 (1-based index + header 1줄)
    try:
        row_idx = df[df["id"] == row_id].index[0] + 2
        headers = wks.row_values(1)
        
        # 각 컬럼별로 업데이트
        for col_name, value in update_dict.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1
                wks.update_cell(row_idx, col_idx, value)
        st.cache_data.clear()
    except IndexError:
        st.error("ID not found.")

def delete_row(worksheet_name, row_id):
    """ID로 행을 찾아 삭제"""
    sh = get_sheet_connection()
    wks = sh.worksheet(worksheet_name)
    data = wks.get_all_records()
    df = pd.DataFrame(data)
    
    try:
        row_idx = df[df["id"] == row_id].index[0] + 2
        wks.delete_rows(row_idx)
        st.cache_data.clear()
    except IndexError:
        st.error("ID not found.")

# ==========================================
# 데이터 처리 로직 (기존 DB 로직 대체)
# ==========================================
def get_items_df():
    return get_data("items")

def add_item(name, unit, cs, upb, bpc, safe):
    add_row("items", {
        "name": name, "unit": unit, "cs_total_units": cs,
        "units_per_box": upb, "boxes_per_cs": bpc, "safety_stock": safe
    })

def update_item_logic(iid, name, unit, cs, upb, bpc, safe):
    update_row("items", iid, {
        "name": name, "unit": unit, "cs_total_units": cs,
        "units_per_box": upb, "boxes_per_cs": bpc, "safety_stock": safe
    })

def delete_item_logic(iid):
    # 사용 중인지 체크
    snaps = get_data("snapshots")
    dels = get_data("deliveries")
    
    s_cnt = len(snaps[snaps["item_id"] == iid]) if not snaps.empty else 0
    d_cnt = len(dels[dels["item_id"] == iid]) if not dels.empty else 0
    
    if s_cnt == 0 and d_cnt == 0:
        delete_row("items", iid)
        return True, 0, 0
    return False, s_cnt, d_cnt

def add_snapshot(iid, date, qc, qb, tot, note):
    add_row("snapshots", {
        "item_id": iid, "snap_date": date, "qty_cs": qc,
        "qty_box": qb, "total_units": tot, "note": note
    })

def delete_snapshot(sid):
    delete_row("snapshots", sid)

def add_delivery(iid, o_date, a_date, qc, qb, tot, note):
    add_row("deliveries", {
        "item_id": iid, "order_date": o_date, "arrival_date": a_date,
        "qty_cs": qc, "qty_box": qb, "total_units": tot, "note": note
    })

def delete_delivery(did):
    delete_row("deliveries", did)

def get_latest_stock_df():
    items = get_data("items")
    snaps = get_data("snapshots")
    
    if items.empty: return pd.DataFrame()
    if snaps.empty:
        items["current_stock"] = 0
        items["last_snap_date"] = None
        return items
    
    snaps["snap_date"] = pd.to_datetime(snaps["snap_date"])
    snaps = snaps.sort_values(["item_id", "snap_date"])
    latest = snaps.groupby("item_id").tail(1)
    latest = latest.rename(columns={"total_units": "current_stock", "snap_date": "last_snap_date"})
    
    merged = items.merge(latest[["item_id", "current_stock", "last_snap_date"]], left_on="id", right_on="item_id", how="left")
    merged["current_stock"] = merged["current_stock"].fillna(0)
    return merged

def get_recent_snapshots_per_item():
    df = get_latest_stock_df()
    if df.empty: return df
    return df[["id", "name", "current_stock", "last_snap_date"]]

def get_snapshot_history():
    snaps = get_data("snapshots")
    items = get_data("items")
    if snaps.empty or items.empty: return pd.DataFrame()
    
    merged = snaps.merge(items[["id", "name"]], left_on="item_id", right_on="id", how="left")
    return merged.sort_values("snap_date", ascending=False).head(50)

def get_usage_from_snapshots(days=60):
    snaps = get_data("snapshots")
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
            
    return pd.DataFrame(records)

def get_future_deliveries(horizon_days):
    dels = get_data("deliveries")
    if dels.empty: return pd.DataFrame(columns=["item_id", "incoming_units"])
    
    today = pd.to_datetime(date.today())
    end_date = today + timedelta(days=horizon_days)
    dels["arrival_date"] = pd.to_datetime(dels["arrival_date"])
    
    mask = (dels["arrival_date"] > today) & (dels["arrival_date"] <= end_date)
    future = dels[mask]
    
    return future.groupby("item_id")["total_units"].sum().reset_index().rename(columns={"total_units": "incoming_units"})

def get_delivery_list():
    dels = get_data("deliveries")
    items = get_data("items")
    if dels.empty or items.empty: return pd.DataFrame()
    
    merged = dels.merge(items[["id", "name"]], left_on="item_id", right_on="id", how="left")
    merged = merged.rename(columns={"name": "item"})
    return merged.sort_values(["arrival_date", "order_date"])

def get_jp_holiday_name(dt: date):
    iso = dt.isoformat()
    return JAPAN_HOLIDAYS.get(iso, None)

# ==========================================
# 페이지 함수들 (기존 UI 로직 유지)
# ==========================================
def page_home():
    st.header(t("menu_home"))
    stock_df = get_latest_stock_df()
    if stock_df.empty:
        st.info("No Data / 데이터 없음 (구글 시트를 확인하세요)")
        return

    days, horizon = 60, 30
    usage_df = get_usage_from_snapshots(days)
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
    
    urgent = merged[merged["order_qty"] > 0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric(t("dashboard_alert"), f"{len(urgent)}", delta_color="inverse")
    c2.metric(t("dashboard_incoming"), f"{len(get_delivery_list())}")
    c3.metric(t("dashboard_total_items"), f"{len(stock_df)}")
    
    st.divider()
    if not urgent.empty:
        st.subheader("🚨 Urgent Orders")
        st.dataframe(
            urgent[["name", "current_stock", "safety_stock", "order_qty", "unit"]].style.background_gradient(cmap="Reds", subset=["order_qty"]),
            use_container_width=True
        )
    else:
        st.success("✅ All stocks are safe.")

def page_items():
    st.header(t("items_header"))
    tab1, tab2 = st.tabs([t("items_list"), t("items_new")])
    
    with tab1:
        df = get_items_df()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.divider()
            st.subheader(t("items_edit"))
            
            opts = [f"{row['name']} (ID:{row['id']})" for _, row in df.iterrows()]
            sel = st.selectbox(t("select_item_edit"), opts)
            if sel:
                iid = int(sel.split("ID:")[1].replace(")", ""))
                row = df[df["id"] == iid].iloc[0]
                
                with st.form("edit_item"):
                    c1, c2 = st.columns(2)
                    n = c1.text_input(t("item_name"), row["name"])
                    u = c1.text_input(t("unit"), row["unit"])
                    s = c1.number_input(t("safety"), 0, value=int(row["safety_stock"]))
                    ct = c2.number_input(t("cs_total"), 0, value=int(row["cs_total_units"]))
                    up = c2.number_input(t("units_per_box"), 0, value=int(row["units_per_box"]))
                    bp = c2.number_input(t("boxes_per_cs"), 0, value=int(row["boxes_per_cs"]))
                    
                    if st.form_submit_button(t("btn_update")):
                        update_item_logic(iid, n, u, ct, up, bp, s)
                        st.success(t("success_update"))
                        st.rerun()
                
                if st.button(t("btn_delete"), type="primary"):
                    ok, sc, dc = delete_item_logic(iid)
                    if ok:
                        st.success(t("success_delete"))
                        st.rerun()
                    else:
                        st.error(f"Cannot delete. Used in {sc} snapshots, {dc} deliveries.")
        else:
            st.info("No items.")

    with tab2:
        with st.form("new_item"):
            c1, c2 = st.columns(2)
            n = c1.text_input(t("item_name"))
            u = c1.text_input(t("unit"), "本")
            s = c1.number_input(t("safety"), 0)
            ct = c2.number_input(t("cs_total"), 0)
            up = c2.number_input(t("units_per_box"), 0)
            bp = c2.number_input(t("boxes_per_cs"), 0)
            
            if st.form_submit_button(t("btn_register")):
                if n:
                    add_item(n, u, ct, up, bp, s)
                    st.success(t("success_register"))
                    st.rerun()
                else:
                    st.error(t("err_itemname"))

def page_stock():
    st.header(t("stock_header"))
    t1, t2 = st.tabs([t("stock_tab_input"), t("stock_tab_history")])
    items = get_items_df()
    
    with t1:
        if not items.empty:
            c1, c2 = st.columns([1, 1.5])
            with c1:
                imap = {r["name"]: r["id"] for _, r in items.iterrows()}
                sel = st.selectbox(t("stock_select_item"), list(imap.keys()))
                iid = imap[sel]
                row = items[items["id"] == iid].iloc[0]
                st.caption(f"1CS={row['cs_total_units']}, 1Box={row['units_per_box']}")
                
                with st.form("stock_in"):
                    d = st.date_input(t("stock_date"), date.today())
                    cc1, cc2 = st.columns(2)
                    qc = cc1.number_input(t("stock_cs"), 0)
                    qb = cc2.number_input(t("stock_box"), 0)
                    nt = st.text_area(t("stock_note"), height=68)
                    
                    if st.form_submit_button(t("btn_save_stock")):
                        tot = qc * row["cs_total_units"] + qb * row["units_per_box"]
                        add_snapshot(iid, d.isoformat(), qc, qb, tot, nt)
                        st.success(t("success_save_stock"))
                        st.rerun()
            with c2:
                st.subheader(t("recent_stock"))
                st.dataframe(get_recent_snapshots_per_item(), use_container_width=True)
    
    with t2:
        hist = get_snapshot_history()
        if not hist.empty:
            st.dataframe(hist, use_container_width=True)
            st.subheader(t("btn_delete"))
            opts = [f"ID {r['id']}: {r['snap_date']} - {r['name']}" for _, r in hist.iterrows()]
            s = st.selectbox(t("select_delete"), opts)
            if st.button(t("btn_delete"), key="del_snap"):
                if s:
                    sid = int(s.split(":")[0].replace("ID", "").strip())
                    delete_snapshot(sid)
                    st.success(t("success_delete"))
                    st.rerun()

def page_forecast_general():
    st.header(t("forecast_header"))
    stock = get_latest_stock_df()
    if stock.empty: return
    
    with st.expander("⚙️ Settings"):
        c1, c2 = st.columns(2)
        days = c1.slider(t("days_label"), 7, 120, 60)
        hor = c2.slider(t("horizon_label"), 7, 120, 30)
        
    usage = get_usage_from_snapshots(days)
    merged = stock.merge(usage, on="id", how="left").fillna(0)
    merged["forecast"] = merged["daily_avg_usage"] * hor
    incoming = get_future_deliveries(hor)
    if not incoming.empty:
        merged = merged.merge(incoming, left_on="id", right_on="item_id", how="left").fillna(0)
    else:
        merged["incoming_units"] = 0
        
    merged["order"] = (merged["forecast"] + merged["safety_stock"] - merged["current_stock"] - merged["incoming_units"]).apply(lambda x: x if x > 0 else 0)
    
    st.dataframe(merged[["name", "current_stock", "incoming_units", "forecast", "safety_stock", "order"]].sort_values("order", ascending=False), use_container_width=True)

def page_toothbrush():
    st.header(t("tb_header"))
    stock = get_latest_stock_df()
    if stock.empty: return
    
    c1, c2 = st.columns([1, 2])
    with c1:
        rooms = st.number_input("Rooms", value=238)
        occ = st.slider("Occupancy", 0, 100, 90) / 100
        days = st.slider("Days", 1, 60, 30)
        
    def get_st(k):
        r = stock[stock["name"].str.contains(k)]
        return r.iloc[0]["current_stock"] if not r.empty else 0
        
    cur = {"N": get_st("ナチュラル"), "G": get_st("グリーン"), "A": get_st("アッシュ")}
    usage = rooms * occ
    
    data = []
    for d in range(days + 1):
        data.append({"d": d, "type": "Natural", "val": cur["N"] - (usage * 1.0 * d)})
        data.append({"d": d, "type": "Green", "val": cur["G"] - (usage * 1.0 * d)})
        data.append({"d": d, "type": "Ash", "val": cur["A"] - (usage * 0.5 * d)})
        
    chart = alt.Chart(pd.DataFrame(data)).mark_line().encode(x='d', y='val', color='type')
    st.altair_chart(chart + alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red').encode(y='y'), use_container_width=True)

def page_calendar():
    st.header(t("cal_header"))
    t1, t2 = st.tabs([t("cal_tab_new"), t("cal_tab_list")])
    items = get_items_df()
    
    with t1:
        if not items.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                imap = {r["name"]: r["id"] for _, r in items.iterrows()}
                sel = st.selectbox(t("cal_item"), list(imap.keys()))
                iid = imap[sel]
                row = items[items["id"] == iid].iloc[0]
                
                with st.form("cal_in"):
                    od = st.date_input(t("cal_order_date"))
                    ad = st.date_input(t("cal_arrival_date"))
                    cc1, cc2 = st.columns(2)
                    qc = cc1.number_input(t("cal_cs"), 0)
                    qb = cc2.number_input(t("cal_box"), 0)
                    nt = st.text_input(t("cal_note"))
                    
                    if st.form_submit_button(t("btn_save_cal")):
                        tot = qc * row["cs_total_units"] + qb * row["units_per_box"]
                        add_delivery(iid, od.isoformat(), ad.isoformat(), qc, qb, tot, nt)
                        st.success(t("success_save_cal"))
                        st.rerun()
                        
    with t2:
        df = get_delivery_list()
        if not df.empty:
            # 달력
            if "cy" not in st.session_state: st.session_state["cy"] = date.today().year
            if "cm" not in st.session_state: st.session_state["cm"] = date.today().month
            
            c_p, c_l, c_n = st.columns([1, 2, 1])
            if c_p.button(t("prev_month")): 
                if st.session_state["cm"] == 1: st.session_state["cm"]=12; st.session_state["cy"]-=1
                else: st.session_state["cm"]-=1
                st.rerun()
            if c_n.button(t("next_month")):
                if st.session_state["cm"] == 12: st.session_state["cm"]=1; st.session_state["cy"]+=1
                else: st.session_state["cm"]+=1
                st.rerun()
            c_l.markdown(f"<h3 style='text-align:center'>{st.session_state['cy']} / {st.session_state['cm']}</h3>", unsafe_allow_html=True)
            
            cols = st.columns(7)
            for i, d in enumerate(t("weekdays")):
                cols[i].markdown(f"<div style='text-align:center;font-weight:bold;color:{'blue' if i==5 else 'red' if i==6 else 'black'}'>{d}</div>", unsafe_allow_html=True)
            
            cal = calendar.monthcalendar(st.session_state["cy"], st.session_state["cm"])
            df["adt"] = pd.to_datetime(df["arrival_date"])
            m_df = df[(df["adt"].dt.year == st.session_state["cy"]) & (df["adt"].dt.month == st.session_state["cm"])]
            
            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    with cols[i]:
                        if day != 0:
                            dt = date(st.session_state["cy"], st.session_state["cm"], day)
                            hol = get_jp_holiday_name(dt)
                            bg = "#e3f2fd" if dt == date.today() else "white"
                            clr = "blue" if i==5 else "red" if i==6 or hol else "black"
                            
                            with st.container(border=True):
                                lbl = f"{day}" + (f" <small>({hol})</small>" if hol else "")
                                st.markdown(f"<div style='text-align:right;color:{clr};background:{bg}'>{lbl}</div>", unsafe_allow_html=True)
                                for _, r in m_df[m_df["adt"].dt.day == day].iterrows():
                                    # CS 단위 표시
                                    q_txt = f"{r['qty_cs']} CS"
                                    if r['qty_box'] > 0: q_txt += f" + {r['qty_box']} B"
                                    st.markdown(f"<div style='background:#f0f0f0;font-size:0.8em;padding:2px'>📦 {r['item']}<br><b>{q_txt}</b></div>", unsafe_allow_html=True)
                        else:
                            st.write("")

            st.divider()
            st.subheader(t("cal_list"))
            
            # 검색 및 삭제
            c1, c2 = st.columns(2)
            si = c1.selectbox(t("cal_search_item"), ["All"] + list(df["item"].unique()))
            if si != "All": df = df[df["item"] == si]
            
            st.dataframe(df[["order_date", "arrival_date", "item", "qty_cs", "qty_box", "total_units", "note"]], use_container_width=True)
            
            opts = [f"ID {r['id']}: {r['arrival_date']} - {r['item']} ({r['qty_cs']} CS)" for _, r in df.iterrows()]
            sd = st.selectbox(t("select_delete"), opts, key="del_cal")
            if st.button(t("btn_delete"), key="btn_del_cal"):
                if sd:
                    did = int(sd.split(":")[0].replace("ID", "").strip())
                    delete_delivery(did)
                    st.success(t("success_delete"))
                    st.rerun()

# ==========================================
# 메인 실행
# ==========================================
def main():
    if "lang_code" not in st.session_state:
        st.session_state["lang_code"] = "ko"
    
    st.set_page_config(page_title="Inventory", layout="wide")
    
    with st.sidebar:
        st.title("🏨 Inventory AI")
        lang_display = {"jp": "🇯🇵 日本語", "en": "🇺🇸 English", "ko": "🇰🇷 한국어"}
        st.selectbox("Language", list(lang_display.keys()), format_func=lambda x: lang_display[x], key="lang_code")
        st.divider()
        
        menu = ["menu_home", "menu_items", "menu_stock", "menu_forecast", "menu_toothbrush", "menu_calendar"]
        sel_label = st.radio(t("menu_title"), [t(k) for k in menu])
        sel = menu[[t(k) for k in menu].index(sel_label)].replace("menu_", "")
        st.divider()
        st.caption("v2.2 Google Sheets + CS Unit")

    if sel == "home": page_home()
    elif sel == "items": page_items()
    elif sel == "stock": page_stock()
    elif sel == "forecast": page_forecast_general()
    elif sel == "toothbrush": page_toothbrush()
    elif sel == "calendar": page_calendar()

if __name__ == "__main__":
    main()
