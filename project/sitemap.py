from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from store.models import Product

class StoreSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def get_urls(self, site=None, **kwargs):
        site = Site(domain='dev.vleaf.xyz', name='dev.vleaf.xyz')
        kwargs['protocol'] = 'https'
        return super(StoreSitemap, self).get_urls(site=site, **kwargs)        

    def items(self):
        return Product.objects.all()
    
    def location(self, item) -> str:
        return item.get_absolute_url()