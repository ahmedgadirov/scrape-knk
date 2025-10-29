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
import signal
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Simplified logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# ADD YOUR URLS HERE - Replace this empty list with your URLs
urls = [
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2h3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2j3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-mx2k3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-14-z17g001bc-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-14-z17g001bw-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnw83ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnw93ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnwa3ru-a-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnwc3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnwd3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mnwe3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw13ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw23ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw33ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw43ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw63ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mrw73ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx2t3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx2u3ru-a-silver",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx2x3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx2y3ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx303ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-mx313ru-a-space-black",
"https://kontakt.az/notbuk-apple-macbook-pro-16-z174000gu-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-16-z174000h5-space-gray",
"https://kontakt.az/notbuk-apple-macbook-pro-m4-max-silver-mx2g3ru-a",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mgn73ua-a-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mgn93ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mgna3ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mgnd3ua-a-gold",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mgne3ru-a-gold",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mlxw3ru-a-space-grey",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mlxy3ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mly03ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mly13ru-a-starlight",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mly23ru-a-starlight",
"https://kontakt.az/noutbuk-apple-macbook-air-13-mly43ru-a-midnight",
"https://kontakt.az/noutbuk-apple-macbook-air-13-z1240004p-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-air-13-zkz15s000nb-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-air-13-zkz15w000ks-silver",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-mlxx3ru-a-space-grey",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-mly33ru-a-midnight",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-mneq3ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-mr9q2",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-myd82ru-a-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-myd92ru-a-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-mydc2ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-zkz11b0004t-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-13-zkz11c00030-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-14-mkgq3ru-a-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-14-mkgr3ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-pro-16-mk193ru-a-space-gray",
"https://kontakt.az/noutbuk-apple-macbook-pro-16-mk1e3ru-a-silver",
"https://kontakt.az/noutbuk-apple-macbook-pro-16-mvvm2ru-a",
"https://kontakt.az/noutbuk-apple-macbook-pro13-mneh3ru-a-space-gray",
"https://kontakt.az/oturucu-apple-mw2p3zm-a",
"https://kontakt.az/plansetler-ve-elektron-kitablar/plansetler/apple",
"https://kontakt.az/porodo-powerbank-10000mah-magsafe-apple-watch-charger-pd-20w-black-pd-pbfch021-bk",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-w-magsafe-mgh64zm-a-fox-orange",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-w-magsafe-mgh74zm-a-moss",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-w-magsafe-mgh84zm-a-midnight-purple",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-w-magsafe-mgha4zm-a-black",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-wallet-w-magsafe-black-ma6w4zm-a",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-wallet-w-magsafe-blackberry-ma7a4zm-a",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-wallet-w-magsafe-dark-green-ma6y4zm-a",
"https://kontakt.az/pul-kisesi-apple-iphone-finewoven-wallet-w-magsafe-deep-blue-ma6x4zm-a",
"https://kontakt.az/qoruyucu-cercive-apple-iphone-air-bumper-mh004zm-a-black",
"https://kontakt.az/qoruyucu-cercive-apple-iphone-air-bumper-mh024zm-a-light-blue",
"https://kontakt.az/qoruyucu-cercive-apple-iphone-air-bumper-mh044zm-a-tan",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-clear-case-w-magsafe-ma6a4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-clear-case-w-magsafe-ma7d4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-black-myy93zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-denim-myya3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-fuchsia-myye3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-lake-green-myyh3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-plum-myyd3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-star-fruit-myyg3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-stone-gray-myyc3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-plus-silicone-case-w-magsafe-ultramarine-myyf3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-clear-case-w-magsafe-ma7e4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-clear-case-w-magsafe-ma7f4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-black-myyt3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-denim-myyu3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-fuchsia-myyx3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-lake-green-ma7v4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-plum-myyw3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-star-fruit-ma7u4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-stone-gray-myyv3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-max-silicone-case-w-magsafe-ultramarine-myyy3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-black-myyj3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-denim-myyk3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-fuchsia-myyn3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-lake-green-myyr3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-plum-myym3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-star-fruit-myyq3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-stone-gray-myyl3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-pro-silicone-case-w-magsafe-ultramarine-myyp3zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-black-myy13zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-denim-myy23zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-fuchsia-myy53zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-lake-green-myy83zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-plum-myy43zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-star-fruit-myy73zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-stone-gray-myy33zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16-silicone-case-w-magsafe-ultramarine-myy63zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16e-silicone-case-black-md3n4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16e-silicone-case-lake-green-md3x4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16e-silicone-case-white-md3p4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-16e-silicone-case-winter-blue-md3q4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfm4zm-a-neon-yellow",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfn4zm-a-purple-fog",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfp4zm-a-midnight",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfq4zm-a-terra",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfr4zm-a-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgfw4zm-a-clear",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-mgj84ll-a-everest-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-techwoven-w-magsafe-mgf84zm-a-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-techwoven-w-magsafe-mgf94zm-a-blue",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-techwoven-w-magsafe-mgfa4zm-a-purple",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-techwoven-w-magsafe-mgfc4zm-a-sienna",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-techwoven-w-magsafe-mgfd4zm-a-green",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-max-w-magsafe-mgfl4zm-a-orange",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgfe4zm-a-orange",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgff4zm-a-neon-yellow",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgfg4zm-a-purple-fog",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgfh4zm-a-midnight",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgfj4zm-a-terra-cotta",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgfk4zm-a-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-mgft4zm-a-clear",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-techwoven-w-magsafe-mgf34zm-a-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-techwoven-w-magsafe-mgf44zm-a-blue",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-techwoven-w-magsafe-mgf54zm-a-purple",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-techwoven-w-magsafe-mgf64zm-a-sienna",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-pro-techwoven-w-magsafe-mgf74zm-a-green",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgev4zm-a-neon-yellow",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgew4zm-a-anchor-blue",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgex4zm-a-light-moss",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgf04zm-a-purple-fog",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgf14zm-a-black",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-17-w-magsafe-mgf24zm-a-clear",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-air-mgh24zm-a-shadow",
"https://kontakt.az/qoruyucu-ortuk-apple-iphone-air-mgh34zm-a-frost",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-cover-for-ipad-10-2-english-lavender",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-folio-for-ipad-a16-lemonade-mden4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-folio-for-ipad-a16-sky-mdeq4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-folio-for-ipad-a16-watermelon-mdep4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-folio-for-ipad-a16-white-mdej4zm-a",
"https://kontakt.az/qoruyucu-ortuk-apple-smart-folio-for-ipad-mini-6th-gen-mm6k3zm-a",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-air-11-5-4-pro-11-gen-4-3-2-0457-black",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-air-13-2024-0800-black",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-11-2024-0725-black",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-11-2024-0732-light-blue",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-11-2024-0749-light-pink",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-13-2024-0763-black",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-13-2024-0770-light-blue",
"https://kontakt.az/qoruyucu-ortuk-comma-joy-series-apple-ipad-pro-13-2024-0787-light-pink",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-11-5-4-pro-11-gen-4-3-2-0631-spaceman",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-11-5-4-pro-11-gen-4-3-2-0648-lucky-cat",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-11-5-4-pro-11-gen-4-3-2-9155-animal-party",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-13-2024-9193-cheers",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-13-2024-9209-happy-sticker",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-13-2024-9254-spaceman",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-air-13-2024-9261-animal-party",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-pro-11-2024-0381-cheers",
"https://kontakt.az/qoruyucu-ortuk-comma-lingos-series-apple-ipad-pro-11-2024-9216-happy-sticker",
"https://kontakt.az/qulaqliq-apple-airpods-2-mv7n2ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-3-mme73ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-3-w-lightning-charging-case-mpny3ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-4-mxp63ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-4-w-anc-mxp93ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-green-mgyn3ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-mgym3ru-a-pink",
"https://kontakt.az/qulaqliq-apple-airpods-max-mgym3ru-a-sky-blue",
"https://kontakt.az/qulaqliq-apple-airpods-max-silver-mgyj3ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-space-gray-mgyh3ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-usb-c-blue-mww63ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-usb-c-midnight-mww43ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-usb-c-orange-mww73ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-usb-c-purple-mww83ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-max-usb-c-starlight-mww53ze-a",
"https://kontakt.az/qulaqliq-apple-airpods-pro-2nd-gen-w-magsafe-case-usb-c-mtjv3ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-pro-2nd-generation-mqd83ru-a",
"https://kontakt.az/qulaqliq-apple-airpods-pro-3-mfhp4ze-a",
"https://kontakt.az/qulaqliq-apple-earpods-3-5-mm-mwu53zm-a",
"https://kontakt.az/qulaqliq-apple-earpods-lightning-connector-mwty3zm-a",
"https://kontakt.az/qulaqliq-apple-earpods-lightning-mmtn2zm-a",
"https://kontakt.az/qulaqliq-apple-earpods-usb-c-mtjy3zm-a",
"https://kontakt.az/qulaqliq-apple-earpods-usb-c-myqy3zm-a",
"https://kontakt.az/qulaqlliq-apple-earpods-3-5-mm-mnhf2zm-a",
"https://kontakt.az/sbs-band-apple-watch-40-mm-black-tebandwatch40mk",
"https://kontakt.az/sbs-band-apple-watch-40-mm-blue-tebandwatch40mb",
"https://kontakt.az/sbs-band-apple-watch-44-mm-blue-tebandwatch44mb",
"https://kontakt.az/sbs-band-apple-watch-44-mm-red-tebandwatch44mr",
"https://kontakt.az/sbs-band-apple-watch-44mm-black-tebandwatch44mk",
"https://kontakt.az/simsiz-enerji-toplama-cihazi-apple-iphone-air-magsafe-mgpg4ze-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mcyt4ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mmfj3ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mnh73ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mrtr2ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mrtt2ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mu9d3ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mu9e3ru-a",
"https://kontakt.az/sistem-bloku-apple-mac-mini-mxng2ua-a",
"https://kontakt.az/smart-saat-apple-watch-se-3-40mm-meh54rk-a-starlight",
"https://kontakt.az/smart-saat-apple-watch-se-3-40mm-meh94rk-a-midnight",
"https://kontakt.az/smart-saat-apple-watch-se-3-40mm-mehc4rk-a-midnight",
"https://kontakt.az/smart-saat-apple-watch-se-3-44mm-mehj4rk-a-starlight",
"https://kontakt.az/smart-saat-apple-watch-se-3-44mm-mehn4rk-a-midnight",
"https://kontakt.az/smart-saat-apple-watch-se-3-44mm-mehq4rk-a-midnight",
"https://kontakt.az/smart-saat-apple-watch-se-3-meh34rk-a-starlight",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-meqt4rk-a-jet-black",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-mequ4rk-a-jet-black",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-meqw4rk-a-space-grey",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-meqx4rk-a-space-grey",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-meu04rk-a-rose-gold",
"https://kontakt.az/smart-saat-apple-watch-series-11-42mm-meu64rk-a-silver",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-meuw4rk-a-jet-black",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-meux4rk-a-jet-black",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-mev04rk-a-space-grey",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-mev44rk-a-space-grey",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-mev74rk-a-rose-gold",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-mev94rk-a-silver",
"https://kontakt.az/smart-saat-apple-watch-series-11-46mm-meva4rk-a-silver",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mewh4qi-a-natural-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mewm4qi-a-natural-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mewp4qi-a-natural-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mewr4qi-a-natural-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mewu4qi-a-natural-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf0j4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf0v4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf0x4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf1d4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf1h4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf1q4qi-a-black-titanium",
"https://kontakt.az/smart-saat-apple-watch-ultra-3-cellular-49mm-mf1t4qi-a-black-titanium",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mgge4zm-a-neon-yellow",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mggh4zm-a-light-blue",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mggk4zm-a-tan",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mggl4zm-a-black",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mggm4zm-a-light-gray",
"https://kontakt.az/smartfon-ucun-kemer-apple-crossbody-strap-mggn4zm-a-sienna",
"https://kontakt.az/stilus-apple-pencil-1st-gen-mk0c2",
"https://kontakt.az/stilus-apple-pencil-2nd-gen-mu8f2",
"https://kontakt.az/stilus-apple-pencil-mxn43zm-a",
"https://kontakt.az/stilus-apple-pencil-usb-c-muwa3zm-a",
"https://kontakt.az/unisex-clive-christian-crab-apple-blossom-50-ml-652638008929",
"https://kontakt.az/usaq-dis-mecunu-chicco-applebanana-8058664175567",
"https://kontakt.az/usb-c-to-apple-pencil-adapter-mqlu3zm-a",
"https://kontakt.az/utu-russell-hobbs-26481-56-light-easy-brights-apple-iron",
"https://kontakt.az/winso-merssus-apple-cinnamon-18-ml-534390",
"https://kontakt.az/zaschitnyj-chehol-apple-smart-folio-for-ipad-air-5th-english-lavender-mna63zm-a",
]

# Simplified Configuration
@dataclass
class ScrapingConfig:
    max_retries: int = 3
    base_delay: float = 4.0
    max_delay: float = 8.0
    timeout: int = 15
    page_load_timeout: int = 20
    headless: bool = True
    session_restart_after: int = 25  # Restart driver after N URLs

config = ScrapingConfig()

class ProgressTracker:
    """Simple progress tracking with file persistence"""
    
    def __init__(self):
        self.progress_file = f"scraping_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.completed_urls = set()
        self.failed_urls = set()
        self.results = []
        self.current_position = 0
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
                    self.current_position = data.get('current_position', 0)
                    logger.info(f"🔄 Resumed: {len(self.completed_urls)} completed, {len(self.failed_urls)} failed")
        except Exception as e:
            logger.warning(f"Could not load progress: {e}")
    
    def save_progress(self):
        """Save current progress"""
        try:
            data = {
                'completed_urls': list(self.completed_urls),
                'failed_urls': list(self.failed_urls),
                'results': self.results,
                'current_position': self.current_position,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def add_result(self, url: str, result: Optional[Dict]):
        """Add scraping result"""
        if result:
            self.results.append(result)
            self.completed_urls.add(url)
            if url in self.failed_urls:
                self.failed_urls.remove(url)
        else:
            self.failed_urls.add(url)
        
        self.current_position += 1
        
        # Save every 5 successful results
        if len(self.results) % 5 == 0:
            self.save_progress()
    
    def get_pending_urls(self, all_urls: List[str]) -> List[str]:
        """Get URLs that still need to be scraped"""
        return [url for url in all_urls if url not in self.completed_urls]

# Simplified User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

class SimpleWebDriver:
    """Simplified WebDriver with better resource management"""
    
    def __init__(self):
        self.driver = None
        self.session_count = 0
        self.max_session_uses = config.session_restart_after
        self.create_driver()
    
    def create_driver(self):
        """Create a clean WebDriver instance"""
        self.quit_driver()
        
        chrome_options = Options()
        
        if config.headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential options only
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        
        # Random user agent
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument("--window-size=1366,768")
        
        # Disable unnecessary features for speed
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set reasonable timeouts
            self.driver.set_page_load_timeout(config.page_load_timeout)
            self.driver.implicitly_wait(5)
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.session_count = 0
            logger.info("✅ WebDriver created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create WebDriver: {e}")
            self.driver = None
            raise
    
    def get_page(self, url: str) -> bool:
        """Navigate to page with proper error handling"""
        try:
            # Restart driver if overused
            if self.session_count >= self.max_session_uses:
                logger.info(f"🔄 Restarting driver after {self.session_count} uses")
                self.create_driver()
            
            if not self.driver:
                return False
            
            self.driver.get(url)
            self.session_count += 1
            return True
            
        except TimeoutException:
            logger.error(f"❌ Page load timeout: {url}")
            return False
        except (InvalidSessionIdException, WebDriverException) as e:
            logger.error(f"❌ WebDriver session error: {e}")
            try:
                self.create_driver()
                if self.driver:
                    self.driver.get(url)
                    self.session_count += 1
                    return True
            except Exception:
                pass
            return False
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    def quit_driver(self):
        """Safely quit the driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.debug(f"Error quitting driver: {e}")
            finally:
                self.driver = None

def extract_price(soup):
    """Extract price with fallback methods"""
    # Method 1: GTM data
    try:
        gtm_elements = soup.select(".product-gtm-data")
        for gtm_elem in gtm_elements:
            gtm_data = gtm_elem.get("data-gtm")
            if gtm_data:
                try:
                    gtm_json = json.loads(gtm_data)
                    price = gtm_json.get("price")
                    discount = gtm_json.get("discount")
                    if price:
                        return str(price), str(discount) if discount else None
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    
    # Method 2: Price display elements
    price_selectors = [
        ".prodCart__prices strong b",
        ".prodCart__prices b", 
        ".price-final_price .price",
        ".regular-price .price"
    ]
    
    for selector in price_selectors:
        try:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'([\d.,]+)', price_text.replace('₼', '').replace(',', '.'))
                if price_match:
                    return price_match.group(1), None
        except Exception:
            continue
    
    return None, None

def extract_specifications(soup):
    """Extract product specifications"""
    specs = {}
    
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
    except Exception:
        pass
    
    return specs

def extract_images(soup):
    """Extract product images"""
    images = []
    
    try:
        gallery_selectors = [
            ".slider111__thumbs .item",
            ".product-image-gallery .item img"
        ]
        
        for selector in gallery_selectors:
            elements = soup.select(selector)
            for elem in elements:
                if elem.name == 'a':
                    href = elem.get("href")
                    if href and "kontakt.az" in href:
                        images.append(href)
                elif elem.name == 'img':
                    src = elem.get("src") or elem.get("data-src")
                    if src and "kontakt.az" in src:
                        images.append(src)
    except Exception:
        pass
    
    return list(set(images))  # Remove duplicates

def scrape_product(driver: SimpleWebDriver, url: str, attempt: int = 1):
    """Scrape single product with retry logic"""
    
    for retry in range(config.max_retries):
        try:
            logger.info(f"🔍 Scraping [{attempt}] (attempt {retry+1}): {url.split('/')[-1][:50]}")
            
            # Navigate to page
            if not driver.get_page(url):
                if retry < config.max_retries - 1:
                    sleep(random.uniform(3, 6))
                    continue
                else:
                    return None
            
            # Wait for page elements
            try:
                wait = WebDriverWait(driver.driver, config.timeout)
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".prodCart__code"))
                    )
                )
            except TimeoutException:
                logger.debug(f"Timeout waiting for page elements")
            
            # Brief wait for dynamic content
            sleep(random.uniform(2, 4))
            
            # Get page source
            html = driver.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract data
            title_elem = soup.select_one(".page-title .base, .page-title, h1")
            title = title_elem.get_text(strip=True) if title_elem else None
            
            sku_elem = soup.select_one(".prodCart__code")
            sku = sku_elem.get_text(strip=True).replace('№', '').strip() if sku_elem else None
            
            price, discount = extract_price(soup)
            
            # Category from breadcrumb
            category = None
            try:
                breadcrumb = soup.select(".breadcrumb a")
                if breadcrumb:
                    category = " / ".join([c.get_text(strip=True) for c in breadcrumb])
            except Exception:
                pass
            
            # Brand
            brand = None
            try:
                brand_elem = soup.select_one(".product-brand-relation-link__brand, [itemprop='brand']")
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
            except Exception:
                pass
            
            # Specifications
            specs = extract_specifications(soup)
            
            # Images
            images = extract_images(soup)
            
            # Availability
            availability = "In Stock"
            try:
                if soup.select_one(".product-alert-stock__button, .out-of-stock"):
                    availability = "Pre-order / Out of Stock"
            except Exception:
                pass
            
            # Build result
            result = {
                "url": url,
                "title": title,
                "sku": sku,
                "brand": brand,
                "category": category,
                "price": price,
                "discount": discount,
                "availability": availability,
                "specifications": json.dumps(specs, ensure_ascii=False) if specs else None,
                "images": "|".join(images) if images else None,
                "scraped_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Attempt {retry+1} failed: {str(e)}")
            if retry < config.max_retries - 1:
                sleep(random.uniform(4, 8))
                continue
    
    return None

def handle_interrupt(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n🛑 Interrupted by user. Saving progress...")
    sys.exit(0)

def main():
    """Main scraping function - single threaded for reliability"""
    if not urls:
        print("❌ No URLs found! Please add URLs to the 'urls' list at the top of the script.")
        return
    
    # Setup interrupt handler
    signal.signal(signal.SIGINT, handle_interrupt)
    
    print("🚀 Starting Enhanced Kontakt.az scraper v3 (Stable)...")
    print(f"📋 Total URLs: {len(urls)}")
    print(f"🎯 Single-threaded for maximum stability")
    print(f"⚡ Delays: {config.base_delay}-{config.max_delay}s")
    print(f"🔄 Driver restart every {config.session_restart_after} URLs")
    
    # Initialize components
    tracker = ProgressTracker()
    driver = None
    
    # Get pending URLs
    pending_urls = tracker.get_pending_urls(urls)
    
    if not pending_urls:
        print("✅ All URLs already completed!")
        return
    
    print(f"📋 Pending URLs: {len(pending_urls)}")
    
    start_time = time.time()
    
    try:
        driver = SimpleWebDriver()
        
        for i, url in enumerate(pending_urls):
            try:
                result = scrape_product(driver, url, i + 1)
                tracker.add_result(url, result)
                
                if result:
                    logger.info(f"✅ [{i+1}/{len(pending_urls)}] {result.get('title', 'Unknown')[:50]}")
                else:
                    logger.warning(f"❌ [{i+1}/{len(pending_urls)}] Failed: {url}")
                
                # Adaptive delay
                if result:
                    delay = random.uniform(config.base_delay, config.max_delay)
                else:
                    delay = random.uniform(config.max_delay, config.max_delay * 1.5)
                
                logger.debug(f"😴 Sleeping {delay:.1f}s")
                sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                tracker.add_result(url, None)
    
    finally:
        if driver:
            driver.quit_driver()
        
        # Save final progress
        tracker.save_progress()
        
        # Save results to CSV
        if tracker.results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kontakt_products_v3_{timestamp}.csv"
            
            print(f"\n💾 Saving {len(tracker.results)} products to {filename}")
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                if tracker.results:
                    writer = csv.DictWriter(f, fieldnames=tracker.results[0].keys())
                    writer.writeheader()
                    writer.writerows(tracker.results)
            
            print(f"✅ Data saved to {filename}")
        
        # Final statistics
        end_time = time.time()
        duration = end_time - start_time
        total_completed = len(tracker.completed_urls)
        total_failed = len(tracker.failed_urls)
        
        print(f"\n📊 Final Summary:")
        print(f"   Total URLs: {len(urls)}")
        print(f"   Completed: {total_completed}")
        print(f"   Failed: {total_failed}")
        if total_completed + total_failed > 0:
            print(f"   Success rate: {total_completed/(total_completed + total_failed)*100:.1f}%")
        print(f"   Duration: {duration/60:.1f} minutes")
        if total_completed > 0:
            print(f"   Average time per URL: {duration/total_completed:.1f}s")

if __name__ == "__main__":
    main()
