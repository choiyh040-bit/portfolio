import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# We need to split the "Graphic & Web Design" section into two sections.
# Web Design items: Work 1, 2, 4, 5, 6, 19, 20
# Editorial Design items: Work 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

# Let's use regex to find all work items
works_grid_match = re.search(r'<h3 class="category-title">Graphic & Web Design</h3>\s*<div class="works-grid">(.*?)</div>\s*<!-- 새로 추가된 로고 디자인 섹션 -->', content, re.DOTALL)
if not works_grid_match:
    print("Could not find works-grid section")
    exit(1)

works_html = works_grid_match.group(1)
items = re.findall(r'<!-- Work [a-zA-Z0-9\s()]+ -->\s*<div class="work-item">.*?</div>\s*</div>', works_html, re.DOTALL)
# Wait, the closing tag is tricky. Let's use a simpler split by '<!-- Work'
items_raw = works_html.split('<!-- Work ')
items = []
for item in items_raw[1:]:
    items.append('<!-- Work ' + item.strip())

web_items = []
editorial_items = []

web_keywords = ["W컨셉", "퓨린이 여성의류", "인스타그램", "퓨린이 유튜브", "틱톡", "마이스태프"]

for item in items:
    is_web = False
    for kw in web_keywords:
        if kw in item:
            is_web = True
            break
    if is_web:
        web_items.append(item)
    else:
        editorial_items.append(item)

# Transform web items to use popup with data-link
for i in range(len(web_items)):
    # Find a href="..." target="_blank"
    # and change to href="#" class="gallery-trigger" data-gallery="..." data-link="..."
    match = re.search(r'<a href="([^"]+)" target="_blank"[^>]*>\s*<img src="([^"]+)"', web_items[i], re.DOTALL)
    if match:
        url = match.group(1)
        img_src = match.group(2)
        # Check if it's already a gallery-trigger? No, we matched target="_blank"
        new_a = f'<a href="#" class="gallery-trigger" data-gallery="{img_src}" data-link="{url}">' + f'\n              <img src="{img_src}"'
        web_items[i] = re.sub(r'<a href="[^"]+" target="_blank"[^>]*>\s*<img src="[^"]+"', new_a, web_items[i], flags=re.DOTALL)

# For mice_2025 (iframe-trigger), keep it as is or change it?
# The user said: "W컨셉, 유튜브, 틱톡 등 외부 URL로 가는 프로젝트들도 클릭 시 일단 팝업을 띄웁니다. 팝업 안에는 해당 사이트의 긴 캡처 이미지(또는 대표 썸네일)를 보여주고, 팝업 상단이나 하단에 [👉 실제 사이트 방문하기] 같은 명확한 버튼을 배치하는 것입니다."
# mice_2025 is an internal HTML page (iframe). It's technically already opening in a popup. We can leave it as iframe-trigger, but maybe change the iframe popup to have a link?
# Mice 2025 is fine as iframe because it embeds perfectly.

new_works_html = """
        <h3 class="category-title">Web Design</h3>
        <div class="works-grid">
          """ + "\n\n          ".join(web_items) + """
        </div>

        <h3 class="category-title">Graphic & Editorial Design</h3>
        <div class="works-grid">
          """ + "\n\n          ".join(editorial_items) + """
        </div>
"""

new_content = content[:works_grid_match.start()] + new_works_html.strip() + "\n\n        " + content[works_grid_match.end() - len('<!-- 새로 추가된 로고 디자인 섹션 -->'):]

# Also need to add the modal external link button in the modal HTML
modal_btn_html = """
    <div id="modalContentWrapper" style="display:flex; flex-direction:column; justify-content:flex-start; align-items:center; width:100%; min-height:100%;">
      <!-- External Link Button -->
      <div id="modalBtnContainer" style="display:none; width:90%; max-width:800px; text-align:right; padding:10px 0; margin-top:20px;">
        <a id="modalExternalLink" href="#" target="_blank" style="display:inline-block; padding:12px 24px; background:#333; color:#fff; border-radius:30px; font-weight:bold; text-decoration:none; box-shadow:0 4px 10px rgba(0,0,0,0.2); transition:transform 0.2s;">
          👉 실제 사이트 방문하기
        </a>
      </div>
      <img class="modal-content" id="modalImg" style="display:none;">
"""
new_content = new_content.replace('<div id="modalContentWrapper" style="display:flex; justify-content:center; align-items:flex-start; width:100%; min-height:100%;">\n      <img class="modal-content" id="modalImg" style="display:none;">', modal_btn_html)

# Update the JS for gallery-trigger
js_update_trigger = """
        const customWidth = this.getAttribute('data-width');
        galleryWrapper.style.maxWidth = customWidth ? customWidth : '800px';
        
        const dataLink = this.getAttribute('data-link');
        const modalBtnContainer = document.getElementById("modalBtnContainer");
        const modalExternalLink = document.getElementById("modalExternalLink");
        if (dataLink) {
          modalExternalLink.href = dataLink;
          modalBtnContainer.style.display = "block";
        } else {
          modalBtnContainer.style.display = "none";
        }
"""
new_content = new_content.replace("""
        const customWidth = this.getAttribute('data-width');
        galleryWrapper.style.maxWidth = customWidth ? customWidth : '800px';
""", js_update_trigger)

# Update single image (zoomable) JS as well to hide the button
js_update_zoomable = """
        const customWidth = this.getAttribute('data-width');
        modalImg.style.width = customWidth ? '100%' : 'auto';
        modalImg.style.maxWidth = customWidth ? customWidth : '90vw';
        
        const dataLink = this.getAttribute('data-link');
        const modalBtnContainer = document.getElementById("modalBtnContainer");
        const modalExternalLink = document.getElementById("modalExternalLink");
        if (dataLink) {
          modalExternalLink.href = dataLink;
          modalBtnContainer.style.display = "block";
        } else {
          if (modalBtnContainer) modalBtnContainer.style.display = "none";
        }
"""
new_content = new_content.replace("""
        const customWidth = this.getAttribute('data-width');
        modalImg.style.width = customWidth ? '100%' : 'auto';
        modalImg.style.maxWidth = customWidth ? customWidth : '90vw';
""", js_update_zoomable)

# Hide button for iframe
js_update_iframe = """
        galleryWrapper.style.display = "none";
        const modalBtnContainer = document.getElementById("modalBtnContainer");
        if (modalBtnContainer) modalBtnContainer.style.display = "none";
"""
new_content = new_content.replace('galleryWrapper.style.display = "none";', js_update_iframe)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_content)
print("done")
