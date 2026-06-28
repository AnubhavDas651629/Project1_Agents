# Method 2: Orchestrating by LLMs (via Tools)

from agents import Runner,trace, Agent

from main import (
    sales_agent1,
    sales_agent2,
    sales_agent3,
    sales_refiner,
    send_email_tool,
    MODEL_NAME,
)


async def run_method2():
    print("\n" + "=" * 55)
    print("  🤖  METHOD 2: Orchestrating by LLMs (via Tools)")
    print("=" * 55)

    description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email"

    tool1 = sales_agent1.as_tool(
        tool_name="sales_email_writer_1",
        tool_description=description,
    )
    tool2 = sales_agent2.as_tool(
        tool_name="sales_email_writer_2",
        tool_description=description,
    )
    tool3 = sales_agent3.as_tool(
        tool_name="sales_email_writer_3",
        tool_description=description,
    )

    refine_tool = sales_refiner.as_tool(
        tool_name="refine_email",
        tool_description="use this tool to refine and improve a sales email. Pass in the draft email text",
    )

    all_tools = [tool1, tool2, tool3, refine_tool]

    instructions = """
You are a Sales Manager at ComplAI. Your goal is to find, refine, and send the single best cold sales email.
"""

    task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.

2. Evaluate and Select: Review the drafts and choose the single best email using your judgment.

3. Refine: Use the refine_email tool to polish and improve the winning email.

4. Send: Use the send_email_tool to send the refined email. Only send 1 email.
"""
    sales_manager = Agent(
        name="Sales Manager",
        instructions=instructions,
        tools=all_tools,
        model=MODEL_NAME,
    )

    print("\n🚀 Running the Sales Manager agent...\n")
    print("   The LLM will autonomously:")
    print("   1. Call 3 writers")
    print("   2. Pick the best")
    print("   3. Refine it")
    print("   4. Send it")
    print()

    with trace("Method 2 - Via LLMS(tools)"):
        result = await Runner.run(sales_manager, task)

    print(f"\n📋 Sales Manager final response:\n{result.final_output}")
