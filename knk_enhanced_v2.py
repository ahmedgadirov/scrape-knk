import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import re
from time import sleep
import random
import time
import os
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Enhanced logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ADD YOUR URLS HERE - Replace this empty list with your URLs
urls = [
"https://kontakt.az/adapter-apple-30w-usb-c-power-a2164-mw2g3zm-a",
"https://kontakt.az/adapter-apple-35w-dual-usb-c-power-a2676-mw2k3zm-a",
"https://kontakt.az/adapter-apple-96w-usb-c-mx0j2zm-a",
"https://kontakt.az/adapter-apple-dual-usb-c-mnwp3zm-a",
"https://kontakt.az/apple-12w-power-adapter-md836",
"https://kontakt.az/apple-12w-usb-adapter-mgn03za-a",
"https://kontakt.az/apple-140w-usb-c-power-adapter-mlyu3zm-a",
"https://kontakt.az/apple-20w-usb-c-adapter-mhje3zm-a",
"https://kontakt.az/apple-30w-usb-c-adapter-macbook-12",
"https://kontakt.az/apple-40mm-black-unity-sport-band-m-l-muq63zm-a",
"https://kontakt.az/apple-41-mm-evergreen-magnetic-link-m-l-mtj63zm-a",
"https://kontakt.az/apple-41-mm-silver-milanese-loop-ml753zm-a",
"https://kontakt.az/apple-41-mm-taupe-magnetic-link-mtj83zm-a",
"https://kontakt.az/apple-41mm-black-black-nike-sport-band-mpgn3zm",
"https://kontakt.az/apple-41mm-blue-flame-nike-sport-band-m-l-muuu3zm-a",
"https://kontakt.az/apple-41mm-cargo-khaki-nike-sport-band-m-l-muuw3zm-a",
"https://kontakt.az/apple-41mm-clay-sport-band-m-l-mt3a3zm-a",
"https://kontakt.az/apple-41mm-desert-stone-nike-sport-band-m-l-muur3zm-a",
"https://kontakt.az/apple-41mm-gold-milanese-loop-ml733zm-a",
"https://kontakt.az/apple-41mm-light-pink-sport-band-m-l-mt303zm-a",
"https://kontakt.az/apple-41mm-magic-ember-nike-sport-band-m-l-muuy3zm-a",
"https://kontakt.az/apple-41mm-midnight-sky-nike-sport-band-m-l-muup3zm-a",
"https://kontakt.az/apple-41mm-midnight-sport-band-m-l-mt2t3zm-a",
"https://kontakt.az/apple-41mm-mulberry-sport-band-m-l-mt343zm-a",
"https://kontakt.az/apple-41mm-pride-edition-sport-band-m-l-muq23zm-a",
"https://kontakt.az/apple-41mm-pure-platinum-nike-sport-band-m-l-muul3zm-a",
"https://kontakt.az/apple-41mm-starlight-sport-band-m-l-mt2v3zm-a",
"https://kontakt.az/apple-41mm-storm-blue-sport-band-m-l-mt2x3zm-a",
"https://kontakt.az/apple-41mm-winter-blue-sport-band-m-l-mt363zm-a",
"https://kontakt.az/apple-42-mm-blue-cloud-sport-loop-mxkx3zm-a",
"https://kontakt.az/apple-42-mm-ink-sport-loop-mxkw3zm-a",
"https://kontakt.az/apple-42-mm-ultramarine-sport-loop-mxl03zm-a",
"https://kontakt.az/apple-42mm-black-sport-band-s-m-mxlj3zm-a",
"https://kontakt.az/apple-42mm-blue-flame-nike-sport-band-s-m-myjw3zm-a",
"https://kontakt.az/apple-42mm-cargo-khaki-nike-sport-band-s-m-myjy3zm-a",
"https://kontakt.az/apple-42mm-denim-sport-band-s-m-mxle3zm-a",
"https://kontakt.az/apple-42mm-desert-stone-nike-sport-band-s-m-myjr3zm-a",
"https://kontakt.az/apple-42mm-gold-milanese-loop-mxmn3zm-a",
"https://kontakt.az/apple-42mm-light-blush-sport-band-s-m-mxln3zm-a",
"https://kontakt.az/apple-42mm-magic-ember-nike-sport-band-s-m-myl23zm-a",
"https://kontakt.az/apple-42mm-midnight-sky-nike-sport-band-s-m-myjp3zm-a",
"https://kontakt.az/apple-42mm-natural-milanese-loop-mxmm3zm-a",
"https://kontakt.az/apple-42mm-plum-sport-band-s-m-mxlc3zm-a",
"https://kontakt.az/apple-42mm-plum-sport-loop-mxky3zm-a",
"https://kontakt.az/apple-42mm-pure-platinum-nike-sport-band-s-m-myjm3zm-a",
"https://kontakt.az/apple-42mm-slate-milanese-loop-mxmp3zm-a",
"https://kontakt.az/apple-42mm-starlight-sport-band-s-m-mxll3zm-a",
"https://kontakt.az/apple-42mm-stone-gray-s-m-mxlg3zm-a",
"https://kontakt.az/apple-42mm-volt-splash-nike-sport-band-s-m-mxu53zm-a",
"https://kontakt.az/apple-44-mm-black-unity-sport-band-m-l-muq83zm-a",
"https://kontakt.az/apple-45-mm-black-black-nike-sport-band-mph43zm-a",
"https://kontakt.az/apple-45-mm-black-summit-white-nike-sport-loop-mpj13zm-a",
"https://kontakt.az/apple-45-mm-silver-milanese-loop-ml783zm-a",
"https://kontakt.az/apple-45-mm-storm-blue-sport-loop-mplg3zm-a",
"https://kontakt.az/apple-45-mm-umber-leather-link-s-m-mp853zm-a",
"https://kontakt.az/apple-45mm-blue-flame-nike-sport-band-m-l-muv93zm-a",
"https://kontakt.az/apple-45mm-cargo-khaki-nike-sport-band-m-l-muvd3zm-a",
"https://kontakt.az/apple-45mm-clay-sport-band-m-l-mt493zm-a",
"https://kontakt.az/apple-45mm-desert-stone-nike-sport-band-m-l-muv73zm-a",
"https://kontakt.az/apple-45mm-gold-milanese-loop-ml763zm-a",
"https://kontakt.az/apple-45mm-graphite-milanese-loop-ml773zm-a",
"https://kontakt.az/apple-45mm-ink-leather-link-s-m-mp873zm-a",
"https://kontakt.az/apple-45mm-light-pink-sport-band-m-l-mt3v3zm-a",
"https://kontakt.az/apple-45mm-magic-ember-nike-sport-band-m-l-muvf3zm-a",
"https://kontakt.az/apple-45mm-midnight-sky-nike-sport-band-m-l-muv53zm-a",
"https://kontakt.az/apple-45mm-midnight-sport-band-m-l-mt3f3zm-a",
"https://kontakt.az/apple-45mm-mulberry-sport-band-m-l-mt403zm-a",
"https://kontakt.az/apple-45mm-pride-edition-sport-band-m-l-muq43zm-a",
"https://kontakt.az/apple-45mm-pure-platinum-nike-sport-band-m-l-muv13zm-a",
"https://kontakt.az/apple-45mm-starlight-sport-band-m-l-mt3k3zm-a",
"https://kontakt.az/apple-45mm-storm-blue-sport-band-m-l-mt3r3zm-a",
"https://kontakt.az/apple-45mm-summit-white-black-nike-sport-loop-mpj03zm-a",
"https://kontakt.az/apple-45mm-winter-blue-sport-band-m-l-mt443zm-a",
"https://kontakt.az/apple-45w-magsafe-2-adapter-macbook-air-13-md592",
"https://kontakt.az/apple-45w-magsafe-power-adapter-mc747z-a",
"https://kontakt.az/apple-46-mm-gold-milanese-loop-s-m-mc7k4zm-a",
"https://kontakt.az/apple-46-mm-slate-milanese-loop-s-m-mc7l4zm-a",
"https://kontakt.az/apple-46mm-black-sport-band-s-m-mxm23zm-a",
"https://kontakt.az/apple-46mm-blue-cloud-sport-loop-mxl53zm-a",
"https://kontakt.az/apple-46mm-blue-flame-nike-sport-band-s-m-myla3zm-a",
"https://kontakt.az/apple-46mm-cargo-khaki-nike-sport-band-s-m-myld3zm-a",
"https://kontakt.az/apple-46mm-denim-sport-band-s-m-mxlv3zm-a",
"https://kontakt.az/apple-46mm-desert-stone-nike-sport-band-s-m-myl83zm-a",
"https://kontakt.az/apple-46mm-ink-sport-loop-mxl33zm-a",
"https://kontakt.az/apple-46mm-lake-green-sport-band-s-m-mxlq3zm-a",
"https://kontakt.az/apple-46mm-lake-green-sport-loop-mxl83zm-a",
"https://kontakt.az/apple-46mm-magic-ember-nike-sport-band-s-m-mylf3zm-a",
"https://kontakt.az/apple-46mm-midnight-sky-nike-sport-band-s-m-myl63zm-a",
"https://kontakt.az/apple-46mm-plum-sport-band-s-m-mxlt3zm-a",
"https://kontakt.az/apple-46mm-plum-sport-loop-mxl63zm-a",
"https://kontakt.az/apple-46mm-pure-platinum-nike-sport-band-s-m-myl43zm-a",
"https://kontakt.az/apple-46mm-slate-milanese-loop-s-m-mc7l4zm-a",
"https://kontakt.az/apple-46mm-starlight-sport-band-s-m-mxm63zm-a",
"https://kontakt.az/apple-46mm-stone-gray-sport-band-s-m-mxlx3zm-a",
"https://kontakt.az/apple-46mm-ultramarine-sport-loop-mxl73zm-a",
"https://kontakt.az/apple-46mm-volt-splash-nike-sport-band-s-m-mxu73zm-a",
"https://kontakt.az/apple-49-mm-blue-alphine-loop-medium-mt5l3zm-a",
"https://kontakt.az/apple-49-mm-midnight-ocean-band-extension-mqef3zm-a",
"https://kontakt.az/apple-49-mm-orange-alpine-loop-small-mqdy3zm-a",
"https://kontakt.az/apple-49-mm-orange-beige-trail-loop-m-l-mt5x3zm-a",
"https://kontakt.az/apple-49-mm-starlight-alpine-loop-small-mqe53zm-a",
"https://kontakt.az/apple-49mm-black-ocean-band-natural-titanium-finish-mxtl3zm-a",
"https://kontakt.az/apple-49mm-black-titanium-milanese-loop-m-mxkg3zm-a",
"https://kontakt.az/apple-49mm-blue-black-trail-loop-m-l-mt623zm-a",
"https://kontakt.az/apple-49mm-green-gray-trail-loop-m-l-mt603zm-a",
"https://kontakt.az/apple-49mm-ice-blue-ocean-natural-titanium-finish-mxtf3zm-a",
"https://kontakt.az/apple-49mm-indigo-alpine-loop-medium-mt5q3zm-a",
"https://kontakt.az/apple-49mm-navy-ocean-band-natural-titanium-finish-mxth3zm-a",
"https://kontakt.az/apple-49mm-olive-alpine-loop-medium-mt5u3zm-a",
"https://kontakt.az/apple-5w-power-adapter-md813-original",
"https://kontakt.az/apple-5w-power-adapter-mgn13zm-a",
"https://kontakt.az/apple-60w-magsafe-2-adapter-macbook-pro-15-md565",
"https://kontakt.az/apple-60w-magsafe-power-adapter-mc461z-a",
"https://kontakt.az/apple-61w-usb-c-adapter-macbook-pro-13-mrw22",
"https://kontakt.az/apple-67w-usb-c-power-adapter-mku63zm-a",
"https://kontakt.az/apple-70w-usb-c-power-adapter-mqln3zm-a",
"https://kontakt.az/apple-85w-magsafe-2-power-adapter-md506z-a",
"https://kontakt.az/apple-85w-magsafe-power-adapter-mc556z-b",
"https://kontakt.az/apple-airtag-1-pack-mx532ru-a",
"https://kontakt.az/apple-airtag-4-pack-mx542ru-a",
"https://kontakt.az/apple-airtag-finewoven-key-ring-black-mt2h3zm-a",
"https://kontakt.az/apple-airtag-finewoven-key-ring-coral-mt2m3zm-a",
"https://kontakt.az/apple-airtag-finewoven-key-ring-mulberry-mt2j3zm-a",
"https://kontakt.az/apple-airtag-finewoven-key-ring-pacific-blue-mt2k3zm-a",
"https://kontakt.az/apple-airtag-finewoven-key-ring-taupe-mt2l3zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-baltic-blue-mhj23zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-brown-mmfa3zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-midnight-mmf93zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-red-mk103zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-saddle-brown-mx4m2zm-a",
"https://kontakt.az/apple-airtag-leather-key-ring-wisteria-mmfc3zm-a",
"https://kontakt.az/apple-airtag-loop-deep-navy-mhj03zm-a",
"https://kontakt.az/apple-airtag-loop-electric-orange-mk0x3zm-a",
"https://kontakt.az/apple-airtag-loop-pink-citrus-mlyy3zm-a",
"https://kontakt.az/apple-airtag-loop-white-mx4f2zm-a",
"https://kontakt.az/apple-band-40-mm-sport-band-cornflower-mv692zm-a",
"https://kontakt.az/apple-band-40-mm-sport-loop-cornflower-mv9e2zm-a",
"https://kontakt.az/apple-band-40-mm-sport-loop-olive-mjfu3zm-a",
"https://kontakt.az/apple-band-40-mm-sport-loop-sunflower-mjft3zm-a",
"https://kontakt.az/apple-band-40mm-nike-sport-band-anthracite-black-mx8c2zm-a",
"https://kontakt.az/apple-band-42-mm-women-nylon-blue-mqvu2zm-a",
"https://kontakt.az/apple-band-42-mm-woven-nylon-black-mqvr2zm-a",
"https://kontakt.az/apple-band-44-mm-sport-loop-olive-mjg13zm-a",
"https://kontakt.az/apple-band-44mm-nike-sport-band-hasta-silver-mj6k3zm-a",
"https://kontakt.az/apple-bundle",
"https://kontakt.az/apple-homepod",
"https://kontakt.az/apple-homepod-mini",
"https://kontakt.az/apple-homepod-mini-my5g2ll-a-space-gray",
"https://kontakt.az/apple-imac-21-5-mrt32",
"https://kontakt.az/apple-imac-24-mgpc3ru-a-silver",
"https://kontakt.az/apple-imac-24-mgpm3ru-a-pink",
"https://kontakt.az/apple-imac-24-mjv93ru-a-blue",
"https://kontakt.az/apple-imac-24-zkmjv83ru-a-green",
"https://kontakt.az/apple-imac-27-mxwu2ru-a",
"https://kontakt.az/apple-ipad-air-2019-wi-fi-64gb-space-grey",
"https://kontakt.az/apple-iphone-16-pro-max",
"https://kontakt.az/apple-iphone-lightning-dock-black",
"https://kontakt.az/apple-iphone-lightning-dock-silver",
"https://kontakt.az/apple-lightning-to-3-5mm-audio-cable-1-2m-mxk22zm-a",
"https://kontakt.az/apple-lightning-to-av-adapter-md826",
"https://kontakt.az/apple-lightning-to-headphone-jack-adapter-mmx62zm-a",
"https://kontakt.az/apple-lightning-to-usb-3-camera-adapter-model-a1619-mx5j3zm-a",
"https://kontakt.az/apple-lightning-usb-cable-0-5m-me291",
"https://kontakt.az/apple-lightning-usb-cable-1m-mxly2",
"https://kontakt.az/apple-lightning-usb-cable-2m-md819-original",
"https://kontakt.az/apple-mac-mini-mmfk3ru-a",
"https://kontakt.az/apple-mac-studio-mqh73ru-a",
"https://kontakt.az/apple-macbook-air-13-mvfm2",
"https://kontakt.az/apple-macbook-air-13-mwtj2ua-a",
"https://kontakt.az/apple-macbook-air-13-zkz15y000kq-starlight",
"https://kontakt.az/apple-macbook-air-13-zkz160000kq-midnight",
"https://kontakt.az/apple-macbook-air13-zkz15s000mp-space-grey",
"https://kontakt.az/apple-macbook-pro-13-zkz11b0004p-space-gray",
"https://kontakt.az/apple-macbook-pro-13-zkz11b0004v-space-gray",
"https://kontakt.az/apple-macbook-pro-14-mphk3ru-a-silver",
"https://kontakt.az/apple-macbook-pro-14-mrx43ru-a-space-black",
"https://kontakt.az/apple-macbook-pro-16-mk1f3ru-a-silver",
"https://kontakt.az/apple-macbook-pro-16-mvvl2ru-a",
"https://kontakt.az/apple-magic-keyboard-2-mla22",
"https://kontakt.az/apple-magic-keyboard-folio-for-ipad-10th-gen-a2695-mqdp3rs-a",
"https://kontakt.az/apple-magic-keyboard-w-touch-id-and-numeric-keypad-silver-mk2c3rs-a",
"https://kontakt.az/apple-magic-keyboard-w-touch-id-english-black-mmmr3z-a",
"https://kontakt.az/apple-magic-keyboard-w-touch-id-silver-mk293rs-a",
"https://kontakt.az/apple-magic-keyboard-with-numeric-keypad-space-gray",
"https://kontakt.az/apple-magic-keyboard-with-touch-id-mmmr3rs-a",
"https://kontakt.az/apple-magic-mouse-2",
"https://kontakt.az/apple-magic-mouse-2-space-gray",
"https://kontakt.az/apple-magic-mouse-black-mmmq3zm-a",
"https://kontakt.az/apple-magic-mouse-mk2e3",
"https://kontakt.az/apple-magic-trackpad-2",
"https://kontakt.az/apple-magic-trackpad-2-mk2d3zm-a",
"https://kontakt.az/apple-magic-trackpad-black-mmmp3zm-a",
"https://kontakt.az/apple-magsafe-battery-pack-mjwy3zm-a",
"https://kontakt.az/apple-magsafe-charger-mhxh3zm-a",
"https://kontakt.az/apple-magsafe-duo-charger-mhxf3zm-a",
"https://kontakt.az/apple-pencil-1st-gen-mqly3zm-a",
"https://kontakt.az/apple-pencil-pro-mx2d3qn-a",
"https://kontakt.az/apple-pencil-tips-2gen-mlun2zm-a",
"https://kontakt.az/apple-polishing-cloth",
"https://kontakt.az/apple-studio-display-27-mmyw3ru-a",
"https://kontakt.az/apple-studio-display-27-zkmk0u3rua",
"https://kontakt.az/apple-thunderbolt-3-usb-c-cable-0-8m-mq4h2zm-a",
"https://kontakt.az/apple-thunderbolt-4-pro-cable-3m-mwp02zm-a",
"https://kontakt.az/apple-thunderbolt-4-usb-c-pro-cable-1-8m-mn713zm-a",
"https://kontakt.az/apple-thunderbolt-4-usb-c-pro-cable-mu883zm-a",
"https://kontakt.az/apple-tv-4k-128-gb-mn893ru-a",
"https://kontakt.az/apple-tv-4k-32gb-mqd22",
"https://kontakt.az/apple-tv-4k-64-gb-mn873ru-a",
"https://kontakt.az/apple-tv-remote-mjfn3zm-a",
"https://kontakt.az/apple-tv-remote-mnc83zm-a",
"https://kontakt.az/apple-tv-remote-mqge2",
"https://kontakt.az/apple-usb-c-charge-cable-1-m-mm093zm-a",
"https://kontakt.az/apple-usb-c-charge-cable-1m-muf72zm-a",
"https://kontakt.az/apple-usb-c-charge-cable-2m-mll82zm-a",
"https://kontakt.az/apple-usb-c-charge-cable-mu2g3zm-a",
"https://kontakt.az/apple-usb-c-digital-av-multiport-adapter",
"https://kontakt.az/apple-usb-c-to-headphone-jack-adapter-mu7e2zm-a",
"https://kontakt.az/apple-usb-c-to-lightning-adapter-muqx3zm-a",
"https://kontakt.az/apple-usb-c-to-lightning-cable-1m-mm0a3zm-a",
"https://kontakt.az/apple-usb-c-to-lightning-cable-1m-mx0k2zm-a",
"https://kontakt.az/apple-usb-c-to-lightning-cable-2m-mqgh2zm-a",
"https://kontakt.az/apple-usb-c-to-magsafe-3-cable-2-m-mlyv3zm-a",
"https://kontakt.az/apple-usb-c-to-sd-card-reader-model-a2082-mw653zm-a",
"https://kontakt.az/apple-usb-c-to-usb-adapter",
"https://kontakt.az/apple-usb-c-woven-charge-cable-1m-mqkj3zm-a",
"https://kontakt.az/apple-usb-multi-drive-md564",
"https://kontakt.az/apple-watch-3-42-mm-space-grey-mtf32gk-a",
"https://kontakt.az/apple-watch-6-40mm-red-m00a3gk-a",
"https://kontakt.az/apple-watch-6-40mm-silver-mg283gk-a",
"https://kontakt.az/apple-watch-6-40mm-space-grey-mg133gk-a",
"https://kontakt.az/apple-watch-6-44-mm-red-m00m3gk-a",
"https://kontakt.az/apple-watch-6-44mm-gold-m00e3gk-a",
"https://kontakt.az/apple-watch-7-41-mm-blue-mkn13rb-a",
"https://kontakt.az/apple-watch-7-41-mm-green-mkn03",
"https://kontakt.az/apple-watch-7-41-mm-midnight-mkmx3rb-a",
"https://kontakt.az/apple-watch-7-41-mm-red-mkn23",
"https://kontakt.az/apple-watch-7-41-mm-starlight-mkmy3rb-a",
"https://kontakt.az/apple-watch-7-45-mm-blue-mkn83rb-a",
"https://kontakt.az/apple-watch-7-45-mm-green-mkn73rb-a",
"https://kontakt.az/apple-watch-7-45-mm-midnight-mkn53rb-a",
"https://kontakt.az/apple-watch-7-45-mm-red-mkn93rb-a",
"https://kontakt.az/apple-watch-7-45-mm-starlight-mkn63rb-a",
"https://kontakt.az/apple-watch-8-41-mm-starlight-aluminium-mnp63rb-a",
"https://kontakt.az/apple-watch-8-41mm-midnight-aluminium-mnp53rb-a",
"https://kontakt.az/apple-watch-8-41mm-silver-aluminium-mp6k3rb-a",
"https://kontakt.az/apple-watch-8-45-mm-midnight-aluminium-mnp13rb-a",
"https://kontakt.az/apple-watch-8-45-mm-silver-aluminium-mp6n3rb-a",
"https://kontakt.az/apple-watch-8-45-mm-starlight-aluminium-mnp23rb-a",
"https://kontakt.az/apple-watch-9-41-mm-midnight-aluminium-case-midnight-sport-band-m-l",
"https://kontakt.az/apple-watch-9-41-mm-midnight-aluminium-case-midnight-sport-band-s-m",
"https://kontakt.az/apple-watch-9-41-mm-pink-aluminium-case-pink-sport-band-m-l",
"https://kontakt.az/apple-watch-9-41-mm-pink-w-light-pink-sport-band-s-m-mr933qi-a",
"https://kontakt.az/apple-watch-9-41-mm-silver-alluminium-w-blue-sport-band-s-mr903qr-a",
"https://kontakt.az/apple-watch-9-41-mm-silver-aluminium-w-storm-blue-sport-band-m-l-mr913qi-a",
"https://kontakt.az/apple-watch-9-41-mm-starlight-aluminium-case-starlight-sport-band-loop",
"https://kontakt.az/apple-watch-9-41-mm-starlight-aluminium-case-starlight-sport-band-m-l",
"https://kontakt.az/apple-watch-9-41-mm-starlight-w-starlight-sport-band-s-m-mr8t3qi-a",
"https://kontakt.az/apple-watch-9-45-mm-midnight-aluminium-case-midnight-sport-band-m-l",
"https://kontakt.az/apple-watch-9-45-mm-midnight-w-midnight-sport-band-s-m-mr993qi-a",
"https://kontakt.az/apple-watch-9-45-mm-product-red-aluminium-case-product-red-sport-band-s-m",
"https://kontakt.az/apple-watch-9-45-mm-silver-aluminium-case-storm-blue-sport-band-s-m",
"https://kontakt.az/apple-watch-9-45-mm-silver-wstorm-blue-sport-band-m-l-mr9e3qr-a",
"https://kontakt.az/apple-watch-9-45-mm-starlight-aluminium-case-starlight-sport-band-m-l",
"https://kontakt.az/apple-watch-magnetic-charging-cable-1m-mx2e2zm-a",
"https://kontakt.az/apple-watch-magnetic-fast-charging-usb-c-cable-1-m-mlwj3zm-a",
"https://kontakt.az/apple-watch-magnetic-fast-charging-usb-c-cable-1m-mt0h3zm-a",
"https://kontakt.az/apple-watch-nike-6-44mm-space-grey-mg173gk-a",
"https://kontakt.az/apple-watch-se-2-40-mm-silver-aluminium-sport-band-s-m-mre13qr-a",
"https://kontakt.az/apple-watch-se-2-40-mm-starlight-w-starlight-sport-band-s-m-mr9u3qi-a",
"https://kontakt.az/apple-watch-se-2-40mm-starlight-w-starlight-sport-band-m-l-mxeg3qi-a",
"https://kontakt.az/apple-watch-se-2-44-mm-midnight-aluminium-sport-loop-mrea3qr-a",
"https://kontakt.az/apple-watch-se-2-44-mm-midnight-w-midnight-sport-band-s-m-mre73qi-a",
"https://kontakt.az/apple-watch-se-2-44-mm-silver-wstorm-blue-sport-band-m-l-mree3qr-a",
"https://kontakt.az/apple-watch-se-2-44-mm-starlight-w-starlight-sport-band-s-m-mre43qi-a",
"https://kontakt.az/apple-watch-se-2-44mm-midnght-w-midnght-sport-band-m-l-mxek3qi-a",
"https://kontakt.az/apple-watch-se-2-44mm-starlight-sport-band-m-l-mxek3qi-a",
"https://kontakt.az/apple-watch-se-40-mm-gold",
"https://kontakt.az/apple-watch-se-40-mm-midnight-aluminium-case-midnight-sport-band-loop",
"https://kontakt.az/apple-watch-se-40-mm-midnight-case-midnight-sport-band-s-m",
"https://kontakt.az/apple-watch-se-40-mm-silver",
"https://kontakt.az/apple-watch-se-40-mm-silver-aluminium-mnjv3rb-a",
"https://kontakt.az/apple-watch-se-40-mm-space-grey",
"https://kontakt.az/apple-watch-se-40-mm-starlight-aluminium-case-starlight-sport-band-loop",
"https://kontakt.az/apple-watch-se-40-mm-starlight-aluminium-case-starlight-sport-band-m-l",
"https://kontakt.az/apple-watch-se-40mm-midnight-aluminium-mnjt3rb-a",
"https://kontakt.az/apple-watch-se-40mm-midnight-w-midnight-sport-band-s-m-mxe73qi-a",
"https://kontakt.az/apple-watch-se-40mm-silver-w-denim-sport-band-s-m-mxec3qi-a",
"https://kontakt.az/apple-watch-se-40mm-starlight-aluminium-mnjp3rb-a",
"https://kontakt.az/apple-watch-se-40mm-starlight-w-starlight-sport-band-s-m-mxef3qi-a",
"https://kontakt.az/apple-watch-se-40mm-starlight-w-starlight-sport-band-s-m-mxef3qi-a-68f73d80e7453-promo",
"https://kontakt.az/apple-watch-se-44-mm-gold-mkq53rb-a",
"https://kontakt.az/apple-watch-se-44-mm-midnight-aluminium-case-midnight-sport-band-m-l",
"https://kontakt.az/apple-watch-se-44-mm-midnight-aluminium-mnk03rb-a",
"https://kontakt.az/apple-watch-se-44-mm-silver",
"https://kontakt.az/apple-watch-se-44-mm-space-grey",
"https://kontakt.az/apple-watch-se-44-mm-starlight-aluminium-case-starlight-sport-band-loop",
"https://kontakt.az/apple-watch-se-44-mm-starlight-aluminium-case-starlight-sport-band-m-l",
"https://kontakt.az/apple-watch-se-44-mm-starlight-aluminium-mnjx3rb-a",
"https://kontakt.az/apple-watch-se-nike-44-mm-silver",
"https://kontakt.az/apple-watch-se-nike-44-mm-space-grey",
"https://kontakt.az/apple-watch-series-10-42mm-jet-black-w-back-sport-band-s-m-mwwe3qi-a",
"https://kontakt.az/apple-watch-series-10-42mm-jet-black-w-ink-sport-loop-mwwg3qi-a",
"https://kontakt.az/apple-watch-series-10-42mm-rose-gold-w-light-blush-sport-band-s-m-mwwh3qi-a",
"https://kontakt.az/apple-watch-series-10-42mm-silver-w-blue-cloud-sport-loop-mwwd3qi-a",
"https://kontakt.az/apple-watch-series-10-42mm-silver-w-denim-sport-band-s-m-mwwa3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-jet-black-w-black-sport-band-m-l-mwwq3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-jet-black-w-ink-sport-loop-mwwr3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-rose-gold-w-light-blush-sport-band-m-l-mwwu3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-rose-gold-w-plum-sport-loop-mwwv3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-silver-w-blue-cloud-sport-loop-mwwn3qi-a",
"https://kontakt.az/apple-watch-series-10-46mm-silver-w-denim-sport-band-m-l-mwwm3qi-a",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-blue-alpine-band-loop-large-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-blue-black-trail-loop-s-m-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-blue-ocean-band-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-green-grey-trail-loop-m-l-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-indigo-alpine-band-loop-large-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-olive-alpine-band-loop-large-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-orange-beige-trail-loop-m-l-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-orange-ocean-band-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-case-white-ocean-band-cellular",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-w-blue-black-trail-loop-m-l-mrf63gk-a",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-w-green-grey-trail-loop-s-mrf33gk-a",
"https://kontakt.az/apple-watch-ultra-2-49-mm-titanium-w-olive-alpine-band-loop-l-mrf03gk-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-black-ocean-band-mx4p3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-black-titanium-milanese-loop-m-mx5u3gk-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-black-trail-loop-m-l-mx4v3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-black-trail-loop-s-m-mx4u3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-dark-green-alpine-loop-l-mx4t3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-black-w-dark-green-alpine-loop-m-mx4r3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-natural-w-blue-trail-loop-m-l-mx4l3gk-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-natural-w-natural-milanese-loop-m-mx5r3gk-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-natural-w-navy-ocean-band-mx4d3rb-a",
"https://kontakt.az/apple-watch-ultra-2-cellular-49mm-natural-w-tan-alpine-loop-m-mx4f3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-black-grey-trail-loop-m-l-mqfx3gk-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-black-grey-trail-loop-s-m-mqfw3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-blue-grey-trail-loop-m-l-mqfv3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-blue-grey-trail-loop-s-m-mnhl3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-green-alpine-loop-l-mqfp3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-green-alpine-loop-md-mqfn3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-green-alpine-loop-sm-mnhj3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-midnight-ocean-band-mqfk3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-orange-alpine-loop-l-mqfm3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-orange-alpine-loop-sm-mnhh3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-starlight-alpine-loop-l-mqft3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-starlight-alpine-loop-s-mqfq3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-yellow-beige-trail-loop-m-l-mqfu3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-yellow-beige-trail-loop-s-m-mnhk3rb-a",
"https://kontakt.az/apple-watch-ultra-49-mm-titanium-case-w-yellow-ocean-band-mnhg3rb-a",
"https://kontakt.az/apple-watch-ultra-49mm-titanium-case-w-orange-alpine-loop-md-mqfl3rb-a",
"https://kontakt.az/apple-watch-ultra-49mm-titanium-case-w-white-ocean-band-mnhf3rb-a",
"https://kontakt.az/apple-world-travel-adapter-kit-md837zm-a",
"https://kontakt.az/blue-apple-airpods-2-liquid-silicone-protect-case-black",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-blue",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-green",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-ice-blue",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-pink",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-purple",
"https://kontakt.az/blueo-apple-airpods-2-liquid-silicone-protect-case-yellow",
"https://kontakt.az/blueo-apple-airpods-pro-liquid-silicone-protect-case-black",
"https://kontakt.az/charging-case-for-apple-airpods",
"https://kontakt.az/dezodorant-dove-apple-white-tea-250-ml-8717163676721",
"https://kontakt.az/klaviatura-apple-magic-keyboard-mk2a3rs-a",
"https://kontakt.az/klaviatura-apple-magic-keyboard-touch-id-mxk83rs-a",
"https://kontakt.az/klaviatura-apple-magic-keyboard-with-numeric-keypad-silver-mq052rs-a",
"https://kontakt.az/klaviatura-apple-magic-keyboard-with-touch-id-mxck3rs-a",
"https://kontakt.az/klaviatura-apple-magic-keyboard-with-touch-id-mxk73rs-a",
"https://kontakt.az/magic-trackpad-apple-a3120-mxk93zm-a-white",
"https://kontakt.az/magic-trackpad-apple-a3120-mxka3zm-a-black",
"https://kontakt.az/monitor-apple-imac-24-mqrd3ru-a-pink",
"https://kontakt.az/monitor-apple-studio-display-27-mk0q3ru-a",
"https://kontakt.az/monoblok-apple-imac-21-5-mhk23ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mgpd3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mgph3ru-a-green",
"https://kontakt.az/monoblok-apple-imac-24-mgpj3ru-a-green",
"https://kontakt.az/monoblok-apple-imac-24-mgpk3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mgpl3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mgpn3ru-a-pink",
"https://kontakt.az/monoblok-apple-imac-24-mgtf3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mjva3ru-a-pink",
"https://kontakt.az/monoblok-apple-imac-24-mqr93ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mqrc3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mqrj3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mqrk3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mqrn3ru-a-green",
"https://kontakt.az/monoblok-apple-imac-24-mqrp3ru-a-green",
"https://kontakt.az/monoblok-apple-imac-24-mqrq3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mqrr3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mqrt3ru-a-pink",
"https://kontakt.az/monoblok-apple-imac-24-mqru3ru-a-pink",
"https://kontakt.az/monoblok-apple-imac-24-mwuc3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mwue3ru-a-green",
"https://kontakt.az/monoblok-apple-imac-24-mwuf3ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mwuv3ru-a-silver",
"https://kontakt.az/monoblok-apple-imac-24-mwv13ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-mwv33ru-a-blue",
"https://kontakt.az/monoblok-apple-imac-24-silver-mcr24ru-a",
"https://kontakt.az/monoblok-apple-imac-24-zkz132000bz-orange",
"https://kontakt.az/monoblok-apple-imac-27-mxwt2ru-a",
"https://kontakt.az/mouse-apple-magic-touch-surface-white-a3204-mxk53zm",
"https://kontakt.az/naqil-apple-thunderbolt-5-usb-c-1-m-a3189-mc9c4zm-a",
"https://kontakt.az/naqil-apple-usb-type-c-1-m-a2795-mw493zm-a",
"https://kontakt.az/naqil-ugreen-us304-70523-18w-3a-lightning-apple-mfi-1m-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-m3-silver-mc8h4ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-midnight-mw123ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-midnight-mw133ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-silver-mw0w3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-silver-mw0x3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-sky-blue-mc6t4ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-sky-blue-mc6u4ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-starlight-mw0y3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-m4-starlight-mw103ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc7u4ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc7v4ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc7w4ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc7x4ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8g4ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8j4ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8k4ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8m4ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8n4ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-mc8p4ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mgn63ll-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-13-mgn63ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-13-mgn73ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-13-mgna3ua-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-mgnd3ru-a-gold",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxn3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxp3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxq3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxr3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxt3ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxu3ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxv3ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-13-mrxw3ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-13-zkz160000lc-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-midnight-mw1l3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-midnight-mw1m3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-silver-mw1g3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-silver-mw1h3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-sky-blue-mc7a4ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-sky-blue-mc7c4ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-starlight-mw1j3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-m4-starlight-mw1k3ru-a",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9d4ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9e4ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9g4ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9h4ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9j4ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9k4ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mc9l4ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkp3rua-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkq3rua-space-grey",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkr3rua-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkt3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqku3rua-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkv3rua-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkw3rua-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mqkx3rua-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mrym3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryn3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryp3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryq3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryr3ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryt3ru-a-starlight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryu3ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mryv3ru-a-midnight",
"https://kontakt.az/notbuk-apple-macbook-air-15-mxd13ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-pro-13-mnej3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-13-mnep3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-13-mxk32ll-a",
"https://kontakt.az/notbuk-apple-macbook-pro-13-myda2ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-13-z16r0006v-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-13-z16s00061-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mcx04ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mcx14ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde04ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde14ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde34ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde44ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde54ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mde64ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mkgt3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mphf3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mphg3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mphj3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mr7j3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mr7k3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mrx33ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mrx53ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mrx63ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mrx73ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mtl73ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mtl83ru-a-space-grey",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mw2u3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mw2v3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mw2w3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mw2x3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2e3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2f3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2h3ru-a-space-black",
]

# Configuration
@dataclass
class ScrapingConfig:
    max_workers: int = 2  # Reduced to 2 workers for better stability
    max_retries: int = 3
    base_delay: float = 3.0  # Slightly increased for reliability
    max_delay: float = 6.0
    session_restart_interval: int = 50  # More frequent restarts
    checkpoint_interval: int = 5  # Save progress more frequently
    timeout: int = 20  # Increased timeout
    headless: bool = True
    page_load_timeout: int = 30  # Max time for any single page

config = ScrapingConfig()

# Progress tracking
class ProgressManager:
    def __init__(self):
        self.progress_file = f"scraping_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.completed_urls = set()
        self.failed_urls = set()
        self.results = []
        self.lock = threading.Lock()
        self.load_progress()
    
    def load_progress(self):
        """Load existing progress if available"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_urls = set(data.get('completed_urls', []))
                    self.failed_urls = set(data.get('failed_urls', []))
                    self.results = data.get('results', [])
                    logger.info(f"🔄 Loaded progress: {len(self.completed_urls)} completed, {len(self.failed_urls)} failed")
        except Exception as e:
            logger.warning(f"Could not load progress: {e}")
    
    def save_progress(self):
        """Save current progress"""
        try:
            with self.lock:
                data = {
                    'completed_urls': list(self.completed_urls),
                    'failed_urls': list(self.failed_urls),
                    'results': self.results,
                    'timestamp': datetime.now().isoformat()
                }
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def add_result(self, url: str, result: Optional[Dict]):
        """Add scraping result"""
        with self.lock:
            if result:
                self.results.append(result)
                self.completed_urls.add(url)
                if url in self.failed_urls:
                    self.failed_urls.remove(url)
            else:
                self.failed_urls.add(url)
            
            # Auto-save progress periodically
            if len(self.results) % config.checkpoint_interval == 0:
                self.save_progress()
    
    def get_pending_urls(self, all_urls: List[str]) -> List[str]:
        """Get URLs that still need to be scraped"""
        return [url for url in all_urls if url not in self.completed_urls]
    
    def get_stats(self) -> Dict[str, int]:
        """Get current statistics"""
        return {
            'completed': len(self.completed_urls),
            'failed': len(self.failed_urls),
            'total_results': len(self.results)
        }

# Enhanced browser headers with rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class EnhancedWebDriver:
    """Enhanced WebDriver with session management and health checks"""
    
    def __init__(self, worker_id: int = 0):
        self.worker_id = worker_id
        self.driver = None
        self.session_count = 0
        self.max_session_uses = config.session_restart_interval
        self.create_driver()
    
    def create_driver(self):
        """Create a new WebDriver with optimized settings"""
        if self.driver:
            self.quit_driver()
        
        chrome_options = Options()
        
        if config.headless:
            chrome_options.add_argument("--headless=new")
        
        # Enhanced performance options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Speed optimizations
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript-harmony-shipping")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        
        # Random user agent
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent.replace('HeadlessChrome', 'Chrome')
            })
            
            self.session_count = 0
            logger.info(f"✅ WebDriver {self.worker_id} created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create WebDriver {self.worker_id}: {e}")
            self.driver = None
            raise
    
    def is_session_healthy(self) -> bool:
        """Check if the current session is healthy"""
        if not self.driver:
            return False
        
        try:
            # Try to get current URL to test session health
            _ = self.driver.current_url
            return True
        except (InvalidSessionIdException, WebDriverException):
            logger.warning(f"🚨 WebDriver {self.worker_id} session is unhealthy")
            return False
    
    def restart_if_needed(self):
        """Restart driver if session is unhealthy or overused"""
        need_restart = (
            not self.is_session_healthy() or
            self.session_count >= self.max_session_uses
        )
        
        if need_restart:
            logger.info(f"🔄 Restarting WebDriver {self.worker_id} (uses: {self.session_count})")
            self.create_driver()
    
    def get_page(self, url: str) -> bool:
        """Navigate to page with session health management and timeout protection"""
        try:
            self.restart_if_needed()
            
            if not self.driver:
                return False
            
            # Set aggressive timeouts
            self.driver.set_page_load_timeout(config.page_load_timeout)
            self.driver.implicitly_wait(5)
            
            self.driver.get(url)
            self.session_count += 1
            return True
            
        except TimeoutException:
            logger.error(f"❌ Page load timeout for WebDriver {self.worker_id}: {url}")
            # Force restart on timeout
            try:
                self.create_driver()
            except Exception:
                pass
            return False
        except Exception as e:
            logger.error(f"❌ Navigation failed for WebDriver {self.worker_id}: {e}")
            return False
    
    def quit_driver(self):
        """Safely quit the driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.debug(f"Error quitting driver {self.worker_id}: {e}")
            finally:
                self.driver = None

def safe_get_text(element):
    """Safely extract text from element"""
    if not element:
        return None
    try:
        return element.text.strip() if hasattr(element, 'text') else element.get_text(strip=True)
    except:
        return None

def extract_price_enhanced(soup, driver=None):
    """Enhanced price extraction with multiple fallback methods"""
    # Method 1: From GTM data (most reliable)
    try:
        gtm_elements = soup.select(".product-gtm-data")
        for gtm_elem in gtm_elements:
            gtm_data_attr = gtm_elem.get("data-gtm")
            if gtm_data_attr:
                try:
                    gtm_json = json.loads(gtm_data_attr)
                    price = gtm_json.get("price")
                    discount = gtm_json.get("discount")
                    if price:
                        return str(price), str(discount) if discount else None
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.debug(f"GTM price extraction failed: {e}")
    
    # Method 2: From price display elements
    price_selectors = [
        ".prodCart__prices strong b",
        ".prodCart__prices b",
        ".price-final_price .price",
        ".regular-price .price",
        ".special-price .price",
        "[data-price-type='finalPrice'] .price"
    ]
    
    for selector in price_selectors:
        try:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Extract numeric price
                price_match = re.search(r'([\d.,]+)', price_text.replace('₼', '').replace(',', '.'))
                if price_match:
                    price = price_match.group(1)
                    return price, None
        except Exception:
            continue
    
    # Method 3: JavaScript execution if driver available
    if driver and hasattr(driver, 'driver') and driver.driver:
        try:
            price_js = driver.driver.execute_script("""
                var priceElements = document.querySelectorAll('.prodCart__prices b, .price, [data-price]');
                for (var i = 0; i < priceElements.length; i++) {
                    var elem = priceElements[i];
                    var text = elem.textContent || elem.innerText;
                    var match = text.match(/([\\d.,]+)/);
                    if (match) {
                        return match[1];
                    }
                }
                return null;
            """)
            if price_js:
                return price_js, None
        except Exception:
            pass
    
    return None, None

def extract_specifications_enhanced(soup, driver=None):
    """Enhanced specification extraction"""
    specs = {}
    
    # Method 1: From .har tables (primary)
    try:
        spec_rows = soup.select(".har .har__row")
        for row in spec_rows:
            title_elem = row.select_one(".har__title")
            value_elem = row.select_one(".har__znach")
            if title_elem and value_elem:
                key = title_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                if key and value and len(key) < 100 and len(value) < 500:
                    specs[key] = value
        
        if specs:
            return specs
    except Exception:
        pass
    
    # Method 2: From attribute tables (fallback)
    try:
        attr_selectors = [
            ".product-attribute tr",
            ".data.table tr", 
            ".additional-attributes tr",
            ".product-attribute-specs tr"
        ]
        
        for selector in attr_selectors:
            attr_rows = soup.select(selector)
            if attr_rows:
                for row in attr_rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and len(key) < 100 and len(value) < 500:
                            specs[key] = value
                if specs:
                    break
    except Exception:
        pass
    
    return specs

def extract_product_title_enhanced(soup, driver=None):
    """Enhanced title extraction"""
    title_selectors = [
        ".page-title .base",
        ".page-title",
        ".product-name",
        "h1.page-title",
        "[data-ui-id='page-title-wrapper'] h1",
        "[data-ui-id='page-title-wrapper'] .base",
        "h1"
    ]
    
    for selector in title_selectors:
        try:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        except Exception:
            continue
    
    return None

def extract_sku_enhanced(soup, driver=None):
    """Enhanced SKU extraction"""
    sku_selectors = [
        ".prodCart__code",
        ".product-sku",
        "[itemprop='sku']",
        ".product-item-sku",
        ".sku-value"
    ]
    
    for selector in sku_selectors:
        try:
            elem = soup.select_one(selector)
            if elem:
                sku_text = elem.get_text(strip=True)
                # Clean up SKU text
                sku = re.sub(r'^(SKU:|№|Code:)', '', sku_text, flags=re.IGNORECASE).strip()
                if sku and len(sku) > 3:
                    return sku
        except Exception:
            continue
    
    return None

def extract_images_enhanced(soup, driver=None):
    """Enhanced image extraction"""
    images = []
    
    # Method 1: From gallery thumbnails
    try:
        gallery_selectors = [
            ".slider111__thumbs .item",
            ".product-image-gallery .item",
            ".gallery-image a",
            ".product-media-gallery a"
        ]
        
        for selector in gallery_selectors:
            gallery_images = soup.select(selector)
            for img_link in gallery_images:
                href = img_link.get("href")
                if href and "kontakt.az" in href:
                    if href not in images:
                        images.append(href)
        
        if images:
            return images
    except Exception:
        pass
    
    # Method 2: From main product images
    try:
        img_selectors = [
            ".main-image img",
            ".product-image img",
            ".product-photo img",
            ".slider111__image img"
        ]
        
        for selector in img_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get("src") or img.get("data-src")
                if src and "kontakt.az" in src:
                    if src not in images:
                        images.append(src)
    except Exception:
        pass
    
    return images

def scrape_product_enhanced(enhanced_driver: EnhancedWebDriver, url: str):
    """Enhanced product scraping with improved session management"""
    max_retries = config.max_retries
    
    for attempt in range(max_retries):
        try:
            # Navigate to page with session health management
            if not enhanced_driver.get_page(url):
                if attempt < max_retries - 1:
                    sleep(random.uniform(2, 4))
                    continue
                else:
                    return None
            
            # Wait for page to load with optimized waits
            try:
                wait = WebDriverWait(enhanced_driver.driver, config.timeout)
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".prodCart__code")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-gtm-data"))
                ))
            except TimeoutException:
                logger.debug(f"Timeout waiting for elements on {url}")
            
            # Reduced wait time for dynamic content
            sleep(random.uniform(1, 2))
            
            # Quick scroll to load lazy content
            try:
                enhanced_driver.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                sleep(0.5)
                enhanced_driver.driver.execute_script("window.scrollTo(0, 0);")
            except Exception:
                pass
            
            # Get page source and create soup
            html = enhanced_driver.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Enhanced data extraction (keeping all existing logic)
            title = extract_product_title_enhanced(soup, enhanced_driver)
            sku = extract_sku_enhanced(soup, enhanced_driver)
            price, discount = extract_price_enhanced(soup, enhanced_driver)
            
            # Category from breadcrumb
            category = None
            try:
                breadcrumb = soup.select(".breadcrumb a")
                if breadcrumb:
                    category = " / ".join([c.get_text(strip=True) for c in breadcrumb if c.get_text(strip=True)])
            except Exception:
                pass
            
            # Brand
            brand = None
            try:
                brand_selectors = [
                    ".product-brand-relation-link__brand",
                    "[itemprop='brand']",
                    ".brand",
                    ".product-brand"
                ]
                for selector in brand_selectors:
                    brand_elem = soup.select_one(selector)
                    if brand_elem:
                        brand = brand_elem.get_text(strip=True)
                        break
            except Exception:
                pass
            
            # Rating and reviews
            rating = safe_get_text(soup.select_one(".product-rating, [itemprop='ratingValue']"))
            reviews_count = safe_get_text(soup.select_one(".rating-count-info, [itemprop='reviewCount']"))
            
            # Specifications
            specs = extract_specifications_enhanced(soup, enhanced_driver)
            
            # Images
            images = extract_images_enhanced(soup, enhanced_driver)
            
            # Availability
            availability = "In Stock"
            try:
                out_of_stock = soup.select_one(".product-alert-stock__button, .out-of-stock")
                if out_of_stock:
                    availability = "Pre-order / Out of Stock"
            except Exception:
                pass
            
            # Warranty
            warranty = None
            if specs:
                warranty = specs.get("Zəmanət") or specs.get("Warranty") or specs.get("Гарантия")
            
            # Product type detection
            product_type = "Unknown"
            if category:
                cat_lower = category.lower()
                if "telefon" in cat_lower or "smartphone" in cat_lower:
                    product_type = "Smartphone"
                elif "adapter" in cat_lower:
                    product_type = "Accessory"
                elif "qulaqlıq" in cat_lower:
                    product_type = "Headphones"
                elif "kompüter" in cat_lower:
                    product_type = "Computer"
            
            # Build result
            result = {
                "url": url,
                "category": category,
                "product_type": product_type,
                "title": title,
                "sku": sku,
                "brand": brand,
                "price": price,
                "discount": discount,
                "rating": rating,
                "reviews_count": reviews_count,
                "availability": availability,
                "warranty": warranty,
                "specifications": json.dumps(specs, ensure_ascii=False) if specs else None,
                "images": "|".join(images) if images else None,
                "fetched_at": datetime.now().isoformat(),
                "worker_id": enhanced_driver.worker_id
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Worker {enhanced_driver.worker_id} attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = random.uniform(2, 5)
                sleep(sleep_time)
                # Try to restart driver on repeated failures
                if attempt > 0:
                    enhanced_driver.restart_if_needed()
            continue
    
    return None

def worker_scraper(worker_id: int, urls_chunk: List[str], progress_manager: ProgressManager):
    """Worker function for parallel scraping"""
    enhanced_driver = None
    scraped_count = 0
    
    try:
        enhanced_driver = EnhancedWebDriver(worker_id)
        logger.info(f"🚀 Worker {worker_id} started with {len(urls_chunk)} URLs")
        
        for i, url in enumerate(urls_chunk):
            try:
                logger.info(f"Worker {worker_id} [{i+1}/{len(urls_chunk)}]: {url.split('/')[-1][:50]}")
                
                result = scrape_product_enhanced(enhanced_driver, url)
                progress_manager.add_result(url, result)
                
                if result:
                    scraped_count += 1
                    logger.info(f"✅ Worker {worker_id}: {result.get('title', 'Unknown')[:50]}")
                else:
                    logger.warning(f"❌ Worker {worker_id}: Failed to scrape {url}")
                
                # Intelligent delay - adaptive based on success
                base_delay = config.base_delay if result else config.base_delay * 1.5
                delay = random.uniform(base_delay, config.max_delay)
                sleep(delay)
                
            except KeyboardInterrupt:
                logger.info(f"🛑 Worker {worker_id} interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error processing {url}: {e}")
                progress_manager.add_result(url, None)
    
    finally:
        if enhanced_driver:
            enhanced_driver.quit_driver()
        
        logger.info(f"🏁 Worker {worker_id} finished: {scraped_count} successful scrapes")

def main():
    """Main scraping function with parallel processing"""
    if not urls:
        print("❌ No URLs found! Please add URLs to the 'urls' list at the top of the script.")
        return
    
    print("🚀 Starting Enhanced Kontakt.az scraper v2...")
    print(f"📋 Total URLs: {len(urls)}")
    print(f"⚡ Parallel workers: {config.max_workers}")
    print(f"🎯 Speed optimized: {config.base_delay}-{config.max_delay}s delays")
    print(f"🛡️  Session management: Restart every {config.session_restart_interval} URLs")
    
    # Initialize progress manager
    progress_manager = ProgressManager()
    
    # Get pending URLs
    pending_urls = progress_manager.get_pending_urls(urls)
    
    if not pending_urls:
        print("✅ All URLs already completed!")
        return
    
    print(f"📋 Pending URLs: {len(pending_urls)}")
    stats = progress_manager.get_stats()
    if stats['completed'] > 0:
        print(f"🔄 Resuming from previous session: {stats['completed']} already completed")
    
    start_time = time.time()
    
    try:
        # Split URLs among workers
        chunk_size = max(1, len(pending_urls) // config.max_workers)
        url_chunks = [pending_urls[i:i + chunk_size] for i in range(0, len(pending_urls), chunk_size)]
        
        # Start parallel scraping
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            futures = [
                executor.submit(worker_scraper, i, chunk, progress_manager)
                for i, chunk in enumerate(url_chunks) if chunk
            ]
            
            # Wait for all workers to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Worker failed: {e}")
    
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    
    finally:
        # Final progress save
        progress_manager.save_progress()
        
        # Save final results
        if progress_manager.results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kontakt_products_enhanced_v2_{timestamp}.csv"
            
            print(f"\n💾 Saving {len(progress_manager.results)} products to {filename}")
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                if progress_manager.results:
                    writer = csv.DictWriter(f, fieldnames=progress_manager.results[0].keys())
                    writer.writeheader()
                    writer.writerows(progress_manager.results)
            
            print(f"✅ Data saved to {filename}")
        
        # Final statistics
        end_time = time.time()
        duration = end_time - start_time
        stats = progress_manager.get_stats()
        
        print(f"\n📊 Final Summary:")
        print(f"   Total URLs: {len(urls)}")
        print(f"   Completed: {stats['completed']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['completed']/(stats['completed']+stats['failed'])*100:.1f}%")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Average time per URL: {duration/max(1, stats['completed']):.1f}s")
        
        if stats['failed'] > 0:
            print(f"📝 Progress file saved: {progress_manager.progress_file}")
            print("   Run the script again to retry failed URLs")

if __name__ == "__main__":
    main()
