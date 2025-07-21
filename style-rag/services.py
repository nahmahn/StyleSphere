import json
from groq import Groq
from . import config
from .models import ConversationState, ItemMetadata
from .agents import AgentToolkit

# --- ORCHESTRATOR INITIALIZATION ---
# This creates a single instance of our toolkit for the whole application
agent_toolkit = AgentToolkit(config)
orchestrator_llm = Groq(api_key=config.GROQ_API_KEY)


def orchestrator_agent(query: str, history: list, state: ConversationState, image_bytes: bytes = None) -> tuple[str, list[ItemMetadata], ConversationState]:
    """
    The main orchestrator that decides which agent/tool to use, now aware of images.
    """
    print("Orchestrator Agent activated.")
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    state_str = state.model_dump_json(indent=2)
    image_provided_str = "Yes" if image_bytes else "No"

    prompt = f"""
    You are the Orchestrator, a master AI agent that directs a team of specialized fashion agents.
    Your job is to analyze the user's request, which may include an image, and decide which tool to use.

    **Image Provided by User:** {image_provided_str}
    **Your Tools:**
    1.  `fashion_search(query: str)`: Search the clothing catalog. If an image is provided, this tool automatically uses it for visual search. Use for requests like "find something similar to this image", "build an outfit with this", "show me red dresses".
    2.  `fashion_knowledge(query: str)`: For general fashion questions that are not about our catalog and DO NOT involve an image. E.g., "what's in style this season?".
    3.  `chit_chat(query: str)`: For greetings and non-fashion related conversation.

    **Conversation State:** {state_str}
    **Conversation History:** {history_str}
    **User's Latest Message:** "{query}"

    **Instructions:**
    1.  **Analyze Intent:** If an image is provided, the intent is almost always `fashion_search`. The `tool_query` should be the user's text, which gives context to the image search (e.g., "find pants to match this").
    2.  **Choose ONE Tool:** Based on the intent, decide which single tool is most appropriate.
    3.  **Formulate Query for Tool:** Create the precise query to send to the chosen tool.
    4.  **Output JSON:** Your response MUST be a JSON object with "tool_to_use" (e.g. "fashion_search") and "tool_query" (the user's text to give context). You can also include an "updated_state" object.
    """
    
    try:
        completion = orchestrator_llm.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-70b-8192",
            temperature=0.1, response_format={"type": "json_object"}
        )
        plan = json.loads(completion.choices[0].message.content)
        tool_to_use = plan.get("tool_to_use")
        tool_query = plan.get("tool_query", query)
        new_state = ConversationState(**plan.get("updated_state")) if plan.get("updated_state") else state
    except Exception as e:
        print(f"Orchestrator planning failed: {e}"); return "I'm having trouble understanding. Could you rephrase?", [], state

    items_found = []
    final_response_text = ""
    if tool_to_use == "fashion_search":
        items_found = agent_toolkit.fashion_search_agent(tool_query, image_bytes)
        if not items_found: final_response_text = f"I looked for '{tool_query}' but couldn't find a close match. Try another search?"
        else: final_response_text = f"I found some great options for '{tool_query}'! Here are the top results."
    elif tool_to_use == "fashion_knowledge": final_response_text = agent_toolkit.fashion_knowledge_agent(tool_query)
    elif tool_to_use == "chit_chat": final_response_text = agent_toolkit.chit_chat_agent(tool_query)
    else: final_response_text = "I'm not sure which tool to use. Can you be more specific?"
    
    return final_response_text, items_found, new_state