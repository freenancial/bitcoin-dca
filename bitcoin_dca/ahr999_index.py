import urllib.request
import re

INDEX_RESOURCE_URL = "https://btajy.com/btcie.com/ahr999/datanew.php"


def getCurrentIndexValue():
    pattern = "囤比特币 ahr999指数(.*) BtcIE"
    content = _getWebContent()
    value_str = re.search(pattern, content).group(1)
    return float(value_str)


def _getWebContent():
    return urllib.request.urlopen(INDEX_RESOURCE_URL).read().decode()
