"""Render a normalized customer case. All asset paths in the manifest are local."""
import argparse
import json
import os
from pathlib import Path
from io import BytesIO
from tempfile import TemporaryDirectory
from math import ceil
from html import escape
from urllib.parse import urlsplit

from lxml import html
from PIL import Image as PILImage, ImageColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, KeepTogether,
                               HRFlowable, Table, TableStyle)
from pypdf import PdfReader, PdfWriter

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('manifest', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
case = json.loads(args.manifest.read_text(encoding='utf-8'))
base = args.manifest.resolve().parent
assets = Path(__file__).resolve().parents[1] / 'assets'
sections = case['sections']
assert sections and all(s['heading'].strip() and s['blocks'] for s in sections)
client = case['client'].strip()
industry = case['industry'].strip().removesuffix('行业')
assert client and industry and 1 <= len(case['title']) <= 2
logo = base / case['logo']
W, H = A4
font = 'CaseText'
symbol = 'CaseSymbol'
fonts = assets / 'fonts'
bold = 'CaseBold'
for face, filename in [(font,'NotoSansSC-Regular.ttf'),(bold,'NotoSansSC-Bold.ttf'),(symbol,'DejaVuSans.ttf')]:
    pdfmetrics.registerFont(TTFont(face, str(fonts / filename)))
pdfmetrics.registerFontFamily(font,normal=font,bold=bold)
from reportlab import rl_config
rl_config.canvas_basefontname = font
defaults = dict(primary='#0F88F1', deep='#075EAB', yellow='#F4CA33', green='#AECB45', pale='#ECE7FA', light='#66B1F2', lavender='#BAB8D9')
palette = {**defaults, **case.get('palette', {})}
colors = {key: HexColor(value) for key,value in palette.items()}
toc = [s['heading'] for s in sections] + ['附录｜营销枢纽与客户成功服务模式']
toc_pages = ceil(len(toc)/10)
offset = 1 + toc_pages
marks = {}

def style(name, size, leading, role=None, **kw):
    return ParagraphStyle(name,fontName=bold if name in ('heading','sub') else font,fontSize=size,leading=leading,
                          textColor=colors[role] if role else HexColor('#263849'),wordWrap='CJK',**kw)
body = style('body',10.2,17.2,spaceAfter=5)
lead = style('lead',12,21,'deep',spaceAfter=9)
heading = style('heading',19,29,'deep',spaceBefore=17,spaceAfter=11,keepWithNext=True)
sub = style('sub',12.2,20.5,'deep',spaceBefore=12,spaceAfter=8,keepWithNext=True)
caption = style('caption',8.5,13,alignment=TA_CENTER,spaceBefore=5,spaceAfter=12)

def rich(node):
    text = escape(node.text or '')
    for child in node:
        value = rich(child)
        if child.tag in ('strong','b'):
            value = f'<font color="{palette["deep"]}">{value}</font>'
        elif child.tag == 'a' and urlsplit(child.get('href','')).scheme in ('http','https','mailto'):
            value = f'<link color="{palette["deep"]}" href="{escape(child.get("href"),quote=True)}">{value}</link>'
        elif child.tag == 'br':
            value = '<br/>'
        text += value + escape(child.tail or '')
    return text

def content(block):
    if 'html' in block:
        return rich(html.fragment_fromstring(block['html'],create_parent='div'))
    return escape(block['text']).replace('\n','<br/>')

def story():
    flow = []
    for i,section in enumerate(sections):
        title = Paragraph(escape(section['heading']),heading)
        title.section_index = i
        flow.append(title)
        if i:
            rule = HRFlowable(width=88,thickness=3,color=colors['yellow'],spaceAfter=10,hAlign='LEFT')
            rule.keepWithNext = True
            flow.append(rule)
        for block in section['blocks']:
            kind = block['type']
            if kind == 'figure':
                path = base / block['path']
                with PILImage.open(path) as pic:
                    w,h = pic.size
                scale = min(360/w, 400/h)
                image = Image(str(path),width=w*scale,height=h*scale)
                group = [image]
                if block.get('caption'):
                    group.append(Paragraph(escape(block['caption']),caption))
                flow.append(KeepTogether(group))
            elif kind == 'table':
                rows = [[Paragraph(escape(str(v)),body) for v in row] for row in block['rows']]
                cols = len(rows[0])
                if not cols or any(len(row)!=cols for row in rows):
                    raise ValueError('Table rows must have equal column counts')
                table = Table(rows,colWidths=[(W-118)/cols]*cols,repeatRows=int(block.get('header',False)))
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,0),(-1,-1),[colors['pale'],white])]))
                flow.append(table)
            else:
                item = content(block).replace('▸',f'<font name="{symbol}">▸</font>')
                flow.append(Paragraph(item,{'p':body,'lead':lead,'h3':sub}[kind]))
    return flow

class BodyDoc(SimpleDocTemplate):
    def afterFlowable(self,item):
        if hasattr(item,'section_index'):
            marks[item.section_index] = self.page + offset

def draw_body(path,total):
    def decorate(c,doc):
        c.setFillColor(colors['pale'])
        c.rect(0,0,8,H,fill=1,stroke=0)
        for x,width,key in [(0,.43,'yellow'),(.43,.20,'green'),(.63,.37,'primary')]:
            c.setFillColor(colors[key])
            c.rect(x*W,H-13,width*W,13,fill=1,stroke=0)
        c.setFont(font,8)
        c.setFillColor(colors['deep'])
        c.drawString(53,H-42,'枢纽云  /  客户成功案例')
        c.setStrokeColor(colors['pale'])
        c.line(53,H-49,W-53,H-49)
        c.setFillColor(HexColor('#52687C'))
        c.drawString(53,29,f'枢纽云·{industry}行业案例')
        c.drawRightString(W-53,29,f'{doc.page+offset:02d} / {total:02d}')
    doc = BodyDoc(str(path),pagesize=A4,leftMargin=53,rightMargin=53,topMargin=59,bottomMargin=43)
    doc.build(story(),onFirstPage=decorate,onLaterPages=decorate)
    return doc.page

def fitted(c,x,y,text,size,width,face=font):
    length = pdfmetrics.stringWidth(text,face,size)
    c.setFont(face,min(size,size*width/max(length,1)))
    c.drawString(x,y,text)

def background(folder):
    if palette == defaults:
        return assets/'cover-gradient.png'
    import numpy as np
    yy,xx = np.mgrid[0:1697,0:1200]
    rgb = np.array(ImageColor.getrgb(palette['pale']))
    for x,y,sx,sy,strength,key in [(1200,90,440,360,.90,'light'),(1250,670,255,300,.37,'green'),(1260,1560,290,320,.97,'yellow')]:
        alpha = (strength*np.exp(-.5*((xx-x)**2/sx**2+(yy-y)**2/sy**2)))[...,None]
        rgb = rgb*(1-alpha)+np.array(ImageColor.getrgb(palette[key]))*alpha
    path = folder/'gradient.png'
    PILImage.fromarray(rgb.astype('uint8')).save(path)
    return path

def draw_front(folder,total,starts):
    path = folder/'front.pdf'
    c = canvas.Canvas(str(path),pagesize=A4)
    c.drawImage(str(background(folder)),0,0,width=W,height=H)
    c.drawImage(str(assets/'ltd-logo.png'),49,H-192,width=171,height=106,mask='auto',preserveAspectRatio=True)
    with PILImage.open(logo) as source_logo:
        customer_logo = source_logo.convert('RGBA')
    visible = customer_logo.getchannel('A').point(lambda value: 255 if value > 8 else 0).getbbox()
    if visible:
        customer_logo = customer_logo.crop(visible)
    logo_width, logo_height = customer_logo.size
    logo_scale = min(112 / logo_width, 76 / logo_height)
    draw_width, draw_height = logo_width * logo_scale, logo_height * logo_scale
    c.drawImage(ImageReader(customer_logo), 465 - draw_width,
                H - 142 - draw_height / 2, width=draw_width, height=draw_height, mask='auto')
    c.setStrokeColor(HexColor('#8295B5'))
    c.line(225,H-142,269,H-142)
    c.line(302,H-142,345,H-142)
    c.circle(285,H-142,16)
    c.setFillColor(HexColor('#24304C'))
    c.setFont(symbol,15)
    c.drawCentredString(285,H-147,'×')
    parts = [(font,'枢纽云'),(symbol,'✖'),(font,client)]
    widths = [pdfmetrics.stringWidth(text,face,11.4) for face,text in parts]
    x = (W-sum(widths)-18)/2
    for (face,text),width in zip(parts,widths):
        c.setFont(face,11.4)
        c.drawString(x,H-226,text)
        x += width+9
    c.setFillColor(HexColor('#0B1837'))
    for i,line in enumerate(case['title']):
        fitted(c,39,H-317-i*56,line,44,W-78,bold)
    c.setStrokeColor(colors['yellow'])
    c.setLineWidth(3)
    c.line(39,H-391,193,H-391)
    fitted(c,40,H-433,case['subtitle'],17.5,W-80)
    c.setFillColor(HexColor('#3F4050'))
    fitted(c,40,H-544,'营销枢纽好，用好客来找',21,W-80)
    for x,width,bg in [(38,174,colors['lavender']),(212,174,Color(*[(v+1)/2 for v in colors['lavender'].rgb()])),(386,173,colors['pale'])]:
        c.setFillColor(bg)
        c.rect(x,128,width,20,fill=1,stroke=0)
    c.setFillColor(HexColor('#F7F6FC'))
    c.rect(0,60,W,69,fill=1,stroke=0)
    c.setFillColor(HexColor('#0B1837'))
    fitted(c,39,93,f'枢纽云·{industry}行业客户案例',21,W-78)
    fitted(c,40,70,'LTD.COM/CASE',12,W-80,font)
    c.showPage()
    for n in range(toc_pages):
        c.setFillColor(Color(.984,.981,.968))
        c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(colors['primary'])
        c.rect(0,H-14,W,14,fill=1,stroke=0)
        c.setFillColor(colors['deep'])
        fitted(c,53,H-93,'目录',27,200)
        fitted(c,54,H-115,'CONTENTS',10,200,font)
        for slot,label in enumerate(toc[n*10:n*10+10]):
            i = n*10+slot
            y = H-176-slot*52
            c.setFillColor(colors['pale'] if i%2 else white)
            c.roundRect(53,y-16,W-106,45,7,fill=1,stroke=0)
            c.setFillColor(colors['deep'])
            fitted(c,68,y,f'{i+1:02d}',10,38)
            fitted(c,111,y,label,10,W-217)
            c.setFont(font,10)
            c.drawRightString(W-68,y,f'{starts[i]:02d}')
        c.setFont(font,8)
        c.drawRightString(W-53,29,f'{n+2:02d} / {total:02d}')
        c.showPage()
    c.save()
    return path

def number_appendix(page,index,page_no,total):
    buf = BytesIO()
    c = canvas.Canvas(buf,pagesize=A4)
    c.setFillColor(HexColor('#293378' if index==2 else '#FBFAF6'))
    c.rect(W-86,9,76,29,fill=1,stroke=0)
    c.setFillColor(white if index==2 else HexColor('#2D3A80'))
    c.setFont(font,7.2)
    c.drawRightString(W-29,23,f'{page_no:02d} / {total:02d}')
    c.save()
    page.merge_page(PdfReader(buf).pages[0])

with TemporaryDirectory() as temporary:
    folder = Path(temporary)
    appendix = PdfReader(assets/'about.pdf')
    body_path = folder/'body.pdf'
    count = draw_body(body_path,0)
    total = offset+count+len(appendix.pages)
    assert count == draw_body(body_path,total)
    starts = [marks[i] for i in range(len(sections))]+[offset+count+1]
    writer = PdfWriter()
    writer.append(draw_front(folder,total,starts))
    writer.append(body_path)
    for i,page in enumerate(appendix.pages):
        number_appendix(page,i,starts[-1]+i,total)
        writer.add_page(page)
    for label,num in zip(toc,starts):
        writer.add_outline_item(label,num-1)
    for license_name in ('OFL-NotoSansSC.txt', 'LICENSE-DejaVuSans.txt'):
        writer.add_attachment(license_name,(fonts/license_name).read_bytes())
    writer.add_metadata({'/Title':'枢纽云客户成功案例｜'+client,'/Author':'枢纽云'})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(dir=args.output.parent,delete=False,suffix='.pdf') as staged:
        try:
            writer.write(staged)
            staged.close()
            os.replace(staged.name,args.output)
        finally:
            Path(staged.name).unlink(missing_ok=True)
    print(f'{args.output} ({total} pages)')
