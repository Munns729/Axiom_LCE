
import sys

path = r"c:\Users\Jack\Documents\Axiom_LCE\backend\services\scenario_service.py"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: line 121
target1 = """        response = await self.mistral.client.chat.complete(
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )"""
replacement1 = """        response = await asyncio.to_thread(
            self.mistral.client.chat.complete,
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )"""

# Fix 2: line 350
target2 = """        response = await self.mistral.client.chat.complete(
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )"""
# Same replacement because both had 0.3 temp and same structure

if target1 in content:
    content = content.replace(target1, replacement1)
    print("Fixed first instance")

if target2 in content:
    content = content.replace(target2, replacement1) # target2 is the same as target1
    print("Fixed second instance")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
