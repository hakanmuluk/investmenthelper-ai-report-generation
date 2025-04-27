from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import json



load_dotenv()  # reads .env into os.environ

apiKey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apiKey)

def generateQuestions(userQuery, questionCount):
    today_str = date.today().strftime("%d.%m.%Y")
    prompt = f"""
    Sen bir araştırma asistanısın. Görevin, bir rapor amacını bilgi toplamak için {questionCount} basit, genel soruya dönüştürmek. Her soru net ve kendi başına anlaşılır olmalı. Rapor oluşturma sorgularında birden fazla şirket adı geçse bile, üretilen her soru yalnızca tek bir şirket hakkında bilgi talep etmeli (aynı soruda birden fazla şirketten kaçın). Soruları mümkün olduğunca genel tut; belirli bir finansal gösterge sormaktan kaçın ve “... hakkında bilgi ver” kalıbını kullanarak geniş bilgi al. Eğer rapor oluşturma sorgusunda bir zaman aralığı belirtilmişse (örneğin "son 6 ay", "son bir yıl"), her soruya bu zaman aralığını ekle.

    İşte birkaç örnek.

    Örnek 1:  
    Rapor oluşturma sorgusu: “Koç Holding’in son 2 aydaki finansal performansını analiz et”  
    Çıktı:
    {{
    "questions": [
        "Koç Holding’in son 2 aydaki genel performansı hakkında bilgi ver?",
        "Koç Holding’in son 2 ayda faaliyet alanları hakkında bilgi ver?",
        "Koç Holding’in son 2 ayda piyasa ortamını nasıl değerlendirirsin?",
        "Koç Holding’in son 2 aydaki stratejik öncelikleri nelerdir?",
        "Koç Holding’in son 2 ayda sektörel konumunu anlatır mısın?",
        "Koç Holding’in son 2 aydaki uzun vadeli hedefleri nelerdir?",
        "Koç Holding’in son 2 ayda güncel risk faktörlerini paylaşır mısın?",
        "Koç Holding’in son 2 aydaki büyüme fırsatlarını nasıl görüyorsun?",
        "Koç Holding’in son 2 ayda yönetim stratejisini açıklar mısın?",
        "Koç Holding’in son 2 aydaki genel trendleri değerlendirir misin?"
    ]
    }}

    Örnek 2:  
    Rapor oluşturma sorgusu: “Vestel’in son 6 aylık gelir trendini değerlendir”  
    Çıktı:
    {{
    "questions": [
        "Vestel’in son 6 aydaki genel performansı hakkında bilgi ver?",
        "Vestel’in son 6 ayda faaliyet alanları hakkında bilgi ver?",
        "Vestel’in son 6 ayda sektördeki konumunu nasıl görüyorsun?",
        "Vestel’in son 6 ayda stratejik önceliklerini paylaşır mısın?",
        "Vestel’in son 6 ayda piyasa ortamını değerlendirir misin?",
        "Vestel’in son 6 ayda büyüme fırsatlarını anlatır mısın?",
        "Vestel’in son 6 ayda genel risk faktörlerini açıklar mısın?",
        "Vestel’in son 6 ayda yönetim stratejisini nasıl değerlendirirsin?",
        "Vestel’in son 6 ayda uzun vadeli hedeflerini paylaşır mısın?",
        "Vestel’in son 6 ayda sektörel trendleri nasıl yorumlarsın?"
    ]
    }}

    Örnek 3:  
    Rapor oluşturma sorgusu: “Sabancı Holding ve Pegasus’un son bir yıllık performansını karşılaştır”  
    Çıktı:
    {{
    "questions": [
        "Sabancı Holding’in son bir yıldaki genel performansı hakkında bilgi ver?",
        "Pegasus’un son bir yıldaki genel performansı hakkında bilgi ver?",
        "Sabancı Holding’in son bir yıldaki sektördeki konumunu nasıl görüyorsun?",
        "Pegasus’un son bir yıldaki faaliyet alanlarını anlatır mısın?",
        "Sabancı Holding’in son bir yıldaki stratejik önceliklerini paylaşır mısın?",
        "Pegasus’un son bir yıldaki büyüme fırsatlarını nasıl değerlendirirsin?",
        "Sabancı Holding’in son bir yıldaki risk faktörlerini açıklar mısın?",
        "Pegasus’un son bir yıldaki piyasa ortamını nasıl yorumlarsın?",
        "Sabancı Holding’in son bir yıldaki uzun vadeli hedeflerini paylaşır mısın?",
        "Pegasus’un son bir yıldaki yönetim stratejisini anlatır mısın?"
    ]
    }}

    Şimdi şu adımları izle:

    1. Aşağıdaki “Rapor oluşturma sorgusu”nu oku.  
    2. Tam olarak {questionCount} basit, genel, kendi başına anlaşılır soru yaz.  
    3. Çıktıyı yalnızca aşağıdaki JSON yapısında, ekstra metin olmadan ver:

    {{
    "questions": [
        "Soru 1…",
        …,
        "Soru {questionCount}…"
    ]
    }}

    Unutma: her soru yalnızca tek bir şirket hakkında olmalı, soruları mümkün olduğunca genel tutarak “... hakkında bilgi ver” kalıbını kullan ve eğer sorguda zaman aralığı varsa (“son 6 ay”, “son bir yıl” gibi), bu zaman aralığını her soruya ekle!

    Bugünün tarihi: {today_str}

    Rapor oluşturma sorgusu:  
    "{userQuery}"
    """

    response = client.chat.completions.create(model = "gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.30)
    data = json.loads(response.choices[0].message.content)

    # extract the list under the "questions" key
    questions_list = data["questions"]

    return questions_list

def generateMoreQuestions(userQuery, questionCount, answeredQuestions, unanswerableQuestions):
    today_str = date.today().strftime("%d.%m.%Y")
    prompt = f"""Sen bir araştırma asistanısın ve bir raporu iyileştirmeye yardımcı oluyorsun. Sana şunlar verildi:

    -Cevapları zaten verilmiş soruların listesi.

    -Cevaplanamayan soruların listesi.

    -Üretilmesi istenen yeni soru sayısı n.

    Talimatlar:
    --Her yeni soru yalnızca bir şirketi içermeli.
    --Genel sorular sormaya çalış, fazla spesifik sorular sorma!

    Görevin: tam olarak n adet, basit ve kendi başına anlaşılır sorular üretmek. (a) Cevaplanan veya cevaplanamayan listelerdeki soruları tekrarlamamak, (b) Orijinal kullanıcı sorusuyla ilgili, kullanıcı sorusunun yanıtlanmasına yardımcı olacak sorular yazmak. Tekrarlıyorum, genel sorular sor!

    Ek metin olmadan sadece aşağıdaki geçerli JSON formatında çıktı ver:
    {{ "questions": [ "Yeni soru 1…", "Yeni soru 2…", …, "Yeni soru n…" ] }}
    Örnek:

    Orijinal kullanıcı sorusu: “Koç Holding son 2 ayda nasıl performans gösterdi, analiz et?”

    Cevaplanmış sorular: [ "Koç Holding’in son iki aydaki gelirleri hakkında bilgi ver?", "Son iki ayda Koç Holding’in kârı hakkında bilgi ver?" ]
    Cevaplanamayan sorular: [ "Koç Holding’in bu dönemde hisse fiyatı nasıl seyretti?", "Koç Holding son iki ayda ne kadar temettü ödedi?" ]
    n = 3
    Beklenen JSON çıktısı: {{ "questions": [ "Koç Holding'in gelir kaynakları hakkında bilgi ver?", "Koç Holding’in son 2 aydaki harcamaları hakkında bilgi ver?", "Koç Holding’in nakit akışını son iki ayda etkileyen dış faktörler hakkında bilgi ver?" ] }}
    LLM için Talimatlar:
    Aşağıdaki üç girdiyi oku.
    Tam olarak n adet yeni, basit ve kendi başına anlaşılır soru üret.
    Cevaplanan veya cevaplanamayan listelerdeki soruları tekrarlama.
    Yalnızca yukarıda belirtilen geçerli JSON formatında çıktı ver.
    Orijinal Kullanıcı Sorusu: {userQuery}
    Cevaplanmış sorular: {answeredQuestions} 
    Cevaplanamayan sorular: {unanswerableQuestions}
    n: {questionCount}
    Bugünün tarihi: {today_str}
    unutma, her yeni soru yalnızca bir şirketi içermeli.
    Ve son olarak: daha genel sorular sormaya çalış ve çok spesifik olmayan bilgiler almaya çalış!"""

    response = client.chat.completions.create(model = "gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.30)
    data = json.loads(response.choices[0].message.content)

    # extract the list under the "questions" key
    questions_list = data["questions"]

    return questions_list

def generateTitles(reportTopic, userConversationsString):
    prompt = f"""Aşağıdaki “Rapor Konusu” ve “Chatbot–Kullanıcı Konuşması” bilgilerini kullanarak, finansal raporunuz için 6–7 başlık ve her bir başlığın 2–3 alt başlık olarak düzenlenmiş biçimde üretin. Çıktı, her satırı “- Başlık (Alt1, Alt2, …)” formatında olacak şekilde, düzenli bir madde listesi olarak sunulmalıdır.
    Önemli: Başlıkları ve alt başlıkları oluştururken, hem Rapor Konusu hem de Chatbot–Kullanıcı Konuşması metinlerine çok dikkat edin. Oluşturduğunuz başlıklar ve alt başlıklar;
    Rapor konusuyla doğrudan ilgili olmalı
    Sohbetten elde edilen spesifik bilgileri yansıtmalı
    Bu bilgilerle detaylı olarak yazılabilecek nitelikte olmalıdır
    Girdi formatı Rapor Konusu: {{RAPOR_KONUSU}} Chatbot–Kullanıcı Konuşması: {{KONUŞMA_METNI}}
    Çıktı formatı
    Başlık1 (Alt başlık A, Alt başlık B, …)
    Başlık2 (Alt başlık A, Alt başlık B, …) …
    Başlık6 (Alt başlık A, Alt başlık B, …)
    Örnek 1
    Rapor Konusu: Koç Holding’in 2025 İlk Çeyrek Finansal Performansı Chatbot–Kullanıcı Konuşması: Kullanıcı: “2025 ilk çeyrekte gelirimiz nasıl değişti?” Chatbot: “Önceki yıl aynı döneme göre %12 artış, Segsan %8 büyüme gösterdi.”
    Beklenen Çıktı:
    Giriş & Kapsam (Rapor Amacı, Kapsam Sınırları)
    Gelir Performansı (Toplam Gelir, Yıllık Yüzde Değişim)
    Segment Analizi (Segsan Satışları, Diğer Ana Segmentler)
    Nakit Akışı (Operasyonel Nakit, Serbest Nakit Akışı)
    Karlılık Oranları (Brüt Kar Marjı, Net Kar Marjı)
    Sonuç & Öneriler (Stratejik Öneriler, Karar Kriterleri)
    Örnek 2
    Rapor Konusu: Sabancı Holding’in ESG Stratejisi Chatbot–Kullanıcı Konuşması: Kullanıcı: “Sabancı’nın karbon ayak izi hedefleri nelerdir?” Chatbot: “2030’a kadar %30 azaltım, 2050’ye kadar net sıfır.”
    Beklenen Çıktı:
    Giriş & Kapsam (Raporun Amacı, Tanımlar)
    ESG Yönetim Çerçevesi (Hedefler, Politikalar)
    Karbon Ayak İzi Analizi (Mevcut Durum, 2030 Hedefi)
    Yenilenebilir Enerji Yatırımları (Güneş, Rüzgar Kapasitesi)
    Finansal Etki & Maliyet Analizi (Yatırım Maliyeti, Geri Dönüş Süresi)
    Riskler & Fırsatlar (Regülasyon Değişiklikleri, Yeşil Tahvil İhracı)
    Sonuç 
    Örnek 3
    Rapor Konusu: Turkcell’i finansal açıdan analiz et ve hisse almalı mıyım söyle Chatbot–Kullanıcı Konuşması: Kullanıcı: "Turkcell'in son 4 çeyrekteki gelir artışı ve borçluluk oranı hakkında bilgi verir misin?" Chatbot: "Son 4 çeyrekte toplam gelir ortalama %6 artış gösterdi. Net borç/EBITDA oranı 2.5 seviyesinde." Kullanıcı: "Hisse alımı konusunda ne önerirsin?" Chatbot: "Büyüme trendi sağlam, hisse şu an iskontolu görünüyor."
    Beklenen Çıktı:
    Giriş & Kapsam (Rapor Amacı, İncelenen Dönem)
    Gelir & Büyüme Analizi (Çeyreklik Gelir Değişimi, Yıllık Büyüme)
    Borçluluk & Finansal Kaldıraç (Net Borç/EBITDA, Kısa Vadeli Borç)
    Karlılık Oranları (Brüt Kar Marjı, F/K Oranı)
    Nakit Akışı & Yatırım (Operasyonel Nakit Akışı, Sermaye Harcamaları)
    Riskler & Fırsatlar (Döviz Kuru Riski, Abone Artışı Trendleri)
    Sonuç & Öneri (Al/Tut/Sat Kararı)
    Örnek 4
    Rapor Konusu: Türk Hava Yolları ve Pegasus’u finansal açıdan karşılaştır Chatbot–Kullanıcı Konuşması: Kullanıcı: "THY ile Pegasus'un yolcu sayıları ve gelirleri nasıl karşılaştırılıyor?" Chatbot: "2024'te THY 60 milyon, Pegasus 40 milyon yolcu taşıdı. Gelirleri sırasıyla 15 ve 8 milyar TL." Kullanıcı: "Hisse performansları ve kârlılık oranlarını da öğrenebilir miyim?" Chatbot: "THY F/K 8, net kar marjı %10; Pegasus F/K 12, net kar marjı %8."
    Beklenen Çıktı:
    Giriş & Kapsam (Amaç, Karşılaştırılan Dönem)
    Yolcu & Gelir Karşılaştırması (Yolcu Sayısı, Toplam Gelir)
    Hisse Performansı Karşılaştırması (Fiyat Geçmişi, Volatilite)
    Kârlılık & Oran Karşılaştırması (Net Kar Marjı, F/K Oranı)
    Nakit Akışı & Finansal Sağlık (Operasyonel Nakit, Borçluluk)
    Riskler & Fırsatlar (Yakıt Maliyetleri, Regülasyon Riski)
    Sonuç & Öneri (Hisse Al/Tut/Sat Kararı)

    Rapor Konusu: {reportTopic}
    Kullanıcı-chatbot konuşmaları:
    {userConversationsString}

    Giriş ve Sonuç eklemeyi unutma!"""

    response = client.chat.completions.create(model = "gpt-4.1-mini", messages=[{"role": "user", "content": prompt}], temperature=0.30)
    titles = response.choices[0].message.content
    return titles

def generateReportName(reportQuery):
    prompt = f"""Şimdi sana bir finansal rapor hazırlama isteği vereceğim, bu isteğe uygun, 4-5 kelimelik bir başlık seç:
    {reportQuery}"""
    response = client.chat.completions.create(model = "gpt-4.1-mini", messages=[{"role": "user", "content": prompt}], temperature=0.30)
    return response.choices[0].message.content

