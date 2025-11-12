from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from threading import Thread
import requests, webbrowser, urllib.parse, time, os, configparser, httpx, ssl

BG_COLOR = (0.98, 0.97, 0.95, 1)
DEEP_BLUE = (0.05, 0.13, 0.28, 1)          # #0D2047 (TrueCall dark blue)
BRIGHT_BLUE = (0.0, 0.31, 0.96, 1)         # #004EF4 (TrueCall bright blue)
ORANGE = (0.95, 0.28, 0.12, 1)             # #F1471E (TrueCall orange)
GREEN = (0.06, 0.75, 0.13, 1)               # #0FCB2D (TrueCall green)
RED = (0.86, 0.15, 0.15, 1)                 # #DB2424 (TrueCall red)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
http_client = httpx.Client(verify=ctx)
from langchain_openai import ChatOpenAI

config = configparser.ConfigParser()
config.read('config.ini')
AI_HOST = config.get('AI', 'host')
AI_MODEL = config.get('AI', 'model')
API_KEY = config.get('API', 'api_key')
RAPID_API_HOST = config.get('RAPID_API', 'host')
RAPID_API_KEY = config.get('RAPID_API', 'key')
RAPID_API_LOCATION_RETRIEVAL_URL = config.get('RAPID_API', 'location_retrieval_url')
RAPID_API_NUMBER_VERIFICATION_URL = config.get('RAPID_API', 'number_verification_url')
RAPID_API_OAUTH2_URL = config.get('RAPID_API', 'oauth2_url')
RAPID_API_OPENID_CONFIGURATION_URL = config.get('RAPID_API', 'openid_configuration_url')

llm = ChatOpenAI(
    api_key=API_KEY,
    base_url=AI_HOST,
    http_client=http_client,
    model=AI_MODEL
)

def ai_describe_location(location_text):
    messages = [
        ("system", "You are a helpful assistant that takes a technical location string for mobile networks with time, area type, coordinates, and boundary points if present, and returns the location or area where the number is located in easy to understand for a customer. no need to mention coordinates or technical terms"),
        ("human", location_text),
    ]
    response = llm.invoke(messages)
    return response.content if response and hasattr(response, "content") else ""  

class TruecallApp(App):
    def build(self):
        from kivy.graphics import Color, RoundedRectangle, Rectangle

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        # Set BG_COLOR for the entire app window

        root.clearcolor = BG_COLOR

        with root.canvas.before:
            Color(*BG_COLOR)
            root.bg_rect = Rectangle(pos=root.pos, size=root.size)
        def update_root_bg_rect(instance, value):
            root.bg_rect.pos = root.pos
            root.bg_rect.size = root.size
        root.bind(pos=update_root_bg_rect, size=update_root_bg_rect)

        # --------- TOP LOGO ---------
        header = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=100)
        with header.canvas.before:
            Color(*BG_COLOR)
            header.bg_rect = Rectangle(pos=header.pos, size=header.size)

        def update_bg_rect(instance, value):
            header.bg_rect.pos = header.pos
            header.bg_rect.size = header.size

        header.bind(pos=update_bg_rect, size=update_bg_rect)

        logo_img = AsyncImage(source='truecall_logo.png', size_hint=(None, None), size=(220, 75), allow_stretch=True)
        header.add_widget(logo_img)
        root.add_widget(header)
        # ...existing code...

        # --------- MAIN CARD ---------
        card = BoxLayout(orientation='vertical', spacing=14, padding=[22,18,22,18])
        with card.canvas.before:
            Color(*BG_COLOR)
            card.rect = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda inst,v: card.rect.__setattr__('pos',v), size=lambda inst,v: card.rect.__setattr__('size',v))
        
        # --------- BUSINESS CARD ---------
        self.business_card_box = BoxLayout(orientation='horizontal', size_hint=(1,None), height=120, padding=[0,0,0,0], spacing=18)
        self.business_logo = AsyncImage(source='', size_hint=(None,None), size=(94,94), allow_stretch=True)
        self.business_info_label = Label(
            text='', font_size=28, color=DEEP_BLUE, bold=True, markup=True,
            halign='left', valign='middle', size_hint=(1,1))
        self.business_info_label.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.business_card_box.add_widget(self.business_logo)
        self.business_card_box.add_widget(self.business_info_label)
        self.business_card_box.opacity = 0 # Hide by default
        card.add_widget(Widget(size_hint=(1,None), height=8)) # Spacer
        card.add_widget(self.business_card_box)
        card.add_widget(Widget(size_hint=(1,None), height=6)) # Spacer

        # --------- STATUS LABEL ---------
        self.status_label = Label(
            text='Welcome! Please log in.', font_size=22, color=DEEP_BLUE, bold=True,
            size_hint=(1, None), height=36, halign='center', valign='middle')
        self.status_label.bind(size=lambda i,v: setattr(i, 'text_size', v))
        card.add_widget(self.status_label)
        card.add_widget(Widget(size_hint=(1,None), height=8)) # Spacer

        # --------- LOCATION LABEL ---------
        self.location_label = Label(
            text='Location: Awaiting verification...', font_size=17, color=DEEP_BLUE,
            size_hint=(1, None), height=40, halign='center', valign='middle')
        self.location_label.bind(size=lambda i,v: setattr(i, 'text_size', v))
        card.add_widget(self.location_label)
        
        # --------- AI SUMMARY LABEL ---------
        self.ai_label = Label(
            text="",
            font_size=17,
            color=DEEP_BLUE,
            size_hint=(1, None),
            height=32,
            halign='center',
            valign='top'
        )
        self.ai_label.bind(size=lambda i,v: setattr(i, 'text_size', v))
        card.add_widget(self.ai_label)
        card.add_widget(Widget(size_hint=(1,None), height=12)) # Spacer  

        # --------- PHONE INPUT ---------
        card.add_widget(Label(text='Phone Number', font_size=18, color=DEEP_BLUE, size_hint=(1,None), height=28))
        self.phone_input = TextInput(
            text='', multiline=False, font_size=21, size_hint=(1,None),
            height=44, background_color=(1,1,1,1), foreground_color=DEEP_BLUE
        )
        self.phone_input.bind(text=self.on_phone_change)
        card.add_widget(self.phone_input)
        card.add_widget(Widget(size_hint=(1,None), height=4))  

        # --------- LOGIN BUTTON ---------
        login_btn = Button(
            text='Login (Auto Verify)', font_size=20,
            size_hint=(1,None), height=52,
            background_color=BRIGHT_BLUE, color=(1,1,1,1), bold=True
        )
        login_btn.bind(on_press=self.login)
        card.add_widget(login_btn)

        # --------- AUTH CODE INPUT ---------
        # card.add_widget(Label(text='Auth Code', font_size=18, color=DEEP_BLUE, size_hint=(1,None), height=26))
        self.auth_code_input = TextInput(
            text='', multiline=False, font_size=21, size_hint=(1,None), height=44,
            background_color=(1,1,1,1), foreground_color=DEEP_BLUE
        )
        card.add_widget(self.auth_code_input)

        # --------- SUBMIT AUTH CODE BUTTON ---------
        self.submit_code_btn = Button(
            text='Submit Auth Code & Verify', font_size=20,
            size_hint=(1,None), height=52, background_color=(0.95, 0.28, 0.12, 1), color=(1,1,1,1), bold=True, background_normal=''
        )
        self.submit_code_btn.bind(on_press=self.submit_auth_code)
        self.submit_code_btn.disabled = True
        card.add_widget(self.submit_code_btn)

        # --------- FETCH LOCATION BUTTON ---------
        location_btn = Button(
            text='Fetch Location', font_size=20, size_hint=(1,None), height=52,
            background_color=BRIGHT_BLUE, color=(1,1,1,1), bold=True
        )
        location_btn.bind(on_press=self.fetch_location)
        card.add_widget(location_btn)
        card.add_widget(Widget(size_hint=(1,None), height=8))  

        # --------- SIMULATE CALL BUTTON ---------
        sim_btn = Button(
            text='Simulate Call', font_size=20, size_hint=(1,None), height=52,
            background_color=(0.95, 0.28, 0.12, 1), color=(1,1,1,1), bold=True, background_normal=''
        )
        sim_btn.bind(on_press=self.simulate_call)
        card.add_widget(sim_btn)
        card.add_widget(Widget(size_hint=(1,None), height=13))

        # --------- DATA / CONFIG ---------
        self.session_id = None
        self.qod_active = False
        self.client_id = None
        self.client_secret = None
        self.auth_endpoint = None
        self.token_endpoint = None
        self.access_token = None
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.api_key = self.config.get('API','rapidapi_key')
        self.business_map = {}
        if self.config.has_section('BUSINESS'):
            for number in self.config.options('BUSINESS'):
                val = self.config.get('BUSINESS', number)
                parts = [x.strip() for x in val.split(',')]
                name = parts[0] if len(parts) > 0 else ''
                logo = parts[1] if len(parts) > 1 else ''
                self.business_map[number] = {'name': name, 'logo': logo}
        self.hide_business_card()
        root.add_widget(card)
        return root  

    def on_phone_change(self, instance, value):
        self.hide_business_card()  

    def show_business_card(self, number):
        info = self.business_map.get(number)
        if info:
            self.business_info_label.text = f"[b]{info['name']}[/b]\n[color=0D2047][b]({number})[/b][/color]"
            self.business_info_label.markup = True
            self.business_logo.source = info['logo'] if info['logo'] else ''
            self.business_logo.opacity = 1 if info['logo'] else 0
            self.business_card_box.opacity = 1
        else:
            self.hide_business_card()  

    def hide_business_card(self):
        self.business_info_label.text = ''
        self.business_logo.source = ''
        self.business_logo.opacity = 0
        self.business_card_box.opacity = 0

    # ------------ API FLOW ------------
    def check_auth_code(self, dt):
        auth_code_file = 'auth_code.txt'
        elapsed_time = time.time() - self.poll_start
        if os.path.exists(auth_code_file):
            with open(auth_code_file, 'r') as f:
                self.auth_code = f.read().strip()
            if self.auth_code:
                self.auth_code_input.text = self.auth_code
                self.submit_code_btn.disabled = False
                self.status_label.text = f'Auth code captured automatically! Submitting...'
                Clock.unschedule(self.check_auth_code)
                Clock.schedule_once(lambda dt: self.submit_auth_code(None), 1)
                os.remove(auth_code_file)
            else:
                if elapsed_time >= self.poll_timeout:
                    self.status_label.text = f'Timeout ({self.poll_timeout}s) waiting for auth code. Please enter manually and submit.'
                    self.submit_code_btn.disabled = False
                    Clock.unschedule(self.check_auth_code)
                else:
                    self.status_label.text = f'Waiting for auth code ({int(elapsed_time)}s)...'

    def poll_for_auth_code(self):
        self.poll_timeout = 30
        self.poll_start = time.time()
        Clock.schedule_interval(self.check_auth_code, 2)
        self.submit_code_btn.disabled = True

    def construct_and_open_auth_url(self):
        phone = self.phone_input.text
        redirect_uri = 'http://localhost:8080/callback'
        state = 'super-secret-state'
        scope = 'number-verification:verify'
        params = {
            'scope': scope, 'state': state, 'response_type': 'code',
            'client_id': self.client_id, 'redirect_uri': redirect_uri,
            'login_hint': phone
        }
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.auth_endpoint}?{query_string}"
        self.status_label.text = 'Opening login page in browser...'
        print(f'[Auth] URL: {auth_url}')
        webbrowser.open(auth_url)
        self.poll_for_auth_code()

    def fetch_endpoints(self):
        headers = {
            'X-RapidAPI-Host': RAPID_API_HOST,
            'X-RapidAPI-Key': RAPID_API_KEY
        }
        try:
            url = RAPID_API_OPENID_CONFIGURATION_URL
            print(f'Fetching endpoints from: {url}')
            response = requests.get(url, headers=headers, verify=False)
            print(f'Response status: {response.status_code}')
            print(f'Response content: {response.text}')
            response.raise_for_status()
            config = response.json()
            self.auth_endpoint = config.get('authorization_endpoint')
            self.token_endpoint = config.get('token_endpoint')
            if not self.auth_endpoint or not self.token_endpoint:
                raise ValueError('Missing endpoints')
            self.status_label.text = 'Endpoints ready. Opening authentication browser...'
            print(f'Auth Endpoint: {self.auth_endpoint}')
            print(f'Token Endpoint: {self.token_endpoint}')
            Clock.schedule_once(lambda dt: self.construct_and_open_auth_url(), 0)
        except Exception as e:
            self.status_label.text = f'Error fetching endpoints. Try again.'
            print(f'Error: {str(e)}')

    def fetch_client_credentials(self):
        headers = {
            'X-RapidAPI-Host': RAPID_API_HOST,
            'X-RapidAPI-Key': RAPID_API_KEY
        }
        try:
            url = RAPID_API_OAUTH2_URL
            print(f'Fetching credentials from: {url}')
            response = requests.get(url, headers=headers, verify=False)
            print(f'Response status: {response.status_code}')
            print(f'Response content: {response.text}')
            response.raise_for_status()
            creds = response.json()
            self.client_id = creds.get('client_id')
            self.client_secret = creds.get('client_secret')
            if not self.client_id or not self.client_secret:
                raise ValueError('Missing client_id/client_secret')
            self.status_label.text = f'Client credentials received. Starting login...'
            print(f'Client ID: {self.client_id}')
            print(f'Client Secret: {self.client_secret[:10]}... (truncated)')
            Clock.schedule_once(lambda dt: self.fetch_endpoints(), 0)
        except Exception as e:
            self.status_label.text = f'Error getting credentials. Check your API key.'
            print(f'Error: {str(e)}')

    def login(self, instance):
        self.status_label.text = 'Connecting to login service...'
        self.location_label.text = 'Location: Awaiting verification...'
        self.ai_label.text = ''
        self.hide_business_card()
        print('[Login] Starting OAuth Flow')
        Clock.schedule_once(lambda dt: self.fetch_client_credentials(), 0)

    def submit_auth_code(self, instance):
        self.auth_code = self.auth_code_input.text.strip()
        if not self.auth_code:
            self.status_label.text = 'Please enter the Auth Code.'
            return
        self.status_label.text = 'Verifying authentication code...'
        print(f'Submitted Auth Code: {self.auth_code}')
        Clock.schedule_once(lambda dt: self.fetch_access_token(), 0)

    def fetch_access_token(self):
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': self.auth_code
        }
        try:
            print(f'Fetching token from: {self.token_endpoint}')
            print(f'Token Request Data: {data}')
            response = requests.post(self.token_endpoint, data=data, verify=False)
            print(f'Response status: {response.status_code}')
            print(f'Response content: {response.text}')
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            if not self.access_token:
                raise ValueError('Missing access_token')
            self.status_label.text = 'Authentication successful.'
            print(f'Access Token: {self.access_token[:20]}... (truncated)')
            self.hide_business_card()
            Clock.schedule_once(lambda dt: self.verify_phone_number(), 0)
        except Exception as e:
            self.status_label.text = f'Authentication failed. Please retry.'
            self.hide_business_card()
            print(f'Error: {str(e)}')

    def verify_phone_number(self):
        phone = self.phone_input.text
        headers = {
            'Content-Type': 'application/json',
            'X-RapidAPI-Host': RAPID_API_HOST,
            'X-RapidAPI-Key': RAPID_API_KEY,
            'Authorization': f'Bearer {self.access_token}'
        }
        data = {"phoneNumber": phone}
        try:
            url = RAPID_API_NUMBER_VERIFICATION_URL
            print(f'Verifying number at: {url}')
            print(f'Request Headers: {headers}')
            print(f'Request Data: {data}')
            response = requests.post(url, headers=headers, json=data, verify=False)
            print(f'Response status: {response.status_code}')
            print(f'Response content: {response.text}')
            response.raise_for_status()
            verification = response.json()
            if verification.get('devicePhoneNumberVerified', False):
                self.status_label.text = f'Phone number {phone} is logged in.'
                self.hide_business_card()
                Clock.schedule_once(self.fetch_location, 0)
            else:
                self.status_label.text = 'Verification Failed - Phone Number Mismatch.'
                self.hide_business_card()
                print(f'Verification Result: {verification}')
        except requests.RequestException as e:
            self.status_label.text = f'Phone verification failed. Please retry.'
            self.hide_business_card()
            print(f'Error: {str(e)}')

    def fetch_location(self, instance):
        phone = self.phone_input.text.strip()
        headers = {
            'Content-Type': 'application/json',
            'X-RapidAPI-Host': RAPID_API_HOST,
            'X-RapidAPI-Key': RAPID_API_KEY
        }
        data = {"device": {"phoneNumber": phone}}
        try:
            url = RAPID_API_LOCATION_RETRIEVAL_URL
            print(f'Fetching location from: {url}')
            response = requests.post(url, headers=headers, json=data, verify=False)
            print(f'Response status: {response.status_code}')
            print(f'Response content: {response.text}')
            response.raise_for_status()
            result = response.json()
            last_time = result.get('lastLocationTime', 'N/A')
            area = result.get('area', {})
            area_type = area.get('areaType', 'N/A')
            location_text = ""
            if area_type == "CIRCLE":
                center = area.get('center', {})
                lat = center.get('latitude', 'N/A')
                lon = center.get('longitude', 'N/A')
                radius = area.get('radius', 'N/A')
                location_text = (
                    f"Type: {area_type}, "
                    f"Latitude: {lat}, Longitude: {lon}, Radius: {radius} m"
                )
            elif area_type == "POLYGON":
                boundary = area.get('boundary', [])
                boundary_points = "\n".join(
                    [f"Point {i+1}: Lat {pt.get('latitude', 'N/A')}, Lon {pt.get('longitude', 'N/A')}"
                     for i, pt in enumerate(boundary)]
                )
                location_text = (
                    f"Last Location Time: {last_time}\n"
                    f"Type: {area_type}\n"
                    f"Boundary Points:\n{boundary_points}"
                )
            else:
                location_text = (
                    f"Last Location Time: {last_time}\n"
                    f"Type: {area_type}\n"
                    f"Location info not available."
                )
            self.location_label.text = location_text
            self.ai_label.text = ""
            self.status_label.text = "Location retrieved successfully."
            # Show business card only if location found
            if last_time != 'N/A':
                self.show_business_card(phone)
            else:
                self.hide_business_card()
            # Run AI summary in background
            def run_ai_summary():
                try:
                    ai_summary = ai_describe_location(location_text)
                    print("\n==== AI Description ====\n", ai_summary, "\n========================")
                    Clock.schedule_once(lambda dt: self.show_ai_summary(ai_summary), 0)
                except Exception as e:
                    print("AI summary error:", str(e))
                    Clock.schedule_once(lambda dt: self.show_ai_summary(
                        "AI description not available."), 0)
            Thread(target=run_ai_summary).start()
        except requests.RequestException as e:
            self.location_label.text = f'Location Error: {str(e)}'
            self.status_label.text = "Failed to retrieve location."
            self.ai_label.text = ""
            self.hide_business_card()
            print(f'Location fetch error: {str(e)}')

    def show_ai_summary(self, summary):
        if not summary or not summary.strip():
            summary = "Sorry, could not generate a description."
        self.ai_label.text = f"[AI]: {summary}"

    def simulate_call(self, instance):
        number = self.phone_input.text.strip()
        info = self.business_map.get(number)
        caller_name = info['name'] if info else "Unknown Caller"
        logo_url = info['logo'] if info else ''
        # Popup styled like iPhone incoming call
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.image import AsyncImage
        from kivy.uix.button import Button
        from kivy.uix.label import Label  
        popup_content = BoxLayout(orientation='vertical', padding=0, spacing=18)

        # Add the logo at the very top
        logo_anchor = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None), height=70)
        logo_img = AsyncImage(source='truecall_logo.png', size_hint=(None, None), size=(180, 60), allow_stretch=True)
        logo_anchor.add_widget(logo_img)
        popup_content.add_widget(logo_anchor)
        # Show verified banner if mapped
        if info:
            popup_content.add_widget(Label(
                text="[b]Verified[/b]",
                font_size=26,
                color=GREEN,  # green
                markup=True,
                size_hint=(1, None),
                height=40,
                halign='center',
                valign='middle'
            ))
        else:  # Phone number mismatch, possible scam
            popup_content.add_widget(Label(
                text="[b]Fraudulent[/b]",
                font_size=26,
                color=RED,  # Bold orange
                markup=True,
                size_hint=(1, None),
                height=40,
                halign='center',
                valign='middle'
            ))
        # Large business logo if available
        if logo_url:
            try:
                popup_content.add_widget(AsyncImage(source=logo_url, size_hint=(1, None), height=90))
            except: pass
        # Caller name
        popup_content.add_widget(Label(
            text=caller_name,
            font_size=32,
            color=DEEP_BLUE,
            bold=True,
            size_hint=(1, None),
            height=54,
            halign='center',
            valign='middle'
        ))
        # Caller number
        popup_content.add_widget(Label(
            text=number,
            font_size=21,
            color=DEEP_BLUE,
            size_hint=(1, None),
            height=36,
            halign='center',
            valign='middle'
        ))
        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=40,
            size_hint=(None, None),
            width=300, height=68,
            padding=[0, 0, 0, 0]
        )
        btn_decline = Button(
            text='Decline',
            background_color=RED, color=(1,1,1,1),
            font_size=22, size_hint=(None, None), width=120, height=68, background_normal=''
        )
        btn_accept = Button(
            text='Accept',
            background_color=GREEN, color=(1,1,1,1),
            font_size=22, size_hint=(None, None), width=120, height=68, background_normal=''
        )
        btn_layout.add_widget(btn_accept)
        btn_layout.add_widget(btn_decline)
        centered_buttons = AnchorLayout(
            anchor_x='center', anchor_y='center',
            size_hint=(1, None), height=68
        )
        centered_buttons.add_widget(btn_layout)
        popup_content.add_widget(centered_buttons)
        # Bottom status for verified/unverified
        status_text = "[b]Status: VERIFIED - Safe to answer.[/b]" if info else "[b]Status: FRAUDULENT - Do NOT answer.[/b]"
        popup_content.add_widget(Label(
            text=status_text,
            font_size=18,
            color=GREEN if info else RED,
            markup=True,
            size_hint=(1, None),
            height=36,
            halign='center',
            valign='middle'
        ))
        # Container for iPhone-like gradient background
        popup_bg = BoxLayout(orientation='vertical')
        popup_bg.add_widget(popup_content)
        from kivy.graphics import Color, Rectangle
        with popup_bg.canvas.before:
            Color(*BG_COLOR) 
            popup_bg.rect = Rectangle(pos=popup_bg.pos, size=popup_bg.size)
        popup_bg.bind(pos=lambda inst,v: popup_bg.rect.__setattr__('pos',v),
                    size=lambda inst,v: popup_bg.rect.__setattr__('size',v))
        popup = Popup(
            title="",
            content=popup_bg,
            size_hint=(0.76, 0.66),
            separator_height=0,
            auto_dismiss=True
        )
        popup.open()

if __name__ == '__main__':
    TruecallApp().run()