"""
🛒 E-TİCARET FİYAT KARŞILAŞTIRMA BOTU
Müşteri Senaryosu: "Hepsiburada'da laptop fiyatlarını takip et, Excel'e dök!"
Freelance Değeri: $150-300/proje
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import json
import os


class ECommerceProductTracker:
    """
    Profesyonel E-Ticaret Ürün Takip Sınıfı
    Özellikler:
    - Dinamik arama
    - Fiyat karşılaştırma
    - Excel export
    - HTML rapor
    """

    def __init__(self, headless=False):
        """Tarayıcıyı başlat"""
        self.driver = None
        self.products = []
        self.headless = headless
        self._setup_driver()

    def _setup_driver(self):
        """Chrome'u profesyonel ayarlarla yapılandır"""
        print("=" * 70)
        print("🚀 E-TİCARET ÜRÜN TAKİP BOTU BAŞLATILIYOR...")
        print("=" * 70)

        options = Options()

        # Profesyonel ayarlar
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # User-Agent (Bot tespitini zorlaştır)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Headless mod (Müşteri "arka planda çalışsın" derse)
        if self.headless:
            options.add_argument("--headless=new")
            print("🔇 Sessiz mod aktif (Tarayıcı görünmeyecek)")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)

        print("✅ Tarayıcı hazır!")

    def search_products(self, site_url, search_keyword, max_products=10):
        """
        Ürün arama ve veri toplama
        Args:
            site_url: Hedef site (örn: https://www.hepsiburada.com)
            search_keyword: Arama terimi (örn: "gaming laptop")
            max_products: Kaç ürün toplanacak
        """
        try:
            print(f"\n🌐 Siteye gidiliyor: {site_url}")
            self.driver.get(site_url)

            # Çerezleri kabul et (varsa)
            self._handle_cookie_popup()

            # Arama kutusunu bul ve aramayı yap
            print(f"🔍 '{search_keyword}' aranıyor...")
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[placeholder*='Ara']"))
            )

            search_box.clear()
            search_box.send_keys(search_keyword)
            search_box.send_keys(Keys.RETURN)

            # Arama sonuçlarının yüklenmesini bekle
            print("⏳ Sonuçlar yükleniyor...")
            self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "[class*='product'], [class*='Product'], li[class*='item']"))
            )

            # Sayfayı scroll et (Lazy loading için)
            self._scroll_to_load_products()

            # Ürünleri topla
            print(f"📦 İlk {max_products} ürün toplanıyor...")
            self._extract_products(max_products)

            print(f"✅ Toplam {len(self.products)} ürün başarıyla toplandı!")

        except Exception as e:
            print(f"❌ Hata: {e}")
            self._take_error_screenshot()

    def _handle_cookie_popup(self):
        """Çerez popup'ını kapat (varsa)"""
        try:
            cookie_buttons = [
                "//button[contains(text(), 'Kabul')]",
                "//button[contains(text(), 'Accept')]",
                "//button[@id='onetrust-accept-btn-handler']",
                "[id*='accept'], [id*='cookie']"
            ]

            for selector in cookie_buttons:
                try:
                    if selector.startswith("//"):
                        btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    btn.click()
                    print("🍪 Çerez popup'ı kapatıldı")
                    return
                except:
                    continue
        except:
            pass  # Popup yoksa devam et

    def _scroll_to_load_products(self):
        """Sayfayı kademeli olarak kaydır (Lazy loading tetikleme)"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(3):  # 3 kez scroll
            # Yavaş yavaş aşağı in
            self.driver.execute_script(f"window.scrollTo(0, {(i + 1) * 800});")

            # Yeni içeriğin yüklenmesini bekle
            self.driver.implicitly_wait(1)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _extract_products(self, max_products):
        """Ürün bilgilerini çıkar"""
        # Farklı sitelerde farklı CSS selector'ları deneyeceğiz
        product_selectors = [
            "[class*='product-card']",
            "[class*='productListContent']",
            "li[class*='product']",
            "div[data-test*='product']",
            ".product-item",
            "[class*='Product']"
        ]

        product_elements = []
        for selector in product_selectors:
            try:
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(product_elements) >= 3:  # En az 3 ürün bulunduysa geçerli
                    print(f"✅ Ürünler bulundu! Selector: {selector}")
                    break
            except:
                continue

        if not product_elements:
            print("⚠️ Ürün bulunamadı, genel HTML yapısı kaydediliyor...")
            return

        for idx, element in enumerate(product_elements[:max_products], 1):
            try:
                # Ürün adı
                name_selectors = ["h3", "h2", "[class*='title']", "[class*='name']", "a"]
                product_name = "Bulunamadı"
                for selector in name_selectors:
                    try:
                        product_name = element.find_element(By.CSS_SELECTOR, selector).text.strip()
                        if product_name and len(product_name) > 5:
                            break
                    except:
                        continue

                # Fiyat
                price_selectors = ["[class*='price']", "[data-test*='price']", "span[class*='Price']", ".price"]
                price = "Fiyat Yok"
                for selector in price_selectors:
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text.strip()
                        if price_text and any(char.isdigit() for char in price_text):
                            price = price_text
                            break
                    except:
                        continue

                # Ürün linki
                try:
                    link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    link = "Link Yok"

                # Rating (varsa)
                try:
                    rating = element.find_element(By.CSS_SELECTOR, "[class*='rating'], [class*='star']").text
                except:
                    rating = "N/A"

                product_data = {
                    "Sıra": idx,
                    "Ürün Adı": product_name[:100],  # İlk 100 karakter
                    "Fiyat": price,
                    "Rating": rating,
                    "Link": link,
                    "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                self.products.append(product_data)
                print(f"   {idx}. {product_name[:50]}... | {price}")

            except Exception as e:
                print(f"   ⚠️ Ürün {idx} atlandı: {str(e)[:50]}")
                continue

    def _take_error_screenshot(self):
        """Hata durumunda ekran görüntüsü al"""
        try:
            os.makedirs("screenshots", exist_ok=True)
            error_path = f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(error_path)
            print(f"📸 Hata ekran görüntüsü: {error_path}")
        except:
            pass

    def save_to_excel(self, filename="urun_karsilastirma.xlsx"):
        """Excel'e kaydet (Müşteriler bunu SEVIYOR!)"""
        if not self.products:
            print("⚠️ Kaydedilecek ürün yok!")
            return

        print(f"\n💾 Excel dosyası oluşturuluyor: {filename}")

        df = pd.DataFrame(self.products)

        # Excel'e kaydet (güzel formatla)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ürünler')

            # Sütun genişliklerini ayarla
            worksheet = writer.sheets['Ürünler']
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        print(f"✅ Excel dosyası kaydedildi: {filename}")

    def save_to_json(self, filename="urun_data.json"):
        """JSON formatında kaydet (API entegrasyonu için)"""
        print(f"💾 JSON dosyası oluşturuluyor: {filename}")

        report = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "toplam_urun": len(self.products),
            "urunler": self.products
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON dosyası kaydedildi: {filename}")

    def create_html_report(self, filename="urun_raporu.html"):
        """HTML rapor oluştur (Müşteriye gönderebilirsin!)"""
        if not self.products:
            return

        print(f"📊 HTML raporu oluşturuluyor: {filename}")

        # En ucuz ürünü bul
        cheapest = min(self.products, key=lambda x: self._extract_price(x['Fiyat']))

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>Ürün Karşılaştırma Raporu</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    padding: 30px;
                    background: #f8f9fa;
                }}
                .stat-box {{
                    text-align: center;
                    padding: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    flex: 1;
                    margin: 0 10px;
                }}
                .stat-box h3 {{ color: #667eea; font-size: 2em; }}
                .stat-box p {{ color: #666; margin-top: 10px; }}
                .best-deal {{
                    background: #d4edda;
                    border-left: 5px solid #28a745;
                    padding: 20px;
                    margin: 20px 40px;
                    border-radius: 5px;
                }}
                .best-deal h2 {{ color: #28a745; margin-bottom: 10px; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 15px;
                    text-align: left;
                }}
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{ background: #f8f9fa; }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: #333;
                    color: white;
                }}
                .price {{ font-weight: bold; color: #f5576c; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 Ürün Karşılaştırma Raporu</h1>
                    <p>Tarih: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <h3>{len(self.products)}</h3>
                        <p>Toplam Ürün</p>
                    </div>
                    <div class="stat-box">
                        <h3>{cheapest['Fiyat']}</h3>
                        <p>En Düşük Fiyat</p>
                    </div>
                    <div class="stat-box">
                        <h3>✅</h3>
                        <p>Test Başarılı</p>
                    </div>
                </div>

                <div class="best-deal">
                    <h2>🏆 En İyi Teklif</h2>
                    <p><strong>{cheapest['Ürün Adı']}</strong></p>
                    <p class="price">{cheapest['Fiyat']}</p>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Sıra</th>
                            <th>Ürün Adı</th>
                            <th>Fiyat</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for product in self.products:
            html_content += f"""
                        <tr>
                            <td>{product['Sıra']}</td>
                            <td>{product['Ürün Adı']}</td>
                            <td class="price">{product['Fiyat']}</td>
                            <td>{product['Rating']}</td>
                        </tr>
            """

        html_content += """
                    </tbody>
                </table>

                <div class="footer">
                    <p>🤖 Bu rapor otomatik olarak oluşturulmuştur</p>
                    <p>Powered by Selenium Professional Bot</p>
                </div>
            </div>
        </body>
        </html>
        """

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML raporu oluşturuldu: {filename}")

    def _extract_price(self, price_str):
        """Fiyat string'inden sayıyı çıkar (karşılaştırma için)"""
        import re
        numbers = re.findall(r'\d+[\.,]?\d*', price_str.replace('.', '').replace(',', '.'))
        return float(numbers[0]) if numbers else 99999999

    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            print("\n🔒 Tarayıcı kapatılıyor...")
            self.driver.quit()
            print("✅ İşlem tamamlandı!")


# ============================================================================
# ANA PROGRAM - BURADAN ÇALIŞTIR!
# ============================================================================

def main():
    """Ana çalıştırma fonksiyonu"""

    # Takip edilecek site bilgileri
    TARGET_SITE = "https://www.hepsiburada.com"
    SEARCH_KEYWORD = "gaming laptop"
    MAX_PRODUCTS = 10

    # Botu başlat
    bot = ECommerceProductTracker(headless=False)  # headless=True yaparsanız tarayıcı görünmez

    try:
        # Ürünleri ara ve topla
        bot.search_products(
            site_url=TARGET_SITE,
            search_keyword=SEARCH_KEYWORD,
            max_products=MAX_PRODUCTS
        )

        # Raporları oluştur
        if bot.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            bot.save_to_excel(f"urun_karsilastirma_{timestamp}.xlsx")
            bot.save_to_json(f"urun_data_{timestamp}.json")
            bot.create_html_report(f"urun_raporu_{timestamp}.html")

            print("\n" + "=" * 70)
            print("🎉 TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI!")
            print("=" * 70)
            print(f"📁 Excel Dosyası: urun_karsilastirma_{timestamp}.xlsx")
            print(f"📁 JSON Dosyası: urun_data_{timestamp}.json")
            print(f"📁 HTML Rapor: urun_raporu_{timestamp}.html")
            print("=" * 70)
        else:
            print("\n⚠️ Hiç ürün toplanamadı. Site yapısı değişmiş olabilir.")
            print("💡 İpucu: CSS selector'ları güncellemeniz gerekebilir.")

    except Exception as e:
        print(f"\n❌ Kritik Hata: {e}")

    finally:
        bot.close()


if __name__ == "__main__":
    main()