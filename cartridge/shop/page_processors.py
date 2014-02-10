from __future__ import unicode_literals

from django.template.defaultfilters import slugify

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product, ProductVariation
from ornatus.sieve.views import sieve, winnow, active_sieves


@processor_for(Category)
def variant_processor(request, page):
    """
    Use ProductVariations to display in the category.
    Add paging ,sort by db order and filtering by sieves.
    """
    settings.use_editable()
    products = ProductVariation.objects.filter(product__category=page.category
                                              ).exclude(option1='Green')
    products = sieve(products.order_by('_order'),
                     request.GET.get('primary', None),
                     request.GET.get('pattern', None))
    primary, pattern = winnow(products)
    products = paginate(products,
                        request.GET.get('page', 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    sub_categories = page.category.children.published()
    child_categories = []#Category.objects.filter(id__in=sub_categories)
    
    active = active_sieves(request)
    # display sieves for these categories
    cats = ('vegan-ties', 'skinny-vegan-ties')
    return {'products': products,
            'sieve_cats': cats, 'sieves': active,
            'primary': primary, 'pattern': pattern,
            'child_categories': child_categories}


def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.use_editable()
    products = Product.objects.published(for_user=request.user
                                ).filter(page.category.filters()).distinct()
    sort_options = [(slugify(option[0]), option[1])
                    for option in settings.SHOP_PRODUCT_SORT_OPTIONS]
    sort_by = request.GET.get("sort", sort_options[0][1])
    products = paginate(products.order_by(sort_by),
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by
    sub_categories = page.category.children.published()
    child_categories = Category.objects.filter(id__in=sub_categories)
    return {"products": products, "child_categories": child_categories}
