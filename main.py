import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from pyzbar.pyzbar import decode

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel

class BarcodeScannerApp(MDApp):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(MDLabel(text='Scan Barcode:', halign='center', font_style='H5'))
        self.camera = Camera(play=True)
        layout.add_widget(self.camera)
        self.scan_button = Button(text='Scan', size_hint=(None, None), size=(100, 50))
        self.scan_button.bind(on_press=self.scan)
        layout.add_widget(self.scan_button)
        self.result_label = MDLabel(text='', halign='center', font_style='Body1')
        layout.add_widget(self.result_label)
        return layout

    def scan(self, instance):
        # Take a photo
        image_path = os.path.join(os.getcwd(), 'barcode_image.jpg')
        self.camera.export_to_png(image_path)

        # Scan the barcode
        barcode_data = self.scan_barcode(image_path)
        if barcode_data:
            # Scrape brand name
            url = "https://go-upc.com/search?q=" + barcode_data
            brand = self.scrape_brand_name(url)
            if brand:
                self.result_label.text = "Brand: " + brand
            else:
                self.result_label.text = "Brand name not found"
        else:
            self.result_label.text = "No barcode detected"

    def scan_barcode(self, image_path):
        with Image.open(image_path) as img:
            img_gray = img.convert('L')
            decoded_objects = decode(img_gray)
            if decoded_objects:
                barcode_data = [obj.data.decode('utf-8') for obj in decoded_objects if obj.data]
                return ', '.join(barcode_data) if barcode_data else None
            else:
                return None

    def scrape_brand_name(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                brand_cell = row.find('td', string='Brand')
                if brand_cell:
                    brand_name = brand_cell.find_next_sibling('td').text.strip()
                    return brand_name
            return None
        else:
            return None

if __name__ == '__main__':
    BarcodeScannerApp().run()
