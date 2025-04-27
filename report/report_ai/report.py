import os
import asyncio
from tqdm import tqdm
from typing import List, Dict, Literal
from tenacity import retry, stop_after_attempt

from report_ai.common.utils import configs
from report_ai.section import design_section
from report_ai.skeleton import design_report_skeleton
from report_ai.summary import design_executive_summary

from report_ai.components.llms import openai, anthropic
from report_ai.components.convert import html_to_pdf
from report_ai.components.deduplicate import deduplicate_section
from report_ai.components.functions import (
    serialize_conversation,
    sanitize_filename,
    extract_html_body_content,
    compile_full_html,
    add_title_to_html
)

logger = configs.logger


@retry(stop=stop_after_attempt(3))
async def generate_executive_summary_content(serialized_conversation: str, llm: str):
    executive_summary_html = await design_executive_summary(serialized_conversation, llm)
    return extract_html_body_content(executive_summary_html)


@retry(stop=stop_after_attempt(3))
async def generate_section_content(serialized_conversation: str, section: Dict, previous_text: str,
                                   llm: str, apply_dedup: bool = False) -> (str, str):
    section_html = await design_section(serialized_conversation, section, previous_text, llm)
    if apply_dedup:
        section_html = await deduplicate_section(section_html, previous_text, llm)
    return extract_html_body_content(section_html)


async def generate_report(serialized_conversation: str, report_skeleton: List[Dict], references: List[str],
                          llm: str, apply_section_dedup: bool) -> (str, str):
    # Initialize lists to hold HTML and text sections of the report
    html_sections, text_sections = [], []

    html_executive_summary, _ = await generate_executive_summary_content(
        serialized_conversation, llm=llm
    )

    for section in tqdm(report_skeleton, desc="Generating report..."):
        # Combine all previously generated text sections into one string
        previous_text = '\n'.join(text_sections)
        # Generate the content for the current section in both HTML and text formats
        html_section, text_section = await generate_section_content(
            serialized_conversation, section, previous_text, llm=llm, apply_dedup=apply_section_dedup
        )

        # Append the generated HTML and text content to their respective lists
        html_sections.append(html_section)
        text_sections.append(text_section)

    # Concatenate all HTML sections into a single HTML document
    html_report = '\n'.join(html_sections)

    # Compile the complete HTML report, incorporating references, and return it
    return await compile_full_html(
        html_content={"executive_summary": html_executive_summary, "report": html_report},
        references=references
    )


async def run_generation_async(userQuery, conversation: List[Dict],
                               title_dict: Dict[str, str],
                               user_name: str,
                               request_id: int | None,
                               llm: Literal['gpt', 'claude'] | None,
                               apply_section_dedup: bool):
    # 1) configure LLM
    match llm:
        case 'claude':
            llm_instance = anthropic[openai[os.getenv('CLAUDE_MODEL', 'claude-3-opus')]]
        case _:
            llm_instance = openai[os.getenv('GPT_MODEL', 'gpt-4-turbo')]
    logger.info(f"Using LLM: {llm}")

    # 2) prepare unique filename suffix
    sanitized_user  = sanitize_filename(user_name)
    sanitized_title = sanitize_filename(title_dict["title"])
    # include request_id if provided
    suffix_parts = [part for part in (str(request_id) if request_id is not None else None,
                                      sanitized_user,
                                      sanitized_title) if part]
    unique_suffix = "_".join(suffix_parts)

    # 3) serialize conversation & design skeleton
    serialized_conversation, references = await serialize_conversation(conversation)
    report_skeleton = await design_report_skeleton(
        userQuery,
        serialized_conversation,
        llm=llm_instance
    )

    # 4) generate HTML sections
    html_exec_summary, html_report = await generate_report(
        serialized_conversation,
        report_skeleton,
        references,
        llm_instance,
        apply_section_dedup
    )

    # 5) write out the two HTML files with unique names
    exec_filename = f"executive_summary_{unique_suffix}.html"
    report_filename = f"report_{unique_suffix}.html"
    exec_path = os.path.join(configs.assets_dir, exec_filename)
    report_path = os.path.join(configs.assets_dir, report_filename)

    for content, path in [(html_exec_summary, exec_path), (html_report, report_path)]:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    # 6) prepare title HTML pieces, also uniquely named
    title_src = os.path.join(configs.assets_dir, 'title.html')
    temp_title = os.path.join(configs.assets_dir, f"temp_title_{unique_suffix}.html")
    await add_title_to_html(
        title_info=title_dict,
        user_name=user_name,
        html_title_path=title_src,
        output_path=temp_title
    )

    # 7) convert to PDF with a unique name
    pdf_filename = f"{sanitized_user}_{sanitized_title}_{request_id or ''}.pdf"
    pdf_path = os.path.join(configs.reports_dir, pdf_filename)
    await html_to_pdf(
        html_file_executive_summary=exec_path,
        html_file_content=report_path,
        html_file_title=temp_title,
        html_file_disclaimer=os.path.join(configs.assets_dir, 'disclaimer.html'),
        html_file_end=os.path.join(configs.assets_dir, 'end.html'),
        output_path=pdf_path
    )

    # 8) clean up temporary HTML files
    for tmp in (exec_path, report_path, temp_title):
        try:
            os.remove(tmp)
        except OSError:
            logger.warning(f"Could not remove temp file: {tmp}")

    logger.info(f"PDF report generated and saved to {pdf_path}")
    return pdf_path



def run_generation(conversation: List[Dict], title_dict: Dict[str, str], user_name: str, request_id: int | None = None,
                   llm: Literal['gpt', 'claude'] = 'gpt', apply_section_dedup: bool = True):
    asyncio.run(run_generation_async(conversation, title_dict, user_name, request_id, llm, apply_section_dedup))
