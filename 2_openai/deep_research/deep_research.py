import gradio as gr
from dotenv import load_dotenv
from agents import Runner, trace, gen_trace_id

from research_manager import ResearchManager
from question_agent import question_agent

load_dotenv(override=True)


async def get_clarification_questions(query: str, trace_id_state: gr.State):
    """First step: ask question_agent for clarifying questions."""
    # Generate trace_id if not already set
    if trace_id_state is None:
        trace_id_state = gen_trace_id()
    
    thinking_msg = "🧠 Thinking of clarifying questions to focus the research..."
    # Initial placeholder / status
    yield (
        thinking_msg,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        trace_id_state,  # Pass trace_id through state
    )

    # Run question_agent within the trace context
    # Use the same trace name and ID so it appears in the same trace
    with trace("Deep Research Session", trace_id=trace_id_state):
        result = await Runner.run(question_agent, query)
        clarifications = result.final_output.questions

    questions_md = "To help focus the research, please answer these questions:\n\n"
    questions_md += "\n\n".join(
        f"{i + 1}. {item.question}\n\n_Reason: {item.reason}_"
        for i, item in enumerate(clarifications)
    )

    # Show the questions markdown, three answer boxes, and enable the research button
    yield (
        questions_md,
        gr.update(visible=True, label="Answer 1"),
        gr.update(visible=True, label="Answer 2"),
        gr.update(visible=True, label="Answer 3"),
        gr.update(visible=True, value="Run research"),
        trace_id_state,  # Pass trace_id through state
    )


async def run_research(query: str, questions_md: str, answer1: str, answer2: str, answer3: str, trace_id_state: gr.State):
    """Second step: run the full deep research using the query + answers."""
    research_input = f"Original query: {query}"
    if questions_md:
        research_input += f"\n\nClarifying questions:\n{questions_md}"

    if answer1:
        research_input += f"\n\nAnswer 1: {answer1}"
    if answer2:
        research_input += f"\n\nAnswer 2: {answer2}"
    if answer3:
        research_input += f"\n\nAnswer 3: {answer3}"

    # Use the same trace_id from the clarification step
    trace_id = trace_id_state if trace_id_state else gen_trace_id()
    
    # Continue the same trace - use the exact same trace name and ID
    with trace("Deep Research Session", trace_id=trace_id):
        # Surface trace URL as first chunk
        yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
        
        # Pass the trace_id to ResearchManager so it uses the same trace
        async for chunk in ResearchManager().run(research_input, trace_id=trace_id):
            yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research (with Clarifying Questions)")
    
    # State to store trace_id across both steps
    trace_id_state = gr.State(value=None)

    with gr.Row():
        with gr.Column(scale=1):
            query_textbox = gr.Textbox(label="What topic would you like to research?")
            ask_button = gr.Button("Get clarifying questions", variant="secondary")

            questions_md = gr.Markdown(label="Clarifying questions")

            answer1_box = gr.Textbox(label="Answer 1", visible=False)
            answer2_box = gr.Textbox(label="Answer 2", visible=False)
            answer3_box = gr.Textbox(label="Answer 3", visible=False)

            run_button = gr.Button("Run research", variant="primary", visible=False)

        with gr.Column(scale=1):
            report = gr.Markdown(label="Research report")

    # Step 1: get clarification questions
    ask_button.click(
        fn=get_clarification_questions,
        inputs=[query_textbox, trace_id_state],
        outputs=[questions_md, answer1_box, answer2_box, answer3_box, run_button, trace_id_state],
    )
    # Also trigger on Enter in the query box
    query_textbox.submit(
        fn=get_clarification_questions,
        inputs=[query_textbox, trace_id_state],
        outputs=[questions_md, answer1_box, answer2_box, answer3_box, run_button, trace_id_state],
    )

    # Step 2: run the full deep research using query + answers
    run_button.click(
        fn=run_research,
        inputs=[query_textbox, questions_md, answer1_box, answer2_box, answer3_box, trace_id_state],
        outputs=report,
    )

ui.launch(inbrowser=True)

