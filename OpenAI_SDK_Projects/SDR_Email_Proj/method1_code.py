# Method 1: Orchestrating by Code

import asyncio
import email
from agents import Runner, trace

from main import (
    sales_agent1,
    sales_agent2,
    sales_agent3,
    sales_picker,
    sales_refiner,
    send_message,
)

async def run_method1():
    print("\n" + "=" * 55)
    print("  🔧  METHOD 1: Orchestrating by Code")
    print("=" * 55)

    message = "Write a cold sales email"

    with trace("Method 1 - Code Orchestration"):
        print("\n📝 Step 1: Generating 3 email drafts in parallel...")
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
    outputs = [result.final_output for result in results]

    for i, output in enumerate(outputs):
        print(f"\n--- Draft #{i} ---")
        print(output[:200] + "..." if len(output) > 200 else output)

    print("\n\n🏆 Step 2: Picking the best draft...")
    emails = "Cold sales email:\n\n" + "\n\nEmail:\n\n".join(outputs)
    best = await Runner.run(sales_picker, emails)
    best_email = best.final_output

    print("\n--- Selected Email ---")
    print(best_email[:300] + "..." if len(best_email) > 300 else best_email)

    print("\n\n✨ Step 3: Refining the selected email...")
    refined = await Runner.run(
        sales_refiner, 
        f"please refine this sales email {best_email}",
    )
    refined_email = refined.final_output

    print("\n--- Refined Email ---")
    print(refined_email)

    print("\n\n📤 Step 4: Sending the final email...")

    lines = refined_email.strip().split("\n")
    if lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
    else:
        subject = "A Quick Note from ComplAI"
        body = refined_email

    html_body = f"<html><body>{''.join(f'<p>{line}</p>' for line in body.split(chr(10)) if line.strip())}</body></html>"

    send_message(subject, body, html_body)




    




