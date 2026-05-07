import os
from openai import OpenAI
from crewai import Agent, Task, Crew, Process, LLM


def analyze_blueprint(api_key, image_base64, text_prompt, mime_type="image/png"):
    """
    使用小米 MiMo 原生接口进行多模态图纸解析
    """
    client = OpenAI(api_key=api_key, base_url="https://api.xiaomimimo.com/v1")

    # 构建多模态请求体
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"你是一个高级机械工程师。请仔细分析这张图纸，提取关键的加工参数、尺寸要求、结构特征。用户的额外描述是：{text_prompt}。请将图纸信息和用户描述整合，输出一份极其详尽的纯文本加工需求报告。"
                },
                {
                    "type": "image_url",
                    # 🌟 修改 4：动态拼接 mime_type
                    "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                }
            ]
        }
    ]

    response = client.chat.completions.create(
        model="mimo-v2-omni",
        messages=messages
    )
    return response.choices[0].message.content


def run_supply_chain_crew(part_description, api_key):
    # 配置小米原生 LLM
    mimo_llm = LLM(
        model="mimo-v2.5-pro",
        api_key=api_key,
        base_url="https://api.xiaomimimo.com/v1"
    )

    # 定义 Agents
    analyst = Agent(
        role='机器人硬件需求分析师',
        goal='分析零件的功能需求、材质要求及加工精度',
        backstory='你擅长将模糊的零件描述转化为专业的加工参数（公差、表面处理等）。',
        llm=mimo_llm,
        verbose=True
    )

    scout = Agent(
        role='供应链开发经理',
        goal='根据技术参数搜寻匹配的加工厂家类型并评估其工艺适配度',
        backstory='你熟悉中国及全球的机械加工产业带，能识别哪些厂家擅长高精度机器人零件。',
        llm=mimo_llm,
        verbose=True
    )

    accountant = Agent(
        role='成本核算工程师',
        goal='估算加工成本、起订量及潜在的物流周期，并生成排版精美的报告',
        backstory='你对材料成本和加工工时非常敏感，擅长用Markdown格式输出清晰的对比表格。',
        llm=mimo_llm,
        verbose=True
    )

    # 定义任务 Tasks
    task1 = Task(
        description=f"深度解析以下已汇总的加工需求：\n\n{part_description}\n\n提取加工材质、精度和关键技术难点。",
        agent=analyst,
        expected_output="一份包含材质、公差和关键参数的技术说明书。"
    )

    task2 = Task(
        description="根据技术说明书，列出3-5家推荐的加工厂家类型（如：深圳某精密五轴加工厂、东莞某3D打印中心等）及其核心优势。",
        agent=scout,
        expected_output="推荐供应商列表及初步的筛选逻辑。"
    )

    task3 = Task(
        description="对上述方案进行成本预估，对比各家厂家的优劣，并整合出一份最终的《机器人零件加工筛选报告》。",
        agent=accountant,
        expected_output="完整的Markdown格式综合报告。"
    )

    # 组建团队并执行
    crew = Crew(
        agents=[analyst, scout, accountant],
        tasks=[task1, task2, task3],
        process=Process.sequential
    )

    # 显式转换为字符串返回
    return str(crew.kickoff())