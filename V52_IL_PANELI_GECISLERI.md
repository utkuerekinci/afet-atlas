# İl panelinden modüller arası geçiş

- Yaşam Kalitesi ve Ticari Potansiyel: seçilen ilin sağ bilgi panelindeki
  **Neden Bu İlçe Birinci?** bölümünün altında diğer üç bölümün kırmızı
  geçiş butonları yer alır.
- Afet Analizi: deprem ve diğer altı afet ekranının il bilgi panelinde
  Genel Bakış, Yaşam Kalitesi ve Ticari Potansiyel bağlantıları vardır.
- Her sayfada mevcut modüle ait tekrar butonu gösterilmez.
- Seçilmiş il `st.session_state['secilen_il']` içinde korunur; gidilen analiz
  seçili ile yakınlaşarak açılır.
- Sıralamalar, diğer ekranların görünümleri ve veri/model hesaplamaları değişmedi.
