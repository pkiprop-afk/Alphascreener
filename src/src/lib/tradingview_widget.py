import streamlit.components.v1 as components

def render_tradingview_widget(symbol: str, interval: str = "D", height: int = 520) -> None:
    html = f"""
    <div class=\"tradingview-widget-container\" style=\"height:{height}px;width:100%\">
      <div id=\"tradingview_chart\" style=\"height:{height}px;width:100%\"></div>
      <script type=\"text/javascript\" src=\"https://s3.tradingview.com/tv.js\"></script>
      <script type=\"text/javascript\">
        new TradingView.widget({{
          \"autosize\": true,
          "symbol": "{symbol.upper()}",
          \"interval\": \"{interval}\",
          \"timezone\": \"Etc/UTC\",
          \"theme\": \"dark\",
          \"style\": \"1\",
          \"locale\": \"en\",
          \"toolbar_bg\": \"#0E1117\",
          \"enable_publishing\": false,
          \"hide_top_toolbar\": false,
          \"hide_legend\": false,
          \"save_image\": false,
          \"container_id\": \"tradingview_chart\"
        }});
      </script>
    </div>
    """
    components.html(html, height=height)

    