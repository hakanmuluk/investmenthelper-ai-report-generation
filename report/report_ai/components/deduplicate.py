from report_ai.components.llms import invoke_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

SYSTEM_PROMPT = (
    "Göreviniz TEXT2'yi sadeleştirmek, metnin bütünlüğünü ve tutarlılığını korurken TEXT1 ile örtüşen tüm kısımları kaldırmaktır. Sadece düzenlenmiş TEXT2'yi döndürün. TEXT1 ile TEXT2 arasında örtüşme yoksa, TEXT2'yi değişmeden döndürün.\n"
    "Aşağıdaki yönergeleri kesinlikle uyguladığınızdan emin olun:\n"
    "- **İlk Okuma**: Hem TEXT1'i hem de TEXT2'yi dikkatlice okuyun. Metin, şekiller, tablolar ve kodlar da dahil olmak üzere tüm ayrıntılara dikkat edin.\n"
    "- **Yinelenen İçeriği Belirleme**: TEXT2'de, TEXT1'de yer alan yinelenen veya çok benzer içerikleri tespit edin; tekrarlanan cümleler, yeniden ifade edilen fikirler, şekiller, tablolar ve kod bölümleri dahildir.\n"
    "- **Yinelenenleri Kaldırmak İçin Düzenleme**:\n"
    "   - **Yeniden İfade Etme**: TEXT1'deki aynı fikirleri aktaran TEXT2 içindeki cümlelerin kelime dizimini değiştirin, orijinal anlamı koruyarak.\n"
    "   - **Gereksiz Tekrarları Kaldırma**: Değer katmayan, yinelenen TEXT2 bölümlerini çıkarın.\n"
    "   - **Şekil/Tablo Ayarlamaları**: TEXT2, TEXT1 ile aynı şekil veya tabloyu içeriyorsa ve yeni içgörüler sunmuyorsa bunları değiştirin veya kaldırın.\n"
    "- **Mermaid Şekil Standartlaştırmasını Sağlayın**: Tüm mermaid diyagram kodlarını `<div class='mermaid'>` HTML öğesi içinde tutun. Standart etiket ve sınıf kullanılmalıdır.\n"
    "- **Tutarlılığı Sağlayın**: Düzenlemelerden sonra TEXT2'nin mantıksal akışını kontrol edin. Bilgi kesintisiz ve akıcı bir şekilde ilerlemelidir.\n"
    "- **Boş Bölümlerden Kaçının**: Düzenleme sonrası TEXT2'de boş veya anlamsız bölümlerin olmadığını doğrulayın.\n"
    "- **Gereksiz Eklentilerden Kaçının**: TEXT2'de önceden bulunmayan 'Final Thoughts' veya 'Conclusion' gibi yeni bölümler eklemeyin.\n"
    "- **Son Kontrol**: TEXT2'yi son bir kez gözden geçirerek tüm yinelenenlerin kaldırıldığını ve metnin net, amaç odaklı olduğunu doğrulayın. Düzenlenmiş TEXT2'de 'TEXT1' veya 'TEXT2' kelimelerinin açıkça kullanılmaması çok önemlidir."
)

USER_PROMPT_TEMPLATE = "### TEXT1 ###\n{__TEXT1__}\n\n---------------\n\n ### TEXT2 ###\n{__TEXT2__}"


async def deduplicate_section(section_content: str, serialized_report: str, llm: BaseChatModel | None = None):
    USER_PROMPT = USER_PROMPT_TEMPLATE.format_map({
        '__TEXT1__': serialized_report,
        '__TEXT2__': section_content
    })

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        HumanMessage(
            content=USER_PROMPT
        ),
    ]
    response = await invoke_llm(messages, llm=llm)
    return response.content
