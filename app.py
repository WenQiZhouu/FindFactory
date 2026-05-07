import streamlit as st
from agents_logic import run_supply_chain_crew

st.set_page_config(page_title="MiMo 机器人供应链助手", layout="wide")

st.title("🤖 机器人零件加工厂家筛选系统")
st.subheader("基于小米 MiMo v2.5-pro 多智能体协作")

# 侧边栏配置
with st.sidebar:
    st.header("API 配置")
    mimo_api_key = st.text_input("输入你的 MiMo API Key", type="password")
    st.info("该项目已适配小米 MiMo Orbit 百万亿 Token 计划。")

# 主界面输入
part_input = st.text_area(
    "描述你的零件需求：",
    placeholder="例如：我需要加工一个机器人关节连接件，要求轻量化，使用铝合金 7075，精度要求在 0.02mm 以内，数量 50 件。"
)

if st.button("开始 AI 协同筛选"):
    if not mimo_api_key:
        st.error("请先在左侧输入 API Key！")
    elif not part_input:
        st.warning("请输入零件描述。")
    else:
        with st.status("🚀 AI 团队正在协作中...", expanded=True) as status:
            st.write("需求分析师正在审图...")
            # 调用逻辑
            final_report = run_supply_chain_crew(part_input, mimo_api_key)
            status.update(label="✅ 报告生成完毕！", state="complete", expanded=False)

        # 展示结果
        st.divider()
        st.header("📋 最终筛选报告")
        st.markdown(final_report)

        # 导出功能
        st.download_button(
            label="下载报告 (Markdown)",
            data=str(final_report),
            file_name="mimo_report.md",
            mime="text/markdown"
        )