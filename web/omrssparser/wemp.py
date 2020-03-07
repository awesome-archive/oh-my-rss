
import django
from web.models import *
import logging
import requests
from scrapy.http import HtmlResponse
from web.utils import save_avatar
from feed.utils import current_ts, is_crawled_url, mark_crawled_url
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import urllib
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_wemp_ershicimi(url, update=False):
    """
    解析微信公众号，www.ershicimi.com
    :param url: 公众号主页地址
    :param update: 如果已经存在，是否更新
    :return: 解析结果，成功返回字典；失败 None
    """
    try:
        rsp = requests.get(url, timeout=10)
    except:
        logger.warning(f'请求出现异常：`{url}')
        return None

    if rsp.ok:
        response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

        qrcode = response.selector.xpath("//img[@class='qr-code']/@src").extract_first()

        if qrcode:
            name = urllib.parse.parse_qs(urllib.parse.urlparse(qrcode).query)['username'][0]

            if name:
                if not Site.objects.filter(name=name).exists():
                    # 新增站点
                    cname = response.selector.xpath("//li[@class='title']//span[@class='name']/text()").\
                        extract_first().strip()

                    avatar = response.selector.xpath("//img[@class='avatar']/@src").extract_first().strip()
                    favicon = save_avatar(avatar, name)

                    brief = response.selector.xpath(
                        "//div[@class='Profile-sideColumnItemValue']/text()").extract_first().strip()

                    if cname and avatar and brief:
                        try:
                            site = Site(name=name, cname=cname, link=qrcode, brief=brief, star=19, freq='日更',
                                        creator='wemp', copyright=20, tag='公众号', rss=url, favicon=favicon)
                            site.save()
                        except:
                            logger.warning(f'新增公众号失败：`{name}')
                else:
                    # 更新内容
                    if update:
                        try:
                            site = Site.objects.get(name=name)
                            links = response.selector.xpath("//*[@class='weui_media_title']/a/@href").extract()[:3]
                            wemp_spider(links, site)
                        except:
                            logger.warning(f'更新公众号内容出现异常：`{name}')
                return {"name": name}
            else:
                logger.warning(f'微信公众号 id 解析失败：`{qrcode}')
        else:
            logger.warning(f'二维码链接解析失败：`{url}')

    return None


def wemp_spider(urls, site):
    """
    抓取微信内容
    :param urls:
    :param site:
    :return:
    """
    for url in urls:
        if is_crawled_url(url):
            continue

        try:
            logger.info(f'开始爬取公众号地址：`{url}')
            rsp = requests.get(url, timeout=10)
    
            if rsp.ok:
                response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')
    
                title = response.selector.xpath('//h2[@id="activity-name"]/text()').extract_first().strip()
                content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()

                try:
                    author = response.selector.xpath('//span[@id="js_author_name"]/text()').\
                        extract_first().strip()
                except:
                    author = response.selector.xpath('//a[@id="js_name"]/text()').extract_first().strip()
    
                if title and content:
                    content_soup = BeautifulSoup(content, "html.parser")
                    for img in content_soup.find_all('img'):
                        if img.attrs.get('data-src'):
                            img.attrs['src'] = img.attrs['data-src']

                    article = Article(title=title, author=author, site=site, uindex=current_ts(),
                                      content=str(content_soup), src_url=url)
                    article.save()

                    mark_crawled_url(url)
                else:
                    logger.warning(f'公众号内容解析异常：`{title}`{author}`{content}')
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
            logger.warning(f'公众号爬取出现网络异常：`{url}')
        except:
            logger.warning(f'公众号爬取出现未知异常：`{url}')
