from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path('/Users/lucky/Documents/ChatGPT/Ontology')
ASSET_DIR = ROOT / 'prd_assets'
ASSET_DIR.mkdir(exist_ok=True)
OUTPUT = ROOT / '汽车后市场智能客服Ontology产品需求与架构设计V1.0.docx'
FONT_PATH = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'

NAVY = '17365D'
BLUE = '2F75B5'
LIGHT_BLUE = 'EAF2F8'
PALE_BLUE = 'F4F8FC'
GRAY = '666666'
LIGHT_GRAY = 'F2F2F2'
BORDER = 'D9D9D9'
WHITE = 'FFFFFF'
BLACK = '000000'
GREEN = '2E7D32'
ORANGE = 'B45F06'
RED = 'A61B1B'


def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size=size)


def draw_box(draw, xy, title, body='', fill='#EAF2F8', outline='#AAB7C4', title_fill='#17365D'):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=16, fill=fill, outline=outline, width=2)
    draw.text((x1 + 18, y1 + 14), title, font=font(25, True), fill=title_fill)
    if body:
        lines = []
        for paragraph in body.split('\n'):
            lines.extend(wrap(paragraph, max(10, int((x2 - x1) / 25))))
        draw.multiline_text((x1 + 18, y1 + 54), '\n'.join(lines), font=font(19), fill='#333333', spacing=7)


def arrow(draw, start, end, color='#607D8B', width=4):
    draw.line([start, end], fill=color, width=width)
    x2, y2 = end
    x1, y1 = start
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 > x1 else -1
        pts = [(x2, y2), (x2 - sign * 16, y2 - 9), (x2 - sign * 16, y2 + 9)]
    else:
        sign = 1 if y2 > y1 else -1
        pts = [(x2, y2), (x2 - 9, y2 - sign * 16), (x2 + 9, y2 - sign * 16)]
    draw.polygon(pts, fill=color)


def save_architecture():
    img = Image.new('RGB', (1700, 1120), 'white')
    d = ImageDraw.Draw(img)
    d.text((50, 28), '汽车后市场智能客服 Ontology 总体架构', font=font(36, True), fill='#000000')
    layers = [
        ('渠道与交互层', ['App与小程序', '网页客服', '企业微信', '人工坐席工作台']),
        ('对话理解层', ['统一对话API', '会话与身份', '意图识别小模型', '实体与参数抽取']),
        ('AI运行编排层', ['ServiceRequest', '能力路由', '通用LangGraph', '回答生成']),
        ('可执行本体层', ['对象与关系', '能力注册', '业务与风险规则', 'Function与Action', '权限与审计']),
        ('数据知识与系统层', ['对象数据访问', 'Ontology RAG', '系统连接器', '订单库存门店', '会员质保预约'])
    ]
    colors = ['#F4F8FC', '#EEF5FA', '#E8F2F6', '#E8F4EE', '#F7F3EA']
    y = 95
    for idx, (label, nodes) in enumerate(layers):
        d.text((50, y + 48), label, font=font(23, True), fill='#17365D')
        x = 285
        gap = 18
        width = int((1350 - gap * (len(nodes) - 1)) / len(nodes))
        for node in nodes:
            draw_box(d, (x, y, x + width, y + 135), node, fill=colors[idx])
            x += width + gap
        if idx < len(layers) - 1:
            arrow(d, (985, y + 138), (985, y + 180), width=3)
        y += 198
    img.save(ASSET_DIR / 'architecture.png')


def save_runtime_flow():
    img = Image.new('RGB', (1600, 1250), 'white')
    d = ImageDraw.Draw(img)
    d.text((45, 25), '单轮对话运行流程', font=font(36, True), fill='#000000')
    steps = [
        ('1 用户请求', 'Query、登录身份、渠道、会话'),
        ('2 语言理解', '一级/二级意图、置信度、实体、缺失参数'),
        ('3 创建运行实例', 'ConversationTurn、IntentPrediction、ServiceRequest'),
        ('4 解析业务对象', 'Customer、Vehicle、Order、Appointment等对象实例'),
        ('5 能力与策略', '选择Capability，校验业务规则、风险和权限'),
        ('6 编排执行', 'Function查询、RAG检索、Agent分析或Action提案'),
        ('7 确认与审批', '低风险直接回答；写操作用户确认；高风险人工审核'),
        ('8 写回与回答', '执行Action、同步源系统、生成结构化与文本结果'),
        ('9 审计与反馈', 'DecisionRecord、ActionExecution、用户反馈、指标')
    ]
    left = 145
    top = 95
    bw = 1310
    bh = 95
    for i, (title, body) in enumerate(steps):
        fill = '#EAF2F8' if i % 2 == 0 else '#EAF4EE'
        draw_box(d, (left, top, left + bw, top + bh), title, body, fill=fill)
        if i < len(steps) - 1:
            arrow(d, (800, top + bh + 2), (800, top + bh + 32), width=3)
        top += 125
    img.save(ASSET_DIR / 'runtime_flow.png')


def save_ontology_map():
    img = Image.new('RGB', (1700, 1100), 'white')
    d = ImageDraw.Draw(img)
    d.text((45, 25), '汽车后市场核心业务本体', font=font(36, True), fill='#000000')
    groups = {
        '客户与车辆': ((50, 115, 510, 390), 'Customer\nMemberAccount\nVehicle\nVehicleModel'),
        '商品与适配': ((620, 90, 1080, 390), 'TireProduct\nTireSKU\nTireCompatibility\nPrice · Promotion'),
        '门店与库存': ((1190, 115, 1650, 390), 'Store\nStoreInventory\nServiceSlot'),
        '订单与服务': ((50, 560, 510, 865), 'Order\nServiceAppointment\nRepairPlan\nMaintenancePlan\nQuote'),
        '保障与售后': ((620, 560, 1080, 865), 'WarrantyPolicy\nWarrantyClaim\nAfterSalesCase\nComplaint'),
        'AI运行与审计': ((1190, 535, 1650, 890), 'ConversationTurn\nIntentPrediction\nServiceRequest\nRiskAssessment\nDecisionRecord\nActionExecution')
    }
    for idx, (title, (xy, body)) in enumerate(groups.items()):
        fill = ['#EAF2F8', '#EAF4EE', '#F7F3EA'][idx % 3]
        draw_box(d, xy, title, body, fill=fill)
    arrows = [
        ((510, 250), (620, 250), '拥有车辆并匹配商品'),
        ((1080, 250), (1190, 250), '商品在门店形成库存'),
        ((280, 390), (280, 560), '客户产生订单与预约'),
        ((850, 390), (850, 560), '商品受质保政策约束'),
        ((1420, 390), (1420, 535), '交互生成运行记录'),
        ((510, 710), (620, 710), '订单关联理赔与售后'),
        ((1080, 710), (1190, 710), '业务过程形成决策审计')
    ]
    for start, end, label in arrows:
        arrow(d, start, end, width=3)
        lx = (start[0] + end[0]) // 2
        ly = (start[1] + end[1]) // 2
        d.text((lx - 80, ly - 30), label, font=font(17), fill='#555555')
    img.save(ASSET_DIR / 'ontology_map.png')


def save_chat_wireframe():
    img = Image.new('RGB', (1500, 980), 'white')
    d = ImageDraw.Draw(img)
    d.text((45, 25), '客户聊天端原型', font=font(36, True), fill='#000000')
    d.rounded_rectangle((220, 90, 1280, 925), radius=28, outline='#7A8A99', width=3, fill='#FAFAFA')
    d.rectangle((220, 90, 1280, 180), fill='#17365D')
    d.text((265, 120), '智能服务助手', font=font(28, True), fill='white')
    draw_box(d, (650, 220, 1190, 320), '用户', '把我明天下午的保养预约取消掉', fill='#EAF2F8')
    draw_box(d, (300, 355, 1040, 495), '系统识别到一条预约', '9月8日 14:00 · 徐汇门店 · 常规保养\n取消后需重新预约，请确认是否取消。', fill='#FFFFFF')
    d.rounded_rectangle((350, 535, 650, 610), radius=14, fill='#17365D')
    d.text((435, 555), '确认取消', font=font(24, True), fill='white')
    d.rounded_rectangle((690, 535, 990, 610), radius=14, outline='#9AA7B2', width=2, fill='#FFFFFF')
    d.text((780, 555), '暂不取消', font=font(24), fill='#333333')
    draw_box(d, (300, 650, 1040, 760), 'Action结果', '预约状态已更新。操作编号 AX-20260908-1021', fill='#EAF4EE')
    d.rounded_rectangle((270, 820, 1110, 885), radius=16, outline='#B0B8C0', width=2, fill='white')
    d.text((300, 836), '输入问题或选择下一步操作', font=font(22), fill='#777777')
    d.rounded_rectangle((1130, 820, 1235, 885), radius=16, fill='#2F75B5')
    d.text((1157, 837), '发送', font=font(22, True), fill='white')
    img.save(ASSET_DIR / 'chat_wireframe.png')


def save_agent_wireframe():
    img = Image.new('RGB', (1600, 980), 'white')
    d = ImageDraw.Draw(img)
    d.text((45, 25), '人工坐席与审核工作台原型', font=font(36, True), fill='#000000')
    d.rectangle((45, 90, 1555, 940), outline='#7A8A99', width=3, fill='#FAFAFA')
    d.rectangle((45, 90, 1555, 165), fill='#17365D')
    d.text((80, 112), '待处理服务请求  SR-20260908-2031', font=font(26, True), fill='white')
    draw_box(d, (80, 205, 480, 500), '客户与对象', '客户 C10086\n车辆 BMW 3系 2023\n订单 O90008\n轮胎 SKU-T101\n会员等级 金卡', fill='#EAF2F8')
    draw_box(d, (520, 205, 1020, 500), 'AI分析与证据', '意图 理赔更换申请 0.93\n基础风险 L4\n命中规则 WARRANTY-03\n证据 订单、质保政策、用户图片\n建议 创建理赔案件并补充胎面照片', fill='#EAF4EE')
    draw_box(d, (1060, 205, 1515, 500), '处理动作', '请求补件\n创建理赔案件\n驳回并说明\n转交技术专家', fill='#F7F3EA')
    draw_box(d, (80, 550, 1000, 875), '会话与时间线', '21:06 用户提交理赔问题\n21:06 意图识别完成\n21:06 订单与质保资格校验完成\n21:07 检测到材料缺失\n21:07 转入人工审核队列', fill='#FFFFFF')
    draw_box(d, (1040, 550, 1515, 875), '审核意见', '填写处理理由\n选择下一步Action\n提交后生成ActionExecution记录', fill='#FFFFFF')
    img.save(ASSET_DIR / 'agent_wireframe.png')


def save_admin_wireframe():
    img = Image.new('RGB', (1600, 980), 'white')
    d = ImageDraw.Draw(img)
    d.text((45, 25), 'Ontology配置管理端原型', font=font(36, True), fill='#000000')
    d.rectangle((45, 90, 1555, 940), outline='#7A8A99', width=3, fill='#FAFAFA')
    d.rectangle((45, 90, 340, 940), fill='#17365D')
    menu = ['对象与关系', '意图与能力', '业务规则', '风险与权限', 'Function与Action', '知识映射', '版本与发布']
    y = 150
    for i, item in enumerate(menu):
        if i == 1:
            d.rectangle((65, y - 8, 320, y + 48), fill='#2F75B5')
        d.text((90, y), item, font=font(23, i == 1), fill='white')
        y += 82
    d.text((390, 125), '意图与能力映射', font=font(30, True), fill='#17365D')
    draw_box(d, (390, 190, 970, 410), 'ORDER CANCEL', '一级意图 订单服务\n二级意图 修改取消预约\nCapability ManageAppointment\n基础风险 L3', fill='#EAF2F8')
    draw_box(d, (1010, 190, 1505, 410), '运行依赖', '对象 Customer、Appointment\nFunction GetAppointment\nAction CancelAppointment\nResponse ActionConfirmation', fill='#EAF4EE')
    draw_box(d, (390, 465, 1505, 740), '发布检查', '对象映射完整 · 规则测试通过 · Action权限已审批\n回归样本 128条 · 影子运行通过率 97.8%\n当前生产版本 v1.6 · 待发布版本 v1.7', fill='#FFFFFF')
    d.rounded_rectangle((1190, 800, 1505, 875), radius=14, fill='#17365D')
    d.text((1270, 820), '提交灰度发布', font=font(23, True), fill='white')
    img.save(ASSET_DIR / 'admin_wireframe.png')


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        tc_pr.append(shd)
    shd.set(qn('w:fill'), fill)


def set_cell_border(cell, color=BORDER, size='6'):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in('w:tcBorders')
    if borders is None:
        borders = OxmlElement('w:tcBorders')
        tc_pr.append(borders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        tag = 'w:' + edge
        el = borders.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            borders.append(el)
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), size)
        el.set(qn('w:color'), color)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in('w:tcMar')
    if tc_mar is None:
        tc_mar = OxmlElement('w:tcMar')
        tc_pr.append(tc_mar)
    for m, v in [('top', top), ('start', start), ('bottom', bottom), ('end', end)]:
        node = tc_mar.find(qn('w:' + m))
        if node is None:
            node = OxmlElement('w:' + m)
            tc_mar.append(node)
        node.set(qn('w:w'), str(v))
        node.set(qn('w:type'), 'dxa')


def repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement('w:tblHeader')
    tbl_header.set(qn('w:val'), 'true')
    tr_pr.append(tbl_header)


def set_repeat_table_header(table):
    repeat_table_header(table.rows[0])


def set_repeat_rows(table):
    for row in table.rows:
        row._tr.get_or_add_trPr()


def set_run_font(run, name='Arial Unicode MS', east='Arial Unicode MS', size=None, bold=None, color=None):
    run.font.name = name
    rfonts = run._element.get_or_add_rPr().rFonts
    rfonts.set(qn('w:ascii'), name)
    rfonts.set(qn('w:hAnsi'), name)
    rfonts.set(qn('w:eastAsia'), east)
    rfonts.set(qn('w:cs'), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def set_paragraph_spacing(p, before=0, after=6, line=1.25):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def add_para(doc, text='', bold_lead=None, keep=False, after=6):
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2)
    else:
        r = p.add_run(text)
        set_run_font(r)
    set_paragraph_spacing(p, after=after)
    p.paragraph_format.keep_together = keep
    return p


def add_bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style='List Bullet' if level == 0 else 'List Bullet 2')
        r = p.add_run(item)
        set_run_font(r)
        set_paragraph_spacing(p, after=3)


def add_numbered(doc, items):
    # Use explicit section-local numbering. Word/LibreOffice may otherwise
    # continue the same abstract list across distant sections.
    for index, item in enumerate(items, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        r = p.add_run(f'{index}.  {item}')
        set_run_font(r)
        set_paragraph_spacing(p, after=4)


def add_table(doc, headers, rows, widths=None, font_size=9.2):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    hdr = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr[i].text = str(header)
        shade_cell(hdr[i], NAVY)
        hdr[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(hdr[i], 110, 100, 110, 100)
        set_cell_border(hdr[i])
        for p in hdr[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                set_run_font(run, size=font_size, bold=True, color=WHITE)
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            if ridx % 2 == 1:
                shade_cell(cells[i], PALE_BLUE)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cells[i], 95, 100, 95, 100)
            set_cell_border(cells[i])
            for p in cells[i].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(str(value)) < 18 else WD_ALIGN_PARAGRAPH.LEFT
                set_paragraph_spacing(p, after=0, line=1.1)
                for run in p.runs:
                    set_run_font(run, size=font_size)
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    set_repeat_table_header(table)
    p = doc.add_paragraph()
    set_paragraph_spacing(p, after=2)
    return table


def add_figure(doc, path, caption, width=6.8):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    inline_shape = p.add_run().add_picture(str(path), width=Inches(width))
    # Caption doubles as meaningful alternative text for accessibility tools.
    inline_shape._inline.docPr.set('descr', caption)
    inline_shape._inline.docPr.set('title', caption)
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption)
    set_run_font(r, size=9, color=GRAY)
    set_paragraph_spacing(c, after=10)


def page_break(doc):
    return None


def hard_page_break(doc):
    doc.add_page_break()


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


def configure_doc(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.72)
    section.right_margin = Inches(0.72)

    styles = doc.styles
    normal = styles['Normal']
    normal.font.name = 'Arial Unicode MS'
    normal._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
    normal._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
    normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
    normal._element.rPr.rFonts.set(qn('w:cs'), 'Arial Unicode MS')
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    title = styles['Title']
    title.font.name = 'Arial Unicode MS'
    title._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
    title._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
    title._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
    title._element.rPr.rFonts.set(qn('w:cs'), 'Arial Unicode MS')
    title.font.size = Pt(28)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title_ppr = title._element.get_or_add_pPr()
    title_border = title_ppr.find(qn('w:pBdr'))
    if title_border is not None:
        title_ppr.remove(title_border)

    heading_sizes = {1: 17, 2: 14, 3: 12}
    for i, size in heading_sizes.items():
        st = styles[f'Heading {i}']
        st.font.name = 'Arial Unicode MS'
        st._element.rPr.rFonts.set(qn('w:ascii'), 'Arial Unicode MS')
        st._element.rPr.rFonts.set(qn('w:hAnsi'), 'Arial Unicode MS')
        st._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial Unicode MS')
        st._element.rPr.rFonts.set(qn('w:cs'), 'Arial Unicode MS')
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(12 if i == 1 else 8)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run('汽车后市场智能客服 Ontology 产品需求与架构设计')
    set_run_font(hr, size=8.5, color=GRAY)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run('内部评审材料   V1.0   2026年9月')
    set_run_font(r, size=8.5, color=GRAY)


def build_doc():
    for maker in [save_architecture, save_runtime_flow, save_ontology_map, save_chat_wireframe, save_agent_wireframe, save_admin_wireframe]:
        maker()

    doc = Document()
    configure_doc(doc)

    # Cover
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph(style='Title')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('汽车后市场智能客服 Ontology 产品需求与架构设计')
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run('新项目立项评审版本')
    set_run_font(r, size=16, bold=True, color=BLACK)
    set_paragraph_spacing(sub, before=8, after=28)
    meta = [
        ('文档版本', 'V1.0'),
        ('方案选择', '方案B  Ontology驱动的业务能力平台'),
        ('规划范围', '20个二级意图  查询与Action  人工审核  全链路审计'),
        ('计划周期', '28周'),
        ('预算区间', '人民币440万元至690万元  不含可选私有化硬件'),
        ('评审日期', '2026年9月')
    ]
    add_table(doc, ['项目', '内容'], meta, widths=[1.6, 5.1], font_size=10)
    add_para(doc, '本文用于产品、业务、技术、安全和项目管理联合评审。评审需要确认范围、业务规则责任人、系统接口条件、人工审核边界、资源投入和预算。', after=0)

    hard_page_break(doc)
    add_heading(doc, '文档结论', 1)
    add_para(doc, '本项目采用方案B。Ontology负责统一业务对象、关系、能力、规则、权限和Action；意图识别小模型负责理解用户诉求；LangGraph负责编排运行步骤；RAG提供非结构化知识；现有业务系统继续保存订单、库存、会员、预约和理赔等事实。')
    add_para(doc, '一期按生产试点设计，覆盖图中20个二级意图，并优先上线5个代表性场景。项目计划周期为28周，预计供应侧投入约72至86人月，客户侧另需业务和IT骨干持续参与。预算基线为人民币440万元至690万元；如果要求模型、向量库和全部中间件私有化部署，还需增加硬件和软件许可预算。')
    add_heading(doc, '目录', 1)
    toc = [
        '1 项目背景与决策', '2 产品价值与项目目标', '3 产品范围与用户角色', '4 业务场景与需求优先级',
        '5 产品总体架构', '6 Ontology本体设计', '7 运行流程与决策闭环', '8 各端产品需求与原型',
        '9 功能模块需求', '10 数据 RAG 与系统集成', '11 安全权限风险与审计', '12 非功能需求',
        '13 迭代与发布机制', '14 项目计划与里程碑', '15 团队与资源投入', '16 费用估算',
        '17 验收标准', '18 项目风险与待决策事项', '附录A 核心配置示例', '附录B 术语表'
    ]
    add_bullets(doc, toc)

    hard_page_break(doc)
    add_heading(doc, '1 项目背景与决策', 1)
    add_heading(doc, '1.1 业务背景', 2)
    add_para(doc, '汽车后市场客服同时处理商品咨询、原厂保障、订单服务、门店服务、账户会员、会话控制和维修保养报价。用户问题表面上是对话，实际会访问客户、车辆、商品、订单、库存、门店、预约、质保和售后系统。部分请求只需回答知识，部分请求会改变订单或服务状态。')
    add_para(doc, '现有意图驱动方案可以快速上线，但每个意图容易形成独立LangGraph分支、Method、Prompt和知识库路由。业务规模扩大后，相同的客户查询、订单校验、权限判断和转人工逻辑会在多个流程重复。规则更新需要修改代码，运行证据分散在节点日志中。')
    add_heading(doc, '1.2 方案决策', 2)
    add_para(doc, '项目选择Ontology驱动的业务能力平台。系统先把用户诉求映射到标准业务对象和Capability，再由规则、Function和Action完成查询或执行。LangGraph继续作为运行编排器，不承担业务语义和权限的唯一来源。')
    add_table(doc, ['组件', '职责', '不承担的职责'], [
        ('意图识别小模型', '输出一级意图、二级意图、置信度和候选意图', '不直接操作订单、库存或预约'),
        ('Ontology', '定义对象、关系、能力、规则、Action、权限和审计对象', '不替代自然语言理解模型'),
        ('LangGraph', '控制节点顺序、分支、等待、恢复和异常处理', '不保存唯一业务规则'),
        ('RAG', '检索产品说明、质保条款、维修保养知识', '不提供实时库存、价格和订单状态'),
        ('Function与Action', '查询业务事实或改变业务状态', '不自行生成未经证据支持的回答'),
        ('大模型', '参数抽取、证据归纳、解释和语言生成', '不绕过权限和Action前置条件')
    ], widths=[1.35, 2.8, 2.55])

    add_heading(doc, '1.3 产品原则', 2)
    add_bullets(doc, [
        '真实业务事实以源系统为准。本体通过虚拟映射、索引或缓存提供统一对象视图。',
        '读操作使用Function，改变状态的操作必须定义为Action。',
        '意图风险只是基础风险，最终风险还要考虑数据敏感度、Action、业务状态和模型置信度。',
        '大模型可以生成建议和解释，关键资格、金额、权限和执行条件由确定性规则校验。',
        '每次运行记录输入、对象版本、规则版本、证据、人工修改和Action结果。'
    ])

    page_break(doc)
    add_heading(doc, '2 产品价值与项目目标', 1)
    add_heading(doc, '2.1 产品价值', 2)
    add_table(doc, ['价值对象', '当前问题', '目标变化'], [
        ('客户', '需要在多个入口查询商品、订单、门店和售后', '一个对话入口完成咨询、查询、申请和进度跟踪'),
        ('客服坐席', '重复查询多个系统，人工整理上下文', '收到结构化客户、车辆、订单、证据和建议'),
        ('业务团队', '规则散落在代码和Prompt中', '规则版本化管理并记录命中依据'),
        ('技术团队', '每个意图单独开发流程', '复用对象、Function、Action和公共LangGraph'),
        ('管理与合规', '难以还原AI为何回答或执行', '通过DecisionRecord和ActionExecution追踪全过程')
    ], widths=[1.15, 2.65, 2.9])
    add_heading(doc, '2.2 项目目标', 2)
    add_bullets(doc, [
        '覆盖20个二级意图，其中知识问答、个人数据查询、业务Action和人工转接均具备标准处理链路。',
        '建立12至18个核心业务Object Type、不少于15个Capability、20至30个Function以及8至12个Action。',
        '形成一张公共LangGraph和不超过5张特殊子图，减少按意图复制流程。',
        '让新增相似意图至少复用60%的对象、Function、Action和知识映射。',
        '对写操作实现100%的身份校验、前置条件、用户确认或人工审批，以及完整审计。'
    ])
    add_heading(doc, '2.3 建议KPI', 2)
    add_table(doc, ['指标', '试点目标', '正式运营目标', '测量方式'], [
        ('一级意图准确率', '不低于95%', '不低于97%', '标注测试集和线上抽样'),
        ('二级意图准确率', '不低于88%', '不低于92%', '分意图混淆矩阵'),
        ('自动解决率', '不低于45%', '不低于60%', '无人工介入且用户未重复咨询'),
        ('高风险错误执行', '0', '0', 'Action审计记录'),
        ('Action成功率', '不低于95%', '不低于99%', '排除业务规则拒绝'),
        ('回答证据覆盖率', '不低于90%', '不低于95%', '需证据场景的引用记录'),
        ('P95响应时间', '问答小于8秒', '问答小于5秒', '端到端监控'),
        ('新增意图交付周期', '小于10个工作日', '小于5个工作日', '需求进入到灰度发布')
    ], widths=[1.5, 1.5, 1.55, 2.15], font_size=8.8)

    page_break(doc)
    add_heading(doc, '3 产品范围与用户角色', 1)
    add_heading(doc, '3.1 范围内', 2)
    add_bullets(doc, [
        '客户聊天端及结构化交互组件。', '意图识别、实体抽取、对象解析和能力路由。',
        '商品、质保、订单、门店、会员、会话控制和维修保养场景。', 'Ontology对象、关系、规则、Function、Action和运行实例。',
        '知识域建设、Ontology过滤检索、证据和版本管理。', '人工坐席与审核工作台。',
        '配置发布、回归测试、运营监控和全链路审计。'
    ])
    add_heading(doc, '3.2 范围外', 2)
    add_bullets(doc, [
        '替换现有订单、库存、门店、会员、预约、质保和财务系统。',
        '让大模型直接决定赔付金额、退款或其他高风险不可逆操作。',
        '一期建设覆盖企业全部业务的通用Ontology平台。',
        '一期训练通用大模型或建设自有基础模型。',
        '未获得业务授权时自动调用外部系统执行写操作。'
    ])
    add_heading(doc, '3.3 用户角色', 2)
    add_table(doc, ['角色', '核心需求', '主要权限'], [
        ('匿名客户', '公开商品和门店咨询', '公开知识与有限查询'),
        ('登录客户', '查询本人车辆、订单、会员、预约和售后', '本人对象读取和受控Action'),
        ('客服坐席', '查看上下文、接管会话、处理普通工单', '授权范围内读取和操作'),
        ('业务审核人', '审批理赔、投诉、异常报价', '高风险Action审批'),
        ('知识运营', '维护文档、标签、版本和有效期', 'KnowledgeDocument管理'),
        ('业务规则管理员', '维护业务和风险规则', '规则草稿与送审'),
        ('平台管理员', '管理对象、能力、连接器和发布', '平台配置及发布'),
        ('审计人员', '查询运行证据和操作记录', '只读审计视图')
    ], widths=[1.25, 3.0, 2.45])

    page_break(doc)
    add_heading(doc, '4 业务场景与需求优先级', 1)
    intent_rows = [
        ('商品咨询', '原装轮胎型号', 'GetOEMTireSpec', 'L1', 'P0'),
        ('商品咨询', '换胎咨询与选型', 'RecommendReplacementTire', 'L1', 'P0'),
        ('商品咨询', '价格优惠活动', 'GetPriceAndPromotion', 'L1/L2', 'P1'),
        ('商品咨询', '门店库存查询', 'CheckNearbyInventory', 'L2', 'P0'),
        ('原厂保障', '质保内容咨询', 'ExplainWarranty', 'L1', 'P1'),
        ('原厂保障', '理赔或更换申请', 'SubmitWarrantyClaim', 'L4', 'P0'),
        ('原厂保障', '理赔进度查询', 'GetClaimStatus', 'L2', 'P1'),
        ('原厂保障', '售后进度查询', 'GetAfterSalesStatus', 'L2', 'P1'),
        ('订单服务', '订单查询', 'GetCustomerOrder', 'L2', 'P1'),
        ('订单服务', '预约门店服务', 'BookStoreService', 'L3', 'P1'),
        ('订单服务', '修改或取消预约', 'ManageAppointment', 'L3', 'P0'),
        ('门店服务', '门店咨询', 'FindStore', 'L1', 'P1'),
        ('门店服务', '门店服务投诉', 'CreateStoreComplaint', 'L4', 'P1'),
        ('账户会员', '会员权益与积分', 'GetMemberBenefits', 'L2', 'P1'),
        ('账户会员', '账户问题反馈', 'CreateAccountIssue', 'L3', 'P1'),
        ('会话控制', '转人工', 'EscalateToHuman', 'L2', 'P0'),
        ('会话控制', '闲聊或无效输入', 'HandleSmallTalk', 'L1', 'P1'),
        ('会话控制', '情绪吐槽', 'DetectEmotionAndCare', 'L2/L3', 'P1'),
        ('维修保养', '维修报价', 'GenerateRepairQuote', 'L3/L4', 'P1'),
        ('维修保养', '保养报价', 'GenerateMaintenanceQuote', 'L3', 'P1')
    ]
    add_table(doc, ['一级意图', '二级意图', 'Capability', '基础风险', '优先级'], intent_rows,
              widths=[1.2, 1.55, 2.4, 0.85, 0.7], font_size=8.4)
    add_para(doc, 'P0用于验证对象解析、规则、RAG、实时查询、写Action、高风险人工审批和转人工六类核心能力。P1在P0稳定后复用同一套运行时扩展。')

    page_break(doc)
    add_heading(doc, '5 产品总体架构', 1)
    add_figure(doc, ASSET_DIR / 'architecture.png', '图1  汽车后市场智能客服总体架构', width=7.0)
    add_heading(doc, '5.1 架构说明', 2)
    add_numbered(doc, [
        '渠道层只处理展示和交互，不保存唯一业务规则。所有渠道使用统一对话API。',
        '对话理解层输出意图、置信度、实体和缺失参数，并把当前用户身份传给运行时。',
        'AI运行编排层创建ServiceRequest，查询Capability定义，再由通用LangGraph执行。',
        '可执行本体层统一对象、规则、Function、Action、权限和审计。',
        '数据与知识层通过连接器访问源系统，按场景选择虚拟查询、缓存或索引。'
    ])
    add_heading(doc, '5.2 建议技术边界', 2)
    add_table(doc, ['模块', '建议实现形态', '边界'], [
        ('对话入口', 'Web组件或原生SDK加BFF', '不直接访问业务系统'),
        ('意图与实体识别', '小模型加大模型兜底', '输出结构化结果'),
        ('运行编排', 'LangGraph服务', '读取配置，不保存唯一业务口径'),
        ('Ontology Runtime', '对象查询、关系解析、规则和Action服务', '为上层提供稳定语义API'),
        ('知识检索', '向量、关键词、元数据过滤和重排', '只处理非结构化知识'),
        ('Action Gateway', '统一写操作代理', '权限、幂等、审计、补偿'),
        ('审计与观测', '事件日志、指标、链路追踪', '保留运行版本和证据')
    ], widths=[1.45, 2.45, 2.7])

    page_break(doc)
    add_heading(doc, '6 Ontology本体设计', 1)
    add_figure(doc, ASSET_DIR / 'ontology_map.png', '图2  核心业务对象与关系', width=7.0)
    add_heading(doc, '6.1 对象分层', 2)
    add_table(doc, ['领域', '核心对象', '主要事实来源'], [
        ('客户与车辆', 'Customer、MemberAccount、Vehicle、VehicleModel', 'CRM、会员、车辆主数据'),
        ('商品与适配', 'TireProduct、TireSKU、TireCompatibility、Price、Promotion', 'PIM、商品、价格活动系统'),
        ('门店与库存', 'Store、StoreInventory、ServiceSlot', '门店系统、库存、预约排班'),
        ('订单与服务', 'Order、ServiceAppointment、RepairPlan、MaintenancePlan、Quote', '订单、预约、维修保养系统'),
        ('保障与售后', 'WarrantyPolicy、WarrantyClaim、AfterSalesCase、Complaint', '质保、理赔、工单系统'),
        ('AI运行', 'ConversationTurn、IntentPrediction、ServiceRequest、RiskAssessment、DecisionRecord、ActionExecution', 'AI运行时和审计事件')
    ], widths=[1.2, 3.25, 2.15], font_size=8.8)
    add_heading(doc, '6.2 对象实例化策略', 2)
    add_table(doc, ['数据类型', '建议方式', '原因'], [
        ('客户、车辆、订单、预约当前状态', 'API或虚拟查询，必要时短时缓存', '保持源系统为事实来源'),
        ('车型与轮胎适配关系', '索引或物化', '高频关联查询和规则计算'),
        ('实时库存和价格', '源系统实时查询', '避免陈旧结果'),
        ('产品和政策文档', '向量索引并关联对象ID', '支持语义检索和版本过滤'),
        ('DecisionRecord和ActionExecution', '本体运行时持久化', '支持审计、复盘和指标')
    ], widths=[2.0, 2.1, 2.5])

    page_break(doc)
    add_heading(doc, '7 运行流程与决策闭环', 1)
    add_figure(doc, ASSET_DIR / 'runtime_flow.png', '图3  单轮对话从意图识别到审计的运行流程', width=6.7)
    add_heading(doc, '7.1 公共LangGraph', 2)
    add_para(doc, '公共图包含意图识别、实体抽取、对象解析、能力路由、参数检查、对象加载、策略评估、执行、确认、回答和审计节点。特殊子图只用于理赔材料收集、复杂报价、人工审批等长流程。')
    add_heading(doc, '7.2 风险决策', 2)
    add_table(doc, ['风险等级', '典型场景', '处理方式'], [
        ('L1', '公开商品知识、门店信息、闲聊', '可以直接回答'),
        ('L2', '本人订单、会员、理赔进度查询', '完成身份认证后查询'),
        ('L3', '预约、取消、账户问题提交、一般报价', '明确确认后执行Action'),
        ('L4', '理赔、更换、重大投诉、异常高金额报价', '建立案件并人工审核')
    ], widths=[0.8, 3.0, 2.8])
    add_para(doc, '最终风险由意图基础风险、数据敏感度、Action风险、对象当前状态和模型置信度共同决定。业务拒绝不会自动重试。只有网络超时等技术失败可以通过幂等机制有限重试。')

    page_break(doc)
    add_heading(doc, '8 各端产品需求与原型', 1)
    add_heading(doc, '8.1 客户聊天端', 2)
    add_figure(doc, ASSET_DIR / 'chat_wireframe.png', '图4  客户侧Action确认原型', width=6.6)
    add_table(doc, ['功能', '需求'], [
        ('会话', '支持多轮上下文、历史消息、重新进入和会话超时'),
        ('结构化组件', '商品、门店、订单、预约、报价、确认、进度和上传组件'),
        ('身份', '匿名与登录态区分，敏感查询前完成认证'),
        ('Action确认', '显示目标对象、影响、有效期和取消入口'),
        ('转人工', '显示排队状态，并把上下文和证据交给坐席'),
        ('证据', '适用场景显示政策来源、商品依据和数据更新时间')
    ], widths=[1.45, 5.15])

    page_break(doc)
    add_heading(doc, '8.2 人工坐席与审核工作台', 2)
    add_figure(doc, ASSET_DIR / 'agent_wireframe.png', '图5  坐席和高风险审核工作台原型', width=7.0)
    add_table(doc, ['区域', '内容'], [
        ('对象摘要', '客户、车辆、订单、商品、预约、会员和案件'),
        ('会话摘要', '用户诉求、已追问内容、情绪和未解决事项'),
        ('AI建议', '候选结论、命中规则、风险等级和置信度'),
        ('证据', '结构化数据、RAG引用、图片和材料完整性'),
        ('操作', '补件、批准、驳回、修改建议、转交专家'),
        ('审计', '记录人工修改内容、原因、操作者和Action结果')
    ], widths=[1.45, 5.15])

    page_break(doc)
    add_heading(doc, '8.3 Ontology配置管理端', 2)
    add_figure(doc, ASSET_DIR / 'admin_wireframe.png', '图6  意图能力映射与发布原型', width=7.0)
    add_table(doc, ['模块', '一期要求'], [
        ('对象管理', '查看Object Type、属性、关系、主键和数据来源'),
        ('能力管理', '维护Intent到Capability的映射和输入输出契约'),
        ('规则管理', '草稿、版本、测试、审批、生效和回滚'),
        ('Action管理', '权限、前置条件、确认、幂等、补偿和接口绑定'),
        ('知识管理', '知识域、对象标签、地区、版本、有效期和权限'),
        ('发布管理', '回归结果、影子运行、灰度比例和生产版本')
    ], widths=[1.45, 5.15])
    add_para(doc, '一期可以使用Git中的YAML和JSON配置配合简单只读页面。业务规则需要频繁调整后，再建设完整可视化编辑器，避免首期把预算消耗在低频后台功能上。')

    page_break(doc)
    add_heading(doc, '8.4 运营与审计端', 2)
    add_table(doc, ['视图', '核心指标或信息'], [
        ('意图效果', '准确率、混淆矩阵、低置信度比例、未识别Query'),
        ('业务效果', '自动解决率、转人工率、一次解决率、用户重复提问率'),
        ('运行质量', '响应时间、节点失败率、RAG无证据率、Tool错误率'),
        ('Action', '提案数、确认率、成功率、失败原因、补偿次数'),
        ('人工审核', '队列时长、通过率、修改原因、不同审核人差异'),
        ('审计查询', '按客户、对象、规则版本、Action和时间检索运行记录')
    ], widths=[1.45, 5.15])

    add_heading(doc, '8.5 单一聊天窗口的边界', 2)
    add_para(doc, '客户侧可以只嵌入一个聊天入口，但完整生产系统不能只有聊天窗口。查询和低风险问答可以在聊天端完成；理赔、投诉和异常报价需要坐席或审核工作台；规则、对象、Action和知识版本需要配置发布能力；运营团队需要质量与审计视图。')

    page_break(doc)
    add_heading(doc, '9 功能模块需求', 1)
    modules = [
        ('M01', '会话与身份', '会话创建、身份传递、匿名和登录状态、上下文保存', 'P0'),
        ('M02', '意图识别', '一级二级意图、Top K、置信度、版本、兜底', 'P0'),
        ('M03', '实体与参数抽取', '车型、SKU、订单号、日期、门店和操作类型', 'P0'),
        ('M04', '对象解析', '实体消歧、主键映射、对象加载和关系遍历', 'P0'),
        ('M05', 'Capability Router', '意图到能力映射、适用条件、缺参策略', 'P0'),
        ('M06', '规则与风险', '业务规则、最终风险、权限和前置条件', 'P0'),
        ('M07', 'LangGraph Runtime', '公共图、子图、暂停、恢复、超时和异常', 'P0'),
        ('M08', 'Function Gateway', '只读查询、缓存、超时、降级和数据血缘', 'P0'),
        ('M09', 'Action Gateway', '确认、审批、幂等、写回、补偿和审计', 'P0'),
        ('M10', 'Ontology RAG', '知识域、对象过滤、混合检索、重排和引用', 'P0'),
        ('M11', '回答生成', '结构化结果、Prompt策略、内容安全和渠道适配', 'P0'),
        ('M12', '人工工作台', '队列、对象摘要、证据、审批和接管', 'P0'),
        ('M13', '配置与发布', '版本、测试、审批、灰度、回滚', 'P1'),
        ('M14', '运营与审计', '指标、抽样、回放、查询和导出', 'P0')
    ]
    add_table(doc, ['编号', '模块', '一期功能', '优先级'], modules, widths=[0.7, 1.55, 3.95, 0.65], font_size=8.6)
    add_heading(doc, '9.1 统一Capability契约', 2)
    add_para(doc, '每个Capability必须声明支持的意图、所需对象、输入参数、可调用Function、允许的Action、知识策略、风险策略、输出结构和兜底方式。运行时只依赖契约，不依赖意图名称拼接方法名。')
    add_heading(doc, '9.2 统一运行结果', 2)
    add_para(doc, '每个节点返回status、data、evidence、errorCode、latency和sourceVersion。大模型生成回答时只读取允许暴露给当前用户的数据和证据。')

    page_break(doc)
    add_heading(doc, '10 数据 RAG 与系统集成', 1)
    add_heading(doc, '10.1 系统接口清单', 2)
    add_table(doc, ['系统', '读取能力', '写入能力', '一期优先级'], [
        ('客户与会员', '身份、会员等级、积分、权益', '创建账户问题', 'P1'),
        ('车辆主数据', 'VIN、车型、年款、原厂参数', '无', 'P0'),
        ('商品与适配', 'SKU、规格、适配关系、上下架', '无', 'P0'),
        ('价格活动', '价格、优惠、生效期', '报价记录可选', 'P1'),
        ('门店库存', '门店、服务能力、实时库存', '预留库存可选', 'P0'),
        ('订单预约', '订单、预约、可约时段', '新增、修改、取消预约', 'P0'),
        ('质保理赔', '政策、案件、进度', '创建理赔、补件', 'P0'),
        ('客服工单', '队列、历史工单', '建单、转派、关闭', 'P0')
    ], widths=[1.35, 2.55, 2.15, 0.75], font_size=8.8)
    add_heading(doc, '10.2 知识域', 2)
    add_table(doc, ['知识域', '内容', '本体过滤字段'], [
        ('商品知识', '产品手册、规格说明、使用建议', 'ProductID、SKU、车型、地区、版本'),
        ('质保政策', '保障范围、排除条款、材料要求', 'PolicyID、SKU、购买时间、生效期'),
        ('维修保养', '周期、项目、技术说明和安全提示', 'VehicleModel、里程、年款'),
        ('门店服务', '服务项目、营业信息和说明', 'StoreID、地区、服务类型'),
        ('会员政策', '等级、积分和权益规则', '会员等级、地区、生效期')
    ], widths=[1.35, 2.55, 2.8])
    add_heading(doc, '10.3 数据质量要求', 2)
    add_bullets(doc, [
        '客户、车辆、订单、SKU、门店和案件必须有稳定主键。',
        '所有时间相关数据明确时区、生效时间和更新时间。',
        '库存、价格和预约数据必须返回数据时间戳。',
        '知识文档必须设置版本、生效期、责任人和权限。',
        '对象映射失败进入异常队列，不允许大模型猜测对象。'
    ])

    page_break(doc)
    add_heading(doc, '11 安全权限风险与审计', 1)
    add_heading(doc, '11.1 权限模型', 2)
    add_table(doc, ['控制层级', '要求'], [
        ('渠道和身份', '传递可信actorId、角色、组织和认证强度'),
        ('对象权限', '用户只能读取本人对象；坐席按组织和职责授权'),
        ('属性权限', '手机号、地址、VIN等敏感字段按角色脱敏'),
        ('Function权限', '查询能力按对象和数据来源检查'),
        ('Action权限', '同时检查操作者、目标对象、当前状态和金额范围'),
        ('知识权限', '内部文档不得进入客户回答上下文'),
        ('审计权限', '审计记录只读，限制导出并记录访问')
    ], widths=[1.45, 5.15])
    add_heading(doc, '11.2 Action安全要求', 2)
    add_bullets(doc, [
        '每个写Action定义输入Schema、权限、前置条件、确认文案、幂等键和目标系统。',
        'Action执行前重新读取目标对象版本，避免基于陈旧状态操作。',
        '已产生外部影响的操作使用补偿Action，不删除历史。',
        '技术失败可以有限重试；业务拒绝进入明确分支，不自动重复计算。',
        'L4场景必须形成证据包并由授权人员审批。'
    ])
    add_heading(doc, '11.3 审计记录', 2)
    add_table(doc, ['记录', '必须保存的内容'], [
        ('IntentPrediction', '原始Query、意图、Top K、置信度、小模型版本'),
        ('DecisionRecord', '对象引用、数据时间、规则版本、模型版本、证据、结论'),
        ('ActionExecution', '操作者、权限结果、前置校验、输入、目标、状态、错误'),
        ('HumanReview', '审核人、修改内容、修改原因、审批时间'),
        ('ResponseRecord', '最终文本、结构化组件、引用、内容安全结果')
    ], widths=[1.55, 5.05])

    page_break(doc)
    add_heading(doc, '12 非功能需求', 1)
    add_table(doc, ['类别', '一期要求'], [
        ('性能', '普通知识问答P95小于8秒；结构化查询P95小于5秒；Action不含人工等待P95小于10秒'),
        ('可用性', '核心运行时月可用性不低于99.5%；业务系统不可用时给出明确降级'),
        ('扩展性', '新增渠道无需复制业务规则；新增相似意图可以复用已有Capability'),
        ('可观测性', '每轮请求具备traceId；记录节点耗时、模型调用、Tool调用和错误码'),
        ('可恢复性', '长流程支持暂停和恢复；Action支持幂等；发布支持版本回滚'),
        ('安全', '传输和存储加密；敏感字段脱敏；密钥集中管理；最小权限'),
        ('合规', '保留期限可配置；支持用户数据删除或匿名化流程；高风险操作可追责'),
        ('模型治理', '模型、Prompt、知识、规则和Ontology版本可定位；上线前完成回归评估')
    ], widths=[1.25, 5.35], font_size=9)

    add_heading(doc, '12.1 降级策略', 2)
    add_table(doc, ['故障', '降级方式'], [
        ('意图模型低置信度', '大模型复核或追问；仍不确定则转人工'),
        ('RAG无可靠证据', '返回可确认的结构化事实或转人工，不编造政策'),
        ('业务接口超时', '只读接口有限重试；写接口通过幂等查询状态'),
        ('大模型不可用', '使用模板回答、展示查询结果或转人工'),
        ('Ontology对象解析失败', '请求用户选择对象或进入人工异常队列')
    ], widths=[2.0, 4.6])

    page_break(doc)
    add_heading(doc, '13 迭代与发布机制', 1)
    add_heading(doc, '13.1 快速开发方式', 2)
    add_numbered(doc, [
        '新增表达只更新训练样本和评估集，不修改Ontology。',
        '新增相似意图时绑定已有Capability，优先复用对象、Function和Action。',
        '业务政策变化通过规则新版本发布，不修改聊天端和主流程。',
        '接入新系统时替换对象数据连接器，上层Capability接口保持稳定。',
        '新增写操作时创建Action定义，并补齐权限、前置条件、确认、幂等和补偿。',
        '每次发布先跑离线回归，再做影子运行和小流量灰度。'
    ])
    add_heading(doc, '13.2 配置发布流程', 2)
    add_para(doc, '业务或产品人员提交意图、规则、知识或能力变更；平台自动校验Schema和依赖；测试环境运行回归样本；业务负责人审核规则；安全负责人审核L3和L4 Action；影子环境比较新旧版本；通过后按5%、20%、50%和100%逐级放量。')
    add_heading(doc, '13.3 版本对象', 2)
    add_table(doc, ['版本类型', '要求'], [
        ('Ontology Schema', '对象和属性变更保持向后兼容，破坏性变更需要迁移方案'),
        ('Intent Model', '保存训练集版本、指标和混淆矩阵'),
        ('Capability', '输入输出Schema版本化'),
        ('Rule', '责任人、生效期、审批人和回滚版本'),
        ('Prompt与Model', '保存精确模型、参数、模板和评估结果'),
        ('Knowledge', '文档版本、生效期、对象标签和索引批次')
    ], widths=[1.65, 4.95])

    page_break(doc)
    add_heading(doc, '14 项目计划与里程碑', 1)
    add_para(doc, '计划总周期为28周。接口准备、Ontology建模、平台开发和业务场景可以并行，但P0场景上线前必须完成身份、权限、审计和Action安全检查。')
    schedule_rows = [
        ('阶段0', '立项与业务发现', '第1至2周', '范围、KPI、20个意图确认、5个P0场景、接口清单'),
        ('阶段1', '本体与方案设计', '第3至5周', '对象模型、关系、Capability、规则和Action设计'),
        ('阶段2', '平台基础能力', '第4至9周', '统一State、公共LangGraph、Ontology Runtime、审计骨架'),
        ('阶段3', '数据与RAG接入', '第5至11周', '车辆、商品、门店库存、预约、质保和知识域'),
        ('阶段4', 'P0五场景开发', '第8至15周', '车型、选型、库存、取消预约、理赔和转人工能力'),
        ('阶段5', 'P1十五场景扩展', '第14至21周', '全部20个意图、坐席工作台和运营视图'),
        ('阶段6', '联调与验收', '第20至24周', '安全、性能、回归、UAT和应急演练'),
        ('阶段7', '生产试点', '第25至28周', '灰度、运营复盘、指标验收和正式切换')
    ]
    add_table(doc, ['阶段', '工作', '周期', '主要产出'], schedule_rows, widths=[0.75, 1.6, 1.15, 3.1], font_size=8.7)
    add_heading(doc, '14.1 关键里程碑', 2)
    add_table(doc, ['里程碑', '时间', '通过条件'], [
        ('M1 需求基线', '第2周', '场景、KPI、风险等级和接口责任人确认'),
        ('M2 设计评审', '第5周', 'Ontology、架构、Action边界和原型通过'),
        ('M3 平台骨架', '第9周', '公共图、对象查询、审计链路跑通'),
        ('M4 P0完成', '第15周', '5个场景在测试环境端到端完成'),
        ('M5 全场景完成', '第21周', '20个意图进入回归测试'),
        ('M6 上线许可', '第24周', '安全、性能和UAT通过'),
        ('M7 试点验收', '第28周', '达到约定KPI并完成问题关闭')
    ], widths=[1.5, 1.15, 3.95])

    page_break(doc)
    add_heading(doc, '15 团队与资源投入', 1)
    add_heading(doc, '15.1 供应侧团队', 2)
    resource_rows = [
        ('项目经理', '1', '全程', '计划、风险、跨团队协调、验收'),
        ('产品经理', '1至2', '全程', 'PRD、原型、场景和运营指标'),
        ('业务分析与FDE', '2', '前16周为主', '驻场调研、规则、验收样本和业务闭环'),
        ('Ontology架构师', '1', '全程', '对象、关系、能力和Action标准'),
        ('解决方案架构师', '1', '全程', '总体架构、接口、安全和非功能'),
        ('AI算法工程师', '2', '第3至24周', '意图、实体、RAG、评估和模型治理'),
        ('后端工程师', '3', '第4至24周', 'Runtime、连接器、Function、Action和审计'),
        ('前端工程师', '2', '第7至24周', '聊天组件、坐席和配置运营端'),
        ('数据工程师', '1至2', '第4至18周', '对象映射、数据质量和索引'),
        ('测试工程师', '2', '第8至28周', '功能、回归、接口、性能和安全测试'),
        ('DevOps与安全', '1', '第4至28周', '环境、发布、监控、安全和应急'),
        ('UI设计师', '0.5', '第2至10周', '交互、组件和视觉规范')
    ]
    add_table(doc, ['角色', '峰值人数', '主要阶段', '职责'], resource_rows, widths=[1.35, 0.75, 1.35, 3.15], font_size=8.3)
    add_para(doc, '供应侧峰值约15至17人，平均约11至13人，预计总投入72至86人月。实际人数取决于客户接口成熟度、前端复用程度和私有化部署要求。')
    add_heading(doc, '15.2 客户侧投入', 2)
    add_table(doc, ['角色', '建议投入', '职责'], [
        ('业务负责人', '0.5人全程', '范围、规则和KPI拍板'),
        ('产品与客服运营', '1至2人全程', '场景、语料、原型和运营'),
        ('商品与技术专家', '每周1至2人日', '轮胎、维修保养规则确认'),
        ('质保与售后专家', '每周1至2人日', '政策、理赔和人工审核'),
        ('IT与数据负责人', '1至2人全程', '接口、数据、环境和上线'),
        ('安全与合规', '关键评审参与', '权限、隐私、安全测试和上线许可')
    ], widths=[1.6, 1.65, 3.35])

    page_break(doc)
    add_heading(doc, '16 费用估算', 1)
    add_para(doc, '以下为2026年新项目规划级估算，适用于立项预算，不作为最终商务报价。估算基于28周、72至86供应侧人月、复用现有云或数据中心基础设施，并假设订单、库存、预约、会员和质保系统提供可用API。')
    cost_rows = [
        ('产品、业务与架构', '18至22人月', '95至145万元', '产品、FDE、Ontology与方案架构'),
        ('AI、数据与RAG', '16至20人月', '85至135万元', '意图、实体、检索、评估和数据映射'),
        ('后端与集成', '22至26人月', '115至175万元', 'Runtime、连接器、Function、Action和审计'),
        ('前端与交互', '9至12人月', '45至75万元', '聊天、坐席、配置与运营端'),
        ('测试、DevOps和安全', '12至16人月', '60至105万元', '测试、环境、监控、安全和上线'),
        ('模型、向量库和运行基础设施', '项目期', '25至65万元', '开发测试和试点流量'),
        ('安全测评与专项测试', '项目期', '15至35万元', '渗透、隐私和性能专项'),
        ('预备费', '约10%至15%', '35至60万元', '接口变化、数据清洗和范围波动')
    ]
    add_table(doc, ['费用项', '投入依据', '估算区间', '说明'], cost_rows, widths=[1.6, 1.35, 1.25, 2.5], font_size=8.4)
    add_heading(doc, '16.1 总预算', 2)
    add_table(doc, ['口径', '预算'], [
        ('推荐项目预算', '人民币440万元至690万元'),
        ('建议立项控制数', '人民币550万元'),
        ('可选私有化硬件与商业软件', '另增加人民币80万元至300万元'),
        ('客户侧内部人员成本', '未计入，预计15至25人月'),
        ('上线后年度运维', '通常为建设费用的15%至25%，另加模型实际调用成本')
    ], widths=[2.7, 3.9], font_size=9.5)
    add_heading(doc, '16.2 费用敏感因素', 2)
    add_bullets(doc, [
        '如果源系统没有稳定API，需要新增适配和数据治理，预算可能增加15%至30%。',
        '如果一期只上线5个P0场景，预算可控制在人民币220万元至360万元，周期约16至18周。',
        '如果仅做知识问答且不建设Action、坐席和审计，成本可进一步下降，但不属于本PRD选择的方案B范围。',
        '如果要求全栈私有化、高可用双中心或国产化软硬件适配，需要单独估算。'
    ])

    page_break(doc)
    add_heading(doc, '17 验收标准', 1)
    add_heading(doc, '17.1 产品验收', 2)
    add_bullets(doc, [
        '20个二级意图全部有明确Capability、风险等级和处理链路。',
        '客户聊天端能够完成问答、查询、确认、上传、进度和转人工。',
        '人工工作台能够查看对象、证据、规则、建议并完成审批或接管。',
        '配置变更经过测试、审批、灰度和回滚流程。'
    ])
    add_heading(doc, '17.2 技术验收', 2)
    add_bullets(doc, [
        '核心对象主键和关系映射完成，并通过数据质量检查。',
        '读Function与写Action边界清晰，写Action全部具备幂等、前置条件和审计。',
        '满足第2.3节KPI和第12节非功能需求。',
        '任意生产回答可以定位意图模型、规则、对象数据、知识和模型版本。',
        '完成异常、降级、补偿、安全和灾备演练。'
    ])
    add_heading(doc, '17.3 业务验收样本', 2)
    add_para(doc, '每个二级意图至少准备正常、缺参数、对象歧义、无权限、低置信度、源系统超时和人工接管样本。每个L3和L4场景另需覆盖重复提交、对象版本冲突、审批驳回和Action部分失败。')

    page_break(doc)
    add_heading(doc, '18 项目风险与待决策事项', 1)
    add_heading(doc, '18.1 主要风险', 2)
    add_table(doc, ['风险', '影响', '应对'], [
        ('源系统接口不稳定', '查询和Action无法达到上线指标', '第2周锁定接口责任人，建立Mock和降级策略'),
        ('对象主键不统一', '客户、车辆、订单无法可靠关联', '优先完成主数据映射和消歧规则'),
        ('业务规则未形成书面口径', '模型和人工处理结果不一致', '规则指定责任人、版本和生效期'),
        ('过度依赖大模型判断', '关键操作不可预测', '关键条件落到确定性规则和Action校验'),
        ('一期平台范围过大', '延期并降低业务验收质量', '先完成P0五场景和最小配置能力'),
        ('客户侧投入不足', '语料、规则、接口和UAT阻塞', '立项时确认客户侧角色和每周投入')
    ], widths=[1.65, 2.2, 2.75], font_size=8.8)
    add_heading(doc, '18.2 立项前必须确认', 2)
    add_numbered(doc, [
        '客户聊天端使用现有App、小程序还是新建Web组件。',
        '20个意图的准确名称、风险基线和业务责任人。',
        'P0五场景的成功指标及试点用户范围。',
        '订单、预约、库存、车辆、质保和客服系统接口成熟度。',
        '哪些Action允许用户确认后自动执行，哪些必须人工审批。',
        '部署在公有云、客户私有云还是本地数据中心。',
        '日志和会话数据保留期限，以及敏感信息脱敏规则。',
        '预算采用P0试点分段立项，还是一次批准全量28周计划。'
    ])

    page_break(doc)
    add_heading(doc, '附录A 核心配置示例', 1)
    add_heading(doc, 'A.1 意图与能力映射', 2)
    p = doc.add_paragraph()
    code = '''intent_id: ORDER_CANCEL
capability_id: ManageAppointment
required_objects:
  - Customer
  - ServiceAppointment
required_slots:
  - operation
functions:
  - GetAppointment
  - CheckAppointmentEligibility
actions:
  - CancelAppointment
risk_policy: APPOINTMENT_CHANGE_POLICY
response_policy: ACTION_CONFIRMATION_RESPONSE'''
    r = p.add_run(code)
    set_run_font(r, name='Courier New', east='Arial Unicode MS', size=8.5)
    shade = OxmlElement('w:shd')
    shade.set(qn('w:fill'), LIGHT_GRAY)
    p._p.get_or_add_pPr().append(shade)
    set_paragraph_spacing(p, after=10, line=1.05)
    add_heading(doc, 'A.2 Action配置', 2)
    p = doc.add_paragraph()
    code = '''action_id: CancelAppointment
required_permission: appointment.cancel.self
preconditions:
  - actor.customer_id == appointment.customer_id
  - appointment.status == CONFIRMED
confirmation_required: true
executor: appointment-service.cancel
idempotency_key:
  - customer_id
  - appointment_id
  - request_id
on_failure:
  timeout: query_status_then_retry
  version_conflict: reload_and_reconfirm
  policy_rejected: escalate_to_human'''
    r = p.add_run(code)
    set_run_font(r, name='Courier New', east='Arial Unicode MS', size=8.5)
    shade = OxmlElement('w:shd')
    shade.set(qn('w:fill'), LIGHT_GRAY)
    p._p.get_or_add_pPr().append(shade)
    set_paragraph_spacing(p, after=10, line=1.05)

    add_heading(doc, 'A.3 统一运行状态', 2)
    add_table(doc, ['字段组', '主要字段'], [
        ('身份与会话', 'sessionId、turnId、actorId、channel、authLevel'),
        ('语言理解', 'query、intentPrediction、entities、missingSlots'),
        ('业务上下文', 'objectRefs、capabilityId、objectVersions'),
        ('策略', 'policyDecision、riskAssessment、requiredApproval'),
        ('执行', 'structuredData、evidence、proposedActions、actionResults'),
        ('结果', 'response、decisionRecordId、traceId')
    ], widths=[1.65, 4.95])

    page_break(doc)
    add_heading(doc, '附录B 术语表', 1)
    add_table(doc, ['术语', '定义'], [
        ('Ontology', '企业业务对象、关系、逻辑、Action和安全规则组成的可执行模型。'),
        ('Object Type', '业务对象的类型定义，例如Customer、Vehicle或Order。'),
        ('Object Instance', '具体业务实体，例如某位客户或某一笔订单。'),
        ('Capability', '面向业务目标的稳定能力契约，由Function、规则、RAG和Action组合实现。'),
        ('Function', '只读取或计算，不改变外部业务状态的能力。'),
        ('Action', '会改变业务对象或外部系统状态的受控操作。'),
        ('DecisionRecord', '记录某次判断的数据、规则、证据、版本和结论。'),
        ('ActionExecution', '记录Action的操作者、校验、输入、输出和执行状态。'),
        ('Ontology grounded RAG', '先通过业务对象限定知识范围，再进行语义和关键词检索。'),
        ('FDE', '深入客户现场，把业务问题转化为可运行产品能力的工程角色。')
    ], widths=[2.0, 4.6])

    doc.core_properties.title = '汽车后市场智能客服 Ontology 产品需求与架构设计'
    doc.core_properties.subject = '产品需求 方案架构 项目计划 资源和费用'
    doc.core_properties.author = '项目组'
    doc.core_properties.keywords = 'Ontology 智能客服 LangGraph 汽车后市场 PRD'
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == '__main__':
    build_doc()
