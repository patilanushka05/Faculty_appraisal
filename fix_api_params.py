import os
import re

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_params(match):
        func_head = match.group(1)
        params_str = match.group(2)
        func_tail = match.group(3)
        
        # Split parameters while respecting brackets (for Annotated)
        params = []
        bracket_level = 0
        current_param = ""
        for char in params_str:
            if char == '[':
                bracket_level += 1
            elif char == ']':
                bracket_level -= 1
            
            if char == ',' and bracket_level == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        if current_param.strip():
            params.append(current_param.strip())
            
        new_params = []
        has_default = False
        changed = False
        
        # Target parameters
        targets = [
            'current_user: CurrentUser',
            'db: Annotated[AsyncSession, Depends(get_db)]',
            'db: AsyncSession'
        ]
        
        for p in params:
            new_p = p
            # If it matches any target and doesn't have a default, add = None
            for t in targets:
                if t in p and ' = ' not in p:
                    new_p = p + ' = None'
                    changed = True
                    break
            
            if ' = ' in new_p:
                has_default = True
            elif has_default:
                # SyntaxError if non-default follows default
                new_p = p + ' = None'
                changed = True
            
            new_params.append(new_p)
            
        if changed:
            # Join with newline and indentation if original was multiline
            if '\n' in params_str:
                return f"{func_head}(\n    {',\n    '.join(new_params)}\n){func_tail}"
            return f"{func_head}({', '.join(new_params)}){func_tail}"
        return match.group(0)

    # Improved regex for async def functions
    pattern = r'(async def \w+)\((.*?)\)([\s\w\-\>\[\],.]*:)'
    
    new_content = re.sub(pattern, replace_params, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

api_dirs = ['src/api/Part_A/v1', 'src/api/Part_B/v1', 'src/api/overall/v1']
for d in api_dirs:
    if not os.path.exists(d): continue
    for f in os.listdir(d):
        if f.endswith('.py') and f != '__init__.py':
            path = os.path.join(d, f)
            if fix_file(path):
                print(f"Fixed {path}")
