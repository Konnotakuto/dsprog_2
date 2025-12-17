import requests
import flet as ft

AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
WEATHER_ICON_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/img/{code}.svg"

# 地域グループの定義（ExpansionTile用）
REGION_GROUPS = {
    "北海道": ["016000", "017000"],
    "東北": ["020000", "030000", "040000", "050000", "060000", "070000"],
    "関東": ["080000", "090000", "100000", "110000", "120000", "130000", "140000"],
    "中部": ["150000", "160000", "170000", "180000", "190000", "200000", "210000", "220000", "230000"],
    "近畿": ["240000", "250000", "260000", "270000", "280000", "290000", "300000"],
    "中国": ["310000", "320000", "330000", "340000", "350000"],
    "四国": ["360000", "370000", "380000", "390000"],
    "九州・沖縄": ["400000", "410000", "420000", "430000", "440000", "450000", "460100", "471000"],
}

# 天気コードから天気名へのマッピング（簡易版）
WEATHER_CODE_MAP = {
    "100": "晴れ",
    "101": "晴れ時々曇り",
    "102": "晴れ一時雨",
    "103": "晴れ時々雨",
    "104": "晴れ一時雪",
    "105": "晴れ時々雪",
    "110": "晴れのち曇り",
    "111": "晴れのち雨",
    "112": "晴れのち雪",
    "200": "曇り",
    "201": "曇り時々晴れ",
    "202": "曇り一時雨",
    "203": "曇り時々雨",
    "204": "曇り一時雪",
    "205": "曇り時々雪",
    "210": "曇りのち晴れ",
    "211": "曇りのち雨",
    "212": "曇りのち雪",
    "300": "雨",
    "301": "雨時々晴れ",
    "302": "雨時々曇り",
    "303": "雨時々雪",
    "311": "雨のち晴れ",
    "313": "雨のち曇り",
    "314": "雨のち雪",
    "400": "雪",
    "401": "雪時々晴れ",
    "402": "雪時々曇り",
    "403": "雪時々雨",
    "411": "雪のち晴れ",
    "413": "雪のち曇り",
    "414": "雪のち雨",
}


def fetch_area_map() -> dict:
    response = requests.get(AREA_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    offices = data.get("offices")
    if offices:
        return offices
    raise ValueError("offices データを取得できませんでした")


def fetch_forecast(area_code: str) -> list:
    url = FORECAST_URL_TEMPLATE.format(code=area_code)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def pick_area_entry(series: dict, area_code: str, area_name: str) -> dict:
    """選択された地域に最も近いエリア情報を取得"""
    areas = series.get("areas", [])
    if not areas:
        return {}
    for entry in areas:
        code = entry.get("area", {}).get("code")
        if code == area_code:
            return entry
    for entry in areas:
        name = entry.get("area", {}).get("name")
        if name == area_name:
            return entry
    return areas[0]


def create_forecast_view(forecast: list, area_name: str, area_code: str) -> ft.Column:
    """天気予報をListTileを使って表示するビューを作成"""
    if not forecast or len(forecast) == 0:
        return ft.Column([ft.Text("予報データがありません")])

    series = forecast[0].get("timeSeries", [])
    if not series:
        return ft.Column([ft.Text("時系列データがありません")])

    # 天気情報を取得
    time_series = series[0]
    area = pick_area_entry(time_series, area_code, area_name)
    weathers = area.get("weathers", [])
    weather_codes = area.get("weatherCodes", [])
    time_defines = time_series.get("timeDefines", [])

    # 降水確率を取得（別の時系列にある場合がある）
    pops = []
    if len(series) > 1:
        pop_series = series[1]
        pop_area = pick_area_entry(pop_series, area_code, area_name)
        pops = pop_area.get("pops", [])

    # 風情報を取得
    winds = area.get("winds", [])

    # 天気予報カードのリスト
    forecast_cards = []

    # ヘッダー
    forecast_cards.append(
        ft.Text(
            f"📍 {area_name} の天気予報",
            size=24,
            weight=ft.FontWeight.BOLD,
        )
    )
    forecast_cards.append(ft.Divider())

    # 各時間帯の予報を表示
    item_count = max(
        len(weather_codes),
        len(weathers),
        len(time_defines),
        len(winds),
        len(pops),
    )
    if item_count == 0:
        return ft.Column([
            ft.Text("詳細な予報データがありません"),
        ])
    max_items = min(item_count, 3)

    for i in range(max_items):
        weather_code = weather_codes[i] if i < len(weather_codes) else None
        weather_text = weathers[i] if i < len(weathers) else "情報なし"
        time_label = time_defines[i].split("T")[0] if i < len(time_defines) else f"Day {i+1}"
        wind_text = winds[i] if i < len(winds) else "情報なし"
        pop_text = f"{pops[i]}%" if i < len(pops) and pops[i] else "-"
        if len(wind_text) > 30:
            wind_text = f"{wind_text[:30]}..."

        # 天気アイコン
        if weather_code:
            icon_url = WEATHER_ICON_TEMPLATE.format(code=weather_code)
            weather_name = WEATHER_CODE_MAP.get(weather_code, weather_text)
            weather_icon = ft.Image(
                src=icon_url,
                width=60,
                height=60,
                fit=ft.ImageFit.CONTAIN,
            )
        else:
            weather_name = weather_text
            weather_icon = ft.Text("☁️", size=40)

        # ExpansionTileを使って詳細情報を折りたたみ可能に
        expansion_tile = ft.ExpansionTile(
            title=ft.Text(time_label, weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(weather_name),
            leading=weather_icon,
            affinity=ft.TileAffinity.LEADING,
            initially_expanded=i == 0,  # 最初のアイテムだけ展開
            controls=[
                ft.ListTile(
                    leading=ft.Text("💧", size=20),
                    title=ft.Text("降水確率"),
                    trailing=ft.Text(pop_text, size=16, weight=ft.FontWeight.BOLD),
                ),
                ft.ListTile(
                    leading=ft.Text("🌬️", size=20),
                    title=ft.Text("風"),
                    subtitle=ft.Text(wind_text, size=12),
                ),
                ft.ListTile(
                    leading=ft.Text("📝", size=20),
                    title=ft.Text("詳細"),
                    subtitle=ft.Text(weather_text if len(weather_text) <= 50 else f"{weather_text[:50]}...", size=12),
                ),
            ],
        )

        forecast_cards.append(
            ft.Card(
                content=ft.Container(
                    content=expansion_tile,
                    padding=8,
                ),
            )
        )

    return ft.Column(forecast_cards, spacing=16, scroll=ft.ScrollMode.AUTO)


def main(page: ft.Page) -> None:
    page.title = "JMA 天気予報ビューワー"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    status_text = ft.Text("")
    spinner = ft.ProgressRing(visible=False)
    forecast_container = ft.Container(expand=True)
    area_name_map: dict[str, str] = {}
    selected_code: str = ""
    selected_name: str = ""

    # 選択された地域を表示するテキスト
    selected_area_text = ft.Text("地域を選択してください", size=16)

    def set_status(message: str, *, error: bool = False) -> None:
        status_text.value = message
        status_text.color = "red" if error else "black"
        page.update()

    def on_area_click(code: str, name: str):
        """地域が選択された時の処理"""
        nonlocal selected_code, selected_name
        selected_code = code
        selected_name = name
        selected_area_text.value = f"選択中: {name}"
        page.update()

    def on_fetch(_):
        if not selected_code:
            set_status("地域を選択してください", error=True)
            return
        spinner.visible = True
        set_status("天気予報を取得中...")
        forecast_container.content = None
        page.update()
        try:
            forecast = fetch_forecast(selected_code)
            forecast_container.content = create_forecast_view(forecast, selected_name, selected_code)
            set_status("天気予報を取得しました")
        except Exception as exc:
            forecast_container.content = ft.Text(f"エラー: {exc}", color="red")
            set_status(f"天気予報の取得に失敗: {exc}", error=True)
        finally:
            spinner.visible = False
            page.update()

    def create_region_tiles(area_map: dict) -> list:
        """ExpansionTileを使って地域をグループ化"""
        tiles = []

        for region_name, codes in REGION_GROUPS.items():
            region_areas = []
            for code in codes:
                if code in area_map:
                    meta = area_map[code]
                    name = meta.get("name", code)
                    # ListTileを使って各地域を表示
                    region_areas.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOCATION_ON, size=20),
                            title=ft.Text(name, size=14),
                            on_click=lambda e, c=code, n=name: on_area_click(c, n),
                        )
                    )

            if region_areas:
                # ExpansionTileで地域グループを作成
                tiles.append(
                    ft.ExpansionTile(
                        title=ft.Text(region_name, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{len(region_areas)}地域", size=12),
                        affinity=ft.TileAffinity.PLATFORM,
                        controls=region_areas,
                    )
                )

        return tiles

    def load_areas() -> None:
        nonlocal area_name_map
        spinner.visible = True
        set_status("地域情報を読み込み中...")
        page.update()
        try:
            area_map = fetch_area_map()
            area_name_map = {
                code: meta.get("name", code)
                for code, meta in area_map.items()
                if isinstance(meta, dict)
            }

            # ExpansionTileを使った地域選択パネルを作成
            region_tiles = create_region_tiles(area_map)
            region_panel.controls = region_tiles

            set_status("地域情報を読み込みました")
        except Exception as exc:
            set_status(f"地域情報の読み込みに失敗: {exc}", error=True)
        finally:
            spinner.visible = False
            page.update()

    # NavigationRailで画面切り替え
    current_view = ft.Ref[ft.Container]()

    def on_nav_change(e):
        index = e.control.selected_index
        if index == 0:  # 天気予報ビュー
            main_content.content = forecast_view
        elif index == 1:  # 地域選択ビュー
            main_content.content = region_selection_view
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CLOUD_OUTLINED,
                selected_icon=ft.Icons.CLOUD,
                label="天気予報",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MAP_OUTLINED,
                selected_icon=ft.Icons.MAP,
                label="地域選択",
            ),
        ],
        on_change=on_nav_change,
    )

    # 地域選択パネル（ExpansionTile使用）
    region_panel = ft.Column([], scroll=ft.ScrollMode.AUTO, spacing=0)

    region_selection_view = ft.Container(
        content=ft.Column(
            [
                ft.Text("🗾 地域を選択", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                region_panel,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )

    # 天気予報ビュー
    fetch_button = ft.ElevatedButton("天気予報を取得", on_click=on_fetch, icon=ft.Icons.REFRESH)

    forecast_view = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [selected_area_text, fetch_button, spinner],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                ),
                status_text,
                ft.Divider(),
                forecast_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )

    # メインコンテンツ
    main_content = ft.Container(content=forecast_view, expand=True)

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                main_content,
            ],
            expand=True,
        )
    )

    load_areas()


if __name__ == "__main__":
    ft.app(target=main)
