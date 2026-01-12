"""
🗺️ SEYYAHLAB İÇERİK ANALİZ BOTU
Senaryo: "SeyyahLab'daki tüm seyahat rehberlerini topla, kategorilere ayır,
          en popüler destinasyonları bul, Excel'e dök!"
Freelance Değeri: $200-400/proje (İçerik analizi + SEO raporu)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from collections import Counter
import pandas as pd
import json
import os
import re


class SeyyahLabAnalyzer:
    """
    SeyyahLab.com İçerik Analiz Robotu

    Özellikler:
    - Blog yazılarını topla
    - Kategorilere göre sınıflandır
    - Destinasyon analizi
    - Kelime bulutu verisi
    - SEO analizi
    - Çoklu format export (Excel, JSON, HTML)
    """

    def __init__(self):
        """Bot'u başlat"""
        self.driver = None
        self.articles = []
        self.categories = []
        self.destinations = []
        self.stats = {}
        self._setup_driver()

    def _setup_driver(self):
        """Chrome'u profesyonel ayarlarla yapılandır"""
        print("=" * 80)
        print("🗺️  SEYYAHLAB İÇERİK ANALİZ BOTU BAŞLATILIYOR...")
        print("=" * 80)

        options = Options()

        # Profesyonel bot ayarları
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Bot tespitini zorlaştır
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Performans optimizasyonu
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)

        # Sayfa yükleme timeout'u
        self.driver.set_page_load_timeout(30)

        print("✅ Tarayıcı hazır!")

    def analyze_homepage(self):
        """Ana sayfa analizini yap"""
        try:
            print(f"\n🌐 SeyyahLab ana sayfasına gidiliyor...")
            self.driver.get("https://www.seyyahlab.com")

            # Sayfa yüklenmesini bekle
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Sayfa başlığı
            page_title = self.driver.title
            print(f"✅ Sayfa Başlığı: {page_title}")

            # Meta description (SEO için önemli!)
            try:
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, "meta[name='description']").get_attribute(
                    "content")
                print(f"📝 Meta Description: {meta_desc[:100]}...")
            except:
                meta_desc = "Bulunamadı"
                print("⚠️ Meta description bulunamadı (SEO eksiği!)")

            # Sayfa yavaşça aşağı kaydır (tüm içeriği yükle)
            print("\n⬇️ Sayfa kaydırılıyor (Lazy loading tetikleniyor)...")
            self._smooth_scroll()

            # İçerik kartlarını topla
            print("\n📦 İçerik kartları toplanıyor...")
            self._extract_content_cards()

            # Navigasyon menüsünü analiz et
            print("\n🧭 Navigasyon menüsü analiz ediliyor...")
            self._analyze_navigation()

            # Link analizi
            print("\n🔗 Link analizi yapılıyor...")
            self._analyze_links()

            # Görsel analizi
            print("\n🖼️ Görsel analizi yapılıyor...")
            self._analyze_images()

            # İstatistikleri hesapla
            self._calculate_statistics()

            return True

        except TimeoutException:
            print("❌ Sayfa yükleme zaman aşımı!")
            self._take_screenshot("timeout_error")
            return False
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            self._take_screenshot("general_error")
            return False

    def _smooth_scroll(self):
        """Sayfayı yumuşak şekilde kaydır (kullanıcı simülasyonu)"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")

        current_position = 0
        scroll_step = viewport_height // 2  # Yarım ekran adımlarla

        while current_position < total_height:
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            current_position += scroll_step

            # Yeni içeriğin yüklenmesini bekle
            self.driver.implicitly_wait(0.5)

            # Dinamik içerik yüklendiyse yükseklik değişir
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height

        # En alta git
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"✅ Sayfa kaydırıldı (Toplam yükseklik: {total_height}px)")

    def _extract_content_cards(self):
        """İçerik kartlarını (blog yazıları, rehberler) topla"""
        card_selectors = [
            "article",
            "[class*='card']",
            "[class*='post']",
            "[class*='content']",
            ".blog-item",
            "[class*='article']"
        ]

        content_cards = []
        for selector in card_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 0:
                    content_cards.extend(elements)
                    print(f"   ✓ '{selector}' ile {len(elements)} öğe bulundu")
            except:
                continue

        # Benzersiz elementleri al
        unique_cards = list(set(content_cards))
        print(f"✅ Toplam {len(unique_cards)} içerik kartı tespit edildi")

        # Her karttan bilgi çıkar
        for idx, card in enumerate(unique_cards[:20], 1):  # İlk 20 kart
            try:
                article_data = {}

                # Başlık
                title_selectors = ["h1", "h2", "h3", "[class*='title']", "a"]
                for selector in title_selectors:
                    try:
                        title_element = card.find_element(By.CSS_SELECTOR, selector)
                        title_text = title_element.text.strip()
                        if title_text and len(title_text) > 5:
                            article_data['baslik'] = title_text[:150]
                            break
                    except:
                        continue

                if 'baslik' not in article_data:
                    continue  # Başlık yoksa atla

                # Link
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    article_data['link'] = link_element.get_attribute("href")
                except:
                    article_data['link'] = "Link bulunamadı"

                # Özet metin
                try:
                    text_selectors = ["p", "[class*='excerpt']", "[class*='description']", "[class*='summary']"]
                    for selector in text_selectors:
                        try:
                            text = card.find_element(By.CSS_SELECTOR, selector).text.strip()
                            if text and len(text) > 20:
                                article_data['ozet'] = text[:200]
                                break
                        except:
                            continue
                except:
                    article_data['ozet'] = "Özet bulunamadı"

                # Görsel
                try:
                    img = card.find_element(By.CSS_SELECTOR, "img")
                    article_data['gorsel'] = img.get_attribute("src") or img.get_attribute("data-src")
                except:
                    article_data['gorsel'] = "Görsel yok"

                # Kategori/Etiket (varsa)
                try:
                    tag_selectors = ["[class*='category']", "[class*='tag']", "[class*='label']", "span"]
                    for selector in tag_selectors:
                        try:
                            tags = card.find_elements(By.CSS_SELECTOR, selector)
                            tag_texts = [t.text.strip() for t in tags if t.text.strip()]
                            if tag_texts:
                                article_data['kategori'] = ", ".join(tag_texts[:3])
                                break
                        except:
                            continue
                except:
                    article_data['kategori'] = "Kategori yok"

                # Destinasyon çıkarımı (başlıktan)
                self._extract_destination(article_data['baslik'])

                article_data['sira'] = idx
                article_data['tarih'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.articles.append(article_data)
                print(f"   {idx}. {article_data['baslik'][:60]}...")

            except Exception as e:
                continue

    def _extract_destination(self, text):
        """Metinden destinasyon çıkar (Örn: 'İstanbul', 'Kapadokya')"""
        # Türkiye'nin popüler destinasyonları
        destinations = [
            "İstanbul", "Ankara", "İzmir", "Antalya", "Kapadokya", "Bodrum",
            "Marmaris", "Fethiye", "Çeşme", "Alanya", "Trabzon", "Bursa",
            "Konya", "Pamukkale", "Ephesus", "Efes", "Göreme", "Safranbolu",
            "Mardin", "Şanlıurfa", "Gaziantep", "Kayseri", "Erzurum"
        ]

        for dest in destinations:
            if dest.lower() in text.lower():
                self.destinations.append(dest)
                return dest
        return None

    def _analyze_navigation(self):
        """Site navigasyon menüsünü analiz et"""
        try:
            nav_items = self.driver.find_elements(By.CSS_SELECTOR, "nav a, header a, [class*='menu'] a")

            categories_found = []
            for item in nav_items:
                text = item.text.strip()
                if text and len(text) > 1 and text not in ['', 'Home', 'Ana Sayfa']:
                    categories_found.append(text)

            self.categories = list(set(categories_found))
            print(f"✅ {len(self.categories)} kategori bulundu: {', '.join(self.categories[:5])}...")

        except Exception as e:
            print(f"⚠️ Navigasyon analizi başarısız: {e}")

    def _analyze_links(self):
        """Sayfa linklerini analiz et (SEO önemli!)"""
        try:
            all_links = self.driver.find_elements(By.TAG_NAME, "a")

            internal_links = []
            external_links = []
            broken_links = []

            base_domain = "seyyahlab.com"

            for link in all_links:
                href = link.get_attribute("href")
                if not href:
                    continue

                if base_domain in href or href.startswith("/"):
                    internal_links.append(href)
                elif href.startswith("http"):
                    external_links.append(href)

            self.stats['toplam_link'] = len(all_links)
            self.stats['ic_link'] = len(set(internal_links))
            self.stats['dis_link'] = len(set(external_links))

            print(f"✅ Link Analizi:")
            print(f"   - Toplam Link: {self.stats['toplam_link']}")
            print(f"   - İç Linkler: {self.stats['ic_link']}")
            print(f"   - Dış Linkler: {self.stats['dis_link']}")

        except Exception as e:
            print(f"⚠️ Link analizi başarısız: {e}")

    def _analyze_images(self):
        """Görselleri analiz et"""
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")

            images_with_alt = [img for img in images if img.get_attribute("alt")]
            images_without_alt = len(images) - len(images_with_alt)

            self.stats['toplam_gorsel'] = len(images)
            self.stats['alt_tag_var'] = len(images_with_alt)
            self.stats['alt_tag_yok'] = images_without_alt

            print(f"✅ Görsel Analizi:")
            print(f"   - Toplam Görsel: {self.stats['toplam_gorsel']}")
            print(f"   - Alt Tag Var: {self.stats['alt_tag_var']}")
            print(f"   - Alt Tag Yok: {self.stats['alt_tag_yok']} (SEO eksiği!)")

        except Exception as e:
            print(f"⚠️ Görsel analizi başarısız: {e}")

    def _calculate_statistics(self):
        """Genel istatistikleri hesapla"""
        self.stats['toplam_makale'] = len(self.articles)
        self.stats['toplam_kategori'] = len(self.categories)

        # En popüler destinasyonlar
        if self.destinations:
            destination_counts = Counter(self.destinations)
            self.stats['populer_destinasyonlar'] = dict(destination_counts.most_common(5))

        # Kelime analizi (başlıklardan)
        all_words = []
        for article in self.articles:
            words = re.findall(r'\w+', article['baslik'].lower())
            all_words.extend([w for w in words if len(w) > 3])  # 3 harften uzun kelimeler

        word_counts = Counter(all_words)
        self.stats['populer_kelimeler'] = dict(word_counts.most_common(10))

    def _take_screenshot(self, name):
        """Ekran görüntüsü al"""
        try:
            os.makedirs("screenshots", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/seyyahlab_{name}_{timestamp}.png"
            self.driver.save_screenshot(path)
            print(f"📸 Ekran görüntüsü: {path}")
        except:
            pass

    def save_to_excel(self, filename="seyyahlab_analiz.xlsx"):
        """Excel'e kaydet (Çok detaylı!)"""
        if not self.articles:
            print("⚠️ Kaydedilecek içerik yok!")
            return

        print(f"\n💾 Excel raporu oluşturuluyor...")

        # Ana makale listesi
        df_articles = pd.DataFrame(self.articles)

        # İstatistikler için ayrı sheet
        stats_data = []
        for key, value in self.stats.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    stats_data.append({"Metrik": f"{key} - {k}", "Değer": v})
            else:
                stats_data.append({"Metrik": key, "Değer": value})

        df_stats = pd.DataFrame(stats_data)

        # Kategoriler için ayrı sheet
        df_categories = pd.DataFrame({"Kategoriler": self.categories})

        # Excel'e yaz
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_articles.to_excel(writer, sheet_name='Makaleler', index=False)
            df_stats.to_excel(writer, sheet_name='İstatistikler', index=False)
            df_categories.to_excel(writer, sheet_name='Kategoriler', index=False)

            # Sütun genişliklerini ayarla
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 60)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        print(f"✅ Excel kaydedildi: {filename}")
        print(f"   📊 3 Sheet: Makaleler, İstatistikler, Kategoriler")

    def save_to_json(self, filename="seyyahlab_data.json"):
        """JSON formatında kaydet"""
        print(f"💾 JSON dosyası oluşturuluyor...")

        report = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "site": "SeyyahLab.com",
            "makaleler": self.articles,
            "kategoriler": self.categories,
            "istatistikler": self.stats
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON kaydedildi: {filename}")

    def create_html_report(self, filename="seyyahlab_rapor.html"):
        """Premium HTML rapor oluştur"""
        if not self.articles:
            return

        print(f"📊 HTML raporu oluşturuluyor...")

        # Popüler destinasyonları listele
        dest_html = ""
        if 'populer_destinasyonlar' in self.stats:
            for dest, count in self.stats['populer_destinasyonlar'].items():
                dest_html += f'<div class="dest-badge">{dest} ({count})</div>'

        # Makale kartları
        articles_html = ""
        for article in self.articles[:10]:  # İlk 10 makale
            articles_html += f"""
            <div class="article-card">
                <div class="article-number">{article['sira']}</div>
                <h3>{article['baslik']}</h3>
                <p class="excerpt">{article.get('ozet', 'Özet yok')[:150]}...</p>
                <div class="article-meta">
                    <span>📍 Kategori: {article.get('kategori', 'N/A')}</span>
                </div>
                <a href="{article['link']}" target="_blank" class="btn">Yazıyı Oku →</a>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SeyyahLab İçerik Analiz Raporu</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 25px 70px rgba(0,0,0,0.3);
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 50px;
                    text-align: center;
                }}
                .header h1 {{ font-size: 3em; margin-bottom: 10px; }}
                .header p {{ font-size: 1.2em; opacity: 0.9; }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    padding: 40px;
                    background: #f8f9fa;
                }}
                .stat-card {{
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }}
                .stat-card:hover {{ transform: translateY(-5px); }}
                .stat-card h2 {{ 
                    color: #667eea; 
                    font-size: 3em; 
                    margin-bottom: 10px;
                }}
                .stat-card p {{ color: #666; font-size: 1.1em; }}

                .section {{
                    padding: 40px;
                }}
                .section h2 {{
                    color: #333;
                    font-size: 2em;
                    margin-bottom: 20px;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}

                .destinations {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-top: 20px;
                }}
                .dest-badge {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 12px 25px;
                    border-radius: 25px;
                    font-weight: bold;
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                }}

                .articles-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 25px;
                    margin-top: 30px;
                }}
                .article-card {{
                    background: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 15px;
                    padding: 25px;
                    transition: all 0.3s;
                    position: relative;
                }}
                .article-card:hover {{
                    border-color: #667eea;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                    transform: translateY(-3px);
                }}
                .article-number {{
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: #f093fb;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                }}
                .article-card h3 {{
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                    line-height: 1.4;
                }}
                .excerpt {{
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 15px;
                }}
                .article-meta {{
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 0.9em;
                    color: #666;
                    margin-bottom: 15px;
                }}
                .btn {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: all 0.3s;
                    font-weight: bold;
                }}
                .btn:hover {{
                    transform: translateX(5px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }}

                .footer {{
                    background: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 30px;
                }}
                .footer p {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🗺️ SeyyahLab İçerik Analiz Raporu</h1>
                    <p>Seyahat içeriklerinin detaylı analizi</p>
                    <p style="margin-top: 10px; font-size: 0.9em;">
                        Tarih: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                    </p>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h2>{self.stats.get('toplam_makale', 0)}</h2>
                        <p>📝 Toplam Makale</p>
                    </div>
                    <div class="stat-card">
                        <h2>{self.stats.get('toplam_kategori', 0)}</h2>
                        <p>📂 Kategori</p>
                    </div>
                    <div class="stat-card">
                        <h2>{self.stats.get('toplam_link', 0)}</h2>
                        <p>🔗 Toplam Link</p>
                    </div>
                    <div class="stat-card">
                        <h2>{self.stats.get('toplam_gorsel', 0)}</h2>
                        <p>🖼️ Görsel</p>
                    </div>
                    <div class="stat-card">
                        <h2>{self.stats.get('ic_link', 0)}</h2>
                        <p>🏠 İç Link (SEO)</p>
                    </div>
                    <div class="stat-card">
                        <h2>{self.stats.get('alt_tag_yok', 0)}</h2>
                        <p>⚠️ Alt Tag Eksik</p>
                    </div>
                </div>

                <div class="section">
                    <h2>🌍 Popüler Destinasyonlar</h2>
                    <div class="destinations">
                        {dest_html if dest_html else '<p>Destinasyon bilgisi bulunamadı</p>'}
                    </div>
                </div>

                <div class="section">
                    <h2>📰 Öne Çıkan Makaleler (İlk 10)</h2>
                    <div class="articles-grid">
                        {articles_html if articles_html else '<p>Makale bulunamadı</p>'}
                    </div>
                </div>

                <div class="footer">
                    <p><strong>🤖 Bu rapor otomatik olarak oluşturulmuştur</strong></p>
                    <p>Selenium Professional Bot | İçerik Analiz Sistemi</p>
                    <p style="margin-top: 10px; opacity: 0.7;">
                        Rapor Tipi: SEO + İçerik Analizi | Format: HTML
                    </p>
                </div>
            </div>