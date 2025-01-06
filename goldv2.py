import time
import requests
import uuid
from threading import Thread
from rich.console import Console
from rich.table import Table

# إعداد مكتبة rich
console = Console()

# الروابط
url_tap = "https://gold-eagle-api.fly.dev/tap"
url_wallet = "https://gold-eagle-api.fly.dev/wallet/my"
url_progress = "https://gold-eagle-api.fly.dev/user/me/progress"

# عرض جدول التقدم بشكل منسق باستخدام rich
def display_rich_progress_table(token, progress_data):
    table = Table(title=f"Progress for Token {token[:5]}")  # أول 5 أحرف من التوكين
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Current Energy", f"{progress_data['energy']}/{progress_data['max_energy']}")
    table.add_row("Available Coins", f"{progress_data.get('coins_amount', 0)}")
    table.add_row("Incomplete Tasks", f"{progress_data['not_completed_tasks_count']}")
    table.add_row("Unregistered Events", f"{progress_data['not_registerd_events_count']}")

    console.print(table)

# دالة للحصول على بيانات التقدم
def get_progress_data(headers):
    try:
        response = requests.get(url_progress, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[red]❌ Failed to fetch progress data for token: {headers['authorization'][:10]}[/red]")
            return None
    except Exception as e:
        console.print(f"[red]❌ Error fetching progress data: {e}[/red]")
        return None

# دالة لجمع العملات باستخدام الطاقة المتاحة
def collect_coins_using_energy(energy, headers, token):
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
                    console.print(f"[green]✅ [Token {token[:5]}] Coins collected! Total coins: {data['coins_amount']}[/green]")
                else:
                    console.print(f"[red]❌ [Token {token[:5]}] Failed to collect coins. Invalid data received.[/red]")
            else:
                console.print(f"[red]❌ [Token {token[:5]}] Failed to collect coins: {response.status_code}[/red]")
        else:
            console.print(f"[yellow]⚠️ [Token {token[:5]}] Not enough energy to collect coins. Waiting for energy to recharge...[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ [Token {token[:5]}] Error collecting coins: {e}[/red]")

# دالة تشغيل التوكن
def run_token_process(token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    try:
        while True:
            # جلب بيانات التقدم
            progress_data = get_progress_data(headers)
            if progress_data:
                energy = progress_data["energy"]
                max_energy = progress_data["max_energy"]

                # عرض بيانات التقدم
                display_rich_progress_table(token, progress_data)

                # جمع العملات
                collect_coins_using_energy(energy, headers, token)

            # الانتظار دقيقة قبل المحاولة التالية
            time.sleep(60)
    except KeyboardInterrupt:
        console.print(f"[yellow]⛔ [Token {token[:5]}] Stopped by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ [Token {token[:5]}] Error in token process: {e}[/red]")

# بدء التشغيل
if __name__ == "__main__":
    console.print("[cyan]Starting the bot for multiple tokens...[/cyan]")

    # قراءة التوكنات من ملف
    with open("tokens.txt", "r") as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]

    threads = []
    for token in tokens:
        thread = Thread(target=run_token_process, args=(token,))
        thread.start()
        threads.append(thread)

    # انتظار انتهاء كل الـ Threads (في حالة الإنهاء اليدوي)
    for thread in threads:
        thread.join()