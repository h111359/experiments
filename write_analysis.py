import pathlib

new_content = pathlib.Path(r'c:\Hristo\projects\AI_Builder\analysis_new.md').read_text(encoding='utf-8')
pathlib.Path(r'c:\Hristo\projects\AI_Builder\.aib_memory\analysis.md').write_text(new_content, encoding='utf-8', newline='\n')
print('Done')
