#!/usr/bin/env python3
"""
Gmail Account Creator Pro - Real Account Creation Tool
Creates actual Gmail accounts using Selenium automation
"""

import os
import sys
import json
import time
import random
import string
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GmailCreator:
    def __init__(self):
        self.driver = None
        self.config = self.load_config()
        self.accounts = []
        self.success_count = 0
        self.failure_count = 0
        
    def load_config(self):
        """Load configuration from config files"""
        config = {
            'password': self.read_file('config/password.txt').strip(),
            'names': [n.strip() for n in self.read_file('data/names.txt').strip().split('\n') if n.strip()],
            'user_agents': [ua.strip() for ua in self.read_file('config/user_agents.txt').strip().split('\n') if ua.strip()],
            'birthday': ('2', '4', '1990'),
            'gender': '1'  # 1=Male, 2=Female
        }
        
        if not config['password']:
            config['password'] = 'Gmail@2024Secure1'
        if not config['names']:
            config['names'] = ['Ahmed Mohamed', 'Mohamed Ali', 'Omar Ibrahim']
            
        return config
    
    @staticmethod
    def read_file(filepath):
        """Read file content"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"{Colors.WARNING}Warning: Could not read {filepath}: {e}{Colors.ENDC}")
        return ""
    
    def init_driver(self):
        """Initialize Chrome WebDriver with anti-detection settings"""
        try:
            chrome_options = Options()
            
            # Add random user agent
            if self.config['user_agents']:
                user_agent = random.choice(self.config['user_agents'])
                chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Anti-detection arguments
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--start-maximized')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            print(f"{Colors.OKGREEN}✓ Chrome driver initialized successfully{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ Failed to initialize driver: {e}{Colors.ENDC}")
            return False
    
    def random_delay(self, min_sec=1, max_sec=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def generate_email(self, name):
        """Generate unique Gmail address from name"""
        base_name = name.lower().replace(' ', '.').replace("'", "").replace('ي', 'i').replace('ى', 'a')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        email_base = f"{base_name}{random_suffix}"
        return f"{email_base}@gmail.com"
    
    def type_with_delay(self, element, text, delay_range=(0.05, 0.15)):
        """Type text with human-like delays between keystrokes"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(delay_range[0], delay_range[1]))
    
    def create_account(self, account_num, total_accounts):
        """Create a single Gmail account"""
        try:
            print(f"\n{Colors.HEADER}[Account {account_num}/{total_accounts}] Starting creation...{Colors.ENDC}")
            
            # Navigate to Gmail signup
            print(f"{Colors.OKBLUE}→ Opening Gmail signup page...{Colors.ENDC}")
            self.driver.get('https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignUp&flowEntry=SignUp')
            self.random_delay(3, 5)
            
            # Select random name
            full_name = random.choice(self.config['names']).strip()
            if not full_name or len(full_name.strip()) == 0:
                full_name = f"User{random.randint(10000, 99999)}"
            
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else f"User{random.randint(100, 999)}"
            
            # Fill First Name
            print(f"{Colors.OKBLUE}→ Entering name: {first_name} {last_name}{Colors.ENDC}")
            try:
                first_name_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "firstName"))
                )
                first_name_field.clear()
                self.type_with_delay(first_name_field, first_name)
                self.random_delay(0.5, 1.5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error entering first name: {e}{Colors.ENDC}")
                return False
            
            # Fill Last Name
            try:
                last_name_field = self.driver.find_element(By.ID, "lastName")
                last_name_field.clear()
                self.type_with_delay(last_name_field, last_name)
                self.random_delay(0.5, 1.5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error entering last name: {e}{Colors.ENDC}")
                return False
            
            # Click Next
            try:
                next_button = self.driver.find_element(By.ID, "collectNameNext")
                next_button.click()
                self.random_delay(2, 4)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error clicking name next: {e}{Colors.ENDC}")
                return False
            
            # Fill Birthday
            print(f"{Colors.OKBLUE}→ Setting birthday...{Colors.ENDC}")
            try:
                month_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "month"))
                )
                month_field.send_keys(self.config['birthday'][0])
                self.random_delay(0.3, 0.7)
                
                day_field = self.driver.find_element(By.ID, "day")
                day_field.send_keys(self.config['birthday'][1])
                self.random_delay(0.3, 0.7)
                
                year_field = self.driver.find_element(By.ID, "year")
                year_field.send_keys(self.config['birthday'][2])
                self.random_delay(0.5, 1)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error filling birthday: {e}{Colors.ENDC}")
                return False
            
            # Select Gender
            try:
                gender_select = self.driver.find_element(By.ID, "gender")
                gender_select.send_keys('Male')
                self.random_delay(0.5, 1)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error selecting gender: {e}{Colors.ENDC}")
                return False
            
            # Click Next
            try:
                next_button = self.driver.find_element(By.ID, "collectBirthdayAndGenderNext")
                next_button.click()
                self.random_delay(3, 5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error clicking birthday next: {e}{Colors.ENDC}")
                return False
            
            # Generate Gmail address
            email = self.generate_email(full_name)
            print(f"{Colors.OKBLUE}→ Gmail address: {email}{Colors.ENDC}")
            
            # Fill Gmail address
            try:
                gmail_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                gmail_field.clear()
                self.type_with_delay(gmail_field, email.split('@')[0])
                self.random_delay(0.5, 1.5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error entering Gmail: {e}{Colors.ENDC}")
                return False
            
            # Click Next to check availability
            try:
                next_button = self.driver.find_element(By.ID, "collectUsernameNext")
                next_button.click()
                self.random_delay(3, 6)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error clicking username next: {e}{Colors.ENDC}")
                return False
            
            # Check if email is available
            try:
                error_elements = self.driver.find_elements(By.CLASS_NAME, "o6cuqc")
                for elem in error_elements:
                    error_text = elem.text.lower()
                    if "not available" in error_text or "already in use" in error_text or "in use" in error_text:
                        print(f"{Colors.WARNING}✗ Email not available, retrying...{Colors.ENDC}")
                        return False
            except:
                pass
            
            # Fill Password
            print(f"{Colors.OKBLUE}→ Setting password...{Colors.ENDC}")
            try:
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "passwd"))
                )
                password_field.clear()
                self.type_with_delay(password_field, self.config['password'])
                self.random_delay(0.5, 1.5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error entering password: {e}{Colors.ENDC}")
                return False
            
            # Confirm Password
            try:
                confirm_password_field = self.driver.find_element(By.ID, "confirm-passwd")
                confirm_password_field.clear()
                self.type_with_delay(confirm_password_field, self.config['password'])
                self.random_delay(0.5, 1.5)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error confirming password: {e}{Colors.ENDC}")
                return False
            
            # Click Next
            try:
                next_button = self.driver.find_element(By.ID, "createpasswdnext")
                next_button.click()
                self.random_delay(3, 6)
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Error clicking password next: {e}{Colors.ENDC}")
                return False
            
            # Try to skip phone verification
            print(f"{Colors.OKBLUE}→ Handling verification...{Colors.ENDC}")
            try:
                skip_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Skip')]")
                if skip_buttons:
                    skip_buttons[0].click()
                    self.random_delay(2, 4)
            except:
                pass
            
            # Save account details
            account_data = {
                'index': account_num,
                'email': email,
                'password': self.config['password'],
                'full_name': full_name,
                'created_at': datetime.now().isoformat(),
                'status': 'created'
            }
            self.accounts.append(account_data)
            self.success_count += 1
            
            print(f"{Colors.OKGREEN}✓ Account created successfully!{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ Unexpected error: {str(e)}{Colors.ENDC}")
            self.failure_count += 1
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.random_delay(2, 4)
    
    def create_multiple_accounts(self, count=1):
        """Create multiple Gmail accounts"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}║   🚀 REAL GMAIL ACCOUNT CREATOR 🚀    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}║   Creating {count} Actual Gmail Accounts   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}╚════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        for i in range(1, count + 1):
            if not self.init_driver():
                self.failure_count += 1
                continue
            
            success = False
            retries = 0
            max_retries = 2
            
            while not success and retries < max_retries:
                success = self.create_account(i, count)
                if not success:
                    retries += 1
                    if retries < max_retries:
                        print(f"{Colors.WARNING}⟳ Retry {retries}/{max_retries}...{Colors.ENDC}")
            
            if not success:
                self.failure_count += 1
        
        self.save_accounts()
        self.print_summary()
    
    def save_accounts(self):
        """Save created accounts to JSON file"""
        try:
            Path('data').mkdir(exist_ok=True)
            output_file = 'data/accounts.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
            
            print(f"\n{Colors.OKGREEN}✓ Accounts saved to {output_file}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error saving accounts: {e}{Colors.ENDC}")
    
    def print_summary(self):
        """Print summary statistics"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}║        ✅ CREATION SUMMARY ✅          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}╚════════════════════════════════════════════╝{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Successful: {self.success_count}{Colors.ENDC}")
        print(f"{Colors.FAIL}✗ Failed: {self.failure_count}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}→ Total Created: {len(self.accounts)}{Colors.ENDC}")
        
        if self.accounts:
            print(f"\n{Colors.BOLD}📧 Created Accounts:{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
            for account in self.accounts:
                print(f"Email:    {Colors.OKGREEN}{account['email']}{Colors.ENDC}")
                print(f"Password: {Colors.OKGREEN}{account['password']}{Colors.ENDC}")
                print(f"Name:     {Colors.OKBLUE}{account['full_name']}{Colors.ENDC}")
                print(f"Created:  {Colors.OKBLUE}{account['created_at']}{Colors.ENDC}")
                print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")

def main():
    """Main entry point"""
    try:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        if count < 1:
            count = 1
        
        creator = GmailCreator()
        creator.create_multiple_accounts(count)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Process interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except ValueError:
        print(f"{Colors.FAIL}Error: Please provide a valid number of accounts{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == '__main__':
    main()
