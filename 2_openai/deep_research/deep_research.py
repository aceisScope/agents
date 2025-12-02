import gradio as gr
from dotenv import load_dotenv
from agents import Runner, trace, gen_trace_id

from research_manager import ResearchManager
from question_agent import question_agent

load_dotenv(override=True)


async def get_clarification_questions(query: str):
    """First step: ask question_agent for clarifying questions."""
    thinking_msg = "🧠 Thinking of clarifying questions to focus the research..."
    # Initial placeholder / status
    yield (
        thinking_msg,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )

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
    )


async def run_research(query: str, questions_md: str, answer1: str, answer2: str, answer3: str):
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

    trace_id = gen_trace_id()
    with trace("Research trace", trace_id=trace_id):
        # Surface trace URL as first chunk
        yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
        async for chunk in ResearchManager().run(research_input):
            yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research (with Clarifying Questions)")

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
        inputs=query_textbox,
        outputs=[questions_md, answer1_box, answer2_box, answer3_box, run_button],
    )
    # Also trigger on Enter in the query box
    query_textbox.submit(
        fn=get_clarification_questions,
        inputs=query_textbox,
        outputs=[questions_md, answer1_box, answer2_box, answer3_box, run_button],
    )

    # Step 2: run the full deep research using query + answers
    run_button.click(
        fn=run_research,
        inputs=[query_textbox, questions_md, answer1_box, answer2_box, answer3_box],
        outputs=report,
    )

ui.launch(inbrowser=True)

