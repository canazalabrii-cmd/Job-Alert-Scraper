import requests
from bs4 import BeautifulSoup
import json
import telegram
import os 
from datetime import datetime

# --- الإعدادات والرموز السرية (يتم سحبها من GitHub Secrets) ---
TELEGRAM_BOT_TOKEN = os.environ.get('8289814129:AAGhJL_DjLl104OwK1RsxZ90DiNP6hynqGc')
TELEGRAM_CHAT_ID = os.environ.get('198842533')

# الروابط المتخصصة في مجالي (Comptabilité - Gestion)
IND_URL = "https://ma.indeed.com/jobs?q=comptabilite+gestion"
EMP_URL = "https://www.emploi.ma/recherche-jobs-maroc?mots_cles=comptabilite+gestion"

# تهيئة البوت
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# ----------------- وظيفة إرسال الرسائل -----------------
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print("تم إرسال الرسالة بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الرسالة: {e}")

# ----------------- وظيفة جلب البيانات من Indeed (مثال) -----------------
def scrape_indeed():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(IND_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # **تنبيه:** يجب تعديل كلاسات (classes) البحث بناءً على بنية موقع Indeed الحالية
        # هذا مجرد مثال على كلاسات Indeed الشائعة:
        job_cards = soup.find_all('div', class_='job_card_class_Indeed') 
        
        for card in job_cards:
            # يجب تحديد كيفية استخراج العنوان والرابط لكل موقع
            title_tag = card.find('h2') 
            link_tag = card.find('a', href=True)
            
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = "https://ma.indeed.com" + link_tag['href']
                jobs.append({'title': title, 'link': link})
                
        return jobs
    except Exception as e:
        print(f"خطأ في جلب بيانات Indeed: {e}")
        return []

# ----------------- وظيفة التشغيل والمقارنة الرئيسية -----------------
def run_scraper():
    # 1. تحميل الفرص القديمة (للمقارنة)
    try:
        # GitHub Actions يحتاج هذا الملف ليكون موجوداً لذا نستخدم نفس الاسم
        with open('old_jobs.json', 'r', encoding='utf-8') as f:
            old_jobs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        old_jobs = []

    all_new_jobs = []
    # جلب الفرص من المواقع (يجب إضافة دالة scrape_emploi_ma هنا)
    all_new_jobs.extend(scrape_indeed())
    # all_new_jobs.extend(scrape_emploi_ma()) # عند الانتهاء من دالة Emploi.ma

    newly_found_jobs = []

    # 2. المقارنة والإرسال
    for job in all_new_jobs:
        # نعتمد على الرابط كمعرف فريد للوظيفة
        is_old = any(old_job['link'] == job['link'] for old_job in old_jobs)
        
        if not is_old:
            newly_found_jobs.append(job)
            
            message = (
                f"✨ *فرصة Comptabilité/Gestion جديدة!* ✨\n\n"
                f"**المنصب:** {job['title']}\n"
                f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"**الرابط:** [اضغط هنا للتقديم]({job['link']})"
            )
            send_telegram_message(message)
    
    # 3. حفظ الفرص الجديدة لتصبح هي الأساس في المرة القادمة
    if newly_found_jobs:
        # نحفظ كل ما تم إيجاده كفرص قديمة
        with open('old_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(all_new_jobs, f, ensure_ascii=False, indent=4)
        print(f"تم العثور على {len(newly_found_jobs)} فرصة جديدة وحفظها.")
    else:
        print("لم يتم العثور على فرص جديدة.")
        
if __name__ == "__main__":
    run_scraper()
