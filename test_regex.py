import re

cases = [
    'remind me to submit my project tomorrow at 5 pm',
    'remind me to submit my project tomorrow at 5:00 pm',
    'remind me to submit my project at tomorrow, 5 pm',
    'remind me to submit my project at tomorrow, 5:00 pm',
    'remind me to submit my project tomorrow, 5 pm',
    'remind me to submit my project tomorrow, 5:00 pm',
    'remind me tomorrow to submit my project',
    'remind me in 30 minutes to clean the house',
]

pattern = r'(?:at\s+)?(today|tomorrow|in \d+ (?:minutes|hours|days)|next \w+|this evening)(?:[\s,]+(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))?'

for c in cases:
    match = re.search(pattern, c)
    if match:
        dt_str = match.group()
        task_name = re.sub(r'^(remind me to|remind me)\b\s*', '', c, flags=re.IGNORECASE)
        task_name = task_name.replace(dt_str, '')
        task_name = re.sub(r'^\s*to\b\s*', '', task_name, flags=re.IGNORECASE)
        task_name = re.sub(r'\s*(at|,)\s*$', '', task_name, flags=re.IGNORECASE).strip()
        
        print(f"Original: {c}")
        print(f"Date: {dt_str}")
        print(f"Task: {task_name}\n")
