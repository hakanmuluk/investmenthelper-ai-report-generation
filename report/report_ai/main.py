import os
from report_ai.report import run_generation

if __name__ == '__main__':
    conversation = [
        {
            "role": "user",
            "content": "Koç Holding’in genel finansal durumu hakkında bilgi ver?"
        },
        {
            "role": "assistant",
            "content": """A: Verilen belgeler doğrultusunda, Koç Holding A.Ş.'nin 2025 yılı başındaki genel mali durumu hakkında bir genel bakış:

1. Yetkili Sermaye:
- Şirket, yetkili sermayesini 5.000.000.000.000 TL'den 10.000.000.000.000 TL'ye artırdı (Belge 1).
- Bu artış, 16.01.2025 tarihinde Yönetim Kurulu tarafından onaylandı ve 31.12.2029 tarihine kadar tamamen gerçekleştirilmesi planlanıyor.
- Ana Sözleşme buna göre değiştirildi (Belgeler 1 ve 3).

2. Karlılık:
- Sermaye Piyasası Kurulu (SPK) düzenlemelerine göre, mevcut dönem kârı 26.712.683.000 TL, vergi sonrası net mevcut dönem kârı ise 1.306.263.000 TL'dir (Belge 2).
- Yasal/kanuni kayıtlara göre, mevcut dönem kârı daha yüksek olup 36.622.498.332,91 TL, net mevcut dönem kârı ise 35.195.056.460,88 TL'dir (Belgeler 2 ve 5).
- Ödenecek vergiler, SPK ve yasal kayıtlar arasında önemli farklılıklar göstermektedir (32.000.288.000 TL'ye karşı 1.427.441.872,03 TL).
- SPK tarafından önceki yıllara ait herhangi bir zarar kaydedilmemiştir, ancak yasal kayıtlarda küçük zararlar görünmektedir (Belgeler 2 ve 5).

3. Temettü Dağıtımı:
- Yönetim Kurulu, yaklaşık 17,5 milyar TL (tam olarak ifade edildiğinde 17.505.362.626.930 TL) brüt nakit temettü ödemesini onayladı ve bu ödeme 10 Nisan 2025'ten itibaren yapılacaktır (Belgeler 3, 4, 6 ve 7).
- Temettü verimi, A Grubu hisseleri için brüt %688 ve B Grubu hisseleri için brüt %688 (stopaj vergisi sonrası net %584,8) ile oldukça yüksektir (Belge 6).
- Temettü ödemesi, kısmen mevcut yıl vergiye tabi kazançlardan (1,3 milyar TL) ve çoğunlukla birikmiş kazançlardan (16,2 milyar TL) finanse edilmektedir (Belge 7).

4. Özsermaye ve Yedekler:
- Yasal yedekler, sermayenin %20'sine ulaşmış olduğundan, ek bir tahsisata gerek yoktur (Belge 5).
- Önceki yıllara ait ticari zararlar, yasal kayıtlarda mevcut yıl kârları ile telafi edilmektedir (Belge 5).
- Özsermayede enflasyon düzeltme yedekleri, önceki yıllara ait kâr/zarar hesaplarındaki negatif bakiyeleri karşılamak için yeterlidir (Belge 5).

5. Kurumsal Yönetim:
- Yönetim Kurulu, 4 bağımsız yönetim kurulu üyesi dahil 12 üyeden oluşmaktadır ve bir yıl için seçilmektedir (Belge 3).
- Şirketin 2024 yılına ait mali tabloları ve yıllık raporu onaylandı ve Yönetim Kurulu üyeleri o yıl için sorumluluktan muaf tutuldu (Belge 4).

6. İştirakler ve Bağlı Ortaklıklar:
- Koç Holding, finans, tüketici finansmanı, yatırım, sağlık, teknoloji ve ticaret gibi çeşitli sektörlerde önemli yatırımlara sahiptir ve Koç Finansal Hizmetler A.Ş., Koç Finansman A.Ş., Koç Investments B.V., Koç Medical B.V., Koç Sistem Bilgi ve İletişim Hizmetleri A.Ş. ve Koç Yapı Malzemeleri Ticaret A.Ş. gibi bağlı ortaklıklarında önemli ödenmiş sermaye ve sermaye paylarına sahiptir (Belge 8).

Özet:
Koç Holding, 10 trilyon TL'ye iki katına çıkarılmış çok büyük bir yetkili sermaye tabanına sahip, mali açıdan güçlü bir şirkettir. Şirket, yasal kayıtlarda güçlü bir kârlılık bildirmiştir ve önemli bir net dağıtılabilir kâr ile yüksek bir temettü ödeme oranına sahiptir. Şirket, sağlam yedekler bulundurmakta ve çok çeşitli sektörlerde bağlı ortaklıklar portföyüne sahiptir. Yönetim yapısı, icra ve bağımsız yönetim kurulu üyelerinin bir karışımı ile iyi tanımlanmıştır. Genel olarak, Koç Holding mali açıdan sağlıklı görünmekte ve hissedarlara önemli temettüler aracılığıyla değer geri döndürmeye kararlıdır."""
        },
        {
            "role": "Koç Holding’in yıllık gelirleri ve giderleri hakkında genel bir değerlendirme yap?",
            "content": "Koç Holding’in ana iştirakleri hangileri ve her birindeki pay oranları nedir?"
        },
        {
            "role": "assistant",
            "content": """Koç Holding A.Ş.'nin 2024 ve 2025'in başındaki mali bildirimlerine dayanarak, şirketin gelirleri ve giderleri ile ilgili aşağıdaki genel değerlendirme yapılabilir:

1. Karlılık:
- Sermaye Piyasası Kurulu (SPK) düzenlemelerine göre, mevcut dönem karı yaklaşık 26.7 milyar TL olarak bildirilirken, yasal kayıtlarda yaklaşık 36.6 milyar TL gibi çok daha yüksek bir kar gösterilmektedir.
- Vergiler sonrası net mevcut dönem karı, SPK standartlarına göre 1.3 milyar TL, yasal kayıtlara göre ise yaklaşık 35.2 milyar TL'dir.
- SPK ve yasal kayıtlar arasındaki büyük fark, enflasyon muhasebesi ve vergi dikkate alımları gibi muhasebe işlemlerinde veya ayarlamalarında farklılıklar olduğunu göstermektedir.

2. Vergiler ve Yedekler:
- Ödenecek vergiler, SPK'ya göre 32 milyar TL olarak bildirilirken, yasal kayıtlara göre yalnızca yaklaşık 1.4 milyar TL'dir; bu da farklı vergi hesaplama tabanlarını göstermektedir.
- Yasal yedekler, sermayenin %20'sine ulaşmış durumda, bu nedenle ek bir yasal yedek tahsisi gerekmemiştir.
- Önceki yıllara ait zararlar, mevcut karlarla karşılaştırıldığında minimaldir ve buna göre telafi edilmiştir.

3. Temettü Dağıtımı:
- Koç Holding, mevcut yıl vergilendirilebilir kazançları ve tutulan kazançlardan ödenen yaklaşık 17.5 milyar TL tutarında önemli bir temettü dağıtımını onaylamıştır.
- Temettüler, hissedarlara, intifa senedi sahiplerine ve Koç Holding Emekli Sandığı Vakfı'na ödenmiştir.
- Hisse senedi temettüsü dağıtılmamış; tüm temettüler nakit olarak ödenmiştir.

4. Giderler ve Bağışlar:
- Yıl içinde yapılan bağışlar, SPK kılavuzlarına göre yaklaşık 80.6 milyon TL tutarındadır.
- Sağlanan belgelerde işletme giderleri veya satılan malın maliyeti ile ilgili detaylı bir ayrım bulunmadığı için toplam giderlerin kesin bir değerlendirmesi mümkün değildir.

5. Yedekler ve Özsermaye:
- Yasal kayıtlara ve SPK standartlarına göre olağanüstü yedekler ve diğer dağıtılabilir kaynaklar önemli bir seviyededir ve güçlü bir özsermaye tabanını göstermektedir.
- Enflasyon düzeltme yedekleri, önceki yıllara ait kar/zarar hesaplarındaki negatif bakiyeleri telafi etmek için kullanılmıştır.

Özet:
Koç Holding, 2024 yılında önemli net karlar elde ederek ve hissedarlara ve ilgili taraflara büyük bir temettü ödemesi yaparak güçlü bir karlılık göstermiştir. Şirket, önemli yedeklerle birlikte sağlam bir özsermaye pozisyonunu korumaktadır. Ancak, SPK ve yasal kayıtlar arasındaki büyük farklılıklar, farklı muhasebe standartlarının ve enflasyon düzeltmelerinin raporlanan sonuçlar üzerindeki etkisini vurgulamaktadır. Detaylı gider rakamları sağlanmadığı için değerlendirme esas olarak kar, vergi ve temettü verileri üzerine odaklanmaktadır.

Gelirler veya giderler hakkında daha spesifik detaylara ihtiyaç duyulursa, sağlanan belgelerde bunlar mevcut değildir."""
        },
        {
            "role": "user",
            "content": "Koç Holding’in piyasa konumu ve rekabet durumu hakkında bilgi ver?"
        },
        {
            "role": "assistant",
            "content": """Verilen belgeler doğrultusunda, Koç Holding'in piyasa konumu ve rekabet durumu hakkında çıkarılabilecekler şunlardır:

1. **Çeşitli Portföy ve Önemli Sermaye Yatırımları**: Koç Holding, finans, tüketici finansmanı, yatırım, sağlık, teknoloji ve ticaret gibi birçok sektörde geniş ve çeşitlendirilmiş bir portföye sahiptir. Örneğin, Koç Finansal Hizmetler A.Ş. %84,53 oranında önemli bir sermaye payına sahiptir, Koç Medical B.V. tamamen (yüzde 100) mülkiyete sahiptir ve Koç Yapı Malzemeleri Ticaret A.Ş. %92,47 sermaye payına sahiptir. Bu çeşitlilik, çeşitli endüstrilerde güçlü bir piyasa varlığını işaret eder ve rekabet dayanıklılığını artırabilir.

2. **Güçlü Sermaye Temeli ve Yetkili Sermaye Artışı**: Şirket, yetkili sermayesini 5.000.000.000.000 TL'den 10.000.000.000.000 TL'ye artırmıştır ve bu durum 2029'un sonuna kadar geçerlidir. Yetkili sermayenin iki katına çıkması, büyümeyi, yatırımları ve muhtemel satın almaları desteklemek için stratejik bir hamle olduğunu göstermektedir; bu da rekabetçi konumunu güçlendirebilir.

3. **Hissedar Yapısı ve Oy Hakları**: Koç Holding, A ve B grubu hisseleri ile farklı oy hakları uygulamaktadır; A grubu hisseleri, belirli kararlar hariç, çift oy hakkına sahiptir. A grubu hisselerin tamamı, oy haklarının %42,23'ünü temsil eden Aile Danışmanlık Gayrimenkul ve Ticaret A.Ş. tarafından elinde bulundurulurken, en büyük hissedar %43,75'e sahiptir. Bu yapı, kontrol altında ama şeffaf bir yönetim çerçevesi sunarak istikrar ve stratejik yön sağlayabilir.

4. **Şeffaflık ve Kurumsal Yönetim**: Şirket, medya kapsamıyla kamu genel kurul toplantıları, hissedar yapısı, temettü politikaları ve kurumsal yönetim uygulamaları hakkında detaylı açıklamalarla şeffaflığı vurgulamaktadır. Bu şeffaflık, yatırımcı güvenini ve piyasa itibarını artırabilir.

5. **Temettü Ödemeleri ve Finansal Güç**: Koç Holding ve bağlı ortaklıkları, Enerji Yatırımları A.Ş. karlarından 2025'in 1. çeyreği için 2.870.000.000.000 TL'lik avans temettü ve Nisan 2025'te ödenen nakit temettüler gibi aktif temettü dağıtımları yapmaktadır. Düzenli temettü ödemeleri, finansal sağlığı ve hissedar değerine odaklanmayı yansıtır.

6. **İnsan Kaynakları ve Kalite Standartları**: Şirket, eşit fırsatlar, halefiyet planlaması ve çalışan gelişimini sağlayan iyi geliştirilmiş bir insan kaynakları politikası uygulamaktadır. Ayrıca, rekabet avantajını sürdürmek için önemli olan kalite standartlarına ve gizlilik kontrollerine uymaktadır.

7. **Piyasa Varlığı ve Ticaret**: Koç Holding'in hisseleri 1986'dan beri Borsa İstanbul'da, özellikle Yıldız Pazar alt pazarında işlem görmektedir; bu da uzun süreli bir piyasa varlığı ve likiditeyi göstermektedir.

**Özet Yorum**: Koç Holding, güçlü bir sermaye temeli, şeffaf yönetim ve aktif temettü politikası ile iyi kurulmuş, çeşitlendirilmiş bir konglomerat olarak görünmektedir. Yetkili sermayede yapılan stratejik artış ve çeşitlendirilmiş sektörel varlık, onu Türk pazarında ve potansiyel olarak uluslararası alanda rekabetçi bir konuma yerleştirmektedir. Şirketin yönetim yapısı ve şeffaflık taahhüdü, piyasa itibarını ve yatırımcı güvenini daha da desteklemektedir. Ancak, belgelerde piyasa payı, doğrudan rakipler veya sektör sıralamaları gibi belirli rekabet metrikleri sağlanmamıştır.

Daha ayrıntılı bir rekabet analizi veya piyasa payı verisi gerekiyorsa, bu bilgiler sağlanan belgelerde mevcut değildir."""
        },
        
    ]


    title_dict = {
        "title": "A Detailed Analysis of Koç Holding's Financial Performance",
        "sub_title": "Finance"
    }

    run_generation(
        conversation=conversation,
        title_dict=title_dict,
        user_name="Tadic",
        llm=os.getenv('LLM', 'gpt'),
        apply_section_dedup=True
    )
