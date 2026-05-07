import streamlit as st
import os
import glob
import base64
from datetime import datetime
from agents_logic import run_supply_chain_crew, analyze_blueprint

st.set_page_config(page_title="MiMo 机器人供应链助手", layout="wide")

# --- 侧边栏：配置与历史记录 ---
with st.sidebar:
    st.header("⚙️ API 配置")
    mimo_api_key = st.text_input("输入你的 MiMo API Key", type="password")
    st.info("已接入小米 MiMo V2.5 多模态视觉模型")

    st.divider()

    st.header("📁 历史筛选报告")
    # 获取当前目录下所有的 md 文件
    md_files = glob.glob("*.md")
    # 过滤掉可能的 README 文件
    md_files = [f for f in md_files if f.lower() != "readme.md"]

    if md_files:
        md_files.sort(reverse=True)  # 按时间倒序
        selected_file = st.selectbox("选择历史报告查看", ["-- 请选择 --"] + md_files)

        if selected_file != "-- 请选择 --":
            st.markdown(f"**正在查看: `{selected_file}`**")
            with open(selected_file, "r", encoding="utf-8") as f:
                with st.expander("展开报告内容", expanded=True):
                    st.markdown(f.read())
    else:
        st.write("暂无历史生成的报告。")

# --- 主界面：需求输入与生成 ---
st.title("🤖 机器人零件加工厂家筛选系统")
st.subheader("支持图纸视觉识别 (Vision) + 多智能体协作 (Multi-Agent)")

# 核心输入区
col1, col2 = st.columns([2, 1])

with col1:
    part_input = st.text_area(
        "📝 描述你的零件需求（文字）：",
        placeholder="例如：我需要加工一个机器人关节连接件，要求轻量化，使用铝合金 7075，精度要求在 0.02mm 以内，数量 50 件。",
        height=150
    )

with col2:
    # 🌟 修改 1：放开格式限制
    uploaded_file = st.file_uploader("🖼️ 上传参考图纸 (PNG/JPG)", type=["png", "jpg", "jpeg"])
    image_base64 = None
    mime_type = "image/png"  # 设定一个默认的 mime 类型

    if uploaded_file is not None:
        # 获取图片后缀并动态判断类型
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg']:
            mime_type = "image/jpeg"
        else:
            mime_type = "image/png"

        # 转换为 Base64
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        st.image(image_bytes, caption="已加载图纸", use_container_width=True)

if st.button("🚀 开始 AI 协同筛选", type="primary"):
    if not mimo_api_key:
        st.error("请先在左侧输入 API Key！")
    elif not part_input and not uploaded_file:
        st.warning("请输入文字需求或上传图纸。")
    else:
        final_description = part_input

        with st.status("正在进行 AI 分析...", expanded=True) as status:
            # 步骤 1：如果有图片，先调用多模态解析
            if image_base64:
                st.write("👁️ 正在利用 MiMo 视觉模型解析机械图纸...")
                try:
                    vision_analysis = analyze_blueprint(mimo_api_key, image_base64, part_input, mime_type)
                    st.write("✅ 图纸解析完成，已提取关键参数。")
                    # 将图纸解析结果作为详细需求传给 CrewAI
                    final_description = f"【用户原始需求】\n{part_input}\n\n【图纸视觉解析结果】\n{vision_analysis}"
                except Exception as e:
                    st.error(f"图纸解析失败: {e}")
                    st.stop()

            # 步骤 2：启动多智能体团队
            st.write("🤖 专家团队已接管，正在进行技术分析与供应链匹配...")
            try:
                final_report = run_supply_chain_crew(final_description, mimo_api_key)
                status.update(label="✅ 筛选报告生成完毕！", state="complete", expanded=False)
            except Exception as e:
                st.error(f"分析过程中发生错误: {e}")
                st.stop()

        # --- 结果展示与自动保存 ---
        st.divider()
        st.header("📋 最终筛选报告")
        st.markdown(final_report)

        # 自动保存为 Markdown 文件到本地
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_report)
        st.toast(f"报告已自动保存为 {filename}，可在侧边栏查看。")