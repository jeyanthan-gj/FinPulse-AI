import asyncio
import sys
import uuid

from guardrails import MarketGuardrails
from agents.research_synthesis_agent.agent import (
    create_research_synthesis_supervisor,
)


def print_status(text: str, color: str = "36"):
    """Print an ANSI colored live progress line."""
    print(f"\033[{color}m{text}\033[0m", flush=True)


async def main():
    print("=" * 70)
    print("   Indian Market Research AI")
    print("=" * 70)
    print()
    print("Research-only AI powered by Deep Agents + MCP")
    print("• Type 'new' to start a fresh topic")
    print("• Type 'exit' or 'quit' to stop.")
    print("=" * 70)
    print()

    # ------------------------------------------------------------
    # Create the main Research Synthesis Deep Agent
    # ------------------------------------------------------------
    print("Initializing research agent...")
    agent = await create_research_synthesis_supervisor()
    print("Research agent ready.\n")

    # ------------------------------------------------------------
    # Single-user persistent session configuration
    # ------------------------------------------------------------
    current_session = "demo_session_1"
    session_config = {"configurable": {"thread_id": current_session}}

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Command to start a fresh topic clean for demo recording
        if user_input.lower() in {"new", "clear", "reset"}:
            current_session = f"demo_session_{uuid.uuid4().hex[:6]}"
            session_config = {"configurable": {"thread_id": current_session}}
            print_status(f"✓ [Started fresh research topic: {current_session}]\n", color="32")
            continue

        # Check Colang Guardrails (0-token intercept for greetings, thanks, off-topic)
        guarded_response = MarketGuardrails.check_input_rails(user_input)
        if guarded_response:
            print()
            print("=" * 70)
            print("AI:")
            print("=" * 70)
            print(guarded_response)
            print()
            continue

        print()

        try:
            final_text_chunks = []

            # Stream step events so the terminal always shows real-time progress
            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": user_input}]},
                config=session_config,
                version="v2",
            ):
                ev = event.get("event")
                meta = event.get("metadata", {})
                current_agent = meta.get("lc_agent_name") or meta.get("run_name") or "supervisor"

                # 1. When a task or tool starts
                if ev == "on_tool_start":
                    tool_name = event.get("name")
                    inp = event.get("data", {}).get("input", {})

                    if tool_name == "task" and isinstance(inp, dict):
                        subagent = inp.get("subagent_type", "Specialist")
                        desc = inp.get("description", "")
                        summary = (desc[:65] + "...") if len(desc) > 65 else desc
                        print_status(f"⚡ [Delegating to {subagent}] -> {summary}", color="33")
                    else:
                        print_status(f"   ↳ [{current_agent}] Running tool: {tool_name}", color="36")

                # 2. When a tool completes
                elif ev == "on_tool_end":
                    tool_name = event.get("name")
                    if tool_name != "task":
                        print_status(f"   ✓ [{current_agent}] {tool_name} completed", color="32")
                    else:
                        print_status("✓ [Specialist research completed]", color="32")

                # 3. Collect final assistant response chunks
                elif ev == "on_chat_model_stream":
                    if current_agent == "research-synthesis-supervisor":
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content") and isinstance(chunk.content, str):
                            final_text_chunks.append(chunk.content)

            # Print final synthesized response once all agents finish
            final_response = "".join(final_text_chunks).strip()
            print()
            print("=" * 70)
            print("AI Research Report:")
            print("=" * 70)
            if final_response:
                print(final_response)
            else:
                print("Research finished, but no summary content was returned.")
            print()

        except Exception as e:
            print(f"\n\033[31mError while processing request: {e}\033[0m\n")


if __name__ == "__main__":
    asyncio.run(main())
