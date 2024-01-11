import re

def extract_domains(file_path):
    domains = set()
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'https://(.*?\.com|.*?\.cn)', line)
            if match:
                domains.add(match.group(1))
    return domains

