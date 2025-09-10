```python
import requests
import netaddr

def fetch_prefixes(url):
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    cidr_list = []
    for prefix in data.get("prefixes", []):
        if "ipv4Prefix" in prefix:
            cidr_list.append(str(netaddr.IPNetwork(prefix["ipv4Prefix"])))
        elif "ipv6Prefix" in prefix:
            cidr_list.append(str(netaddr.IPNetwork(prefix["ipv6Prefix"])))
    return set(cidr_list)

goog = fetch_prefixes("https://www.gstatic.com/ipranges/goog.json")
cloud = fetch_prefixes("https://www.gstatic.com/ipranges/cloud.json")

service_ranges = sorted(goog - cloud)

# Wrap in quotes and join on one line
line = ",".join(f"\"{cidr}\"" for cidr in service_ranges)

with open("GoogleServiceRanges.txt", "w") as f:
    f.write(line)

print("Export complete! Saved as GoogleServiceRanges.txt")
