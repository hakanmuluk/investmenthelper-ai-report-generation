from typing import Dict
from report_ai.components.llms import invoke_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

SECTION_SYSTEM_PROMPT_TEMPLATE = (
    "Göreviniz, bir Finansal Raporun {__SECTION_HEADING__} bölümünü geliştirmektir. Size, bölüm gereksinimlerinin "
    "bir taslağı ve bölümünüzle ilgili bilgi ve içgörüler içeren bir kullanıcı ile bir yapay zeka arasındaki diyalog "
    "alışverişi sağlanacaktır. İçeriğinizi zenginleştirmek için bu diyaloğu özenle kullanın. Bu bölüm, aşağıdaki alt "
    "başlıklar altında listelenen anahtar noktalar etrafında yapılandırılacaktır: {__SUB_SECTION_HEADINGS__}. "
    "Sadece verilen alt başlıklarla içerik oluşturmaya sıkı sıkıya bağlı kalın.\n"
    "{__SECTION_HEADING__} bölümünü oluştururken, lütfen aşağıdaki öğeleri etkin bir şekilde dahil ettiğinizden emin olun:\n"
    "- **Yapılandırılmış İçerik**: Bölümünüzü belirtilen alt başlıklara göre düzenleyin. Her alt başlık, bölümün ayrı bir "
    "yönünü ele almalı ve bilgileri mantıklı, tutarlı bir şekilde sunmalıdır.\n"
    "**Anahtar Hususlar**:\n"
    "- **HTML Biçimlendirme**: Belgenizi yapılandırmak için HTML öğeleri kullanın. Okunabilirlik ve düzeni artırmak için "
    "başlıklar, listeler, vurgulamalar ve tablolar gibi uygun HTML sözdizimini kullanın. Her zaman <body> öğesi ile başlayın. "
    "<html>, <meta> gibi başlangıç HTML öğeleri eklemenize gerek yoktur. Bölüm başlıkları için <h2>, alt başlıklar için <h3> "
    "etiketlerini kullanın.\n"
    "{__ADDITIONAL_GUIDELINES__}"
    "Unutmayın, amaç yalnızca bilgilendirici olmak değil, aynı zamanda ilgi çekici ve görsel olarak çekici bir bölüm "
    "oluşturmaktır. Bunu başarmak için metin içeriğinizi {__CONTENT_ADJECTIVE__} dengede tutun ve bölümünüzün titizlikle "
    "düzenlenmiş ve biçimlendirilmiş olduğundan emin olun.\n\n"
    "Mevcut raporun şu anki hali:\n{__SERIALIZED_REPORT__}\n\n ÖNEMLİ: Unutmayın, mevcut rapordaki içerik veya bilgilerin "
    "hiçbirini tekrar etmemeniz çok, çok önemlidir. Buna tüm rakamlar, tablolar ve metinler dahildir. Bu konuda ekstra dikkatli "
    "olun; dünyanın kaderi buna bağlı."
)


additional_guidelines_with_figures = (
    "- **Tabloların Kullanımı**: Mümkün olduğunca verileri ve bulguları tablolara dönüştürerek sentezleyin. Tablolar açıkça etiketlenmeli ve sundukları verileri özetleyen başlıklar içermelidir. Tabloları numaralandırmayın.\n"
)



async def design_section(serialized_conversation: str, section_dict: Dict, serialized_report: str,
                         llm: BaseChatModel | None = None) -> (str, str):
    if section_dict['heading'] in ["Introduction", "Conclusion"]:
        SYSTEM_PROMPT = SECTION_SYSTEM_PROMPT_TEMPLATE.format_map({
            "__SECTION_HEADING__": section_dict['heading'],
            "__SUB_SECTION_HEADINGS__": "; ".join(section_dict['sub_headings']),
            "__SERIALIZED_REPORT__": serialized_report,
            "__ADDITIONAL_GUIDELINES__": "",
            "__CONTENT_ADJECTIVE__": "well"
        })
    else:
        SYSTEM_PROMPT = SECTION_SYSTEM_PROMPT_TEMPLATE.format_map({
            "__SECTION_HEADING__": section_dict['heading'],
            "__SUB_SECTION_HEADINGS__": "; ".join(section_dict['sub_headings']),
            "__SERIALIZED_REPORT__": serialized_report,
            "__ADDITIONAL_GUIDELINES__": additional_guidelines_with_figures,
            "__CONTENT_ADJECTIVE__": "with visual elements"
        })

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        HumanMessage(
            content=serialized_conversation
        ),
    ]
    response = await invoke_llm(messages, llm=llm)
    html_content = response.content
    return html_content.replace('&gt;', '>')  # Fix errors when arrows are generated incorrectly by LLM
