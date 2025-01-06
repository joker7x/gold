import time
import requests
import uuid

# عرض كلمة "Dexter" بتنسيق جميل
def display_dexter():
    print("\033[1;31mD\033[1;33me\033[1;32mx\033[1;34mt\033[1;35me\033[1;36mr\033[0m")
    print("\033[1;37m[Automation Tool]\033[0m")
    print("\033[3;37m[Mine $SSLX and Collect Gold Eagle Coins!]\033[0m")

# عرض وصف الأداة
def display_tool_description():
    print("\033[1;37m$SSLX Miner & Gold Eagle Bot\033[0m\n")
    print("\033[1;36mAn automated tool for mining $SSLX and collecting Gold Eagle coins.\033[0m")
    print("\033[3;32mSimply run the bot and let it handle the rest!\033[0m\n")

# عرض معرف التليجرام بشكل مميز
def display_telegram_username():
    print("\033[1;37m📩 Telegram: \033[1;36m@IFJOB\033[0m\n")
    print("\033[1;37m[Contact Me]\033[0m")

# عرض بيانات التقدم في جدول
def display_progress_table(progress_data):
    print("\n📊 Progress Data")
    print("---------------")
    print(f"Metric: Current Energy  | Value: {progress_data['energy']}/{progress_data['max_energy']}")
    print(f"Metric: Available Coins | Value: {progress_data.get('coins_amount', 0)}")
    print(f"Metric: Incomplete Tasks | Value: {progress_data['not_completed_tasks_count']}")
    print(f"Metric: Unregistered Events | Value: {progress_data['not_registerd_events_count']}")
    print("---------------\n")

# إعداد البيانات اللازمة
url_tap = "https://gold-eagle-api.fly.dev/tap"
url_wallet = "https://gold-eagle-api.fly.dev/wallet/my"
url_progress = "https://gold-eagle-api.fly.dev/user/me/progress"

# دالة للتحقق من صحة الـ Authorization Code
def verify_authorization_code(code):
    try:
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {code}",
            "content-type": "application/json",
        }
        response = requests.get(url_wallet, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ An error occurred while verifying the authorization code: {e}")
        return False

# دالة للحصول على بيانات المحفظة
def get_wallet_data(headers):
    try:
        response = requests.get(url_wallet, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch wallet data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ An error occurred while fetching wallet data: {e}")
        return None

# دالة للحصول على بيانات التقدم
def get_progress_data(headers):
    try:
        response = requests.get(url_progress, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch progress data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ An error occurred while fetching progress data: {e}")
        return None

# دالة لجمع العملات باستخدام الطاقة المتاحة
def collect_coins_using_energy(energy, headers):
    try:
        if energy > 0:
            timestamp = int(time.time())
            salt = str(uuid.uuid4())  # استخدام UUID كـ salt فريد
            
            body = {
                "available_taps": energy,
                "count": energy,  # عدد النقرات بناءً على الطاقة المتاحة
                "timestamp": timestamp,
                "salt": salt,
            }
            
            response = requests.post(url_tap, json=body, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'coins_amount' in data:
                    print(f"\n✅ Successfully collected coins! Total coins now: {data['coins_amount']}")
                else:
                    print("❌ Failed to collect coins. Invalid data received.")
            else:
                print(f"❌ Failed to collect coins: {response.status_code}")
        else:
            print("⚠️ Not enough energy to collect coins. Waiting for energy to recharge...")
    except Exception as e:
        print(f"❌ An error occurred while collecting coins: {e}")

# دالة لانتظار استعادة الطاقة مع عرض علامة التحميل
def wait_for_energy(max_energy):
    try:
        energy_recharge_time = 16 * 60  # 16 دقيقة لإعادة شحن الطاقة بالكامل (بالثواني)
        print(f"⏳ Waiting for {energy_recharge_time / 60} minutes to recharge energy...")
        
        time.sleep(energy_recharge_time)  # الانتظار حتى تكتمل الطاقة
        
        print("✅ Energy fully recharged!")
    except Exception as e:
        print(f"❌ An error occurred while waiting: {e}")

# دالة لعرض المعلومات بشكل دوري
def display_info_periodically(headers, interval_minutes=1):
    try:
        while True:
            # جلب بيانات التقدم لعرض الطاقة
            progress_data = get_progress_data(headers)
            if progress_data:
                energy = progress_data["energy"]
                max_energy = progress_data["max_energy"]
                coins_amount = progress_data.get("coins_amount", 0)
                
                # عرض المعلومات بشكل احترافي ومنسق
                display_progress_table(progress_data)
                
                # جمع العملات إذا كانت الطاقة كافية
                collect_coins_using_energy(energy, headers)
                
            print(f"\n⏰ Waiting for {interval_minutes} minute(s) before the next attempt...")
            
            time.sleep(interval_minutes * 60)  # الانتظار لمدة المحددة بالدقائق
    except KeyboardInterrupt:
        print("⛔ Automated coin collection stopped successfully.")
    except Exception as e:
        print(f"❌ An error occurred during periodic display: {e}")

# بدء الأداة
if __name__ == "__main__":
    display_dexter()
    display_tool_description()
    display_telegram_username()

    # طلب إدخال Authorization Bearer Code من المستخدم
    auth_code = input("Enter your Authorization Bearer Code: ")
    
    # التحقق من صحة الكود
    if verify_authorization_code(auth_code):
        print("✅ Authorization successful! Starting the bot...")
        
        # إعداد الرؤوس (headers) مع إضافة التوكين
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_code}",
            "content-type": "application/json",
        }

        # بدء جمع العملات التلقائي مع عرض البيانات بشكل دوري
        display_info_periodically(headers, interval_minutes=1)
    else:
        print("❌ Invalid Authorization Code. Exiting...")
