from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.clock import Clock
import os

# --------- Main TrueCall Kivy App (Hackathon Demo) ---------
class TruecallApp(App):
    def build(self):
        from kivy.uix.widget import Widget
        from kivy.graphics import Color, RoundedRectangle

        bg_color = (0.97, 0.97, 0.98, 1)
        accent_color = (0.0, 0.48, 1.0, 1)
        button_radius = [20]

        class RoundedButton(Button):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.background_normal = ''
                self.background_color = accent_color
                self.color = (1, 1, 1, 1)
                self.font_size = 20
                self.size_hint = (1, None)
                self.height = 50
                with self.canvas.before:
                    Color(*accent_color)
                    self.rect = RoundedRectangle(radius=button_radius)
                self.bind(pos=self.update_rect, size=self.update_rect)
            def update_rect(self, *args):
                self.rect.pos = self.pos
                self.rect.size = self.size

        class Card(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = 'vertical'
                self.padding = [20, 20, 20, 20]
                self.spacing = 15
                with self.canvas.before:
                    Color(*bg_color)
                    self.rect = RoundedRectangle(radius=[30], pos=self.pos, size=self.size)
                self.bind(pos=self.update_rect, size=self.update_rect)
            def update_rect(self, *args):
                self.rect.pos = self.pos
                self.rect.size = self.size

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        card = Card()

        card.add_widget(Label(text='TrueCall: Hackathon Demo', font_size=34, color=(0.1,0.15,0.35,1), size_hint=(1, 0.12)))

        # Status label (top, large)
        self.status_label = Label(
            text='Welcome! Enter business call details below.',
            font_size=20,
            color=(0.08, 0.2, 0.5, 1),
            size_hint=(1, 0.11),
            halign='center', valign='middle'
        )
        self.status_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        card.add_widget(self.status_label)

        # --- Business Call Fields ---
        card.add_widget(Label(text='Caller Name (Business)', font_size=17, color=(0,0,0,1), size_hint=(1, None), height=25))
        self.caller_name_input = TextInput(
            text='Acme Bank', multiline=False, font_size=17, size_hint=(1, None), height=38,
        )
        card.add_widget(self.caller_name_input)

        card.add_widget(Label(text='Business Logo URL', font_size=17, color=(0,0,0,1), size_hint=(1, None), height=25))
        self.logo_url_input = TextInput(
            text='', multiline=False, font_size=17, size_hint=(1, None), height=38,
        )
        card.add_widget(self.logo_url_input)

        card.add_widget(Label(text='Video Intro URL (optional)', font_size=17, color=(0,0,0,1), size_hint=(1, None), height=25))
        self.video_url_input = TextInput(
            text='', multiline=False, font_size=17, size_hint=(1, None), height=38,
        )
        card.add_widget(self.video_url_input)

        card.add_widget(Label(text='Caller (phone number)', font_size=17, color=(0,0,0,1), size_hint=(1, None), height=25))
        self.caller_phone_input = TextInput(
            text='+6112345678', multiline=False, font_size=17, size_hint=(1, None), height=38,
        )
        card.add_widget(self.caller_phone_input)

        card.add_widget(Label(text='Recipient (phone number)', font_size=17, color=(0,0,0,1), size_hint=(1, None), height=25))
        self.recipient_input = TextInput(
            text='+6198765432', multiline=False, font_size=17, size_hint=(1, None), height=38,
        )
        card.add_widget(self.recipient_input)

        # Simulate Verified Call Button
        simulate_btn = RoundedButton(text='Simulate Verified Call')
        simulate_btn.bind(on_press=self.simulate_verified_call)
        card.add_widget(simulate_btn)

        # --- For call result screen ---
        self.call_result_label = Label(text="", font_size=20, color=(0.15, 0.3, 0.15, 1), size_hint=(1, 0.12), halign='center', valign='top')
        self.call_result_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        card.add_widget(self.call_result_label)

        # For showing branding logo
        self.logo_img = None
        self.video_label = Label(text="", font_size=16, color=(0.3, 0.15, 0.15, 1), size_hint=(1, 0.09), halign='center', valign='top')
        self.video_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        card.add_widget(self.video_label)

        root.add_widget(card)
        return root

    def simulate_verified_call(self, instance):
        # Get the entered business details
        caller_name = self.caller_name_input.text.strip() or 'Unknown Caller'
        logo_url = self.logo_url_input.text.strip()
        video_url = self.video_url_input.text.strip()
        caller_phone = self.caller_phone_input.text.strip()
        recipient = self.recipient_input.text.strip()

        # Simulate API verification (just always "verified" in demo)
        self.status_label.text = f"Simulating incoming call from '{caller_name}' to '{recipient}'\n[Caller is VERIFIED]"
        call_text = f"[Verified Business Call]\nFrom: {caller_name}\n({caller_phone})\n\nTo: {recipient}\n"
        self.call_result_label.text = call_text

        # Show logo (clear older logo if present)
        if self.logo_img:
            self.call_result_label.parent.remove_widget(self.logo_img)
            self.logo_img = None
        if logo_url:
            try:
                self.logo_img = AsyncImage(source=logo_url, size_hint=(1, None), height=100)
                # Insert logo just after call_result_label
                idx = self.call_result_label.parent.children.index(self.call_result_label)
                self.call_result_label.parent.add_widget(self.logo_img, index=idx)
            except Exception as e:
                self.call_result_label.text += "\n(Logo display failed)"
        else:
            self.call_result_label.text += "\n[No logo provided]"

        # Show video intro
        if video_url:
            self.video_label.text = f"Video Intro: {video_url}\n[Copy URL to browser]"
        else:
            self.video_label.text = ""

        # Optionally, popup for dramatic incoming call effect
        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(
            text=f"Incoming Call\nVERIFIED\n\nBusiness: {caller_name}",
            font_size=22, color=(0.1, 0.45, 0.2, 1), size_hint=(1, None), height=70
        ))
        if logo_url:
            try:
                popup_content.add_widget(AsyncImage(source=logo_url, size_hint=(1, None), height=100))
            except: pass
        popup_content.add_widget(Label(
            text=f"To: {recipient}", font_size=18, color=(0.06,0.28,0.45,1), size_hint=(1, None), height=40
        ))
        if video_url:
            popup_content.add_widget(Label(
                text=f"Video Intro: {video_url}\n(copy to browser)",
                font_size=16, color=(0.25,0.18,0.42,1), size_hint=(1, None), height=40
            ))
        popup_content.add_widget(Label(
            text="Status: VERIFIED\nSafe to answer.", font_size=18, color=(0.07,0.59,0.24,1), size_hint=(1, None), height=40
        ))
        popup = Popup(title="Incoming Call - Branded Business Card",
                      content=popup_content,
                      size_hint=(0.96, 0.85))
        popup.open()

if __name__ == '__main__':
    TruecallApp().run()