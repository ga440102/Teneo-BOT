# -*- coding: utf-8 -*-
from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz, time

init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

class Teneo:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://dashboard.teneo.pro",
            "Referer": "https://dashboard.teneo.pro/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://auth.teneo.pro/api"
        self.PAGE_URL = "https://dashboard.teneo.pro"
        self.SITE_KEY = "0x4AAAAAAAkhmGkb2VS6MRU0"
        self.API_KEY = "OwAG3kib1ivOJG4Y0OCZ8lJETa6ypvsDtGmdhcjB"
        self.SOLVER_SERVER = "http://127.0.0.1:5000"  # 打码服务端
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.turnstile_tokens = {}
        self.password = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message, color=Fore.WHITE):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{color}{message}{Style.RESET_ALL}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Setup {Fore.BLUE + Style.BRIGHT}Teneo - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"File {filename} Not Found.", Fore.RED)
                return []

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            self.log(f"保存tokens时出错: {str(e)}", Fore.RED)

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"File {filename} Not Found.", Fore.RED)
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log("No Proxies Found.", Fore.RED)
                return

            self.log(
                f"Proxies Total: {len(self.proxies)}",
                Fore.GREEN
            )
        
        except Exception as e:
            self.log(f"Failed To Load Proxies: {e}", Fore.RED)
            self.proxies = []

    def check_proxy_schemes(self, proxy):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy.startswith(scheme) for scheme in schemes):
            return proxy
        return f"http://{proxy}"

    def get_next_proxy_for_account(self, user_id):
        if user_id not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[user_id] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[user_id]

    def rotate_proxy_for_account(self, user_id):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[user_id] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    self.log(f"Run {proxy_type} Proxy Selected.", Fore.GREEN)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def solve_cf_turnstile(self, email: str, proxy=None, retries=5):
        for attempt in range(retries):
            try:
                # 1. 触发任务
                async with ClientSession() as session:
                    params = {
                        "url": self.PAGE_URL,
                        "sitekey": self.SITE_KEY
                    }
                    async with session.get(
                        f"{self.SOLVER_SERVER}/turnstile",
                        params=params,
                        proxy=proxy,
                        timeout=ClientTimeout(total=30)
                    ) as response:
                        if response.status != 202:
                            self.log(f"打码服务器错误 {response.status}: {await response.text()}", Fore.RED)
                            continue
                            
                        data = await response.json()
                        task_id = data.get("task_id")
                        if not task_id:
                            self.log("打码服务器响应缺少task_id", Fore.RED)
                            continue
                            
                    # 2. 轮询结果
                    start = time.time()
                    while time.time() - start < 90:  # 90秒超时
                        async with session.get(
                            f"{self.SOLVER_SERVER}/result",
                            params={"id": task_id},
                            proxy=proxy,
                            timeout=ClientTimeout(total=20)
                        ) as res:
                            if res.status in (200, 422):
                                try:
                                    data = await res.json()
                                    token = data.get("value") if isinstance(data, dict) else None
                                    if token and token != "CAPTCHA_FAIL":
                                        self.turnstile_tokens[email] = token
                                        self.log("验证码解决成功", Fore.GREEN)
                                        return True
                                except:
                                    body = await res.text()
                                    if body.strip() != "CAPTCHA_NOT_READY":
                                        self.log(f"打码服务器返回意外响应: {body[:100]}", Fore.YELLOW)
                            
                        await asyncio.sleep(3)
                        
                    self.log("验证码解决超时", Fore.RED)
                    
            except Exception as e:
                self.log(f"验证码解决出错: {str(e)}", Fore.RED)
                await asyncio.sleep(5)
                continue
                
        return None

    async def auth_login(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/login"
        data = json.dumps({
            "email": email,
            "password": self.password[email],
            "turnstileToken": self.turnstile_tokens[email]
        })
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "X-Api-Key": self.API_KEY
        }
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url,
                        headers=headers,
                        data=data,
                        ssl=False
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"登录失败: {str(e)}",
                    Fore.RED
                )
        return None
        
    async def process_accounts(self, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
    
        self.log(
            f"使用代理: {proxy if proxy else '无'}",
            Fore.CYAN
        )

        self.log("正在解决验证码...", Fore.CYAN)

        cf_solved = await self.solve_cf_turnstile(email, proxy)
        if not cf_solved:
            self.log("验证码解决失败", Fore.RED)
            return
        
        login = await self.auth_login(email, proxy)
        if login:
            access_token = login.get("access_token")
            if access_token:
                self.save_tokens([{"Email": email, "accessToken": access_token}])
                self.log("登录成功，令牌已保存", Fore.GREEN)
            else:
                self.log("登录响应中未找到access_token", Fore.YELLOW)
        else:
            self.log("登录失败", Fore.RED)
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log("未加载到账户", Fore.RED)
                return

            use_proxy_choice = self.print_question()
            use_proxy = use_proxy_choice in [1, 2]

            self.clear_terminal()
            self.welcome()
            self.log(
                f"账户总数: {len(accounts)}",
                Fore.GREEN
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            separator = "="*25
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account.get("Email")
                    password = account.get("Password")
                    self.log(
                        f"{separator}[ {idx}/{len(accounts)} ]{separator}",
                        Fore.CYAN
                    )

                    if not email or not password or "@" not in email:
                        self.log("无效的账户数据", Fore.RED)
                        continue

                    self.log(
                        f"账户: {self.mask_account(email)}",
                        Fore.CYAN
                    )

                    self.password[email] = password
                    await self.process_accounts(email, use_proxy)
                    await asyncio.sleep(3)

            self.log("所有账户处理完成", Fore.CYAN)

        except Exception as e:
            self.log(f"发生错误: {str(e)}", Fore.RED)
            raise e

if __name__ == "__main__":
    try:
        bot = Teneo()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"\n{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ 退出 ] Teneo - BOT{Style.RESET_ALL}"
        )