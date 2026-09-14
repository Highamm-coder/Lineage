from html.parser import HTMLParser
import re, html as H

class TableParser(HTMLParser):
    """Extract tables as list-of-rows-of-cell-text, with rowspan/colspan expansion."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables=[]; self.stack=[]; self.cur=None; self.row=None; self.cell=None
        self.depth=0; self.pending={}  # (tableidx) rowspan carry
        self.skip=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='table':
            self.stack.append({'rows':[], 'carry':{}, 'cls':a.get('class','')})
        elif tag=='tr' and self.stack:
            self.stack[-1]['row']=[]
        elif tag in ('td','th') and self.stack and 'row' in self.stack[-1]:
            self.cell={'txt':[], 'rs':int(a.get('rowspan',1) or 1), 'cs':int(a.get('colspan',1) or 1)}
        elif tag in ('sup','style','script') :
            self.skip+=1
        elif tag=='br' and self.cell is not None:
            self.cell['txt'].append(' | ')
    def handle_endtag(self, tag):
        if tag=='table' and self.stack:
            t=self.stack.pop(); self.tables.append(t)
        elif tag=='tr' and self.stack and 'row' in self.stack[-1]:
            t=self.stack[-1]; t['rows'].append(t.pop('row'))
        elif tag in ('td','th') and self.cell is not None and self.stack and 'row' in self.stack[-1]:
            txt=re.sub(r'\s+',' ',''.join(self.cell['txt'])).strip(' |').strip()
            for _ in range(self.cell['cs']):
                self.stack[-1]['row'].append({'t':txt,'rs':self.cell['rs']})
            self.cell=None
        elif tag in ('sup','style','script'):
            self.skip=max(0,self.skip-1)
    def handle_data(self, d):
        if self.skip: return
        if self.cell is not None: self.cell['txt'].append(d)

def expand(rows):
    """apply rowspans downward"""
    out=[]; carry={}
    for r in rows:
        line=[]; i=0; src=list(r)
        col=0
        while True:
            while col in carry and carry[col][1]>0:
                line.append(carry[col][0]); carry[col]=(carry[col][0],carry[col][1]-1); col+=1
            if not src: break
            c=src.pop(0)
            line.append(c['t'])
            if c['rs']>1: carry[col]=(c['t'], c['rs']-1)
            col+=1
        out.append(line)
    return out

def get_tables(htmltext):
    p=TableParser(); p.feed(htmltext)
    return [ (t.get('cls',''), expand(t['rows'])) for t in p.tables ]
