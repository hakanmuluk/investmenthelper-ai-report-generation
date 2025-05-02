from report_ai.section import additional_guidelines_with_figures
from report_ai.components.llms import invoke_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

SUMMARIZE_CONVERSATION_SYSTEM_PROMPT_TEMPLATE = (
    "Finansal bilgileri özetleme konusunda uzman biri olarak göreviniz, sağlanan bir kullanıcı ile bir yapay zeka arasındaki diyalog alışverişinden elde edilen temel ayrıntıları sentezlemek ve yoğunlaştırmaktır. "
    "Amacınız, konuşmadaki tüm mesajlardan gelen verileri entegre etmek ve C düzeyindeki yöneticiler, kritik karar vericiler ve Borsa İstanbul yatırımcılarından oluşan hedef kitlenize kusursuzca hitap eden, tekrarlar veya geniş tanımlamalar içermeyen odaklı bir özet oluşturmaktır. "
    "Her kelimeyi değerli kılın ve birleşim, sıkıştırma ile bilgi verici olmayan ifadelerin çıkarılması yoluyla yer açın. "
    "Özet, kısa ancak kendi kendine yeterli olmalı; örneğin diyalog alışverişlerine bakmadan kolaylıkla anlaşılmalıdır. "
    "Hedef kitleniz zaten bir dil modeli olduğunuzu ve yetenekleriniz ile sınırlamalarınızı biliyor, bu yüzden bunları hatırlatmayın. "
    "Onlar genel olarak etik konulara zaten aşinadır, bu yüzden bunları da hatırlatmanıza gerek yok. "
    "Özetiniz, ana bulguları açıkça detaylandırmalı ve hiçbir bölüm başlığı içermemelidir. "
    "Yalnızca özetlenmiş metni döndürün"
)

EXECUTIVE_SUMMARY_SYSTEM_PROMPT_TEMPLATE = (
    "Bir yapay zeka uzmanısınız, özellikle ayrıntılı şirket hisse analiz raporları için özlü, veri‑odaklı yönetici özetleri hazırlama konusunda eğitim aldınız. "
    "Hedef kitleniz, AI doğanızı hatırlatan ifadeler veya genel etik uyarılar olmaksızın net, uygulanabilir içgörüler talep eden C düzey yöneticiler, portföy yöneticileri ve Borsa İstanbul yatırımcılarından oluşmaktadır.\n\n"

    "Özetinizi **Markdown** formatında bu yapıyı kullanarak oluşturun:\n")
    

EXECUTIVE_SUMMARY_SYSTEM_PROMPT_TEMPLATE_2 = ("**Yönergeler:**\n"
    "- Her bölüm için en fazla 3–4 madde kullanın; her madde kesin odaklı olmalı ve verilerle desteklenmelidir.\n"
    "- Anahtar rakamları veya oranları satır içinde kalın yazı tipiyle vurgulayın (örn. **F/K: 12.5x**, **Temettü Verimi: 3.2%**).\n"
    "- Dili analitik, nesnel ve klişelerden arındırılmış tutun (‘rapor tartışıyor’ gibi ifadelere yer vermeyin).\n"
    "- Özetiniz bağımsız olmalı: bir okuyucu ek bağlam olmadan tam öneriyi kavrayabilmelidir.\n\n"

    "Rapor özetiniz aşağıdaki kurallara uymalı:\n"
    "- **HTML Biçimlendirmesi**: Belgenizi yapılandırmak için HTML öğeleri kullanın. Okunabilirlik ve düzen için başlıklar, listeler, vurgulama ve tablolar gibi uygun HTML sözdizimini kullanın. Her zaman <body> öğesi ile başlayın. <html>, <meta> gibi başlangıç HTML öğeleri eklemenize gerek yok. Bölüm başlıkları için <h2>, alt başlıklar için <h3> etiketlerini kullanın. 'Rapor Özeti' başlığını içeren bir <h2> etiketi ile başlayın.\n"
    "- Her bölüm en fazla 3–4 önemli madde içermelidir. Ayrıca oluşturulan içerik analitik, yüksek düzeyde ilgili, nesnel ve ayrıntılarla dolu olmalıdır.\n"
    "{__ADDITIONAL_GUIDELINES__}"
    "Genel geçer ifadelerden ve aşırı kullanılan klişelerden kaçının ve sağlanan verilerin kapsamlı analizi temelinde benzersiz içgörüler sunmaya çalışın."
)



async def generate_conversation_summary(serialized_conversation: str, llm):
    messages = [
        SystemMessage(
            content=SUMMARIZE_CONVERSATION_SYSTEM_PROMPT_TEMPLATE
        ),
        HumanMessage(
            content=serialized_conversation
        ),
    ]
    response = await invoke_llm(messages, llm=llm)
    return response.content


async def design_executive_summary(skeleton_str, serialized_conversation: str, llm: BaseChatModel | None = None):
    prompt = EXECUTIVE_SUMMARY_SYSTEM_PROMPT_TEMPLATE + skeleton_str + EXECUTIVE_SUMMARY_SYSTEM_PROMPT_TEMPLATE_2
    SYSTEM_PROMPT = prompt.format_map({
        "__ADDITIONAL_GUIDELINES__": additional_guidelines_with_figures
    })
    USER_PROMPT = await generate_conversation_summary(serialized_conversation, llm)

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        HumanMessage(
            content=USER_PROMPT
        ),
    ]
    response = await invoke_llm(messages, llm=llm)
    html_content = response.content
    return html_content.replace('&gt;', '>')  # Fix errors when arrows are generated incorrectly by LLM
