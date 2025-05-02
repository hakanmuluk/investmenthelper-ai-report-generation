from typing import List

from report_ai.components.llms import invoke_parser_llm

from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from report_ai.components.prompts import generateTitles

SYSTEM_PROMPT_1 = (
    "Göreviniz, bir kullanıcı ile bir yapay zeka arasındaki verilen diyalog veya veri alışverişine dayanarak bir şirket hissesinin **finansal analiz raporu** için yapılandırılmış bir iskelet oluşturmaktır. "
    "Amacınız, her veri noktasını tek bir mantıklı bölüme eşlemek—gereksiz tekrarları önleyerek—ve ana hatların hisse senedi analizine tam uyumlu olmasını sağlamaktır.\n\n"

    "1. **Analiz & Kategorize Etme**: Diyaloğu/veriyi gözden geçirerek tüm ilgili gerçekleri, rakamları ve temaları (örn. fiyat hareketleri, finansal oranlar, piyasa dinamikleri) belirleyin. "
    "Bunları yüksek seviyeli finansal konular altında gruplandırın: Şirket Profili, Sektör & Piyasa Bağlamı, Hisse Performansı, Finansal Sağlık, Değerleme, Riskler & Fırsatlar ve Öneriler.\n\n"

    "2. **Bölümleri & Alt Bölümleri Tanımlama**: Her konu için açık bir başlık ve mantıklı alt başlıklar oluşturun. Örneğin:\n"

)

SYSTEM_PROMPT_2 = (
    "3. **Veri Noktalarını Yerleştirme**: Her bir veri noktasını en ilgili olduğu bölümün altına yerleştirin. "
    "Bir nokta birden fazla yere ait görünüyorsa, birincil analitik değerinin en yüksek olduğu bölümü seçin.\n\n"

    "4. **Yinelenmeyi Önleyin**: Her bir gerçek veya rakam için bir kontrol listesi tutun. Bir kez atadıktan sonra, ek bilgi için çapraz referans yapmıyorsanız başka bir yerde tekrar kullanmayın. "
    "Çapraz referans yaptığınızda, orijinal bölümü belirtin (örn. “bkz. Bölüm 4: Finansal Sağlık”).\n\n"

    "5. **Bölüm Yönergeleri Yazın**: Her başlık altında, oraya ait veri veya analizleri gösterecek 2–4 madde halinde ipucu ekleyin. "
    "Örneğin, “• Son 12 aylık gelir büyümesini ve marj trendlerini özetleyin.”\n\n"

    "6. **Giriş & Sonuç**: \n"
    "   - Giriş: Raporun amacını, veri kaynaklarını ve kapsamını belirtin—ayrıntılı rakamlara yer vermeyin.\n"
    "   - Sonuç: Genel bulguyu ve açık Al/Tut/Sat önerisini özetleyin—yeni veri noktaları eklemeyin.\n\n"

    "7. **Gözden Geçirme & İyileştirme**: Bölümler arasında akış ve mantıksal ilerlemeyi sağlayın. "
    "Her veri öğesinin tam olarak bir kez yer aldığını ve ana hatların kapsamlı ancak özlü olduğunu onaylayın.\n\n"

    "Son olarak, net başlıklar (##) ve her bölüm altında madde‑işaretli ipuçları içerecek şekilde iskeleti Markdown formatında çıktılayın."
)




class Section(BaseModel):
    heading: str = Field(...,
                         description="Heading of the section")
    sub_headings: List[str] = Field(...,
                                    description="Sub-headings in the section.")


class ReportSkeleton(BaseModel):
    skeleton: List[Section] = Field(...,
                                    description="Skeleton of the report consisting of all sections")


async def create_prompt(serialized_conversation: str, format_instructions: str, title: str) -> PromptValue:
    titles = generateTitles(title, serialized_conversation)
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_1 + str(titles) + SYSTEM_PROMPT_2),
            HumanMessagePromptTemplate.from_template(
                "{format_instructions}\n{user_prompt}")
        ],
        input_variables=["user_prompt"],
        partial_variables={"format_instructions": format_instructions}
    )
    return prompt.format_prompt(user_prompt=serialized_conversation)


async def design_report_skeleton(title: str, serialized_conversation: str, llm: BaseChatModel | None = None):
    output_parser = PydanticOutputParser(pydantic_object=ReportSkeleton)
    format_instructions = output_parser.get_format_instructions()

    prompt = await create_prompt(serialized_conversation, format_instructions, title)
    parsed_output = await invoke_parser_llm(
        prompt,
        output_parser,
        llm=llm
    )
    skeleton_list: List[Section] = parsed_output.skeleton

    # 3) build one big string, heading + bullets
    lines: List[str] = []
    for sec in skeleton_list:
        lines.append(sec.heading)
        for sub in sec.sub_headings:
            lines.append(sub)

    skeleton_str = "\n".join(lines)
    return parsed_output.dict()['skeleton'], skeleton_str
