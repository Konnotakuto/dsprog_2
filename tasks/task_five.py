import requests
import flet as ft

AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
WEATHER_ICON_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/img/{code}.svg"

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
    """天気予報を画像付きで表示するビューを作成"""
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
        if len(wind_text) > 20:
            wind_text = f"{wind_text[:20]}..."

        # 天気アイコン
        weather_icon = None
        if weather_code:
            icon_url = WEATHER_ICON_TEMPLATE.format(code=weather_code)
            weather_name = WEATHER_CODE_MAP.get(weather_code, weather_text)
            weather_icon = ft.Image(
                src=icon_url,
                width=100,
                height=100,
                fit=ft.ImageFit.CONTAIN,
            )
        else:
            weather_name = weather_text
            weather_icon = ft.Text("☁️", size=100)

        # 予報カード
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(time_label, size=16, weight=ft.FontWeight.BOLD),
                        weather_icon,
                        ft.Text(weather_name, size=14, text_align=ft.TextAlign.CENTER),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("💧", size=16),
                                ft.Text(f"降水確率: {pop_text}", size=12),
                            ],
                            spacing=5,
                        ),
                        ft.Row(
                            [
                                ft.Text("🌬️", size=16),
                                ft.Text(f"風: {wind_text[:20]}...", size=12),
                            ],
                            spacing=5,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=16,
                width=250,
            ),
        )
        forecast_cards.append(card)

    return ft.Column(forecast_cards, spacing=16, scroll=ft.ScrollMode.AUTO)


def main(page: ft.Page) -> None:
    page.title = "JMA 天気予報ビューワー"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 24
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    area_dropdown = ft.Dropdown(
        label="地域を選択",
        width=360,
        options=[],
        disabled=True,
    )
    fetch_button = ft.ElevatedButton("天気予報を取得", disabled=True)
    status_text = ft.Text("")
    spinner = ft.ProgressRing(visible=False)

    # 予報表示用のコンテナ
    forecast_container = ft.Container()

    area_name_map: dict[str, str] = {}

    def set_status(message: str, *, error: bool = False) -> None:
        status_text.value = message
        status_text.color = "red" if error else "black"
        page.update()

    def load_areas() -> None:
        nonlocal area_name_map
        spinner.visible = True
        set_status("地域情報を読み込み中...")
        page.update()
        try:
            area_map = fetch_area_map()
            sorted_items = sorted(area_map.items(), key=lambda item: item[1].get("name", ""))
            area_dropdown.options = [
                ft.dropdown.Option(
                    key=meta.get("code", code),
                    text=meta.get("name", code)
                )
                for code, meta in sorted_items
                if isinstance(meta, dict)
            ]
            area_name_map = {
                meta.get("code", code): meta.get("name", code)
                for code, meta in area_map.items()
                if isinstance(meta, dict)
            }
            area_dropdown.disabled = False
            fetch_button.disabled = False
            set_status("地域情報を読み込みました")
        except Exception as exc:
            set_status(f"地域情報の読み込みに失敗: {exc}", error=True)
        finally:
            spinner.visible = False
            page.update()

    def on_fetch(_):
        code = area_dropdown.value
        if not code:
            set_status("地域を選択してください", error=True)
            return
        spinner.visible = True
        set_status("天気予報を取得中...")
        forecast_container.content = None
        page.update()
        try:
            forecast = fetch_forecast(code)
            area_name = area_name_map.get(code, "Unknown")
            forecast_container.content = create_forecast_view(forecast, area_name, code)
            set_status("天気予報を取得しました")
        except Exception as exc:
            forecast_container.content = ft.Text(
                f"エラー: {exc}",
                color="red"
            )
            set_status(f"天気予報の取得に失敗: {exc}", error=True)
        finally:
            spinner.visible = False
            page.update()

    fetch_button.on_click = on_fetch

    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [area_dropdown, fetch_button, spinner],
                        spacing=16,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                status_text,
                ft.Divider(),
                forecast_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )

    load_areas()


if __name__ == "__main__":
    ft.app(target=main)
