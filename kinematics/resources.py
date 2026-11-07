"""Fetch one reviewer-supplied public HTTPS page, with DNS pinning and size limits."""
import html
import http.client
import ipaddress
import re
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit


class ResourceError(ValueError):pass


def public_target(url,resolver=socket.getaddrinfo):
    if not isinstance(url,str) or len(url)>2000:raise ResourceError('Enter a public HTTPS URL.')
    try:
        parsed=urlsplit(url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443):raise ValueError()
        host=parsed.hostname.encode('idna').decode()
        addresses=resolver(host,443,type=socket.SOCK_STREAM)
        ips={r[4][0] for r in addresses}
        if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):raise ValueError()
    except (ValueError,UnicodeError,OSError):raise ResourceError('Use a public HTTPS address; private, local and metadata addresses are blocked.') from None
    return parsed,host,sorted(ips)[0]


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self,host,ip):super().__init__(host,timeout=10,context=ssl.create_default_context());self.ip=ip
    def connect(self):
        sock=socket.create_connection((self.ip,443),self.timeout)
        try:self.sock=self._context.wrap_socket(sock,server_hostname=self.host)
        except Exception:sock.close();raise


class TextPage(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.title=[];self.skip=0;self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript','svg'):self.skip+=1
        if tag=='title':self.in_title=True
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript','svg'):self.skip=max(0,self.skip-1)
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if not self.skip:self.parts.append(data)


def fetch_public(url):
    deadline=time.monotonic()+20
    for redirect in range(4):
        if time.monotonic()>deadline:raise ResourceError('The resource preview timed out.')
        parsed,host,ip=public_target(url);connection=PinnedHTTPS(host,ip)
        try:
            path=parsed.path or '/'
            if parsed.query:path+='?'+parsed.query
            connection.request('GET',path,headers={'User-Agent':'FieldnotesLocalResourceReview/1.0','Accept':'text/html,text/plain','Accept-Encoding':'identity'})
            response=connection.getresponse()
            if response.status in (301,302,303,307,308):
                location=response.getheader('Location')
                if not location:raise ResourceError('This redirect has no destination.')
                url=urljoin(url,location);continue
            if response.status!=200:raise ResourceError('The resource could not be fetched.')
            kind=response.getheader('Content-Type','').split(';')[0].strip().lower()
            if kind not in ('text/html','text/plain'):raise ResourceError('Use an HTML or plain-text teaching page.')
            if response.getheader('Content-Encoding','identity').lower() not in ('identity',''):raise ResourceError('Compressed responses are not accepted by this preview fetcher.')
            chunks=[];size=0
            while True:
                if time.monotonic()>deadline:raise ResourceError('The resource preview timed out.')
                chunk=response.read1(min(16384,512*1024+1-size))
                if not chunk:break
                chunks.append(chunk);size+=len(chunk)
                if size>512*1024:raise ResourceError('This page exceeds the 512 KB preview limit.')
            body=b''.join(chunks)
            text=body.decode('utf-8',errors='replace')
            if kind=='text/html':
                parser=TextPage();parser.feed(text);title=' '.join(parser.title);text=' '.join(parser.parts)
            else:title=host
            text=re.sub(r'\s+',' ',html.unescape(text)).strip()
            if not text:raise ResourceError('The page has no readable text.')
            return {'url':url,'title':title.strip()[:200] or host,'excerpt':text[:6000]}
        except (OSError,http.client.HTTPException):raise ResourceError('The resource connection failed or timed out.') from None
        finally:connection.close()
    raise ResourceError('Too many redirects.')
