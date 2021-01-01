from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Site, Article
from web.utils import get_content


class SiteFeed(Feed):
    ttl = 12 * 3600

    def get_object(self, request, site_id):
        try:
            return Site.objects.get(pk=site_id, status='active', creator__in=('system', 'wemp'))
        except ValueError:
            return Site.objects.get(name=site_id, status='active', creator__in=('system', 'wemp'))

    def title(self, site):
        return site.cname

    def link(self, site):
        return site.link

    def description(self, site):
        return site.brief

    def feed_url(self, site):
        return reverse('get_feed_entries', kwargs={"site_id": site.pk})

    def author_name(self, site):
        return site.author

    def categories(self, site):
        return ''

    def feed_copyright(self, site):
        if site.creator == 'wemp':
            return site.favicon
        return ''

    def items(self, site):
        return Article.objects.filter(site=site, status='active').order_by('-id')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return get_content(item.uindex, item.site_id)

    def item_link(self, item):
        return item.src_url

    def item_author_name(self, item):
        return item.author

    def item_pubdate(self, item):
        return item.ctime
