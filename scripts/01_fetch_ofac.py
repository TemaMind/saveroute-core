from scripts._utils import download
from scripts.config import OFAC_URL
download(OFAC_URL, "ofac_sdn.csv")
