import os
from crewai import Agent, Task, Crew, Process
from crewai import LLM  # 🌟 关键修改：改用 CrewAI 原生的 LLM 类


def run_supply_chain_crew(part_description, api_key):
    # 1. 定义小米原生的联网搜索工具配置
    mimo_search_tool_config = [
        {
            "type": "web_search",
            "web_search": {
                "force_search": False,
                "max_keyword": 5,
                "limit": 8
            }
        }
    ]

    # 2. 🌟 关键修改：使用 CrewAI 原生 LLM 进行初始化
    mimo_llm = LLM(
        model="mimo-v2.5-pro",
        api_key=api_key,
        base_url="https://api.xiaomimimo.com/v1",
        # 透传小米专属的联网搜索配置
        extra_body={
            "tools": mimo_search_tool_config
        }
    )

    # 3. 定义 Agents
    analyst = Agent(
        role='机器人硬件需求分析师',
        goal='分析零件的功能需求、材质要求（如铝合金/不锈钢）及加工精度',
        backstory='你擅长将模糊的零件描述转化为专业的加工参数（公差、表面处理等）。',
        llm=mimo_llm,
        verbose=True
    )

    scout = Agent(
        role='供应链开发经理',
        goal='利用互联网搜索，根据技术参数搜寻匹配的加工厂家（如CNC加工、3D打印或注塑）',
        backstory='你熟悉中国及全球的机械加工产业带，能识别哪些厂家擅长高精度机器人零件。',
        llm=mimo_llm,
        verbose=True
    )

    accountant = Agent(
        role='成本核算工程师',
        goal='估算加工成本、起订量及潜在的物流周期，并生成报告',
        backstory='你对材料成本和加工工时非常敏感，能给出合理的预算区间。',
        llm=mimo_llm,
        verbose=True
    )

    # 4. 定义任务 (Tasks)
    task1 = Task(
        description=f"深度解析用户需求：{part_description}。提取加工材质、精度和数量。",
        agent=analyst,
        expected_output="一份包含材质、公差和关键参数的技术说明书。"
    )

    task2 = Task(
        description="根据技术说明书，通过搜索引擎，列出3-5家真实的推荐加工厂家类型及其核心优势。务必包含厂家名称和所在地。",
        agent=scout,
        expected_output="推荐供应商列表及初步的筛选逻辑。"
    )

    task3 = Task(
        description="对上述方案进行成本预估，对比各家厂家的优劣，并整合出一份最终的《机器人零件加工筛选报告》。",
        agent=accountant,
        expected_output="完整的Markdown格式综合报告。"
    )

    # 5. 组建团队
    crew = Crew(
        agents=[analyst, scout, accountant],
        tasks=[task1, task2, task3],
        process=Process.sequential
    )

    return crew.kickoff()