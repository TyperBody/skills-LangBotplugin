#!/usr/bin/env python3
"""
Subprocess runner for Planner ReAct loop.
This script runs in a separate process to allow parallel execution and immediate stop.
"""

import sys
import os
import asyncio
import json
import base64
import logging

# Configure logging - output to stderr (NOT stdout) for debugging
# stdout is reserved for passing results back to parent process
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Output to stderr, not stdout
)
logger = logging.getLogger(__name__)


def print_output(msg: str):
    """Print output to stdout (will be captured by parent)"""
    print(msg, flush=True)


async def run_planner(args: dict):
    """Run the planner in a subprocess"""
    import asyncio
    from components.tools.planner import PlannerExecutor

    task = args["task"]
    max_iterations = args["max_iterations"]
    llm_model_uuid = args["llm_model_uuid"]
    config = args.get("config", {})
    task_id = args.get("task_id", "unknown")

    print_output(f"[{task_id}] Starting planner task: {task[:50]}...")

    # Import the plugin to get access to invoke_llm
    # We need to initialize it properly
    from main import LangTARS

    plugin = LangTARS()
    plugin.config = config.copy()
    await plugin.initialize()

    # Also set config on the helper
    helper_plugin = LangTARS()
    helper_plugin.config = config.copy()
    await helper_plugin.initialize()

    # Create executor and run
    executor = PlannerExecutor()

    try:
        async for result in executor.execute_task_streaming(
            task=task,
            max_iterations=max_iterations,
            llm_model_uuid=llm_model_uuid,
            plugin=plugin,
            helper_plugin=helper_plugin,
            session=None,
            query_id=0
        ):
            print_output(result)

        print_output(f"\n[{task_id}] Task completed.")

    except Exception as e:
        print_output(f"\n[{task_id}] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python planner_subprocess.py <base64_encoded_args>")
        sys.exit(1)

    args_b64 = sys.argv[1]

    try:
        args_json = base64.b64decode(args_b64).decode('utf-8')
        args = json.loads(args_json)
    except Exception as e:
        print(f"Error decoding arguments: {e}")
        sys.exit(1)

    await run_planner(args)


if __name__ == "__main__":
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

    asyncio.run(main())
