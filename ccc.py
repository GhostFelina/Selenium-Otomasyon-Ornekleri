def link_ve_gorsel_analizi(self):
    """
    GÜNCELLENMİŞ (FINAL): Standart resimleri, CSS arka planlarını VE SVG ikonları da görsel olarak raporlar.
    """
    logging.info("Link ve Görsel analizi yapılıyor (SVG Dahil)...")

    # --- LİNKLER ---
    elements = self.driver.find_elements(By.TAG_NAME, "a")
    self.data["linkler"]["ic_linkler"] = []
    self.data["linkler"]["dis_linkler"] = []

    for elem in elements:
        href = elem.get_attribute("href")
        text = elem.text.strip()
        if href:
            if self.base_url in href:
                self.data["linkler"]["ic_linkler"].append({"text": text, "url": href})
            else:
                self.data["linkler"]["dis_linkler"].append({"text": text, "url": href})

    self.data["linkler"]["toplam"] = len(self.data["linkler"]["ic_linkler"]) + len(self.data["linkler"]["dis_linkler"])

    # --- GÖRSELLER VE GRAFİKLER ---
    self.data["gorseller"] = []

    # 1. JavaScript ile Resim ve Background'ları Bul
    js_script = """
    var images = [];
    // IMG etiketleri
    var imgs = document.getElementsByTagName('img');
    for(var i=0; i<imgs.length; i++) {
        if(imgs[i].src) images.push({src: imgs[i].src, type: 'Standart Resim (IMG)'});
    }
    // CSS Arka Planları
    var all = document.getElementsByTagName('*');
    for(var i=0; i<all.length; i++) {
        var bg = window.getComputedStyle(all[i]).backgroundImage;
        if (bg !== 'none' && bg.startsWith('url')) {
            var cleanUrl = bg.slice(4, -1).replace(/["']/g, "");
            images.push({src: cleanUrl, type: 'Arka Plan Resmi (CSS)'});
        }
    }
    return images;
    """
    found_images = self.driver.execute_script(js_script)

    # Bulunan resimleri ekle
    seen_urls = set()
    for img in found_images:
        if img['src'] not in seen_urls:
            self.data["gorseller"].append({
                "tip": img['type'],
                "src": img['src'],
                "alt_text": "JS ile tespit edildi"
            })
            seen_urls.add(img['src'])

    # 2. SVG (Vektörel) Elementleri Bul ve Listeye Ekle
    svgs = self.driver.find_elements(By.TAG_NAME, "svg")
    if len(svgs) > 0:
        logging.info(f"{len(svgs)} adet SVG elementi bulundu ve rapora eklendi.")
        for i, svg in enumerate(svgs, 1):
            # SVG'lerin genellikle bir 'src'si olmaz, HTML kodu olur.
            # Rapora sembolik olarak ekliyoruz.
            self.data["gorseller"].append({
                "tip": "Vektörel Grafik (SVG)",
                "src": "Gömülü SVG Kodu",
                "alt_text": f"Grafik/İkon #{i}"
            })

    logging.info(f"Toplam {len(self.data['gorseller'])} görsel materyal (Resim + SVG) raporlandı.")