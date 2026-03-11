import gradio as gr
import pandas as pd

# ==========================================
# 1. 系統設定與連結區
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ltze3OKi-Z0LMfBO143EFYEMxWl4td4HCYqJOQ0_oK8/export?format=csv&gid=959653312"
FORM_URL = "https://docs.google.com/forms/d/1YE_IUaZ8-QmoDd1ylVVvq0v-YSWkmo18GWwMsjAewlY/viewform"

# ==========================================
# 2. 核心邏輯：抓取資料、過濾欄位與排序
# ==========================================
def fetch_and_sort_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)

        # 依據總分由高到低排序
        if 'AUTO_TotalScore_100' in df.columns:
            df = df.sort_values(by='AUTO_TotalScore_100', ascending=False)

        # 🎯 精準對齊你指定的欄位清單 (已去除多餘的空白與換行)
        target_columns = [
            '時間戳記',
            '需求單位 / 團隊名稱',
            '需求名稱（請用一句話描述）',
            '目前遇到的問題是什麼？（請用 3 句內描述）',
            '如果不解決，最直接的代價是什麼？（延遲 / 錯誤 / 成本 / 客戶抱怨 / 合規風險）',
            '這題完成後，你期待改善哪一種「主要效益」？',
            '你預估可節省多少時間？（請填：每次省__分鐘 × 每月__次）',
            '若能換算成金額，預估每月節省/創造金額（TWD，選填）',
            '你如何判斷「成功」？請列 3 個驗收條件',
            'AUTO_GateResult',
            'AUTO_TotalScore_100',
            'AUTO_Track',
            'AUTO_Action'
        ]

        # 安全過濾：比對目前 df 中有的欄位，避免因表單名稱微調導致 KeyError 報錯
        available_columns = [col for col in target_columns if col in df.columns]
        df = df[available_columns]

        return df

    except Exception as e:
        return pd.DataFrame({"系統提示": [f"無法讀取資料，請確認試算表權限。錯誤細節: {str(e)}"]})

# ==========================================
# 3. 前端介面設計 (Dashboard UI)
# ==========================================
# 🎨 視覺升級：使用 Ocean 主題
custom_theme = gr.themes.Ocean(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate"
)

# 💡 修改這裡：將 theme 放回 Blocks 中 (維持原本設定)
with gr.Blocks(theme=custom_theme, title="程曦資訊 | AI 轉型加速器") as demo:

    # --- 🎨 頁首：品牌視覺與團隊介紹 ---
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 10px; margin-bottom: 15px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em;">程曦資訊集團｜AI 轉型加速器</h1>
        <h3 style="color: #e0f2fe; margin-top: 5px;">創新研發部 · AI 解題小組</h3>
    </div>
    """)

    gr.Markdown("""
    **【我們的使命】** 以最短時間將 AI 能力轉換為可用成果，幫公司節省工時、降低錯誤率，並建立可複用的 AI 解法資產庫！
    *📌 核心節奏：每週只收斂並交付 1 題，維持穩定產能與節拍。*
    """)

    # --- 頁籤分類區塊 ---
    with gr.Tabs():

        # 🟢 頁籤 1：提案 Intake
        with gr.TabItem("📝 1. 提出需求 (Intake)"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📱 掃描或點擊連結填寫表單")
                    gr.Markdown(f"[👉 **點擊這裡直接進入表單**]({FORM_URL})")
                    gr.Image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={FORM_URL}", label="手機掃碼提交", width=250)

                with gr.Column(scale=2):
                    gr.Markdown("### 🚨 提案避坑指南 (Do / Don't)")
                    gr.HTML("""
                    <div style="background-color: #f0fdf4; padding: 15px; border-left: 5px solid #22c55e; border-radius: 5px; margin-bottom: 10px;">
                        <b>✅ 歡迎提交這樣的案子：</b><br>
                        • <b>問題夠具體：</b> 請用「公式」描述最痛點：【目前做什麼事】＋【遇到什麼困難】＋【導致什麼損失(時間/金錢)】。<br>
                        • <b>資料已備妥：</b> 能提供至少 5 筆以上的真實 Sample 與期望輸出。<br>
                        • <b>擁抱改變：</b> 團隊願意為了自動化改變現有操作流程。
                    </div>
                    <div style="background-color: #fef2f2; padding: 15px; border-left: 5px solid #ef4444; border-radius: 5px;">
                        <b>❌ 請避免這類提案：</b><br>
                        • 純粹抱怨但無法衡量「不解決的代價（如：延遲 / 成本）」的問題。<br>
                        • 不願意安排 30 分鐘教學或改變現有流程。
                    </div>
                    """)

        # 🔵 頁籤 2：排隊看板
        with gr.TabItem("📊 2. 排隊看板 (Backlog)"):
            gr.Markdown("""
            ### 📥 許願池與評分排序
            根據 Impact (40)、Adoption (25)、Feasibility (20)、Reusability (15) 計算總分。 👉 規則：80分以上進入戰略題
            """)

            with gr.Row():
                refresh_btn = gr.Button("🔄 立即刷新", variant="primary")

            data_grid = gr.Dataframe(value=fetch_and_sort_data(), interactive=False, wrap=True)

            refresh_btn.click(fn=fetch_and_sort_data, outputs=data_grid)

        # 🟡 頁籤 3：本週進行中專案
        with gr.TabItem("🏃‍♂️ 3. 進行中專案 (Current Sprint)"):
            gr.Markdown("### 📍 本週解題進度")
            gr.HTML("""
            <div style="border: 2px solid #3b82f6; border-radius: 8px; padding: 20px; background-color: #eff6ff;">
                <h4 style="margin-top: 0; color: #1e3a8a;">專案名稱：[請手動填寫本週專案]</h4>
                <ul>
                    <li><b>提出單位：</b> [請手動填寫]</li>
                    <li><b>預計交付：</b> 本週五</li>
                    <li><b>目前狀態：</b> <span style="background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.9em;">Day 2 - 初版 MVP Demo</span></li>
                </ul>
            </div>
            """)

        # 🟣 頁籤 4：已結案資產庫
        with gr.TabItem("🏆 4. 已結案資產庫 (Solution Assets)"):
            gr.Markdown("### 📦 企業 AI 資產沉澱\n我們不只解題，更留下可複用的資產。歡迎各部門直接參考取用！")

            with gr.Accordion("📄 專案 1：遠端文件簽署", open=False):
                gr.Markdown("""
                **結案日：**

                **問題描述：**

                **核心痛點：**

                **解題模式：** Google Esignature

                **可複用模組：** [Esignature 模板連結](#)

                **教學資源：** [YouTube 教學影片連結](#) / [SOP 文件](#)
                """)

           

            with gr.Accordion("📈 專案 2：投資損益週報表自動運算產生", open=False):
                gr.Markdown("""
                **結案日：** 2026/03/06

                **問題描述：** 目前老大的股票投資分散於 6 個不同的證券與銀行帳戶。為了有效追蹤投資績效，每週必須定期彙整各帳戶的對帳單與銀行存款明細，並計算出當週的持股成本、總市值與總損益。
                  
                **核心痛點：**
                  - 跨券商資料格式不一，清理成本極高
                  - 人工計算繁瑣，且易受雜訊干擾
                  - 市價更新缺乏效率

                **解題模式：** LLM Prompt 模板

                **可複用模組：** [Prompt 模板連結](https://www.canva.com/design/DAHDC2JwAwk/lV8lJhCq_Cc4_2BjL70Scg/edit)
                """)


    # ==========================================
    # 4. 全自動更新指令 (Gradio 5.0 專用寫法)
    # ==========================================
    # 網頁一載入時先抓取一次
    demo.load(fn=fetch_and_sort_data, outputs=data_grid)

    # 使用 gr.Timer(60) 來取代原本的 every=60
    timer = gr.Timer(60)
    timer.tick(fn=fetch_and_sort_data, outputs=data_grid)

# ==========================================
# 5. 啟動 Dashboard
# ==========================================
if __name__ == "__main__":
    # 💡 修改這裡：將 theme 從 launch 中拿掉，避免 TypeError
    demo.launch(debug=True)
