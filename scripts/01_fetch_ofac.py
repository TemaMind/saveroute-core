from _utils import download
from 00_config import OFAC_URL
download(OFAC_URL, "ofac_sdn.csv")